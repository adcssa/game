Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

python .\generate_bgm.py

pyinstaller `
  --noconfirm `
  --clean `
  --windowed `
  --onefile `
  --name FogHarborEcho `
  --add-data "bgm.wav;." `
  .\main.py
