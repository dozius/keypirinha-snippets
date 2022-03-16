<#
.SYNOPSIS
    Builds the plugin into a package for release
#>
if (Test-Path .\build) {
    Remove-Item .\build -Recurse -Force
}

New-Item -Path .\build -ItemType Directory

$compress = @{
    Path = ".\src\*", ".\LICENSE", ".\README.md"
    CompressionLevel = "Optimal"
    DestinationPath = ".\build\snippets.zip"
}

Compress-Archive @compress
Rename-Item .\build\snippets.zip snippets.keypirinha-package
