alias grp="'customGrep'"
function grp?() {
    echo "Performs a recursive grep in the current directory searching for the given pattern"
    echo "- Parameters (searchString)"
    echo "  - searchString: The string to search for."
}

function customGrep() {
    grep -r -n -Z --color "$1" .
}
