alias tree="'PrintDirectoryTree'"
function tree?() {
    echo "Prints the directory tree"
    echo "- Parameters (directory_path)"
    echo "  - directory_path: The directory path to print children of"
}

function PrintDirectoryTree() {
  if [[ "$OSTYPE" == "msys"* ]]; then
    cmd //c tree  $1
  else
    tree $1
  fi
}
