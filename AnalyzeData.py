import json
import os
import random
import time
from time import sleep

import openpyxl
import pandas as pd
import requests
from bs4 import BeautifulSoup

from C import C
from Utils import Utils
import re


class AnalyzeData:

    @staticmethod
    def getStocks(ball):

        groupLength = 300
        headAndTail = 10

        print("获取个股信息...")

        bk_keys = Utils.readFromCSV('stocks')
        bk_table = pd.DataFrame(columns=['code', 'name', 'percent'])

        symbols = [
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
        ]

        group = 0
        count = 0

        for row in bk_keys.iterrows():
            symbols[group] = symbols[group] + Utils.T2Bcode(row[0]) + ","
            count = count + 1
            if count >= groupLength:
                # print(symbols[group])
                group = group + 1
                count = 0

        # print("symbols，" + str(symbols))

        # print(json.dumps(data, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ':')))

        for i in range(0, group + 1):
            data = ball.quotec(symbols[i])
            for item in data['data']:
                bk_table = bk_table.append({
                    'code': item['symbol'],
                    'name': bk_keys.loc[
                        Utils.B2Tcode(item['symbol'])
                    ]['name'],
                    'percent': item['percent'],
                    'current_year_percent': item['current_year_percent'],
                    'site': "<a target=\"_blank\" href=\"" + "https://xueqiu.com/S/" + item['symbol'] + "\">" + item[
                        'symbol'] + "</a>",
                }, ignore_index=True)
        Utils.saveCSVToCache(bk_table, 'today_stocks')

        print("今日涨幅前10:")
        head_table = bk_table[bk_table.percent > 0].sort_values('percent', ascending=False).head(
            headAndTail).reset_index()
        # head_table['site'] = head_table.apply(lambda x: "https://xueqiu.com/S/" + x.code, axis=1)
        # head_table['site'] = "https://xueqiu.com/S/" + head_table['code']
        print(head_table.loc[:, ['name', 'percent', 'site']])

        print("今日跌幅前10:")
        tail_table = bk_table[bk_table.percent < 0].sort_values('percent').head(
            headAndTail).reset_index()

        print(tail_table.loc[:, ['name', 'percent', 'site']])

        print("今年涨幅幅前10:")
        year_head_table = bk_table[bk_table.current_year_percent > 0].sort_values('current_year_percent',
                                                                                  ascending=False).head(
            headAndTail).reset_index()

        print(year_head_table.loc[:, ['name', 'current_year_percent', 'site']])

        print("今年跌幅前10:")
        year_tail_table = bk_table[bk_table.current_year_percent < 0].sort_values('current_year_percent').head(
            headAndTail).reset_index()
        print(year_tail_table.loc[:, ['name', 'current_year_percent', 'site']])

        return head_table, tail_table, year_head_table, year_tail_table

    @staticmethod
    def getCapitalAssort(ball):

        headAndTail = 20

        print("获取个股资金排行...")

        bk_keys = Utils.readFromCSV('stocks')
        bk_table = pd.DataFrame(columns=['code', 'name', 'percent'])

        for row in bk_keys.iterrows():
            code = Utils.T2Bcode(row[0])
            if code.startswith("SZ300"):
                name = row[1][1]
                print(code)
                data = ball.quotec(code)
                flows = ball.capital_assort(code)
                item = data['data'][0]
                flow = flows['data']
                bk_table = bk_table.append({
                    'code': code,
                    'name': name,
                    'percent': item['percent'],
                    'current_year_percent': item['current_year_percent'],
                    'buy_large': Utils.divFormat(flow['buy_large'], flow['buy_total']),
                    'sell_large': Utils.divFormat(flow['sell_large'], flow['sell_total']),
                    'large': Utils.divFormat(Utils.minusFormat(flow['buy_large'], flow['sell_large']),
                                             Utils.minusFormat(flow['buy_total'], flow['sell_total'])),
                    'medium': Utils.divFormat(Utils.minusFormat(flow['buy_medium'], flow['sell_medium']),
                                              Utils.minusFormat(flow['buy_total'], flow['sell_total'])),
                    'small': Utils.divFormat(Utils.minusFormat(flow['buy_small'], flow['sell_small']),
                                             Utils.minusFormat(flow['buy_total'], flow['sell_total'])),
                    '': Utils.divFormat(flow['sell_small'], flow['sell_total']),
                    'site': "<a target=\"_blank\" href=\"" + "https://xueqiu.com/S/" + code + "\">site</a>",
                }, ignore_index=True)

        Utils.saveCSVToCache(bk_table, 'today_flow')

        print("今日流入前20:")
        head_table = bk_table[bk_table.percent > 0].sort_values('large', ascending=False).head(
            headAndTail).reset_index()

        print("今日流出前10:")
        tail_table = bk_table[bk_table.percent < 0].sort_values('large').head(
            headAndTail).reset_index()

        print("今日流入前20:")
        head_table_layge = bk_table[bk_table.percent > 0].sort_values('buy_large', ascending=False).head(
            headAndTail).reset_index()

        print("今日流出前10:")
        tail_table_layge = bk_table[bk_table.percent < 0].sort_values('sell_large', ascending=False).head(
            headAndTail).reset_index()

        return head_table.loc[:, ['name', 'large', 'percent', 'current_year_percent', 'site']], \
               tail_table.loc[:, ['name', 'large', 'percent', 'current_year_percent', 'site']], \
               head_table_layge.loc[:, ['name', 'buy_large', 'percent', 'current_year_percent', 'site']], \
               tail_table_layge.loc[:, ['name', 'sell_large', 'percent', 'current_year_percent', 'site']]

    @staticmethod
    def getBKs(ball):

        groupLength = 100
        headAndTail = 10

        print("获取板块涨跌排行...")

        bk_keys = Utils.readFromCSV('bk')
        bk_table = pd.DataFrame(columns=['code', 'name', 'percent'])

        symbols = [
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
        ]

        group = 0
        count = 0

        for row in bk_keys.iterrows():
            if row[1]['stock_count'] > 0:  # 超过1个股票的板块
                if row[1]['region'] == "CN":  # 区域是CN
                    symbols[group] = symbols[group] + row[0] + ","
                    count = count + 1
                    if count >= groupLength:
                        # print(symbols[group])
                        group = group + 1
                        count = 0

        # print(json.dumps(data, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ':')))

        for i in range(0, group):
            data = ball.quotec(symbols[i])
            for item in data['data']:
                bk_table = bk_table.append({
                    'code': item['symbol'],
                    'name': bk_keys.loc[item['symbol']]['name'],
                    'percent': item['percent'],
                    'current_year_percent': item['current_year_percent'],
                    'site': "<a target=\"_blank\" href=\"" + "https://xueqiu.com/S/" + item['symbol'] + "\">" + item[
                        'symbol'] + "</a>",
                }, ignore_index=True)

        Utils.saveCSVToCache(bk_table, 'today_bk')

        print("今日涨幅前10:")
        head_table = bk_table[bk_table.percent > 0].sort_values('percent', ascending=False).head(
            headAndTail).reset_index()
        print(head_table.loc[:, ['name', 'percent', 'site']])

        print("今日跌幅前10:")
        tail_table = bk_table[bk_table.percent < 0].sort_values('percent').head(
            headAndTail).reset_index()
        print(tail_table.loc[:, ['name', 'percent', 'site']])

        print("今年涨幅幅前10:")
        year_head_table = bk_table[bk_table.current_year_percent > 0].sort_values('current_year_percent',
                                                                                  ascending=False).head(
            headAndTail).reset_index()
        print(year_head_table.loc[:, ['name', 'current_year_percent', 'site']])

        print("今年跌幅前10:")
        year_tail_table = bk_table[bk_table.current_year_percent < 0].sort_values('current_year_percent').head(
            headAndTail).reset_index()
        print(year_tail_table.loc[:, ['name', 'current_year_percent', 'site']])

        return head_table, tail_table, year_head_table, year_tail_table

    def get_url(qType, pages=0, code=""):

        date = time.strftime("%Y-%m-%d", time.localtime())
        url_list = []
        for page in range(0, pages + 1):
            if code == "":
                url = f"https://reportapi.eastmoney.com/report/jg?cb=datatable6176985&pageSize=300&beginTime={date}&endTime={date}8&pageNo={page}&fields=&qType={qType}&code={code}"
                url_list.append(url)
            else:
                url = f"https://reportapi.eastmoney.com/report/list?pageSize=30&beginTime={date}&endTime={date}8&pageNo={page}&fields=&qType={qType}&code={code}&fields=encodeUrl,title"
                url_list.append(url)

        return url_list

    def get_report(url_list, type=1):  # type0是个股，type1是行业，3是宏观
        '''
        获取东方财富网宏观研报表格信息
        url_list是指宏观研报链接
        '''

        date = time.strftime("%Y-%m-%d", time.localtime())

        dict = {
            0: '个股',
            1: "行业",
            3: "宏观",
        }

        typeStr = dict[type]
        if not os.path.exists(C.REPORT_PATH):
            os.mkdir(C.REPORT_PATH)

        if not os.path.exists(C.REPORT_PATH + f"{date}-{typeStr}/"):
            os.mkdir(C.REPORT_PATH + f"{date}-{typeStr}/")

        index = 2

        for k in range(len(url_list)):
            url = url_list[k]
            res = requests.get(url)
            res_text = res.text
            if type == 1 or type == 3:
                res_text = res_text[17:-1]

            res_js = json.loads(res_text)
            for i in range(len(res_js["data"])):
                index += 1

                fileName = res_js["data"][i]["title"].replace('/', u"\u2215")

                # if type == 0:  # 个股文件名单独处理
                #     fileName = "" + fileName

                file_full_name = C.REPORT_PATH + f"{date}-{typeStr}/{fileName}.pdf"

                if not os.path.exists(file_full_name):
                    print(fileName)
                    pdfUrl = f"https://data.eastmoney.com/report/zw_macresearch.jshtml?encodeUrl={res_js['data'][i]['encodeUrl']}"
                    res = requests.get(pdfUrl)
                    soup = BeautifulSoup(res.text, "html.parser")
                    pdf_link = soup.select(".pdf-link")[0]["href"]
                    # pdf_link = pdf_link[:pdf_link.find("?")]
                    res_pdf = requests.get(pdf_link)

                    with open(file_full_name, "wb") as fp:
                        for chunk in res_pdf.iter_content(chunk_size=1024):
                            if chunk:
                                fp.write(chunk)
                else:
                    print("pass " + fileName)

            # sleep(random.uniform(1, 2))
