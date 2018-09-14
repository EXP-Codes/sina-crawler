# -*- coding: utf-8 -*-
__author__ = 'EXP (272629724@qq.com)'
__date__ = '2018-03-30 22:53'


import re
import src.main.py.utils.pic as pic


class Photo(object):
    '''
    照片对象
    '''

    name = ''   # 照片名称
    desc = ''   # 照片描述
    time = ''   # 照片上传时间
    url = ''    # 照片地址


    def __init__(self, desc, time, url):
        '''
        构造函数
        ==========================
            注意必须在此初始化类成员变量.
            python的类其实就是[原始实例对象], 实例化新的对象, 就相当于从这个实例对象上拷贝一个副本,
            而所有实例对象的操作，都会影响[原始实例对象]的成员变量值
            因此在新建实例时（即在拷贝副本时），为了避免把既有实例对[原始实例对象]的操作结果也拷贝过来,
            则必须在 __init__ 里面重新对类成员对象初始化
        :param desc: 照片描述
        :param time: 照片上传时间
        :param url: 照片地址
        :return:
        '''
        self.desc = '' if not desc else re.sub('[\r\n]', '', desc)
        self.time = '' if not time else time.strip()
        self.url = '' if not url else url.strip()
        self.name = pic.get_pic_name(self.time, self.desc)


    def to_str(self, is_download):
        '''
        打印照片信息
        :param is_download: 是否下载成功
        :return: 照片信息
        '''
        return '[下载状态] : %s\r\n' \
               '[上传时间] : %s\r\n' \
               '[照片描述] : %s\r\n' \
               '[照片路径] : %s\r\n' \
               '======================================================\r\n' % (
            'true' if is_download else 'false',
            self.time, self.desc, self.url
        )