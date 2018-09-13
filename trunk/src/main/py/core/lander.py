# -*- coding: utf-8 -*-
__author__ = 'EXP (272629724@qq.com)'
__date__ = '2018-03-29 20:17'


import time
import base64
import rsa
import binascii
import requests
import json
import re
import traceback
import src.main.py.config as cfg
import src.main.py.utils.xhr as xhr
from src.main.py.bean.cookie import SinaCookie
from PIL import Image
from urllib.parse import quote_plus
from urllib.parse import unquote


class Lander(object):
    '''
    新浪微博登陆器.
    ========================================================
     新浪微博XHR登陆分析参考：
        登陆流程拆解：https://www.cnblogs.com/xmyzero/articles/8280052.html
        登陆流程分析：https://blog.csdn.net/u014193283/article/details/71988082
        加密流程分析：http://python.jobbole.com/86638/
    '''

    RSA_EXPONENT = int('10001', 16) # 新浪微博的RSA算法因子：把16进制的10001转换成十进制, 即65537
    username = ''   # 新浪微博账号
    password = ''   # 新浪微博密码
    base64_un = ''  # 使用Base编码后的新浪微博账号
    rsa_pwd = ''    # 使用RSA加密后的新浪微博密码
    cookie = None   # 登陆成功后保存的cookie


    def __init__(self, username, password):
        '''
        构造函数
        :param username: 新浪微博账号
        :param password: 新浪微博密码
        :return: None
        '''
        self.username = '' if not username else username
        self.password = '' if not password else password
        self.base64_un = self.__to_base64__(self.username)
        self.rsa_pwd = ''
        self.cookie = SinaCookie()


    def __to_base64__(self, username):
        '''
        对登陆账号使用base64编码（加密过程是通过分析登陆ssologin.js脚本得到）
        :param username: 登陆账号
        :return: base64编码后的账号
        '''
        un = quote_plus(username)       # 先对账号进行URL编码 (邮箱账号存在 '@' 等特殊字符需要转义)
        byte = un.encode(cfg.CHARSET_UTF8)
        byte = base64.b64encode(byte)   # base64编码
        return bytes.decode(byte)       # 字节转字符串


    def __to_rsa__(self, password):
        '''
        对登陆密码使用RSA加密（加密过程是通过分析登陆ssologin.js脚本得到）
        :param password: 登陆密码
        :return: RSA加密后的登陆密码
        '''
        int_pubkey = int(self.cookie.pubkey, 16)    # 把十六进制的公钥转换成十进制
        rsa_pubkey = rsa.PublicKey(int_pubkey, self.RSA_EXPONENT)   # 创建公钥
        data = '%s\t%s\n%s' % (self.cookie.servertime, self.cookie.nonce, password) # 拼接被加密的内容
        data = data.encode(cfg.CHARSET_UTF8)
        rsa_pwd = rsa.encrypt(data, rsa_pubkey) # 执行加密
        hex = binascii.b2a_hex(rsa_pwd)         # 转换为16进制
        return bytes.decode(hex)                # 字节转字符串


    def execute(self):
        '''
        执行登陆操作
        :return: True:登陆成功; False:登陆失败
        '''
        is_ok = False
        try:

            # 第一次登陆: 高几率失败（新浪微博的登陆有问题, 就算正常浏览器登陆，也需要正确输入2次验证码）
            reason = self.__execute__()
            if not reason :
                print('登陆新浪微博账号 [%s] 成功' % self.username)
                is_ok = True

            # 第二次登陆： 新浪微博一般需要连续[正确]登陆两次， 第一次登陆高几率失败, 但必须登陆
            else:
                reason = self.__execute__()
                if not reason :
                    print('登陆新浪微博账号 [%s] 成功' % self.username)
                    is_ok = True
                else:
                    print('登陆新浪微博账号 [%s] 失败: %s' % (self.username, reason))

        except:
            print('登陆新浪微博账号 [%s] 失败: XHR协议异常' % self.username)
            traceback.print_exc()

        return is_ok


    def __execute__(self):
        self.init_cookie_env()
        self.rsa_pwd = self.__to_rsa__(self.password)
        pin_code = self.get_pin_code(self.cookie.pin_code_id)

        print('微博登陆账号(Base64编码): %s' % self.base64_un)
        print('微博登陆密码(RSA加密): %s' % self.rsa_pwd)
        print('登陆环境参数[showpin]: %s' % self.cookie.showpin)
        print('登陆环境参数[pcid]: %s' % self.cookie.pin_code_id)
        print('登陆环境参数[pin_code]: %s' % pin_code)
        print('登陆环境参数[servertime]: %s' % self.cookie.servertime)
        print('登陆环境参数[nonce]: %s' % self.cookie.nonce)
        print('登陆环境参数[pubkey]: %s' % self.cookie.pubkey)
        print('登陆环境参数[rsakv]: %s' % self.cookie.rsakv)

        reason = self.login(pin_code)
        return reason


    def init_cookie_env(self):
        '''
        获取登陆前环境参数
        :return: None(保存到cookie中)
        '''
        params = {
            'su' : self.base64_un,
            '_' : str(int(time.time() * 1000)),
            'callback' : 'sinaSSOController.preloginCallBack',
            'client' : 'ssologin.js(v1.4.18)',
            'entry' : 'weibo',
            'rsakt' : 'mod',
            'checkpin' : '1'
        }
        response = requests.get(url=cfg.PRE_LOGIN_URL, headers=xhr.get_headers(), params=params)
        root = json.loads(xhr.to_json(response.text))
        self.cookie.servertime = root.get('servertime', '')
        self.cookie.vcode_id = root.get('pcid', '')
        self.cookie.showpin = root.get('showpin', 0)
        self.cookie.nonce = root.get('nonce', '')
        self.cookie.pubkey = root.get('pubkey', '')
        self.cookie.rsakv = root.get('rsakv', '')


    def get_pin_code(self, pcid):
        '''
        获取登陆校验码
        :param pcid: 登陆校验码ID
        :return: 登陆校验码
        '''

        # 图片验证码登陆
        if self.cookie.showpin == 1 :
            pin_code = self.get_vcode(self.cookie.pin_code_id)

        # 动态微盾码登陆
        elif self.cookie.showpin == 2 :
            pin_code = self.get_dymaic_code(self.cookie.pin_code_id)

        # 无需验证
        else:
            pin_code = ''

        return pin_code


    def get_vcode(self, pcid):
        '''
        获取登陆图片验证码
        :param pcid: 图片验证码ID
        :return: 图片验证码
        '''
        params = {
            'r' : int(time.time()),
            's' : '0',
            'p' : pcid
        }
        is_ok, set_cookie = xhr.download_pic(pic_url=cfg.VCODE_URL,
                                             headers=xhr.get_headers(),
                                             params=params,
                                             save_path=cfg.VCODE_PATH)
        vcode = ''
        if is_ok == True :
            self.cookie.add(set_cookie)

            with Image.open(cfg.VCODE_PATH) as image:
                image.show()
                vcode = input("请输入图片验证码:").strip()
        return vcode


    def get_dymaic_code(self, pcid):
        '''
        获取登陆微盾动态码
        :param pcid: 微盾动态码ID
        :return: 微盾动态码
        '''
        dymaic_code = input("请输入微盾动态码:").strip()
        return dymaic_code


    def login(self, pin_code):
        '''
        登陆
        :param pin_code: 登陆校验码
        :return: 登陆失败原因（若登陆成功返回''）
        '''
        params = {
            'client' : 'ssologin.js(v1.4.18)',
            'entry' : 'weibo',
            'encoding' : cfg.CHARSET_UTF8,
            'su' : self.base64_un,
            'sp' : self.rsa_pwd,
            'pcid' : self.cookie.pin_code_id,
            'door' : pin_code,
            'servertime' : self.cookie.servertime,
            'nonce' : self.cookie.nonce,
            'rsakv' : self.cookie.rsakv,
            'pwencode' : 'rsa2',
            'gateway' : '1',
            'from' : '',
            'savestate' : '7',
            'qrcode_flag' : 'false',
            'useticket' : 'useticket',
            'vsnf' : '1',
            'service' : 'miniblog',
            'sr' : '1366*768',
            'prelt' : '7873',
            'pagerefer' : 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https://weibo.com/logout.php?backurl=%252F',
            'url' : 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype' : 'META',
        }
        response = requests.get(url=cfg.LOGIN_URL,
                                headers=xhr.get_headers(),
                                params=params,
                                allow_redirects=False)
        xhr.take_response_cookies(response, self.cookie)
        callback_url = self.get_callback_url(response.text, 'location\.replace\("([\s\S]*)"\);')

        reason = self.is_logined(callback_url)
        if not reason :

            # 登陆后, 第一次重定向
            response = requests.get(url=callback_url, headers=xhr.get_headers(self.cookie.to_nv()))
            xhr.take_response_cookies(response, self.cookie)
            callback_url = self.get_callback_url(response.text, "location\.replace\('([\s\S]*)'\);")

            # 第二次重定向(获取登录信息)
            response = requests.get(url=callback_url, headers=xhr.get_headers(self.cookie.to_nv()))
            xhr.take_response_cookies(response, self.cookie)
            root = json.loads(xhr.to_json(response.text))
            if root.get('result') == True :
                userinfo = root.get('userinfo')
                self.cookie.user_id = userinfo.get('uniqueid', '')  # 用户ID

            else:
                reason = '登陆成功, 但获取用户信息失败'
        return reason


    def get_callback_url(self, page_source, url_regex):
        '''
        从页面源码中提取回调地址
        :param page_source: 页面源码
        :param url_regex: 回调地址提取正则
        :return: 回调地址
        '''
        match = re.search(url_regex, page_source)
        callback_url = match.group(1)
        return callback_url


    def is_logined(self, callback_url):
        '''
        通过回调地址判断是否登陆成功
        :param callback_url: 登陆回调地址
        :return: 登陆失败原因（若成功则返回''）
        '''
        reason = ''
        match = re.search('retcode=(\d+)', callback_url)
        if match :
            retcode = match.group(1)
            if retcode != '0' :
                match = re.search('reason=([^&]+)', callback_url)
                if match :
                    raw_reason = unquote(match.group(1), encoding=cfg.CHARSET_GBK)
                    reason = '[%s][%s]' % (retcode, raw_reason)
                else:
                    reason = '[unknow][%s]' % callback_url
        return reason

