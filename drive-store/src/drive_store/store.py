"""A Google Drive folder as a file store, with a filesystem-ish API.

Paths are POSIX-style and relative to the store root, e.g. ``inputs/data.csv``.
Intermediate folders are created on write.

    from drive_store import DriveStore

    store = DriveStore(root_id="1AbC...", app="my_project")
    store.upload("local/data.geojson", "inputs/data.geojson")
    df = store.read_csv("outputs/results.csv")

Drive allows several files to share a name inside one folder. Every write here
is an *upsert* — it looks for an existing file with that name and updates it in
place, so a given path stays a single file with Drive-native version history.

Storage note: in Drive a file is owned by whoever uploads it, and counts
against *that* account's quota regardless of who owns the enclosing folder.
Uploading into a folder someone shared with you consumes your own quota, not
theirs. Only a Shared Drive (Google Workspace) makes the drive itself the owner.
"""

from __future__ import annotations

import hashlib
import io
import logging
import mimetypes
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload, MediaIoBaseUpload

from .auth import DRIVE_FILE_SCOPE, get_credentials

logger = logging.getLogger(__name__)

FOLDER_MIME = "application/vnd.google-apps.folder"

# Fields worth pulling back on every file lookup.
_FILE_FIELDS = "id, name, mimeType, size, md5Checksum, modifiedTime, parents"

# Google-native types have no byte stream to download and no md5.
_GOOGLE_NATIVE_PREFIX = "application/vnd.google-apps."


@dataclass(frozen=True)
class DriveFile:
    """A file in the store."""

    id: str
    name: str
    path: str
    mime_type: str
    size: int | None
    md5: str | None
    modified: str | None

    @property
    def is_folder(self) -> bool:
        return self.mime_type == FOLDER_MIME

    @property
    def view_url(self) -> str:
        return f"https://drive.google.com/file/d/{self.id}/view"


