$url = 'https://github.com/conan-io/conan-center-index'
$folder = 'core/conan/assets/repo/src/recipes'

Set-Location repo

if (Test-Path -path $folder)
{
    Write-Output "Cloned git repository"
    git pull
} else {
    Write-Output "Cloned git repository"
    git clone -v $url core/conan/assets/repo/src
}