import os

import pandas as pd

from Utils import Utils


class DataUpgrade:

    @staticmethod
    def updateStocks(pro):
        data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
        Utils.saveToCSV(data, "stocks")
        print('stocks updated')

    @staticmethod
    def updateBK(ball):

        # os.rename(
        #     os.path.join(os.getcwd(), 'data/bk.csv'),
        #     os.path.join(os.getcwd(), 'data/bk_old.csv')
        # )

        bk_table = pd.DataFrame(columns=['code', 'name', 'price', 'date', 'stock_count', 'market_capital', 'region'])

        for i in range(1, 9999):

            code = 'BK' + str(i).zfill(4)

            bk = ball.quote_detail(code)
            quote = bk['data']['quote']
            market = bk['data']['market']
            if quote:
                print(code)
                # print(json.dumps(bk, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ':')))
                bk_table = bk_table.append({
                    'code': code,
                    'name': quote['name'],
                    'price': quote['current'],
                    'date': quote['time'],
                    'stock_count': str(int(quote['fall_count'] or 0) + int(quote['flat_count'] or 0)),
                    'market_capital': quote['market_capital'],
                    'region': market['region'],
                }, ignore_index=True)
            Utils.saveToCSV(bk_table, 'bk')
        print('BKs updated')