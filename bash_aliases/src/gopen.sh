alias gopen="'openInGitHub'"
function gopen?() {
    echo "Opens the current bransh of the current repo in GitHub"
}

function openInGitHub() {
    status=$(git status)
    branch="master"

    count=0
    for i in $(echo $status | tr " " "\n")
    do
        let count=count+1
        if [ $count -eq 3 ]
        then
            branch=$i
        fi
    done

    url=$(gurl) # defined in gurl.sh

    if [[ $url != *"https"* ]];
    then
        url=${url/":"/"/"}
        url=$(trimString "$url" 4 4) # Defined in trim-string.sh
    else
        url=$(trimString "$url" 0 4)
    fi

    url="$url/tree/$branch"
    echo $url
    web $url # Defined in web.sh
}
