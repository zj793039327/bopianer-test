# encoding: utf-8

__author__ = 'zjhome'

import os
import random
import struct
import hashlib

from Crypto.Cipher import AES

from bopianer.settings import ASSET_ENCRYPT_KEY


def get_aes_key():
    """
    加解密使用, 必须要 16, 24 或者32 byte的字符串
    :return:
    """
    key = hashlib.sha256(ASSET_ENCRYPT_KEY).digest()
    return key


def get_aes_key_hex():
    """
    打印key使用
    :return:
    """
    key = hashlib.sha256(ASSET_ENCRYPT_KEY).hexdigest()
    return key


def encrypt_file(key, in_filename, out_filename=None, chunksize=64 * 1024):
    """ Encrypts a file using AES (CBC mode) with the
        given key.

        key:
            The encryption key - a string that must be
            either 16, 24 or 32 bytes long. Longer keys
            are more secure.

        in_filename:
            Name of the input file

        out_filename:
            If None, '<in_filename>.enc' will be used.

        chunksize:
            Sets the size of the chunk which the function
            uses to read and encrypt the file. Larger chunk
            sizes can be faster for some files and machines.
            chunksize must be divisible by 16.
    """
    if not out_filename:
        out_filename = in_filename + '.enc'

    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))


def decrypt_file(key, in_filename, out_filename=None, chunksize=24 * 1024):
    """ Decrypts a file using AES (CBC mode) with the
        given key. Parameters are similar to encrypt_file,
        with one difference: out_filename, if not supplied
        will be in_filename without its last extension
        (i.e. if in_filename is 'aaa.zip.enc' then
        out_filename will be 'aaa.zip')
    """
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)

# #Create a Test Src File and Get FileSteam
# fs = open(u'G:\\057bb40cc1b84cee8d53ebbfff9e788d.jpg', 'rb')
# fs_msg = fs.read()
# fs.close()
#
# #Crypt Src FileStream
# fc = open(u'G:\\057bb40cc1b84cee8d53ebbfff9e788d_en.jpg', 'wb')
# fc_msg = aes_encrypt_file(fs_msg)
# fc.writelines(fc_msg)
# fc.close()
#
# raw_input('Enter for Exit...')


# small file 49Kb
# file = u'G:\\057bb40cc1b84cee8d53ebbfff9e788d.jpg'
# middle file 4Mb
# file = u'G:\\05778c0ee3a7440096de60410ca93335.jpg'
# huge file 4Mb
# file = u'G:\\4f227a1fec414f8ba0cb08c7b1b69a68.png'

# encrypt_file(key, u'G:\\057bb40cc1b84cee8d53ebbfff9e788d.jpg', u'G:\\057bb40cc1b84cee8d53ebbfff9e788d_en.jpg')
# decrypt_file(key, u'G:\\057bb40cc1b84cee8d53ebbfff9e788d_en.jpg', u'G:\\057bb40cc1b84cee8d53ebbfff9e788d_en_cn.jpg')

# file_name = file.split('.')[0]
# file_ext = file.split('.')[1]
# #05778c0ee3a7440096de60410ca93335.jpg
# encrypt_file(key, file, file_name + '_en.' + file_ext)
# decrypt_file(key, file_name + '_en.' + file_ext, file_name + '_en_cn.' + file_ext)

