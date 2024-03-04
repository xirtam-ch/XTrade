import time
from configparser import ConfigParser

import math
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

from Utils import Utils


def prepare():
    if not os.path.exists(C.DATA_PATH):
        os.mkdir(C.DATA_PATH)
    config = ConfigParser()
    config.read('token.config')

    ball.set_token(config.get('token', 'xueqiu'))  # xq_a_token=XXXX


if __name__ == '__main__':
    prepare()

    black_list = []
    noticed_list = []

    # 今天
    date = time.strftime("%Y-%m-%d", time.localtime())
    while True:
        date = time.strftime("%Y-%m-%d", time.localtime())

        all_stock_keys = Utils.readFromCSV('stocks')
        remove_bj = all_stock_keys[~all_stock_keys.index.str.contains('BJ')]  # 排除北郊所，减少请求次数
        bk_keys = remove_bj[~(remove_bj.name.str.contains('ST'))]  # 排除ST股，减少请求次数

        symbols = []
        symbols_str = ''
        count = 0
        group = 0
        groupLength = 300

        for row in bk_keys.iterrows():
            symbols_str = symbols_str + Utils.T2Bcode(row[0]) + ","
            count = count + 1
            if count >= groupLength:
                symbols.append(symbols_str)

                symbols_str = ''
                group = group + 1
                count = 0

        for i in range(0, group):
            data = ball.quotec(symbols[i])
            for item in data['data']:
                if Utils.get_daily_limit_price(item['symbol'], item['last_close']) != item[
                    'current']:  # 非涨停
                    if item['is_trade']:  # if item['high'] is not None:
                        if item['current'] >= math.floor(item['last_close'] * Utils.get_daily_limit_percent(item['symbol']) * 0.99 * 100) / 100:
                            review_days = 10
                            last_last_close = \
                                AnalyzeData.get_days_kline(item['symbol'], review_days)[review_days - 3]['close'][0]
                            if not Utils.is_daily_limit_up(item['symbol'], last_last_close,
                                                           item['last_close']):  # 昨日未涨停
                                if item['symbol'] not in noticed_list:
                                    print('涨9 ' + item['symbol'][2:] + ' ' +
                                          bk_keys.loc[Utils.B2Tcode(item['symbol'])]['name'])
                                    noticed_list.append(item['symbol'])
                                    subprocess.run(['say', '-r', '150', ' '.join(item['symbol'][2:])])

        print('执行一轮...')
        time.sleep(1)
    # subprocess.run(['say', '运行完毕，恭喜发财'])