def _escape(value: str) -> str:
    """Escape a string for embedding in a Drive query literal."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def _md5(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def _split(remote_path: str) -> tuple[str, str]:
    """Split 'inputs/raw/file.csv' into ('inputs/raw', 'file.csv')."""
    clean = remote_path.strip().strip("/").strip()
    if not clean:
        raise ValueError(f"remote_path must name a file, got {remote_path!r}")
    if "/" not in clean:
        return "", clean
    parent, _, name = clean.rpartition("/")
    if not name.strip():
        raise ValueError(f"remote_path must end in a filename, got {remote_path!r}")
    return parent.strip("/"), name


class DriveStore:
    """Read/write access to one Drive folder tree.

    Args:
        root_id: Drive folder ID to use as the store root. Falls back to the
            ``DRIVE_FOLDER_ID`` env var. The ID is the trailing path segment of
            a folder URL: ``drive.google.com/drive/folders/<root_id>``.
        app: Namespace for the cached OAuth token, so separate projects using
            this library don't overwrite each other's credentials.
        scopes: OAuth scopes. Defaults to ``drive.file`` (per-file access to
            files this app creates); pass ``DRIVE_FULL_SCOPE`` to also see
            files created by others, at the cost of Google verification.
        credentials: Pre-built credentials. Built from the environment if omitted.
        open_browser: Passed to the OAuth flow on first auth. Set False on a
            headless machine.
    """

    def __init__(
        self,
        root_id: str | None = None,
        app: str = "default",
        *,
        scopes: str | list[str] = DRIVE_FILE_SCOPE,
        credentials=None,
        open_browser: bool = True,
    ):
        root_id = root_id or os.environ.get("DRIVE_FOLDER_ID")
        if not root_id:
            raise ValueError(
                "No Drive folder given. Pass root_id= or set DRIVE_FOLDER_ID. "
                "The ID is the last path segment of the folder's URL: "
                "https://drive.google.com/drive/folders/<root_id>"
            )
        self.root_id = root_id
        creds = credentials or get_credentials(
            scopes=scopes, app=app, open_browser=open_browser
        )
        self._service = build("drive", "v3", credentials=creds, cache_discovery=False)
        # remote dir path -> folder id
        self._dir_cache: dict[str, str] = {"": self.root_id}

    # ── internals ─────────────────────────────────────────────────────────

    @property
    def _files(self):
        return self._service.files()

    def _find_child(self, parent_id: str, name: str) -> dict | None:
        query = (
            f"name = '{_escape(name)}' and "
            f"'{_escape(parent_id)}' in parents and trashed = false"
        )
        resp = self._files.list(
            q=query,
            fields=f"files({_FILE_FIELDS})",
            pageSize=2,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
        ).execute()
        files = resp.get("files", [])
        if len(files) > 1:
            logger.warning(
                "%d files named %r share a parent; using the first. "
                "Drive permits duplicate names — consider cleaning this up.",
                len(files),
                name,
            )
        return files[0] if files else None

    def _ensure_dir(self, remote_dir: str) -> str:
        """Return the folder ID for a remote dir, creating missing levels."""
        remote_dir = remote_dir.strip("/")
        if remote_dir in self._dir_cache:
            return self._dir_cache[remote_dir]

        parent_id = self.root_id
        walked: list[str] = []
        for part in remote_dir.split("/"):
            walked.append(part)
            key = "/".join(walked)
            if key in self._dir_cache:
                parent_id = self._dir_cache[key]
                continue

            existing = self._find_child(parent_id, part)
            if existing and existing["mimeType"] == FOLDER_MIME:
                parent_id = existing["id"]
            elif existing:
                raise NotADirectoryError(
                    f"{key!r} exists in Drive but is a file, not a folder"
                )
            else:
                created = self._files.create(
                    body={
                        "name": part,
                        "mimeType": FOLDER_MIME,
                        "parents": [parent_id],
                    },
                    fields="id",
                    supportsAllDrives=True,
                ).execute()
                parent_id = created["id"]
                logger.info("Created Drive folder %s", key)
            self._dir_cache[key] = parent_id

        return parent_id

    def _resolve_dir(self, remote_dir: str) -> str | None:
        """Folder ID for a remote dir, or None if any level is missing."""
        remote_dir = remote_dir.strip("/")
        if remote_dir in self._dir_cache:
            return self._dir_cache[remote_dir]

        parent_id = self.root_id
        walked: list[str] = []
        for part in remote_dir.split("/"):
            walked.append(part)
            key = "/".join(walked)
            if key in self._dir_cache:
                parent_id = self._dir_cache[key]
                continue
            found = self._find_child(parent_id, part)
            if not found or found["mimeType"] != FOLDER_MIME:
                return None
            parent_id = found["id"]
            self._dir_cache[key] = parent_id
        return parent_id

    @staticmethod
    def _to_drive_file(raw: dict, path: str) -> DriveFile:
        size = raw.get("size")
        return DriveFile(
            id=raw["id"],
            name=raw["name"],
            path=path,
            mime_type=raw.get("mimeType", ""),
            size=int(size) if size is not None else None,
            md5=raw.get("md5Checksum"),
            modified=raw.get("modifiedTime"),
        )

    # ── metadata ──────────────────────────────────────────────────────────

    def stat(self, remote_path: str) -> DriveFile | None:
        """Metadata for a path, or None if it doesn't exist."""
        parent, name = _split(remote_path)
        parent_id = self._resolve_dir(parent) if parent else self.root_id
        if parent_id is None:
            return None
        raw = self._find_child(parent_id, name)
        return self._to_drive_file(raw, remote_path.strip("/")) if raw else None

    def exists(self, remote_path: str) -> bool:
        return self.stat(remote_path) is not None

    def list_dir(self, remote_dir: str = "") -> list[DriveFile]:
        """List one directory (non-recursive). Missing dir returns []."""
        parent_id = self._resolve_dir(remote_dir) if remote_dir.strip("/") else self.root_id
        if parent_id is None:
            return []

        prefix = remote_dir.strip("/")
        out: list[DriveFile] = []
        page_token = None
        while True:
            resp = self._files.list(
                q=f"'{_escape(parent_id)}' in parents and trashed = false",
                fields=f"nextPageToken, files({_FILE_FIELDS})",
                pageSize=1000,
                pageToken=page_token,
                orderBy="folder,name",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            ).execute()
            for raw in resp.get("files", []):
                path = f"{prefix}/{raw['name']}" if prefix else raw["name"]
                out.append(self._to_drive_file(raw, path))
            page_token = resp.get("nextPageToken")
            if not page_token:
                return out

    def walk(self, remote_dir: str = "") -> list[DriveFile]:
        """Recursively list all non-folder files under a directory."""
        out: list[DriveFile] = []
        for entry in self.list_dir(remote_dir):
            if entry.is_folder:
                out.extend(self.walk(entry.path))
            else:
                out.append(entry)
        return out

    # ── bytes ─────────────────────────────────────────────────────────────

    def write_bytes(
        self, data: bytes, remote_path: str, mime_type: str | None = None
    ) -> DriveFile:
        """Upsert raw bytes to a path."""
        parent, name = _split(remote_path)
        parent_id = self._ensure_dir(parent) if parent else self.root_id
        mime_type = mime_type or mimetypes.guess_type(name)[0] or "application/octet-stream"

        media = MediaIoBaseUpload(
            io.BytesIO(data), mimetype=mime_type, resumable=len(data) > 5 * 1024 * 1024
        )
        existing = self._find_child(parent_id, name)
        if existing:
            raw = self._files.update(
                fileId=existing["id"],
                media_body=media,
                fields=_FILE_FIELDS,
                supportsAllDrives=True,
            ).execute()
            logger.info("Updated drive://%s (%d bytes)", remote_path, len(data))
        else:
            raw = self._files.create(
                body={"name": name, "parents": [parent_id]},
                media_body=media,
                fields=_FILE_FIELDS,
                supportsAllDrives=True,
            ).execute()
            logger.info("Created drive://%s (%d bytes)", remote_path, len(data))
        return self._to_drive_file(raw, remote_path.strip("/"))

    def read_bytes(self, remote_path: str) -> bytes:
        """Download a file's contents."""
        meta = self.stat(remote_path)
        if meta is None:
            raise FileNotFoundError(f"drive://{remote_path}")
        if meta.mime_type.startswith(_GOOGLE_NATIVE_PREFIX):
            raise ValueError(
                f"{remote_path} is a Google-native file ({meta.mime_type}); "
                "export it manually or store it as CSV/XLSX instead."
            )

        buf = io.BytesIO()
        downloader = MediaIoBaseDownload(
            buf, self._files.get_media(fileId=meta.id, supportsAllDrives=True)
        )
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return buf.getvalue()

    # ── files ─────────────────────────────────────────────────────────────

    def upload(self, local_path: str | Path, remote_path: str | None = None) -> DriveFile:
        """Upsert a local file. Defaults the remote name to the local filename."""
        local = Path(local_path)
        if not local.is_file():
            raise FileNotFoundError(local)
        remote_path = remote_path or local.name

        parent, name = _split(remote_path)
        parent_id = self._ensure_dir(parent) if parent else self.root_id
        mime_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
        media = MediaFileUpload(
            str(local),
            mimetype=mime_type,
            resumable=local.stat().st_size > 5 * 1024 * 1024,
        )

        existing = self._find_child(parent_id, name)
        if existing:
            raw = self._files.update(
                fileId=existing["id"],
                media_body=media,
                fields=_FILE_FIELDS,
                supportsAllDrives=True,
            ).execute()
            logger.info("Updated drive://%s", remote_path)
        else:
            raw = self._files.create(
                body={"name": name, "parents": [parent_id]},
                media_body=media,
                fields=_FILE_FIELDS,
                supportsAllDrives=True,
            ).execute()
            logger.info("Created drive://%s", remote_path)
        return self._to_drive_file(raw, remote_path.strip("/"))

    def download(self, remote_path: str, local_path: str | Path) -> Path:
        """Download to a local path, creating parent directories."""
        local = Path(local_path)
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(self.read_bytes(remote_path))
        logger.info("Downloaded drive://%s -> %s", remote_path, local)
        return local

    def delete(self, remote_path: str) -> bool:
        """Move a path to Drive's trash. Returns False if it wasn't there."""
        meta = self.stat(remote_path)
        if meta is None:
            return False
        self._files.update(
            fileId=meta.id, body={"trashed": True}, supportsAllDrives=True
        ).execute()
        self._dir_cache.pop(remote_path.strip("/"), None)
        logger.info("Trashed drive://%s", remote_path)
        return True

    # ── dataframe / structured helpers ────────────────────────────────────

    def write_csv(self, df, remote_path: str, **to_csv_kwargs) -> DriveFile:
        to_csv_kwargs.setdefault("index", False)
        return self.write_bytes(
            df.to_csv(**to_csv_kwargs).encode("utf-8"), remote_path, "text/csv"
        )

    def read_csv(self, remote_path: str, **read_csv_kwargs):
        import pandas as pd

        return pd.read_csv(io.BytesIO(self.read_bytes(remote_path)), **read_csv_kwargs)

    def write_parquet(self, df, remote_path: str, **kwargs) -> DriveFile:
        buf = io.BytesIO()
        df.to_parquet(buf, **kwargs)
        return self.write_bytes(buf.getvalue(), remote_path, "application/octet-stream")

    def read_parquet(self, remote_path: str, **kwargs):
        import pandas as pd

        return pd.read_parquet(io.BytesIO(self.read_bytes(remote_path)), **kwargs)

    def write_geojson(self, gdf, remote_path: str) -> DriveFile:
        """Write a GeoDataFrame, reprojecting to EPSG:4326 (GeoJSON's CRS)."""
        if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")
        return self.write_bytes(
            gdf.to_json().encode("utf-8"), remote_path, "application/geo+json"
        )

    def read_geojson(self, remote_path: str):
        import geopandas as gpd

        return gpd.read_file(io.BytesIO(self.read_bytes(remote_path)))

    def write_json(self, obj, remote_path: str, indent: int = 2) -> DriveFile:
        import json

        return self.write_bytes(
            json.dumps(obj, indent=indent, default=str).encode("utf-8"),
            remote_path,
            "application/json",
        )

    def read_json(self, remote_path: str):
        import json

        return json.loads(self.read_bytes(remote_path))

    # ── bulk sync ─────────────────────────────────────────────────────────

    def push(
        self,
        local_dir: str | Path,
        remote_dir: str,
        pattern: str = "*",
        recursive: bool = True,
        skip_unchanged: bool = True,
    ) -> dict[str, list[str]]:
        """Upload a local directory. Unchanged files are skipped by md5.

        Returns a dict with 'uploaded' and 'skipped' path lists.
        """
        local_root = Path(local_dir)
        if not local_root.is_dir():
            raise NotADirectoryError(local_root)

        globber = local_root.rglob if recursive else local_root.glob
        result: dict[str, list[str]] = {"uploaded": [], "skipped": []}

        for local_file in sorted(p for p in globber(pattern) if p.is_file()):
            rel = local_file.relative_to(local_root).as_posix()
            remote_path = f"{remote_dir.strip('/')}/{rel}" if remote_dir.strip("/") else rel

            if skip_unchanged:
                meta = self.stat(remote_path)
                if meta and meta.md5 and meta.md5 == _md5(local_file):
                    result["skipped"].append(remote_path)
                    continue

            self.upload(local_file, remote_path)
            result["uploaded"].append(remote_path)

        logger.info(
            "push %s -> drive://%s: %d uploaded, %d unchanged",
            local_root,
            remote_dir,
            len(result["uploaded"]),
            len(result["skipped"]),
        )
        return result

    def pull(
        self,
        remote_dir: str,
        local_dir: str | Path,
        skip_unchanged: bool = True,
    ) -> dict[str, list[str]]:
        """Download a remote directory tree, skipping files that match by md5."""
        local_root = Path(local_dir)
        prefix = remote_dir.strip("/")
        result: dict[str, list[str]] = {"downloaded": [], "skipped": []}

        for entry in self.walk(remote_dir):
            rel = entry.path[len(prefix) :].lstrip("/") if prefix else entry.path
            target = local_root / rel

            if entry.mime_type.startswith(_GOOGLE_NATIVE_PREFIX):
                logger.warning("Skipping Google-native file %s", entry.path)
                result["skipped"].append(entry.path)
                continue

            if (
                skip_unchanged
                and target.exists()
                and entry.md5
                and entry.md5 == _md5(target)
            ):
                result["skipped"].append(entry.path)
                continue

            self.download(entry.path, target)
            result["downloaded"].append(entry.path)

        logger.info(
            "pull drive://%s -> %s: %d downloaded, %d unchanged",
            remote_dir,
            local_root,
            len(result["downloaded"]),
            len(result["skipped"]),
        )
        return result

    def snapshot(self, remote_dir: str, label: str | None = None) -> str:
        """Copy a directory's files to ``snapshots/<label>/`` for a point-in-time
        archive. Uses server-side copies, so nothing is re-uploaded.

        Returns the snapshot directory path.
        """
        label = label or datetime.now().strftime("%Y-%m-%d_%H%M%S")
        dest_dir = f"snapshots/{label}"
        dest_id = self._ensure_dir(dest_dir)

        for entry in self.walk(remote_dir):
            self._files.copy(
                fileId=entry.id,
                body={"name": entry.name, "parents": [dest_id]},
                fields="id",
                supportsAllDrives=True,
            ).execute()

        logger.info("Snapshotted drive://%s -> drive://%s", remote_dir, dest_dir)
        return dest_dir
