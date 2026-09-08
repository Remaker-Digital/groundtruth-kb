"""PostgreSQL archive_command: copy one complete WAL file without replacing bytes."""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path


def archive(source: Path, destination: Path) -> None:
    """A retry succeeds only if the previously archived bytes are identical."""
    if destination.exists():
        if source.read_bytes() != destination.read_bytes():
            raise ValueError("Existing WAL archive has different bytes")
        with destination.open("r+b") as persisted:
            os.fsync(persisted.fileno())
        return
    temporary = None
    try:
        with (
            source.open("rb") as src,
            tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".partial", delete=False) as dst,
        ):
            temporary = Path(dst.name)
            shutil.copyfileobj(src, dst)
            dst.flush()
            os.fsync(dst.fileno())
        # Atomic no-replace publication, on both NTFS and POSIX filesystems.
        try:
            os.link(temporary, destination)
        except FileExistsError:
            if source.read_bytes() != destination.read_bytes():
                raise ValueError("Concurrent WAL archive has different bytes") from None
        with destination.open("r+b") as persisted:
            os.fsync(persisted.fileno())
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    archive(Path(sys.argv[1]), Path(sys.argv[2]))
