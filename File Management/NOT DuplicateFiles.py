import os
import sys
import hashlib
from win32com.client import Dispatch
import send2trash


def hashfile(path, blocksize=65536):
    afile = open(path, "rb")
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


def findDup(parentFolder):
    # Dups in format {hash:[names]}
    dups = {}
    for dirName, subdirs, fileList in os.walk(parentFolder):
        # Get the path for the file
        print("Scanning %s..." % dirName)
        try:
            for filename in fileList:
                # Get the path to the file
                path = os.path.join(dirName, filename)
                # Calculate hash
                file_hash = hashfile(path)
                # Add or append the file path
                if file_hash in dups:
                    dups[file_hash].append(path)
                else:
                    dups[file_hash] = [path]
        except:
            print("Unable to process ", path)
            continue
    return dups


def joinDicts(dict1, dict2):
    for key in dict2.keys():
        if key in dict1:
            dict1[key] = dict1[key] + dict2[key]
        else:
            dict1[key] = dict2[key]


# def deleteDups(dict1):
# results = list(filter(lambda x: len(x) > 1, dict1.values()))
# if len(results) > 0:
#     print('Duplicates Found:')
#     print('The following files are identical. The name could differ, but the content is identical')
#     print('___________________')
#     for result in results:
#         #print(result)
#         targetPath = os.path.abspath(result[0])
#         for subresult in result[1:]:
#             fileDirectory = os.path.dirname(subresult)
#             shortcutName = os.path.basename(subresult)
#             if createShortcutBool == True:
#                 shortcutLinkName = os.path.splitext(shortcutName)[0] + '.lnk'
#                 createShortcut(fileDirectory, shortcutLinkName, targetPath)
#             #Need to Delete subresult file
#             send2trash.send2trash(fileDirectory + '\\' + shortcutName)
#             print(fileDirectory + '\\' + shortcutName + ' deleted')
#         print('___________________')
# else:
#     print('No duplicate files found.')


def createShortcut(fileDirectory, shortcutName, targetPath):
    # replace a file in fileDirectory with a link to the file at targetPath
    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(fileDirectory + "\\" + shortcutName)
    shortcut.Targetpath = targetPath
    shortcut.WorkingDirectory = fileDirectory + "\\" + shortcutName
    shortcut.IconLocation = targetPath
    shortcut.save()


def printResults(dict1):
    results = list(filter(lambda x: len(x) == 1, dict1.values()))
    if len(results) > 0:
        print("Unique Files were found:")
        print("The following files are unique.")
        print("___________________")
        for result in results:
            for subresult in result:
                print("\t\t%s" % subresult)
            print("___________________")
    else:
        print("No unique files found.")


if __name__ == "__main__":
    args = []
    # Set args if passed
    if len(sys.argv) > 1:
        args = sys.argv[1:]

    # If not args are passed, request them from user
    if len(sys.argv) <= 1:
        tempArgs = input(
            "Please enter the directory paths you would like to compare. Please separate by a comma\n"
        ).split(",")
        for a in tempArgs:
            a = a.strip("'")
            a = a.strip('"')
            args.append(a.strip())

    # if input('Delete files in 2nd argument filepath? True/False\n').lower() == "true":
    #     deleteFilesBool = True
    #     if input('Create replacement shortcut? True/False\n').lower() == "true":
    #         createShortcutBool = True
    #     else:
    #         createShortcutBool = False
    # else:
    deleteFilesBool = False
    createShortcutBool = False
    dups = {}
    folders = args
    for i in folders:
        # Iterate the folders given
        if os.path.exists(i):
            # Find the duplicated files and append them to the dups
            joinDicts(dups, findDup(i))
        else:
            print("%s is not a valid path, please verify" % i)
            sys.exit()

    printResults(dups)
    # if deleteFilesBool == True:
    #     deleteDups(dups)
