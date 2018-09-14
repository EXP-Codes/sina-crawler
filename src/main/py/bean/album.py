# -*- coding: utf-8 -*-
__author__ = 'EXP (272629724@qq.com)'
__date__ = '2018-03-30 22:53'


import src.main.py.config as cfg
import src.main.py.utils.pic as pic


class Album(object):
    '''
    相册对象
    '''

    id = ''             # 相册编号
    name = ''           # 相册名称/描述
    type = 0            # 相册类型
    page_num = 0        # 相册页数
    total_pic_num = 0   # 相册照片总数
    photos = None       # 相册照片集


    def __init__(self, id, name, type, total_pic_num):
        '''
        构造函数
        ==========================
            注意必须在此初始化类成员变量.
            python的类其实就是[原始实例对象], 实例化新的对象, 就相当于从这个实例对象上拷贝一个副本,
            而所有实例对象的操作，都会影响[原始实例对象]的成员变量值
            因此在新建实例时（即在拷贝副本时），为了避免把既有实例对[原始实例对象]的操作结果也拷贝过来,
            则必须在 __init__ 里面重新对类成员对象初始化
        :param id: 相册编号
        :param name: 相册名称/描述
        :param type: 相册类型
        :param total_pic_num: 相册照片总数
        :return:
        '''
        self.id = '' if not id else id.strip()
        self.name = '' if not name else name.strip()
        self.type = 0 if type < 0 else type
        self.total_pic_num = 0 if total_pic_num < 0 else total_pic_num
        self.page_num = pic.get_page_num(total_pic_num, cfg.BATCH_LIMT)
        self.photos = []


    def pic_num(self):
        '''
        获取当前相册的实际照片数量
        :return: 实际照片数量
        '''
        return len(self.photos)


    def add(self, photo):
        '''
        添加单张照片
        :param photo: 照片
        :return: None
        '''
        if photo != None :
            self.photos.append(photo)


    def adds(self, photos):
        '''
        添加多张照片
        :param photos: 照片集
        :return: None
        '''
        if photos != None :
            self.photos.extend(photos)


    def to_str(self, album_url):
        '''
        打印相册信息
        :return: 相册信息
        '''
        return '++++++++++++++++++++++++++++++++++++++++++++++++++++++\r\n' \
               '+ [相册名称] : %s\r\n' \
               '+ [相册编号] : %s\r\n' \
               '+ [相册地址] : %s\r\n' \
               '+ [照片数量] : %s\r\n' \
               '++++++++++++++++++++++++++++++++++++++++++++++++++++++\r\n' % (
            self.name, self.id, album_url, self.total_pic_num
        )
