import os


class C:
    REPORT_PATH = os.path.join(os.getcwd(), 'reports/')
    DATA_PATH = os.path.join(os.getcwd(), 'data/')
    CACHE_PATH = os.path.join(os.getcwd(), 'cache/')
    WEEK_KLINE_PATH = os.path.join(os.getcwd(), 'wkline/')
    XLS_OUTPUT_PATH = os.path.expanduser("~") + '/Downloads/'
