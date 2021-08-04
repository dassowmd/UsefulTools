ALIAS_DIR=~/toc-aliases

function loopOverAliases() {
    for f in $ALIAS_DIR/src/*.sh; do
	. $f
    done
}

loopOverAliases
