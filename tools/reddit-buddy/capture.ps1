# Reddit Scrolling Buddy - Pure PowerShell (no Python needed!)
# Run: .\capture.ps1
# Or for loop: .\capture.ps1 -Loop 5

param(
    [int]$Loop = 0,  # Seconds between captures (0 = single capture)
    [string]$OutDir = "$PSScriptRoot\captures"
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Create output directory
if (!(Test-Path $OutDir)) { New-Item -ItemType Directory -Path $OutDir | Out-Null }

function Take-Screenshot {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $outPath = "$OutDir\screen_$timestamp.png"

    $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bitmap = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
    $bitmap.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)

    $graphics.Dispose()
    $bitmap.Dispose()

    Write-Host "📸 Captured: $outPath" -ForegroundColor Green
    return $outPath
}

if ($Loop -gt 0) {
    Write-Host "🔄 Auto-capturing every ${Loop}s. Press Ctrl+C to stop." -ForegroundColor Cyan
    Write-Host "📁 Saving to: $OutDir" -ForegroundColor Gray
    Write-Host ("-" * 50)

    while ($true) {
        $path = Take-Screenshot
        Write-Host "   → Tell Claude: Read $path" -ForegroundColor Yellow
        Start-Sleep -Seconds $Loop
    }
} else {
    $path = Take-Screenshot
    Write-Host ""
    Write-Host "💡 Now tell Claude:" -ForegroundColor Cyan
    Write-Host "   `"Read $path and react to my Reddit feed!`"" -ForegroundColor Yellow

    # Copy path to clipboard for convenience
    $path | Set-Clipboard
    Write-Host "   (Path copied to clipboard!)" -ForegroundColor Gray
}
