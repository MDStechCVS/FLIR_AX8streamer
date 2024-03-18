# import cv2
# import time
# import queue
# import urllib3
# from turtle import width
# import numpy as np
import logging
import requests
import threading
import traceback
import subprocess
import xml.etree.ElementTree as ET
from UTIL.CAMERA_API import API
from UTIL.Temp_Log import TempMonitor
from UTIL.VIDEO import OpenCVCamera
from UTIL.UIGenerator import MAINUI
from UTIL.Log_Util import Init_Logger
import urllib3


from kivy.app import App
from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout



#==============================================================================================================================
urllib3_logger = logging.getLogger('urllib3') # ulib 통신 로거 ERROR 이상만 표기
urllib3_logger.setLevel(logging.ERROR)



Init_Logger() # 로그 생성
logger = logging.getLogger("TRACE") # logger get

#==============================================================================================================================

Window.fullscreen = 'auto'


class LoginApp(App):
    title = "AX8 STREAMER"

    # 로그인 및 메인화면 레이아웃 및 위젯 추가
    def build(self):
        logger.info(f"program Start!!!")

        Config.set('input', 'mouse', 'mouse, multitouch_on_demand')
        Config.set('graphics', 'resizable', 1)  # 윈도우 크기 조정 비활성화
        Config.set('graphics', 'fullscreen', 1)  # 전체 화면 모드 비활성화
        Config.set('graphics', 'borderless  ', 1)
        Config.set('kivy', 'exit_on_escape', '0')

        self.ip = None
        self.login_layout = BoxLayout(orientation='vertical')
        self.ip_label = Label(text='Enter IP:', font_size=30)
        self.ip_input = TextInput(hint_text='IP Address', text='192.168.0.178', font_size=30, width=1000, height=50)
        self.login_button = Button(text='SELECT', font_size=30)
        self.login_button.bind(on_press=self.camera_connect_check)
        self.login_layout.add_widget(self.ip_label)
        self.login_layout.add_widget(self.ip_input)
        self.login_layout.add_widget(self.login_button)
        self.float_layout = FloatLayout(size=(Window.width, Window.height))
        self.current_selected_tab  = None
        #back ground Color 
        with self.float_layout.canvas.before:
            Color(0, 0, 0, 1)
            self.rect = Rectangle(size=self.float_layout.size, pos=self.float_layout.pos)

        self.current_layout = None

        return self.login_layout


    # IP 핑테스트 및 장치 이름 확인 후 스피너 레이아웃 Open : login_button과 bind
    def camera_connect_check(self, instance):
        try:
            self.ip = self.ip_input.text
            self.ip = self.ip.replace(" ",'').replace('\n','')
            if self.ping_test:
                print("ping TEST OK")
                logger.info(f"ping TEST OK")
                
            else:
                popup = Popup(title='Error', content=Label(text='Please check the camera IP address'), size_hint=(None, None),size=(300, 200))
                logger.info(f"Camera IP Popup On") 
                popup.open()
            
            camera_name = self.check_camera_name()
            if camera_name == 'FLIR AX8':
                logger.info(f"Camera Name Check Complete // IP : {self.ip}")    
                self.api = API(self.ip)
                self.second_layout = FloatLayout()
                self.login_layout.clear_widgets()
                # UI Create
                self.UI = MAINUI(self.second_layout, self.api, self.ip)
                logger.info(f"UI Generate Complete")    
                # Camera Class Initialize
                self.CAMERA = OpenCVCamera(self.ip, self.second_layout ,size_hint=(1,1), pos=(-450, 150))
                logger.info(f"Camera Connection Complete")    
                
                #save_image func bind 
                self.UI.snapshot_button.bind(on_press=self.CAMERA.save_image)

                self.second_layout.add_widget(self.CAMERA)
                self.login_layout.add_widget(self.second_layout)
                self.TEMP = TempMonitor(self.api, self.UI)
                threading.Thread(target = self.TEMP.temp_thread, daemon=True).start()
                logger.info(f"Temperature Thread Start") 
            else:
                popup = Popup(title='Error', content=Label(text='Please check the camera product.'), size_hint=(None, None), size=(300, 200))
                logger.info(f"Camera Product Popup On") 
                popup.open()

        except Exception as e:
            print(f"error : {e}")
            


    def ping_test(ip_address):
        command = ['ping', '-c', '1', '-W', '3', ip_address]  # '-c 1'은 핑을 한 번만 보내도록 함, '-W 3'은 타임아웃 시간을 3초로 설정

        try:
            # 시스템 명령어 실행
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5, text=True)

            # 반환값이 0인 경우 핑에 대한 응답이 있음을 의미
            if result.returncode == 0:
                return True
            else:
                return False
        except subprocess.TimeoutExpired:
            # 타임아웃이 발생한 경우 (3초 내에 응답이 없는 경우)
            return False


    def check_camera_name(self):
        URL = F'http://{self.ip}/prod/res/version/product/name'
        try:
            response = requests.get(URL, timeout=2)
        except requests.exceptions.Timeout:
            print("연결 시간이 초과되었습니다.")
            return False
        
        print(response)
        root = ET.fromstring(response.content)
        if response.status_code == 200:
            camera_name = root.find(".//xsi:value", namespaces={"xsi": "http://www.w3.org/2001/XMLSchema-instance"}).text
            print(camera_name)
        else:
            return False
        return camera_name

        



if __name__ == '__main__':
    APP = LoginApp().run()


