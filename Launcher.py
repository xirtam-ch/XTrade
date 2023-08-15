import json
import os
import sys
import time

import numpy as np
import pysnowball as ball
import streamlit as st
import tushare as ts

from AnalyzeData import AnalyzeData
from DataUpgrade import DataUpgrade
from Utils import Utils
from C import C
from configparser import ConfigParser
import pandas as pd


def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)


def add_color(table, column):
    table[column] = table[column].map(
        lambda x: f"<div class='bg_green'>{x}</div>" if (x is not None and x > 0) else f"<div class='bg_red'>{x}</div>")


def str_big_number(table, column):
    table[column] = table[column].map(lambda x: Utils.str_of_num(x))


if __name__ == '__main__':

    os.environ['NUMEXPR_MAX_THREADS'] = '8'

    config = ConfigParser()
    config.read('token.config')

    ball.set_token(config.get('token', 'xueqiu'))  # xq_a_token=XXXX
    pro = ts.pro_api(config.get('token', 'tushare'))

    st.set_page_config(layout="wide")
    local_css("style.css")

    date = time.strftime("%Y-%m-%d", time.localtime())

    myStockWithName = [  # 自选股，跟踪个股研报，格式直接从雪球网页复制
        '西藏旅游(SH:600749)', "千味央厨(SZ:001215)", "亚钾国际(SZ:000893)", "小熊电器(SZ:002959)",
        "盐湖股份(SZ:000792)",
        "杭萧钢构(SH:600477)", '中望软件(SH:688083)', '兴发集团(SH:600141)', '华大基因(SZ:300676)',
        "雪人股份(SZ:002639)",
        "牧高笛(SH:603908)", "燕京啤酒(SZ:000729)", "和远气体(SZ:002971)", "中体产业(SH:600158)", '中国船舶(SH:600150)',
        '中无人机(SH:688297)',
        '新强联(SZ:300850)', '奇安信-U(SH:688561)', "成都先导(SH:688222)", "洽洽食品(SZ:002557)", "农发种业(SH:600313)",
        '东方电缆(SH:603606)', '东方财富(SZ:300059)', '沃森生物(SZ:300142)', '道恩股份(SZ:002838)',
        '南模生物(SH:688265)', '君亭酒店(SZ:301073)'
    ]

    myStock = {x[-7:-1] for x in myStockWithName}

    if not os.path.exists(C.DATA_PATH):
        os.mkdir(C.DATA_PATH)

        # 更新基础数据
        DataUpgrade.updateBK(ball)
        DataUpgrade.updateStocks(pro)

    elif len(sys.argv) > 1 and sys.argv[1] == 'bk':
        DataUpgrade.updateBK(ball)

    if not os.path.exists(C.CACHE_PATH):
        os.mkdir(C.CACHE_PATH)

    # ——————————————————————————————

    # 板块涨跌
    dfs = AnalyzeData.getBKs(ball)

    chartData = AnalyzeData.getChart()
    st.line_chart(chartData,x='date',y='X')

    st.markdown(f"[打开个股研报](file:///{C.REPORT_PATH}{date}-个股/)")
    st.markdown(f"[打开行业研报](file:///{C.REPORT_PATH}{date}-行业/)")
    st.markdown(f"[打开宏观研报](file:///{C.REPORT_PATH}{date}-宏观/)")

    st.write("")
    st.markdown("### 今晚财报:")

    fReport = AnalyzeData.getFReport()
    fReportTable = AnalyzeData.getStocksTable(ball, fReport)
    add_color(fReportTable, 'percent')
    add_color(fReportTable, 'current_year_percent')
    str_big_number(fReportTable, 'amount')
    st.write(fReportTable.to_html(escape=False, index=False), unsafe_allow_html=True)

    st.write("")
    st.markdown("### 今日涨幅前10板块:")

    add_color(dfs[0], 'percent')
    add_color(dfs[0], 'current_year_percent')

    st.write(dfs[0].to_html(escape=False, index=False), unsafe_allow_html=True)

    st.write("")
    st.markdown("### 今日跌幅前10板块:")

    add_color(dfs[1], 'percent')
    add_color(dfs[1], 'current_year_percent')

    st.write(dfs[1].to_html(escape=False, index=False), unsafe_allow_html=True)

    st.write("")
    st.markdown("### 今年涨幅前10板块:")

    add_color(dfs[2], 'percent')
    add_color(dfs[2], 'current_year_percent')

    st.write(dfs[2].to_html(escape=False, index=False), unsafe_allow_html=True)

    st.write("")
    st.markdown("### 今年跌幅前10板块:")

    add_color(dfs[3], 'percent')
    add_color(dfs[3], 'current_year_percent')

    st.write(dfs[3].to_html(escape=False, index=False), unsafe_allow_html=True)
    ## 板块涨跌

    ## 个股涨跌
    df_stocks = AnalyzeData.getStocks(ball)

    st.write("")
    st.markdown("### 今日涨幅前10个股(所有个股数据排除ST，下同):")

    add_color(df_stocks[0], 'percent')
    add_color(df_stocks[0], 'current_year_percent')

    st.write(df_stocks[0].to_html(escape=False, index=False), unsafe_allow_html=True)

    st.write("")
    st.markdown("### 今日跌幅前10个股:")

    add_color(df_stocks[1], 'percent')
    add_color(df_stocks[1], 'current_year_percent')

    st.write(df_stocks[1].to_html(escape=False, index=False), unsafe_allow_html=True)

    st.write("")
    st.markdown("### 今日成交额前10个股:")

    add_color(df_stocks[2], 'percent')
    add_color(df_stocks[2], 'current_year_percent')
    str_big_number(df_stocks[2], 'amount')
    st.write(df_stocks[2].to_html(escape=False, index=False), unsafe_allow_html=True)

    st.write("")
    st.markdown("### 今日成交额后10个股(排除北交所):")

    add_color(df_stocks[3], 'percent')
    add_color(df_stocks[3], 'current_year_percent')
    str_big_number(df_stocks[3], 'amount')

    st.write(df_stocks[3].to_html(escape=False, index=False), unsafe_allow_html=True)

    st.write("")
    st.markdown("### 今年涨幅前10个股:")

    add_color(df_stocks[4], 'percent')
    add_color(df_stocks[4], 'current_year_percent')

    st.write(df_stocks[4].to_html(escape=False, index=False), unsafe_allow_html=True)

    st.write("")
    st.markdown("### 今年跌幅前10个股:")

    add_color(df_stocks[5], 'percent')
    add_color(df_stocks[5], 'current_year_percent')

    st.write(df_stocks[5].to_html(escape=False, index=False), unsafe_allow_html=True)
    ## 个股涨跌

    st.write("")
    df_stocks_today = Utils.readCSVFromCache("today_stocks_" + date)

    today_up = df_stocks_today[df_stocks_today.percent > 0].shape[0]
    today_same = df_stocks_today[df_stocks_today.percent == 0].shape[0]
    today_down = df_stocks_today[df_stocks_today.percent < 0].shape[0]

    today_sum = today_up + today_same + today_down
    st.markdown(
        "### 今日上涨:" + str(today_up) +"(" + str(round(Utils.divFormat(today_up, today_sum), 2) * 100) + "%)"
        + "，横盘:" + str(today_same) +"(" + str(round(Utils.divFormat(today_same, today_sum), 2) * 100) + "%)"
        + "，下跌:" + str(today_down) +"(" + str(round(Utils.divFormat(today_down, today_sum), 2) * 100) + "%)"
    )

    st.markdown(
        "### 涨幅中位数:" + str(round(np.median(df_stocks_today[df_stocks_today.percent > 0].percent), 2)) + "%"
        + "，跌幅中位数:" + str(round(np.median(df_stocks_today[df_stocks_today.percent < 0].percent), 2)) + "%"
    )

    st.markdown(
        "### 涨幅超9.5%:" + str(df_stocks_today[df_stocks_today.percent > 9.5].shape[0])
        + "，跌幅超9.5%:" + str(df_stocks_today[df_stocks_today.percent < -9.5].shape[0])
    )

    # 测试折线图 开始
    # st.line_chart(np.array(df_stocks_today[df_stocks_today.percent > 0].sort_values('percent').percent).tolist())
    # st.line_chart(np.array(pd.DataFrame.abs(df_stocks_today[df_stocks_today.percent < 0].sort_values('percent', ascending=False).percent)).tolist())
    # 测试折线图 结束

    # ## 个股资金
    # df_stocks = AnalyzeData.getCapitalAssort(ball)
    #
    # st.write("")
    # st.markdown("### 今日流入前10个股:")
    # st.write(df_stocks[0].to_html(escape=False, index=False), unsafe_allow_html=True)
    #
    # st.write("")
    # st.markdown("### 今日流出前10个股:")
    # st.write(df_stocks[1].to_html(escape=False, index=False), unsafe_allow_html=True)
    #
    # st.write("")
    # st.markdown("### 今日大单前10个股:")
    # st.write(df_stocks[2].to_html(escape=False, index=False), unsafe_allow_html=True)
    #
    # st.write("")
    # st.markdown("### 今日大单后10个股:")
    # st.write(df_stocks[3].to_html(escape=False, index=False), unsafe_allow_html=True)
    #
    # ## 个股资金

    print('宏观研报...')
    AnalyzeData.get_report(AnalyzeData.get_url(3), type=3)  # 宏观

    print('行业研报...')
    AnalyzeData.get_report(AnalyzeData.get_url(1), type=1)  # 行业
    # AnalyzeData.get_report(AnalyzeData.get_url(1), type=1, keyword=['深度', '旅游'])  # 行业

    print('个股研报...')
    AnalyzeData.get_report(AnalyzeData.get_url(0, ), type=0)  # 个股

    # 仅获取自选股个股研报
    for code in myStock:
        AnalyzeData.get_report(AnalyzeData.get_url(0, code=code), type=0)  # 个股

    print("执行完毕")
