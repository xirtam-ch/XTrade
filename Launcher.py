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
from C import C
from configparser import ConfigParser


def local_css(file_name):
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)


def add_color(table, column):
    table[column] = table[column].map(
        lambda x: f"<div class='bg_green'>{x}</div>" if x > 0 else f"<div class='bg_red'>{x}</div>")


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

    myStock = [  # 自选股，跟踪个股研报
        "605089", "600749", "001215", "000893", "600258", "002959", "000792", "600477",
        "002639", "603908", "000729", "002971", "600158", "300043", "600078", "002326",
        "688222", "600054", "000589", "000831", "002557", "300315", "600313"
    ]

    if not os.path.exists(C.DATA_PATH):
        os.mkdir(C.DATA_PATH)

        # 更新基础数据
        DataUpgrade.updateBK(ball)
        DataUpgrade.updateStocks(pro)

    if not os.path.exists(C.CACHE_PATH):
        os.mkdir(C.CACHE_PATH)

    # ——————————————————————————————

    # 板块涨跌
    dfs = AnalyzeData.getBKs(ball)

    st.markdown(f"[打开个股研报](file:///{C.REPORT_PATH}{date}-个股/)")
    st.markdown(f"[打开行业研报](file:///{C.REPORT_PATH}{date}-行业/)")
    st.markdown(f"[打开宏观研报](file:///{C.REPORT_PATH}{date}-宏观/)")

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

    st.markdown(
        "### 今日上涨:" + str(today_up)
        + "，横盘:" + str(today_same)
        + "，下跌:" + str(today_down)
        + "，涨跌比:" + str(round(Utils.divFormat(today_up, today_down), 2))
    )

    st.markdown(
        "### 涨幅中位数:" + str(round(np.median(df_stocks_today[df_stocks_today.percent > 0].percent), 2)) + "%"
        + "，跌幅中位数:" + str(round(np.median(df_stocks_today[df_stocks_today.percent < 0].percent), 2)) + "%"
    )

    st.markdown(
        "### 涨幅超9.5%:" + str(df_stocks_today[df_stocks_today.percent > 9.5].shape[0])
        + "，跌幅超9.5%:" + str(df_stocks_today[df_stocks_today.percent < -9.5].shape[0])
    )

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
    AnalyzeData.get_report(AnalyzeData.get_url(1), type=1, keyword=['深度', '旅游'])  # 行业

    print('个股研报...')
    AnalyzeData.get_report(AnalyzeData.get_url(0, ), type=0, keyword="首次")  # 个股

    # 仅获取自选股个股研报
    for code in myStock:
        AnalyzeData.get_report(AnalyzeData.get_url(0, code=code), type=0)  # 个股

    print("执行完毕")
