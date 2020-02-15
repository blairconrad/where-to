[CmdletBinding()]
Param (
    [string]$NewVersion = $(throw "NewVersion is required")
)


Function Replace {
    [CmdletBinding()]
    param (
        [string]$File,
        [string]$Pattern,
        [string]$Replacement
    )

    $newContent = @()
    $content = Get-Content -Encoding UTF8 $File
    $content | ForEach-Object {
        if ($_ -match $Pattern) {
            $newContent += $Replacement
        }
        else {
            $newContent += $_
        }
    }


    Set-Content -Path $File -Encoding Ascii -Value ($newContent -join "`r`n").Trim()
}

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

    Replace -File $versionFile -Pattern '^__version__ = "[^"]+"$' -Replacement "__version__ = `"$NewVersion`""
    Replace -File $pyProjectTomlFile -Pattern '^version = "[^"]+"$' -Replacement "version = `"$NewVersion`""

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
