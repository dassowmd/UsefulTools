from pathlib import Path
import os
import shutil

source_dirs = [
"F:Pictures",
"F:Videos",
"F:Documents",
"F:Zip Files",
"F:Microsoft Access",
"F:Power Points",
]
destination_dir = 'D:'

def ignore_files(src, names):
    for name in names:
        if Path(name).suffix == '.lnk':
            yield name

for source_dir in source_dirs:
    shutil.copytree(source_dir, destination_dir, symlinks=True, ignore=ignore_files)