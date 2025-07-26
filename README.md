# Hand Gesture Volume Controller

A real-time hand gesture-based volume control system that allows you to adjust your computer's system volume using simple finger pinch gestures. Built with MediaPipe for hand tracking and Pycaw for Windows audio control.

## Features

### 🎛️ Gesture Controls
- **Pinch to Control**: Pinch your thumb and index finger together to lower volume
- **Spread to Increase**: Move thumb and index finger apart to raise volume
- **Real-time Response**: Instant visual and audio feedback
- **Smooth Control**: Advanced smoothing algorithms prevent volume jumps

### 📊 Visual Feedback
- **Live Hand Tracking**: Real-time hand landmark visualization
- **Volume Bar**: Color-coded vertical volume indicator
- **Distance Display**: Shows finger distance measurements
- **Dual Volume Display**: Both gesture-based and actual system volume percentages
- **Color-Coded Levels**: Green (low), Yellow (medium), Red (high) volume indicators

### 🔧 Advanced Features
- **Exponential Volume Curve**: Natural volume perception mapping
- **Distance Smoothing**: Reduces jitter in hand tracking
- **Volume Change Smoothing**: Prevents sudden volume spikes
- **COM Error Handling**: Robust error handling for audio system
- **Threshold-based Updates**: Efficient volume updates only when necessary

## Requirements

### Python Dependencies
```bash
pip install opencv-python
pip install mediapipe
pip install numpy
pip install pycaw
pip install comtypes
```

### System Requirements
- **Operating System**: Windows (required for Pycaw audio control)
- **Camera**: Webcam or external camera
- **Python**: 3.7 or higher

## Installation & Setup

1. **Clone or download the project**
   ```bash
   git clone https://github.com/AnitPaul112/Hand-Gesture-Volume-Controller
   cd mediapipe
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install individually:
   ```bash
   pip install opencv-python mediapipe numpy pycaw comtypes
   ```

3. **Run the application**
   ```bash
   python volume_controller.py
   ```

## How to Use

### Getting Started
1. **Position your hand** clearly in front of the camera
2. **Extend your thumb and index finger** to start control
3. **Adjust volume** by changing the distance between your fingers

### Gesture Controls
- **Lower Volume**: Pinch thumb and index finger close together
- **Raise Volume**: Spread thumb and index finger apart
- **Mute**: Bring fingers very close (minimum distance)
- **Max Volume**: Spread fingers to maximum comfortable distance

### Visual Interface
```
┌─────────────────────────────────────────────────────────┐
│                Camera Feed (640x480)                    │
│  ┌─────┐  Hand Gesture Volume Control                   │
│  │ MIN │  Pinch to control volume                       │
│  │     │  Close fingers = Low volume                    │
│  │ VOL │  Far fingers = High volume                     │
│  │ BAR │                                                │
│  │     │  Distance: 45                                  │
│  │     │  Smoothed: 42                                  │
│  │ MAX │                                                │
│  └─────┘  Gesture: 65%                                  │
│           System: 67%                                   │
└─────────────────────────────────────────────────────────┘
```

### Controls
- **ESC Key**: Exit the application
- **Camera View**: Shows real-time hand tracking with landmarks

## Technical Details

### Architecture
- **Hand Detection**: MediaPipe Hands solution with 21 landmark points
- **Audio Control**: Pycaw library for Windows Core Audio APIs
- **Distance Calculation**: Euclidean distance between thumb tip (ID 4) and index finger tip (ID 8)
- **Volume Mapping**: Exponential curve for natural volume perception

### Key Components

#### Hand Tracking Configuration
```python
mp_hands.Hands(
    max_num_hands=1,                    # Single hand tracking
    min_detection_confidence=0.7,       # High confidence threshold
    min_tracking_confidence=0.5         # Moderate tracking threshold
)
```

#### Volume Smoothing Parameters
- **Distance Smoothing**: 3-frame averaging for stable measurements
- **Volume Smoothing**: 5-frame averaging for smooth audio changes
- **Update Threshold**: 0.1 seconds minimum between volume updates
- **Change Threshold**: 0.03 minimum volume difference for updates

#### Distance Range Configuration
- **Minimum Distance**: 0 pixels (fingers touching)
- **Maximum Distance**: 100 pixels (comfortable spread)
- **Volume Curve**: Square root function for natural perception

### Performance Optimizations
- **Efficient Landmark Processing**: Only processes necessary hand points
- **Throttled Updates**: Rate-limited volume changes prevent system overload
- **Error Handling**: Graceful COM error recovery
- **Memory Management**: Circular buffers for smoothing data

## Troubleshooting

### Common Issues

**Camera not detected:**
- Ensure webcam is properly connected and not in use by other applications
- Try changing camera index: `cv2.VideoCapture(1)` instead of `cv2.VideoCapture(0)`
- Check camera permissions in Windows settings

**Hand tracking not working:**
- **Lighting**: Ensure good, consistent lighting
- **Background**: Use a plain background for better hand detection
- **Hand Position**: Keep hand clearly visible and within frame
- **Distance**: Maintain 1-2 feet from camera for optimal tracking

**Volume not changing:**
- **Windows Audio**: Ensure audio drivers are properly installed
- **Permissions**: Run as administrator if needed
- **Audio Device**: Check that the correct audio device is set as default
- **COM Errors**: Restart the application if COM interface errors occur

**Jittery volume control:**
- **Hand Stability**: Keep hand steady while gesturing
- **Lighting Consistency**: Avoid changing light conditions
- **Smoothing**: Adjust `smoothing_factor` and `distance_smoothing_factor` values

### Performance Tips
- **Optimal Distance**: Keep 18-24 inches from camera
- **Hand Orientation**: Keep palm facing camera for best landmark detection
- **Gesture Speed**: Make slow, deliberate movements for better control
- **Background**: Use solid, contrasting background

## Customization

### Adjusting Sensitivity
```python
# Distance range for volume control
min_distance = 0    # Minimum finger distance
max_distance = 100  # Maximum finger distance

