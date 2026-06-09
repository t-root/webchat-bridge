# Mở Chrome thật với remote debugging — dùng cùng profile với bridge.
# Sau khi Chrome mở: đăng nhập Claude, vượt Cloudflare thủ công, rồi chạy python server.py

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$ProfileDir = Join-Path $ProjectRoot "browser-profile"
$Port = if ($env:BROWSER_CDP_PORT) { $env:BROWSER_CDP_PORT } else { "9222" }

$ChromePaths = @(
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)

$Chrome = $ChromePaths | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Chrome) {
    Write-Host "Không tìm thấy Google Chrome. Cài Chrome rồi chạy lại script này." -ForegroundColor Red
    exit 1
}

New-Item -ItemType Directory -Force -Path $ProfileDir | Out-Null

Write-Host ""
Write-Host "=== Chrome CDP mode (tránh bot detection) ===" -ForegroundColor Cyan
Write-Host "Profile: $ProfileDir"
Write-Host "CDP port: $Port"
Write-Host ""
Write-Host "1. Đăng nhập claude.ai / chatgpt.com trong cửa sổ này"
Write-Host "2. Vượt Cloudflare thủ công nếu có"
Write-Host "3. Trong ai_models_config.json đặt: `"connect_cdp`": `"http://127.0.0.1:$Port`""
Write-Host "4. Chạy: python server.py"
Write-Host ""

& $Chrome `
    --remote-debugging-port=$Port `
    --user-data-dir="$ProfileDir" `
    --no-first-run `
    --no-default-browser-check `
    about:blank
