import configparser
import os
from UTIL.API import CAMERA_API
        
# self.ip_config = configparser.ConfigParser()
# self.box_config = configparser.ConfigParser()
# self.spot_config = configparser.ConfigParser()
CONFIG_DIC = {}


# Ini Config Control Class
class ConfigManager():
    def __init__(self):
        self.config_path = "./setting/Main.ini"
        self.ini_list = ['CAMERA','SPOT_1','SPOT_2','SPOT_3','BOX_1','BOX_2','BOX_3']
        # ip_config, box_config, spot_config
        self.MainParser = configparser.ConfigParser()
        
        os.makedirs('./setting', exist_ok =True)
        self.ini_dic = {}
        self.config_dic = self.read_ini()
        self.ip = self.config_dic['CAMERA']['ip']
        self.API = CAMERA_API(self.ip)
        self.dict_to_camera = self.API.get_parameter(self.config_dic)
        self.MakeDicToIni(self.dict_to_camera)
        print("Config Initialize Complete")


    # 초기화 시 Camera에서 값 가져온 후 Ini file update
    def InitValueToCamera(self):
        modify_dict = self.API.get_parameter(self.config_dic)
        return modify_dict


    # Camera Setting 값 변경
    def change_setting_value(self, section, value_dic):
        config = configparser.ConfigParser()
        config.read(self.config_path)
        if section in config:
            config[section] = value_dic
        else:
            print(f"'{section}' 섹션이 INI 파일에 존재하지 않습니다.")
            return
        with open(self.config_path, 'w') as config_file:
            config.write(config_file)
        print("111")
        self.API.set_parameter(section, value_dic)
        change_dic = self.read_ini()
        return change_dic


    # Dictionary 값 Ini에 저장
    def MakeDicToIni(self, dic):

        config = configparser.ConfigParser()

        for key, values in dic.items():
            config[key] = values

        # 파일로 저장
        with open(self.config_path, "w") as config_file:
            config.write(config_file)
        print(f"{self.config_path} 파일에 저장되었습니다.")


    #Config 생성
    def CreateConfig(self):
        for name in self.ini_list:
            self.MainParser[name] = {}
            print('!!!!    :   ', name)
            if "SPOT" in name:
                self.MainParser[name]["ACTIVE"] = "False"
                self.MainParser[name]["X"] = "100"
                self.MainParser[name]["Y"] = "100"
                self.MainParser[name]["MIN"] = "10"
                self.MainParser[name]["MAX"] = "50"
                
            elif "BOX" in name:
                self.MainParser[name]["ACTIVE"] = "False"
                self.MainParser[name]["X"] = "100"
                self.MainParser[name]["Y"] = "100"
                self.MainParser[name]["WIDTH"] = "50"
                self.MainParser[name]["HEIGHT"] = "50"
                self.MainParser[name]["MIN"] = "10"
                self.MainParser[name]["MAX"] = "50"
            else:
                self.MainParser[name]['IP'] = self.ip
        with open (self.config_path,"a",encoding = "utf-8") as configfile:
            self.MainParser.write(configfile)  
            
            
    # Ini File to Dic
    def read_ini(self):
        self.MainParser.read(self.config_path)  # .ini 파일의 경로를 지정하세요.
        print(f"self.config_path = {self.config_path}")
        # configparser 객체를 중첩 딕셔너리로 변환
        config_dict = {}
        for section in self.MainParser.sections():
            # print(section)
            config_dict[section] = {}
            for key, val in self.MainParser.items(section):
                config_dict[section][key] = val

                # print(config_dict)
        return config_dict 