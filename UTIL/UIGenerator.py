import time
import logging
import traceback
import webbrowser
import numpy as np
import xml.etree.ElementTree as ET

from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.garden.graph import Graph, LinePlot
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader

logger = logging.getLogger("TRACE")



class MAINUI():
    def __init__(self, layout, api, ip):
        self.layout = layout
        self.api = api
        self.ip = ip
        self.info = self.api.INFO
        self.rest_url = self.api.rest_url
        self.selected_mode = None
        self.selected_palette = None
        self.data_toggle_lock = False # active => False // inactive => True
        self.sub_info = [['SPOT1_ACTIVE', 'SPOT1_X', 'SPOT1_Y', 'SPOT1_MIN', 'SPOT1_MAX'], 
                        ['SPOT2_ACTIVE', 'SPOT2_X', 'SPOT2_Y', 'SPOT2_MIN', 'SPOT2_MAX'], 
                        ['SPOT3_ACTIVE', 'SPOT3_X', 'SPOT3_Y', 'SPOT3_MIN', 'SPOT3_MAX'], 
                        ['BOX1_ACTIVE', 'BOX1_X', 'BOX1_Y','BOX1_MIN', 'BOX1_MAX', 'BOX1_W', 'BOX1_H'], 
                        ['BOX2_ACTIVE', 'BOX2_X', 'BOX2_Y', 'BOX2_MIN', 'BOX2_MAX', 'BOX2_W', 'BOX2_H'], 
                        ['BOX3_ACTIVE', 'BOX3_X', 'BOX3_Y','BOX3_MIN', 'BOX3_MAX', 'BOX3_W', 'BOX3_H']]

        self.data_write = False
        self.save_trigger = False
        self.data_selected = ''
        self.interval = 0
        self.start_time = None
        self.start_button = None
        self.temp_tabs = []
        self.chart_tabs = []
        self.chart_data_spot1 = []
        self.chart_data_spot2 = []
        self.chart_data_spot3 = []
        self.chart_data_box1 = []
        self.chart_data_box2 = []
        self.chart_data_box3 = []

        self.create_widget()


    def create_chart_widget(self):
        panel_pos = (1020, 410)
        self.chart_panel = TabbedPanel(size_hint=(None, None), size=(600, 650), pos = panel_pos, do_default_tab=False)
        spot1_tab = TabbedPanelHeader(text='SPOT1')
        spot2_tab = TabbedPanelHeader(text='SPOT2')
        spot3_tab = TabbedPanelHeader(text='SPOT3')
        box1_tab = TabbedPanelHeader(text='BOX1')
        box2_tab = TabbedPanelHeader(text='BOX2')
        box3_tab = TabbedPanelHeader(text='BOX3')

        self.chart_tabs.append(spot1_tab)
        self.chart_tabs.append(spot2_tab)
        self.chart_tabs.append(spot3_tab)
        self.chart_tabs.append(box1_tab)
        self.chart_tabs.append(box2_tab)
        self.chart_tabs.append(box3_tab)


        spot1_tab.content = self.create_chart_content('SPOT1')
        spot2_tab.content = self.create_chart_content('SPOT2')
        spot3_tab.content = self.create_chart_content('SPOT3')
        box1_tab.content = self.create_chart_content('BOX1')
        box2_tab.content = self.create_chart_content('BOX2')
        box3_tab.content = self.create_chart_content('BOX3')


        self.chart_panel.add_widget(spot1_tab)
        self.chart_panel.add_widget(spot2_tab)
        self.chart_panel.add_widget(spot3_tab)
        self.chart_panel.add_widget(box1_tab)
        self.chart_panel.add_widget(box2_tab)
        self.chart_panel.add_widget(box3_tab)
        
        return self.chart_panel
    

    def create_chart_content(self, name):
        if name == "SPOT1":
            graph, self.plot_spot1 = self.create_graph("spot")
            self.graph_spot1 = graph
            return graph
        elif name == "SPOT2":
            graph, self.plot_spot2 = self.create_graph("spot")
            self.graph_spot2 = graph
            # self.update_graph(graph, plot)
            return graph
        elif name == "SPOT3":
            graph, self.plot_spot3 = self.create_graph("spot")
            self.graph_spot3 = graph
            # self.update_graph(graph, plot)
            return graph
        elif name == "BOX1":
            graph, self.boxplot_max_1, self.boxplot_min_1 = self.create_graph("box")
            self.graph_box1 = graph
            return graph
        elif name == "BOX2":
            graph, self.boxplot_max_2, self.boxplot_min_2 = self.create_graph("box")
            self.graph_box2 = graph
            return graph
        elif name == "BOX3":
            graph, self.boxplot_max_3, self.boxplot_min_3 = self.create_graph("box")
            self.graph_box3 = graph
            return graph


    def create_graph(self, category):
        graph = Graph(x_ticks_minor=1,
                    y_ticks_major=5,
                    y_grid_label=True, x_grid_label=True, padding=5,
                    x_grid=True, y_grid=True)
        graph.x_label = 'Time'
        graph.x_ticks_major = 0
        graph.x_grid_label = True
        graph.x_label_rotation = 45

        # Adjusting graph properties
        graph.xmin = -0.5  # x 축 최솟값
        graph.xmax = 9.5  # x 축 최댓값
        graph.ymin = 0  # y 축 최솟값
        graph.ymax = 50  # y 축 최댓값

        # SmoothLinePlot으로 그래프를 만듭니다.
        if category == "spot":
            plot = LinePlot(color=[1, 0, 0, 1], line_width=4)
            graph.add_plot(plot)
            return graph, plot
        if category == "box":
            plot1 = LinePlot(color=[1, 0, 0, 1], line_width=4)
            plot2 = LinePlot(color=[0, 0, 1, 1], line_width=4)
            graph.add_plot(plot1)
            graph.add_plot(plot2)
            return graph, plot1, plot2


    def update_graph(self, graph, plot):
        # Generate random data for 10 points
        x = np.arange(0, 10, 1)  # 범위를 0부터 90까지로 변경하여 10개의 데이터를 생성
        y = np.random.randint(0, 10, size=1)
        data = list(zip(x, y))
        # Update the plot
        plot.points = data

            
    def update_graph_spot(self, data, target_plot):
        x = list(range(len(data)))  # x 값을 인덱스로 설정
        y = data  # y 값은 주어진 데이터 그대로 사용

        target_plot.points = list(zip(x, y))


    def update_graph_box(self, data, target_plot1, target_plot2):
        x = list(range(len(data)))  
        y1 = [entry[0] for entry in data]  # 데이터 리스트 안의 첫 번째 요소로부터 첫 번째 plot에 대한 y값 추출
        y2 = [entry[1] for entry in data]  # 데이터 리스트 안의 두 번째 요소로부터 두 번째 plot에 대한 y값 추출

        target_plot1.points = list(zip(x, y1))
        target_plot2.points = list(zip(x, y2))


    def transfer_temperature(self,category, temperature):
        if category == "spot1":
            self.chart_data_spot1.append(temperature)
            data = self.list_normalize(self.chart_data_spot1)
            self.update_graph_spot(data, self.plot_spot1)
            print(f"spot1 data\t len = {len(data)}   data = {data}")
        
        elif category == "spot2":
            self.chart_data_spot2.append(temperature)
            data = self.list_normalize(self.chart_data_spot2)
            self.update_graph_spot(data, self.plot_spot2)
            print(f"spot2 data\t len = {len(data)}   data = {data}")
        
        elif category == "spot3":
            self.chart_data_spot3.append(temperature)
            data = self.list_normalize(self.chart_data_spot3)
            self.update_graph_spot(data, self.plot_spot3)
            print(f"spot3 data\t len = {len(data)}   data = {data}")
        
        elif category == "box1":
            self.chart_data_box1.append(temperature)
            self.chart_data_box1 = self.list_normalize(self.chart_data_box1)
            self.update_graph_box(self.chart_data_box1, self.boxplot_max_1, self.boxplot_min_1)
            # print(f"box1 data\t len = {len(data)}   data = {data}")
        
        elif category == "box2":
            self.chart_data_box2.append(temperature)
            self.chart_data_box2 = self.list_normalize(self.chart_data_box2)
            self.update_graph_box(self.chart_data_box2, self.boxplot_max_2, self.boxplot_min_2)
            # print(f"box2 data\t len = {len(data)}   data = {data}")
        
        elif category == "box3":
            self.chart_data_box3.append(temperature)
            self.chart_data_box3 = self.list_normalize(self.chart_data_box3)
            self.update_graph_box(self.chart_data_box3, self.boxplot_max_3, self.boxplot_min_3)
            # print(f"box3 data\t len = {len(data)}   data = {data}")
        else:
            print("invalid Value")
            

    def list_normalize(self, data):
        # 입력 데이터가 1차원 리스트인 경우
        if isinstance(data[0], (int, float)):
            if len(data) > 10:
                # 최대 10개의 데이터만 유지하도록 잘라냄
                data = data[-10:]
            return data
        # 입력 데이터가 2차원 리스트인 경우
        elif isinstance(data[0], list):
            # 2차원 리스트의 복사본 생성
            copied_data = [sublist[:] for sublist in data]
            for sublist in copied_data:
                if len(sublist) == 11:
                    # 첫 번째 요소 삭제
                    del sublist[0]
            if len(copied_data) > 10:
                # 최대 10개의 서브 리스트만 유지하도록 잘라냄
                copied_data = copied_data[-10:]
            return copied_data


    def create_tempature_widget(self):
        panel_pos = (1020, 5)
        # panel_pos = (1020, 720)
        self.temp_panel = TabbedPanel(size_hint=(None, None), size=(600, 300), pos = panel_pos, do_default_tab=False)
        spot1_tab = TabbedPanelHeader(text='SPOT1')
        spot2_tab = TabbedPanelHeader(text='SPOT2')
        spot3_tab = TabbedPanelHeader(text='SPOT3')
        box1_tab = TabbedPanelHeader(text='BOX1')
        box2_tab = TabbedPanelHeader(text='BOX2')
        box3_tab = TabbedPanelHeader(text='BOX3')
        
        self.temp_tabs.append(spot1_tab)
        self.temp_tabs.append(spot2_tab)
        self.temp_tabs.append(spot3_tab)
        self.temp_tabs.append(box1_tab)
        self.temp_tabs.append(box2_tab)
        self.temp_tabs.append(box3_tab)

        spot1_tab.content = self.create_temp_content('SPOT1')
        spot2_tab.content = self.create_temp_content('SPOT2')
        spot3_tab.content = self.create_temp_content('SPOT3')
        box1_tab.content = self.create_temp_content('BOX1')
        box2_tab.content = self.create_temp_content('BOX2')
        box3_tab.content = self.create_temp_content('BOX3')

        self.temp_panel.add_widget(spot1_tab)
        self.temp_panel.add_widget(spot2_tab)
        self.temp_panel.add_widget(spot3_tab)
        self.temp_panel.add_widget(box1_tab)
        self.temp_panel.add_widget(box2_tab)
        self.temp_panel.add_widget(box3_tab)
        
        return self.temp_panel
    
    
    def create_temp_content(self, name):
        self.temp_tab_layout = FloatLayout(size=(600, 600))
        try:
            if "SPOT" in name:

                if "1" in name : 
                    self.make_temptab_ui(0)

                elif "2" in name:
                    self.make_temptab_ui(1)

                elif "3" in name:
                    self.make_temptab_ui(2)

            elif "BOX" in name:

                if "1" in name:
                    self.make_temptab_ui(3, True)

                elif "2" in name:
                    self.make_temptab_ui(4, True)

                elif "3" in name:
                    self.make_temptab_ui(5, True)

            else:
                print("other ...")
            self.temp_tabs[int(name[-1])-1].add_widget(self.temp_tab_layout)
            
        except Exception as e:
            print(f"Temp TAB Create error {traceback.format_exc()}")
            
        return self.temp_tab_layout
        

    def create_widget(self):
        temp_tabs = self.create_tempature_widget()
        self.layout.add_widget(temp_tabs)

        setting_tabs = self.create_setting_tab()
        self.layout.add_widget(setting_tabs)

        chart_tabs = self.create_chart_widget()
        self.layout.add_widget(chart_tabs)


    def make_temptab_ui(self, index, box = False):
        self.width_text_input = None
        self.height_text_input = None
        keys = self.sub_info[index]
        std_x = 1000
        std_y = 930 - 715
        self.active_label = Label(text=f"Active", size_hint=(None, None), size=(100, 30), pos = (std_x, std_y))
        self.x_label = Label(text=f"X", size_hint=(None, None), size=(100, 30), pos = (std_x + 80, std_y))
        self.y_label = Label(text=f"Y", size_hint=(None, None),size=(100, 30), pos=(std_x + 80, std_y - 50))
        self.min_label = Label(text=f"MIN", size_hint=(None, None), size=(100, 30), pos=(std_x + 400, std_y)) 
        self.max_label = Label(text=f"MAX", size_hint=(None, None), size=(100, 30), pos=(std_x + 400, std_y - 50))
        
        self.temp_tab_layout.add_widget(self.active_label)
        self.temp_tab_layout.add_widget(self.x_label)
        self.temp_tab_layout.add_widget(self.y_label)
        self.temp_tab_layout.add_widget(self.min_label)
        self.temp_tab_layout.add_widget(self.max_label)

        self.active_checkbox = CheckBox(size_hint=(None, None), size=(30, 30), pos=(std_x + 80 , std_y), active = True if self.info[keys[0]] == 'true' else False)
        self.x_text_input = TextInput(hint_text=f"1~80", size_hint=(None, None), size=(50, 30), pos=(std_x + 150, std_y), text = self.info[keys[1]])
        self.y_text_input = TextInput(hint_text=f"1~60", size_hint=(None, None), size=(50, 30), pos=(std_x + 150, std_y - 50), text = self.info[keys[2]])
        self.min_text_input = TextInput(hint_text=f"MIN", size_hint=(None, None), size=(50, 30), pos=(std_x + 490, std_y), text = self.info[keys[3]])        
        self.max_text_input = TextInput(hint_text=f"MAX", size_hint=(None, None), size=(50, 30), pos=(std_x + 490, std_y - 50), text = self.info[keys[4]])
        self.temp_tab_layout.add_widget(self.active_checkbox)
        self.temp_tab_layout.add_widget(self.x_text_input)
        self.temp_tab_layout.add_widget(self.y_text_input)
        self.temp_tab_layout.add_widget(self.min_text_input)
        self.temp_tab_layout.add_widget(self.max_text_input)
        

        if box == True:
            self.width_label = Label(text=f"WIDTH", size_hint=(None, None), size=(100, 30), pos=(std_x + 190, std_y)) 
            self.height_label = Label(text=f"HEIGHT", size_hint=(None, None), size=(100, 30), pos=(std_x + 190, std_y - 50))
            self.height_text_input = TextInput(hint_text=f"1~40", size_hint=(None, None), size=(50, 30), pos=(std_x + 280, std_y ), text = self.info[keys[6]])
            self.width_text_input = TextInput(hint_text=f"1~60", size_hint=(None, None), size=(50, 30), pos=(std_x + 280, std_y - 50), text = self.info[keys[5]])
            self.temp_tab_layout.add_widget(self.width_label)
            self.temp_tab_layout.add_widget(self.height_label)
            self.temp_tab_layout.add_widget(self.width_text_input)
            self.temp_tab_layout.add_widget(self.height_text_input)
        
        
        send_button = Button(
                text='SEND',
                font_size=15,
                size_hint=(None, None),
                size=(60, 60),
                pos=(std_x + 350, std_y - 40)
            )
        
        send_button.bind(
            on_release=lambda instance, 
                        tab_name = index,
                        active_text=self.active_checkbox, 
                        x_text=self.x_text_input,
                        y_text=self.y_text_input,
                        width_text=self.width_text_input, 
                        height_text=self.height_text_input:
                        self.send_coordi_callback(instance, tab_name, active_text, x_text, y_text, width_text, height_text))
        

        apply_button = Button(
                text='APPLY',
                font_size=15,
                size_hint=(None, None),
                size=(60, 60),
                pos=(std_x + 550, std_y - 40)
            )
        

        apply_button.bind(
                on_release=lambda instance, 
                            tab_name= index, 
                            max_temp=self.max_text_input, 
                            min_temp=self.min_text_input,:
                            self.send_temp_callback(instance, index, min_temp, max_temp))

        self.temp_tab_layout.add_widget(send_button)
        self.temp_tab_layout.add_widget(apply_button)
        print("Make Temp UI Complete")
        
    
    def send_coordi_callback(self, instance, tab_number, active_checkbox, x_text, y_text, width_text=None, height_text=None):
        active_value = 'true' if active_checkbox.active else 'false'
        try:
            x_value = x_text.text
            y_value = y_text.text
            width_value = width_text.text if width_text else ""
            height_value = height_text.text if height_text else ""
            if width_value and height_value:
                self.send_coordi_info(tab_number, active_value, x_value, y_value, width_value, height_value)
                print(f"{tab_number} - Active: {active_value}, X: {x_value}, Y: {y_value}, Width: {width_value}, Height: {height_value}")
            else:
                self.send_coordi_info(tab_number, active_value, x_value, y_value)
                print(f"{tab_number} - Active: {active_value}, X: {x_value}, Y: {y_value}")
        except ValueError:
            print('invalid value')
            logger.error('invalid value')
            


    def send_temp_callback(self, instance, tab_name, min_temp, max_temp):
        min_value = min_temp.text
        max_value = max_temp.text
        self.send_temp_info(tab_name, min_value, max_value)


    def send_temp_info(self, tab_name, min_value, max_value):
        if tab_name == 0:
            self.info['SPOT1_MIN'] = min_value
            self.info['SPOT1_MAX'] = max_value
            print(f"SPOT1_MIN = {min_value}")
            print(f"SPOT1_MAX = {max_value}")


        elif tab_name == 1:
            self.info['SPOT2_MIN'] = min_value
            self.info['SPOT2_MAX'] = max_value
            print(f"SPOT2_MIN = {min_value}")
            print(f"SPOT2_MAX = {max_value}")
        

        elif tab_name == 2:
            self.info['SPOT3_MIN'] = min_value
            self.info['SPOT3_MAX'] = max_value
            print(f"SPOT3_MIN = {min_value}")
            print(f"SPOT3_MAX = {max_value}")
        

        elif tab_name == 3:
            self.info['BOX1_MIN'] = min_value
            self.info['BOX1_MAX'] = max_value
            print(f"BOX1_MIN = {min_value}")
            print(f"BOX1_MAX = {max_value}")


        elif tab_name == 4:
            self.info['BOX2_MIN'] = min_value
            self.info['BOX2_MAX'] = max_value
            print(f"BOX2_MIN = {min_value}")
            print(f"BOX2_MAX = {max_value}")


        elif tab_name == 5:
            self.info['BOX3_MIN'] = min_value
            self.info['BOX3_MAX'] = max_value
            print(f"BOX3_MIN = {min_value}")
            print(f"BOX3_MAX = {max_value}")


        else:
            print("invalid TAB!")
            pass
        

    def send_coordi_info(self, tab_number, active_value, x_value, y_value, width_value = None, height_value= None):
        if tab_number == 0: # spot1
            active_url = self.api.make_url(self.rest_url['SPOT1_ACTIVE'], True, active_value) 
            result = self.api.set_camera_value(active_url) 
            self.info['SPOT1_ACTIVE'] = active_value

            X_url = self.api.make_url(self.rest_url['SPOT1_X'], True, x_value) 
            result = self.api.set_camera_value(X_url) 
            self.info['SPOT1_X'] = x_value

            Y_url = self.api.make_url(self.rest_url['SPOT1_Y'], True, y_value) 
            result = self.api.set_camera_value(Y_url) 
            self.info['SPOT1_Y'] = y_value

            if width_value and height_value:
                self.info ['SPOT1_W'] = width_value
                self.info ['SPOT1_h'] = height_value

        elif tab_number == 1: # spot2
            active_url = self.api.make_url(self.rest_url['SPOT2_ACTIVE'], True, active_value) 
            result = self.api.set_camera_value(active_url) 
            self.info['SPOT2_ACTIVE'] = active_value

            X_url = self.api.make_url(self.rest_url['SPOT2_X'], True, x_value) 
            result = self.api.set_camera_value(X_url) 
            self.info['SPOT2_X'] = x_value

            Y_url = self.api.make_url(self.rest_url['SPOT2_Y'], True, y_value) 
            result = self.api.set_camera_value(Y_url) 
            self.info['SPOT2_Y'] = y_value

            if width_value and height_value:
                self.info ['SPOT2_W'] = width_value
                self.info ['SPOT2_h'] = height_value

            
        elif tab_number == 2: # spot3
            active_url = self.api.make_url(self.rest_url['SPOT3_ACTIVE'], True, active_value) 
            result = self.api.set_camera_value(active_url) 
            self.info['SPOT3_ACTIVE'] = active_value

            X_url = self.api.make_url(self.rest_url['SPOT3_X'], True, x_value) 
            result = self.api.set_camera_value(X_url) 
            self.info['SPOT3_X'] = x_value

            Y_url = self.api.make_url(self.rest_url['SPOT3_Y'], True, y_value) 
            result = self.api.set_camera_value(Y_url) 
            self.info['SPOT3_Y'] = y_value

            if width_value and height_value:
                self.info ['SPOT3_W'] = width_value
                self.info ['SPOT3_h'] = height_value
            
        elif tab_number == 3: # box1
            active_url = self.api.make_url(self.rest_url['BOX1_ACTIVE'], True, active_value) 
            result = self.api.set_camera_value(active_url) 
            self.info['BOX1_ACTIVE'] = active_value

            X_url = self.api.make_url(self.rest_url['BOX1_X'], True, x_value) 
            result = self.api.set_camera_value(X_url) 
            self.info['BOX1_X'] = x_value

            Y_url = self.api.make_url(self.rest_url['BOX1_Y'], True, y_value) 
            result = self.api.set_camera_value(Y_url) 
            self.info['BOX1_Y'] = y_value
        
            if width_value and height_value:
                # width 
                width_url = self.api.make_url(self.rest_url['BOX1_W'], True, width_value) 
                result = self.api.set_camera_value(width_url) 
                self.info ['BOX1_W'] = width_value

                # height
                height_url = self.api.make_url(self.rest_url['BOX1_H'], True, height_value) 
                result = self.api.set_camera_value(height_url) 
                self.info ['BOX1_H'] = height_value
            
        elif tab_number == 4:
            active_url = self.api.make_url(self.rest_url['BOX2_ACTIVE'], True, active_value) 
            result = self.api.set_camera_value(active_url) 
            self.info['BOX2_ACTIVE'] = active_value

            X_url = self.api.make_url(self.rest_url['BOX2_X'], True, x_value) 
            result = self.api.set_camera_value(X_url) 
            self.info['BOX2_X'] = x_value

            Y_url = self.api.make_url(self.rest_url['BOX2_Y'], True, y_value) 
            result = self.api.set_camera_value(Y_url) 
            self.info['BOX2_Y'] = y_value
        
            if width_value and height_value:
                # width 
                width_url = self.api.make_url(self.rest_url['BOX2_W'], True, width_value) 
                result = self.api.set_camera_value(width_url) 
                self.info ['BOX2_W'] = width_value

                # height
                height_url = self.api.make_url(self.rest_url['BOX2_H'], True, height_value) 
                result = self.api.set_camera_value(height_url) 
                self.info ['BOX2_H'] = height_value

            
        elif tab_number == 5: # box3
            active_url = self.api.make_url(self.rest_url['BOX3_ACTIVE'], True, active_value) 
            result = self.api.set_camera_value(active_url) 
            self.info['BOX3_ACTIVE'] = active_value

            X_url = self.api.make_url(self.rest_url['BOX3_X'], True, x_value) 
            result = self.api.set_camera_value(X_url) 
            self.info['BOX3_X'] = x_value

            Y_url = self.api.make_url(self.rest_url['BOX3_Y'], True, y_value) 
            result = self.api.set_camera_value(Y_url) 
            self.info['BOX3_Y'] = y_value
        
            if width_value and height_value:
                # width 
                width_url = self.api.make_url(self.rest_url['BOX3_W'], True, width_value) 
                result = self.api.set_camera_value(width_url) 
                self.info ['BOX3_W'] = width_value

                # height
                height_url = self.api.make_url(self.rest_url['BOX3_H'], True, height_value) 
                result = self.api.set_camera_value(height_url) 
                self.info ['BOX3_H'] = height_value


