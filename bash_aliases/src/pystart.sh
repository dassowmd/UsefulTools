alias pystart="'doStuffForpystart'"
function pystart?() {
    echo "This will start your python virtual enviornment."
}

function doStuffForpystart() {
    source venv/Scripts/activate
}
