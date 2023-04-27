import json
import os
import random
import time
from datetime import timedelta, datetime
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

        date = time.strftime("%Y-%m-%d", time.localtime())

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

        if False:  # test code
            bk_table = Utils.readCSVFromCache('today_stocks_' + date)
        else:
            for i in range(0, group + 1):
                data = ball.quotec(symbols[i])
                for item in data['data']:
                    bk_table = bk_table.append({
                        'code': item['symbol'],
                        'name': "<a target=\"_blank\" href=\"" + "https://xueqiu.com/S/" + item['symbol'] + "\">" +
                                bk_keys.loc[Utils.B2Tcode(item['symbol'])]['name'] + "</a>",
                        'amount': item['amount'],
                        'percent': item['percent'],
                        'current_year_percent': item['current_year_percent'],
                    }, ignore_index=True)
            Utils.saveCSVToCache(bk_table, 'today_stocks_' + date)

        # 排除ST
        bk_table = bk_table[~(bk_table.name.str.contains('ST'))]

        print("今日涨幅前10")
        head_table = bk_table[bk_table.percent > 0].sort_values('percent', ascending=False).head(
            headAndTail).reset_index()
        # head_table['site'] = head_table.apply(lambda x: "https://xueqiu.com/S/" + x.code, axis=1)
        # head_table['site'] = "https://xueqiu.com/S/" + head_table['code']
        head_table = head_table.loc[:, ['name', 'percent', 'current_year_percent']]

        print("今日跌幅前10")
        tail_table = bk_table[bk_table.percent < 0].sort_values('percent').head(
            headAndTail).reset_index()

        tail_table = tail_table.loc[:, ['name', 'percent', 'current_year_percent']]

        print("今日成交额前10")
        amount_head_table = bk_table[bk_table.amount > 0].sort_values('amount', ascending=False).head(
            headAndTail).reset_index()
        amount_head_table = amount_head_table.loc[:, ['name', 'amount', 'percent', 'current_year_percent']]

        print("今日成交额后10")
        amount_tail_table = bk_table[(bk_table.amount > 0)].sort_values('amount').reset_index()
        amount_tail_table = amount_tail_table[~(amount_tail_table['code'].str.contains('BJ'))].head(headAndTail)
        amount_tail_table = amount_tail_table.loc[:, ['name', 'amount', 'percent', 'current_year_percent']]

        print("今年涨幅幅前10")
        year_head_table = bk_table[bk_table.current_year_percent > 0].sort_values('current_year_percent',
                                                                                  ascending=False).head(
            headAndTail).reset_index()
        year_head_table = year_head_table.loc[:, ['name', 'percent', 'current_year_percent']]

        print("今年跌幅前10")
        year_tail_table = bk_table[bk_table.current_year_percent < 0].sort_values('current_year_percent').head(
            headAndTail).reset_index()
        year_tail_table = year_tail_table.loc[:, ['name', 'percent', 'current_year_percent']]

        return head_table, tail_table, amount_head_table, amount_tail_table, year_head_table, year_tail_table

    @staticmethod
    def getCapitalAssort(ball):

        date = time.strftime("%Y-%m-%d", time.localtime())

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
                    'name': "<a target=\"_blank\" href=\"" + "https://xueqiu.com/S/" + name + "\">site</a>",
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
                }, ignore_index=True)

        Utils.saveCSVToCache(bk_table, 'today_flow_' + date)

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

        return head_table.loc[:, ['name', 'large', 'percent', 'current_year_percent']], \
            tail_table.loc[:, ['name', 'large', 'percent', 'current_year_percent']], \
            head_table_layge.loc[:, ['name', 'buy_large', 'percent', 'current_year_percent']], \
            tail_table_layge.loc[:, ['name', 'sell_large', 'percent', 'current_year_percent']]

    @staticmethod
    def getBKs(ball):

        date = time.strftime("%Y-%m-%d", time.localtime())

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
                    'name': "<a target=\"_blank\" href=\"" + "https://xueqiu.com/S/" + item['symbol'] + "\">" +
                            bk_keys.loc[item['symbol']]['name'] + "</a>",
                    'percent': item['percent'],
                    'current_year_percent': item['current_year_percent'],
                }, ignore_index=True)

        print("今日涨幅前10板块")
        head_table = bk_table[bk_table.percent > 0].sort_values('percent', ascending=False).head(
            headAndTail).reset_index()
        head_table = head_table.loc[:, ['name', 'percent', 'current_year_percent']]

        print("今日跌幅前10板块")
        tail_table = bk_table[bk_table.percent < 0].sort_values('percent').head(
            headAndTail).reset_index()
        tail_table = tail_table.loc[:, ['name', 'percent', 'current_year_percent']]

        print("今年涨幅幅前10板块")
        year_head_table = bk_table[bk_table.current_year_percent > 0].sort_values('current_year_percent',
                                                                                  ascending=False).head(
            headAndTail).reset_index()
        year_head_table = year_head_table.loc[:, ['name', 'percent', 'current_year_percent']]

        print("今年跌幅前10板块")
        year_tail_table = bk_table[bk_table.current_year_percent < 0].sort_values('current_year_percent').head(
            headAndTail).reset_index()
        year_tail_table = year_tail_table.loc[:, ['name', 'percent', 'current_year_percent']]

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

    def get_report(url_list, type=1, keyword=None):  # type0是个股，type1是行业，3是宏观
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

            if res_text.startswith('datatable'):
                res_text = re.sub('datatable\d+\\(', '', res_text)[:-1]

            res_js = json.loads(res_text)
            for i in range(len(res_js["data"])):
                index += 1

                fileName = res_js["data"][i]["title"].replace('/', u"\u2215")

                if keyword is not None and not any(word in fileName for word in keyword):
                    continue

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
                    pass
                    # print("pass " + fileName)

            # sleep(random.uniform(1, 2))

    @staticmethod
    def getFReport():
        headers = {
            'Host': 'datacenter-web.eastmoney.com',
            'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"macOS"',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Dest': 'script',
            'Referer': 'https://data.eastmoney.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cookie': 'qgqp_b_id=3997baaa71fb9a0d03b20110481eb575; HAList=ty-100-RTS-%u4FC4%u7F57%u65AFRTS; st_si=68922960107662; st_asi=delete; JSESSIONID=036ED8B200088541963AC0A51CEBF105; st_pvi=60029143568755; st_sp=2019-10-10%2011%3A05%3A42; st_inirUrl=https%3A%2F%2Fwww.google.com%2F; st_sn=8; st_psi=20230427094251587-113300301069-5338659879'
        }

        params = {
            'callback': 'jQuery112306298208397781508_1682559797537',
            'sortColumns': 'FIRST_APPOINT_DATE,SECURITY_CODE',
            'sortTypes': '1,1',
            'pageSize': '5000',
            'pageNumber': '1',
            'reportName': 'RPT_PUBLIC_BS_APPOIN',
            'columns': 'ALL',
            'filter': '(SECURITY_TYPE_CODE in ("058001001","058001008"))(TRADE_MARKET_CODE!="069001017")(REPORT_DATE=\'2023-03-31\')'
        }

        response = requests.get('https://datacenter-web.eastmoney.com/api/data/v1/get', headers=headers, params=params)
        json_str = re.search(r'\{.*\}', response.text).group()

        # 解析JSON
        jsonBean = json.loads(json_str)

        result = []
        for item in jsonBean['result']['data']:
            time_str = ''
            if item['THIRD_CHANGE_DATE'] is not None:
                time_str = item['THIRD_CHANGE_DATE']
            elif item['SECOND_CHANGE_DATE'] is not None:
                time_str = item['SECOND_CHANGE_DATE']
            elif item['FIRST_CHANGE_DATE'] is not None:
                time_str = item['FIRST_CHANGE_DATE']
            else:
                time_str = item['FIRST_APPOINT_DATE']

            # 将time_str转换为datetime对象
            time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

            # 将日期增加一天
            tomorrow_obj = datetime.now() + timedelta(days=1)

            # 判断日期是否为明天
            if tomorrow_obj.date() == time_obj.date():
                # print(item['SECURITY_NAME_ABBR'] + ' ' + time_str)
                result.append(item['SECUCODE'])
                # print(item['SECUCODE'])
            else:
                # print(item['SECURITY_NAME_ABBR'] + ' ' + time_str)
                pass
        return result

    @staticmethod
    def getStocksTable(ball, codes):
        bk_keys = Utils.readFromCSV('stocks')
        resultTable = pd.DataFrame(columns=['name', 'amount', 'percent', 'current_year_percent'])

        for code in codes:
            data = ball.quotec(Utils.T2Bcode(code))
            for item in data['data']:
                resultTable = resultTable.append({
                    'name': "<a target=\"_blank\" href=\"" + "https://xueqiu.com/S/" + item['symbol'] + "\">" +
                            bk_keys.loc[Utils.B2Tcode(item['symbol'])]['name'] + "</a>",
                    'amount': item['amount'],
                    'percent': item['percent'],
                    'current_year_percent': item['current_year_percent'],
                }, ignore_index=True)

        return resultTable
