# auggie-wsl.ps1
# Wrapper that converts Windows paths to WSL paths and calls auggie via WSL.
# Used as AUGGIE_CLI_PATH to avoid Windows Node.js filesystem slowness.

function ConvertTo-WslPath([string]$p) {
    # C:\foo\bar -> /mnt/c/foo/bar  (pure PowerShell, no wslpath call)
    $drive = $p[0].ToString().ToLower()
    $rest  = $p.Substring(2).Replace('\', '/')
    return "/mnt/$drive$rest"
}

[string[]]$converted = @()
foreach ($arg in $args) {
    if ($arg -match '^[A-Za-z]:\\') {
        $converted += ConvertTo-WslPath $arg
    } else {
        $converted += $arg
    }
}

wsl auggie @converted
exit $LASTEXITCODE
