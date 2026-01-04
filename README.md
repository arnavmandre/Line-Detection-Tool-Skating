# Inline Skating Technique Analyzer

A computer vision application that analyzes slalom skating technique, specifically detecting whether the non-crossing leg is properly lifted when the first leg passes a cone.

## Features

- **Object Detection**: Detects green cones and inline skates with red wheels using color-based detection or YOLOv8
- **Event Detection**: Identifies when a skate crosses a cone
- **Technique Analysis**: Determines if the non-crossing leg is properly lifted (legal technique)
- **Video Processing**: Low-light video processing optimizations with CLAHE enhancement
- **Visualization**: Annotated output video with bounding boxes, crossing highlights, and statistics overlay
- **Real-time Statistics**: Tracks total crossings, legal crossings, and technique accuracy

## Requirements

- Python 3.8 or higher
- OpenCV 4.7.0+
- NumPy
- Ultralytics (for optional YOLOv8 detection)
- PyTorch (for YOLOv8)

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd skating-code
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python skating_analyzer.py --video_path "your_video.mp4" --output_path "output.mp4"
```

### Advanced Options

```bash
python skating_analyzer.py \
    --video_path "your_video.mp4" \
    --output_path "output.mp4" \
    --confidence 0.5 \
    --device cpu \
    --debug \
    --use_yolo
```

### Command Line Arguments

- `--video_path`: Path to input video file (required)
- `--output_path`: Path to output video file (default: `output.mp4`)
- `--confidence`: Detection confidence threshold (default: 0.5)
- `--device`: Device to run inference on - `cpu` or `cuda` (default: `cpu`)
- `--debug`: Enable debug visualization
- `--use_yolo`: Use YOLOv8 for detection instead of color-based detection

### Windows Batch Scripts

For Windows users, you can use the provided batch scripts:

- `run_analyzer.bat`: Basic analyzer runner
- `run_enhanced_analyzer.bat`: Enhanced analyzer with options
- `run_enhanced_analyzer_fixed.bat`: Fixed version with better Python path detection

## Project Structure

```
.
├── skating_analyzer.py      # Main script for video analysis
├── detection.py              # Object detection functionality (cones and skates)
├── tracking.py              # Object tracking across frames
├── analysis.py              # Basic technique analysis logic
├── analysis_improved.py     # Improved technique analysis with better precision
├── visualization.py         # Functions for visualizing results
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── TROUBLESHOOTING.md      # Troubleshooting guide
```

## How It Works

1. **Detection**: The system detects green cones and red wheels (which are grouped into skates) in each frame
2. **Tracking**: Objects are tracked across frames to maintain consistent IDs
3. **Crossing Detection**: When a skate's centroid crosses a cone's center line, a crossing event is detected
4. **Technique Analysis**: The system checks if the other skate's wheels are lifted from the ground
5. **Visualization**: Results are overlaid on the video with bounding boxes, crossing highlights, and statistics

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## License

This project is open source and available for use.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 