$url = 'https://github.com/conan-io/conan-center-index'
$folder = 'src/recipes'

Set-Location repo

if (Test-Path -path $folder)
{
    Write-Output "Cloned git repository"
    git pull
} else {
    Write-Output "Cloned git repository"
    git clone -v $url src
}