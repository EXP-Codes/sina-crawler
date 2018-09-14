# -*- coding: utf-8 -*-
__author__ = 'EXP (272629724@qq.com)'
__date__ = '2018-03-30 22:53'


import pyDes
import base64
import src.main.py.config as cfg


KEY = 'EXP-SINA-CRAWLER'
DES = pyDes.triple_des(
    KEY,                        # 加密密钥: 长度为16或24位, 必选
    mode=pyDes.ECB,             # 加密方式: ECB(默认), CBC(安全性好于前者)
    IV=None,                    # 初始字节数(长度为8位): 如果选择的加密方式为CBC就必须有这个参数, 否则可以没有
    pad='0',                    # 加密时,若内容不足8位, 则将该字符添加到数据块的结尾; 解密时,将删除从最后一个开始的往前8位
    padmode=pyDes.PAD_NORMAL    # PAD_NORMAL或PAD_PKCS5, 当选择前者时必须设置pad
)


def encrypt(plaint='', key=KEY):
    '''
    DES加密
    :param data: 明文
    :param key: 密钥
    :return: 密文
    '''
    try:
        byte = plaint.encode(cfg.CHARSET_UTF8)   # 明文字符串转byte
        byte = DES.encrypt(byte)        # DES加密
        byte = base64.b64encode(byte)   # base64编码
        cipher = bytes.decode(byte)     # byte转字符串
    except:
        cipher = ''
    return cipher


def decrypt(cipher='', key=KEY):
    '''
    DES解密
    :param data: 密文
    :param key: 密钥
    :return: 明文
    '''
    try:
        byte = cipher.encode(cfg.CHARSET_UTF8)   # 密文字符串转byte
        byte = base64.b64decode(byte)   # base64解码
        byte = DES.decrypt(byte)        # DES解密
        plaint = bytes.decode(byte)     # byte转字符串
    except:
        plaint = ''
    return plaint

