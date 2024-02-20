import os
import time
import traceback
import matplotlib
import pandas as pd
matplotlib.use('Agg')
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt





class TempMonitor():
    def __init__(self, API, UI):
        self.API = API
        self.ip = API.ip
        self.info = API.INFO
        self.UI = UI
        self.tabs = self.UI.tabs
        self.active_list = None
        self.data_list = []
        self.url_dic = {
                        0:[f'http://{self.ip}/prod/res/image/sysimg/measureFuncs/spot/1/valueT'], 
                        1: [f'http://{self.ip}/prod/res/image/sysimg/measureFuncs/spot/2/valueT'],
                        2: [f'http://{self.ip}/prod/res/image/sysimg/measureFuncs/spot/3/valueT'],
                        3: [
                            f"http://{self.ip}/prod/res/image/sysimg/measureFuncs/mbox/1/maxT",
                            f"http://{self.ip}/prod/res/image/sysimg/measureFuncs/mbox/1/minT"
                            ],
                        4: [
                            f"http://{self.ip}/prod/res/image/sysimg/measureFuncs/mbox/2/maxT",
                            f"http://{self.ip}/prod/res/image/sysimg/measureFuncs/mbox/2/minT"
                            ],
                        5: [
                            f"http://{self.ip}/prod/res/image/sysimg/measureFuncs/mbox/3/maxT",
                            f"http://{self.ip}/prod/res/image/sysimg/measureFuncs/mbox/3/minT"
                            ],
                        }
        self.box1_result = [None, None]
        self.box2_result = [None, None]
        self.box3_result = [None, None]
        self.save_temperature_data = {}

    def key_filter(self, data, target):
        result = []
        for key, value in data.items():
            if target in key:
                result.append(value)
        return result

    def get_temperature(self, urls):
        for url in urls:
            pass
    
    def temp_alarm(self, category, number, temperature, min_max = None ):
        print(f"temperature = {temperature}")
        if  category == "spot":
            if number == "1":
                if temperature > int(self.info['SPOT1_MIN']) and temperature < int(self.info['SPOT1_MAX']):
                    self.change_tab_text_color(0, "OK")
                else:
                    self.change_tab_text_color(0, "NG")

            elif number == "2":
                if temperature > int(self.info['SPOT2_MIN']) and temperature < int(self.info['SPOT2_MAX']):
                    self.change_tab_text_color(1, "OK")
                else:
                    self.change_tab_text_color(1, "NG")
                    
            elif number == "3":
                if temperature > int(self.info['SPOT3_MIN']) and temperature < int(self.info['SPOT3_MAX']):
                    self.change_tab_text_color(2, "OK")
                else:
                    self.change_tab_text_color(2, "NG")
            else:
                print("invalid number")
        
        if  category == "mbox": 
            if number == '1':
                if min_max == "maxT":
                    if temperature <= int(self.info['BOX1_MAX']):  
                        self.box1_result[0] = 'OK'
                    else:
                        self.box1_result[0] = 'NG'
                if min_max == "minT":
                    if temperature >= int(self.info['BOX1_MIN']):
                        self.box1_result[1] = 'OK'
                    else:
                        self.box1_result[1] = 'NG'
                if all(self.box1_result):
                    self.change_tab_text_color(3, self.box1_result)
                    self.box1_result = [None, None]
                    
            elif number == '2':
                if min_max == "maxT":
                    if temperature <= int(self.info['BOX2_MAX']):  
                        self.box2_result[0] = 'OK'
                    else:
                        self.box2_result[0] = 'NG'
                if min_max == "minT":
                    if temperature >= int(self.info['BOX2_MIN']):
                        self.box2_result[1] = 'OK'
                    else:
                        self.box2_result[1] = 'NG'
                if all(self.box2_result):
                    self.change_tab_text_color(4, self.box2_result)
                    self.box2_result = [None, None]
                    
            elif number == '3':
                if min_max == "maxT":
                    if temperature <= int(self.info['BOX3_MAX']):  
                        self.box3_result[0] = 'OK'
                    else:
                        self.box3_result[0] = 'NG'
                if min_max == "minT":
                    if temperature >= int(self.info['BOX3_MIN']):
                        self.box3_result[1] = 'OK'
                    else:
                        self.box3_result[1] = 'NG'
                if all(self.box3_result):
                    self.change_tab_text_color(5, self.box3_result)
                    self.box3_result = [None, None]


    def temp_thread(self):
        temp_log = []

        while True:
            try:
                self.active_list = self.key_filter(self.info, 'ACTIVE')
                print(f"active_list = {self.active_list}")
                if not any(self.active_list):
                    time.sleep(1)
                    continue
                now = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                temp_log.append(now)
                try:
                    for idx, active in enumerate(self.active_list):
                        if active == "true":
                            for url in self.url_dic[idx]:
                                res = url.split('/')
                                category = res[-3]
                                number = res[-2]
                                min_max = res[-1]
                                if float(self.API.get_camera_value(url)) == None:
                                    continue
                                temperature = float(self.API.get_camera_value(url))
                                calvin_value = round(temperature - 273.15, 2)
                                self.temp_alarm(category, number, calvin_value, min_max)
                                temp_log.append(calvin_value)
                    
                        else:
                            self.change_tab_text_color(idx, "OK")
                        time.sleep(0.01)
                 	 
                except Exception as e:
                    print(f"Get Temp Value Error : {traceback.format_exc()}")
                    continue
                time.sleep(1)

                if self.UI.data_write:
                    self.data_list.append(temp_log)
                    print(self.UI.data_selected)
                    current_time = time.time()
                    print(f'1 : {current_time - self.UI.start_time}')
                    print(f"2 : {self.UI.interval}")
                    print(f"3 : {current_time - self.UI.start_time >= self.UI.interval}")
                    if current_time - self.UI.start_time >= self.UI.interval:
                        self.temperature_to_csv(self.active_list, self.data_list)
                        self.data_list = []
                        self.UI.start_time = time.time()
                        
                temp_log = []
                if self.UI.save_trigger == True:
                    self.UI.data_write = False
                    print(f"data_list check  = {self.data_list}")
                    self.data_list = []
                    self.UI.save_trigger = False
                
                time.sleep(0.01)

            except Exception as e:
                print(f"Temp Thread Exception {traceback.format_exc()}")

        
    def data_collect(self, category, number,  min_max, calvin_value):
        save_name = f"{category}_{number}"
        if min_max != None:
            save_name = f"{save_name}_{min_max}"
        self.save_temperature_data[save_name] = calvin_value
        
    def temperature_to_csv(self, active_list, data):
        columns = self.make_header(active_list)
        file_path = self.make_filepath()
        df = pd.DataFrame(data, columns=columns)
        df.to_csv(f'{file_path}', index=False, columns=columns)

    def make_filepath(self):
        file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        folder_path = f'./save_temperature'
        print(f"{folder_path}{file_name}")
        os.makedirs(folder_path, exist_ok=True)
        file_path = f"{folder_path}/{file_name}"
        return file_path

    def make_header(self, active_list):
        columns = ['TIME']
        for idx, value in enumerate(active_list):
            if idx == 0 and value == 'true':
                columns.append('SPOT1')
            if idx == 1 and value == 'true':
                columns.append('SPOT2')
            if idx == 2 and value == 'true':
                columns.append('SPOT3')
            if idx == 3 and value == 'true':
                columns.append('BOX1_MAX')
                columns.append('BOX1_MIN')
            if idx == 4 and value == 'true':
                columns.append('BOX2_MAX')
                columns.append('BOX2_MIN')
            if idx == 5 and value == 'true':
                columns.append('BOX3_MAX')
                columns.append('BOX3_MIN')
        return columns
        
    def change_tab_text_color(self, tab_index, result):
        # OK => white // NG => red
        color = (1, 1, 1, 1) 
        if "NG" in result:
            color = (1, 0, 0, 1) # red
        else:
            color = (1, 1, 1, 1) # white
        if 0 <= tab_index <= len(self.tabs):
            tab = self.tabs[tab_index]  
            tab.color = color

class SaveTempData():
    def __init__(self):
        pass

    def DataToCSV(self, data):
        file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        folder_path = f'./save/'
        print(f"{folder_path}{file_name}")
        os.makedirs(folder_path, exist_ok=True)
        file_path = f"{folder_path}{file_name}"
        df = pd.DataFrame(data, columns=['TIME', 'SPOT1', 'SPOT2', 'SPOT3', 'BOX1_MAX', 'BOX1_MIN', 'BOX2_MAX', 'BOX2_MIN', 'BOX3_MAX', 'BOX3_MIN'])

        # 엑셀 헤더 추가
        header = ['TIME'] + [col for col in df.columns if col != 'TIME']

        # 데이터프레임을 CSV 파일로 저장
        df.to_csv(f'{file_path}', index=False, columns=header)
