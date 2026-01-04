import numpy as np
import cv2
from detection import check_wheel_ground_contact

class CrossingDetector:
    """
    Detector for cone crossing events.
    """
    
    def __init__(self):
        """Initialize the crossing detector."""
        self.prev_positions = {}  # Dictionary of {object_id: previous_centroid}
        self.crossing_history = []  # List of crossing events
        self.current_crossing = None
    
    def detect(self, tracked_objects, frame):
        """
        Detect cone crossing events.
        
        Args:
            tracked_objects: Dictionary of tracked objects from the tracker
            frame: Current video frame
            
        Returns:
            Dictionary with crossing information if a crossing is detected, None otherwise
        """
        if 'cone' not in tracked_objects or 'skate' not in tracked_objects:
            return None
        
        if len(tracked_objects['skate']) < 2:
            return None
        
        # Initialize previous positions if needed
        for class_name, objects in tracked_objects.items():
            for obj in objects:
                object_id = obj['id']
                if object_id not in self.prev_positions:
                    self.prev_positions[object_id] = obj['centroid']
        
        # Check for crossings
        for cone in tracked_objects['cone']:
            cone_id = cone['id']
            cone_centroid = cone['centroid']
            
            for skate in tracked_objects['skate']:
                skate_id = skate['id']
                skate_centroid = skate['centroid']
                
                # Skip if we don't have a previous position
                if skate_id not in self.prev_positions:
                    continue
                
                prev_skate_centroid = self.prev_positions[skate_id]
                
                # Check if skate crossed the cone in this frame
                if self._is_crossing(prev_skate_centroid, skate_centroid, cone_centroid):
                    # Find the other skate to check if it's lifted
                    other_skates = [s for s in tracked_objects['skate'] if s['id'] != skate_id]
                    
                    if other_skates:
                        other_skate = other_skates[0]
                        
                        # Check if the other skate is lifted
                        is_lifted = check_wheel_ground_contact(frame, other_skate['bbox'])
                        
                        # Record the crossing
                        crossing_info = {
                            'cone_id': cone_id,
                            'cone_bbox': cone['bbox'],
                            'skate_id': skate_id,
                            'skate_bbox': skate['bbox'],
                            'other_skate_id': other_skate['id'],
                            'other_skate_bbox': other_skate['bbox'],
                            'is_legal': is_lifted,
                            'frame_position': len(self.crossing_history)
                        }
                        
                        self.crossing_history.append(crossing_info)
                        self.current_crossing = crossing_info
                        
                        return crossing_info
        
        # Update previous positions
        for class_name, objects in tracked_objects.items():
            for obj in objects:
                self.prev_positions[obj['id']] = obj['centroid']
        
        return self.current_crossing
    
    def _is_crossing(self, prev_centroid, curr_centroid, cone_centroid):
        """
        Check if a line from prev_centroid to curr_centroid crosses the cone_centroid.
        
        Args:
            prev_centroid: Previous position of the skate (x, y)
            curr_centroid: Current position of the skate (x, y)
            cone_centroid: Position of the cone (x, y)
            
        Returns:
            True if crossing occurred, False otherwise
        """
        # Get coordinates
        x1, y1 = prev_centroid
        x2, y2 = curr_centroid
        cx, cy = cone_centroid
        
        # Check if the skate moved from one side of the cone to the other
        # For simplicity, we check if the x-coordinate crossed the cone's x-coordinate
        if (x1 < cx < x2) or (x2 < cx < x1):
            # Calculate the y-coordinate at the cone's x-coordinate
            if x2 != x1:  # Avoid division by zero
                y_at_cone = y1 + (y2 - y1) * (cx - x1) / (x2 - x1)
                # Check if this y-coordinate is close to the cone's y-coordinate
                if abs(y_at_cone - cy) < 50:  # Threshold for "closeness"
                    return True
        
        return False
    
    def get_statistics(self):
        """
        Get statistics about crossings.
        
        Returns:
            Dictionary with crossing statistics
        """
        total_crossings = len(self.crossing_history)
        legal_crossings = sum(1 for crossing in self.crossing_history if crossing['is_legal'])
        
        stats = {
            'crossings': total_crossings,
            'legal_crossings': legal_crossings,
            'accuracy': (legal_crossings / total_crossings * 100) if total_crossings > 0 else 0,
        }
        
        if self.current_crossing:
            stats['current_status'] = "LEGAL" if self.current_crossing['is_legal'] else "ILLEGAL"
            stats['is_legal'] = self.current_crossing['is_legal']
        
        return stats

class TechniqueAnalyzer:
    """
    Analyzer for skating technique.
    """
    
    def __init__(self):
        """Initialize the technique analyzer."""
        self.crossing_detector = CrossingDetector()
        self.frame_count = 0
    
    def analyze(self, tracked_objects, frame):
        """
        Analyze skating technique in the current frame.
        
        Args:
            tracked_objects: Dictionary of tracked objects from the tracker
            frame: Current video frame
            
        Returns:
            Dictionary with analysis results
        """
        self.frame_count += 1
        
        # Detect crossing events
        crossing_info = self.crossing_detector.detect(tracked_objects, frame)
        
        # Get crossing statistics
        stats = self.crossing_detector.get_statistics()
        
        # Add frame count
        stats['frame_count'] = self.frame_count
        
        return {
            'crossing_info': crossing_info,
            'stats': stats
        } 