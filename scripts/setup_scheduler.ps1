# 拓漫 TouMan — Windows Task Scheduler 自动化设置
# 需管理员权限运行: 右键 PowerShell → 以管理员身份运行

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$PythonExe = (Get-Command python).Source
$DailyScript = Join-Path $ScriptDir "tuoman_daily.py"

Write-Host "拓漫 TouMan — 设置定时任务" -ForegroundColor Cyan

# 每日获客管线 — 工作日 09:00
$DailyAction = New-ScheduledTaskAction -Execute $PythonExe `
    -Argument "`"$DailyScript`"" `
    -WorkingDirectory $ProjectRoot

$DailyTrigger = New-ScheduledTaskTrigger -Daily -At 09:00
$DailySettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "TouMan-Daily-Pipeline" `
    -Action $DailyAction `
    -Trigger $DailyTrigger `
    -Settings $DailySettings `
    -Description "拓漫 TouMan 每日获客管线" `
    -Force

Write-Host "OK TouMan-Daily-Pipeline (daily 09:00)" -ForegroundColor Green

# 每周汇总 — 周一 09:00
$WeeklyAction = New-ScheduledTaskAction -Execute $PythonExe `
    -Argument "`"$DailyScript`" --weekly" `
    -WorkingDirectory $ProjectRoot

$WeeklyTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 09:00

Register-ScheduledTask -TaskName "TouMan-Weekly-Report" `
    -Action $WeeklyAction `
    -Trigger $WeeklyTrigger `
    -Settings $DailySettings `
    -Description "拓漫 TouMan 每周获客周报" `
    -Force

Write-Host "OK TouMan-Weekly-Report (weekly Mon 09:00)" -ForegroundColor Green

Write-Host "`n已注册的拓漫定时任务:" -ForegroundColor Yellow
Get-ScheduledTask -TaskName "TouMan-*" | Format-Table TaskName, State, Triggers

Write-Host "`n运行 'taskschd.msc' 打开任务计划程序查看/修改。" -ForegroundColor Gray
