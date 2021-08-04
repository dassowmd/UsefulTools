alias awschangeprofile=awschangeprofile

function awschangeprofile() {
    local profile_name="${1:-pfg-azuread}"
    local is_global="${2:-NULL}"

    if [ $profile_name  == '-g' ]
    then
      local profile_name=pfg-azuread
      local is_global="${1:-NULL}"
    fi
    if [ $is_global  == '-g' ]
    then
        # Set global
        setx AWS_DEFAULT_PROFILE $profile_name
    else
        # Set local
        AWS_DEFAULT_PROFILE=$profile_name
    fi
}

function awschangeprofile?() {
    echo "Change the aws role you are using"
}
