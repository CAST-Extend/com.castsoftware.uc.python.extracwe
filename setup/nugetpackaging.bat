@echo off

set VER_DEF=1.0.13-beta
Set BATCHBASE=%~dp0

Set APP_NAME=com.castsoftware.uc.python.extracwe

echo =============================================
echo NuGet Package creation
echo ==



echo = Creating package ...

set EnableNugetPackageRestore=true
NuGet.exe pack %APP_NAME%\plugin.nuspec

echo = ... done.

pause