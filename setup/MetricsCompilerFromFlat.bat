@echo off
@SetLocal EnableDelayedExpansion
@for %%a in (%0) do set CMDDIR=%%~dpa
REM java -cp "%CMDDIR%\*" -jar "%CMDDIR%\MetricsCompilerCLI.jar" %*
"C:\Program Files\Java8\bin\java.exe" -cp "%CMDDIR%\*" -cp CAST-MetricsCompiler.jar  com.castsoftware.metricscompiler.MetricsCompilerCLI %*