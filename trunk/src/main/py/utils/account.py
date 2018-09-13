# -*- coding: utf-8 -*-
__author__ = 'EXP (272629724@qq.com)'
__date__ = '2018-03-30 22:53'


import os
import src.main.py.config as cfg
import src.main.py.utils.des as des


def load():
    '''
    加载上次登陆信息
    :return: username, password, album_url
    '''
    username = ''
    password = ''
    album_url = ''

    if os.path.exists(cfg.ACCOUNT_PATH) :
        with open(cfg.ACCOUNT_PATH, 'r', encoding=cfg.CHARSET_UTF8) as account:
            lines = account.readlines()
            if len(lines) == 3 :
                username = des.decrypt(lines[0].strip())
                password = des.decrypt(lines[1].strip())
                album_url = des.decrypt(lines[2].strip())

    return username, password, album_url


def save(username, password, album_url):
    '''
    保存本次登陆信息
    :param username: 新浪微博账号
    :param password: 新浪微博密码
    :param album_url: 爬取的相册专辑地址
    :return:
    '''
    data = '%s\n%s\n%s\n' % (
        des.encrypt(username),
        des.encrypt(password),
        des.encrypt(album_url)
    )

    with open(cfg.ACCOUNT_PATH, 'w', encoding=cfg.CHARSET_UTF8) as account:
        account.write(data)

