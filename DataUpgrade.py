import os

import pandas as pd

from C import C
from Utils import Utils
from pysnowball import utls
import time


class DataUpgrade:

    @staticmethod
    def updateStocks(pro):
        data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        Utils.saveToCSV(data, "stocks")
        print('stocks updated')

    @staticmethod
    def update_week_k_line():
        if not os.path.exists(C.WEEK_KLINE_PATH):
            os.mkdir(C.WEEK_KLINE_PATH)

        date = time.strftime("%Y-%m-%d", time.localtime())
        url = "https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol={}&begin={}&period=week&type=before&count=-{}&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"
        all_stock_keys = Utils.readFromCSV('stocks')
        remove_bj = all_stock_keys[~all_stock_keys.index.str.contains('BJ')]  # 排除北郊所，减少请求次数
        stock_keys = remove_bj[~(remove_bj.name.str.contains('ST'))]  # 排除ST股，减少请求次数

        count = 1
        for row in stock_keys.iterrows():
            if os.path.exists(os.path.join(C.WEEK_KLINE_PATH + f'{Utils.T2Bcode(row[0])}_{date}' + '.csv')):
                print(f'{Utils.T2Bcode(row[0])} 使用缓存')
                count = count + 1
                continue

            bk_table = pd.DataFrame(
                columns=['timestamp', 'volume', 'open', 'high', 'low', 'close', 'percent', 'turnoverrate', 'amount',
                         'market_capital'])

            code = Utils.T2Bcode(row[0])
            result = utls.fetch(url.format(code, int(time.time() * 1000), 200))  # 200周k线

            for item in result['data']['item']:
                timestamp = item[0]
                volume = item[1]
                open = item[2]
                high = item[3]
                low = item[4]
                close = item[5]
                percent = item[7]
                turnoverrate = item[8]  # 换手率
                amount = item[9]
                market_capital = item[16]

                tmp_data = pd.DataFrame([{
                    'timestamp': str(timestamp),
                    # 'code': Utils.T2Bcode(row[0]),
                    # 'name': stock_keys.loc[row[0]]['name'],
                    'volume': str(volume),
                    'open': str(open),
                    'high': str(high),
                    'low': str(low),
                    'close': str(close),
                    'percent': str(percent),
                    'turnoverrate': str(turnoverrate),
                    'amount': str(amount),
                    'market_capital': str(market_capital)
                }])
                bk_table = pd.concat([bk_table, tmp_data], ignore_index=True)

            bk_table.to_csv(os.path.join(C.WEEK_KLINE_PATH + f'{Utils.T2Bcode(row[0])}_{date}' + '.csv'), index=False)
            # 进度条
            print(f'{round(count / stock_keys.shape[0] * 100, 2)}%, {row[0]}')
            count = count + 1

    @staticmethod
    def updateBK(ball):

        bk_path = os.path.join(os.getcwd(), 'data/bk.csv')
        bk_old_path = os.path.join(os.getcwd(), 'data/bk_old.csv')
        if os.path.exists(bk_path):
            if os.path.exists(bk_old_path):
                os.remove(bk_old_path)
            os.rename(
                bk_path,
                bk_old_path
            )

        bk_table = pd.DataFrame(columns=['code', 'name', 'price', 'date', 'stock_count', 'market_capital', 'region'])

        # 1xxx是US  2xxx是HK，国内bk目前只有999以下
        for i in range(1, 999):

            code = 'BK' + str(i).zfill(4)

            bk = ball.quote_detail(code)
            quote = bk['data']['quote']
            market = bk['data']['market']
            print(str(round(i / 1000 * 100, 2)) + '%')
            if quote:
                # print(json.dumps(bk, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ':')))
                tmp_data = pd.DataFrame([{
                    'code': code,
                    'name': quote['name'],
                    'price': quote['current'],
                    'date': quote['time'],
                    'stock_count': str(
                        int(quote['fall_count'] or 0) + int(quote['flat_count'] or 0) + int(quote['rise_count'] or 0)),
                    'market_capital': quote['market_capital'],
                    'region': market['region'],
                }])
                bk_table = pd.concat([bk_table, tmp_data], ignore_index=True)

            Utils.saveToCSV(bk_table, 'bk')
        print('BKs updated')
