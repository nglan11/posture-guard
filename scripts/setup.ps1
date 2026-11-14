$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (!(Test-Path '.venv/Scripts/python.exe')) {
    if (Test-Path '.python/python.exe') { & ./.python/python.exe -m venv .venv }
    else { & py -3.12 -m venv .venv }
    if ($LASTEXITCODE -ne 0) { throw 'Cần Python 3.12 với pip và Tcl/Tk.' }
}
& ./.venv/Scripts/python.exe -m pip install -e .
if ($LASTEXITCODE -ne 0) { throw 'Không cài được thư viện.' }
New-Item -ItemType Directory -Force data/models | Out-Null
$model = 'data/models/face_landmarker.task'
if (!(Test-Path $model)) {
    Invoke-WebRequest 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task' -OutFile "$model.download"
    Move-Item -LiteralPath "$model.download" -Destination $model
}
Write-Host 'Hoàn tất. Chạy: ./.venv/Scripts/python.exe -m posture_guard.main'
