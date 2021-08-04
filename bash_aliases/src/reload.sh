alias reload="'reloadAliases'"
function reload?() {
    echo "Reloads or resets all aliases. (useful if making or pulling changes to the aliase files.)"
}

function reloadAliases() {
    clralias
    source ~/.bashrc
    # call aliases with two paramters for output to link to source files
    aliases "" "" > $ALIAS_DIR/src/readme.org
}
