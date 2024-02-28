import json
import os
import re
import time
from datetime import timedelta, datetime

import baostock as bs
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pysnowball import utls

from C import C
from Utils import Utils


class AnalyzeData:

    @staticmethod
    def get_weeks_low_vol(weeks=30):
        date = time.strftime("%Y-%m-%d", time.localtime())

        # if os.path.exists(os.path.join(C.CACHE_PATH + 'get_weeks_low_vol_' + date + '.csv')):
        #     print(f'get_last_week_activity_index 使用缓存')
        #     return Utils.readCSVFromCache('get_weeks_low_vol_' + date)

        url = "https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={}&begin={}&period=week&type=before&count=-{}&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"
        all_stock_keys = Utils.readFromCSV('stocks')
        remove_bj = all_stock_keys[~all_stock_keys.index.str.contains('BJ')]  # 排除北郊所，减少请求次数
        stock_keys = remove_bj[~(remove_bj.name.str.contains('ST'))]  # 排除ST股，减少请求次数

        # 制表保存
        bk_table = pd.DataFrame(columns=['code', 'name', 'last_week_amount', 'indicator', 'last_week_percent', 'price'])

        count = 1
        MAX_WEEK_COUNT = weeks
        for row in stock_keys.iterrows():
            code = Utils.T2Bcode(row[0])
            result = utls.fetch(url.format(code, int(time.time() * 1000), MAX_WEEK_COUNT))

            # ['timestamp', 'volume', 'open', 'high', 'low',
            # 'close', 'chg', 'percent', 'turnoverrate', 'amount',
            # 'volume_post', 'amount_post', 'pe', 'pb', 'ps',
            # 'pcf', 'market_capital', 'balance', 'hold_volume_cn', 'hold_ratio_cn',
            # 'net_volume_cn', 'hold_volume_hk', 'hold_ratio_hk', 'net_volume_hk']

            if result['data'] == {}:
                print(f'{Utils.T2Bcode(row[0])} 没有数据')
                count = count + 1
                continue

            if len(result['data']['item']) < MAX_WEEK_COUNT:  # 次新股排除
                print(f'{code} 次新股排除')
                continue

            market_capital = result['data']['item'][4][16]

            if market_capital is None:  # 获取不到市值
                print(f'{code} 获取不到市值')
            else:
                filter_30_percent = 30
                filter_10_percent = filter_30_percent / 3
                filter_5_percent = filter_30_percent / 6
                filter_3_percent = filter_30_percent / 10

                this_week_vol = result['data']['item'][weeks - 1][1]

                sum_30 = 0
                sum_10 = 0
                sum_5 = 0
                sum_3 = 0

                min8 = 2099999999

                for i in range(0, weeks):
                    if i >= weeks - 3:
                        sum_3 = sum_3 + result['data']['item'][i][1]
                    if i >= weeks - 5:
                        sum_5 = sum_5 + result['data']['item'][i][1]
                    if i >= weeks - 10:
                        sum_10 = sum_10 + result['data']['item'][i][1]
                    if i >= weeks - 30:
                        sum_30 = sum_30 + result['data']['item'][i][1]
                    if i < weeks - 1:
                        if result['data']['item'][i][1] < min8:
                            min8 = result['data']['item'][i][1]
                # 计算指标
                # if this_week_vol / sum_30 < 1 / filter_30_percent:
                #     if this_week_vol / sum_10 < 1 / filter_10_percent:
                #         if this_week_vol / sum_5 < 1 / filter_5_percent:
                #             if this_week_vol / sum_3 < 1 / filter_3_percent:
                indicator = this_week_vol / min8
                if indicator < 1:
                    tmp_data = pd.DataFrame([{
                        'code': Utils.T2Bcode(row[0]),
                        'name': stock_keys.loc[row[0]]['name'],
                        'indicator': str(indicator),
                        'market_capital': str(market_capital),
                        'vol': this_week_vol
                    }])
                    bk_table = pd.concat([bk_table if not bk_table.empty else None, tmp_data],
                                         ignore_index=True)
                # 进度条
                print(f'{round(count / stock_keys.shape[0] * 100, 2)}%, {row[0]}')
            count = count + 1

        Utils.saveCSVToCache(bk_table, 'get_weeks_low_vol_' + date)
        return bk_table

    @staticmethod
    def get_last_week_activity_index():
        date = time.strftime("%Y-%m-%d", time.localtime())

        if os.path.exists(os.path.join(C.CACHE_PATH + 'last_week_activity_' + date + '.csv')):
            print(f'get_last_week_activity_index 使用缓存')
            return Utils.readCSVFromCache('last_week_activity_' + date)

        url = "https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={}&begin={}&period=week&type=before&count=-{}&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"
        all_stock_keys = Utils.readFromCSV('stocks')
        remove_bj = all_stock_keys[~all_stock_keys.index.str.contains('BJ')]  # 排除北郊所，减少请求次数
        stock_keys = remove_bj[~(remove_bj.name.str.contains('ST'))]  # 排除ST股，减少请求次数

        # 制表保存
        bk_table = pd.DataFrame(columns=['code', 'name', 'last_week_amount', 'indicator', 'last_week_percent', 'price'])

        count = 1
        MAX_WEEK_COUNT = 5
        # try:
        for row in stock_keys.iterrows():
            code = Utils.T2Bcode(row[0])
            result = utls.fetch(url.format(code, int(time.time() * 1000), MAX_WEEK_COUNT))

            # ['timestamp', 'volume', 'open', 'high', 'low',
            # 'close', 'chg', 'percent', 'turnoverrate', 'amount',
            # 'volume_post', 'amount_post', 'pe', 'pb', 'ps',
            # 'pcf', 'market_capital', 'balance', 'hold_volume_cn', 'hold_ratio_cn',
            # 'net_volume_cn', 'hold_volume_hk', 'hold_ratio_hk', 'net_volume_hk']

            if len(result['data']['item']) < MAX_WEEK_COUNT:  # 次新股排除
                print(f'{code} 次新股排除')
                continue

            market_capital = result['data']['item'][4][16]

            if market_capital is None:  # 获取不到市值
                print(f'{code} 获取不到市值')
            elif market_capital < 5000000000:  # 市值小于50亿
                print(f'{code} 市值小于50亿')
                # indicator = -1
                # print(f'{round(count / stock_keys.shape[0] * 100, 2)}%, {row[0]}，新股无法计算')
                # tmp_data = pd.DataFrame([{
                #     'code': Utils.T2Bcode(row[0]),
                #     'name': stock_keys.loc[row[0]]['name'],
                #     'last_week_amount': -1,
                #     'indicator': str(indicator),
                #     'last_week_percent': -1,
                #     'price': -1,
                # }])
                # bk_table = pd.concat([bk_table if not bk_table.empty else None, tmp_data], ignore_index=True)
            else:
                item_0_amount = result['data']['item'][0][9]
                item_1_amount = result['data']['item'][1][9]
                item_2_amount = result['data']['item'][2][9]
                item_3_amount = result['data']['item'][3][9]  # 上周的
                item_4_amount = result['data']['item'][4][9]  # 本周的

                execWeekData = result['data']['item'][3]
                if datetime.now().weekday() >= 4:  # 周五以后使用本周数据作为最后一周，周五以前使用上周数据作为最后一周
                    execWeekData = result['data']['item'][4]

                # maxAmount = max(item_0_amount, item_1_amount, item_2_amount, item_3_amount, item_4_amount) #取过去5周最大成交量
                maxAmount = execWeekData[9]  # 取最后一周成交量
                avgAmount = (item_0_amount + item_1_amount + item_2_amount + item_3_amount + item_4_amount) \
                            / MAX_WEEK_COUNT
                minAmout = min(item_0_amount, item_1_amount, item_2_amount, item_3_amount, item_4_amount)

                # 计算上影线长度 (high - close - (open - low)) / (close - open)
                upper_shadow_line = 0
                if (execWeekData[5] - execWeekData[2]) > 0:  # 最后一周是上涨的
                    upper_shadow_line = ((execWeekData[3] - execWeekData[5]) -
                                         (execWeekData[2] - execWeekData[4])) \
                                        / (execWeekData[5] - execWeekData[2])

                amount_indicator = 0
                if avgAmount > 600000000:  # 平均成交额大于8亿
                    amount_indicator = maxAmount / avgAmount

                # 计算指标
                indicator = upper_shadow_line

                # 进度条
                print(f'{round(count / stock_keys.shape[0] * 100, 2)}%, {row[0]}')

                tmp_data = pd.DataFrame([{
                    'code': Utils.T2Bcode(row[0]),
                    'name': stock_keys.loc[row[0]]['name'],
                    'last_week_amount': execWeekData[9],
                    'indicator': str(indicator),
                    'last_week_percent': execWeekData[7],
                    'market_capital': str(market_capital),
                    'price': result['data']['item'][4][5]  # 最新价格始终使用最后一周的
                }])
                bk_table = pd.concat([bk_table if not bk_table.empty else None, tmp_data], ignore_index=True)
            count = count + 1
        # except Exception as e:
        #     print(f"出现异常: {e}")

        Utils.saveCSVToCache(bk_table, 'last_week_activity_' + date)
        return bk_table

    @staticmethod
    def get_days_kline(symbol, days):
        data = []
        url = "https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={}&begin={}&period=day&type=before&count=-{}&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"
        result = utls.fetch(url.format(symbol, int(time.time() * 1000), days))
        if result['data'] == {} or result['data']['item'] == {} or len(result['data']['item']) < days:
            return []
        else:

            for i in range(0, days):
                item = {'open': (result['data']['item'][i][2],), 'high': (result['data']['item'][i][3],),
                        'low': (result['data']['item'][i][4],), 'close': (result['data']['item'][i][5],),
                        'amount': (result['data']['item'][i][9],), 'percent': (result['data']['item'][i][7],),
                        'market_capital': (result['data']['item'][i][16],)}
                data.append(item)
        return data  # r[0]['open'][0]

    @staticmethod
    def get_days_kline_all_stocks():
        date = time.strftime("%Y-%m-%d", time.localtime())

        if os.path.exists(os.path.join(C.CACHE_PATH + 'days_kline_' + date + '.csv')):
            print(f'get_last_day_percent 使用缓存')
            return Utils.readCSVFromCache('days_kline_' + date)

        url = "https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={}&begin={}&period=day&type=before&count=-{}&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"
        all_stock_keys = Utils.readFromCSV('stocks')  # stocks_test
        remove_bj = all_stock_keys[~all_stock_keys.index.str.contains('BJ')]  # 排除北郊所，减少请求次数
        remove_st = remove_bj[~(remove_bj.name.str.contains('ST'))]  # 排除ST股，减少请求次数

        remove_st.loc[:, 'list_date'] = pd.to_datetime(remove_st['list_date'], format='%Y%m%d')  # 排除上市不足一年
        one_year_ago = pd.Timestamp(date) - pd.DateOffset(years=1)
        filter_one_year = remove_st['list_date'] <= one_year_ago
        stock_keys = remove_st.loc[filter_one_year]

        # 制表保存
        bk_table = pd.DataFrame()

        count = 1
        MAX_DAYS_COUNT = 3
        # try:
        for row in stock_keys.iterrows():
            code = Utils.T2Bcode(row[0])
            result = utls.fetch(url.format(code, int(time.time() * 1000), MAX_DAYS_COUNT))

            # ['timestamp', 'volume', 'open', 'high', 'low',
            # 'close', 'chg', 'percent', 'turnoverrate', 'amount',
            # 'volume_post', 'amount_post', 'pe', 'pb', 'ps',
            # 'pcf', 'market_capital', 'balance', 'hold_volume_cn', 'hold_ratio_cn',
            # 'net_volume_cn', 'hold_volume_hk', 'hold_ratio_hk', 'net_volume_hk']

            if result['data'] == {} or result['data']['item'] == {} or len(result['data']['item']) < 2:
                print(f'{Utils.T2Bcode(row[0])} 没有数据')
                count = count + 1
                continue

            today_data = result['data']['item'][2]
            yestday_data = result['data']['item'][1]
            last2day_data = result['data']['item'][0]
            # 进度条
            print(f'{round(count / stock_keys.shape[0] * 100, 2)}%, {row[0]}')

            tmp_data = pd.DataFrame([{
                'code': Utils.T2Bcode(row[0]),
                'name': stock_keys.loc[row[0]]['name'],
                'last_open': yestday_data[2],
                'last_high': yestday_data[3],
                'last_low': yestday_data[4],
                'last_close': yestday_data[5],
                'last_amount': yestday_data[9],
                'last_percent': yestday_data[7],
                'last2_open': last2day_data[2],
                'last2_high': last2day_data[3],
                'last2_low': last2day_data[4],
                'last2_close': last2day_data[5],
                'last2_amount': last2day_data[9],
                'last2_percent': last2day_data[7],
                'open': today_data[2],
                'high': today_data[3],
                'low': today_data[4],
                'close': today_data[5],
                'amount': today_data[9],
                'percent': today_data[7],
                'market_capital': today_data[16]
            }])
            bk_table = pd.concat([bk_table, tmp_data], ignore_index=True)
            count = count + 1

        Utils.saveCSVToCache(bk_table, 'days_kline_' + date)
        return bk_table

    @staticmethod
    def getWeekPercentBySymbols(symbols):
        result_list = []
        url = "https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={}&begin={}&period=week&type=before&count=-{}&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"

        for code in symbols:
            data = utls.fetch(url.format(code, int(time.time() * 1000), 1))
            result_list.append(data['data']['item'][0][7])
        return result_list

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
                    tmp_data = pd.DataFrame([{
                        'code': item['symbol'],
                        'name': "<a target=\"_blank\" href=\"" + "https://xueqiu.com/S/" + item['symbol'] + "\">" +
                                bk_keys.loc[Utils.B2Tcode(item['symbol'])]['name'] + "</a>",
                        'amount': item['amount'],
                        'percent': item['percent'],
                        'current_year_percent': item['current_year_percent'],
                    }])
                    bk_table = pd.concat([bk_table if not bk_table.empty else None, tmp_data], ignore_index=True)
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
                tmp_data = pd.DataFrame([{
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
                }])
                bk_table = pd.concat([bk_table if not bk_table.empty else None, tmp_data], ignore_index=True)

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
                tmp_data = pd.DataFrame([{
                    'code': item['symbol'],
                    'name': "<a target=\"_blank\" href=\"" + "https://xueqiu.com/S/" + item['symbol'] + "\">" +
                            bk_keys.loc[item['symbol']]['name'] + "</a>",
                    'percent': item['percent'],
                    'current_year_percent': item['current_year_percent'],
                }])
                bk_table = pd.concat([bk_table if not bk_table.empty else None, tmp_data], ignore_index=True)

        Utils.saveCSVToCache(bk_table, 'today_bks_' + date)

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
        if jsonBean['result'] is not None:
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
                tmp_data = pd.DataFrame([{
                    'name': "<a target=\"_blank\" href=\"" + "https://xueqiu.com/S/" + item['symbol'] + "\">" +
                            bk_keys.loc[Utils.B2Tcode(item['symbol'])]['name'] + "</a>",
                    'amount': item['amount'],
                    'percent': item['percent'],
                    'current_year_percent': item['current_year_percent'],
                }])
                bk_table = pd.concat([bk_table if not bk_table.empty else None, tmp_data], ignore_index=True)

        return resultTable

    @staticmethod
    def getChart():
        # 登录baostock
        bs.login()

        # 获取股票从5月1日到5月10日的5分钟数据
        rs = bs.query_history_k_data_plus("sh.600749",
                                          "date,time,open,high,low,close,volume",
                                          start_date="2023-04-01", end_date="2333-12-31",
                                          frequency="5",
                                          adjustflag="3")

        # 将获取到的数据转换为DataFrame格式
        data_list = []
        while (rs.error_code == '0') & rs.next():
            row_data = rs.get_row_data()
            data_list.append(row_data)
        df = pd.DataFrame(data_list, columns=rs.fields)

        # 检查数据中是否存在缺失值或非数值的数据
        if df.isnull().values.any():
            print("Warning: The data contains missing values!")
        if not pd.to_numeric(df["volume"], errors="coerce").notnull().all() \
                or not pd.to_numeric(df["close"], errors="coerce").notnull().all():
            print("Warning: The data contains non-numeric values!")

        # 对数据进行类型转换
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
        df["close"] = pd.to_numeric(df["close"], errors="coerce")

        total_amount = df.groupby("date")["volume"].sum()
        # 计算每天的第2到6条5分钟数据的总成交额
        df["cum_volume"] = df.groupby("date")["volume"].cumsum()
        df["cum_count"] = df.groupby("date")["date"].cumcount() + 1
        df = df.loc[df["cum_count"].isin([1, 2, 3])]

        # 计算每天的总成交额，并计算指标X

        # print(f'total_amount {total_amount}')
        cum_amount = df.groupby("date")["volume"].sum()
        X = cum_amount / total_amount

        # 保存指标X到新的表格
        df_new = pd.DataFrame({
            "date": X.index,
            "X": X.values,
            "cum_amount": cum_amount.values,
            "total_amount": total_amount.values
        })
        # df_new.to_csv("X.csv", index=False)

        # 关闭baostock
        bs.logout()
        return df_new
