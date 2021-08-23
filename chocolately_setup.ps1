# First, ensure that you are using an administrative shell - you can also install as a non-admin, check out Non-Administrative Installation.
Set-ExecutionPolicy AllSigned
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
choco feature enable -n allowGlobalConfirmation
$env:ChocolateyInstall = Convert-Path "$((Get-Command choco).Path)\..\.."   
Import-Module "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"

## Installs
# Personal
choco install spotify

# Productivity
choco install wox
choco install greenshot
choco install path-copy-copy
choco install firefox
choco install notepadplusplus.install
choco install 7zip.install
choco install treesizefree
choco install zoom

# Do my job
choco install git.install
choco install gh
choco install pycharm-community
choco install intellijidea-community
choco install datagrip
choco install pip
choco install python
choco install nodejs.install
choco install putty.install
choco install filezilla
choco install curl
choco install awscli
choco install azure-cli
choco install postman
choco install terraform
choco install tflint
choco install cmder
choco install openjdk
choco install virtualbox

choco install vscode
choco install vscode-python
choco install vscode-gitignore
choco install vscode-yaml
choco install vscode-vsonline
choco install vscode-jupyter

refreshenv
pip install black
pip install yamllint
pip install flake8
pip install sphinx
pip install pandas
