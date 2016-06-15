# encoding: utf-8
__author__ = 'zjhome'
from PIL import Image
import os


def resize_image(size, src_path, target_path, quality=70):
    """
    生成缩略图, 生成的规则 : 短边缩放, 居中裁剪
    """
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
    thumb.save(target_path, quality=quality)