import cv2
import numpy as np
import argparse
import os
import time
from ultralytics import YOLO
import torch

# Import custom modules
from detection import detect_skates_and_cones, check_wheel_ground_contact
from tracking import ObjectTracker, identify_left_right_skates
from analysis_improved import TechniqueAnalyzer
from visualization import (draw_bounding_boxes, highlight_crossing, 
                          draw_status_overlay, visualize_wheel_detection, 
                          draw_debug_info)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Inline Skating Technique Analyzer')
    parser.add_argument('--video_path', type=str, required=True, help='Path to input video')
    parser.add_argument('--output_path', type=str, default='output.mp4', help='Path to output video')
    parser.add_argument('--confidence', type=float, default=0.5, help='Detection confidence threshold')
    parser.add_argument('--device', type=str, default='cpu', help='Device to run inference on (cpu/cuda)')
    parser.add_argument('--debug', action='store_true', help='Enable debug visualization')
    parser.add_argument('--use_yolo', action='store_true', help='Use YOLOv8 for detection (vs. color-based)')
    return parser.parse_args()

def enhance_frame(frame):
    """Enhance frame for better detection in low-light conditions."""
    # Convert to LAB color space
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    # Split channels
    l, a, b = cv2.split(lab)
    # Apply CLAHE to L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    # Merge enhanced L channel with original A,B channels
    merged = cv2.merge((cl, a, b))
    # Convert back to BGR
    enhanced = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    return enhanced

def detect_objects_yolo(frame, model, confidence):
    """Detect cones and skates in the frame using YOLOv8."""
    results = model(frame, conf=confidence)
    detections = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = model.names[class_id]
            
            # Map YOLOv8 classes to our classes
            if class_name == 'traffic cone' or class_name == 'cone':
                class_name = 'cone'
            elif class_name == 'sports equipment' or class_name == 'skate':
                class_name = 'skate'
            else:
                continue  # Skip other classes
                
            detections.append({
                'bbox': (x1, y1, x2, y2),
                'confidence': confidence,
                'class_name': class_name
            })
    return detections

def process_video(args):
    """Process the video and analyze skating technique."""
    # Check if video exists
    if not os.path.isfile(args.video_path):
        print(f"Error: Video file '{args.video_path}' not found")
        return
    
    # Initialize YOLOv8 model if requested
    model = None
    if args.use_yolo:
        try:
            model = YOLO('yolov8n.pt')
            print("Loaded YOLOv8 model")
        except Exception as e:
            print(f"Error loading YOLOv8 model: {e}")
            print("Falling back to color-based detection")
            args.use_yolo = False
    
    # Open video
    video = cv2.VideoCapture(args.video_path)
    if not video.isOpened():
        print(f"Error: Could not open video '{args.video_path}'")
        return
    
    # Get video properties
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Create output video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output = cv2.VideoWriter(args.output_path, fourcc, fps, (width, height))
    
    # Initialize tracker and analyzer
    tracker = ObjectTracker()
    analyzer = TechniqueAnalyzer()
    
    print(f"Processing video: {args.video_path}")
    print(f"Total frames: {total_frames}")
    
    frame_count = 0
    processing_times = []
    
    while True:
        # Read frame
        ret, frame = video.read()
        if not ret:
            break
        
        frame_count += 1
        start_time = time.time()
        
        # Print progress
        if frame_count % 10 == 0:
            progress = frame_count / total_frames * 100
            print(f"Processing frame {frame_count}/{total_frames} ({progress:.1f}%)", end='\r')
        
        # Enhance frame for better detection
        enhanced_frame = enhance_frame(frame)
        
        # Detect objects
        if args.use_yolo:
            # YOLOv8 detection
            raw_detections = detect_objects_yolo(enhanced_frame, model, args.confidence)
            
            # Convert to tracked objects format
            detections = []
            for detection in raw_detections:
                detections.append({
                    'bbox': detection['bbox'],
                    'class_name': detection['class_name']
                })
        else:
            # Color-based detection
            detections_dict = detect_skates_and_cones(enhanced_frame)
            
            # Convert to flat list
            detections = []
            for class_name, objects in detections_dict.items():
                for obj in objects:
                    detections.append({
                        'bbox': obj['bbox'],
                        'class_name': class_name
                    })
        
        # Track objects
        tracked_objects = tracker.update(detections)
        
        # Analyze technique
        analysis_result = analyzer.analyze(tracked_objects, enhanced_frame)
        crossing_info = analysis_result['crossing_info']
        stats = analysis_result['stats']
        
        # Create visualization
        result_frame = frame.copy()
        
        # Draw bounding boxes
        result_frame = draw_bounding_boxes(result_frame, tracked_objects)
        
        # Highlight crossing if detected
        if crossing_info:
            result_frame = highlight_crossing(result_frame, crossing_info)
        
        # Draw status overlay
        result_frame = draw_status_overlay(result_frame, stats)
        
        # Add debug visualization if requested
        if args.debug:
            if not args.use_yolo:
                # Only show wheel detection visualization for color-based detection
                wheel_boxes = []
                skate_boxes = []
                for class_name, objects in tracked_objects.items():
                    if class_name == 'skate':
                        skate_boxes = [obj['bbox'] for obj in objects]
                
                result_frame = visualize_wheel_detection(result_frame, skate_boxes, wheel_boxes)
            
            # Calculate processing FPS
            if processing_times:
                processing_fps = 1.0 / (sum(processing_times) / len(processing_times))
            else:
                processing_fps = 0
                
            result_frame = draw_debug_info(result_frame, frame_count, processing_fps)
        
        # Write frame to output video
        output.write(result_frame)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        processing_times.append(processing_time)
        if len(processing_times) > 30:
            processing_times.pop(0)  # Keep only the last 30 frames for FPS calculation
    
    # Clean up
    video.release()
    output.release()
    
    # Print final statistics
    stats = analyzer.crossing_detector.get_statistics()
    print("\nProcessing complete!")
    print(f"Total frames processed: {frame_count}")
    print(f"Total crossings detected: {stats['crossings']}")
    print(f"Legal crossings: {stats['legal_crossings']}")
    print(f"Illegal crossings: {stats['crossings'] - stats['legal_crossings']}")
    print(f"Technique accuracy: {stats['accuracy']:.1f}%")
    print(f"Output written to: {args.output_path}")

def main():
    """Main function for the skating analyzer."""
    args = parse_arguments()
    process_video(args)

if __name__ == "__main__":
    main() 