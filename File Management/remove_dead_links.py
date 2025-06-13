import sys
import os
import logging

logger = logging.getLogger(__name__)
loghandler = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
loghandler.setLevel(logging.DEBUG)
logger.addHandler(loghandler)

from clean_up_link_files import check_if_link_target_is_valid, list_file_paths


if __name__ == "__main__":
    args = []
    # Set args if passed
    if len(sys.argv) > 1:
        args = sys.argv[1:]
    # If not args are passed, request them from user
    if len(sys.argv) == 0:
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
                check_if_link_target_is_valid(link_file_path=file_path)
        else:
            print("%s is not a valid path, please verify" % parentFolder)
            sys.exit()


