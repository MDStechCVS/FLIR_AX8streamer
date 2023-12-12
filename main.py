import logging
import os
import traceback
import tkinter as tk
from  UTIL.Video import VideoUtilsClass
from  UTIL.Temp_Log import SaveTempData
from UTIL.Config_Util import ConfigManager
from tkinter import messagebox
from queue import Queue
import cv2
from PIL import Image, ImageTk
from tkinter import ttk
import threading
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime




class MainWindow(tk.Frame):
    def __init__(self, master=None, ):
        super().__init__(master)
        self.master = master
        self.configure(bg=bg_color)  
        
        # 이미지 업데이트 윈도우 
        self.image_canvas = None
        
        # img_show함수 관련 변수
        self.cvtimg = None
        self.cvtshow = None
        self.updateImage = None
        self.back_cam = None
        self.updateImage_backup = None
        self.bufferImage = None
        
        # tk label variable
        self.label_s1 = None
        self.label_s2 = None
        self.label_s3 = None
        self.label_b1 = None
        self.label_b2 = None
        self.label_b3 = None
        
        # Box, Spot Activate
        self.active_value = [False, False, False, False, False, False]
        self.active_data = []
        
        
        #Ini config   
        self.CONFIG = ConfigManager()
        self.ini_dic = self.CONFIG.InitValueToCamera()
        self.main_ip = self.ini_dic['CAMERA']['ip']
        self.main_dic = self.CONFIG.dict_to_camera        
        
        # Text SERIAL / PORT
        self.text_ipinfo = "SERIAL / PORT"
        
        
        # widget init
        self.CreateWidgets()
        self.image_canvas = self.main_canvas.create_image(10, 20, image = '', anchor = 'nw')
        self.back_cam = self.main_canvas.create_image(10, 20, image = '', anchor = 'nw')
        
        # csv file variable
        self.file_save_active = False
        self.file_save_trigger = False
        self.interval = 60

        

        

    #=======================================================================================================================================    
    # Create widgets 
    def CreateWidgets(self):
        self.main_canvas = tk.Canvas(self, width=900, height=600, bg=bg_color) 
        self.main_canvas.grid(row=0, column=0)  
        self.main_canvas.pack(fill=tk.BOTH, expand=True)
        self.radio_value = tk.StringVar(value=' ')
        
        # Spot, Box Radio button
        for i in range(1, 4):
            spot_rb = tk.Radiobutton(self, text=f"SPOT_{i}", variable=self.radio_value, value=f"SPOT_{i}", bg = "#04001f", fg="white", font=("Arial", 10, "bold"), selectcolor="black")
            spot_rb.place(x=653, y= i * 25 - 5 )
            
        # BOX 라디오버튼 생성
            box_rb = tk.Radiobutton(self, text=f"BOX_{i}", variable=self.radio_value, value=f"BOX_{i}", bg = "#04001f", fg="white", font=("Arial", 10, "bold"), selectcolor="black")
            box_rb.place(x=750, y= i * 25 - 5)

        # Mouse Coordi Event
        self.event_x = tk.Label(root, text="X", fg="white", bg="#04001f", font=("Arial", 15, "bold"))
        self.event_x.place(x = 40, y = 520)

        self.event_y = tk.Label(root, text="Y", fg="white", bg="#04001f", font=("Arial", 15, "bold"))
        self.event_y.place(x = 40, y = 550)


        # Label
        self.label_s1 = tk.Label(root, text="SPOT_1", fg="white", bg="#04001f", font=("Arial", 15, "bold"))
        self.label_s1.place(x = 660, y = 190)
        
        self.label_s2 = tk.Label(root, text="SPOT_2", fg="white", bg="#04001f", font=("Arial", 15, "bold"))
        self.label_s2.place(x = 660, y = 220)
        
        self.label_s3 = tk.Label(root, text="SPOT_3", fg="white", bg="#04001f", font=("Arial", 15, "bold"))
        self.label_s3.place(x = 660, y = 250)
        
        self.label_b1 = tk.Label(root, text="BOX_1", fg="white", bg="#04001f", font=("Arial", 15, "bold"))
        self.label_b1.place(x = 660, y = 280)
        
        self.label_b2 = tk.Label(root, text="BOX_2", fg="white", bg="#04001f", font=("Arial", 15, "bold"))
        self.label_b2.place(x = 660, y = 310)
        
        self.label_b3 = tk.Label(root, text="BOX_3", fg="white", bg="#04001f", font=("Arial", 15, "bold"))
        self.label_b3.place(x = 660, y = 340)

        self.show_active()
        
        # Button
        self.edit_btn = tk.Button(self, text="edit", command=self.SettingFrame, width=5, height=2,
                                    bg="#ff7f00", fg="white", font=("Arial", 14, "bold"))
        self.edit_btn.place(x=653, y=100) 


        self.savebutton = tk.Button(root, text="선택", command=self.save_activate, width=5, height=2,
                                    bg="#ff7f00", fg="white", font=("Arial", 14, "bold"))
        self.savebutton.place(x=653, y=440)  

        self.temp_save_start = tk.Button(root, text="Start", command=self.get_save_cycle, width=5, height=2,
                                    bg="#ff7f00", fg="white", font=("Arial", 14, "bold"))
        self.temp_save_start.place(x=730, y=440)  

        # Combobox
        self.save_excel_combobox = ttk.Combobox(root, values=["30초", "1분", "5분", "10분"],  state='normal', width = 8)
        self.save_excel_combobox.set("1분")
        self.save_excel_combobox.place(x=653, y=415)

        # Packing
        self.main_canvas.bind('<Button-1>', self.main_btn)
        self.main_canvas.pack()
        
    # Save Time Control
    def get_save_cycle(self):
        print("Save Start")
        self.file_save_trigger = not self.file_save_trigger
        selected_value = self.save_excel_combobox.current()
        if selected_value == 0:
            self.interval = 30
        elif selected_value == 1:
            self.interval = 60
        elif selected_value == 2:
            self.interval = 300
        elif selected_value == 3:
            self.interval = 600
        else:
            pass

    # Save Button to Combobox   normal / disabled
    def save_activate(self):
        if str(self.save_excel_combobox['state']) == 'normal':
            self.save_excel_combobox['state'] = 'disabled'
            self.file_save_active = True
            self.savebutton.config(text="Cancel")
        else:
            self.save_excel_combobox['state'] = 'normal'
            self.file_save_active = False
            self.file_save_trigger = False
            GT.data_box = []
            self.savebutton.config(text="선택")

    # Mouse Event Func
    def main_btn(self, event):
        x = event.x
        y = event.y
        # print(f'x = {x} y = {y}')
        if 800< x < 900 and 500 < y < 600:
            print(self.main_dic)

        if 10 < x < 650 and 20 < y < 500:
             self.event_x.config(text=f"X : { int(((x - 10) * (800 / 640)) / 10) }")
             self.event_y.config(text=f"Y : { int(((y - 20) * (600 / 480)) / 10)  +1 }")

    # label color change 
    def change_color(self, label, color):
        if color == 0:
            label.config(fg="white")
        if color == 1:
            label.config(fg="green")
        if color == 2:
            label.config(fg="red")
        
        return

    # Init label Color
    def show_active(self):
        self.active_data = {key: value['active'] for key, value in self.main_dic.items() if 'active' in value}
        for key, value in self.active_data.items():
            if value == "true":
                if key == "SPOT_1":
                    self.change_color(self.label_s1, 1)
                    self.active_value[0] = True
                if key == "SPOT_2":
                    self.change_color(self.label_s2, 1)
                    self.active_value[1] = True
                if key == "SPOT_3":
                    self.change_color(self.label_s3, 1)
                    self.active_value[2] = True
                if key == "BOX_1":
                    self.change_color(self.label_b1, 1)
                    self.active_value[3] = True
                if key == "BOX_2":
                    self.change_color(self.label_b2, 1)
                    self.active_value[4] = True
                if key == "BOX_3":
                    self.change_color(self.label_b3, 1)
                    self.active_value[5] = True
            else:
                if key == "SPOT_1":
                    self.change_color(self.label_s1, 0)
                    self.active_value[0] = False
                if key == "SPOT_2":
                    self.change_color(self.label_s2, 0)
                    self.active_value[1] = False
                if key == "SPOT_3":
                    self.change_color(self.label_s3, 0)
                    self.active_value[2] = False
                if key == "BOX_1":
                    self.change_color(self.label_b1, 0)
                    self.active_value[3] = False
                if key == "BOX_2":
                    self.change_color(self.label_b2, 0)
                    self.active_value[4] = False
                if key == "BOX_3":
                    self.change_color(self.label_b3, 0)
                    self.active_value[5] = False
                
                


    # Setting Frame 
    def SettingFrame(self):
        # 현재 선택된 라디오 버튼의 값을 가져와서 사용
        selected_value = self.radio_value.get()
        new_window = tk.Toplevel(self)
        new_window.title(f"{selected_value} Setting Winodw")
        new_window.geometry("600x400")
        new_window.configure(bg="#04001f")
        print(f"selected : {selected_value}")
        
        # 탑레벨 창에 대한 새로운 StringVar 생성
        self.SettingWindowWidget(new_window, selected_value)
        
        
    # Setting Widget Create        
    def SettingWindowWidget(self, new_window, selected_value):
        self.top_radio_value = tk.StringVar()
        info_label = tk.Label(new_window, text="좌표\n X = 0 ~ 79\n Y = 0 ~ 59", fg="white", bg="#04001f", font=("Arial", 12, "bold"))
        info_label.place(x = 20, y = 330)

        Active_rb = tk.Radiobutton(new_window, text="Active", variable=self.top_radio_value, value="true", bg="#04001f", fg="white", font=('gothic', 13, 'bold'), selectcolor="#04001f")
        Active_rb.place(x = 30, y = 40)
        
        Inactive_rb = tk.Radiobutton(new_window, text="Inactive", variable=self.top_radio_value, value="false", bg="#04001f", fg="white", font=('gothic', 13, 'bold'), selectcolor="#04001f")
        Inactive_rb.place(x = 30, y = 70)
        
        self.top_radio_value.set(self.main_dic[selected_value]['active'])


        if "SPOT" in selected_value:
            # SPOT인 경우 X, Y 좌표 입력받을 수 있는 박스
            tk.Label(new_window, text="X", fg="white", bg="#04001f", font=('gothic', 13, 'bold')).place(x = 200, y=40)
            self.x_entry = tk.Entry(new_window)
            self.x_entry.place(x = 200, y= 70)
            self.x_entry.insert(0, f"{self.main_dic[selected_value]['x']}")
            

            tk.Label(new_window, text="Y", fg="white", bg="#04001f", font=('gothic', 13, 'bold')).place(x = 200, y= 100)
            self.y_entry = tk.Entry(new_window)
            self.y_entry.place(x = 200, y= 130)
            self.y_entry.insert(0, f"{self.main_dic[selected_value]['y']}")
            

        elif "BOX" in selected_value:
            # BOX인 경우 START_X, START_Y, WIDTH, HEIGHT 입력받을 수 있는 박스
            tk.Label(new_window, text="START_X", fg="white", bg="#04001f", font=('gothic', 13, 'bold')).place(x = 200, y= 40)
            self.x_entry = tk.Entry(new_window)
            self.x_entry.place(x = 200, y = 70)
            self.x_entry.insert(0, f"{self.main_dic[selected_value]['x']}")
            

            tk.Label(new_window, text="START_Y", fg="white", bg="#04001f", font=('gothic', 13, 'bold')).place(x = 200, y = 100)
            self.y_entry = tk.Entry(new_window)
            self.y_entry.place(x = 200, y = 130)
            self.y_entry.insert(0, f"{self.main_dic[selected_value]['y']}")
            

            tk.Label(new_window, text="WIDTH", fg="white", bg="#04001f", font=('gothic', 13, 'bold')).place(x = 200, y = 160)
            self.width_entry = tk.Entry(new_window)
            self.width_entry.place(x = 200, y = 190)
            self.width_entry.insert(0, f"{self.main_dic[selected_value]['width']}")
            
            tk.Label(new_window, text="HEIGHT", fg="white", bg="#04001f", font=('gothic', 13, 'bold')).place(x = 200, y = 220)
            self.height_entry = tk.Entry(new_window)
            self.height_entry.place(x = 200, y = 250)
            self.height_entry.insert(0, f"{self.main_dic[selected_value]['height']}")
            
        else:
            print("selected_value check")
        
        
        tk.Label(new_window, text="Minimum Temp", fg="white", bg="#04001f", font=('gothic', 13, 'bold')).place(x = 400, y = 40)
        self.low_temp_entry = tk.Entry(new_window)
        self.low_temp_entry.place(x = 400, y = 70)
        self.low_temp_entry.insert(0, f"{self.main_dic[selected_value]['min']}")
        
        
        tk.Label(new_window, text="Maximum Temp", fg="white", bg="#04001f", font=('gothic', 13, 'bold')).place(x = 400, y = 100)
        self.high_temp_entry = tk.Entry(new_window)
        self.high_temp_entry.place(x = 400, y = 130)
        self.high_temp_entry.insert(0, f"{self.main_dic[selected_value]['max']}")
        
        
        save_b = tk.Button(new_window, text="Save", command = lambda: self.save_data(selected_value), fg="black", bg="#ff7f00", font=('gothic', 13, 'bold'), width = 5, height=2)
        save_b.place(x = 450, y = 330)

        
        Cancel_b = tk.Button(new_window, text="Cancel", command=lambda: self.close_toplevel(new_window), fg="black", bg="#ff7f00", font=('gothic', 13, 'bold'), width = 5, height=2)
        Cancel_b.place(x = 520, y = 330)
        
        
    # Setting Window Save Data Button
    def save_data(self, selected_value):
        result = {
            'active': self.top_radio_value.get().lower()
        }
        
        if "SPOT" in selected_value:
            result.update({
                'x': self.x_entry.get(),
                'y': self.y_entry.get()
            })
        elif "BOX" in selected_value:
            result.update({
                'x': self.x_entry.get(),
                'y': self.y_entry.get(),
                'width':  self.width_entry.get(),
                'height': self.height_entry.get()
            })
        result.update({
            'min': self.low_temp_entry.get(),
            'max': self.high_temp_entry.get()
            })
        self.main_dic = self.CONFIG.change_setting_value(selected_value, result) 


    # Close Setting Window
    def close_toplevel(self, new_window):
        new_window.destroy()
    
    
    # Main Window Image Update 
    def show_img(self, img):
        # updateImg = cv2.resize(img, dsize = (600, 400))
        self.cvtimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        self.cvtshow = Image.fromarray(self.cvtimg)
        self.updateImage = ImageTk.PhotoImage(image=self.cvtshow)
        self.main_canvas.itemconfig(self.image_canvas, image = self.updateImage)
        self.updateImage_backup = ImageTk.PhotoImage(image=self.cvtshow)
        self.main_canvas.itemconfig(self.back_cam, image = self.updateImage_backup)


    def proc_active(self):
        true_indices = [i for i, value in enumerate(self.active_value) if value]
        print(true_indices)
            
            
