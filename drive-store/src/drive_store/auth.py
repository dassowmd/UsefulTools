"""Google API credentials: service account or OAuth installed-app flow.

Two modes, tried in this order:

1. **Service account** — set ``GOOGLE_SERVICE_ACCOUNT_FILE`` (or pass
   ``service_account_file``). Best for headless/scheduled runs. Share the
   target resource with the service account's client email, as you would with
   a person. Note that service accounts have no Drive storage quota of their
   own, so they can read and update but cannot own new uploads outside a
   Shared Drive.

2. **OAuth installed-app flow** — interactive. First run opens a browser to
   consent, then caches a refresh token so later runs are silent.

Tokens are cached per ``(app, scopes)`` pair. That matters: a token carries the
scopes it was granted under, so reusing one cached under a different scope set
silently yields credentials lacking the permissions you asked for. Keying the
cache on scopes makes changing them re-prompt instead of failing obscurely.
"""

from __future__ import annotations

import hashlib
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_DIR = Path(
    os.environ.get("DRIVE_STORE_CONFIG_DIR", Path.home() / ".config" / "drive_store")
)

# Per-file access, limited to files this app creates. Preferred over the full
# "drive" scope: "drive" is *restricted*, and publishing an app that requests it
# requires Google verification. An unpublished app sits in Testing status, where
# refresh tokens expire after 7 days. drive.file is non-sensitive, so the app
# publishes immediately and its tokens persist.
DRIVE_FILE_SCOPE = "https://www.googleapis.com/auth/drive.file"

# Full access, including files the app did not create. Requires verification to
# publish; expect the 7-day token expiry until that clears.
DRIVE_FULL_SCOPE = "https://www.googleapis.com/auth/drive"


def _normalize(scopes: str | list[str]) -> list[str]:
    if isinstance(scopes, str):
        return [scopes]
    if not scopes:
        raise ValueError("scopes must not be empty")
    return list(scopes)


def _scope_digest(scopes: list[str]) -> str:
    """Short stable hash of a scope set, used in the token filename."""
    return hashlib.sha256(" ".join(sorted(scopes)).encode()).hexdigest()[:8]


def token_path(
    app: str, scopes: str | list[str], config_dir: Path | None = None
) -> Path:
    """Where the cached OAuth token for this (app, scopes) pair lives."""
    base = Path(config_dir) if config_dir else DEFAULT_CONFIG_DIR
    return base / f"{app}-{_scope_digest(_normalize(scopes))}.json"


def client_secrets_path(app: str, config_dir: Path | None = None) -> Path:
    """Where the OAuth client secrets JSON is expected.

    Prefers an app-specific file, falling back to a shared one, so several
    projects can share a single desktop client if you'd rather not create one
    per project.
    """
    base = Path(config_dir) if config_dir else DEFAULT_CONFIG_DIR
    specific = base / f"{app}-client_secret.json"
    return specific if specific.exists() else base / "client_secret.json"


def _service_account_credentials(key_file: Path, scopes: list[str]):
    from google.oauth2 import service_account

    logger.debug("Authenticating with service account %s", key_file)
    return service_account.Credentials.from_service_account_file(
        str(key_file), scopes=scopes
    )


def _oauth_credentials(
    client_file: Path, token_file: Path, scopes: list[str], open_browser: bool
):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), scopes)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        logger.debug("Refreshing expired token %s", token_file.name)
        try:
            creds.refresh(Request())
        except Exception as exc:
            # Revoked, or the app is in Testing and the 7-day refresh window
            # lapsed. Fall through to fresh consent rather than dying.
            logger.warning("Token refresh failed (%s); re-authenticating", exc)
            creds = None

    if not creds or not creds.valid:
        if not client_file.exists():
            raise FileNotFoundError(
                f"No OAuth client secrets at {client_file}.\n"
                "Create an OAuth client ID (type: Desktop app) at "
                "https://console.cloud.google.com/apis/credentials, enable the "
                "Drive API, download the JSON, and save it there — or pass "
                "client_file= / set DRIVE_STORE_CONFIG_DIR."
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(client_file), scopes)
        # port=0 picks a free port. On a headless box use open_browser=False and
        # forward the port over SSH (-L), or paste the printed URL elsewhere.
        creds = flow.run_local_server(port=0, open_browser=open_browser)

    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text(creds.to_json())
    token_file.chmod(0o600)
    logger.debug("Cached token at %s", token_file)
    return creds


def get_credentials(
    scopes: str | list[str] = DRIVE_FILE_SCOPE,
    app: str = "default",
    *,
    service_account_file: str | Path | None = None,
    client_file: str | Path | None = None,
    config_dir: str | Path | None = None,
    open_browser: bool = True,
):
    """Return Google API credentials, preferring a service account if configured.

    Args:
        scopes: One scope string or a list. Defaults to ``drive.file``.
        app: Namespace for the cached token, so separate projects don't
            overwrite each other's credentials.
        service_account_file: Service account JSON key. Falls back to the
            ``GOOGLE_SERVICE_ACCOUNT_FILE`` env var.
        client_file: OAuth client secrets JSON. Defaults to the app-specific
            then shared file under the config dir.
        config_dir: Override the credential directory
            (``DRIVE_STORE_CONFIG_DIR``, else ``~/.config/drive_store``).
        open_browser: Set False on machines with no browser.
    """
    scopes = _normalize(scopes)
    base = Path(config_dir) if config_dir else DEFAULT_CONFIG_DIR

    sa_file = service_account_file or os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    if sa_file:
        path = Path(sa_file).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"Service account key not found: {path}")
        return _service_account_credentials(path, scopes)

    resolved_client = (
        Path(client_file).expanduser() if client_file else client_secrets_path(app, base)
    )
    return _oauth_credentials(
        resolved_client, token_path(app, scopes, base), scopes, open_browser
    )


def clear_credentials(
    app: str,
    scopes: str | list[str] = DRIVE_FILE_SCOPE,
    config_dir: str | Path | None = None,
) -> bool:
    """Delete the cached token for an (app, scopes) pair.

    Forces fresh consent on the next call. Returns False if nothing was cached.
    Clears only the local copy — to withdraw access entirely, revoke the app at
    https://myaccount.google.com/permissions.
    """
    path = token_path(app, scopes, Path(config_dir) if config_dir else None)
    if path.exists():
        path.unlink()
        logger.info("Removed cached token %s", path)
        return True
    return False
