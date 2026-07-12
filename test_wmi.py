import subprocess
cmd = 'powershell -Command "Get-CimInstance Win32_Process -Filter \\"Name=\'chrome.exe\'\\" | Select-Object -ExpandProperty CommandLine"'
try:
    output = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
    print("Output:", output)
except Exception as e:
    print("Error:", e)
