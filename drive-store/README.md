# drive-store

Use a Google Drive folder as a file store, with a filesystem-ish API.

```python
from drive_store import DriveStore

store = DriveStore(root_id="1AbC...", app="my_project")

store.upload("local/data.geojson", "inputs/data.geojson")
df   = store.read_csv("outputs/results.csv")
gdf  = store.read_geojson("inputs/data.geojson")

store.push("./outdir", "outputs")     # dir upload, skips unchanged by md5
store.pull("outputs", "./outdir")
store.snapshot("outputs")             # server-side copy under snapshots/<ts>/
```

## Install

```bash
pip install -e .            # core
pip install -e '.[pandas]'  # read_csv / write_csv / parquet
pip install -e '.[geo]'     # read_geojson / write_geojson
```

## Auth

Two modes, tried in order.

**Service account** — set `GOOGLE_SERVICE_ACCOUNT_FILE`. Best for headless or
scheduled runs. Share the target folder with the service account's client email
as you would with a person.

> Service accounts have no Drive storage quota of their own. They can read and
> update existing files, but cannot *own* new uploads outside a Shared Drive.
> For write workloads on a consumer account, use OAuth.

**OAuth installed-app flow** — interactive. Put a Desktop-app client secrets
JSON at `~/.config/drive_store/client_secret.json` (or
`<app>-client_secret.json` to scope it to one project). First run opens a
browser; the refresh token is cached at mode 600 for silent reuse.

Tokens are cached per `(app, scopes)` pair. This is deliberate: a token carries
the scopes it was granted under, so reusing one cached under a *different*
scope set yields credentials silently missing the permissions you asked for.
Keying on scopes makes changing them re-prompt instead of failing obscurely.

### Which scope?

Default is `drive.file` — per-file access, limited to files this app creates.
Prefer it. The full `drive` scope is **restricted**: publishing an app that
requests it requires Google verification (up to a third-party security
assessment), and an unpublished app sits in *Testing* status where refresh
tokens expire after **7 days**. `drive.file` is non-sensitive, so the app
publishes immediately and its tokens persist.

The cost of `drive.file` is that the store sees only files it created — not
ones a collaborator adds by hand. Pass `scopes=DRIVE_FULL_SCOPE` if you need
that and are willing to pay the verification cost.

### Publishing an OAuth app (the parts that aren't obvious)

To reach *In production* — required to escape the 7-day token expiry — Google
demands a homepage URL **and** a privacy policy URL, both on a domain listed
under Authorized Domains and verified in Search Console.

`github.io` will not work. It's on the Public Suffix List, so Google treats it
as not-registered-to-you and rejects it, even though Search Console verifies
the subdomain happily. Use a domain you actually registered.

Note that *branding* verification is separate from publishing status. An app
can be In production with branding verification still pending — that only
affects whether your app name and logo render on the consent screen.

## Storage quota

A file is owned by whoever uploads it and counts against **that account's**
quota, regardless of who owns the enclosing folder. Uploading into a folder
someone shared with you consumes *your* quota, not theirs. Only a Shared Drive
(Google Workspace) makes the drive itself the owner.

## Behavior worth knowing

**Writes are upserts.** Drive permits several files with the same name in one
folder. Every write looks up the existing file by name+parent and updates it in
place, so a path stays one file and keeps Drive's native version history. If
duplicates already exist, the store logs a warning and uses the first.

**md5 short-circuit.** `push`/`pull` compare Drive's `md5Checksum` against a
local hash and skip unchanged files.

**Google-native files raise on read.** A Google Doc or Sheet has no byte stream
and no md5. `read_bytes` raises with a clear message rather than returning
something surprising — store tabular data as CSV/XLSX.

**Snapshots are server-side copies.** `snapshot()` uses Drive's `files.copy`,
so archiving costs no upload bandwidth (it does consume quota).

## CLI

```bash
export DRIVE_FOLDER_ID=1AbC...

drive-store ls -r
drive-store put ./local.csv inputs/local.csv
drive-store get outputs/results.csv ./results.csv
drive-store push ./outdir outputs
drive-store pull outputs ./outdir
drive-store snapshot outputs
drive-store logout                 # clear the cached token
drive-store --no-browser ls        # headless
```

## Scope of this library

Google Drive only. It cannot see **Google Photos** — Google separated the two
services in 2019, and Photos has its own API with its own (much narrower)
access rules. Drive API calls will not find, list, or delete anything in your
Photos library.
