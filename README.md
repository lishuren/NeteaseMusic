# Thanks to

https://blog.csdn.net/haha1fan/article/details/104464221

https://github.com/Grente/cloudMusicTransform



# NeteaseMusic
This script is for python self-learning purposes ONLY.
The goal of the script is to demo how to manipulate binary files and iteration json files.
Save Netease music cache to audio files.
Take your own risk while you use the script.

There is a bug in Netease windows player. It will not refresh playlist_history file. A potential workaround is to delete webapp, webdata, and other temp files. After re-login in, the playlist_history will be automatically refreshed. 


网易云音乐缓存转化
纯粹学习交流， 非商业目的。

 Preliminary:
 
 Python 3.8+
 
 pip install aiofiles


具体操作：


 1. 把要下载的歌都放在一个歌单里，一次最多500首。
 2. 设置网易云音乐的缓存目录,设置缓存大小到10G
 3. 用网易云音乐播放歌单， 注意设置音质，耐心等待全部歌曲播放完毕. 
 4. 设置此脚本 UC文件缓冲路径， 生成MP3文件路径， 网易云音乐的播放历史记录文件 (也可以备份cache 和 webdata 文件夹). 
     
     网易云音乐的播放历史记录文件playlist_history有可能不包含tracks信息，文件大约20k。
     
     简单做法： 
     
             1 就是删除重装，播放的第一个歌单的内容会写入playlist_history。
             
             2 或者删干净 webapp 和webdata， 和一些临时文件， 重新登录以后，不更新playlist_history 的bug就好了。
             
 5. 运行脚本 python transform.py

