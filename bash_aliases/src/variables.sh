alias variables="'openVariablesFile'"
function variables?() {
    echo "Opens the variables file"
    echo "- NOTES:"
    echo "  - The variables file is a place to store user specific settings"
}

function openVariablesFile() {
    edit $ALIAS_DIR/src/variables.sh
}

PREFERRED_EDITOR="code"
PREFERRED_BROWSER="\"/C/Program Files (x86)/Google/Chrome/Application/chrome.exe\""
REPO_DIR="/c/git"
ALIAS_DIR=~/toc-aliases
TOOLS_DIR="/c/tools"
