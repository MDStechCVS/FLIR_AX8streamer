import numpy as np
import cv2, time
import traceback
import os.path
import threading

class VideoUtilsClass():
    def __init__(self, windows, ip, fps):
        self.windows = windows
        self.fps = fps                  # 영상 프레임 수
        self.ip = ip
        self.rtsp_url = f"rtsp://{self.ip}/avc"
        self.cap = cv2.VideoCapture(self.rtsp_url)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
        
    # Camera Image        
    def camera_loop(self):
        cnt = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            cnt += 1
            self.windows.show_img(frame)
            time.sleep(0.01)
