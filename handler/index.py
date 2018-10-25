# coding:utf8
from .base import BaseHandler
from tornado.gen import coroutine, Return
from tasks import downAndUpload
import json
import sys
import requests
import oss
import time
reload(sys)
sys.setdefaultencoding('utf-8')


dev_url = 'http://localhost:8880'

# 回调国内服务器
notify_url = 'http://localhost:8883'


class IndexHandler(BaseHandler):
    @coroutine
    def get(self):
        self.json_ok('welcome to here!')


class GetVideoInfoHandler(BaseHandler):
    @coroutine
    def get(self):
        self.json_ok('getvideoinfo')

    @coroutine
    def get_target(self, html):
        start = html.index('window["ytInitialData"]')
        end = html.index('window["ytInitialPlayerResponse"]')
        target = html[start: end]
        start = target.index('{')
        target = target[start:]
        target = json.loads(target.strip()[:-1])
        # print('target----', target)
        raise Return(target)

    @coroutine
    def extract_target(self, html, pid, way=''):
        target = yield self.get_target(html)
        vid = 1
        res = []
        if not way:  # 非完整系列视频
            i = 1
            for v in target['contents']['twoColumnWatchNextResults']['secondaryResults']['secondaryResults']['results']:
                print('--------------------', vid)
                if i > 6: break
                if 1 != i:
                    ret = v['compactVideoRenderer']
                    vtitle = ret['title']['simpleText']
                    vimg = ret['thumbnail']['thumbnails'][1]['url']
                    if i == 2:
                        img_name = str(int(time.time() * 1000)) + '.jpg'
                        oss.uploadNetFileToOss(vimg, img_name)
                        detail_arg = {'pid': pid, 'title': vtitle, 'img': img_name}
                        add2_num = yield self.index_serv.add_playlist_details(detail_arg)
                        res.append(add2_num)
                    vpurl = ret['videoId'] + '.mp4'
                    vvurl = 'https://www.youtube.com/watch?v=' + ret['videoId']
                    videos_arg = {'pid': pid, 'vid': vid, 'vtitle': vtitle, 'vimg': vimg, 'vpurl': vpurl, 'vvurl': vvurl}
                    add3_num = yield self.index_serv.add_videos(videos_arg)
                    res.append(add3_num)
                    vid += 1
                i += 1

        else:  # 完整系列视频
            title = target['contents']['twoColumnWatchNextResults']['playlist']['playlist']['title']
            for v in target['contents']['twoColumnWatchNextResults']['playlist']['playlist']['contents']:
                # print('--------------------', vid)
                try:
                    param = v['playlistPanelVideoRenderer']['navigationEndpoint']['watchEndpoint']
                    vtitle = v['playlistPanelVideoRenderer']['title']['simpleText']
                    vimg = v['playlistPanelVideoRenderer']['thumbnail']['thumbnails'][1]['url']
                    if vid == 1:
                        img_name = str(int(time.time() * 1000)) + '.jpg'
                        oss.uploadNetFileToOss(vimg, img_name)
                        detail_arg = {'pid': pid, 'title': title, 'img': img_name}
                        add2_num = yield self.index_serv.add_playlist_details(detail_arg)
                        res.append(add2_num)
                    vpurl = param['videoId'] + '.mp4'
                    vvurl = 'https://www.youtube.com/watch?v=%s&index=%s&list=%s' % (param['videoId'], vid, param['playlistId'])
                except Exception:
                    continue
                videos_arg = {'pid': pid, 'vid': vid, 'vtitle': vtitle, 'vimg': vimg, 'vpurl': vpurl, 'vvurl': vvurl}
                add3_num = yield self.index_serv.add_videos(videos_arg)
                res.append(add3_num)
                vid += 1
        raise Return(res)

    @coroutine
    def craw_html(self, url):
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'}
        html = requests.get(url, headers=headers).content
        raise Return(html)

    @coroutine
    def post(self):
        arg = json.loads(self.request.body)  # include: num, tag, urls
        try:
            i = int(arg['num'])
        except Exception:
            i = 1
        res = []
        play_list_status = []
        pids = []
        names = []
        for url in arg['urls'].split(';'):
            if not url: break
            name = arg['tag'] + str(i)
            i += 1
            if 'list' in url:
                pid = filter(lambda x: 'list' in x, url.split('&'))[0].split('=')[-1]
                way = 1
            else:
                way = None
                pid = url[url.index('=') + 1:]
            pids.append(pid)
            names.append(name)
            print('-----------way-----------', way)
            playlist_arg = {'name': name, 'fild': 'youtube', 'pid': pid}
            add1_num = yield self.index_serv.add_playlist(playlist_arg)
            play_list_status.append(add1_num)
            html = yield self.craw_html(url)
            if html:
                ret = yield self.extract_target(html, pid, way)
                print(ret, play_list_status)
                status = 0 if 0 in play_list_status or 0 in ret else 1
                res.append({'pid': pid, 'tag': name, 'status': status, 'url': url})
            else:
                res = {'pid': pid, 'tag': name, 'status': 3, 'url': url}
        args = []
        for v in pids:        # arg_pids = {'pids': [pid1, pid2, pid3...]}
            video_objs = yield self.index_serv.get_videos(v)
            for obj in video_objs:
                if '0' == obj['oss_status']: args.append({'vvurl': obj['vvurl'], 'vpurl': obj['vpurl'], 'vimg': obj['vimg']})
        downAndUpload.delay(args)
        self.json_ok({'msg': '', 'code': '1', 'data': res, 'ret': ret})


class UpdateStatus(BaseHandler):
    @coroutine
    def updateStatus(self, obj):
        num = yield self.index_serv.updateStatus(obj)