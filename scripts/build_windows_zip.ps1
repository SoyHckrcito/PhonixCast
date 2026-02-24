Param(
    [string]$AppName = "PhonixCast",
    [string]$EntryPoint = "app/main.py",
    [string]$DistDir = "dist"
)

$ErrorActionPreference = "Stop"

Write-Host "==> Limpiando builds previos"
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
if (Test-Path $DistDir) { Remove-Item $DistDir -Recurse -Force }
if (Test-Path "$AppName.spec") { Remove-Item "$AppName.spec" -Force }

Write-Host "==> Instalando dependencias de build"
python -m pip install --upgrade pip
python -m pip install -r app/requirements-build.txt

Write-Host "==> Generando ejecutable con PyInstaller"
python -m PyInstaller \
    --name $AppName \
    --onefile \
    --clean \
    $EntryPoint

if (!(Test-Path "$DistDir/$AppName.exe")) {
    throw "No se encontró $DistDir/$AppName.exe"
}

Write-Host "==> Preparando paquete ZIP"
New-Item -ItemType Directory -Force -Path "$DistDir/package" | Out-Null
Copy-Item "$DistDir/$AppName.exe" "$DistDir/package/$AppName.exe"
Copy-Item "README.md" "$DistDir/package/README.md"

@"
Requisitos para ejecución en Windows:
- adb.exe en PATH (Android Platform Tools)
- scrcpy en PATH

Uso:
  .\\PhonixCast.exe start --profile ultra-low-latency
"@ | Set-Content "$DistDir/package/RUN-WINDOWS.txt"

if (Test-Path "$DistDir/$AppName-windows.zip") {
    Remove-Item "$DistDir/$AppName-windows.zip" -Force
}

Compress-Archive -Path "$DistDir/package/*" -DestinationPath "$DistDir/$AppName-windows.zip"
Write-Host "ZIP generado en: $DistDir/$AppName-windows.zip"
