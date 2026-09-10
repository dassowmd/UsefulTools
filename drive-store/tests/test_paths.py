"""Tests for the pure helpers — no Drive credentials required."""

import hashlib

import pytest

from drive_store.auth import _scope_digest, client_secrets_path, token_path
from drive_store.store import DriveFile, FOLDER_MIME, _escape, _md5, _split


class TestSplit:
    def test_bare_filename(self):
        assert _split("a.csv") == ("", "a.csv")

    def test_nested(self):
        assert _split("inputs/a.csv") == ("inputs", "a.csv")

    def test_deeply_nested(self):
        assert _split("a/b/c/d.csv") == ("a/b/c", "d.csv")

    def test_strips_surrounding_slashes_and_space(self):
        assert _split("  /inputs/sub/a.csv/  ") == ("inputs/sub", "a.csv")

    @pytest.mark.parametrize("bad", ["", "   ", "/", "///"])
    def test_rejects_empty(self, bad):
        with pytest.raises(ValueError):
            _split(bad)


class TestEscape:
    def test_single_quote(self):
        # Drive query literals are single-quoted, so quotes must be escaped
        # or a filename like O'Brien breaks the query.
        assert _escape("O'Brien") == "O\\'Brien"

    def test_backslash(self):
        assert _escape("back\\slash") == "back\\\\slash"

    def test_backslash_escaped_before_quote(self):
        # Order matters: escaping the quote first would double-escape the
        # backslash introduced by it.
        assert _escape("\\'") == "\\\\\\'"

    def test_plain_untouched(self):
        assert _escape("ordinary_name.csv") == "ordinary_name.csv"


class TestMd5:
    def test_matches_hashlib(self, tmp_path):
        f = tmp_path / "x.bin"
        f.write_bytes(b"hello drive store")
        assert _md5(f) == hashlib.md5(b"hello drive store").hexdigest()

    def test_chunked_read_matches(self, tmp_path):
        payload = b"a" * (1024 * 1024 * 2 + 7)  # spans multiple chunks
        f = tmp_path / "big.bin"
        f.write_bytes(payload)
        assert _md5(f) == hashlib.md5(payload).hexdigest()

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.bin"
        f.write_bytes(b"")
        assert _md5(f) == hashlib.md5(b"").hexdigest()


class TestDriveFile:
    def test_file_is_not_folder(self):
        f = DriveFile("id1", "a.csv", "in/a.csv", "text/csv", 10, "m", None)
        assert not f.is_folder
        assert "id1" in f.view_url

    def test_folder_detected(self):
        d = DriveFile("id2", "in", "in", FOLDER_MIME, None, None, None)
        assert d.is_folder


class TestTokenPaths:
    def test_scope_digest_is_order_independent(self):
        # Same scope set in a different order must map to one cache entry.
        a = _scope_digest(["scope/b", "scope/a"])
        b = _scope_digest(["scope/a", "scope/b"])
        assert a == b

    def test_different_scopes_differ(self):
        assert _scope_digest(["scope/a"]) != _scope_digest(["scope/b"])

    def test_token_path_varies_by_scope(self, tmp_path):
        """The bug this guards: reusing a token cached under different scopes
        yields credentials silently missing the permissions you asked for."""
        narrow = token_path("app", "https://www.googleapis.com/auth/drive.file", tmp_path)
        full = token_path("app", "https://www.googleapis.com/auth/drive", tmp_path)
        assert narrow != full

    def test_token_path_varies_by_app(self, tmp_path):
        assert token_path("one", "s", tmp_path) != token_path("two", "s", tmp_path)

    def test_accepts_str_or_list(self, tmp_path):
        assert token_path("app", "s", tmp_path) == token_path("app", ["s"], tmp_path)

    def test_client_secrets_prefers_app_specific(self, tmp_path):
        shared = tmp_path / "client_secret.json"
        shared.write_text("{}")
        assert client_secrets_path("myapp", tmp_path) == shared

        specific = tmp_path / "myapp-client_secret.json"
        specific.write_text("{}")
        assert client_secrets_path("myapp", tmp_path) == specific
