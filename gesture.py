import cv2
import mediapipe as mp
import webbrowser
import pyautogui
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# YouTube URL
youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
video_opened = False

# Volume setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
min_vol, max_vol, _ = volume.GetVolumeRange()

# Helper to detect fingers up
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
        fingers.append(1 if tip_y < pip_y else 0)

    return fingers

# Map number of fingers to volume level
def get_volume_from_fingers(finger_count):
    mapping = {
        1: 0.2,
        2: 0.4,
        3: 0.6,
        4: 1.0
    }
    return mapping.get(finger_count, None)

# Video capture
cap = cv2.VideoCapture(0)
prev_finger_count = -1

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
            finger_count = sum(finger_status)

            # YouTube Control
            if finger_count == 5 and not video_opened:
                print("Five fingers detected: Opening YouTube video")
                webbrowser.open(youtube_url)
                video_opened = True
                time.sleep(2)

            elif finger_count == 0 and video_opened:
                print("Fist detected: Closing YouTube video/tab")
                pyautogui.hotkey('ctrl', 'w')
                video_opened = False
                time.sleep(2)

            # Volume control with 1-4 fingers
            elif 1 <= finger_count <= 4 and finger_count != prev_finger_count:
                target_percent = get_volume_from_fingers(finger_count)
                if target_percent is not None:
                    new_volume = min_vol + target_percent * (max_vol - min_vol)
                    volume.SetMasterVolumeLevel(new_volume, None)
                    label = f"Volume: {int(target_percent * 100)}%"
                    print(label)
                    cv2.putText(img, label, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 3)
                prev_finger_count = finger_count

    cv2.imshow("Hand Gesture Control", img)

    if cv2.waitKey(100) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
