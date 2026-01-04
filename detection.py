import cv2
import numpy as np

def detect_green_cones(frame, min_area=100):
    """
    Detect green cones using color thresholding.
    
    Args:
        frame: Input BGR frame
        min_area: Minimum contour area to consider
        
    Returns:
        List of bounding boxes (x1, y1, x2, y2) for detected cones
    """
    # Convert to HSV for better color segmentation
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define green color range (adjust these values based on your specific green shade)
    lower_green = np.array([40, 50, 50])
    upper_green = np.array([80, 255, 255])
    
    # Create mask for green color
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Apply morphological operations to remove noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter and process contours
    cone_boxes = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            x, y, w, h = cv2.boundingRect(contour)
            cone_boxes.append((x, y, x + w, y + h))
    
    return cone_boxes

def detect_red_wheels(frame, min_area=50):
    """
    Detect red wheels using color thresholding.
    
    Args:
        frame: Input BGR frame
        min_area: Minimum contour area to consider
        
    Returns:
        List of bounding boxes (x1, y1, x2, y2) for detected wheels
    """
    # Convert to HSV for better color segmentation
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define red color ranges (red wraps around in HSV)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])
    
    # Create masks for red color
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    
    # Apply morphological operations to remove noise
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter and process contours
    wheel_boxes = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            x, y, w, h = cv2.boundingRect(contour)
            wheel_boxes.append((x, y, x + w, y + h))
    
    return wheel_boxes

def group_wheels_to_skates(wheel_boxes, max_distance=100):
    """
    Group detected wheels into skates.
    
    Args:
        wheel_boxes: List of wheel bounding boxes
        max_distance: Maximum distance between wheels to be considered part of the same skate
        
    Returns:
        List of skate bounding boxes (x1, y1, x2, y2)
    """
    if not wheel_boxes:
        return []
    
    # Sort wheels by x-coordinate
    sorted_wheels = sorted(wheel_boxes, key=lambda box: box[0])
    
    # Group wheels into skates
    skates = []
    current_skate_wheels = [sorted_wheels[0]]
    
    for wheel in sorted_wheels[1:]:
        # Calculate distance to last wheel in current skate
        last_wheel = current_skate_wheels[-1]
        center1 = ((last_wheel[0] + last_wheel[2]) // 2, (last_wheel[1] + last_wheel[3]) // 2)
        center2 = ((wheel[0] + wheel[2]) // 2, (wheel[1] + wheel[3]) // 2)
        distance = np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
        
        if distance < max_distance:
            # Add to current skate
            current_skate_wheels.append(wheel)
        else:
            # Create skate bounding box from current wheels
            if len(current_skate_wheels) >= 2:  # At least 2 wheels to form a skate
                x_min = min(wheel[0] for wheel in current_skate_wheels)
                y_min = min(wheel[1] for wheel in current_skate_wheels)
                x_max = max(wheel[2] for wheel in current_skate_wheels)
                y_max = max(wheel[3] for wheel in current_skate_wheels)
                
                # Expand bounding box to include the boot
                y_min = max(0, y_min - (y_max - y_min))  # Expand upward
                
                skates.append((x_min, y_min, x_max, y_max))
            
            # Start new skate
            current_skate_wheels = [wheel]
    
    # Process the last skate
    if len(current_skate_wheels) >= 2:
        x_min = min(wheel[0] for wheel in current_skate_wheels)
        y_min = min(wheel[1] for wheel in current_skate_wheels)
        x_max = max(wheel[2] for wheel in current_skate_wheels)
        y_max = max(wheel[3] for wheel in current_skate_wheels)
        
        # Expand bounding box to include the boot
        y_min = max(0, y_min - (y_max - y_min))  # Expand upward
        
        skates.append((x_min, y_min, x_max, y_max))
    
    return skates

def detect_skates_and_cones(frame):
    """
    Detect both skates and cones in a frame using color-based detection.
    
    Args:
        frame: Input BGR frame
        
    Returns:
        Dictionary with detected objects
    """
    # Detect cones
    cone_boxes = detect_green_cones(frame)
    
    # Detect wheels and group them into skates
    wheel_boxes = detect_red_wheels(frame)
    skate_boxes = group_wheels_to_skates(wheel_boxes)
    
    # Format results
    detections = {
        'cone': [{'bbox': box, 'id': i} for i, box in enumerate(cone_boxes)],
        'skate': [{'bbox': box, 'id': i} for i, box in enumerate(skate_boxes)]
    }
    
    return detections

def check_wheel_ground_contact(frame, skate_box, threshold=0.95):
    """
    Check if wheels of a skate are touching the ground.
    
    Args:
        frame: Input BGR frame
        skate_box: Bounding box of the skate (x1, y1, x2, y2)
        threshold: Threshold for determining ground contact
        
    Returns:
        True if wheels are lifted, False if touching the ground
    """
    x1, y1, x2, y2 = skate_box
    
    # Focus on the bottom part of the skate (where wheels are)
    wheel_region_height = int((y2 - y1) * 0.25)  # Bottom 25% of the skate
    wheel_region = frame[y2 - wheel_region_height:y2, x1:x2]
    
    if wheel_region.size == 0:
        return False  # Cannot determine if empty region
    
    # Convert to HSV and detect red wheels in this region
    hsv = cv2.cvtColor(wheel_region, cv2.COLOR_BGR2HSV)
    
    # Define red color ranges - adjust for better sensitivity
    lower_red1 = np.array([0, 120, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 120, 100])
    upper_red2 = np.array([180, 255, 255])
    
    # Create masks for red color
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)
    
    # Focus specifically on the very bottom pixels
    bottom_region_height = min(5, wheel_region_height // 5)  # Bottom 5 pixels or 1/5 of wheel region
    bottom_region = mask[wheel_region_height - bottom_region_height:, :]
    
    # If red pixels detected at the very bottom, wheels likely touching ground
    red_pixels_at_bottom = np.sum(bottom_region > 0)
    total_pixels = bottom_region.size
    red_ratio = red_pixels_at_bottom / total_pixels if total_pixels > 0 else 0
    
    # Fine-tuned threshold based on the visual from screenshot
    is_lifted = red_ratio < 0.03  # If less than 3% of bottom pixels are red, consider it lifted
    
    # Debug info
    print(f"Wheel analysis - Red pixels at bottom: {red_pixels_at_bottom}, Ratio: {red_ratio:.4f}, Is lifted: {is_lifted}")
    
    return is_lifted 