alias awsclilogin=awsclilogin

function awsclilogin() {
    local profile_name="${1:-pfg-azuread}"
    aws-azure-login --profile $profile_name --mode gui --enable-chrome-seamless-sso false
}

function awsclilogin?() {
    echo "Logs into the AWS cli. Need to use your lastname-alt.firstname@principal.com, your ER account, and your ER password."
	echo "To use a specific profile, pass it as the first paramater"
    echo "Need to install aws-azure-login (from npm) first, along with slightly modify it"
    echo "See https://docs.principal.com/display/AWS/Configuring+and+Testing+AWS+CLI for more details"
}
