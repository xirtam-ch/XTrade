import time
from configparser import ConfigParser

import pandas as pd
import os

from AnalyzeData import AnalyzeData
from C import C

import openpyxl
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.formula.translate import Translator
import pysnowball as ball
import subprocess;


def prepare():
    if not os.path.exists(C.DATA_PATH):
        os.mkdir(C.DATA_PATH)
    config = ConfigParser()
    config.read('token.config')

    ball.set_token(config.get('token', 'xueqiu'))  # xq_a_token=XXXX


if __name__ == '__main__':
    prepare()

    # 今天
    date = time.strftime("%Y-%m-%d", time.localtime())
    kline_data = AnalyzeData.get_days_kline()

    # print(kline_data)

    # 筛选数据，小市值
    # filtered_df = kline_data[kline_data['market_capital'] < 200 * 10000 * 10000]
    # print(f'小市值{filtered_df.shape[0]}')

    # 筛选数据，昨日跌过
    # filtered_df = filtered_df[filtered_df['last_open'] / filtered_df['last_low'] > 1.02]
    # print(f'昨日跌过{filtered_df.shape[0]}')

    # 筛选数据，今日红
    filtered_df = kline_data[(kline_data['close'] / kline_data['open']) > 1.01]
    print(f'今日红{filtered_df.shape[0]}')

    # 筛选数据，昨日绿
    filtered_df = filtered_df[filtered_df['last_open'] / filtered_df['last_close'] > 1.01]
    print(f'昨日绿{filtered_df.shape[0]}')
    #
    # 筛选数据，今日上影
    filtered_df = filtered_df[filtered_df['high'] / filtered_df['close'] > 1]
    print(f'今日上影{filtered_df.shape[0]}')

    # 筛选数据，昨日下影
    filtered_df = filtered_df[filtered_df['last_close'] / filtered_df['last_low'] > 1]
    print(f'昨日下影{filtered_df.shape[0]}')

    # 筛选数据，放量
    filtered_df = filtered_df[filtered_df['amount'] / filtered_df['last_amount'] > 1]
    print(f'放量{filtered_df.shape[0]}')

    # 筛选数据，高开
    filtered_df = filtered_df[filtered_df['open'] / filtered_df['last_close'] > 1]
    print(f'高开{filtered_df.shape[0]}')

    # 筛选数据，跳开
    filtered_df = filtered_df[filtered_df['close'] / filtered_df['last_open'] > 1]
    print(f'跳开{filtered_df.shape[0]}')

    filtered_df = filtered_df.reset_index()

    wb = openpyxl.load_workbook('module.xlsx')
    # 选择要操作的工作表
    sheet = wb.active  # 或者使用 workbook['Sheet1'] 选择特定的工作表

    index = 1
    for table_index, row in filtered_df.iterrows():
        # 获取 DataFrame 中的相关数据
        code = row['code']
        name = row['name']
        price = row['close']
        indicator = abs(
            (row['last_close'] - row['last_low']) / (row['last_open'] - row['last_close']) - 0.382) + abs(
            (row['high'] - row['close']) / (row['close'] - row['open']) - 0.382)
        # if indicator < 0.3: #
        # print(sheet)
        # 将数据填充到 Excel 文件中的相应列
        name_cell = sheet.cell(row=index + 1, column=1, value=f'{name} {str(code)}')
        name_cell.hyperlink = f'https://xueqiu.com/S/{code}'
        sheet.cell(row=index + 1, column=2, value=round(float(indicator), 2))
        sheet.cell(row=index + 1, column=3, value=price)
        index = index + 1

    # # 保存修改后的 Excel 文件
    wb.save(f'{C.XLS_OUTPUT_PATH}short2_{date}.xlsx')
    wb.close()
    subprocess.run(['say', '运行完毕，恭喜发财'])
