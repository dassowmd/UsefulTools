from consolidate_files import list_file_paths
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
logger.setLevel(logging.INFO)
loghandler.setLevel(logging.DEBUG)
logger.addHandler(loghandler)

def check(file_path):
    if '.thumbnails' in str(file_path):
        return True
    if Path(file_path).suffix in ['.iso']:
        return True
    return False
def delete_file(file_path):
    # Need to Delete subresult file
    send2trash.send2trash(file_path)
    logger.info(file_path + " deleted")


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
                if check(file_path=file_path):
                    try:
                        delete_file(file_path=file_path)
                    except Exception as e:
                        logger.error(e)
        else:
            print("%s is not a valid path, please verify" % parentFolder)
            sys.exit()