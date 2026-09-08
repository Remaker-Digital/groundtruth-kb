# THIS FILE IS A PROJECTION, NOT CANONICAL.
# Projected from the neutral harness baseline by the GT-KB projection engine.
# Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
# `gt harness project antigravity`. If a needed change cannot be made through
# the baseline and re-projection, file a work item against the projector
# (GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
"""Shared shell-payload target extraction for baseline PreToolUse gates.

Landed by WI-7289 (proposal ``bridge/gtkb-wi7289-shell-exec-gate-coverage-001.md``,
GO at ``-004``).

Six write gates and the SoT read-discipline gate declared only ``file_write`` or
``read_access`` intents, so the projector never rendered the shell tool names into
their matchers and they were unregistered against shell-command events on every
harness. Declaring ``shell_exec`` in ``manifest.toml`` registers them, but a
shell-command payload carries a command string rather than the
``file_path``/``content`` pair the native branch reads. Without extraction the
newly-registered gates would fire and always allow -- a gate that runs but cannot
see its subject is not enforcement.

This module turns a shell command into the same shape the native branch already
understands, so each gate reuses its existing decision function unchanged. That
is deliberate: it is what keeps native denial reasons byte-identical (GO binding
condition 3) while making shell denial reasons match by construction rather than
by parallel re-implementation. Divergent per-surface parsers are how the
read-side and write-side drifted apart in the first place, which is why this is
one shared helper rather than seven private ones.

Contract (GO binding condition 2):

* Recognized write/read forms yield targets.
* Unrecognized or no-target forms yield an empty list, so the caller allows the
  command. Anything the parser does not understand behaves exactly as it does
  today.
* ``content`` is ``None`` when the command form carries no inline payload (``tee``
  from a pipe, ``sed -i``, ``Out-File``). A content-sensitive gate MUST skip such
  targets rather than substitute ``""``: an empty string reads as "no canonical
  status token" / "no author provenance" and would deny legitimate commands,
  which is the over-blocking failure the proposal's mitigation exists to prevent.
"""

from __future__ import annotations

import re
import shlex
from dataclasses import dataclass
from pathlib import Path

# Native tool names that carry a shell command. Claude renders shell_exec to
# "Bash|PowerShell", Cursor to "Shell|Bash"; Goose registers every PreToolUse
# hook without a matcher at all, so its payloads reach here under whichever name
# its event model reports. Accept the union rather than a single name.
SHELL_TOOL_NAMES = frozenset({"Bash", "PowerShell", "Shell", "shell", "bash", "powershell"})

# Chaining operators that separate independent commands. Split on these only
# outside quotes; a ">" inside a quoted string is data, not a redirect.
_CHAIN_OPERATORS = (";", "&&", "||", "|", "\n")

_HEREDOC_START = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
_ECHO_PAYLOAD = re.compile(r"^\s*(?:echo|printf)\s+(-[a-zA-Z]+\s+)*(\"(?P<d>[^\"]*)\"|'(?P<s>[^']*)')")

_COPY_VERBS = {"cp", "copy", "copy-item"}
_MOVE_VERBS = {"mv", "move", "move-item"}
_PS_CONTENT_VERBS = {"set-content", "add-content", "out-file", "new-item"}
_PATH_FLAGS = {"-path", "-literalpath", "-filepath", "--path"}
_VALUE_FLAGS = {"-value", "--value"}


@dataclass(frozen=True)
class ShellWriteTarget:
    """One file a shell command would write.

    ``path`` is the raw path token as written (quotes stripped); callers
    normalize it the same way they normalize ``tool_input.file_path``.
    ``content`` is the inline payload when the form carries one, else ``None``.
    ``form`` names the recognized shape and exists for diagnostics, so a denial
    can say which construct was matched.
    """

    path: str
    content: str | None
    form: str


def is_shell_tool(tool_name: str | None) -> bool:
    """True when a payload's tool name denotes a shell-command surface."""
    return bool(tool_name) and str(tool_name) in SHELL_TOOL_NAMES


def _unquote(token: str) -> str:
    token = token.strip()
    if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'":
        return token[1:-1]
    return token


def _split_segments(command: str) -> list[str]:
    """Split on chaining operators that fall outside quotes."""
    segments: list[str] = []
    current: list[str] = []
    quote: str | None = None
    index = 0
    while index < len(command):
        char = command[index]
        if quote:
            current.append(char)
            if char == quote:
                quote = None
            index += 1
            continue
        if char in "\"'":
            quote = char
            current.append(char)
            index += 1
            continue
        matched = next((op for op in _CHAIN_OPERATORS if command.startswith(op, index)), None)
        if matched:
            segments.append("".join(current))
            current = []
            index += len(matched)
            continue
        current.append(char)
        index += 1
    segments.append("".join(current))
    return [segment for segment in segments if segment.strip()]


