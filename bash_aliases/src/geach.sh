alias geach="performActionOnEachRepo"
function geach?() {
    echo "Performs the given action on each git repo in the current directory."
    echo "- Parameters (actionToBePerformed)"
    echo "  - actionToBePerformed: A bash command to be executed on each repo"
    echo "- WARNING: This is a powerful command that will execute what ever you give it on each repo."
}

function performActionOnEachRepo() {
    dir=$PWD
    for d in */ ; do
        repoDir="$dir/$d"
        if [ -d "$repoDir/.git" ]; then
            cd $repoDir
            eval $1
        fi
    done
    cd $dir
}
