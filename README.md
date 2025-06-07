🎥 Hand Gesture Controlled YouTube & Volume Controller

A computer vision project built using Python and MediaPipe that allows you to control YouTube playback and system volume with simple hand gestures.

✨ Features

Open YouTube Video/Playlist with a five-finger gesture.🖐️

Close YouTube Tab with a closed-fist gesture.✊

Adjust System Volume using a pinch gesture:

Pinch inwards to increase volume.🤏

Pinch outwards to decrease volume.🤏

Real-time gesture detection using webcam and MediaPipe.

Intelligent gesture state management to avoid repeated triggers.

📸 Demonstration

Insert screenshots or GIFs here if available.

🚀 Technologies Used

Python 3.x

OpenCV

MediaPipe

PyAutoGUI

Pycaw (for Windows system volume control)

Webbrowser (built-in module for opening URLs)
========================================================================================================
this project is still in building phase and may throw errors in return. The code is complete for the things mentioned above and i am planning to add many new feautures as well in the future.
Thank you.

date:- 7/6/2025
changes added in the project
I removed the pinch zoom in to increase the volume and pinch zoom out to decrease the volume as the gesture was conflicting with the previous gestures.
So i added some other gestures to control the volume without making any conflict
1. One finger Up = 20% volume👆
2. Two finger Up = 40% volume✌️
3. Three finger Up = 60% volume👌
4. Four finger Up = 100% volume🖐️
