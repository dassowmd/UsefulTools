from pathlib import Path
import sys
import os
import send2trash
import shutil

from tqdm import tqdm
import logging
from DuplicateFiles import createShortcut
logger = logging.getLogger(__name__)
loghandler = logging.StreamHandler()
logger.setLevel(logging.ERROR)
loghandler.setLevel(logging.DEBUG)
logger.addHandler(loghandler)
extensions_to_delete = [
    '.exe', '.jar', '.ini'
]
path_parts_to_delete = [
    'AppData', 'Program Files', 'WindowsApps'
]
unhandled_file_extensions = set()


def list_file_paths(parentFolder):
    for dirName, subdirs, fileList in tqdm(os.walk(parentFolder)):
        # Get the path for the file
        for filename in fileList:
            # Get the path to the file
            path = os.path.join(dirName, filename)
            if Path(path).suffix not in ['.lnk']:
                yield path

def delete_file(file_path):
    if Path(file_path).suffix.lower() in extensions_to_delete:
        send2trash.send2trash(file_path)
        logger.info(f"{file_path} deleted")
    for part in path_parts_to_delete:
        if part in Path(file_path).parts:
            send2trash.send2trash(file_path)
            logger.info(f"{file_path} deleted")


if __name__ == "__main__":
    args = []
    # Set args if passed
    if len(sys.argv) > 1:
        args = sys.argv[1:]

    # If not args are passed, request them from user
    if len(sys.argv) <= 1:
        tempArgs = input(
            "Please enter the directory paths you would like to consolidate. Please separate by a comma\n"
        ).split(",")
        for a in tempArgs:
            a = a.strip("'")
            a = a.strip('"')
            args.append(a.strip())

    deleteFilesBool = True
    createShortcutBool = True

    folders = args
    for parentFolder in folders:
        if os.path.exists(parentFolder):
            file_paths = list_file_paths(parentFolder=parentFolder)
            for file_path in file_paths:
                # Iterate the folders given
                if '$RECYCLE.BIN' in file_path:
                    continue
                if '.thumbnails' in file_path:
                    os.remove(file_path)
                try:
                    delete_file(file_path=file_path)
                except Exception as e:
                    logger.error(e)
        else:
            print("%s is not a valid path, please verify" % parentFolder)
            sys.exit()

    print(f'Unhandled file extensions: {unhandled_file_extensions}')