def _inline_echo_payload(segment: str) -> str | None:
    match = _ECHO_PAYLOAD.match(segment)
    if match is None:
        return None
    return match.group("d") if match.group("d") is not None else match.group("s")


def _extract_heredocs(command: str) -> tuple[list[ShellWriteTarget], str]:
    """Pull heredoc writes out of ``command``.

    Returns the recognized targets and the command text with heredoc bodies
    removed, so the remaining single-line forms can be parsed without the body
    being mistaken for further commands.
    """
    start = _HEREDOC_START.search(command)
    if start is None:
        return [], command
    delimiter = start.group(2)
    lines = command.splitlines()
    header_index = next(
        (i for i, line in enumerate(lines) if _HEREDOC_START.search(line)),
        None,
    )
    if header_index is None:
        return [], command
    body: list[str] = []
    end_index = len(lines)
    for offset in range(header_index + 1, len(lines)):
        if lines[offset].strip() == delimiter:
            end_index = offset
            break
        body.append(lines[offset])
    header = lines[header_index]
    targets = [
        ShellWriteTarget(path=path, content="\n".join(body), form="heredoc")
        for path in _redirect_targets(header) + _tee_targets(header)
    ]
    # Blank the heredoc marker AND its redirect span in the header. Leaving the
    # redirect behind would re-match the same path as a content-less "redirect"
    # target, shadowing the heredoc target that actually carries the content.
    consumed_header = _blank_redirects(_HEREDOC_START.sub("", header))
    remainder = lines[:header_index] + [consumed_header] + lines[end_index + 1 :]
    return targets, "\n".join(remainder)


def _find_redirects(segment: str) -> list[tuple[int, int, str]]:
    """Locate ``>``/``>>`` redirections that fall outside quotes.

    A regex over the raw text cannot do this: ``grep -rn "x > y" src/`` contains
    a ``>`` that is data, and matching it invents a write target for a read-only
    command. Over-blocking a legitimate command is the failure mode GO binding
    condition 2 forbids, so redirect detection is quote-aware by construction.

    Returns ``(start, end, path)`` spans so callers can both read the target and
    blank the span when rewriting a command.
    """
    spans: list[tuple[int, int, str]] = []
    quote: str | None = None
    index = 0
    while index < len(segment):
        char = segment[index]
        if quote:
            if char == quote:
                quote = None
            index += 1
            continue
        if char in "\"'":
            quote = char
            index += 1
            continue
        if char == ">":
            # A file descriptor prefix ("2>") or a heredoc/herestring ("<<", "<>")
            # is not a plain write redirect.
            if index and segment[index - 1] in "0123456789<":
                index += 1
                continue
            start = index
            index += 1
            if index < len(segment) and segment[index] == ">":
                index += 1
            while index < len(segment) and segment[index] in " \t":
                index += 1
            token_start = index
            if index < len(segment) and segment[index] in "\"'":
                closing = segment[index]
                index += 1
                while index < len(segment) and segment[index] != closing:
                    index += 1
                index = min(index + 1, len(segment))
            else:
                while index < len(segment) and segment[index] not in " \t;&|<>\n":
                    index += 1
            token = segment[token_start:index]
            if token.strip():
                spans.append((start, index, _unquote(token)))
            continue
        index += 1
    return spans


def _redirect_targets(segment: str) -> list[str]:
    return [path for _, _, path in _find_redirects(segment)]


def _blank_redirects(segment: str) -> str:
    """Replace redirect spans with spaces, preserving offsets."""
    result = list(segment)
    for start, end, _ in _find_redirects(segment):
        for position in range(start, min(end, len(result))):
            result[position] = " "
    return "".join(result)


def _tokens(segment: str) -> list[str]:
    try:
        return shlex.split(segment, posix=False)
    except ValueError:
        return []


def _tee_targets(segment: str) -> list[str]:
    tokens = _tokens(segment)
    for index, token in enumerate(tokens):
        if token.lower() != "tee":
            continue
        return [_unquote(candidate) for candidate in tokens[index + 1 :] if not candidate.startswith("-")]
    return []


def _read_source(raw_source: str, root: Path | None) -> str | None:
    """Read a copy/move source so content-sensitive gates can see the payload.

    A prepared file copied into a governed path is the same write as a heredoc
    into it; the content is on disk rather than in the command. Unreadable or
    binary sources return ``None``, which the caller treats as "cannot see" and
    therefore allows.
    """
    if root is None:
        return None
    candidate = Path(raw_source)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        if not candidate.is_file():
            return None
        return candidate.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _positional(tokens: list[str]) -> list[str]:
    return [token for token in tokens[1:] if not token.startswith("-")]


def _flag_value(tokens: list[str], flags: set[str]) -> str | None:
    for index, token in enumerate(tokens):
        if token.lower() in flags and index + 1 < len(tokens):
            return _unquote(tokens[index + 1])
    return None


