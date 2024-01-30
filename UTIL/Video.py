import numpy as np
import cv2, time
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
import queue
import datetime
import traceback
import os.path
import threading



class OpenCVCamera(Image):
    def __init__(self, ip, layout, **kwargs):
        super(OpenCVCamera, self).__init__(**kwargs)
        stream_ip = "rtsp://"+ ip + "/avc" 
        self.layout = layout

        try:
            self.capture = cv2.VideoCapture(stream_ip)
            if not self.capture.isOpened():
                raise Exception("Error: Could not open the stream.")
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return
        threading.Thread(target=self.get_image, daemon=True).start()
        Clock.schedule_interval(self.update, 1.0 / 10.0)  # 9 FPS
        self.capture_trigger = False
        self.coordinate_label = Label(text="X = 0\nY = 0", 
                        font_size = 30, 
                        pos=(-440, -240), 
                        color=(1, 1, 1, 1))
        self.layout.add_widget(self.coordinate_label)

    def save_image(self, instance):
        self.capture_trigger = True
        print("Image save !")

    def update(self ,dt):
        try:
            if not self.image_queue.empty():
                print(f"queue size check : {self.image_queue.qsize()}")
                frame = self.image_queue.get()
                buf = cv2.flip(frame, 0).tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.texture = texture
            else:
                print('pass while')
                pass
        except Exception as e:
            print(f"Error in camera update: {traceback.format_exc()}")

    def get_image(self):
        self.image_queue = queue.Queue()
        try:
            while True:
                ret, frame = self.capture.read()
                if not ret:
                    return
                frame = cv2.resize(frame, (800, 600))
                self.image_queue.put(frame)

                if self.capture_trigger:
                    save_path = self.save_info()
                    cv2.imwrite(f"{save_path}", frame)
                    print(f"save_path = {save_path}")
                    self.capture_trigger = False
                time.sleep(0.001)
        except Exception as e:
            print(f"get_image traceback : {traceback.format_exc()}")

    def save_info(self):
        folder_path = f'./save'
        os.makedirs(folder_path, exist_ok=True)
        save_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S.%f')
        return f"{folder_path}/{save_time}.jpg"
    

    def on_touch_down(self, touch):
        x = int(touch.pos[0]) - 10
        y = - int(touch.pos[1]) + 788
        if (0 < x < 800) and (0 < y < 600):
            if self.collide_point(*touch.pos):
                self.coordinate_label.text = f"X = {round(x * 0.1)}\nY = {round(y * 0.1)}"
                print(f"Mouse clicked at (x = {x}, y = {y})")
        else:
            print("out of coordinate")
        return super().on_touch_down(touch)

