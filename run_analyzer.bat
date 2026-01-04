@echo off
echo Inline Skating Technique Analyzer
echo ===============================
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
echo Please select detection method:
echo 1. Color-based detection (recommended for this specific setup)
echo 2. YOLOv8 detection (better for general purpose, but may need training)

set /p choice="Enter choice (1 or 2): "

set DETECTION_METHOD=
if "%choice%"=="1" set DETECTION_METHOD=
if "%choice%"=="2" set DETECTION_METHOD=--use_yolo

echo.
echo Please select processing device:
echo 1. CPU
echo 2. CUDA (GPU acceleration)

set /p device_choice="Enter choice (1 or 2): "

set DEVICE=--device cpu
if "%device_choice%"=="2" set DEVICE=--device cuda

set /p video_path="Enter video filename: "
set /p output_path="Enter output filename (default: output.mp4): "

if "%output_path%"=="" set output_path=output.mp4

echo.
echo Processing video %video_path%...
echo.

python skating_analyzer.py --video_path "%video_path%" --output_path "%output_path%" %DETECTION_METHOD% %DEVICE% --debug

echo.
echo Processing complete! 
echo Output saved to %output_path%

:end
pause 