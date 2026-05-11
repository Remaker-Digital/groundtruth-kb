"""Tests for standalone admin auth hardening (S161).

SPEC-1688 (Argon2id), SPEC-1689 (opaque session), SPEC-1690 (CSRF), SPEC-1691 (12-char min).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""


class TestArgon2idPasswordStorage:
    """SPEC-1688: Standalone admin password MUST be hashed with Argon2id."""

    def test_argon2_cffi_importable(self):
        import argon2
        assert hasattr(argon2, "PasswordHasher")

    def test_password_hash_is_not_sha256(self):
        import src.app.standalone_auth as m
        h = m._admin_password_hash
        if h:
            is_sha256 = len(h) == 64 and all(c in "0123456789abcdef" for c in h)
            assert not is_sha256, "Password hash is still SHA-256"

    def test_no_plaintext_password_in_module(self):
        import src.app.standalone_auth as m
        pw = getattr(m, "_admin_current_password", None)
        assert pw is None or pw == "", "_admin_current_password holds plaintext"

    def test_verify_password_function_exists(self):
        import src.app.standalone_auth as m
        assert hasattr(m, "_verify_password")

    def test_verify_rejects_wrong_password(self):
        import src.app.standalone_auth as m
        if hasattr(m, "_verify_password"):
            assert m._verify_password("wrong-password-xxxx") is False

    def test_verify_accepts_correct_password(self):
        import src.app.standalone_auth as m
        if hasattr(m, "_verify_password") and hasattr(m, "_hash_password"):
            test_pw = "test-secure-password-123"
            orig = m._admin_password_hash
            m._admin_password_hash = m._hash_password(test_pw)
            try:
                assert m._verify_password(test_pw) is True
            finally:
                m._admin_password_hash = orig


class TestOpaqueSessionCookies:
    """SPEC-1689: Session cookies MUST be opaque signed tokens."""

    def test_compute_cookie_value_removed(self):
        import src.app.standalone_auth as m
        assert not hasattr(m, "_compute_cookie_value")

    def test_generate_session_token_exists(self):
        import src.app.standalone_auth as m
        assert hasattr(m, "_generate_session_token")

    def test_session_tokens_are_random(self):
        import src.app.standalone_auth as m
        if hasattr(m, "_generate_session_token"):
            assert m._generate_session_token() != m._generate_session_token()

    def test_session_token_has_signature(self):
        import src.app.standalone_auth as m
        if hasattr(m, "_generate_session_token"):
            assert "." in m._generate_session_token()

    def test_validate_rejects_tampered(self):
        import src.app.standalone_auth as m
        if hasattr(m, "_validate_session_token"):
            assert m._validate_session_token("tampered.bad") is False
            assert m._validate_session_token("") is False

    def test_validate_accepts_valid(self):
        import src.app.standalone_auth as m
        if hasattr(m, "_generate_session_token") and hasattr(m, "_validate_session_token"):
            assert m._validate_session_token(m._generate_session_token()) is True

    def test_session_secret_exists(self):
        import src.app.standalone_auth as m
        assert hasattr(m, "_SESSION_SECRET")


class TestCSRFProtection:
    """SPEC-1690: Form POST endpoints MUST validate CSRF tokens."""

    def test_csrf_generator_exists(self):
        import src.app.standalone_auth as m
        assert hasattr(m, "_generate_csrf_token")

    def test_csrf_tokens_are_random(self):
        import src.app.standalone_auth as m
        if hasattr(m, "_generate_csrf_token"):
            t1, t2 = m._generate_csrf_token(), m._generate_csrf_token()
            assert t1 != t2
            assert len(t1) >= 32

    def test_csrf_validator_exists(self):
        import src.app.standalone_auth as m
        assert hasattr(m, "_validate_csrf_token")

    def test_csrf_rejects_invalid(self):
        import src.app.standalone_auth as m
        if hasattr(m, "_validate_csrf_token"):
            assert m._validate_csrf_token("", "real") is False
            assert m._validate_csrf_token("wrong", "real") is False

    def test_csrf_accepts_valid(self):
        import src.app.standalone_auth as m
        if hasattr(m, "_validate_csrf_token") and hasattr(m, "_generate_csrf_token"):
            t = m._generate_csrf_token()
            assert m._validate_csrf_token(t, t) is True

    def test_render_login_html_exists(self):
        import src.app.standalone_auth as m
        assert hasattr(m, "_render_login_html")

    def test_login_html_has_csrf_field(self):
        import src.app.standalone_auth as m
        if hasattr(m, "_render_login_html"):
            html = m._render_login_html()
            assert "csrf_token" in html
            assert 'type="hidden"' in html


class TestPasswordPolicy:
    """SPEC-1691: Password minimum MUST be 12 characters."""

    def test_min_password_length_constant(self):
        import src.app.standalone_auth as m
        val = getattr(m, "_MIN_PASSWORD_LENGTH", None)
        assert val is not None, "Missing _MIN_PASSWORD_LENGTH"
        assert val >= 12

    def test_reset_html_no_minlength_6(self):
        import src.app.standalone_auth as m
        html = getattr(m, "_STANDALONE_RESET_PW_HTML", "")
        assert 'minlength="6"' not in html
