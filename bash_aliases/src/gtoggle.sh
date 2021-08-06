alias gtoggle="'toggle'"
function gtoggle?() {
    echo "Toggle between branches"
    echo "Executes a WIP commit to save progress before switching"
    echo "- Parameters"
    echo "  - destination branch"
    echo "    - Optional - if not provided, it will go to the last branched checked out using gtoggle"
}

function toggle(){
    local destBranchInput="${1:-""}"
    echo $destBranchInput

    if [ -z "$destBranchInput" ]
      then
        destBranch=$cachedBranch
      else
        destBranch=$destBranchInput
    fi

    # Check out new branch
    export cachedBranch=$( git rev-parse --abbrev-ref HEAD )
    git checkout $destBranch
}