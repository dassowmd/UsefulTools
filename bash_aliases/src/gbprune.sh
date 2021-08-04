alias gbprune="'pruneAndCleanLocalBranches'"
function gbprune?() {
    echo "Punes and deletes local branches"
}

function pruneAndCleanLocalBranches() {
    git checkout master

    branchFile="$temp/branches-to-prune.txt"
    git remote prune origin --dry-run | grep "would prune" > $branchFile
    oldText="\* \[would prune\] origin\/"
    newText=""
    sed -i "s/$oldText/$newText/g" $branchFile

    git remote prune origin
    
    while read p; do
        git branch -D "$p"
    done < $branchFile
    
    rm $branchFile
}
