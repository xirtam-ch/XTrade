import sys
import time
from configparser import ConfigParser

import pysnowball as ball
import tushare as ts

from Utils import Utils

if __name__ == '__main__':
    config = ConfigParser()
    config.read('token.config')

    ball.set_token(config.get('token', 'xueqiu'))
    pro = ts.pro_api(config.get('token', 'tushare'))

    date = time.strftime("%Y-%m-%d", time.localtime())

    print("### 股东人数")
    print(Utils.B2TcodeWithColon(sys.argv[1]))
    print(pro.stk_holdernumber(ts_code=Utils.B2TcodeWithColon(sys.argv[1]), start_date='20200101', end_date=date))
