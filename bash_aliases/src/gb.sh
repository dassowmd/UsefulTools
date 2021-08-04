alias gb="'createGitBranch'"
function gb?() {
    echo "Creates a new feature branch for the current repo"
    echo "- Parameters (name)"
    echo "  - name: The name of the feature you are creating"
}

function createGitBranch() {
    git checkout -b "feature/$1"
}
