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
master_dir_mapping = {
    '.jpg': 'Pictures',
    '.jpeg': 'Pictures',
    '.png': 'Pictures',
    '.img': 'Pictures',
    '.txt': str(Path('Documents').joinpath('Text Docs')),
    '.doc': str(Path('Documents').joinpath('Word')),
    '.docx': str(Path('Documents').joinpath('Word')),
    '.gdoc': str(Path('Documents').joinpath('Word')),
    '.xlsx': str(Path('Documents').joinpath('Excel')),
    '.xls': str(Path('Documents').joinpath('Excel')),
    '.xlsb': str(Path('Documents').joinpath('Excel')),
    '.xlsm': str(Path('Documents').joinpath('Excel')),
    '.xls summaries': str(Path('Documents').joinpath('Excel')),
    '.csv': str(Path('Documents').joinpath('CSV')),
    '.csv#': str(Path('Documents').joinpath('CSV')),
    '.pdf': str(Path('Documents').joinpath('PDFs')),
    '.pdf-2': str(Path('Documents').joinpath('PDFs')),
    '.pdf gillnet': str(Path('Documents').joinpath('PDFs')),
    '.mp3': str(Path('Music')),
    '.mp4': str(Path('Videos')),
    '.mov': str(Path('Videos')),
    '.m4v': str(Path('Videos')),
    '.avi': str(Path('Videos')),
    '.vob': str(Path('Videos')),
    '.ifo': str(Path('Videos')),
    '.bup': str(Path('Videos')),
    '.3gp': str(Path('Videos')),
    '.mpg': str(Path('Videos')),
    '.mkv': str(Path('Videos')),
    '.wmv': str(Path('Videos')),
    '.zip': str(Path('Zip Files')),
    '.gz': str(Path('Zip Files')),
    '.tar': str(Path('Zip Files')),
    '.accdb': str(Path('Microsoft Access')),
    '.ppt': str(Path('Power Points')),
    '.pptx': str(Path('Power Points')),
    '.exe': str(Path('DELETE_ME')),
}
unhandled_file_extensions = set()
def check_if_matches_mapping(file_path):
    file_ext = Path(file_path).suffix.lower()
    if file_ext in master_dir_mapping.keys():
        return True
    if file_ext not in unhandled_file_extensions:
        unhandled_file_extensions.add(file_ext)
    return False


def list_file_paths(parentFolder):
    for dirName, subdirs, fileList in tqdm(os.walk(parentFolder)):
        # Get the path for the file
        for filename in fileList:
            # Get the path to the file
            path = os.path.join(dirName, filename)
            if Path(path).suffix not in ['.lnk']:
                yield path

def is_already_in_target_dir(file_path, target_dir):
    if str(Path(file_path.split(':')[1])).strip('\\').startswith(target_dir):
        return True
    return False
def move_file(file_path):
    targetDir = master_dir_mapping[Path(file_path).suffix.lower()]
    if is_already_in_target_dir(file_path=file_path, target_dir=targetDir):
        logger.info(f'{file_path} is already in the desired path')
        return
    fileDirectory = os.path.dirname(file_path)
    targetPath = Path(Path(fileDirectory).drive).joinpath(targetDir).joinpath(file_path)
    if not targetPath.parent.exists():
        targetPath.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(file_path, targetPath)
    shortcutName = os.path.basename(file_path)
    shortcutLinkName = os.path.splitext(shortcutName)[0] + ".lnk"
    createShortcut(fileDirectory, shortcutLinkName, str(targetPath))
    # Need to Delete subresult file
    send2trash.send2trash(fileDirectory + "\\" + shortcutName)
    logger.info(fileDirectory + "\\" + shortcutName + " deleted")

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
                if check_if_matches_mapping(file_path=file_path):
                    try:
                        move_file(file_path=file_path)
                    except Exception as e:
                        logger.error(e)
        else:
            print("%s is not a valid path, please verify" % parentFolder)
            sys.exit()

    print(f'Unhandled file extensions: {unhandled_file_extensions}')
