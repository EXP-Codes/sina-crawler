# -*- coding: utf-8 -*-
__author__ = 'EXP (272629724@qq.com)'
__date__ = '2018-03-29 20:17'


import src.main.py.utils.account as account
from src.main.py.core.lander import Lander
from src.main.py.core.album import AlbumAnalyzer


def crawler():
    '''
    执行新浪微博爬虫
    :return: None
    '''
    username, password, album_url = account.load()
    if not username or not password or not album_url :
        username = input('请输入 [新浪微博账号] : ').strip()
        password = input('请输入 [新浪微博密码] : ').strip()
        album_url = input('请输入 [爬取的相册专辑地址](如 http://photo.weibo.com/000000/albums?rd=1) : ').strip()

    print('新浪微博账号: %s' % username)
    print('新浪微博密码: %s' % password)
    print('爬取的相册专辑地址: %s' % album_url)

    # 登陆
    lander = Lander(username, password)
    if lander.execute() == True:

        # 保存登陆信息
        account.save(username, password, album_url)

        # 下载相册
        analyzer = AlbumAnalyzer(lander.cookie, album_url)
        analyzer.execute()



if __name__ == '__main__':
    crawler()

