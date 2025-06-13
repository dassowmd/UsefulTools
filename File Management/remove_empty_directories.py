import os
import sys

def delete_empty_folders(root):
    deleted = set()
    for current_dir, subdirs, files in os.walk(root, topdown=False):
        if '$RECYCLE.BIN' in current_dir:
            continue
        if '$RECYCLE.BIN' in subdirs:
            continue
        still_has_subdirs = False
        for subdir in subdirs:
            if os.path.join(current_dir, subdir) not in deleted:
                still_has_subdirs = True
                break
        if not any(files) and not still_has_subdirs:
            print(f'removing {current_dir}')
            os.rmdir(current_dir)
            deleted.add(current_dir)

    return deleted

if __name__ == "__main__":
    args = []
    # Set args if passed
    if len(sys.argv) > 1:
        args = sys.argv[1:]

    # If not args are passed, request them from user
    if len(sys.argv) <= 1:
        tempArgs = input(
            "Please enter the directory paths you would like to check. Please separate by a comma\n"
        ).split(",")
        for a in tempArgs:
            a = a.strip("'")
            a = a.strip('"')
            args.append(a.strip())

    for path in args:
        delete_empty_folders(root=path)