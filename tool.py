# -*- coding: UTF-8 -*-
import requests
import fire
import urllib.request
import urllib.parse
import json
import execjs
import re
import ssl
import os
import pygame
import sys
import threading


ssl._create_default_https_context = ssl._create_unverified_context


class GoogleTrans(object):
    def __init__(self):
        self.url = 'https://translate.google.cn/translate_a/single'
        self.TKK = '434674.96463358'

        self.header = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "cookie": "NID=188=M1p_rBfweeI_Z02d1MOSQ5abYsPfZogDrFjKwIUbmAr584bc9GBZkfDwKQ80cQCQC34zwD4ZYHFMUf4F59aDQLSc79_LcmsAihnW0Rsb1MjlzLNElWihv-8KByeDBblR2V1kjTSC8KnVMe32PNSJBQbvBKvgl4CTfzvaIEgkqss",
            "referer": "https://translate.google.cn/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
            "x-client-data": "CJK2yQEIpLbJAQjEtskBCKmdygEIqKPKAQi5pcoBCLGnygEI4qjKAQjxqcoBCJetygEIza3KAQ==",
        }

        self.data = {
            "client": "webapp",  # 基于网页访问服务器
            "sl": "auto",  # 源语言,auto表示由谷歌自动识别
            "tl": "vi",  # 翻译的目标语言
            "hl": "zh-CN",  # 界面语言选中文，毕竟URL都是cn后缀了，就不装美国人了
            "dt": ["at", "bd", "ex", "ld", "md", "qca", "rw", "rm", "ss", "t"],  # dt表示要求服务器返回的数据类型
            "otf": "2",
            "ssel": "0",
            "tsel": "0",
            "kc": "1",
            "tk": "",  # 谷歌服务器会核对的token
            "q": ""  # 待翻译的字符串
        }

        with open('../token.js', 'r', encoding='utf-8') as f:
            self.js_fun = execjs.compile(f.read())

        # 构建完对象以后要同步更新一下TKK值
        # self.update_TKK()

    def update_TKK(self):
        url = "https://translate.google.cn/"
        req = urllib.request.Request(url=url, headers=self.header)
        page_source = urllib.request.urlopen(req).read().decode("utf-8")
        self.TKK = re.findall(r"tkk:'([0-9]+\.[0-9]+)'", page_source)[0]

    def construct_url(self):
        base = self.url + '?'
        for key in self.data:
            if isinstance(self.data[key], list):
                base = base + "dt=" + "&dt=".join(self.data[key]) + "&"
            else:
                base = base + key + '=' + self.data[key] + '&'
        base = base[:-1]
        return base

    def query(self, q, lang_to=''):
        self.data['q'] = urllib.parse.quote(q)
        self.data['tk'] = self.js_fun.call('wo', q, self.TKK)
        self.data['tl'] = lang_to
        url = self.construct_url()
        req = urllib.request.Request(url=url, headers=self.header)
        response = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
        targetText = response[0][0][0]
        originalText = response[0][0][1]
        originalLanguageCode = response[2]
        print("raw：{}，from：{}".format(originalText, originalLanguageCode))
        print("after：{}, to：{}".format(targetText, lang_to))


def translate(text, lang_to='zh-CN'):
    GoogleTrans().query(text, lang_to)


def getStockInfo(code):
    code = str(code)
    if 'a' <= code[0] <= 'z':
        codes = searchStock(code)
        if len(codes) > 1:
            out = '请输入代码：'
            for dict in codes:
                out += '\ncode：' + dict['symbol'] + ' name:' + dict['name']
            return out
        elif len(codes) < 1:
            return ''
        else:
            code = codes[0]['symbol']
    url = 'http://api.money.126.net/data/feed/'
    if code[0] in ['0', '3'] and code != '000001':
        code = '1' + code
    else:
        code = '0' + code
    raw_data = requests.get(url + code).text
    json_string = raw_data.replace(')', '(').split('(')[1]
    dict = eval(json_string)[code]
    dict = {key: dict[key] for key in dict if key in ['name', 'price', 'yestclose', 'open', 'high', 'low', 'volume']}
    return dict

def searchStock(name):
    r = requests.get('http://quotes.money.163.com/stocksearch/json.do?type=&count=10&t=&word=' + name).text
    json_list = r.replace(')', '(').split('(')[1]
    json_list = eval(json_list)
    json_list = list(filter(lambda x: x['spell'] == name, json_list))
    print(json_list)
    res = []
    for dict in json_list:
        res.append({'symbol': dict['symbol'],
                    'name': dict['name']
                    })
    return res

def playMusic(filename, loops=0, start=0.0, value=0.5):
    if not os.path.exists(filename):
        print('文件不存在')
        return
    flag = False
    pygame.mixer.init()
    while 1:
        if flag == 0:
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play(loops=loops, start=start)
            pygame.mixer.music.set_volume(value)
            while True:
                print("\r command (q,p,s,+,-): ",end='',flush=True)
                command = sys.stdin.readline().strip()
                if command == 'q':
                    flag = True
                    break
                if command == 'p':
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.pause()
                if command == 's':
                    pygame.mixer.music.unpause()
                if command == '+':
                    if value <= 0.9:
                        value += 0.1
                        pygame.mixer.music.set_volume(value)
                if command == '-':
                    if value >= 0.1:
                        value -= 0.1
                        pygame.mixer.music.set_volume(value)
                else:
                    continue
        else:
            if flag:
                pygame.mixer.quit()
                break

