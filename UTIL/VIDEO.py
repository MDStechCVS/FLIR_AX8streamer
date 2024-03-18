import cv2
import time
import queue
import logging
import os.path
import datetime
import traceback
import threading
import numpy as np
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from UTIL.Log_Util import Init_Logger



Init_Logger()
logger = logging.getLogger("TRACE") # logger get



class OpenCVCamera(Image):
    def __init__(self, ip, layout, **kwargs):
        super(OpenCVCamera, self).__init__(**kwargs)
        self.stream_ip = "rtsp://"+ ip + "/avc" 
        self.layout = layout
        self.capture = None
        self.connect_camera(self.stream_ip)
        threading.Thread(target=self.get_image, daemon=True).start()
        Clock.schedule_interval(self.update, 1.0 / 10.0)  
        self.capture_trigger = False
        self.coordinate_label = Label(text="X = 0\nY = 0", 
                        font_size = 30, 
                        pos=(-900, -300), 
                        color=(1, 1, 1, 1))
        self.layout.add_widget(self.coordinate_label)


    def connect_camera(self, ip):
        try:
            self.capture = cv2.VideoCapture(ip)
            logger.info(f"Camera Instance Create")
            if not self.capture.isOpened():
                raise Exception("Error: Could not open the stream.")
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return


    def save_image(self, instance):
        self.capture_trigger = True
        print("Image save !")


    def update(self ,dt):
        try:
            if not self.image_queue.empty():
                frame = self.image_queue.get()
                buf = cv2.flip(frame, 0).tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.texture = texture
            else:
                print('pass while')
            time.sleep(0.05)
        except Exception as e:
            print(f"Error in camera update: {traceback.format_exc()}")          


    def get_image(self):
        self.image_queue = queue.Queue()
        self.error_cnt = 0
        try:
            while True:
                ret, frame = self.capture.read()
                if not ret:
                    logger.info(f"[get_image]\tnot ret")
                    self.error_cnt += 1
                    if self.error_cnt >= 10:
                        self.release_camera()
                        print("Reconnecting camera...")
                        logger.info("Reconnecting camera...")
                        self.connect_camera(self.stream_ip)
                        self.error_cnt = 0
                        time.sleep(1)
                    continue
                frame = cv2.resize(frame, (1000, 750))
                self.image_queue.put(frame)

                if self.capture_trigger:
                    save_path = self.save_info()
                    cv2.imwrite(f"{save_path}", frame)
                    logger.info(f"print(f"save_path = {save_path}")")
                    print(f"save_path = {save_path}")
                    self.capture_trigger = False
                time.sleep(0.05)

        except Exception as e:
            print(f"get_image traceback : {traceback.format_exc()}")
            logger.error(f"[get_image]] in Exception: {traceback.format_exc()}")
            self.release_camera()
            print("Error occurred. Reconnecting camera...")
            logger.error("Error occurred. Reconnecting camera...")
            self.connect_camera(self.stream_ip)
            time.sleep(1)


    def release_camera(self):
        try:
            if self.capture is not None:
                self.capture.release()
                print("Camera released")
                logger.info("[release_camera]\tCamera released")
        except Exception as e:
            print(f"Error releasing camera: {e}")
            logger.error("[release_camera]\tCamera released")


    def save_info(self):
        folder_path = f'./save'
        os.makedirs(folder_path, exist_ok=True)
        save_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S.%f')
        return f"{folder_path}/{save_time}.jpg"
    
    
    def on_touch_down(self, touch):
        if (10 <= touch.pos[0] <= 1010) and (315 <= touch.pos[1] <= 1065):
            final_x = round(((touch.pos[0] - 10) / 1000) * 79) + 1
            final_y = round((1065 - touch.pos[1]) / 750 * 59) + 1
            if self.collide_point(*touch.pos):
                self.coordinate_label.text = f"X = {final_x}\nY = {round(final_y)}"
                print(f"Mouse clicked at (x = {final_x}, y = {final_y})")
        else:
            print("The coordinates are out of bounds")


       




