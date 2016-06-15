# encoding: UTF-8
import re
import datetime

# string 工具集合


def parse_date(str=''):
    """
    parse srting to date
    1 '2004' -> 2004-01-01
    2 '2015-12' -> 2015-12-01
    3 '2015-09-02' -> 2015-09-02
    :param str:
    :return:
    """
    y_p = re.compile(r'^\d{4}$')
    ym_p = re.compile(r'^\d{4}-\d{2}$')
    ymd_p = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    if str is None:
        return None

    try:

        if y_p.match(str):
            date = datetime.datetime.strptime(str, "%Y").date()
        elif ym_p.match(str):
            date = datetime.datetime.strptime(str, "%Y-%m").date()
        elif ymd_p.match(str):
            date = datetime.datetime.strptime(str, "%Y-%m-%d").date()
        else:
            date = None
    except:
        date = None
    return date

# print parse_date('2015')
# print parse_date('2015-09')
# print parse_date('2015-09-02')
