"""Command-line interface for a Drive-backed file store.

    export DRIVE_FOLDER_ID=1AbC...
    drive-store ls -r
    drive-store put ./local.csv inputs/local.csv
    drive-store get outputs/results.csv ./results.csv
    drive-store push ./outdir outputs
    drive-store pull outputs ./outdir
"""

from __future__ import annotations

import argparse
import logging
import sys

from .auth import DRIVE_FULL_SCOPE, clear_credentials
from .store import DriveStore


def _human(size: int | None) -> str:
    if size is None:
        return "—"
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.0f}{unit}" if unit == "B" else f"{value:.1f}{unit}"
        value /= 1024
    return f"{value:.1f}GB"


def _store(args) -> DriveStore:
    kwargs = {"app": args.app, "open_browser": not args.no_browser}
    if args.root_id:
        kwargs["root_id"] = args.root_id
    if args.full_scope:
        kwargs["scopes"] = DRIVE_FULL_SCOPE
    return DriveStore(**kwargs)


def _cmd_ls(args) -> int:
    store = _store(args)
    entries = store.walk(args.path) if args.recursive else store.list_dir(args.path)
    if not entries:
        print(f"(empty: drive://{args.path or '/'})")
        return 0
    for e in entries:
        kind = "dir " if e.is_folder else "file"
        print(f"{kind}  {_human(e.size):>8}  {e.modified or '':<25}  {e.path}")
    return 0


def _cmd_get(args) -> int:
    print(_store(args).download(args.remote, args.local))
    return 0


def _cmd_put(args) -> int:
    meta = _store(args).upload(args.local, args.remote)
    print(f"{meta.path}  {meta.view_url}")
    return 0


def _cmd_push(args) -> int:
    r = _store(args).push(args.local_dir, args.remote_dir, pattern=args.pattern)
    print(f"uploaded={len(r['uploaded'])} unchanged={len(r['skipped'])}")
    return 0


def _cmd_pull(args) -> int:
    r = _store(args).pull(args.remote_dir, args.local_dir)
    print(f"downloaded={len(r['downloaded'])} unchanged={len(r['skipped'])}")
    return 0


def _cmd_rm(args) -> int:
    print("trashed" if _store(args).delete(args.remote) else "not found")
    return 0


def _cmd_snapshot(args) -> int:
    print(_store(args).snapshot(args.remote_dir, args.label))
    return 0


def _cmd_logout(args) -> int:
    scopes = DRIVE_FULL_SCOPE if args.full_scope else None
    removed = (
        clear_credentials(args.app, scopes) if scopes else clear_credentials(args.app)
    )
    print("cleared cached token" if removed else "no cached token")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="drive-store", description="Use a Google Drive folder as a file store"
    )
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--app", default="default", help="token namespace (default: default)")
    p.add_argument("--root-id", default=None, help="Drive folder ID (or DRIVE_FOLDER_ID)")
    p.add_argument(
        "--full-scope",
        action="store_true",
        help="request full drive scope instead of drive.file (needs verification to publish)",
    )
    p.add_argument(
        "--no-browser", action="store_true", help="don't open a browser during OAuth"
    )
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("ls", help="list a directory")
    s.add_argument("path", nargs="?", default="")
    s.add_argument("-r", "--recursive", action="store_true")
    s.set_defaults(func=_cmd_ls)

    s = sub.add_parser("get", help="download one file")
    s.add_argument("remote")
    s.add_argument("local")
    s.set_defaults(func=_cmd_get)

    s = sub.add_parser("put", help="upload one file")
    s.add_argument("local")
    s.add_argument("remote", nargs="?", default=None)
    s.set_defaults(func=_cmd_put)

    s = sub.add_parser("push", help="upload a directory (skips unchanged)")
    s.add_argument("local_dir")
    s.add_argument("remote_dir")
    s.add_argument("--pattern", default="*")
    s.set_defaults(func=_cmd_push)

    s = sub.add_parser("pull", help="download a directory (skips unchanged)")
    s.add_argument("remote_dir")
    s.add_argument("local_dir")
    s.set_defaults(func=_cmd_pull)

    s = sub.add_parser("rm", help="move a file to Drive's trash")
    s.add_argument("remote")
    s.set_defaults(func=_cmd_rm)

    s = sub.add_parser("snapshot", help="archive a directory under snapshots/")
    s.add_argument("remote_dir")
    s.add_argument("--label", default=None)
    s.set_defaults(func=_cmd_snapshot)

    s = sub.add_parser("logout", help="delete the cached OAuth token")
    s.set_defaults(func=_cmd_logout)

    args = p.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