# Volume curve sensitivity
volume_curve = normalized_distance ** 0.5  # Lower = more sensitive
```

### Smoothing Parameters
```python
smoothing_factor = 5            # Volume smoothing frames
distance_smoothing_factor = 3   # Distance smoothing frames
volume_update_threshold = 0.1   # Seconds between updates
```

### Visual Customization
```python
# Volume bar colors
bar_color = (0, 255, 0)   # Green for low volume
bar_color = (0, 255, 255) # Yellow for medium volume  
bar_color = (0, 0, 255)   # Red for high volume
```

### Hand Tracking Settings
```python
hands = mp_hands.Hands(
    max_num_hands=1,                    # Number of hands to track
    min_detection_confidence=0.7,       # Detection sensitivity
    min_tracking_confidence=0.5         # Tracking stability
)
```

## Advanced Features

### Volume Curve Mathematics
The application uses an exponential curve to map finger distance to volume:
```python
volume_curve = normalized_distance ** 0.5
```
This provides more natural volume control that matches human perception.

### Dual Smoothing System
- **Distance Smoothing**: Reduces hand tracking jitter
- **Volume Smoothing**: Prevents audio system overload

### Error Recovery
- **COM Error Handling**: Automatic recovery from Windows audio API errors
- **Camera Error Handling**: Graceful handling of camera disconnection
- **Memory Management**: Prevents memory leaks in long sessions

## System Integration

### Windows Audio API
The application integrates directly with Windows Core Audio APIs through Pycaw:
- **Real-time Volume Control**: Direct system volume manipulation
- **Volume Range Detection**: Automatic detection of system volume limits
- **Audio Device Management**: Works with default audio output device

### MediaPipe Integration
- **21-Point Hand Model**: Full hand landmark detection
- **Real-time Processing**: 30+ FPS hand tracking
- **Cross-platform Compatibility**: MediaPipe works on multiple platforms

## Contributing

Potential improvements and contributions:
- **Multi-platform Support**: Add macOS and Linux audio control
- **Gesture Expansion**: Add more hand gestures for additional controls
- **UI Enhancements**: Improve visual feedback and interface
- **Configuration**: Add settings file for customization
- **Recording**: Add gesture recording and playback features

## License

This project is open source and available under the MIT License.

## Credits

- **MediaPipe**: Google's MediaPipe for hand tracking
- **Pycaw**: Python Core Audio Windows Library
- **OpenCV**: Computer vision and camera interface
- **NumPy**: Numerical computing support

---

**Made with ❤️ using Python, MediaPipe, and Windows Audio APIs**

*Control your computer's volume with the power of hand gestures!*
