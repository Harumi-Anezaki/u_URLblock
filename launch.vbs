Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\AAAAA_many\app\u_URLblock"
WshShell.Run "cmd.exe /c " & chr(34) & chr(34) & "C:\AAAAA_many\app\u_URLblock\bin\WinLogonAssist.exe" & chr(34) & " system_guard.pyw > vbs_out.log 2>&1" & chr(34), 0
Set WshShell = Nothing
