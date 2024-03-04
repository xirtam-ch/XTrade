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
            # {
            # 	'symbol': 'SZ000719',
            # 	'current': 8.86,
            # 	'percent': -2.42,
            # 	'chg': -0.22,
            # 	'timestamp': 1706857491000,
            # 	'volume': 19173353,
            # 	'amount': 174658253.0,
            # 	'market_capital': 9065585216.0,
            # 	'float_market_capital': 5910927231.0,
            # 	'turnover_rate': 2.87,
            # 	'amplitude': 9.8,
            # 	'open': 8.96,
            # 	'last_close': 9.08,
            # 	'high': 9.49,
            # 	'low': 8.6,
            # 	'avg_price': 9.109,
            # 	'trade_volume': None,
            # 	'side': 0,
            # 	'is_trade': False,
            # 	'level': 1,
            # 	'trade_session': None,
            # 	'trade_type': None,
            # 	'current_year_percent': -8.94,
            # 	'trade_unique_id': None,
            # 	'type': 11,
            # 	'bid_appl_seq_num': None,
            # 	'offer_appl_seq_num': None,
            # 	'volume_ext': None,
            # 	'traded_amount_ext': None,
            # 	'trade_type_v2': None,
            # 	'yield_to_maturity': None
            # }
            for item in data['data']:
                if Utils.get_daily_limit_price(item['symbol'], item['last_close']) != item['open']:  # 非开盘涨停
                    if item['is_trade']:  # if item['high'] is not None:
                        if Utils.is_fried_board(item['symbol'], item['last_close'], item['current'],
                                                item['high']):  # 炸板
                            # print(f'炸板 ' + item['symbol'])
                            review_days = 10
                            last_last_close = \
                                AnalyzeData.get_days_kline(item['symbol'], review_days)[review_days - 3]['close'][0]
                            if not Utils.is_daily_limit_up(item['symbol'], last_last_close,
                                                           item['last_close']):  # 昨日未涨停
                                if item['symbol'] not in noticed_list:
                                    print('首板炸板 ' + item['symbol'][2:] +' '+bk_keys.loc[Utils.B2Tcode(item['symbol'])]['name'])
                                    noticed_list.append(item['symbol'])
                                    subprocess.run(['say', item['symbol'][2:] + '炸板'])

        print('执行一轮...')
        time.sleep(1)
    # subprocess.run(['say', '运行完毕，恭喜发财'])
