import numpy as np
import cv2

class ObjectTracker:
    """
    Simple object tracker that maintains identities across frames.
    """
    
    def __init__(self, max_disappeared=10, max_distance=100):
        """
        Initialize the tracker.
        
        Args:
            max_disappeared: Maximum number of frames an object can be missing
            max_distance: Maximum distance between centroids to consider them the same object
        """
        self.next_object_id = 0
        self.objects = {}  # Dictionary of {object_id: (centroid, class_name, bbox)}
        self.disappeared = {}  # Dictionary of {object_id: count}
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
    
    def register(self, centroid, class_name, bbox):
        """
        Register a new object.
        
        Args:
            centroid: Tuple of (x, y) coordinates of the centroid
            class_name: Class name of the object
            bbox: Bounding box of the object (x1, y1, x2, y2)
        """
        self.objects[self.next_object_id] = (centroid, class_name, bbox)
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1
    
    def deregister(self, object_id):
        """
        Deregister an object.
        
        Args:
            object_id: ID of the object to deregister
        """
        del self.objects[object_id]
        del self.disappeared[object_id]
    
    def update(self, detections):
        """
        Update the tracker with new detections.
        
        Args:
            detections: List of detections, each a dictionary with 'bbox' and 'class_name'
            
        Returns:
            Dictionary mapping class names to lists of tracked objects
        """
        # Handle empty detections case
        if len(detections) == 0:
            # Mark all tracked objects as disappeared
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                
                # Deregister if disappeared for too long
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            
            return self._get_tracking_results()
        
        # Create centroids for new detections
        new_centroids = []
        new_classes = []
        new_bboxes = []
        
        for detection in detections:
            bbox = detection['bbox']
            x1, y1, x2, y2 = bbox
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2
            
            new_centroids.append((cx, cy))
            new_classes.append(detection['class_name'])
            new_bboxes.append(bbox)
        
        # Handle the case where we have no tracked objects
        if len(self.objects) == 0:
            for i in range(len(new_centroids)):
                self.register(new_centroids[i], new_classes[i], new_bboxes[i])
        else:
            # Get existing object IDs and centroids
            object_ids = list(self.objects.keys())
            object_centroids = [self.objects[obj_id][0] for obj_id in object_ids]
            
            # Compute distances between existing objects and new detections
            distances = np.zeros((len(object_centroids), len(new_centroids)))
            
            for i, object_centroid in enumerate(object_centroids):
                for j, new_centroid in enumerate(new_centroids):
                    # Only match objects of the same class
                    if self.objects[object_ids[i]][1] != new_classes[j]:
                        distances[i, j] = float('inf')
                    else:
                        # Calculate Euclidean distance
                        distances[i, j] = np.sqrt(
                            (object_centroid[0] - new_centroid[0]) ** 2 +
                            (object_centroid[1] - new_centroid[1]) ** 2
                        )
            
            # Find the smallest distance for each row and column
            rows = distances.min(axis=1).argsort()
            cols = distances.argmin(axis=1)[rows]
            
            used_rows = set()
            used_cols = set()
            
            # Loop through each matched row-column pair
            for row, col in zip(rows, cols):
                # If the distance is too large, skip this match
                if distances[row, col] > self.max_distance:
                    continue
                
                # If this row or column has already been matched, skip it
                if row in used_rows or col in used_cols:
                    continue
                
                # Get the ID of the matching existing object
                object_id = object_ids[row]
                
                # Update the object's centroid, class, and bbox
                self.objects[object_id] = (new_centroids[col], new_classes[col], new_bboxes[col])
                self.disappeared[object_id] = 0
                
                # Mark this row and column as used
                used_rows.add(row)
                used_cols.add(col)
            
            # Get the rows and columns we didn't use
            unused_rows = set(range(distances.shape[0])).difference(used_rows)
            unused_cols = set(range(distances.shape[1])).difference(used_cols)
            
            # If we have more existing objects than new objects, we need to check if any
            # objects have disappeared
            if distances.shape[0] >= distances.shape[1]:
                for row in unused_rows:
                    object_id = object_ids[row]
                    self.disappeared[object_id] += 1
                    
                    if self.disappeared[object_id] > self.max_disappeared:
                        self.deregister(object_id)
            else:
                # Otherwise, we need to register new objects
                for col in unused_cols:
                    self.register(new_centroids[col], new_classes[col], new_bboxes[col])
        
        return self._get_tracking_results()
    
    def _get_tracking_results(self):
        """
        Get the current tracking results.
        
        Returns:
            Dictionary mapping class names to lists of tracked objects
        """
        results = {}
        
        for object_id, (centroid, class_name, bbox) in self.objects.items():
            if class_name not in results:
                results[class_name] = []
            
            # Add this object to the results
            results[class_name].append({
                'id': object_id,
                'centroid': centroid,
                'bbox': bbox
            })
        
        return results

def identify_left_right_skates(tracked_objects):
    """
    Identify which skate is the left one and which is the right one.
    
    Args:
        tracked_objects: Dictionary of tracked objects from ObjectTracker
        
    Returns:
        Tuple of (left_skate, right_skate) or (None, None) if not enough skates
    """
    if 'skate' not in tracked_objects or len(tracked_objects['skate']) < 2:
        return None, None
    
    # Get the first two skates
    skate1, skate2 = tracked_objects['skate'][:2]
    
    # Compare x-coordinates of centroids
    if skate1['centroid'][0] < skate2['centroid'][0]:
        return skate1, skate2  # skate1 is left, skate2 is right
    else:
        return skate2, skate1  # skate2 is left, skate1 is right 