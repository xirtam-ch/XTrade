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

if __name__ == '__main__':
    ball.set_token('xq_a_token=773e2b1aa13013252cba4bc4922519d585dc3955;')
    pro = ts.pro_api("e138f79884f8fa15e980bf3cceea0b66975d877e91dcc4ffae44d194")

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

    AnalyzeData.get_report(AnalyzeData.get_url(3), 3)  # 宏观
