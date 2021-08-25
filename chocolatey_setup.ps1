# First, ensure that you are using an administrative shell - you can also install as a non-admin, check out Non-Administrative Installation.
Set-ExecutionPolicy AllSigned
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
choco feature enable -n allowGlobalConfirmation
$env:ChocolateyInstall = Convert-Path "$((Get-Command choco).Path)\..\.."   
Import-Module "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"

## Installs
# Personal
choco install spotify
choco install logitech-options
choco install setpoint
choco install unifying
choco install strokesplus

# Productivity
choco install wox
choco uninstall screenpresso
choco install path-copy-copy
choco install firefox
choco install notepadplusplus.install
choco install 7zip.install
choco install treesizefree
choco install zoom
choco install lastpass
choco install beyondcompare

# Do my job
choco install git.install
choco install gh
choco install pycharm-community
choco install intellijidea-community
choco install datagrip
choco install dbeaver
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
choco install docker-cli

choco install vscode
choco install vscode-python
choco install vscode-gitignore
choco install vscode-yaml
choco install vscode-vsonline
choco install vscode-jupyter

refreshenv # Loads pip exe in to session
pip install black
pip install yamllint
pip install flake8
pip install sphinx
pip install pandas

# Set Windows Explorer Default settings
$key = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
Set-ItemProperty $key Hidden 1
Set-ItemProperty $key HideFileExt 0
Set-ItemProperty $key ShowSuperHidden 1
Write-Output 'Restarting Windows Explorer'
Stop-Process -processname explorer
