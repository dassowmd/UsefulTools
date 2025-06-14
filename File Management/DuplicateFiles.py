import os
import sys
import hashlib

from win32com.client import Dispatch
import send2trash
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)
loghandler = logging.StreamHandler()
logger.setLevel(logging.INFO)
loghandler.setLevel(logging.DEBUG)
logger.addHandler(loghandler)

def hashfile(path, blocksize=65536):
    afile = open(path, "rb")
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


def list_file_paths(parentFolder):
    file_paths = []
    for dirName, subdirs, fileList in tqdm(os.walk(parentFolder)):
        # Get the path for the file
        print("Scanning %s" % dirName)
        for filename in fileList:
            # Get the path to the file
            path = os.path.join(dirName, filename)
            file_paths.append(path)

    return file_paths

def find_dups(parentFolder):
    file_paths = list_file_paths(parentFolder=parentFolder)
    # Dups in format {hash:[names]}
    dups = {}
    for path in tqdm(file_paths):
        logger.debug(path)
        try:
            # Calculate hash
            file_hash = hashfile(path)
            # Add or append the file path
            if file_hash in dups:
                dups[file_hash].append(path)
            else:
                dups[file_hash] = [path]
        except Exception as e:
            print(e)
    return dups

def joinDicts(dict1, dict2):
    for key in dict2.keys():
        if key in dict1:
            dict1[key] = dict1[key] + dict2[key]
        else:
            dict1[key] = dict2[key]


def deleteDups(dict1):
    results = list(filter(lambda x: len(x) > 1, dict1.values()))
    if len(results) > 0:
        print("Duplicates Found:")
        print(
            "The following files are identical. The name could differ, but the content is identical"
        )
        print("___________________")
        for result in results:
            # print(result)
            targetPath = os.path.abspath(result[0])
            for subresult in result[1:]:
                try:
                    fileDirectory = os.path.dirname(subresult)
                    shortcutName = os.path.basename(subresult)
                    if createShortcutBool == True:
                        shortcutLinkName = os.path.splitext(shortcutName)[0] + ".lnk"
                        createShortcut(fileDirectory, shortcutLinkName, targetPath)
                    # Need to Delete subresult file
                    send2trash.send2trash(fileDirectory + "\\" + shortcutName)
                    print(fileDirectory + "\\" + shortcutName + " deleted")
                except Exception as e:
                    print(e)
            print("___________________")
    else:
        print("No duplicate files found.")


def createShortcut(fileDirectory, shortcutName, targetPath):
    #replace a file in fileDirectory with a link to the file at targetPath
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(str(fileDirectory) + '\\' + str(shortcutName))
    shortcut.Targetpath = str(targetPath)
    shortcut.WorkingDirectory = str(fileDirectory) + '\\' + str(shortcutName)
    shortcut.IconLocation = str(targetPath)
    shortcut.save()


def printResults(dict1):
    results = list(filter(lambda x: len(x) > 1, dict1.values()))
    if len(results) > 0:
        print("Duplicates Found:")
        print(
            "The following files are identical. The name could differ, but the content is identical"
        )
        print("___________________")
        for result in results:
            for subresult in result:
                print("\t\t%s" % subresult)
            print("___________________")
    else:
        print("No duplicate files found.")


if __name__ == "__main__":
    args = []
    # TODO remove
    args.extend([
        "D:Pictures\Spain",
        "D:Pictures\St Croix water camera",
        "D:Pictures\Raelynns First Christmas",
        "D:Pictures\Raelynn",
        "D:Pictures\Raelynn Videos",
        r"D:Pictures\Norway",
        "D:Pictures\Wedding Pics",
        "D:Pictures\Matt Mel Washington",
        "D:Pictures\Mel baby pics",
        "D:Pictures\Mel's HP External Hard Drive",
        "D:Pictures\Mel's HP Laptop Files",
        "D:Pictures\Mels HP External Hard Drive",
        "D:Pictures\Mels HP Laptop Files",
        "D:Pictures\Mels Photos",
        "D:Pictures\Mels SD Cards",
        "D:Pictures\Mels Thumbdrives",
        "D:Pictures\mels_phone",
        r"D:Pictures\2005-01 (Jan)",
        r"D:Pictures\2006-01 (Jan)",
        "D:Pictures\Addison",
        "D:Pictures\Camera Roll",
        "D:Pictures\Canoe Trip",
        "D:Pictures\Dad",
        "D:Pictures\DCIM",
        "D:Pictures\FileHistory",
        "D:Pictures\matts_laptop",
        "D:Pictures\matts_phone",
        "D:Pictures\Music",
        "D:Pictures\My Pictures",
        "D:Pictures\Picutres taken from googledrive REVIEW",
        "D:Pictures\Ross Wedding Pics",
        "D:Pictures\Cindis Phone",
        "D:Pictures\Viewpoint",
        "D:Videos\Drone Videos",
        "D:Videos\Mel baby pics",
        "D:Videos\Insanity Ready to Burn",
        "D:Videos\ISO_DVDs",
        "D:Videos\T25",
        "D:Videos\P90X Ready to Burn",
        "D:Videos\Mel's HP External Hard Drive",
        "D:Videos\Mel's HP Laptop Files",
        "D:Videos\Mels HP External Hard Drive",
        "D:Videos\Mels HP Laptop Files",
        "D:Videos\Mels Thumbdrives",
        "D:Videos\DCIM",
        "D:\Dell Laptop",
    ])
    # Set args if passed
    if len(sys.argv) > 1:
        args = sys.argv[1:]


    # If not args are passed, request them from user
    if len(args) <= 1:
        tempArgs = input(
            "Please enter the directory paths you would like to compare. Please separate by a comma\n"
        ).split(",")
        for a in tempArgs:
            a = a.strip("'")
            a = a.strip('"')
            args.append(a.strip())

    if input("Delete files in 2nd argument filepath? True/False\n").lower() == "true":
        deleteFilesBool = True
        if input("Create replacement shortcut? True/False\n").lower() == "true":
            createShortcutBool = True
        else:
            createShortcutBool = False
    else:
        deleteFilesBool = False
        createShortcutBool = False
    dups = {}
    folders = args
    for i in folders:
        # Iterate the folders given
        if os.path.exists(i):
            # Find the duplicated files and append them to the dups
            joinDicts(dups, find_dups(i))
        else:
            print("%s is not a valid path, please verify" % i)
            sys.exit()

    printResults(dups)
    if deleteFilesBool == True:
        deleteDups(dups)
