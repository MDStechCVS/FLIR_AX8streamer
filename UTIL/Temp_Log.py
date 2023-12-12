# windows 
#=========================================================
# import openpyxl 
# from openpyxl.utils.dataframe import dataframe_to_rows
# from openpyxl.drawing.image import Image
# from openpyxl import Workbook
#=========================================================





import pandas as pd
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import os


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

    # def DataToExcel(self, value_list, time_list):
    #     file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    #     folder_path = f'./save/'
    #     print(f"{folder_path}{file_name}")
    #     os.makedirs(folder_path, exist_ok=True)
    #     file_path = f"{folder_path}{file_name}"
    #     try:
    #         workbook = openpyxl.load_workbook(file_path)
    #         new_sheet = workbook.create_sheet(title='Temp Log')
    #     except FileNotFoundError:
    #         workbook = openpyxl.Workbook()
    #         new_sheet = workbook.create_sheet(title='Temp Log')

    #     # 데이터프레임 생성
    #     df = pd.DataFrame(value_list, columns=['SPOT_1', 'SPOT_2', 'SPOT_3', 'BOX_1_MAX', 'BOX_1_MIN', 'BOX_2_MAX', 'BOX_2_MIN', 'BOX_3_MAX', 'BOX_3_MIN'])
    #     df["TIME"] = time_list
    #     column_order = ['TIME'] + [col for col in df.columns if col != 'TIME']
    #     df = df[column_order]

    #     # 엑셀 헤더 추가
    #     for row in dataframe_to_rows(df, index=False, header=True):
    #         new_sheet.append(row)

    #     # 그래프 그리기
    #     plt.figure(figsize=(20, 6))
    #     for col in df.columns[1:]:  # 'TIME' 열을 제외하고 그래프 그리기
    #         plt.plot(time_list, df[col], label=col)
    #     plt.xlabel('Time')
    #     plt.ylabel('Value')
    #     plt.title('Data Chart')

    #     plt.legend(loc='upper left', bbox_to_anchor=(1, 1), borderaxespad=0., fontsize='small')
    #     plt.xticks(rotation=45)  # x 라벨을 45도 회전시킴

    #     # 차트 보여주기
    #     plt.tight_layout()

    #     # 그래프 이미지를 BytesIO로 저장
    #     image_stream = BytesIO()
    #     plt.savefig(image_stream, format='png')

    #     # BytesIO의 이미지를 엑셀에 삽입
    #     image = Image(image_stream)
    #     new_sheet.add_image(image, 'L1')
        
    #     if 'Sheet' in workbook.sheetnames:
    #         sheet = workbook['Sheet']
    #         workbook.remove(sheet)

    #     # 엑셀 파일 저장 (덮어쓰기)
    #     workbook.save(file_path)
    #     plt.close()





