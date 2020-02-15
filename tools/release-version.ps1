[CmdletBinding()]
Param (
    [string]$NewVersion = $(throw "NewVersion is required")
)

$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot.Parent

# ------------------------------------------------------------------------------

$releaseNotesFile = Resolve-Path where_to/release_notes.md
$versionFile = Resolve-Path where_to/__init__.py
$pyProjectTomlFile = Resolve-Path pyproject.toml

# ------------------------------------------------------------------------------

try {
    $branchName = "release/$NewVersion"

    Write-Host "Releasing version $NewVersion"

    git checkout master
    git pull --ff-only origin master
    git checkout --quiet -b $branchName master

    $releaseNotesContent = [System.IO.File]::ReadAllText($releaseNotesFile)
    $releaseNotesContent = ("## $NewVersion`r`n`r`n" + $releaseNotesContent)
    [System.IO.File]::WriteAllText($releaseNotesFile, $releaseNotesContent)

    $versionContent = [System.IO.File]::ReadAllText($versionFile)
    $versionContent = $versionContent -replace '^__version__ = "[^"]+"', "__version__ = `"$NewVersion`""
    [System.IO.File]::WriteAllText($versionFile, $versionContent)

    $pyProjectContent = [System.IO.File]::ReadAllText($pyProjectTomlFile)
    $pyProjectContent = $pyProjectContent -replace '^version = "[^"]+"', "version = `"$NewVersion`""
    [System.IO.File]::WriteAllText($pyProjectTomlFile, $pyProjectContent)


    Write-Host "`r`nReleasing version $NewVersion. Changing this stuff:`r`n"
    git diff
    $response = Read-Host "`r`n  Proceed (y/N)?"
    Switch ($response) {
        y { }
        n { Write-Host "Update cancelled. Clean up yourself."; return }
        Default { Write-Host "Unknown response '$response'. Aborting."; return }
    }

    git commit --quiet --message "Set version to $NewVersion" $releaseNotesFile $versionFile $pyProjectTomlFile
    git checkout --quiet master
    git merge --quiet --no-ff $branchName
    git branch -D $branchName

    git tag $NewVersion
    git push origin $NewVersion master
}
finally {
    Pop-Location
}