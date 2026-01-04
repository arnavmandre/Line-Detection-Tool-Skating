@echo off
echo Enhanced Inline Skating Technique Analyzer
echo =========================================
echo This version precisely analyzes frames only when your skate crosses a cone line
echo and checks if your other skate is lifted off the ground.
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    goto end
)

REM Check if dependencies are installed
echo Checking dependencies...
pip install -r requirements.txt

REM Display video files in the current directory
echo.
echo Available video files:
dir /b *.mp4 *.mov *.avi

echo.
echo This enhanced version uses color-based detection optimized for green cones and red wheels.
echo It focuses specifically on the exact moment when your skate crosses a cone line.

echo.
echo Please select processing device:
echo 1. CPU
echo 2. CUDA (GPU acceleration)

set /p device_choice="Enter choice (1 or 2): "

set DEVICE=--device cpu
if "%device_choice%"=="2" set DEVICE=--device cuda

set /p video_path="Enter video filename (e.g. WhatsApp Video 2025-03-18 at 7.13.14 PM.mp4): "
set /p output_path="Enter output filename (default: enhanced_output.mp4): "

if "%output_path%"=="" set output_path=enhanced_output.mp4

echo.
echo Processing video %video_path%...
echo Focusing on precise cone crossing detection and wheel-ground contact...
echo.

python skating_analyzer.py --video_path "%video_path%" --output_path "%output_path%" %DEVICE% --debug

echo.
echo Processing complete! 
echo Enhanced output saved to %output_path%

:end
pause 