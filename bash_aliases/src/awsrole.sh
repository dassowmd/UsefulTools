alias awsrole="aws sts get-caller-identity"
function awsrole?() {
    echo "Calls 'aws sts get-caller-identity' to print information about your current role"
}
