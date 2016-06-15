# encoding: UTF-8
import re
import random
import string

# string 工具集合

def trim_query_str_lucene(str=''):
    str = str.encode('utf-8')
    escape_str = '+-&&||!(){}[]^"~*?:\/'
    for s in escape_str:
        str = str.replace(s, '\\' + s)
    return str


# print trim_query_str_lucene('(1+1):2')

def trim_version(str=''):
    """
    去除 文件名称中带有的 '(ver n)'
    eg. '10 Mile Stereo (ver 2)' -> '10 Mile Stereo'
    :param str:
    :return:
    """
    pattern = re.compile(r'(.+?)\(ver.+?\)')
    match = pattern.match(str)
    if match:
        # 使用Match获得分组信息
        # print match.group(1)
        return match.group(1)
    return str


def get_suffix(str=''):
    """
    get the suffix of file name
    :param str:
    :return:
    """
    str = get_file_name_from_url(re.escape(str))
    try:
        index = str.rindex('.')
        return str[index + 1:]
    except ValueError as e:
        return '*'


def get_file_name_from_url(str=''):
    """
    get file_name from url
    :param str:
    :return:
    """
    try:
        index = str.rindex('/')
        return str[index + 1:]
    except ValueError as e:
        return str


STRING_RAW = list('abcdefghijklmnopqrstuvwxyz123456')


def get_random_str(length=1):
    """
    获取随机长度字符串
    :param length:
    :return:
    """
    if length > 0:
        return string.join(random.sample(STRING_RAW, length)).replace(" ", "")
    else:
        return ""