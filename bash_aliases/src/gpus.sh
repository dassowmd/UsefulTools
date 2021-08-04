alias gpus="'gitPushUpstream'"
function gpus?() {
    echo "Performs a git push upstream for the current branch"
    echo "If a string arg is passed a git commit -am <string arg> will be ran before commiting"
}

function gitPushUpstream() {
    b=$(gcb)
    b=$(trimString "$b" 2 0)
    local commit_message="${1:-""}"
    if ! [ -z "$commit_message" ]
      then
        gcam "$commit_message" || return 1
    fi
    git push --set-upstream origin $b
}
