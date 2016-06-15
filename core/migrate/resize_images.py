# encoding:utf-8
__author__ = 'zjhome'

import os
from PIL import Image
from youpua_server.settings import COVER_IMAGE_THUMB_SIZE

src_dir = u'J:\\all_cover_pic\\netease'
target_dir = u'J:\\all_cover_pic\\netease_thumb'


def resize_dir():
    print src_dir
    size_array = list()
    size_array.append(COVER_IMAGE_THUMB_SIZE.get('BIG'))
    size_array.append(COVER_IMAGE_THUMB_SIZE.get('MID'))
    size_array.append(COVER_IMAGE_THUMB_SIZE.get('MID_PJ'))
    size_array.append(COVER_IMAGE_THUMB_SIZE.get('SMALL'))

    for parent, dirnames, filenames in os.walk(src_dir):
        # 三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
        for dirname in dirnames:  # 输出文件夹信息
            print dirname
            pass

        for filename in filenames:  # 输出文件信息
            local_file_path = os.path.join(parent, filename)

            remote_file_path = target_dir + local_file_path.replace(src_dir, '')
            remote_file_dir = remote_file_path.replace(filename, '')

            if '.' in filename:
                remote_file_name = filename.split('.')[0] + '_{0}x{1}.jpg'
            else:
                remote_file_name = filename + '_{0}x{1}.jpg'
            remote_file_path = os.path.join(remote_file_dir, remote_file_name)

            if not os.path.exists(remote_file_dir):
                os.makedirs(remote_file_dir)
            print local_file_path

            # for size in size_array:
            #     resize_image(size, local_file_path, remote_file_path.format(size[0], size[1]))

            if '.' not in filename:
                os.rename(local_file_path, local_file_path + '.jpg')


def resize_image(size, src_path, target_path):
    """
        缩略图生成程序 by Neil Chen
        sizes 参数传递要生成的尺寸，可以生成多种尺寸
        """
    base, ext = os.path.splitext(src_path)
    try:
        im = Image.open(src_path)
    except IOError:
        return
    mode = im.mode
    # 保持 png 透明
    # if mode not in ('L', 'RGB'):
    # # if mode == 'RGBA':
    # #     # 透明图片需要加白色底
    # #     alpha = im.split()[3]
    # #     bgmask = alpha.point(lambda x: 255 - x)
    # #     im = im.convert('RGB')
    # #     # paste(color, box, mask)
    # #     im.paste((255, 255, 255), None, bgmask)
    # # else:
    # im = im.convert('RGB')

    width, height = im.size
    tw, th = size

    target_rate = float(tw) / th
    actual_rate = float(width) / height

    if target_rate >= actual_rate:
        width_after_cut = width
        height_after_cut = width / target_rate
        delta = (height - height_after_cut) / 2
        box = (0, delta, width_after_cut, height - delta)
    else:
        height_after_cut = height
        width_after_cut = height * target_rate
        delta = (width - width_after_cut) / 2
        box = (delta, 0, width - delta, height_after_cut)

    region = im.crop(box)
    thumb = region.resize((tw, th), Image.ANTIALIAS)
    thumb.save(target_path, quality=70)

resize_dir()