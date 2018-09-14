# -*- coding: utf-8 -*-
__author__ = 'EXP (272629724@qq.com)'
__date__ = '2018-03-29 20:44'


from __project__ import BASR_DIR
import configparser


config = configparser.ConfigParser()
config.read(filenames=('%s%s' % (BASR_DIR, '/conf/url.ini')), encoding='utf-8')


CHARSET_UTF8 = 'utf-8'   # 默认编码
CHARSET_GBK = 'gbk'      # 新浪HTTP页面内容主要编码是GBK
CHARSET_UNICODE = 'unicode_escape'  # UNICODE编码

SLEEP_TIME = 0.1    # 行为休眠间隔(s)
TIMEOUT = 10        # 请求超时(s)
BATCH_LIMT = 30     # 每次批量请求的数量限制(新浪相册每页30张相片)
RETRY = 5           # 重试次数

ACCOUNT_PATH = '%s%s' % (BASR_DIR, '/conf/account.dat')    # 登陆信息的保存位置
VCODE_PATH = '%s%s' % (BASR_DIR, '/conf/vcode.jpg')        # 登陆验证码图片的存储位置
DATA_DIR = '%s%s' % (BASR_DIR, '/data/')                   # 下载相册/说说数据的存储目录

PRE_LOGIN_URL = config.get('lander', 'PRE_LOGIN_URL')   # 获取登陆前参数的URL
VCODE_URL = config.get('lander', 'VCODE_URL')           # 获取登陆验证码图片的URL
LOGIN_URL = config.get('lander', 'LOGIN_URL')           # 新浪微博登陆URL

ALBUM_LIST_URL = config.get('album', 'ALBUM_LIST_URL')  # 新浪相册专辑URL
PHOTO_LIST_URL = config.get('album', 'PHOTO_LIST_URL')  # 新浪相册内的照片列表URL


def ALBUM_URL(user_id, album_id):
    '''
    构造相册地址URL
    :param user_id: 用户ID
    :param album_id: 相册ID
    :return: 相册地址URL
    '''
    return 'http://photo.weibo.com/%s/albums/detail/album_id/%s' % (user_id, album_id)


def PHOTO_URL(pic_host, pic_name):
    '''
    构造相片下载URL
    :param pic_host: 相片域名
    :param pic_name: 相片名称
    :return: 相片下载URL
    '''
    return '%s/large/%s' % (pic_host, pic_name)