DIR = './music'

def searchSongV2(name):
    limit = 10
    page = 0
    url = 'http://jadeite.migu.cn:7090/music_search/v2/search/searchAll' \
          '?sid=4f87090d01c84984a11976b828e2b02c18946be88a6b4c47bcdc92fbd40762db' \
          '&isCorrect=1&isCopyright=1' \
          '&searchSwitch=%7B%22song%22%3A1%2C%22album%22%3A0%2C%22singer%22%3A0%2C%22tagSong%22%3A1%2C%22mvSong%22%3A0%2C%22bestShow%22%3A1%2C%22songlist%22%3A0%2C%22lyricSong%22%3A0%7D' \
          '&pageSize={}' \
          '&text={}' \
          '&pageNo={}&sort=0'.format(limit,urllib.parse.quote(name),page)
    headers = {
        'sign': 'c3b7ae985e2206e97f1b2de8f88691e2',
        'timestamp': '1578225871982',
        'appId': 'yyapp2',
        'mode': 'android',
        'ua': 'Android_migu',
        'version': '6.9.4',
        'osVersion': 'android 7.0',
        'User-Agent': 'okhttp/3.9.1',
    }
    jsonString = requests.get(url,headers=headers).text
    jsonObj = json.loads(jsonString)
    songInfos = []
    index = 1
    for _, i in enumerate(jsonObj['songResultData']['resultList']):
        for _, j in enumerate(i):
            songInfo = {'singer': j['singer'], 'formats': [], 'album': j['album'], 'contentId': j['contentId'],'name':j['name']}
            for _, rateFormat in enumerate(j['newRateFormats']):
                if rateFormat['formatType'] == 'LQ':
                    continue
                item = {'formatType': rateFormat['formatType'],
                        'resourceType': rateFormat['resourceType']}
                if 'androidSize' in rateFormat.keys():
                    item['fileType'] = 'flac'
                    item['size'] = rateFormat['androidSize']
                else:
                    item['size'] = rateFormat['size']
                    item['fileType'] = rateFormat['fileType']
                songInfo['formats'].append(item)
            print('index:{} song:{},singer:{},album:{}'.format(index,songInfo['name'], songInfo['singer'], songInfo['album']))
            songInfos.append(songInfo)
            index += 1
    print('please select ({} to {}):'.format(1, len(songInfos)))
    index = int(sys.stdin.readline())
    selectedSong = songInfos[index-1]
    for index,format in enumerate(selectedSong['formats']):
        print("{}.{} size: {}".format(index+1,format['formatType'],str(int(format['size'])/1048576)+'MB'))
    print('select quality(choose index):')
    index = int(sys.stdin.readline())
    selectedFormat = selectedSong['formats'][index-1]
    songFileName = '{}-{}-{}-{}.{}'.format(selectedSong['name'],selectedSong['singer'],selectedSong['album'],selectedFormat['formatType'],selectedFormat['fileType'])
    songPath = DIR+'/'+songFileName
    if not os.path.exists(songPath):
        songUrl = 'http://218.205.239.34/MIGUM2.0/v1.0/content/sub/listenSong.do?' \
                  'toneFlag={}&netType=00&copyrightId=0&contentId={}&resourceType={}&channel=0' \
            .format(selectedFormat['formatType'], selectedSong['contentId'], selectedFormat['resourceType'])

        #progressbar(songUrl, DIR, songFileName)
        multiThreadDownload(songUrl, DIR,songFileName)

    playMusic(songPath)
    #

def myMusicList():
    files = os.listdir('./music')
    for i,v in enumerate(files):
        if v.endswith('.mp3') or v.endswith('.flac'):
            print('{}.{}'.format(i+1,v))

downloadTimeTick = 0
def multiThreadDownload(url,dir,name,number_of_threads=5):
    if not os.path.exists(dir):
        os.mkdir(dir)
    filepath = dir+'/'+name
    if os.path.exists(filepath):
        return
    r = requests.get(url,stream=True)
    file_size = int(r.headers['content-length'])
    part = int(file_size) / number_of_threads
    fp = open(filepath, "wb")
    fp.write(b'\0' * int(file_size))
    fp.close()
    for i in range(number_of_threads):
        start = part * i
        end = start + part

        # create a Thread with start and end locations
        t = threading.Thread(target=downlodHandler,
                             kwargs={'start': start, 'end': end, 'url': url, 'filename': filepath,'file_size':file_size})
        t.setDaemon(True)
        t.start()

    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()
    print('\n')
def downlodHandler(start,end,url,filename,file_size):
    global downloadTimeTick
    headers = {'Range': 'bytes=%d-%d' % (start, end)}
    r = requests.get(url, headers=headers, stream=True)
    with open(filename, "r+b") as fp:
        fp.seek(int(start))
        for data in r.iter_content(chunk_size=1024):
            downloadTimeTick += len(data)
            print('\r downloading....{}%'.format(int(downloadTimeTick*100/file_size)),end='',flush=True)
            fp.write(data)







if __name__ == '__main__':
    fire.Fire({
        'stock': getStockInfo,
        'trans': translate,
        'music': searchSongV2
    })



