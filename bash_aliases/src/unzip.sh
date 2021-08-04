alias unzip="'unzipFolder'"
function unzip?() {
    echo "Uncompress the given zip file to a directory of the same name."
    echo "- Parameters (zipFile)"
    echo "  - zipFile: The name of the zip file you want to uncompress."
}

function unzipFolder(){
    fileName=$1
    dir=$(trimString $fileName 0 4)
    7z e "$fileName" -o* -aoa
}
