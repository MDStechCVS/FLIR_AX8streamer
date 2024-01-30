import time
import webbrowser
import numpy as np
import xml.etree.ElementTree as ET
import traceback


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


class INITUI():
    def __init__(self, layout, api, ip):
        self.layout = layout
        self.api = api
        self.ip = ip
        self.info = self.api.INFO
        self.rest_url = self.api.rest_url
        self.selected_mode = None
        self.selected_palette = None
        self.data_toggle_lock = False # active => False // inactive => True
        self.data_write = False
        self.save_trigger = False
        self.data_selected = ''
        self.interval = 0
        self.start_time = None


        self.create_widget()

        

        
        
    def create_widget(self):
        
        # self.coordinate_label = Label(text="X = 0\nY = 0", 
        #                         font_size = 30, 
        #                         pos=(-440, -240), 
        #                         color=(1, 1, 1, 1))
                
                
        self.led_text = Label(text="LED\nON/OFF", 
                                font_size = 20, 
                                pos=(343, 360), 
                                color=(1, 1, 1, 1))
        
        self.led_button = Button(
                            text= 'ON' if self.info['LED'] == "true" else "OFF",
                            size=(60, 60),
                            size_hint=(None, None),
                            pos=(900, 730)
                            )
        
        self.overlay_text = Label(text="OVERLAY\nON/OFF", 
                font_size = 20, 
                pos=(350, 290), 
                color=(1, 1, 1, 1))


        self.overlay_button = Button(
                    text= 'ON' if self.info['OVERLAY'] == 'false' else 'OFF',
                    size=(60, 60),  
                    size_hint = (None,None),
                    pos=(900, 660)
                    )
        self.setting_text = Label(text=" SAVE DATA", 
                        font_size = 20, 
                        pos=(365, -280), 
                        color=(1, 1, 1, 1))
        
        self.saveimg_button = Button(
            text=" Save\nImage",
            size=(100, 50),  
            size_hint = (None,None),
            pos=(820, 50)
            )


        self.savedata_button = Button(
            text="      Save\nTemperature",
            size=(100, 50),  
            size_hint = (None,None),
            pos=(820, 0)
            )
        
        self.camera_mode_text = Label(text=" CAMERA MODE", 
                        font_size = 20, 
                        pos=(375, 220), 
                        color=(1, 1, 1, 1))
                
        self.mode_toggle_group = []
        # 라디오 버튼 생성 및 그룹에 추가
        for i, option in enumerate(['IR', 'Visual', 'MSX']):
            radio_button = ToggleButton(
                text=option,
                group='mode_group',  # 그룹 이름을 지정하여 라디오 버튼 그룹을 형성합니다.
                size_hint=(None, None),
                size=(80, 30),  # 라디오 버튼의 크기를 지정합니다.
                pos=(818, 570 - i * 30),  # 라디오 버튼의 위치를 조정합니다.
            )
            if i == int(self.info['MODE'])-1:
                radio_button.state = 'down'
            radio_button.bind(on_release=self.mode_button_release)
            self.mode_toggle_group.append(radio_button)


        self.mode_select_button = Button(
        text="Select",
        size=(70, 90),  
        size_hint = (None,None),
        pos=(898, 510),
        color=(0, 1, 0, 1)
        )

        self.camera_palette_text = Label(text="PALETTE CHANGE", 
                                font_size = 20, 
                                pos=(390, 50), 
                                color=(1, 1, 1, 1))

        self.palette_toggle_group = []
        # 라디오 버튼 생성 및 그룹에 추가
        for i, option in enumerate(['arctic', 'bw', 'iron', 'lava', 'rainbow', 'rainHC']):
            radio_button = ToggleButton(
                text=option,
                group='palette_group',  # 그룹 이름을 지정하여 라디오 버튼 그룹을 형성합니다.
                size_hint=(None, None),
                size=(80, 30),  # 라디오 버튼의 크기를 지정합니다.
                pos=(818, 400 - i * 30),  # 라디오 버튼의 위치를 조정합니다.
            )
            # if option == int(self.info['PALETTE'])-1:
            #     radio_button.state = 'down'
            radio_button.bind(on_release=self.palette_button_release)
            self.palette_toggle_group.append(radio_button)


        self.palette_select_button = Button(
        text="Select",
        size=(70, 180),  
        size_hint = (None,None),
        pos=(898, 250),
        color=(0, 1, 0, 1)
        )
        
        
                
        web_button = Button(
            text='Open Website',
            font_size=15,
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.1, 'center_y': 0.03}
        )
        
        
        # tab1
        self.tabbed_panel = TabbedPanel(size_hint=(None, None), size=(600, 150), pos=(205, 0), do_default_tab=False)

        self.tabs = []

        for i in range(1, 7):
            if i <= 3:
                tab = TabbedPanelItem(text=f"SPOT {i}")
            else:
                tab = TabbedPanelItem(text=f"BOX {i-3}")
            self.tabs.append(tab)

            tab_layout = FloatLayout(size=(600, 150))
            
            active_checkbox = None
            max_text_input = None
            min_text_input= None
            active_label = Label(text=f"Active", size_hint=(None, None), size=(100, 30), pos=(180, 70))
            
            if i == 1 :
                active_checkbox = CheckBox(size_hint=(None, None), size=(30, 30), pos=(250, 70), active = True if self.info['SPOT1_ACTIVE'] == 'true' else False)
                x_text_input = TextInput(hint_text=f"1~80", size_hint=(None, None), size=(50, 30), pos=(320, 70), text = self.info['SPOT1_X'])
                y_text_input = TextInput(hint_text=f"1~60", size_hint=(None, None), size=(50, 30), pos=(460, 70), text = self.info['SPOT1_Y'])
                min_text_input = TextInput(hint_text=f"MIN", size_hint=(None, None), size=(50, 30), pos=(660, 70), text = self.info['SPOT1_MIN'])        
                max_text_input = TextInput(hint_text=f"MAX", size_hint=(None, None), size=(50, 30), pos=(660, 30), text = self.info['SPOT1_MAX'])        
                
                
            elif i == 2 :
                active_checkbox = CheckBox(size_hint=(None, None), size=(30, 30), pos=(250, 70), active= True if self.info['SPOT2_ACTIVE'] == 'true' else False)
                x_text_input = TextInput(hint_text=f"1~80", size_hint=(None, None), size=(50, 30), pos=(320, 70), text = self.info['SPOT2_X'])
                y_text_input = TextInput(hint_text=f"1~60", size_hint=(None, None), size=(50, 30), pos=(460, 70), text = self.info['SPOT2_Y'])
                min_text_input = TextInput(hint_text=f"MIN", size_hint=(None, None), size=(50, 30), pos=(660, 70), text = self.info['SPOT2_MIN'])        
                max_text_input = TextInput(hint_text=f"MAX", size_hint=(None, None), size=(50, 30), pos=(660, 30), text = self.info['SPOT2_MAX'])
                                
            elif i == 3 :
                active_checkbox = CheckBox(size_hint=(None, None), size=(30, 30), pos=(250, 70), active= True if self.info['SPOT3_ACTIVE'] == 'true' else False)
                x_text_input = TextInput(hint_text=f"1~80", size_hint=(None, None), size=(50, 30), pos=(320, 70), text = self.info['SPOT3_X'])
                y_text_input = TextInput(hint_text=f"1~60", size_hint=(None, None), size=(50, 30), pos=(460, 70), text = self.info['SPOT3_Y'])
                min_text_input = TextInput(hint_text=f"MIN", size_hint=(None, None), size=(50, 30), pos=(660, 70), text = self.info['SPOT3_MIN'])        
                max_text_input = TextInput(hint_text=f"MAX", size_hint=(None, None), size=(50, 30), pos=(660, 30), text = self.info['SPOT3_MAX'])
                
            elif i == 4 :
                active_checkbox = CheckBox(size_hint=(None, None), size=(30, 30), pos=(250, 70), active= True if self.info['BOX1_ACTIVE'] == 'true' else False)
                x_text_input = TextInput(hint_text=f"1~80", size_hint=(None, None), size=(50, 30), pos=(320, 70), text = self.info['BOX1_X'])
                y_text_input = TextInput(hint_text=f"1~60", size_hint=(None, None), size=(50, 30), pos=(460, 70), text = self.info['BOX1_Y'])
                min_text_input = TextInput(hint_text=f"MIN", size_hint=(None, None), size=(50, 30), pos=(660, 70), text = self.info['BOX1_MIN'])        
                max_text_input = TextInput(hint_text=f"MAX", size_hint=(None, None), size=(50, 30), pos=(660, 30), text = self.info['BOX1_MAX'])
                
            elif i == 5 :
                active_checkbox = CheckBox(size_hint=(None, None), size=(30, 30), pos=(250, 70), active= True if self.info['BOX2_ACTIVE'] == 'true' else False)
                x_text_input = TextInput(hint_text=f"1~80", size_hint=(None, None), size=(50, 30), pos=(320, 70), text = self.info['BOX2_X'])
                y_text_input = TextInput(hint_text=f"1~60", size_hint=(None, None), size=(50, 30), pos=(460, 70), text = self.info['BOX2_Y'])
                min_text_input = TextInput(hint_text=f"MIN", size_hint=(None, None), size=(50, 30), pos=(660, 70), text = self.info['BOX2_MIN'])        
                max_text_input = TextInput(hint_text=f"MAX", size_hint=(None, None), size=(50, 30), pos=(660, 30), text = self.info['BOX2_MAX'])
                
            elif i == 6 :
                active_checkbox = CheckBox(size_hint=(None, None), size=(30, 30), pos=(250, 70), active= True if self.info['BOX3_ACTIVE'] == 'true' else False)
                x_text_input = TextInput(hint_text=f"1~80", size_hint=(None, None), size=(50, 30), pos=(320, 70), text = self.info['BOX3_X'])
                y_text_input = TextInput(hint_text=f"1~60", size_hint=(None, None), size=(50, 30), pos=(460, 70), text = self.info['BOX3_Y'])
                min_text_input = TextInput(hint_text=f"MIN", size_hint=(None, None), size=(50, 30), pos=(660, 70), text = self.info['BOX3_MIN'])        
                max_text_input = TextInput(hint_text=f"MAX", size_hint=(None, None), size=(50, 30), pos=(660, 30), text = self.info['BOX3_MAX'])
                                
            x_label = Label(text=f"X", size_hint=(None, None), size=(100, 30), pos=(250, 70))
            y_label = Label(text=f"Y", size_hint=(None, None), size=(100, 30), pos=(370, 70))
            min_label = Label(text=f"MIN", size_hint=(None, None), size=(100, 30), pos=(580, 70))            
            max_label = Label(text=f"MAX", size_hint=(None, None), size=(100, 30), pos=(580, 30))

            width_text_input = None
            height_text_input = None
            width_label = None
            height_label = None
            
            if i == 4 :
                width_label = Label(text=f"WIDTH", size_hint=(None, None), size=(100, 30), pos=(240, 30))
                width_text_input = TextInput(hint_text=f"1~60", size_hint=(None, None), size=(50, 30), pos=(320, 30), text = self.info['BOX1_W'])
                height_label = Label(text=f"HEIGHT", size_hint=(None, None), size=(100, 30), pos=(370, 30))
                height_text_input = TextInput(hint_text=f"1~40", size_hint=(None, None), size=(50, 30), pos=(460, 30), text = self.info['BOX1_H'])
                tab_layout.add_widget(width_label)
                tab_layout.add_widget(width_text_input)
                tab_layout.add_widget(height_label)
                tab_layout.add_widget(height_text_input)
                
            elif i == 5:        
                width_label = Label(text=f"WIDTH", size_hint=(None, None), size=(100, 30), pos=(240, 30))
                width_text_input = TextInput(hint_text=f"1~60", size_hint=(None, None), size=(50, 30), pos=(320, 30), text = self.info['BOX2_W'])
                height_label = Label(text=f"HEIGHT", size_hint=(None, None), size=(100, 30), pos=(370, 30))
                height_text_input = TextInput(hint_text=f"1~40", size_hint=(None, None), size=(50, 30), pos=(460, 30), text = self.info['BOX2_H'])
                tab_layout.add_widget(width_label)
                tab_layout.add_widget(width_text_input)
                tab_layout.add_widget(height_label)
                tab_layout.add_widget(height_text_input)

            elif i == 6:
                width_label = Label(text=f"WIDTH", size_hint=(None, None), size=(100, 30), pos=(240, 30))
                width_text_input = TextInput(hint_text=f"1~60", size_hint=(None, None), size=(50, 30), pos=(320, 30), text = self.info['BOX3_W'])        
                height_label = Label(text=f"HEIGHT", size_hint=(None, None), size=(100, 30), pos=(370, 30))
                height_text_input = TextInput(hint_text=f"1~40", size_hint=(None, None), size=(50, 30), pos=(460, 30), text = self.info['BOX3_H'])
                tab_layout.add_widget(width_label)
                tab_layout.add_widget(width_text_input)
                tab_layout.add_widget(height_label)
                tab_layout.add_widget(height_text_input)
                
                
                
                
            send_button = Button(
                text='SEND',
                font_size=15,
                size_hint=(None, None),
                size=(60, 60),
                pos=(530, 35)
            )

            apply_button = Button(
                text='APPLY',
                font_size=15,
                size_hint=(None, None),
                size=(60, 60),
                pos=(730, 35)
            )
            
            
            send_button.bind(
                on_release=lambda instance, 
                            tab_name=f"TAB {i}",
                            active_text=active_checkbox, 
                            x_text=x_text_input,
                            y_text=y_text_input,
                            width_text=width_text_input, 
                            height_text=height_text_input:
                            self.send_coordi_callback(instance, tab_name, active_text, x_text, y_text, width_text, height_text))
            
            apply_button.bind(
                on_release=lambda instance, 
                            tab_name=f"TAB {i}",
                            max_temp=max_text_input, 
                            min_temp=min_text_input,:
                            self.send_temp_callback(instance, tab_name, min_temp, max_temp))
            

            tab_layout.add_widget(x_label)
            tab_layout.add_widget(x_text_input)
            tab_layout.add_widget(y_label)
            tab_layout.add_widget(y_text_input)
            tab_layout.add_widget(max_label)
            tab_layout.add_widget(min_label)
            tab_layout.add_widget(max_text_input)
            tab_layout.add_widget(min_text_input)
            tab_layout.add_widget(active_checkbox)
            tab_layout.add_widget(active_label)
            tab_layout.add_widget(send_button)
            tab_layout.add_widget(apply_button)
            
            tab.add_widget(tab_layout)
            self.tabbed_panel.add_widget(tab)

        
        # add_widget 1 
        # self.layout.add_widget(self.coordinate_label)
        self.layout.add_widget(self.led_text)
        self.layout.add_widget(self.led_button)
        self.layout.add_widget(self.overlay_text)
        self.layout.add_widget(self.overlay_button)
        self.layout.add_widget(self.setting_text)
        self.layout.add_widget(self.saveimg_button)
        self.layout.add_widget(self.savedata_button)
        self.layout.add_widget(self.camera_mode_text)
        self.layout.add_widget(self.camera_palette_text)
        self.layout.add_widget(self.tabbed_panel)
        self.layout.add_widget(web_button)


        for i in range(3):
            self.layout.add_widget(self.mode_toggle_group[i])
        for i in range(6):
            self.layout.add_widget(self.palette_toggle_group[i])

        self.layout.add_widget(self.mode_select_button)
        self.layout.add_widget(self.palette_select_button)            

        



        # bind 1 
        web_button.bind(on_press=self.open_internal_website)

        
        self.led_button.bind(on_release = self.led_button_active)
        self.overlay_button.bind(on_release = self.overlay_button_active)
        self.mode_select_button.bind(on_release = self.camera_mode_change)
        self.palette_select_button.bind(on_release = self.palette_change)
        # self.saveimg_button.bind(on_release=self.save_image)
        self.savedata_button.bind(on_release=self.save_data_popup)

        
    def save_data_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical')

        
        self.save_toggle_group = []

        # 토글 버튼 1, 2, 3, 4를 만들고 그룹에 추가
        toggle_button1 = ToggleButton(text='30 Seconds', group='toggle_group')
        toggle_button2 = ToggleButton(text='1 Minute', group='toggle_group')
        toggle_button3 = ToggleButton(text='5 Minutes', group='toggle_group')
        toggle_button4 = ToggleButton(text='10 Minutes', group='toggle_group')

        

        self.save_toggle_group.extend([toggle_button1, toggle_button2, toggle_button3, toggle_button4])

        for toggle_button in self.save_toggle_group:
            if self.data_toggle_lock:
                toggle_button.disabled = True
            popup_layout.add_widget(toggle_button)

        # 시작 버튼과 중지 버튼 생성
        start_button = Button(text='Start')
        stop_button = Button(text='Stop')
        
        start_button.bind(on_press=self.start_button_pressed)
        stop_button.bind(on_press=self.stop_button_pressed)

        # 레이아웃에 시작 버튼과 중지 버튼 추가
        popup_layout.add_widget(start_button)
        popup_layout.add_widget(stop_button)



        # 팝업 생성
        popup = Popup(title="Temperature Data Save", content=popup_layout, size_hint=(None, None), size=(400, 400))
        popup.open()
    

    def start_button_pressed(self, instance):
        self.start_time = time.time()
        self.data_selected = [btn.text for btn in self.save_toggle_group if btn.state == 'down']
        print(f'Start button pressed. Selected: {", ".join(self.data_selected)}')
        for toggle_button in self.save_toggle_group:
                toggle_button.disabled = True
                self.data_toggle_lock = True
        print(self.data_selected)
        if self.data_selected == ["30 Seconds"]:
            self.interval = 30
            print("interval change 30")
            print(f"self.interval = {self.interval}")
            
        elif self.data_selected == ["1 Minute"]:
            self.interval = 60
        elif self.data_selected == ["5 Minutes"]:
            self.interval = 300
        elif self.data_selected == ["10 Minutes"]:
            self.interval = 600
        else:
            print("not selected")



        # if self.data_selected
        self.data_write = True


    def stop_button_pressed(self, instance):
        for toggle_button in self.save_toggle_group:
                toggle_button.disabled = False
                self.data_toggle_lock = False
        self.save_trigger = True
        

        print("Stop button pressed")

    
    def open_internal_website(self, instance):
        internal_ip_address = self.ip
        if not internal_ip_address.startswith('http://') and not internal_ip_address.startswith('https://'):
            internal_ip_address = 'http://' + internal_ip_address
        print(f"internal_ip_address : {internal_ip_address}")
        webbrowser.open(internal_ip_address)
    
    
    # 기능 1 
    
    
    def palette_button_release(self, instance):
        selected_option_index = None
        for index, button in enumerate(self.palette_toggle_group):
            if button.state == 'down':
                selected_option_index = index
                break
        if selected_option_index is not None:
            self.selected_palette = self.palette_toggle_group[selected_option_index].text
            print(f"선택된 옵션: {self.selected_palette}")
        else:
            print("선택된 옵션이 없습니다.")
    
    
    def mode_button_release(self, instance):
        selected_option_index = None
        for index, button in enumerate(self.mode_toggle_group):
            if button.state == 'down':
                selected_option_index = index
                break
        if selected_option_index is not None:
            self.selected_mode = self.mode_toggle_group[selected_option_index].text
            print(f"선택된 옵션: {self.selected_mode}")
        else:
            print("선택된 옵션이 없습니다.")
            
            
    def camera_mode_change(self,instance):
        try:
            value = None
            data_list = ['image','sysimg','fusion','fusionData','fusionMode']
            if self.selected_mode == "IR":
                value = '1'
            elif self.selected_mode == "Visual":
                value = '2'
            elif self.selected_mode == "MSX":
                value = '3'
            else:
                pass
            URL = self.api.make_url(data_list, True, value)
            rst = self.api.set_camera_value(URL)
            print(f"change {self.selected_mode} Mode Complete{rst}")
        except Exception as e:
            print(f"Cam Mode Change Error = {traceback.format_exc()}")


    def palette_change(self, instance):
        try:
            print(f"target palette : {self.selected_palette}.")
            URL = self.api.make_url(['image','sysimg','palette','readFile'], True, self.selected_palette)
            print(f"Result URL = {URL}")
            rst = self.api.set_camera_value(URL)
            print(f"CAM Palette Change {rst}")
        except Exception as e:
            print(f"Cam palette Change Error = {traceback.format_exc()}")
            
            
    def led_button_active(self, instance):
        print("self.info['LED'] = {self.info['LED']}")
        if self.info['LED'] == 'false':
            self.info['LED'] = 'true'
            instance.text = "ON"
            # instance.color = (1, 0, 0, 1)
            URL = self.api.make_url(['system','vcam','torch'], True, 'true')
            print(f"Result URL = {URL}")
            rst = self.api.set_camera_value(URL)
            print(f"CAM LED ON {rst}")
    
        else:
            instance.text = "OFF"
            self.info['LED'] = 'false'
            instance.color = (1, 1, 1, 1)
            URL = self.api.make_url(['system','vcam','torch'], True, 'false')
            print(f"Result set URL = {URL}")
            rst = self.api.set_camera_value(URL)
            print(f"CAM LED OFF {rst}")
        

    # hideGraphics = true -> 숨김 / false가 overlay On
    def overlay_button_active(self, instance):
        if instance.text == "ON":
            instance.text = "OFF"
            URL = self.api.make_url(['resmon','config','hideGraphics'], True, 'true')
            print(f"off url = {URL}")
            rst = self.api.set_camera_value(URL)
            print(f"CAM Overlay OFF {rst}")
        else:
            instance.text = "ON"
            URL = self.api.make_url(['resmon','config','hideGraphics'], True, 'false')
            print(f"on url = {URL}")
            rst = self.api.set_camera_value(URL)
            print(f"CAM Overlay OFF {rst}")
            
            
    # 기능 2
    def change_tab_text_color(self, tab_index, color_index):
        if color_index == True:
            color = (1, 1, 1, 1) # white
        else:
            color = (1, 0, 0, 1) # green
        print(f"color = {color}")
        if 1 <= tab_index <= len(self.tabs):
            tab = self.tabs[tab_index]  
            tab.color = color
            

    
    
    def send_coordi_callback(self, instance, tab_name, active_checkbox, x_text, y_text, width_text=None, height_text=None):
        active_value = 'true' if active_checkbox.active else 'false'
        try:
            x_value = x_text.text
            y_value = y_text.text
            width_value = width_text.text if width_text else ""
            height_value = height_text.text if height_text else ""
            if width_value and height_value:
                self.send_coordi_info(tab_name, active_value, x_value, y_value, width_value, height_value)
                print(f"{tab_name} - Active: {active_value}, X: {x_value}, Y: {y_value}, Width: {width_value}, Height: {height_value}")
            else:
                self.send_coordi_info(tab_name, active_value, x_value, y_value)
                print(f"{tab_name} - Active: {active_value}, X: {x_value}, Y: {y_value}")
        except ValueError:
            print('숫자를 기입해주세요.')


    def send_temp_callback(self, instance, tab_name, min_temp, max_temp):
        min_value = min_temp.text
        max_value = max_temp.text
        self.send_temp_info(tab_name, min_value, max_value)
        


    def send_temp_info(self, tab_name, min_value, max_value):
        if tab_name == "TAB 1":
            self.info['SPOT1_MIN'] = min_value
            self.info['SPOT1_MAX'] = max_value
            print(f"SPOT1_MIN = {min_value}")
            print(f"SPOT1_MAX = {max_value}")


        elif tab_name == "TAB 2":
            self.info['SPOT2_MIN'] = min_value
            self.info['SPOT2_MAX'] = max_value
            print(f"SPOT2_MIN = {min_value}")
            print(f"SPOT2_MAX = {max_value}")


        
        elif tab_name == "TAB 3":
            self.info['SPOT3_MIN'] = min_value
            self.info['SPOT3_MAX'] = max_value
            print(f"SPOT3_MIN = {min_value}")
            print(f"SPOT3_MAX = {max_value}")


        
        elif tab_name == "TAB 4":
            self.info['BOX1_MIN'] = min_value
            self.info['BOX1_MAX'] = max_value
            print(f"BOX1_MIN = {min_value}")
            print(f"BOX1_MAX = {max_value}")


        elif tab_name == "TAB 5":
            self.info['BOX2_MIN'] = min_value
            self.info['BOX2_MAX'] = max_value
            print(f"BOX2_MIN = {min_value}")
            print(f"BOX2_MAX = {max_value}")


        elif tab_name == "TAB 6":
            self.info['BOX3_MIN'] = min_value
            self.info['BOX3_MAX'] = max_value
            print(f"BOX3_MIN = {min_value}")
            print(f"BOX3_MAX = {max_value}")


        else:
            print("no TAB!")
            pass
        


    def send_coordi_info(self, tab_name, active_value, x_value, y_value, width_value = None, height_value= None):
        if tab_name == "TAB 1": # spot1
            active_url = self.api.make_url(self.rest_url['SPOT1_ACTIVE'], True, active_value) 
            result = self.api.set_camera_value(active_url) 
            self.info['SPOT1_ACTIVE'] = active_value
            print(f"active_url = {active_url}")
            print(f"check 1 result = {result} active_value = {active_value}")

            X_url = self.api.make_url(self.rest_url['SPOT1_X'], True, x_value) 
            result = self.api.set_camera_value(X_url) 
            self.info['SPOT1_X'] = x_value
            print(f"X_url = {X_url}")
            print(f"check 1 result = {result} x_value = {x_value}")

            Y_url = self.api.make_url(self.rest_url['SPOT1_Y'], True, y_value) 
            result = self.api.set_camera_value(Y_url) 
            self.info['SPOT1_Y'] = y_value
            print(f"Y_url = {Y_url}")
            print(f"check 1 result = {result} y_value = {y_value}")

            if width_value and height_value:
                self.info ['SPOT1_W'] = width_value
                self.info ['SPOT1_h'] = height_value

        elif tab_name == "TAB 2": # spot2
            active_url = self.api.make_url(self.rest_url['SPOT2_ACTIVE'], True, active_value) 
            result = self.api.set_camera_value(active_url) 
            self.info['SPOT2_ACTIVE'] = active_value
            print(f"active_url = {active_url}")
            print(f"check 2 result = {result} active_value = {active_value}")

            X_url = self.api.make_url(self.rest_url['SPOT2_X'], True, x_value) 
            result = self.api.set_camera_value(X_url) 
            self.info['SPOT2_X'] = x_value
            print(f"X_url = {X_url}")
            print(f"check 2 result = {result} x_value = {x_value}")

            Y_url = self.api.make_url(self.rest_url['SPOT2_Y'], True, y_value) 
            result = self.api.set_camera_value(Y_url) 
            self.info['SPOT2_Y'] = y_value
            print(f"Y_url = {Y_url}")
            print(f"check 2 result = {result} y_value = {y_value}")

            if width_value and height_value:
                self.info ['SPOT2_W'] = width_value
                self.info ['SPOT2_h'] = height_value

            
        elif tab_name == "TAB 3": # spot3
            active_url = self.api.make_url(self.rest_url['SPOT3_ACTIVE'], True, active_value) 
            result = self.api.set_camera_value(active_url) 
            self.info['SPOT3_ACTIVE'] = active_value
            print(f"active_url = {active_url}")
            print(f"check 3 result = {result} active_value = {active_value}")

            X_url = self.api.make_url(self.rest_url['SPOT3_X'], True, x_value) 
            result = self.api.set_camera_value(X_url) 
            self.info['SPOT3_X'] = x_value
            print(f"X_url = {X_url}")
            print(f"check 3 result = {result} x_value = {x_value}")

            Y_url = self.api.make_url(self.rest_url['SPOT3_Y'], True, y_value) 
            result = self.api.set_camera_value(Y_url) 
            self.info['SPOT3_Y'] = y_value
            print(f"Y_url = {Y_url}")
            print(f"check 3 result = {result} y_value = {y_value}")

            if width_value and height_value:
                self.info ['SPOT3_W'] = width_value
                self.info ['SPOT3_h'] = height_value
            
        elif tab_name == "TAB 4": # box1
            active_url = self.api.make_url(self.rest_url['BOX1_ACTIVE'], True, active_value) 
            result = self.api.set_camera_value(active_url) 
            self.info['BOX1_ACTIVE'] = active_value
            print(f"active_url = {active_url}")
            print(f"check 4 result = {result} active_value = {active_value}")

            X_url = self.api.make_url(self.rest_url['BOX1_X'], True, x_value) 
            result = self.api.set_camera_value(X_url) 
            self.info['BOX1_X'] = x_value
            print(f"X_url = {X_url}")
            print(f"check 4 result = {result} x_value = {x_value}")

            Y_url = self.api.make_url(self.rest_url['BOX1_Y'], True, y_value) 
            result = self.api.set_camera_value(Y_url) 
            self.info['BOX1_Y'] = y_value
            print(f"Y_url = {Y_url}")
            print(f"check 4 result = {result} y_value = {y_value}")
        
            if width_value and height_value:
                # width 
                width_url = self.api.make_url(self.rest_url['BOX1_W'], True, width_value) 
                result = self.api.set_camera_value(width_url) 
                self.info ['BOX1_W'] = width_value

                # height
                height_url = self.api.make_url(self.rest_url['BOX1_H'], True, height_value) 
                result = self.api.set_camera_value(height_url) 
                self.info ['BOX1_H'] = height_value
            
        elif tab_name == "TAB 5": # box2
            active_url = self.api.make_url(self.rest_url['BOX2_ACTIVE'], True, active_value) 
            result = self.api.set_camera_value(active_url) 
            self.info['BOX2_ACTIVE'] = active_value
            print(f"active_url = {active_url}")
            print(f"check 5 result = {result} active_value = {active_value}")

            X_url = self.api.make_url(self.rest_url['BOX2_X'], True, x_value) 
            result = self.api.set_camera_value(X_url) 
            self.info['BOX2_X'] = x_value
            print(f"X_url = {X_url}")
            print(f"check 5 result = {result} x_value = {x_value}")

            Y_url = self.api.make_url(self.rest_url['BOX2_Y'], True, y_value) 
            result = self.api.set_camera_value(Y_url) 
            self.info['BOX2_Y'] = y_value
            print(f"Y_url = {Y_url}")
            print(f"check 5 result = {result} y_value = {y_value}")
        
            if width_value and height_value:
                # width 
                width_url = self.api.make_url(self.rest_url['BOX2_W'], True, width_value) 
                result = self.api.set_camera_value(width_url) 
                self.info ['BOX2_W'] = width_value

                # height
                height_url = self.api.make_url(self.rest_url['BOX2_H'], True, height_value) 
                result = self.api.set_camera_value(height_url) 
                self.info ['BOX2_H'] = height_value

            
        elif tab_name == "TAB 6": # box3
            print(f"dic = {self.info}")
            active_url = self.api.make_url(self.rest_url['BOX3_ACTIVE'], True, active_value) 
            result = self.api.set_camera_value(active_url) 
            self.info['BOX3_ACTIVE'] = active_value
            print(f"active_url = {active_url}")
            print(f"check 6 result = {result} active_value = {active_value}")

            X_url = self.api.make_url(self.rest_url['BOX3_X'], True, x_value) 
            result = self.api.set_camera_value(X_url) 
            self.info['BOX3_X'] = x_value
            print(f"X_url = {X_url}")
            print(f"check 6 result = {result} x_value = {x_value}")

            Y_url = self.api.make_url(self.rest_url['BOX3_Y'], True, y_value) 
            result = self.api.set_camera_value(Y_url) 
            self.info['BOX3_Y'] = y_value
            print(f"Y_url = {Y_url}")
            print(f"check 6 result = {result} y_value = {y_value}")
        
            if width_value and height_value:
                # width 
                width_url = self.api.make_url(self.rest_url['BOX3_W'], True, width_value) 
                result = self.api.set_camera_value(width_url) 
                self.info ['BOX3_W'] = width_value

                # height
                height_url = self.api.make_url(self.rest_url['BOX3_H'], True, height_value) 
                result = self.api.set_camera_value(height_url) 
                self.info ['BOX3_H'] = height_value