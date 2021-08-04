alias pi="'trustedPipInstall'"
function pi?() {
    echo "Performs a pip install with the trusted hosts set"
    echo "- Parameters (package)"
    echo "  - package: The name of the package you want to install"
    echo "- Note: this can also accept the -r flag for requirments files"
}

function trustedPipInstall() {
    python -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org $@
}