# Temp Value Monitor Class         
class TempMonitor():
    def __init__(self):
        self.STD = SaveTempData()
        self.save_list = []
        self.save_time = []
        self.data_box = []
        
    

    def TempFromCamera(self, urls):
        save_value = {"TIME" : None, "SPOT1" : None , "SPOT2" : None, "SPOT2" : None, "SPOT3" : None, "BOX1_MAX" : None, "BOX1_MIN" : None,"BOX2_MAX" : None,"BOX2_MIN" : None,"BOX3_MAX" : None,"BOX3_MIN" : None}
        result_list = []
        
        
        # URL로 모든 spot과 box temp 값 요청
        for url in urls:
            response = requests.get(url)
            root = ET.fromstring(response.content)
            if response.status_code == 200:
                value_node = root.find(".//xsi:value", namespaces={"xsi": "http://www.w3.org/2001/XMLSchema-instance"}).text
                float_num = float(value_node)
                # 캘빈값 섭씨로 변경
                c_temp = round(float_num - 273.15 , 2)
                result_list.append(c_temp)
                

        # 각 result 저장, 구역별 label color 변경
        if main_frame.main_dic['SPOT_1']["active"] == "true":
            if  (result_list[0] > int(main_frame.main_dic['SPOT_1']['max'])  or result_list[0] < int(main_frame.main_dic['SPOT_1']['min'])):
                main_frame.change_color(main_frame.label_s1, 2)
                save_value['SPOT1'] = result_list[0]
            else:
                main_frame.change_color(main_frame.label_s1, 1)
                save_value['SPOT1'] = result_list[0]
        else:
            main_frame.change_color(main_frame.label_s1, 0)
            save_value['SPOT1'] = result_list[0]


        if main_frame.main_dic['SPOT_2']["active"] == "true":
            if  (result_list[1] > int(main_frame.main_dic['SPOT_2']['max'])  or result_list[1] < int(main_frame.main_dic['SPOT_2']['min'])):
                main_frame.change_color(main_frame.label_s2, 2)
                save_value['SPOT2'] = result_list[1]
            else:
                main_frame.change_color(main_frame.label_s2, 1)
                save_value['SPOT2'] = result_list[1]
        else:
            main_frame.change_color(main_frame.label_s2, 0)
            save_value['SPOT2'] = result_list[1]


        if main_frame.main_dic['SPOT_3']["active"] == "true":
            if  (result_list[2] > int(main_frame.main_dic['SPOT_3']['max'])  or result_list[2] < int(main_frame.main_dic['SPOT_3']['min'])):
                main_frame.change_color(main_frame.label_s3, 2)
                save_value['SPOT3'] = result_list[2]
            else:
                main_frame.change_color(main_frame.label_s3, 1)
                save_value['SPOT3'] = result_list[2]
        else:
            main_frame.change_color(main_frame.label_s3, 0)
            save_value['SPOT3'] = result_list[2]


        if main_frame.main_dic['BOX_1']["active"] == "true":
            if  (result_list[3] > int(main_frame.main_dic['BOX_1']['max'])) or (result_list[4] < int(main_frame.main_dic['BOX_1']['min'])):
                main_frame.change_color(main_frame.label_b1, 2)
                save_value['BOX1_MAX'] = result_list[3]
                save_value['BOX1_MIN'] = result_list[4]
            else:
                main_frame.change_color(main_frame.label_b1, 1)
                save_value['BOX1_MAX'] = result_list[3]
                save_value['BOX1_MIN'] = result_list[4]
        else:
            main_frame.change_color(main_frame.label_b1, 0)
            save_value['BOX1_MAX'] = result_list[3]
            save_value['BOX1_MIN'] = result_list[4]


        if main_frame.main_dic['BOX_2']["active"] == "true":
            if  (result_list[5] > int(main_frame.main_dic['BOX_2']['max'])) or (result_list[6] < int(main_frame.main_dic['BOX_2']['min'])):
                main_frame.change_color(main_frame.label_b2, 2)
                save_value['BOX2_MAX'] = result_list[5]
                save_value['BOX2_MIN'] = result_list[6]
            else:
                main_frame.change_color(main_frame.label_b2, 1)
                save_value['BOX2_MAX'] = result_list[5]
                save_value['BOX2_MIN'] = result_list[6]
        else:
            main_frame.change_color(main_frame.label_b2, 0)
            save_value['BOX2_MAX'] = result_list[5]
            save_value['BOX2_MIN'] = result_list[6]


        if main_frame.main_dic['BOX_3']["active"] == "true":
            
            if  (result_list[7] > int(main_frame.main_dic['BOX_3']['max'])) or (result_list[8] < int(main_frame.main_dic['BOX_3']['min'])):
                main_frame.change_color(main_frame.label_b3, 2) 
                save_value['BOX3_MAX'] = result_list[7]
                save_value['BOX3_MIN'] = result_list[8]
            else:
                main_frame.change_color(main_frame.label_b3, 1)
                save_value['BOX3_MAX'] = result_list[7]
                save_value['BOX3_MIN'] = result_list[8]
        else:
            main_frame.change_color(main_frame.label_b3, 0)
            save_value['BOX3_MAX'] = result_list[7]
            save_value['BOX3_MIN'] = result_list[8]
        save_value['TIME'] = datetime.now().strftime("%H_%M_%S")
        return save_value
    
    
    # URL box 생성, get temp 반복문, 저장
    def TempFromURL(self):
        url_box = []
        for number in range(1,4):
            url_box.append(f"http://{main_frame.main_ip}/prod/res/image/sysimg/measureFuncs/spot/{number}/valueT")
        for number in range(1,4):
            url_box.append(f"http://{main_frame.main_ip}/prod/res/image/sysimg/measureFuncs/mbox/{number}/maxT")
            url_box.append(f"http://{main_frame.main_ip}/prod/res/image/sysimg/measureFuncs/mbox/{number}/minT")
        cnt = 0
        st = None
        st_set = True
        os.makedirs("./save", exist_ok=True)
        while True:
            temp_data = self.TempFromCamera(url_box)
            if main_frame.file_save_active:
                if main_frame.file_save_trigger == True:
                    if st_set == True:
                        st = time.time()
                        st_set = False          
                    cnt += 1
                    self.data_box.append(temp_data)
                    current_time = time.time()
                    if current_time - st >= main_frame.interval:
                        self.STD.DataToCSV(self.data_box)
                        self.data_box = []
                        st = current_time
                else:
                    self.data_box = []
            else:
                self.data_box = []
            time.sleep(0.01)

            
            
    #=======================================================================================================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.title("AX8 Controller")
    root.geometry("900x600")  # 윈도우 크기 설정
    bg_color = "#04001f"

    main_frame = MainWindow(master=root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    video = VideoUtilsClass(main_frame, main_frame.main_ip, 10)
    threading.Thread(target=video.camera_loop, daemon=True).start()
    GT = TempMonitor()
    t = threading.Thread(target = GT.TempFromURL, daemon=True).start()

    root.mainloop()