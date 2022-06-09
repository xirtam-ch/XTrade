# coding: utf-8
import os

import numpy as np
import pandas as pd
import time

from C import C


class Utils:

    @staticmethod
    def T2Bcode(code):
        return code.split(".")[1] + code.split(".")[0]

    @staticmethod
    def divFormat(num1, num2):
        if num1 is None or num2 is None or num2 == 0:
            return 0
        return round(num1 / num2, 2)

    @staticmethod
    def minusFormat(num1, num2):
        if num1 is None:
            num1 = 0
        if num2 is None:
            num2 = 0
        return num1 - num2

    @staticmethod
    def B2Tcode(code):
        return code[2:8] + "." + code[:2]

    @staticmethod
    def saveToCSV(df, path, index=False):
        df.to_csv(os.path.join(C.DATA_PATH + path + '.csv'), index=index)

    @staticmethod
    def readFromCSV(path):
        result = None
        if os.path.exists(os.path.join(C.DATA_PATH + path + '.csv')):
            result = pd.read_csv(os.path.join(C.DATA_PATH + path + '.csv'), index_col=0, encoding="utf-8")
        return result

    @staticmethod
    def saveCSVToCache(df, path, index=False):
        df.to_csv(os.path.join(C.CACHE_PATH + path + '.csv'), index=index)

    @staticmethod
    def readCSVFromCache(path):
        result = None
        if os.path.exists(os.path.join(C.CACHE_PATH + path + '.csv')):
            result = pd.read_csv(os.path.join(C.CACHE_PATH + path + '.csv'), index_col=0, encoding="utf-8")
        return result

    @staticmethod
    def saveArrayToCache(data, path):
        np.save(os.path.join(C.CACHE_PATH + path + '.npy'), data, allow_pickle=True, fix_imports=True)

    @staticmethod
    def timeTag(startT, tag):
        if True:
            print(tag, time.time() - startT)

    @staticmethod
    def readArrayFromCache(path):
        result = None
        if os.path.exists(os.path.join(C.CACHE_PATH + path + '.npy')):
            result = np.load(os.path.join(C.CACHE_PATH + path + '.npy'), mmap_mode=None, allow_pickle=True,
                             fix_imports=True,
                             encoding='ASCII')
        return result

    @staticmethod
    def str_of_num(num):
        def strofsize(num, level):
            if level >= 2:
                return num, level
            elif num >= 10000:
                num /= 10000
                level += 1
                return strofsize(num, level)
            else:
                return num, level

        units = ['', '万', '亿']
        num, level = strofsize(num, 0)
        if level > len(units):
            level -= 1
        return '{}{}'.format(round(num, 3), units[level])
