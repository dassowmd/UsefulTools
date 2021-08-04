alias aliases="'listAllAliasesWithDocumentation'"
function aliases?() {
    echo "Outputs a list of all aliases with a description about their function"
    echo "- Parameters (pattern flag)"
    echo "  - pattern: A optional regex pattern to filter on alias name"
    echo "  - flag: A flag to determine if the output should link to alias source files"
}

function listAllAliasesWithDocumentation(){
    tempFile="$TEMP/aliasList.txt"
    alias >$tempFile
    searchString="alias "
    replaceString=""
    sed -i "s/$searchString/$replaceString/g" $tempFile
    searchString="="
    replaceString=""
    sed -i "s/$searchString.*$/$replaceString/g" $tempFile
    
    if [ -z ${1+x} ]; then
	echo "testing something" &> /dev/null
    else
	tempGrepFile="$TEMP/aliasListGrep.txt"
	grep "$1" $tempFile > $tempGrepFile
	cat $tempGrepFile > $tempFile
	rm $tempGrepFile
    fi

    while read l; do
	name=$l
	if [ -z ${2+x} ]; then
	    echo "testing something" &> /dev/null
	else
	    name="[[file:src/$l.sh][$l]]"
	fi
	
        echo "* $name"
        eval "$l?"
        echo ""
    done < $tempFile

    rm $tempFile
}
