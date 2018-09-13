# -*- coding: utf-8 -*-
__author__ = 'EXP (272629724@qq.com)'
__date__ = '2018-03-29 20:17'

import os
import shutil
import requests
import time
import json
import traceback
import src.main.py.config as cfg
import src.main.py.utils.xhr as xhr
import src.main.py.utils.pic as pic
from src.main.py.bean.cookie import SinaCookie
from src.main.py.bean.album import Album
from src.main.py.bean.photo import Photo


class AlbumAnalyzer(object):
    '''
    【新浪相册专辑】解析器
    '''

    ALBUM_INFO_NAME = 'AlbumInfo-[相册信息].txt' # 相册信息保存文件名
    cookie = None       # 已登陆的SinaCookie
    sina_user_id = ''   # 被爬取相册的新浪用户ID
    ALBUM_DIR = ''      # 相册保存目录


    def __init__(self, cookie, album_url):
        '''
        构造函数
        :param cookie: 已登陆的SinaCookie
        :param album_url: 爬取的相册专辑地址
        :return:None
        '''
        self.cookie = SinaCookie() if not cookie else cookie
        self.sina_user_id = pic.get_user_id(album_url)
        self.ALBUM_DIR = '%s%s/album/' % (cfg.DATA_DIR, self.sina_user_id)


    def execute(self):
        '''
        执行空间相册解析, 并下载所有相册及其内的照片
        :return:None
        '''
        try:

            # 清除上次下载的数据
            if os.path.exists(self.ALBUM_DIR):
                shutil.rmtree(self.ALBUM_DIR)
            os.makedirs(self.ALBUM_DIR)

            # 下载相册
            albums = self.get_albums()
            self.download_albums(albums)
            print('任务完成: 新浪用户 [%s] 的相册已保存到 [%s]' % (self.sina_user_id, self.ALBUM_DIR))

        except:
            print('任务失败: 下载新浪用户 [%s] 的相册时发生异常' % self.sina_user_id)
            traceback.print_exc()


    def get_albums(self):
        '''
        提取所有相册及其内的照片信息
        :return: 相册列表（含照片信息）
        '''
        albums = self.get_album_list()
        for album in albums:
            self.open(album)
        return albums


    def get_album_list(self):
        '''
        获取相册列表
        :return: 相册列表(仅相册信息, 不含内部照片信息)
        '''
        print('正在提取新浪用户 [%s] 的相册列表...' % self.sina_user_id)
        params = {
            'uid' : self.sina_user_id,
            '__rnd' : str(int(time.time() * 1000)),
            'page' : '1',
            'count' : '20'
        }
        response = requests.get(url=cfg.ALBUM_LIST_URL,
                                headers=xhr.get_headers(self.cookie.to_nv()),
                                params=params)
        albums = []
        try:
            root = json.loads(response.text)
            data = root['data']
            album_list = data['album_list']
            for album in album_list :
                aid = album.get('album_id', '')
                name = album.get('caption', '')
                type = int(album.get('type', '0'))
                total_pic_num = album.get('count').get('photos', 0)
                albums.append(Album(aid, name, type, total_pic_num))

        except:
            print('提取新浪用户 [%s] 的相册列表异常' % self.sina_user_id)
            traceback.print_exc()

        return albums


    def open(self, album):
        '''
        打开相册, 提取其中的所有照片信息
        :param album: 相册信息
        :return: None
        '''
        print('正在读取相册 [%s] (共%d页, 照片x%d)' % (album.name, album.page_num, album.total_pic_num))
        for page in range(album.page_num) :
            page += 1
            print(' -> 正在提取第 [%d] 页的照片信息...' % page)
            page_photos = self.get_page_photos(album, page)
            album.adds(page_photos)
            print(' ->  -> 第 [%d] 页照片提取完成, 当前进度: %d/%d' % (page, album.pic_num(), album.total_pic_num))
            time.sleep(cfg.SLEEP_TIME)


    def get_page_photos(self, album, page):
        '''
        获取相册的分页照片信息
        :param album: 相册信息
        :param page: 页数
        :return: 分页照片信息
        '''
        params = {
            'uid' : self.sina_user_id,
            'album_id' : album.id,
            '__rnd' : str(int(time.time() * 1000)),
            'page' : str(page),
            'count' : str(cfg.BATCH_LIMT),
            'type' : str(album.type)
        }
        response = requests.get(url=cfg.PHOTO_LIST_URL,
                                headers=xhr.get_headers(self.cookie.to_nv()),
                                params=params)
        photos = []
        try:
            root = json.loads(response.text)
            data = root['data']
            photo_list = data['photo_list']
            for photo in photo_list :
                desc = photo.get('caption_render', '')
                upload_time = photo.get('updated_at', '')
                pic_host = photo.get('pic_host', '')
                pic_name = photo.get('pic_name', '')
                url = cfg.PHOTO_URL(pic_host, pic_name)
                photos.append(Photo(desc, upload_time, url))

        except:
            print('提取相册 [%s] 第%d页的照片信息异常' % (album.name, page))
            traceback.print_exc()

        return photos


    def download_albums(self, albums):
        '''
        下载所有相册及其内的照片
        :param albums: 相册集（含照片信息）
        :return: None
        '''
        if len(albums) <= 0 :
            return

        print('提取新浪用户 [%s] 的相册及照片完成, 开始下载...' % self.sina_user_id)
        for album in albums :
            os.makedirs('%s%s' % (self.ALBUM_DIR, album.name))
            album_url = cfg.ALBUM_URL(self.sina_user_id, album.id)
            album_infos = album.to_str(album_url)

            print('正在下载相册 [%s] 的照片...' % album.name)
            cnt = 0
            for photo in album.photos :
                is_ok = self.download_photo(album, photo)
                cnt += (1 if is_ok else 0)
                album_infos = '%s%s' % (album_infos, photo.to_str(is_ok))
                print(' -> 下载照片进度(%s): %d/%d' % ('成功' if is_ok else '失败', cnt, album.pic_num()))
                time.sleep(cfg.SLEEP_TIME)

            print(' -> 相册 [%s] 下载完成, 成功率: %d/%d' % (album.name, cnt, album.pic_num()))

            # 保存下载信息
            save_path = '%s%s/%s' % (self.ALBUM_DIR, album.name, self.ALBUM_INFO_NAME)
            with open(save_path, 'w', encoding=cfg.CHARSET_UTF8) as file :
                file.write(album_infos) # 新浪微博含有emojji表情符号, 需要使用UNICODE


    def download_photo(self, album, photo):
        '''
        下载单张照片
        :param album: 照片所属的相册信息
        :param photo: 照片信息
        :return: 是否下载成功
        '''
        headers = xhr.get_headers(self.cookie.to_nv())
        save_path = '%s%s/%s' % (self.ALBUM_DIR, album.name, photo.name)

        is_ok = False
        for retry in range(cfg.RETRY) :
            is_ok, set_cookie = xhr.download_pic(photo.url, headers, '{}', save_path)
            if is_ok == True :
                break

            elif os.path.exists(save_path) :
                os.remove(save_path)

        return is_ok

