@echo off
echo Python Installation Checker
echo ========================
echo.

echo Checking for Python installations...
echo.

SET FOUND_PYTHON=0

REM Try standard "python" command
python --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo FOUND: Python is installed and available through 'python' command.
    python --version
    SET FOUND_PYTHON=1
)

REM Try "python3" command
python3 --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo FOUND: Python is installed and available through 'python3' command.
    python3 --version
    SET FOUND_PYTHON=1
)

REM Check common installation locations
IF EXIST "C:\Python39\python.exe" (
    echo FOUND: Python installed at C:\Python39\python.exe
    "C:\Python39\python.exe" --version
    SET FOUND_PYTHON=1
)

IF EXIST "C:\Python310\python.exe" (
    echo FOUND: Python installed at C:\Python310\python.exe
    "C:\Python310\python.exe" --version
    SET FOUND_PYTHON=1
)

IF EXIST "C:\Python311\python.exe" (
    echo FOUND: Python installed at C:\Python311\python.exe
    "C:\Python311\python.exe" --version
    SET FOUND_PYTHON=1
)

IF EXIST "C:\Python312\python.exe" (
    echo FOUND: Python installed at C:\Python312\python.exe
    "C:\Python312\python.exe" --version
    SET FOUND_PYTHON=1
)

IF EXIST "%LocalAppData%\Programs\Python\" (
    echo Looking in %LocalAppData%\Programs\Python\ ...
    dir /b "%LocalAppData%\Programs\Python\"
    SET FOUND_PYTHON=1
)

IF %FOUND_PYTHON% EQU 0 (
    echo No Python installation found on this system.
    echo.
    echo Would you like to:
    echo 1. Open Python download page in browser
    echo 2. Exit
    set /p download_choice="Enter choice (1 or 2): "
    
    if "%download_choice%"=="1" (
        echo Opening Python download page...
        start https://www.python.org/downloads/
        echo.
        echo IMPORTANT: During installation, make sure to check "Add Python to PATH"!
    )
) ELSE (
    echo.
    echo Python is installed but the script couldn't access it.
    echo This might be because:
    echo - Python is not added to the PATH environment variable
    echo - You need to restart your command prompt after installation
    echo.
    echo Try using the "run_enhanced_analyzer_fixed.bat" script which can find Python in various locations.
)

pause 