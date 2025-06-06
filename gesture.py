import cv2
import mediapipe as mp
import webbrowser
import pyautogui
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math

# Mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# YouTube URL
youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

video_opened = False
open_time = 0

# Setup pycaw for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
vol_range = volume.GetVolumeRange()  # (min, max, increment)
min_vol = vol_range[0]
max_vol = vol_range[1]

def fingers_up(hand_landmarks):
    fingers = []
    # Thumb
    if hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x < hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Fingers
    for tip_id in [mp_hands.HandLandmark.INDEX_FINGER_TIP,
                   mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                   mp_hands.HandLandmark.RING_FINGER_TIP,
                   mp_hands.HandLandmark.PINKY_TIP]:
        tip_y = hand_landmarks.landmark[tip_id].y
        pip_y = hand_landmarks.landmark[tip_id - 2].y
        if tip_y < pip_y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

cap = cv2.VideoCapture(0)

prev_pinch_dist = None
volume_control_enabled = False

while True:
    success, img = cap.read()
    if not success:
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(img_rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            finger_status = fingers_up(hand_landmarks)

            # Open/close video based on five fingers or fist
            if finger_status == [1, 1, 1, 1, 1] and not video_opened:
                print("Five fingers detected: Opening YouTube video")
                webbrowser.open(youtube_url)
                video_opened = True
                open_time = time.time()
                time.sleep(2)

            elif finger_status == [0, 0, 0, 0, 0] and video_opened:
                print("Fist detected: Closing YouTube video/tab")
                pyautogui.hotkey('ctrl', 'w')
                video_opened = False
                time.sleep(2)

            # Pinch detection for volume control
            # Get thumb tip and index finger tip landmarks
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Calculate distance between thumb tip and index finger tip
            h, w, _ = img.shape
            x1, y1 = int(thumb_tip.x * w), int(thumb_tip.y * h)
            x2, y2 = int(index_tip.x * w), int(index_tip.y * h)
            pinch_dist = math.hypot(x2 - x1, y2 - y1)

            # Draw circle on fingertips and line between them
            cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)

            # Threshold to activate volume control - pinch fingers closer than 50 pixels approx
            if pinch_dist < 50:
                volume_control_enabled = True

            if volume_control_enabled and prev_pinch_dist is not None:
                # Compare current pinch distance to previous
                if pinch_dist < prev_pinch_dist - 2:  # Fingers moving closer → volume up
                    current_vol = volume.GetMasterVolumeLevel()
                    new_vol = min(current_vol + 1.0, max_vol)
                    volume.SetMasterVolumeLevel(new_vol, None)
                    cv2.putText(img, f'Volume UP', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                    print("Volume Up")

                elif pinch_dist > prev_pinch_dist + 2:  # Fingers moving apart → volume down
                    current_vol = volume.GetMasterVolumeLevel()
                    new_vol = max(current_vol - 1.0, min_vol)
                    volume.SetMasterVolumeLevel(new_vol, None)
                    cv2.putText(img, f'Volume DOWN', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                    print("Volume Down")

            prev_pinch_dist = pinch_dist

            # If fingers open more than threshold, stop volume control
            if pinch_dist > 70:
                volume_control_enabled = False
                prev_pinch_dist = None

    cv2.imshow("Hand Gesture Control", img)

    if cv2.waitKey(100) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
