import cv2
import platform
import sys
from config import CAMERA, DISPLAY, EYE_DETECTION


def get_camera():
    """
    Initialize camera with platform-specific configurations if needed.
    
    Returns:
        cv2.VideoCapture: Initialized camera object
    """
    system = platform.system()

    if system == "Darwin":  # macOS
        # Try to find the built-in camera by trying different indices from the config
        built_in_camera_candidates = CAMERA['macos_camera_indices']
        
        for camera_index in built_in_camera_candidates:
            camera = cv2.VideoCapture(camera_index)
            if camera.isOpened():
                # Found a working camera
                print(f"Using camera index {camera_index}")
                return camera
                
        # If we get here, no camera was found
        print("Could not find any working camera")
        return cv2.VideoCapture(0)  # Fallback to default
    elif system == "Linux":  # For SBC like Raspberry Pi
        # Some SBCs may need specific settings
        camera = cv2.VideoCapture(0)
        return camera
    elif system == "Windows":
        return cv2.VideoCapture(0)
    else:
        print(f"Unsupported system: {system}")
        sys.exit(1)


def detect_eyes(frame, face_cascade, eye_cascade):
    """
    Detect faces and eyes in a frame, and draw relevant markers.
    
    Args:
        frame: The input image frame
        face_cascade: Pre-trained face detection classifier
        eye_cascade: Pre-trained eye detection classifier
        
    Returns:
        tuple: The processed frame with detection markers and eye midpoint coordinates (or None if no eyes detected)
    """
    # Create a copy of the frame to avoid modifying the original
    processed_frame = frame.copy()
    
    # Convert to grayscale for detection
    gray = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2GRAY)

    # Detect faces using parameters from config
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=EYE_DETECTION['face_scale_factor'],
        minNeighbors=EYE_DETECTION['face_min_neighbors'],
        minSize=EYE_DETECTION['face_min_size']
    )

    # For each face, detect eyes
    for (x, y, w, h) in faces:
        # Draw rectangle around face using color from config
        cv2.rectangle(processed_frame, (x, y), (x + w, y + h), DISPLAY['face_color'], 2)

        # Define region of interest for eyes (upper half of the face)
        roi_y = y + int(h * 0.2)  # Start from 20% down the face
        roi_h = int(h * 0.4)      # Use only the upper 40% of the face
        
        roi_gray = gray[roi_y:roi_y + roi_h, x:x + w]
        roi_color = processed_frame[roi_y:roi_y + roi_h, x:x + w]

        # Detect eyes with parameters from config
        eyes = eye_cascade.detectMultiScale(
            roi_gray,
            scaleFactor=EYE_DETECTION['eye_scale_factor'],
            minNeighbors=EYE_DETECTION['eye_min_neighbors'],
            minSize=(int(w/12), int(h/12)),  # Minimum size based on face dimensions
            maxSize=(int(w/3), int(h/4))     # Maximum size based on face dimensions
        )

        # Process detected eyes
        eye_midpoint = process_detected_eyes(processed_frame, eyes, x, roi_y, w, h, roi_color)
        if eye_midpoint:
            return processed_frame, eye_midpoint
    
    # No eyes detected
    return processed_frame, None


def process_detected_eyes(frame, eyes, face_x, roi_y, face_w, face_h, roi_color):
    """
    Process detected eyes to filter valid ones and calculate midpoint.
    
    Args:
        frame: The frame being processed
        eyes: Detected eye regions
        face_x: X-coordinate of the face
        roi_y: Y-coordinate of the region of interest
        face_w: Width of the face
        face_h: Height of the face
        roi_color: Color image of the region of interest
        
    Returns:
        tuple or None: Eye midpoint coordinates if valid eyes detected, None otherwise
    """
    # Filter and validate eyes
    valid_eyes = []
    for (ex, ey, ew, eh) in eyes:
        # Filter out detections with unusual aspect ratios
        aspect_ratio = ew / eh
        if (EYE_DETECTION['eye_aspect_ratio_min'] <= aspect_ratio <= 
            EYE_DETECTION['eye_aspect_ratio_max']):
            valid_eyes.append((ex, ey, ew, eh))
    
    # Sort eyes by x-coordinate (left to right)
    valid_eyes.sort(key=lambda eye: eye[0])
    
    # Only process if we have 1-2 eyes (some people might have one eye closed)
    if 1 <= len(valid_eyes) <= 2:
        # Store eye centers for midpoint calculation
        eye_centers = []
        
        for (ex, ey, ew, eh) in valid_eyes:
            # Calculate center of the eye, accounting for the ROI offset
            eye_center_x = face_x + ex + ew // 2
            eye_center_y = roi_y + ey + eh // 2
            eye_centers.append((eye_center_x, eye_center_y))

            # Draw rectangle around eye using color from config
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), DISPLAY['eye_color'], 2)

            # Draw a point at eye center
            cv2.circle(frame, (eye_center_x, eye_center_y), 3, DISPLAY['point_color'], -1)

            # Display eye position coordinates
            cv2.putText(frame, f"({eye_center_x}, {eye_center_y})",
                        (eye_center_x, eye_center_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, DISPLAY['coord_color'], 1)
        
        # Calculate the midpoint between the eyes (or use the single eye position)
        if len(eye_centers) == 2:
            midpoint_x = (eye_centers[0][0] + eye_centers[1][0]) // 2
            midpoint_y = (eye_centers[0][1] + eye_centers[1][1]) // 2
        else:
            midpoint_x, midpoint_y = eye_centers[0]
        
        # Draw and label the midpoint
        cv2.circle(frame, (midpoint_x, midpoint_y), 5, DISPLAY['mid_color'], -1)
        cv2.putText(frame, f"Midpoint: ({midpoint_x}, {midpoint_y})",
                    (midpoint_x, midpoint_y - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, DISPLAY['mid_color'], 2)
        
        return (midpoint_x, midpoint_y)
    
    return None
