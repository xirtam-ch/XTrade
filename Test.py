import json
import os
import time

import numpy as np
import pysnowball as ball
import streamlit as st
import tushare as ts

from AnalyzeData import AnalyzeData
from DataUpgrade import DataUpgrade
from Utils import Utils
from configparser import ConfigParser

if __name__ == '__main__':
    config = ConfigParser()
    config.read('token.config')

    ball.set_token(config.get('token', 'xueqiu'))  # xq_a_token=XXXX
    pro = ts.pro_api(config.get('token', 'tushare'))

    date = time.strftime("%Y-%m-%d", time.localtime())

    # print(json.dumps(ball.quotec('BK0744'), sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ':')))
    # print(json.dumps(ball.watch_list(), sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ':')))

    # data = ball.capital_assort("SZ300318")
    # print(json.dumps(data, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ':')))
    # print(json.dumps(ball.holders('SH600749'), sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ':')))

    # print(Utils.T2Bcode("838924.BJ"))
    # print(Utils.B2Tcode("BJ838924"))

    # AnalyzeData.get_report(AnalyzeData.get_url(0, code="603236"), 0)
    # AnalyzeData.get_report(AnalyzeData.get_url(1))

    # DataUpgrade.updateBK(ball)
    # DataUpgrade.updateStocks(pro)

    # print(ball.quote_detail('BK0001'))

    # fReport = AnalyzeData.getFReport()
    # fReportTable = AnalyzeData.getStocksTable(ball, fReport)
    # print(fReportTable)
    # AnalyzeData.get_report(AnalyzeData.get_url(3), 3)  # 宏观
    #
    # print("### 西藏旅游股东人数")
    # print(pro.stk_holdernumber(ts_code='600749.SH', start_date='20180101', end_date=date))

    df_stocks = AnalyzeData.get_last_week_activity_index()
    print(df_stocks)
