import cv2
import sys
from eye_utils import get_camera, detect_eyes
from config import DISPLAY, EYE_DETECTION


def main():
    """
    Debug utility to test eye detection algorithm in real-time with camera feedback.
    Press 'Esc' to exit.
    """
    # Initialize camera
    camera = get_camera()
    if not camera.isOpened():
        print("Error: Could not open camera.")
        sys.exit(1)

    # Load pre-trained classifiers for face and eye detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye_tree_eyeglasses.xml')
    
    # Check if the cascades were loaded successfully
    if face_cascade.empty() or eye_cascade.empty():
        print("Error: Could not load cascade classifiers")
        sys.exit(1)

    print("Press 'Esc' to exit")

    while True:
        # Capture frame-by-frame
        ret, frame = camera.read()
        if not ret:
            print("Error: Failed to grab frame")
            break
            
        frame = cv2.flip(frame, 1)

        # Process the frame to detect and mark eyes
        processed_frame, eye_midpoint = detect_eyes(frame, face_cascade, eye_cascade)
        
        # Display eye midpoint if detected
        if eye_midpoint:
            print(f"Eye midpoint: {eye_midpoint}")

        # Display the resulting frame
        cv2.imshow(DISPLAY['window_name'], processed_frame)

        # Exit if 'Esc' is pressed
        if cv2.waitKey(1) & 0xFF == 27:
            break

    # Release the camera and close windows
    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