#setting tab
#==========================================================================================
    def create_setting_tab(self):
        panel_pos = (310,5)
        self.std_x = panel_pos[0] + 20
        self.std_y = panel_pos[1] + 135

        setting_panel = TabbedPanel(size_hint=(None, None), size=(700, 300), pos = panel_pos, do_default_tab=False)
        setting_tab = TabbedPanelHeader(text='Palette')
        mode_tab = TabbedPanelHeader(text='Camera\nMode')
        led_tab = TabbedPanelHeader(text='LED')
        save_tab = TabbedPanelHeader(text='Save')
        overlay_tab = TabbedPanelHeader(text='Overlay')
        web_tab = TabbedPanelHeader(text='Open\nWebsite')
        global_tab = TabbedPanelHeader(text='Global\nParameter')

        setting_tab.content = self.create_setting_content('Palette')
        mode_tab.content = self.create_setting_content('Mode')
        led_tab.content = self.create_setting_content('LED')
        save_tab.content = self.create_setting_content('Save')
        overlay_tab.content = self.create_setting_content('Overlay')
        web_tab.content = self.create_setting_content('Website')
        global_tab.content = self.create_setting_content('Global_parameter')

        setting_panel.add_widget(setting_tab)
        setting_panel.add_widget(mode_tab)
        setting_panel.add_widget(led_tab)
        setting_panel.add_widget(save_tab)
        setting_panel.add_widget(overlay_tab)
        setting_panel.add_widget(web_tab)
        setting_panel.add_widget(global_tab)

        return setting_panel
    

    def create_setting_content(self, name):
        setting_tab_layout = FloatLayout(size=(600, 150))

        if name in 'Palette':
            self.arctic_button = Button(text="arctic",size=(80, 80),  
            size_hint = (None,None),
            pos=(self.std_x, self.std_y),
            color=(1, 1, 1, 1)
            )
            setting_tab_layout.add_widget(self.arctic_button)
            self.arctic_button.bind(on_press=self.palette_button_pressed)

            self.bw_button = Button(text="bw",size=(80, 80),  
            size_hint = (None,None),
            pos=(self.std_x + (80 * 1 + 10 * 1), self.std_y),
            color=(1, 1, 1, 1)
            )
            setting_tab_layout.add_widget(self.bw_button)
            self.bw_button.bind(on_press=self.palette_button_pressed)


            self.iron_button = Button(text="iron",size=(80, 80),  
            size_hint = (None,None),
            pos=(self.std_x + (80 * 2 + 10 * 2), self.std_y),
            color=(1, 1, 1, 1)
            )
            setting_tab_layout.add_widget(self.iron_button)
            self.iron_button.bind(on_press=self.palette_button_pressed)

            self.lava_button = Button(text="lava",size=(80, 80),  
            size_hint = (None,None),
            pos=(self.std_x + (80 * 3 + 10 * 3), self.std_y),
            color=(1, 1, 1, 1)
            )
            setting_tab_layout.add_widget(self.lava_button)
            self.lava_button.bind(on_press=self.palette_button_pressed)

            self.rainbow_button = Button(text="rainbow",size=(80, 80),  
            size_hint = (None,None),
            pos=(self.std_x + (80 * 4 + 10 * 4), self.std_y),
            color=(1, 1, 1, 1)
            )
            setting_tab_layout.add_widget(self.rainbow_button)
            self.rainbow_button.bind(on_press=self.palette_button_pressed)

            self.rainHC_button = Button(text="rainHC",size=(80, 80),  
            size_hint = (None,None),
            pos=(self.std_x + (80 * 5 + 10 * 5), self.std_y),
            color=(1, 1, 1, 1)
            )
            setting_tab_layout.add_widget(self.rainHC_button)
            self.rainHC_button.bind(on_press=self.palette_button_pressed)


        elif name in 'Mode':
            self.msx_button = Button(text="MSX",size=(80, 80),  
            size_hint = (None,None),
            pos=(self.std_x, self.std_y),
            color=(1, 1, 1, 1)
            )
            setting_tab_layout.add_widget(self.msx_button)

            self.Visual_button = Button(text="Visual",size=(80, 80),  
            size_hint = (None,None),
            pos=(self.std_x + (80 * 1 + 10 * 1), self.std_y),
            color=(1, 1, 1, 1)
            )
            setting_tab_layout.add_widget(self.Visual_button)

 
            self.Visual_button.bind(on_press = self.camera_mode_change)
            self.msx_button.bind(on_press = self.camera_mode_change)


        elif name in 'LED':
            self.led_on_button = Button(text="ON",size=(80, 80),  
            size_hint = (None,None),
            pos=(self.std_x, self.std_y),
            color=(1, 1, 1, 1)
            )
            setting_tab_layout.add_widget(self.led_on_button)

            self.led_off_button = Button(text="OFF",size=(80, 80),  
            size_hint = (None,None),
            pos=(self.std_x + (80 * 1 + 10 * 1), self.std_y),
            color=(1, 1, 1, 1)
            )
            setting_tab_layout.add_widget(self.led_off_button)
            self.led_on_button.bind(on_press = self.led_button_active)
            self.led_off_button.bind(on_press = self.led_button_active)


        elif name in 'Save':
            self.snapshot_button = Button(text="    Save\nSnapshot",size=(100, 80),  
            size_hint = (None,None),
            pos=(self.std_x, self.std_y),
            color=(1, 1, 1, 1)
            )
            setting_tab_layout.add_widget(self.snapshot_button)

            self.savedata_button = Button(text="      Save\nTemperature",size=(100, 80),  
            size_hint = (None,None),
            pos=(self.std_x + (100 * 1 + 10 * 1), self.std_y),
            color=(1, 1, 1, 1)
            )
            setting_tab_layout.add_widget(self.savedata_button)
            self.savedata_button.bind(on_release=self.save_data_popup)


        elif name in 'Overlay':
            self.overlay_on_button = Button(text="ON",size=(80, 80),  
            size_hint = (None,None),
            pos=(self.std_x, self.std_y),
            color=(1, 1, 1, 1)
            )
            setting_tab_layout.add_widget(self.overlay_on_button)

            self.overlay_off_button = Button(text="OFF",size=(80, 80),  
            size_hint = (None,None),
            pos=(self.std_x + (80 * 1 + 10 * 1), self.std_y),
            color=(1, 1, 1, 1)
            )
            setting_tab_layout.add_widget(self.overlay_off_button)

            self.overlay_on_button.bind(on_press = self.overlay_button_active)
            self.overlay_off_button.bind(on_press = self.overlay_button_active)


        elif name in 'Website':
            self.website_button = Button(text="Open Website",size=(200, 80),  
            size_hint = (None,None),
            pos=(self.std_x, self.std_y),
            color=(1, 1, 1, 1)
            )
            self.website_button.bind(on_release = self.open_internal_website)
            setting_tab_layout.add_widget(self.website_button)


        elif name in "Global_parameter":
            self.Emissivity = Label(text=f"Emissivity(%)", size_hint=(None, None), size=(150, 30), pos=(self.std_x + 30 , self.std_y + 80))
            self.RT = Label(text=f"Reflected temperature(C)", size_hint=(None, None), size=(150, 30), pos=(self.std_x + 30 , self.std_y + 30))
            self.RH = Label(text=f"Relative humidity(%)", size_hint=(None, None),size=(150, 30), pos=(self.std_x + 30 , self.std_y - 20))
            self.AT = Label(text=f"Atmospheric temperature(C)", size_hint=(None, None), size=(150, 30), pos=(self.std_x + 30 , self.std_y - 70))
            self.Distance = Label(text=f"Distance(M)", size_hint=(None, None), size=(150, 30), pos=(self.std_x + 310 , self.std_y + 80))
            self.EIR = Label(text=f"External IR window(On/Off)", size_hint=(None, None), size=(150, 30), pos=(self.std_x + 310 , self.std_y + 30))
            self.T = Label(text=f"Temperature(C)", size_hint=(None, None), size=(150, 30), pos=(self.std_x + 310 , self.std_y - 20))
            self.TM = Label(text=f"Transmission(%)", size_hint=(None, None), size=(150, 30), pos=(self.std_x + 310 , self.std_y - 70))

            self.Emissivity_text_input = TextInput(hint_text=f"%", size_hint=(None, None), size=(80, 30), pos=(self.std_x + 205 , self.std_y + 80), text = self.info['GLOBAL_EMISS'])
            self.RT_text_input = TextInput(hint_text=f"C", size_hint=(None, None), size=(80, 30), pos=(self.std_x + 205 , self.std_y + 30), text = self.info['GLOBAL_RT'])
            self.RH_text_input = TextInput(hint_text=f"%", size_hint=(None, None), size=(80, 30), pos=(self.std_x + 205 , self.std_y - 20), text = self.info['GLOBAL_RH'])
            self.AT_text_input = TextInput(hint_text=f"C", size_hint=(None, None), size=(80, 30), pos=(self.std_x + 205 , self.std_y - 70), text = self.info['GLOBAL_AT'])
            self.Distance_text_input = TextInput(hint_text=f"m", size_hint=(None, None), size=(80, 30), pos=(self.std_x + 480 , self.std_y + 80), text = self.info['GLOBAL_OD'])
            self.EIR_text_input = TextInput(hint_text=f"on/off", size_hint=(None, None), size=(80, 30), pos=(self.std_x + 480 , self.std_y + 30), text = self.info['GLOBAL_EIRW'])
            self.T_text_input = TextInput(hint_text=f"C", size_hint=(None, None), size=(80, 30), pos=(self.std_x + 480 , self.std_y - 20), text = self.info['GLOBAL_TEMP'])
            self.TM_text_input = TextInput(hint_text=f"%", size_hint=(None, None), size=(80, 30), pos=(self.std_x + 480 , self.std_y - 70), text = self.info['GLOBAL_TRS'])
            
            setting_tab_layout.add_widget(self.Emissivity)
            setting_tab_layout.add_widget(self.RT)
            setting_tab_layout.add_widget(self.RH)
            setting_tab_layout.add_widget(self.AT)
            setting_tab_layout.add_widget(self.Distance)
            setting_tab_layout.add_widget(self.EIR)
            setting_tab_layout.add_widget(self.T)
            setting_tab_layout.add_widget(self.TM)

            self.global_button = Button(text="SEND",size=(80, 80),  
                                        size_hint = (None,None),
                                        pos=(self.std_x + 590 , self.std_y - 80),
                                        color=(1, 1, 1, 1)
                                        )

            self.global_button.bind(
            on_release=lambda instance, 
                        Emissivity = self.Emissivity_text_input.text,
                        RT=self.RT_text_input.text, 
                        RH=self.RH_text_input.text,
                        AT=self.AT_text_input.text,
                        Distance=self.Distance_text_input.text, 
                        EIR=self.EIR_text_input.text,
                        T = self.T_text_input.text,
                        TM = self.TM_text_input.text:
                        self.send_global_callback(instance, Emissivity, RT, RH, AT, Distance, EIR, T, TM))
            

            setting_tab_layout.add_widget(self.Emissivity_text_input)
            setting_tab_layout.add_widget(self.RT_text_input)
            setting_tab_layout.add_widget(self.RH_text_input)
            setting_tab_layout.add_widget(self.AT_text_input)
            setting_tab_layout.add_widget(self.Distance_text_input)
            setting_tab_layout.add_widget(self.EIR_text_input)
            setting_tab_layout.add_widget(self.T_text_input)
            setting_tab_layout.add_widget(self.TM_text_input)
            setting_tab_layout.add_widget(self.global_button)
            
            
        else:
            print("invalid name")
        print("Make Setting Tab Complete")
        logger.info("Make Setting Tab Complete")

        return setting_tab_layout


    def send_global_callback(self, instance, Emissivity, RT, RH, AT, Distance, EIR, T, TM):
        Emissivity_url = self.api.make_url(self.rest_url['GLOBAL_EMISS'], True, Emissivity) 
        result = self.api.set_camera_value(Emissivity_url) 
        if result:
            self.info['GLOBAL_EMISS'] = Emissivity

        RT_url = self.api.make_url(self.rest_url['GLOBAL_RT'], True, RT) 
        result = self.api.set_camera_value(RT_url) 

        if result:
            self.info['GLOBAL_RT'] = RT
        else:
            print(f"Send GLOBAL_RT Error")
            logger.error(f"Send GLOBAL_RT Error")
        
        
        RH_url = self.api.make_url(self.rest_url['GLOBAL_RH'], True, RH) 
        result = self.api.set_camera_value(RH_url) 

        if result:
            self.info['GLOBAL_RH'] = RH
        else:
            print(f"Send GLOBAL_RH Error")
            logger.error(f"Send GLOBAL_RH Error")


        AT_url = self.api.make_url(self.rest_url['GLOBAL_AT'], True, AT) 
        result = self.api.set_camera_value(AT_url)

        if result:
            self.info['GLOBAL_AT'] = AT
        else:
            print(f"Send GLOBAL_AT Error")
            logger.error(f"Send GLOBAL_AT Error")


        
        OD_url = self.api.make_url(self.rest_url['GLOBAL_OD'], True, Distance) 
        result = self.api.set_camera_value(OD_url) 

        if result:
            self.info['GLOBAL_OD'] = Distance
            
        else:
            print(f"Send GLOBAL_OD Error")
            logger.error(f"Send GLOBAL_OD Error")



        EIR_url = self.api.make_url(self.rest_url['GLOBAL_EIRW'], True, EIR) 
        result = self.api.set_camera_value(EIR_url) 

        if result:
            self.info['GLOBAL_EIRW'] = EIR

        else:
            print(f"Send GLOBAL_EIRW Error")
            logger.error(f"Send GLOBAL_EIRW Error")

        
        T_url = self.api.make_url(self.rest_url['GLOBAL_TEMP'], True, T) 
        result = self.api.set_camera_value(T_url) 

        if result:
            self.info['GLOBAL_TEMP'] = T

        else:
            print(f"Send GLOBAL_TEMP Error")
            logger.error(f"Send GLOBAL_TEMP Error")


        TM_url = self.api.make_url(self.rest_url['GLOBAL_TRS'], True, TM) 
        result = self.api.set_camera_value(TM_url) 

        if result:
            self.info['GLOBAL_TRS'] = TM
        else:
            print(f"Send GLOBAL_TRS Error")
            logger.error(f"Send GLOBAL_TRS Error")


        return

        






    def palette_button_pressed(self, instance):
        try:
            name = instance.text
            URL = self.api.make_url(['image','sysimg','palette','readFile'], True, name)
            rst = self.api.set_camera_value(URL)
            print(f"Change Palette : {name}")
            logger.info(f"Change Palette : {name}")
        except Exception as e:
            print(f"change palette Error : {e}")
            logger.error(f"change palette Error : {e}")
        
    def save_data_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical')
        self.save_toggle_group = []
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
        self.start_button = Button(text='Start')

        if self.data_toggle_lock:
            self.start_button.disabled = True
        
        stop_button = Button(text='Stop')
        
        self.start_button.bind(on_press=self.start_button_pressed)
        stop_button.bind(on_press=self.stop_button_pressed)

        # 레이아웃에 시작 버튼과 중지 버튼 추가
        popup_layout.add_widget(self.start_button)
        popup_layout.add_widget(stop_button)

        # 팝업 생성
        popup = Popup(title="Temperature Data Save", content=popup_layout, size_hint=(None, None), size=(400, 400))
        popup.open()
    
    # date write func
    def start_button_pressed(self, instance):

        self.start_time = time.time()
        self.data_selected = [btn.text for btn in self.save_toggle_group if btn.state == 'down']
        for toggle_button in self.save_toggle_group:
                toggle_button.disabled = True
                self.data_toggle_lock = True
        self.start_button.disabled = True
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
        self.data_write = True
        print(f"temperature save start // interval {self.interval}")
        logger.info(f"temperature save start // interval {self.interval}")

    # data write stop
    def stop_button_pressed(self, instance):
        for toggle_button in self.save_toggle_group:
                toggle_button.disabled = False
                self.data_toggle_lock = False
        self.start_button.disabled = False
        self.save_trigger = True
        

        print("temperature save start")
        logger.info("temperature save start")


    # etc func
            
    def open_internal_website(self, instance):
        internal_ip_address = self.ip
        if not internal_ip_address.startswith('http://') and not internal_ip_address.startswith('https://'):
            internal_ip_address = 'http://' + internal_ip_address
        print(f"open website : {internal_ip_address}")
        logger.info(f"open website : {internal_ip_address}")
        webbrowser.open(internal_ip_address)
    
    
    def camera_mode_change(self,instance):
        try:
            value = instance.text
            mode = 0
            data_list = ['image','sysimg','fusion','fusionData','fusionMode']
            if value == "IR":
                mode = '1'
            elif value == "Visual":
                mode = '2'
            elif value == "MSX":
                mode = '3'
            else:
                pass
            URL = self.api.make_url(data_list, True, mode)
            rst = self.api.set_camera_value(URL)
            print(f"change {self.selected_mode} Mode Complete{rst}")
            logger.info(f"change {self.selected_mode} Mode Complete{rst}")
        except Exception as e:
            print(f"Cam Mode Change Error = {traceback.format_exc()}")
            logger.error(f"Cam Mode Change Error = {traceback.format_exc()}")


    def led_button_active(self, instance):
        if self.info['LED'] == 'false':
            self.info['LED'] = 'true'
            instance.text = "ON"
            # instance.color = (1, 0, 0, 1)
            URL = self.api.make_url(['system','vcam','torch'], True, 'true')
            rst = self.api.set_camera_value(URL)
            print(f"CAM LED ON")
            logger.info(f"CAM LED ON")
    
        else:
            instance.text = "OFF"
            self.info['LED'] = 'false'
            instance.color = (1, 1, 1, 1)
            URL = self.api.make_url(['system','vcam','torch'], True, 'false')
            rst = self.api.set_camera_value(URL)
            print(f"CAM LED OFF")
            logger.info(f"CAM LED OFF")
        

    # hideGraphics = true -> 숨김 / false가 overlay On
    def overlay_button_active(self, instance):
        if instance.text == "ON":
            for i in range(3):
                URL = self.api.make_url(['resmon','config','hideGraphics'], True, 'false')
                rst = self.api.set_camera_value(URL)
                time.sleep(0.01)
            print(f"CAM Overlay ON")
            logger.info(f"CAM Overlay ON")
        else:
            for i in range(3):
                URL = self.api.make_url(['resmon','config','hideGraphics'], True, 'true')
                rst = self.api.set_camera_value(URL)
                time.sleep(0.01)
            print(f"CAM Overlay OFF")
            logger.info(f"CAM Overlay OFF")

