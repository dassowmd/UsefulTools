alias gbdelete="'deleteBranch'"
function gbdelete?() {
    echo "Performs a delete of local branches"
    echo "- Parameters (ForceDelete)"
    echo "  - optional 'force"
}

function deleteBranch() {
	ARG1=${1:-noForce}
	if [ "$ARG1" == 'force' ] 
	then 
		git branch | grep -v "master" | grep -v ^* | xargs git branch -D
	else 
		git branch | grep -v "master" | grep -v ^* | xargs git branch -d
	fi
}
