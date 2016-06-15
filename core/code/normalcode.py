# encoding: utf-8
__author__ = 'zj'


class NormalCode():
    """
    主要针对代码进行统一的处理和翻译
    """

    YES_OR_NO = (
        (1, '是'),
        (2, '否')
    )
    SEX_MALE = 1
    SEX_FEMALE = 2
    SEX_GROUP = 3
    SEX_UNKNOWN = 4
    SEX = (
        (SEX_MALE, '男'),
        (SEX_FEMALE, '女'),
        (SEX_GROUP, '组合'),
        (SEX_UNKNOWN, '未知'),
    )
    SCORE_STATUS = (
        (10, '导入'),
        (20, '已校对'),
        (30, '已审核'),
        (40, '已改良'),
    )
    SCORE_ASSET_TYPE_TXT = 1
    SCORE_ASSET_TYPE_IMG = 2
    SCORE_ASSET_TYPE_DIGITAL = 3
    SCORE_ASSET_TYPE_UNKNOWN = 255

    SCORE_ASSET_TYPE = (
        (SCORE_ASSET_TYPE_TXT, '文本谱'),
        (SCORE_ASSET_TYPE_IMG, '图片谱'),
        (SCORE_ASSET_TYPE_DIGITAL, '数字谱'),
        (SCORE_ASSET_TYPE_UNKNOWN, '未知格式'),
    )

    SCORE_ASSET_TYPE_EN = (
        (SCORE_ASSET_TYPE_TXT, 'TXT'),
        (SCORE_ASSET_TYPE_IMG, 'IMG'),
        (SCORE_ASSET_TYPE_DIGITAL, 'MIDI'),
    )
    @staticmethod
    def get_score_asset_type(text=''):
        """
        根据文件后缀获取乐谱类型
        :param text:
        :return:
        """
        suffix_type = {
            'txt': NormalCode.SCORE_ASSET_TYPE_TXT,

            'ptb': NormalCode.SCORE_ASSET_TYPE_DIGITAL,
            'gp5': NormalCode.SCORE_ASSET_TYPE_DIGITAL,
            'gp4': NormalCode.SCORE_ASSET_TYPE_DIGITAL,
            'gpx': NormalCode.SCORE_ASSET_TYPE_DIGITAL,

            'jpg': NormalCode.SCORE_ASSET_TYPE_IMG,
            'jpeg': NormalCode.SCORE_ASSET_TYPE_IMG,
            'gif': NormalCode.SCORE_ASSET_TYPE_IMG,
            'bmp': NormalCode.SCORE_ASSET_TYPE_IMG,
            'png': NormalCode.SCORE_ASSET_TYPE_IMG,
        }
        if text is None:
            text = ''

        if suffix_type.get(text.lower()):
            return suffix_type.get(text.lower())
        else:
            return NormalCode.SCORE_ASSET_TYPE_UNKNOWN

    SCORE_PLAY_TYPE = (
        (1, '指弹'),
        (2, '弹唱'),
        (255, '其他'),
    )
    # 编曲风格
    SCORE_STYLE = (
        (1, '流行'),
        (2, '摇滚'),
        (3, '佛拉门戈'),
        (4, '民谣'),
        (5, '布鲁斯'),
        (6, '乡村'),
        (7, '爵士'),
        (255, '其他'),
    )
    # 演奏类型
    INSTRUMENTS_TYPE_GUITAR = 1
    INSTRUMENTS_TYPE_UKULELE = 2
    INSTRUMENTS_TYPE_BASS = 3
    INSTRUMENTS_TYPE_DRUM = 4
    INSTRUMENTS_TYPE_UNKNOWN = 255

    INSTRUMENTS_TYPE = (
        (INSTRUMENTS_TYPE_GUITAR, '吉他'),
        (INSTRUMENTS_TYPE_UKULELE, '尤克里里'),
        (INSTRUMENTS_TYPE_BASS, '贝斯'),
        (INSTRUMENTS_TYPE_DRUM, '鼓'),
        (5,'钢琴'),
    )

    @staticmethod
    def guess_instruments_type(text=''):
        """
        根据分类文本猜乐器类型
        :param text:
        :return:
        """
        suffix_type = {
            'chords': NormalCode.INSTRUMENTS_TYPE_GUITAR,
            'tabs': NormalCode.INSTRUMENTS_TYPE_GUITAR,
            'tab pro': NormalCode.INSTRUMENTS_TYPE_GUITAR,
            'power tab': NormalCode.INSTRUMENTS_TYPE_GUITAR,
            'guitar pro': NormalCode.INSTRUMENTS_TYPE_GUITAR,
            'gpx': NormalCode.INSTRUMENTS_TYPE_GUITAR,
            'ptb': NormalCode.INSTRUMENTS_TYPE_GUITAR,
            'gp5': NormalCode.INSTRUMENTS_TYPE_GUITAR,
            'gp4': NormalCode.INSTRUMENTS_TYPE_GUITAR,

            'bass': NormalCode.INSTRUMENTS_TYPE_BASS,
            'bass Tabs': NormalCode.INSTRUMENTS_TYPE_BASS,

            'ukulele': NormalCode.INSTRUMENTS_TYPE_UKULELE,
            'drum tabs': NormalCode.INSTRUMENTS_TYPE_DRUM,
        }
        if text is None:
            text = ''

        if suffix_type.get(text.lower()):
            return suffix_type.get(text.lower())
        else:
            return NormalCode.INSTRUMENTS_TYPE_UNKNOWN

    # 节拍
    SCORE_METER = (
        (1, '1/4'),
        (2, '2/4'),
        (3, '3/4'),
        (4, '4/4'),
        (5, '3/8'),
        (6, '6/8'),
        (7, '7/8'),
        (8, '9/8'),
        (9, '12/8'),
    )
    # 曲调
    SCORE_KEY = (
        (11, 'bC'),
        (10, 'C'),
        (12, '#C'),

        (21, 'bD'),
        (20, 'D'),

        (31, 'bE'),
        (30, 'E'),

        (41, '#F'),
        (40, 'F'),

        (51, 'bG'),
        (50, 'G'),

        (61, 'bA'),
        (60, 'A'),

        (71, 'bB'),
        (70, 'B'),
    )
    # 难度 or 评分
    SCORE_DIFFICULTY = (
        (1, '☆'),
        (2, '☆☆'),
        (3, '☆☆☆'),
        (4, '☆☆☆☆'),
        (5, '☆☆☆☆☆'),
    )
    # score类型, 指UG网站上所有的吉他谱类型。程序需要做到的是将RDS中该曲“乐谱类型”选项设定为该乐谱类型名称。
    # 工人校对是否正确，如不正确，需手动修改。
    SCORE_TYPE = (
        ('Chords', 'Chords'),
        ('tab pro', 'tab pro'),
        ('tabs', 'tabs'),
        ('guitar pro', 'guitar pro'),
        ('power tab', 'power tab'),
        ('bass', 'bass'),
        ('bass Tabs', 'bass Tabs'),
        ('Ukulele', 'Ukulele'),
        ('drum Tabs', 'drum Tabs'),
    )
    ASSET_BUSINESS_RELEASE_COVER_PIC = 'release.cover'

    ASSET_BUSINESS_SCORE_FILE = 'score.file'
    ASSET_BUSINESS_SCORE_COVER_PIC = 'score.cover'
    ASSET_BUSINESS_SCORE_RHYTHM = 'score.rhythm'
    # 附件业务类型
    ASSET_BUSINESS_TYPE = (
        (ASSET_BUSINESS_SCORE_FILE, '数据文件'),
        (ASSET_BUSINESS_SCORE_COVER_PIC, '封面图片'),
        (ASSET_BUSINESS_SCORE_RHYTHM, '节奏型'),
    )

    @staticmethod
    def translate(data, key):
        for d in data:
            if d[0] == key:
                return d[1]
            else:
                continue
        return ''

    @staticmethod
    def translate_key(data, value):
        for d in data:
            if d[1] == value:
                return d[0]
            else:
                continue
        return ''

    ARTIST_CATEGORY_TYPE_CN = 0
    ARTIST_CATEGORY_TYPE_HT = 1
    ARTIST_CATEGORY_TYPE_ES = 2
    ARTIST_CATEGORY_TYPE_JK = 3

    ARTIST_CATEGORY_TYPE = (
        (ARTIST_CATEGORY_TYPE_CN, ('CN',), '大陆'),
        (ARTIST_CATEGORY_TYPE_HT, ('HK', 'TW',), '港台'),
        (ARTIST_CATEGORY_TYPE_ES, ('GB', 'US',), '欧美'),
        (ARTIST_CATEGORY_TYPE_JK, ('JP', 'KR',), '日韩'),
    )

    # cms选集类型
    CMS_TOPIC_TYPE = (
        (1, '优选专题'),
        (2, '分类专题'),
        (3, '新手入门'),
        (4, '最佳练习曲'),
    )

    CMS_NORMAL_STATUS_PUBLISHED = 1
    CMS_NORMAL_STATUS_PENDING = 2
    CMS_NORMAL_STATUS_DELETED = 3
    # cms选集类型
    CMS_NORMAL_STATUS = (
        (CMS_NORMAL_STATUS_PUBLISHED, '已发布'),
        (CMS_NORMAL_STATUS_PENDING, '待审核'),
        (CMS_NORMAL_STATUS_DELETED, '已下架'),
    )

    CMS_TOPIC_API_TYPE = (
        {'name': '优选专题', 'url': 'api/v1/cms/topic/category/1', 'type': 'bnnr'},
        {'name': '热门乐谱', 'url': 'api/v1/cms/hotscore', 'type': 'scre'},
        #{'name': '编辑推荐', 'url': 'api/v1/cms/topic/category/2', 'type': 'ctgr'},
        #{'name': '新手入门', 'url': 'api/v1/cms/topic/category/3', 'type': 'scre'},
        {'name': '知名音乐人', 'url': 'api/v1/cms/musician', 'type': 'mscn'},
        #{'name': '最佳练习曲', 'url': 'api/v1/cms/topic/category/4', 'type': 'scre'},
    )
    ARTIST_CATEGORY_API_TYPE = (
        (0, '音乐流派'),

        #(0,'大陆'),
        #(1, '港台'),
        #(2, '欧美'),
        #(3, '日韩'),
    )
    SEX_CATEGORY_API_TYPE = (
        #(1,'男歌星'),
        #(2,'女歌星'),
        #(3,'组合'),
        #(4,'未知'),

        (1,'巴洛克时期'),
        (2,'古典时期'),
        (3,'浪漫时期'),
        (4,'现代时期'),
    )
    SEARCH_CATEGORY = (
        (1, '巴洛克时期(1567~1643)'),
        (2, '古典时期(1714~1787)'),
        (3, '浪漫时期(1782~1840)'),
        (4, '现代时期(1865-1935)'),
    )
