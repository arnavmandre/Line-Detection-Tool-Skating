# Skating Technique Analyzer - Troubleshooting Guide

## Common Issues and Solutions

### "Python not installed or not available in path" Error

This error occurs when the system cannot find the Python executable. Here are solutions:

#### Solution 1: Install Python

If Python is not installed on your system:

1. Download Python from [python.org/downloads](https://www.python.org/downloads/) (version 3.8 or higher recommended)
2. During installation, **check the box that says "Add Python to PATH"**
3. Complete the installation and restart your computer
4. Try running the script again

#### Solution 2: Use the Fixed Batch File

We've created an improved script that can find Python in different locations:

1. Run `run_enhanced_analyzer_fixed.bat` instead of the original script
2. This version will try to locate Python installed in different ways

#### Solution 3: Manually Set Python Path

If you know Python is installed but not in the PATH:

1. Find your Python installation location (e.g., `C:\Users\username\AppData\Local\Programs\Python\Python39\python.exe`)
2. Open Command Prompt and navigate to the skating code directory
3. Run the script with the full path to Python:
   ```
   "C:\Path\To\Your\Python\python.exe" skating_analyzer.py --video_path "WhatsApp Video 2025-03-18 at 7.13.14 PM.mp4" --output_path "output.mp4" --debug
   ```

### CUDA/GPU Related Errors

If you encounter errors related to CUDA:

1. Make sure you have the correct NVIDIA drivers installed
2. Try using CPU mode by selecting option 1 when prompted
3. If you want to use GPU, ensure PyTorch is installed with CUDA support:
   ```
   pip uninstall torch torchvision
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   ```
   (Change cu121 to match your CUDA version - cu118, cu121, etc.)

### Dependency Installation Errors

If you encounter errors while installing dependencies:

1. Update pip: `python -m pip install --upgrade pip`
2. Try installing dependencies one by one:
   ```
   pip install opencv-python==4.7.0.72
   pip install numpy==1.24.3
   pip install ultralytics==8.0.145
   pip install torch>=2.0.0
   pip install torchvision>=0.15.1
   pip install matplotlib==3.7.1
   pip install scikit-learn==1.2.2
   ```

### Video File Not Found

If the script cannot find your video file:

1. Make sure the video file is in the same directory as the script
2. Use the exact filename (case-sensitive)
3. If your filename has spaces, make sure to wrap it in quotes when entering

### Poor Detection Quality

If the analyzer is not correctly detecting cones or skates:

1. Try adjusting lighting conditions in your video
2. You may need to modify color thresholds in `detection.py` to match your specific cone/wheel colors
3. Experiment with the YOLO-based detection by selecting option 2 for detection method

## Still Having Issues?

If you're still experiencing problems, try the following:

1. Run the script with detailed logging:
   ```
   python skating_analyzer.py --video_path "your_video.mp4" --output_path "output.mp4" --debug > log.txt 2>&1
   ```
2. Check the log.txt file for specific error messages
3. Make sure all files are in the correct directory structure 