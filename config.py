"""
Configuration settings for the eye detection system.
Centralizes all parameters for easier management.
"""
import platform
import os

# Detect operating system
CURRENT_OS = platform.system()

# Define platform-specific CAN channel paths
CAN_CHANNELS = {
    'Windows': 'COM14',  # Default Windows COM port for CAN devices
    'Darwin': '/dev/tty.usbmodem*',  # macOS
    'Linux': '/dev/ttyUSB0'  # Linux
}

# CAN Bus Configuration
CAN_CONFIG = {
    'bustype': 'slcan',
    'channel': CAN_CHANNELS.get(CURRENT_OS, 'COM3'),  # Default to COM3 if OS not found
    'bitrate': 500000,
    'trigger_id': 0x200,
    'data_id': 0x100,
    'data_format': 'ii'  # Format string for struct.pack: two int32 values
}

# Eye Detection Configuration
EYE_DETECTION = {
    'max_detection_attempts': 30,
    'attempt_delay': 0.1,  # seconds
    'face_scale_factor': 1.1,
    'face_min_neighbors': 5,
    'face_min_size': (30, 30),
    'eye_scale_factor': 1.1,
    'eye_min_neighbors': 6,
    'eye_aspect_ratio_min': 0.5,
    'eye_aspect_ratio_max': 2.0
}

# Camera Configuration
CAMERA = {
    'macos_camera_indices': [1, 0, 2],
    'flip_horizontal': True
}

# Display Configuration
DISPLAY = {
    'window_name': 'Eye Position Detection',
    'face_color': (255, 0, 0),    # Blue in BGR
    'eye_color': (0, 255, 0),     # Green in BGR
    'point_color': (0, 0, 255),   # Red in BGR
    'coord_color': (0, 255, 255), # Yellow in BGR
    'mid_color': (255, 0, 255),   # Purple in BGR
}

# Error Values
ERROR_VALUES = {
    'no_eyes_detected': (-1, -1)  # Changed to integers for int32 packing
}
