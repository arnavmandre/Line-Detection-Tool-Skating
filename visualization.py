import cv2
import numpy as np

def draw_bounding_boxes(frame, objects, class_colors=None):
    """
    Draw bounding boxes around detected objects.
    
    Args:
        frame: Input BGR frame
        objects: Dictionary of objects with class names as keys and lists of objects as values
        class_colors: Dictionary mapping class names to BGR colors
        
    Returns:
        Frame with bounding boxes
    """
    if class_colors is None:
        class_colors = {
            'cone': (0, 255, 0),  # Green for cones
            'skate': (0, 0, 255)  # Red for skates
        }
    
    # Create a copy of the frame to avoid modifying the original
    result = frame.copy()
    
    # Draw bounding boxes for each class
    for class_name, items in objects.items():
        color = class_colors.get(class_name, (255, 255, 255))  # Default to white
        
        for item in items:
            # Get bounding box
            x1, y1, x2, y2 = item['bbox']
            
            # Draw rectangle
            cv2.rectangle(result, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name} {item.get('id', '')}"
            cv2.putText(result, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return result

def highlight_crossing(frame, crossing_info):
    """
    Highlight a cone crossing event.
    
    Args:
        frame: Input BGR frame
        crossing_info: Dictionary with crossing information
            - 'cone_bbox': Bounding box of the cone
            - 'skate_bbox': Bounding box of the crossing skate
            - 'is_legal': Boolean indicating if technique is legal
        
    Returns:
        Frame with highlighted crossing
    """
    if not crossing_info:
        return frame
    
    result = frame.copy()
    
    # Extract information
    cone_bbox = crossing_info.get('cone_bbox')
    skate_bbox = crossing_info.get('skate_bbox')
    is_legal = crossing_info.get('is_legal', False)
    
    # Determine color based on legality
    color = (0, 255, 0) if is_legal else (0, 0, 255)  # Green if legal, red if illegal
    
    # Draw line connecting cone and skate
    if cone_bbox and skate_bbox:
        cone_center = (
            (cone_bbox[0] + cone_bbox[2]) // 2,
            (cone_bbox[1] + cone_bbox[3]) // 2
        )
        skate_center = (
            (skate_bbox[0] + skate_bbox[2]) // 2,
            (skate_bbox[1] + skate_bbox[3]) // 2
        )
        cv2.line(result, cone_center, skate_center, color, 2)
        
        # Add emphasis to the crossing
        cv2.circle(result, cone_center, 10, color, -1)
    
    return result

def draw_status_overlay(frame, stats):
    """
    Draw an overlay with statistics and current status.
    
    Args:
        frame: Input BGR frame
        stats: Dictionary with statistics
            - 'crossings': Total number of crossings
            - 'legal_crossings': Number of legal crossings
            - 'current_status': Current status text
            - 'is_legal': Boolean indicating if current technique is legal
        
    Returns:
        Frame with status overlay
    """
    result = frame.copy()
    
    # Get statistics
    crossings = stats.get('crossings', 0)
    legal_crossings = stats.get('legal_crossings', 0)
    current_status = stats.get('current_status', '')
    is_legal = stats.get('is_legal')
    
    # Calculate metrics
    accuracy = 0 if crossings == 0 else (legal_crossings / crossings) * 100
    
    # Create background for text
    cv2.rectangle(result, (10, 10), (400, 120), (0, 0, 0), -1)
    cv2.rectangle(result, (10, 10), (400, 120), (255, 255, 255), 2)
    
    # Add statistics text
    cv2.putText(result, f"Total Crossings: {crossings}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(result, f"Legal Crossings: {legal_crossings}", (20, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(result, f"Accuracy: {accuracy:.1f}%", (20, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Add current status if available
    if current_status and is_legal is not None:
        status_color = (0, 255, 0) if is_legal else (0, 0, 255)
        cv2.putText(result, current_status, (frame.shape[1] - 200, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 3)
    
    return result

def visualize_wheel_detection(frame, skate_boxes, wheel_boxes):
    """
    Visualize the wheel detection for debugging purposes.
    
    Args:
        frame: Input BGR frame
        skate_boxes: List of skate bounding boxes
        wheel_boxes: List of wheel bounding boxes
        
    Returns:
        Frame with visualized wheel detection
    """
    result = frame.copy()
    
    # Draw wheel boxes
    for box in wheel_boxes:
        x1, y1, x2, y2 = box
        cv2.rectangle(result, (x1, y1), (x2, y2), (0, 255, 255), 2)  # Yellow for wheels
    
    # Draw skate boxes
    for box in skate_boxes:
        x1, y1, x2, y2 = box
        cv2.rectangle(result, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Red for skates
        
        # Draw line to show bottom of skate (ground contact line)
        cv2.line(result, (x1, y2), (x2, y2), (255, 0, 0), 2)  # Blue line
    
    return result

def draw_debug_info(frame, frame_number, processing_fps):
    """
    Draw debug information on the frame.
    
    Args:
        frame: Input BGR frame
        frame_number: Current frame number
        processing_fps: Processing frames per second
        
    Returns:
        Frame with debug information
    """
    result = frame.copy()
    
    # Add frame number and FPS
    cv2.putText(result, f"Frame: {frame_number}", (10, frame.shape[0] - 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(result, f"FPS: {processing_fps:.1f}", (10, frame.shape[0] - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    return result 