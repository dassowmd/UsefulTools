alias gpusnv="'gitPushUpstreamNoVerify'"
function gpusnv?() {
    echo "Performs a git push upstream for the current branch, skipping githooks"
    echo "If a string arg is passed a git commit -am <string arg> will be ran before commiting"
}

function gitPushUpstreamNoVerify() {
    b=$(gcb)
    b=$(trimString "$b" 2 0)
    local commit_message="${1:-""}"
    if ! [ -z "$commit_message" ]
      then
        git commit -am "$commit_message" --no-verify || return 1
    fi

    git push --set-upstream origin $b --no-verify
}
