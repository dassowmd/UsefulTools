alias pyvenv="'doStuffForpyvenv'"
function pyvenv?() {
    echo "This will create the virtual enviornment for you"
}

function doStuffForpyvenv() {
    python --version
    python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org virtualenv
    python -m venv venv
}
