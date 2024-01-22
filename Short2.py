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


def prepare():
    if not os.path.exists(C.DATA_PATH):
        os.mkdir(C.DATA_PATH)
    config = ConfigParser()
    config.read('token.config')

    ball.set_token(config.get('token', 'xueqiu'))  # xq_a_token=XXXX


if __name__ == '__main__':
    prepare()
    date = time.strftime("%Y-%m-%d", time.localtime())

    kline_data = AnalyzeData.get_two_day_kline()
    # print(kline_data)

    # 筛选数据，小市值
    filtered_df = kline_data[kline_data['market_capital'] < 200 * 10000 * 10000]
    print(f'小市值{filtered_df.shape[0]}')

    # 筛选数据，放量
    filtered_df = filtered_df[filtered_df['amount'] / filtered_df['last_amount'] > 2]
    print(f'放量{filtered_df.shape[0]}')

    # 筛选数据，昨日跌过
    filtered_df = filtered_df[filtered_df['last_open'] / filtered_df['last_low'] > 1.02]
    print(f'昨日跌过{filtered_df.shape[0]}')

    # 筛选数据，今日涨
    filtered_df = filtered_df[filtered_df['percent'] >1.3]
    print(f'今日涨{filtered_df.shape[0]}')

    # 筛选数据，今日上影
    filtered_df = filtered_df[filtered_df['high'] / filtered_df['close'] > 1.02]
    print(f'今日上影{filtered_df.shape[0]}')

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
        indicator = (row['high'] / row['close']) * (row['last_open'] / row['last_low'])

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
