from turtle import width
import cv2
import time
import queue
import requests
import threading
import traceback
import numpy as np
import xml.etree.ElementTree as ET
from UTIL.CAMERA_API import API
from UTIL.Temp_Log import TempMonitor
from UTIL.VIDEO import OpenCVCamera
from UTIL.UIGenerator import INITUI



from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.texture import Texture
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem

Window.size = (1000, 800)
Window.resizable = False

URL_LIST = None



class LoginApp(App):
    title = "AX8 STREAMER"

    # 로그인 및 메인화면 레이아웃 및 위젯 추가
    def build(self):
        Config.set('graphics', 'resizable', '0')
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
            self.api = API(self.ip)
            camera_name = self.check_camera_name()
            if camera_name == 'FLIR AX8':    
                self.second_layout = FloatLayout()
                self.login_layout.clear_widgets()
                # UI Create
                self.UI = INITUI(self.second_layout, self.api, self.ip)
                # Camera Class Initialize
                self.CAMERA = OpenCVCamera(self.ip, self.second_layout ,size_hint=(1,1), pos=(-100, 100))
                
                #save_image func bind 
                self.UI.saveimg_button.bind(on_press=self.CAMERA.save_image)

                self.second_layout.add_widget(self.CAMERA)
                self.login_layout.add_widget(self.second_layout)
                self.TEMP = TempMonitor(self.api, self.UI)
                threading.Thread(target = self.TEMP.temp_thread, daemon=True).start()
            else:
                popup = Popup(title='Error', content=Label(text='Please enter an IP address.'), size_hint=(None, None),
                            size=(300, 200))
                popup.open()
        except Exception as e:
            print(f"error : {e}")

    # def temp_monitor_run(self):
    #     pass
    #     self.TEMP = TempMonitor(self, self.camera_info, self.UI.tabs)
    #     threading.Thread(target = self.TEMP.temp_thread, daemon=True).start()

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
    Config.set('input', 'mouse', 'mouse, multitouch_on_demand')
    APP = LoginApp().run()


