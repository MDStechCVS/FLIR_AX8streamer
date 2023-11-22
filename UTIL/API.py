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
# http://192.168.0.178/prod/res/image/sysimg/measureFuncs/spot/1/active




class CAMERA_API():
    def __init__(self, ip):
        self.ip = ip

    
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
            url = f"http://192.168.0.178/prod/res/image/sysimg/measureFuncs/{target}/{number}/{sub_key}?set={value}"
            response = requests.get(url)
            if response.status_code == 200:
                print("SET parameter Complete")
            else:
                print("SET Parameter FAIL")