def _segment_targets(segment: str, root: Path | None) -> list[ShellWriteTarget]:
    tokens = _tokens(segment)
    if not tokens:
        return []
    verb = _unquote(tokens[0]).lower().rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    inline = _inline_echo_payload(segment)
    targets: list[ShellWriteTarget] = []

    for path in _redirect_targets(segment):
        targets.append(ShellWriteTarget(path=path, content=inline, form="redirect"))
    for path in _tee_targets(segment):
        targets.append(ShellWriteTarget(path=path, content=inline, form="tee"))

    if verb in _COPY_VERBS or verb in _MOVE_VERBS:
        operands = [_unquote(token) for token in _positional(tokens)]
        source = _flag_value(tokens, {"-path", "-literalpath"})
        destination = _flag_value(tokens, {"-destination"})
        if source is None and len(operands) >= 2:
            source = operands[-2]
        if destination is None and len(operands) >= 2:
            destination = operands[-1]
        if destination:
            form = "copy" if verb in _COPY_VERBS else "move"
            content = _read_source(source, root) if source else None
            targets.append(ShellWriteTarget(path=destination, content=content, form=form))

    if verb == "sed" and any(token.startswith("-i") for token in tokens[1:]):
        operands = [_unquote(token) for token in _positional(tokens)]
        if operands:
            targets.append(ShellWriteTarget(path=operands[-1], content=None, form="sed_in_place"))

    if verb in _PS_CONTENT_VERBS:
        path = _flag_value(tokens, _PATH_FLAGS)
        if path is None:
            operands = [_unquote(token) for token in _positional(tokens)]
            path = operands[0] if operands else None
        if path:
            targets.append(
                ShellWriteTarget(
                    path=path,
                    content=_flag_value(tokens, _VALUE_FLAGS),
                    form=verb.replace("-", "_"),
                )
            )

    return targets


def extract_write_targets(command: str, root: Path | None = None) -> list[ShellWriteTarget]:
    """Return every file a shell command would write, or ``[]`` if none is recognized.

    An empty result is the allow path: it means the parser did not recognize a
    write, not that the command is safe. That asymmetry is intentional per GO
    binding condition 2 -- widening registration must not deny commands that the
    native surface never saw.
    """
    if not command or not isinstance(command, str):
        return []
    heredoc_targets, remainder = _extract_heredocs(command)
    targets = list(heredoc_targets)
    # A heredoc target is the authoritative representation of a write to that
    # path: it is the one form that carries the content. Suppress any later,
    # content-less form naming the same path so a gate does not judge the same
    # write twice on strictly worse evidence.
    claimed = {target.path for target in targets}
    seen = {(target.path, target.form) for target in targets}
    for segment in _split_segments(remainder):
        for target in _segment_targets(segment, root):
            key = (target.path, target.form)
            if key in seen or target.path in claimed:
                continue
            seen.add(key)
            targets.append(target)
    return targets


def synthetic_write_payload(payload: dict, target: ShellWriteTarget) -> dict:
    """Build a native ``Write`` payload equivalent to one shell write target.

    Feeding this back through a gate's existing decision function is what makes
    the shell verdict identical to the native verdict without duplicating the
    gate's logic.
    """
    synthetic = dict(payload)
    synthetic["tool_name"] = "Write"
    synthetic["tool_input"] = {
        "file_path": target.path,
        "content": target.content if target.content is not None else "",
    }
    return synthetic


def expand_shell_payload(payload: dict, root: Path | None = None, *, require_content: bool = True) -> list[dict]:
    """Expand one payload into the native-shaped payloads a gate should judge.

    For a native (non-shell) payload this returns ``[payload]`` unchanged, so a
    caller can wrap its existing decision in a loop without special-casing and
    without altering native behavior in any way -- the single-element list runs
    exactly the code that ran before (GO binding condition 3).

    For a shell payload it returns one synthetic ``Write`` payload per recognized
    write target. An unrecognized command yields ``[]``, so the gate allows it.

    ``require_content`` defaults to True because most gates judge file content.
    Path-only gates pass ``False`` to also receive targets whose content the
    parser cannot see (``tee``, ``sed -i``), for which content is rendered as an
    empty string and must not be treated as meaningful.
    """
    tool_name = payload.get("tool_name") or payload.get("tool") or ""
    if not is_shell_tool(tool_name):
        return [payload]
    tool_input = payload.get("tool_input") or {}
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or not command:
        return []
    targets = extract_write_targets(command, root)
    if require_content:
        targets = [target for target in targets if target.content is not None]
    return [synthetic_write_payload(payload, target) for target in targets]


def content_bearing_targets(command: str, root: Path | None = None) -> list[ShellWriteTarget]:
    """Targets whose content the parser can actually see.

    Content-sensitive gates use this instead of :func:`extract_write_targets` so
    a form carrying no inline payload is allowed rather than judged against an
    empty string.
    """
    return [target for target in extract_write_targets(command, root) if target.content is not None]
