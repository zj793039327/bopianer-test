# encoding: utf-8
__author__ = 'zjhome'

import os
from core.utils import encrypt_utils

target_dir = '/home/jixin/DB_FILE_EN'
src_dir = '/home/jixin/DB_FILE'


def encode_dir():
    print src_dir
    for parent, dirnames, filenames in os.walk(src_dir):
        # 三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        for dirname in dirnames:  # 输出文件夹信息
            print dirname
            pass

        for filename in filenames:  # 输出文件信息
            local_file_path = os.path.join(parent, filename)

            remote_file_path = target_dir + local_file_path.replace(src_dir, '')
            remote_file_dir = remote_file_path.replace(filename, '')
            if not os.path.exists(remote_file_dir):
                os.makedirs(remote_file_dir)

            print remote_file_path
            encrypt_utils.encrypt_file(encrypt_utils.get_aes_key(), local_file_path, remote_file_path + '_en')

encode_dir()