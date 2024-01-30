import traceback
import requests
import xml.etree.ElementTree as ET
import time

# URL SAMPLE
#=========================================URL모음
# self.url = "http://192.168.0.178/prod/res/image/sysimg/measureFuncs/"
# self.boxes = f"http://192.168.0.178/prod/res/image/sysimg/measureFuncs/mbox/1"
# self.active = f"http://192.168.0.178/prod/res/image/sysimg/measureFuncs/mbox/1/active"
# self.max = f"http://192.168.0.178/prod/res/image/sysimg/measureFuncs/mbox/1/maxT"
# self.avg = f"http://192.168.0.178/prod/res/image/sysimg/measureFuncs/mbox/1/avgT"
# self.min = f"http://192.168.0.178/prod/res/image/sysimg/measureFuncs/mbox/1/minT"
# self.min = f"http://192.168.0.178/prod/res/image/sysimg/measureFuncs/mbox/1/width?set=15"
# http://192.168.0.178/prod/res/image/sysimg/measureFuncs/spot/1/active




class API():
    def __init__(self, ip):
        self.ip = ip
        self.base_url = f"http://{ip}/prod/res"
        self.rest_url = {
                        "LED" : ['system', 'vcam', 'torch'], 
                        "OVERLAY" : ['resmon', 'config', 'hideGraphics'], 
                        "MODE" : ['image', 'sysimg', 'fusion', 'fusionData', 'fusionMode'], 
                        "PALETTE" : ['image','sysimg','palette','readFile'], 
                        
                        "SPOT1_ACTIVE" : ['image', 'sysimg', 'measureFuncs', 'spot', '1', 'active'], 
                        "SPOT1_X" : ['image', 'sysimg', 'measureFuncs', 'spot', '1', 'x'], 
                        "SPOT1_Y" : ['image', 'sysimg', 'measureFuncs', 'spot', '1', 'y'], 
                        
                        "SPOT2_ACTIVE" : ['image', 'sysimg', 'measureFuncs', 'spot', '2', 'active'], 
                        "SPOT2_X" : ['image', 'sysimg', 'measureFuncs', 'spot', '2', 'x'], 
                        "SPOT2_Y" : ['image', 'sysimg', 'measureFuncs', 'spot', '2', 'y'], 
                        
                        "SPOT3_ACTIVE" : ['image', 'sysimg', 'measureFuncs', 'spot', '3', 'active'], 
                        "SPOT3_X" : ['image', 'sysimg', 'measureFuncs', 'spot', '3',  'x'], 
                        "SPOT3_Y" : ['image', 'sysimg', 'measureFuncs', 'spot', '3',  'y'], 
                        
                        "BOX1_ACTIVE" : ['image', 'sysimg', 'measureFuncs', 'mbox', '1', 'active'],
                        "BOX1_X" : ['image', 'sysimg', 'measureFuncs', 'mbox', '1', 'x'],
                        "BOX1_Y" : ['image', 'sysimg', 'measureFuncs', 'mbox', '1', 'y'],
                        "BOX1_H" : ['image', 'sysimg', 'measureFuncs', 'mbox', '1', 'width'],
                        "BOX1_W" : ['image', 'sysimg', 'measureFuncs', 'mbox', '1', 'height'],

                        "BOX2_ACTIVE" : ['image', 'sysimg', 'measureFuncs', 'mbox', '2', 'active'],
                        "BOX2_X" : ['image', 'sysimg', 'measureFuncs', 'mbox', '2', 'x'],
                        "BOX2_Y" : ['image', 'sysimg', 'measureFuncs', 'mbox', '2', 'y'],
                        "BOX2_H" : ['image', 'sysimg', 'measureFuncs', 'mbox', '2', 'width'],
                        "BOX2_W" : ['image', 'sysimg', 'measureFuncs', 'mbox', '2', 'height'],

                        "BOX3_ACTIVE" : ['image', 'sysimg', 'measureFuncs', 'mbox', '3', 'active'],
                        "BOX3_X" : ['image', 'sysimg', 'measureFuncs', 'mbox', '3', 'x'],
                        "BOX3_Y" : ['image', 'sysimg', 'measureFuncs', 'mbox', '3', 'y'],
                        "BOX3_H" : ['image', 'sysimg', 'measureFuncs', 'mbox', '3', 'width'],
                        "BOX3_W" : ['image', 'sysimg', 'measureFuncs', 'mbox', '3', 'height'],
                        }


        
        
        self.spot_value = ['active', 'x', 'y']
        self.spot_temp = ['maxT', 'minT']
        self.box_value = ['active', 'x', 'y', 'width', 'height']
        self.box_temp = ['maxT', 'minT', 'avgT']
        self.INFO = {
                    "LED" : None,
                    "OVERLAY" : None,
                    "MODE" : None,
                    "PALETTE" : None,
                    "SPOT1_ACTIVE" : None,
                    "SPOT1_X" : None,
                    "SPOT1_Y" : None,
                    "SPOT1_MIN" : '10',
                    "SPOT1_MAX" : '40',
                    "SPOT2_ACTIVE" : None,
                    "SPOT2_X" : None,
                    "SPOT2_Y" : None,
                    "SPOT2_MIN" : '10',
                    "SPOT2_MAX" : '40',
                    "SPOT3_ACTIVE" : None,
                    "SPOT3_X" : None,
                    "SPOT3_Y" : None,
                    "SPOT3_MIN" : '10',
                    "SPOT3_MAX" : '40',
                    "BOX1_ACTIVE" : None,
                    "BOX1_X" : None,
                    "BOX1_Y" : None,
                    "BOX1_H" : None,
                    "BOX1_W" : None,
                    "BOX1_MIN" : '10',
                    "BOX1_MAX" : '40',
                    "BOX2_ACTIVE" : None,
                    "BOX2_X" : None,
                    "BOX2_Y" : None,
                    "BOX2_H" : None,
                    "BOX2_W" : None,
                    "BOX2_MIN" : '10',
                    "BOX2_MAX" : '40',
                    "BOX3_ACTIVE" : None,
                    "BOX3_X" : None,
                    "BOX3_Y" : None,
                    "BOX3_H" : None,
                    "BOX3_W" : None,
                    "BOX3_MIN" : '10',
                    "BOX3_MAX" : '40',
                    }
        for key, value in self.rest_url.items():
            url = self.make_url(value)
            result = self.get_camera_value(url)
            self.INFO[key] = result
        for value, item in self.INFO.items():
            print(f"{value}= \t {item}")


    def make_url(self, data_list, set = False, value = None):
        try:
            if data_list == None:
                raise ValueError
            URL = self.base_url 
            for item in data_list:
                URL += '/' + item
            if set == True and bool(value) == True:
                URL += f'?set={value}'
            print(f"final url : {URL}")
            return URL
        except ValueError as e:
            print(f"API / make_url error: {traceback.format_exc()}")


    def get_camera_value(self, URL):
        try:
            response = requests.get(URL)
            root = ET.fromstring(response.content)
            if response.status_code == 200:
                get_value = root.find(".//xsi:value", namespaces={"xsi": "http://www.w3.org/2001/XMLSchema-instance"}).text
            return get_value
        except Exception as e:
            print(f"get_camera_value Error : {e}")



    def set_camera_value(self, URL):
        try:
            response = requests.get(URL)
            if response.status_code == 200:
                print("SET parameter Complete")
                return True  # 성공 시 True 반환
            else:
                print(f"SET Parameter FAIL. Status code: {response.status_code}")
                return False  # 실패 시 False 반환
            
                
        except Exception as e:
            print(f"set_camera_value Error: {e}")
            return False  # 예외 발생 시 False 반환
    


    # GET value
    def get_parameter(self, infor_dict):
        # print("GET parameter Start")
        target = None
        number = None
        for main_key, sub_dict in infor_dict.items():
            
            target = main_key[:-2].lower()
            number = main_key[-1]
            
            if target == "box":
                target = "mbox"
            
            for sub_key, value in sub_dict.items():  # main, sub, value
                if sub_key == "min" or sub_key == "max" or sub_key == "ip":
                    continue
                url = f"http://{self.ip}/prod/res/image/sysimg/measureFuncs/{target}/{number}/{sub_key}"
                response = requests.get(url)
                root = ET.fromstring(response.content)
                if response.status_code == 200:
                    value_node = root.find(".//xsi:value", namespaces={"xsi": "http://www.w3.org/2001/XMLSchema-instance"}).text
                    infor_dict[main_key][sub_key] = value_node
                else:
                    print("GET Parameter FAIL")
        return infor_dict


    # SET Value     
    def set_parameter(self, section, value_dic):
        print("SET parameter Start")
        target = section[:-2].lower()
        number = section[-1]
        if target == "box":
            target = "mbox"
        for sub_key, value in value_dic.items():  # main, sub, value
            if sub_key == "min" or sub_key == "max" or sub_key == "ip":
                continue
            if sub_key == "active":
                if value == "true":
                    value = True
                else:
                    value = False
            url = f"http://{self.ip}/prod/res/image/sysimg/measureFuncs/{target}/{number}/{sub_key}?set={value}"
            response = requests.get(url)
            if response.status_code == 200:
                print("SET parameter Complete")
            else:
                print("SET Parameter FAIL")
