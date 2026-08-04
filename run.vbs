' u_URLblock - Silent Background Launcher (Commercial Edition)
' Double-clicking this script launches the application silently without opening a black command prompt window.

Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objShell = CreateObject("WScript.Shell")
Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")

' Terminate existing watchdog processes silently to apply new changes
Set colProcessList = objWMIService.ExecQuery("Select * from Win32_Process Where Name = 'WinLogonAssist.exe' OR Name = 'AudioDG_helper.exe' OR Name = 'FontHost_worker.exe' OR Name = 'SpoolerSub_helper.exe'")
For Each objProcess in colProcessList
    On Error Resume Next
    objProcess.Terminate()
    On Error GoTo 0
Next

' Small delay to allow Mutexes to release cleanly
WScript.Sleep 1000

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
