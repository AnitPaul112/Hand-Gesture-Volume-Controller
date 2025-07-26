import cv2
import mediapipe as mp
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Initialize Pycaw for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume_ctrl = cast(interface, POINTER(IAudioEndpointVolume))
vol_range = volume_ctrl.GetVolumeRange()
min_vol = vol_range[0]
max_vol = vol_range[1]

# Volume control parameters
volume_smoothing = []  # For smoothing volume changes
smoothing_factor = 5   # Number of frames to average
last_volume_update = 0
volume_update_threshold = 0.1  # Minimum time between volume updates (seconds)
distance_history = []  # For distance smoothing
distance_smoothing_factor = 3

# Capture from webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

while True:
    success, img = cap.read()
    if not success:
        break
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    lm_list = []

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((id, cx, cy))
            
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    if len(lm_list) >= 21:  # Ensure we have all 21 landmarks
        # Thumb tip is id 4, index finger tip is id 8
        x1, y1 = lm_list[4][1], lm_list[4][2]
        x2, y2 = lm_list[8][1], lm_list[8][2]
        cx, cy = (x1 + x2)//2, (y1 + y2)//2

        cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
        cv2.circle(img, (cx, cy), 8, (0, 255, 0), cv2.FILLED)

        # Calculate the distance
        length = math.hypot(x2 - x1, y2 - y1)
        
        # Smooth the distance measurement
        distance_history.append(length)
        if len(distance_history) > distance_smoothing_factor:
            distance_history.pop(0)
        smoothed_length = sum(distance_history) / len(distance_history)
        
        # Enhanced distance range for better control (adjusted for more realistic hand distances)
        min_distance = 0   # Minimum distance when fingers are close
        max_distance = 100 # Maximum distance when fingers are far apart
        
        # Clamp the distance to prevent extreme values
        smoothed_length = max(min_distance, min(max_distance, smoothed_length))
        
        # Add distance indicator
        cv2.putText(img, f'Distance: {int(smoothed_length)}', (x1, y1 - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Convert distance to volume level with better mapping
        # Using exponential curve for more natural volume control
        normalized_distance = (smoothed_length - min_distance) / (max_distance - min_distance)
        
        # Apply power curve for better volume perception (increased sensitivity)
        volume_curve = normalized_distance ** 0.5  # Lower exponent for more aggressive curve
        
        # Map to actual system volume range more accurately
        vol = np.interp(volume_curve, [0, 1], [min_vol, max_vol])
        vol_bar = np.interp(volume_curve, [0, 1], [400, 150])
        
        # Get actual system volume percentage for display
        try:
            current_system_vol = volume_ctrl.GetMasterVolumeLevel()
            actual_vol_perc = np.interp(current_system_vol, [min_vol, max_vol], [0, 100])
        except:
            actual_vol_perc = np.interp(volume_curve, [0, 1], [0, 100])  # Fallback if COM error occurs
        
        # Also calculate gesture-based percentage for comparison
        gesture_vol_perc = np.interp(volume_curve, [0, 1], [0, 100])
        
        # Smooth volume changes
        volume_smoothing.append(vol)
        if len(volume_smoothing) > smoothing_factor:
            volume_smoothing.pop(0)
        smoothed_vol = sum(volume_smoothing) / len(volume_smoothing)
        
        # Only update volume if enough time has passed and there's a significant change
        current_time = time.time()
        if current_time - last_volume_update > volume_update_threshold:
            try:
                current_vol = volume_ctrl.GetMasterVolumeLevel()
                if abs(smoothed_vol - current_vol) > 0.03:  # Reduced threshold for more responsiveness
                    volume_ctrl.SetMasterVolumeLevel(smoothed_vol, None)
                    last_volume_update = current_time
            except:
                pass  # Handle potential COM errors gracefully
        
        # Visual feedback improvements
        vol_bar_smoothed = np.interp(volume_curve, [0, 1], [400, 150])

        # Draw volume bar with better colors
        cv2.rectangle(img, (50, 150), (85, 400), (255, 255, 255), 2)
        
        # Color coding for volume levels based on actual system volume
        if actual_vol_perc < 30:
            bar_color = (0, 255, 0)  # Green for low volume
        elif actual_vol_perc < 70:
            bar_color = (0, 255, 255)  # Yellow for medium volume
        else:
            bar_color = (0, 0, 255)  # Red for high volume
            
        cv2.rectangle(img, (50, int(vol_bar_smoothed)), (85, 400), bar_color, cv2.FILLED)
        
        # Show both gesture percentage and actual system volume
        cv2.putText(img, f'Gesture: {int(gesture_vol_perc)}%', (40, 430), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (255, 255, 255), 2)
        cv2.putText(img, f'System: {int(actual_vol_perc)}%', (40, 460), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, bar_color, 2)
        

        
        # Additional info display
        cv2.putText(img, f'Smoothed: {int(smoothed_length)}', (x1, y1 - 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        # Show volume range indicators
        cv2.putText(img, 'MIN', (95, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, 'MAX', (95, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Instructions with better volume mapping info
        cv2.putText(img, 'Pinch to control volume', (120, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, (255, 255, 255), 2)
        cv2.putText(img, 'Close fingers = Low volume', (120, 80), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.5, (0, 255, 0), 1)
        cv2.putText(img, 'Far fingers = High volume', (120, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.5, (0, 0, 255), 1)
       

    cv2.imshow("Hand Gesture Volume Control", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
