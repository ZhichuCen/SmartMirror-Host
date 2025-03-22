import cv2
import sys
import can
import struct
import time
from eye_utils import get_camera, detect_eyes


def init_can_interface():
    """Initialize the CAN interface for communication"""
    try:
        # Initialize the CAN bus interface
        # For macOS with canable, typically uses slcan or socketcan interface
        bus = can.interface.Bus(bustype='slcan', channel='/dev/tty.usbmodem*', bitrate=500000)
        print("CAN interface initialized successfully")
        return bus
    except Exception as e:
        print(f"Error initializing CAN interface: {e}")
        print("Please ensure the canable device is connected and properly configured")
        sys.exit(1)


def send_eye_coordinates(can_bus, x, y):
    """Send eye midpoint coordinates via CAN with ID 0x100"""
    try:
        # Pack the x and y coordinates as floats into 8 bytes
        data = struct.pack('ff', float(x), float(y))
        
        # Create and send the CAN message
        message = can.Message(
            arbitration_id=0x100,
            data=data,
            is_extended_id=False
        )
        can_bus.send(message)
        print(f"Sent eye coordinates: x={x}, y={y}")
        return True
    except Exception as e:
        print(f"Error sending CAN message: {e}")
        return False


def process_eye_detection(face_cascade, eye_cascade):
    """Handle the eye detection process after receiving a trigger"""
    # Initialize camera
    camera = get_camera()
    if not camera.isOpened():
        print("Error: Could not open camera.")
        return None
    
    # Try to detect eyes for a short period
    max_attempts = 30  # Try for about 3 seconds at 10 fps
    attempt = 0
    eye_midpoint = None
    
    while attempt < max_attempts and eye_midpoint is None:
        # Capture frame-by-frame
        ret, frame = camera.read()
        if not ret:
            print("Error: Failed to grab frame")
            break
        
        frame = cv2.flip(frame, 1)
        
        # Process the frame to detect and mark eyes
        processed_frame, eye_midpoint = detect_eyes(frame, face_cascade, eye_cascade)
        
        # Display the resulting frame
        cv2.imshow('Eye Position Detection', processed_frame)
        cv2.waitKey(1)  # Update the display
        
        attempt += 1
        time.sleep(0.1)  # Short delay between attempts
    
    # Release the camera and close windows
    camera.release()
    cv2.destroyAllWindows()
    
    return eye_midpoint


def main():
    # Initialize CAN interface
    can_bus = init_can_interface()
    
    # Load pre-trained classifiers for face and eye detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml')
    
    # Check if the cascades were loaded successfully
    if face_cascade.empty() or eye_cascade.empty():
        print("Error: Could not load cascade classifiers")
        sys.exit(1)

    print("Waiting for CAN trigger (ID 0x200)...")
    
    while True:
        # Wait for a CAN message with ID 0x200
        message = can_bus.recv()
        
        if message is not None and message.arbitration_id == 0x200:
            print("Received trigger message. Starting eye detection...")
            
            # Process eye detection
            eye_midpoint = process_eye_detection(face_cascade, eye_cascade)
            
            # Send eye coordinates if detected
            if eye_midpoint is not None:
                x, y = eye_midpoint
                send_eye_coordinates(can_bus, x, y)
            else:
                print("No eyes detected within timeout period")
                # Send a default or error value
                send_eye_coordinates(can_bus, -1.0, -1.0)
            
            print("Waiting for next CAN trigger (ID 0x200)...")


if __name__ == "__main__":
    main()
