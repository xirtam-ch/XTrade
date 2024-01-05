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
                bk_table = pd.concat([bk_table if not bk_table.empty else None, tmp_data], ignore_index=True)

            Utils.saveToCSV(bk_table, 'bk')
        print('BKs updated')
