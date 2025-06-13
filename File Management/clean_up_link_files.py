from pathlib import Path
import sys
import os
import send2trash
import shutil
import pylnk3
from copy import deepcopy

from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)
loghandler = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
loghandler.setLevel(logging.DEBUG)
logger.addHandler(loghandler)

from consolidate_files import master_dir_mapping, is_already_in_target_dir
from DuplicateFiles import createShortcut

file_to_link_map = {}
def check_if_link_target_is_valid(link_file_path):
    try:
        with open(link_file_path, 'rb') as f:
            lnk = pylnk3.parse(f)

        if Path(lnk.path).exists():
            if Path(lnk.path).is_file():
                return True
        else:
            if Path(link_file_path).suffix == '.lnk':
                os.remove(link_file_path)
        return False
    except Exception as e:
        print(e)
        return False
def map_file_to_link(link_file_path):
    try:
        with open(link_file_path, 'rb') as f:
            lnk = pylnk3.parse(f)
        if lnk.path not in file_to_link_map.keys():
            file_to_link_map[lnk.path] = []
        file_to_link_map[lnk.path].append(link_file_path)

    except Exception as e:
        raise e
def move_file(file, link_list):
    # TODO handle passing a link list,
    #  figure out which one is the right one (shortest, and in target dir)
    #  and move it and any other links to the right place.
    #  Also be sure to replace the existing file with the right link
    try:
        targetDir = master_dir_mapping[Path(file).suffix.lower()]
    except Exception as e:
        print(e)
        print(file)
        return # TODO should we return and continue if the suffix isn't found, or reraise the error?
        raise e
    file_in_target_dir = is_already_in_target_dir(file_path=file, target_dir=targetDir)
    # Default to the current file path
    best_destination_in_target_dir = file_in_target_dir
    best_destination_file_path = file
    for link_path in link_list:
        # Check if there is a better file path
        temp_lnk_in_target_dir = is_already_in_target_dir(file_path=link_path, target_dir=targetDir)
        if temp_lnk_in_target_dir:
            # If the file is buried deeper than the link, move it
            if len(Path(best_destination_file_path).parts) > len(Path(link_path).parts):
                logger.debug(f'Moving {file} to {link_path}')
                best_destination_file_path = link_path
            else:
                logger.debug('Already in the shorter path within the target directory')
        else:
            if best_destination_in_target_dir:
                logger.debug('Another path is in the target directory')
                continue
            else:
                if len(Path(best_destination_file_path).parts) > len(Path(link_path).parts):
                    logger.debug('Neither path is in the target directory, but the link is shorter so moving it')
                    best_destination_file_path = link_path
                else:
                    logger.debug('Already in the shorter path and neither is in the target directory')

        # Move file
        best_destination_file_path_with_suffix = Path(best_destination_file_path).with_suffix(Path(file).suffix)
        if not Path(file) == best_destination_file_path_with_suffix:
            if best_destination_file_path_with_suffix.suffix == '.lnk':
                raise Exception('Cant have a .lnk')
            if not Path(file).exists() and not best_destination_file_path_with_suffix.exists():
                if Path(file).with_suffix('.lnk').exists():
                    with open(link_path, 'rb') as f:
                        lnk = pylnk3.parse(f)
                    if Path(lnk.path).exists():
                        file = lnk.path
            if Path(file).exists():
                shutil.copy(file, best_destination_file_path_with_suffix)
            if not best_destination_file_path_with_suffix.exists():
                raise Exception('Neither the file or best file path exist')
            temp_link_file_path = Path(deepcopy(file))
            temp_link_file_path = temp_link_file_path.with_suffix('.lnk')
            createShortcut(temp_link_file_path.parent, temp_link_file_path.name, best_destination_file_path_with_suffix)
            if Path(file).exists():
                send2trash.send2trash(file)

        # Move other links
        for link_path in link_list:
            try:
                with open(link_path, 'rb') as f:
                    lnk = pylnk3.parse(f)
                if Path(lnk.path) != best_destination_file_path_with_suffix:
                    if Path(lnk.working_dir).with_suffix(Path(file).suffix) == Path(file):
                        continue
                    createShortcut(Path(link_path).parent, Path(link_path).name, best_destination_file_path_with_suffix)
                    # Validate shortcut
                    with open(link_path, 'rb') as f:
                        temp_lnk = pylnk3.parse(f)
                    # if Path(temp_lnk.path) != best_destination_file_path_with_suffix:
                    #     raise Exception(f'Link is bad. Expected {best_destination_file_path_with_suffix}, got {temp_lnk.path}')
                    # with open(temp_lnk.path, 'rb') as f:
                    #     f.read()
            except Exception as e:
                logger.error(e)
            if Path(best_destination_file_path).with_suffix('.lnk').exists():
                os.remove(Path(best_destination_file_path).with_suffix('.lnk'))

def list_file_paths(parentFolder):
    for dirName, subdirs, fileList in tqdm(os.walk(parentFolder)):
        # Get the path for the file
        for filename in fileList:
            # Get the path to the file
            path = os.path.join(dirName, filename)
            if Path(path).suffix in ['.lnk']:
                yield path


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
                if check_if_link_target_is_valid(link_file_path=file_path):
                    try:
                        map_file_to_link(link_file_path=file_path)
                    except Exception as e:
                        logger.error(e)
        else:
            print("%s is not a valid path, please verify" % parentFolder)
            sys.exit()

    # Move the file to the best selected path
    for file, link_list in file_to_link_map.items():
        move_file(file, link_list=link_list)


    delete_lnk_files = input('Would you like to delete the lnk files now that the files are moved?').lower()
    if delete_lnk_files in ['true', 'yes']:
        for parentFolder in folders:
            link_files = list_file_paths(parentFolder=parentFolder)
            for file in link_files:
                if Path(file).suffix == '.lnk':
                    os.remove(file)