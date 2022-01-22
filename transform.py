# -*- coding:utf-8 -*-
# 网易云音乐缓存转化


# Preliminary
# Python 3.8+
# pip install aiofiles


# 1. 把要下载的歌都放在一个歌单里，一次最多500首。
# 2. 设置网易云音乐的缓存目录,设置缓存大小到10G
# 3. 用网易云音乐播放歌单， 注意设置音质，耐心等待全部歌曲播放完毕. 
# 4. 设置此脚本 UC文件缓冲路径， 生成MP3文件路径， 网易云音乐的播放历史记录文件 (也可以备份cache 和 webdata 文件夹). 网易云音乐的播放历史记录文件playlist_history有可能不包含tracks信息，文件大约20k，简单做法就是删除重装，播放的第一个歌单的内容会写入playlist_history。
# 5. 运行脚本 python transform.py

#Thanks to https://blog.csdn.net/haha1fan/article/details/104464221
#https://github.com/Grente/cloudMusicTransform

import os
import re
import configparser
import asyncio
import aiofiles
import json

# UC文件缓冲路径 例如 C:\Users\Gimbal\AppData\Local\Netease\CloudMusic\Cache\Cache
UC_PATH = 'C:\\Users\\Gimbal\\AppData\\Local\\Netease\\CloudMusic\\Cache\\Cache'
# 生成MP3文件路径
MP3_PATH = 'C:\\cache\\mp3'
# 网易云音乐的播放历史记录，最多500条
PLAYLIST_HISTORY  = 'C:\\Users\\Gimbal\\AppData\\Local\\Netease\\CloudMusic\\webdata\\file\\playlist_history2' #C:\Users\Gimbal\AppData\Local\Netease\CloudMusic\webdata\file\playlist_history'
class Transform():
    def __init__(self):
        self.uc_path = ''
        self.mp3_path = ''
        self.id2file = {}  # {mp3 ID: file name}
        self.filenamedict = {}  # {mp3 ID: file name}
        self.playlist_history_file = ''
    def check_config(self):
        try:
            self.uc_path = UC_PATH
            self.mp3_path = MP3_PATH
            self.playlist_history_file = PLAYLIST_HISTORY
        except Exception as e:
            print('Warning {} 请检查配置文件config.py变量 UC_PATH MP3_PATH'.format(str(e)))
            return False

        if not os.path.exists(self.uc_path):
            print('缓存路径错误: {}'.format(self.uc_path))
            return False
        if not os.path.exists(self.mp3_path):
            print('目标路径错误: {}'.format(self.mp3_path))
            return False
        if not os.path.exists(self.playlist_history_file):
            print('目标文件错误: {}'.format(self.playlist_history_file))
            return False
        # 容错处理 防止绝对路径结尾不是/
        if self.uc_path[-1] != '\\':
            self.uc_path += '\\'
        if self.mp3_path[-1] != '\\':
            self.mp3_path += '\\'
        print(self.playlist_history_file)
        index = 0
        with open(self.playlist_history_file, encoding='utf-8') as f:
            infos = json.load(f)
            print(infos)
            for info in infos:
                tracks = info['tracks']            
                for track in tracks:
                    song_id = track['id']
                    artistname = ''
                    artcount = len(track['ar'])
                    artindex = 0
                    for artist in track['ar']:
                        if artindex == 0:                    
                            artistname += ' ' + artist['name']
                        elif artindex == artcount-1:
                            artistname += ' and ' + artist['name']
                        else:
                            artistname += ', ' + artist['name']
                        artindex += 1
                    if artcount == 0:
                        artistname = 'Unknown'
                    x = track['name'] + " by"+ artistname    
                    i = 0
                    z  = ''
                    ret_str = []
                    while i < len(x):                    
                        if ord(x[i])>47:  #去掉转义字符  
                            ret_str.append(x[i])        
                            tc = x[i]
                        elif tc != ' ':
                            ret_str.append(' ')        
                            tc = ' '
                        i = i + 1
                    songname = ''.join(ret_str)
                    self.filenamedict[int(song_id)] = fileName = re.sub(r'[\\/:*?"<>|]','-',songname)#去掉非法字符  
                    index += 1
                    print('found {} track {} of {}'.format(index, track['id'], self.filenamedict[track['id']]))
        return True

    def generate_files(self):
        files = os.listdir(self.uc_path)
        for file in files:
            if file[-3:] == '.uc':  # 后缀uc结尾为歌曲缓存
                song_id = self.get_song_by_file(file)
                if not song_id:
                    continue
                self.id2file[song_id] = file[0:-3]
                print('detect {}'.format(self.id2file[song_id]))

    def on_transform(self):
        loop = asyncio.get_event_loop()
        tasks = [self.do_transform(song_id, file) for song_id, file in self.id2file.items()]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    async def do_transform(self, song_id, uc_file):        
        infofile = self.uc_path + uc_file + '.info'
        idxfile = self.uc_path + uc_file + '.idx'
        ucfile = self.uc_path + uc_file + '.uc'
        if os.path.exists(infofile) and os.path.exists(idxfile) and os.path.exists(ucfile):         
            file_ext = await self.get_song_ext(uc_file)
            songname = self.filenamedict.get(int(song_id)) or "Unknown"            
            mp3_file_name = self.mp3_path + '%s.%s' % (songname,file_ext)
            print('convert {} : {} to {}'.format(song_id, ucfile, mp3_file_name))
            if os.path.exists(mp3_file_name):
                print('skip convert {}:{} to {}'.format(song_id, ucfile, mp3_file_name))
            else:
                async with aiofiles.open(ucfile, mode='rb') as f:
                    uc_content = await f.read()
                    mp3_content = bytearray()
                    for byte in uc_content:
                        byte ^= 0xa3
                        mp3_content.append(byte)            
                    async with aiofiles.open(mp3_file_name, 'wb') as mp3_file:
                        await mp3_file.write(mp3_content)
                        print('success {}'.format(mp3_file_name))
        else:
            print('missing one or more  {} , {} and {}'.format(infofile, idxfile, ucfile))


    def get_song_by_file(self, file_name):
        match_inst = re.match('\d*', file_name)  # -前面的数字是歌曲ID，例：1347203552-320-0aa1
        if match_inst:
            return match_inst.group()

    async def get_song_ext(self, uc_file):        
        infofile = self.uc_path + uc_file + '.info'
        async with aiofiles.open(infofile, mode='rb') as f:
            info_content = await f.read()
            info = json.loads(info_content)
            return info['format']

if __name__ == '__main__':
    transform = Transform()
    if not transform.check_config():
        exit()
    transform.generate_files()
    transform.on_transform()
