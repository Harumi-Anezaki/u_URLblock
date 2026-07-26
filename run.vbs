' u_URLblock - Silent Background Launcher (Commercial Edition)
' Double-clicking this script launches the application silently without opening a black command prompt window.

Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objShell = CreateObject("WScript.Shell")

strCurrentDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
objShell.CurrentDirectory = strCurrentDir

strExePath = objFSO.BuildPath(strCurrentDir, "bin\WinLogonAssist.exe")
strScriptPath = objFSO.BuildPath(strCurrentDir, "core\system_guard.pyw")
strCacheDir = objFSO.BuildPath(strCurrentDir, "authenticated_users_kakikomi_true\__pycache__")

If Not objFSO.FileExists(strExePath) Then
    MsgBox "The portable Python environment is not set up yet." & vbCrLf & vbCrLf & _
           "Please run 'setup.bat' first to initialize the environment.", _
           vbExclamation + vbOKOnly, "u_URLblock - Setup Required"
    WScript.Quit 1
End If

objShell.Environment("PROCESS").Item("PYTHONPYCACHEPREFIX") = strCacheDir
objShell.Run """" & strExePath & """ """ & strScriptPath & """", 0, False
