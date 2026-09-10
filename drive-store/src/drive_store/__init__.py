"""Use a Google Drive folder as a file store.

    from drive_store import DriveStore

    store = DriveStore(root_id="1AbC...", app="my_project")
    store.upload("local/data.csv", "inputs/data.csv")
    df = store.read_csv("outputs/results.csv")
"""

from .auth import (
    DRIVE_FILE_SCOPE,
    DRIVE_FULL_SCOPE,
    clear_credentials,
    get_credentials,
)
from .store import DriveFile, DriveStore

__version__ = "0.1.0"

__all__ = [
    "DriveStore",
    "DriveFile",
    "get_credentials",
    "clear_credentials",
    "DRIVE_FILE_SCOPE",
    "DRIVE_FULL_SCOPE",
]
