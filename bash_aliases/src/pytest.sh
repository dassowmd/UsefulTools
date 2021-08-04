alias pytest="'pythonPathedPytest'"
function pytest?() {
    echo "Performs a pytest on the given directory or file and defaults to the current directory"
    echo "- Parameters (path)"
    echo "  - path: The path that you want to start pytest for"
}

function pythonPathedPytest() {
    python -m pytest $@
}
