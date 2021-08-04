alias web="'web'"
function web?() {
    echo "Launches your preferred web browser to the given location."
    echo "- Parameters (url)"
    echo "  - url: The url that you want opened"
    echo "- NOTES:"
    echo "  - The url parameter is optional and a new browser will be opened to your home page if omitted."
}

function web(){
    eval "$PREFERRED_BROWSER $1 &"
}
