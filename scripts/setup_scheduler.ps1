# 拓漫 TouMan — Windows Task Scheduler 定时任务
# 用法: 以管理员身份运行 PowerShell → .\scripts\setup_scheduler.ps1

$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$PythonExe = "$ProjectRoot\.venv\Scripts\python.exe"
$Runner = "$ProjectRoot\scripts\daily.py"

if (-not (Test-Path $PythonExe)) {
    Write-Host "❌ 未找到虚拟环境: $PythonExe" -ForegroundColor Red
    Write-Host "请先运行 tuoman-install.ps1 安装依赖" -ForegroundColor Yellow
    exit 1
}

Write-Host "拓漫 TouMan — 设置定时任务" -ForegroundColor Cyan

# 每日 09:00
$DailyAction = New-ScheduledTaskAction -Execute $PythonExe `
    -Argument "`"$Runner`"" `
    -WorkingDirectory $ProjectRoot
$DailyTrigger = New-ScheduledTaskTrigger -Daily -At 09:00
$DailySettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "TouMan-Daily-Pipeline" `
    -Action $DailyAction -Trigger $DailyTrigger -Settings $DailySettings `
    -Description "拓漫 TouMan 每日获客管线 (B站+小红书)" -Force
Write-Host "  ✅ TouMan-Daily-Pipeline (工作日 09:00)" -ForegroundColor Green

# 每周一 09:00
$WeeklyTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 09:00
Register-ScheduledTask -TaskName "TouMan-Weekly-Report" `
    -Action $DailyAction -Trigger $WeeklyTrigger -Settings $DailySettings `
    -Description "拓漫 TouMan 每周获客汇总" -Force
Write-Host "  ✅ TouMan-Weekly-Report (周一 09:00)" -ForegroundColor Green

Write-Host "`n已注册的任务:" -ForegroundColor Yellow
Get-ScheduledTask -TaskName "TouMan-*" | Format-Table TaskName, State, Triggers
