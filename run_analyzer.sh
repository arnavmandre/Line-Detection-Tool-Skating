#!/bin/bash

echo "Inline Skating Technique Analyzer"
echo "==============================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if dependencies are installed
echo "Checking dependencies..."
pip install -r requirements.txt || {
    echo "Failed to install dependencies. Please make sure pip is installed."
    exit 1
}

# Display video files in the current directory
echo
echo "Available video files:"
ls -la *.mp4 *.mov *.avi 2>/dev/null || echo "No video files found in current directory."

echo
echo "Please select detection method:"
echo "1. Color-based detection (recommended for this specific setup)"
echo "2. YOLOv8 detection (better for general purpose, but may need training)"

read -p "Enter choice (1 or 2): " choice

DETECTION_METHOD=""
if [ "$choice" = "2" ]; then
    DETECTION_METHOD="--use_yolo"
fi

echo
echo "Please select processing device:"
echo "1. CPU"
echo "2. CUDA (GPU acceleration)"

read -p "Enter choice (1 or 2): " device_choice

DEVICE="--device cpu"
if [ "$device_choice" = "2" ]; then
    DEVICE="--device cuda"
fi

read -p "Enter video filename: " video_path
read -p "Enter output filename (default: output.mp4): " output_path

if [ -z "$output_path" ]; then
    output_path="output.mp4"
fi

echo
echo "Processing video $video_path..."
echo

python3 skating_analyzer.py --video_path "$video_path" --output_path "$output_path" $DETECTION_METHOD $DEVICE --debug

echo
echo "Processing complete!"
echo "Output saved to $output_path" 