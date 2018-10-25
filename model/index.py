# coding: utf8
from tornado.gen import Return, coroutine
from base import BaseModel

def get_plays():
    from random import choice
    plays = choice(['100万次', '150万次', '200万次', '250万次', '300万次'])
    return plays


class IndexModel(BaseModel):
    # 查询playlist表的总页数
    @coroutine
    def pageCount(self, page_num):
        sql = 'select count(id) from playlist'
        ret = yield self.db.query(sql)
        num = ret[0]['count(id)']
        quotient, remainder = divmod(num, page_num)
        if remainder > 0:
            pageCount = quotient + 1
        else:
            pageCount = quotient
        raise Return(pageCount)

    # 查询playlist表所有的name(标签+序列号）
    @coroutine
    def findName(self, curr_page, page_num):
        start = (curr_page - 1) * page_num
        sql = 'select name from playlist limit %s, %s' % (start, page_num)
        data = yield self.db.query(sql)
        raise Return(data)

    # 查询playlist表是否有重复数据
    @coroutine
    def findByKey(self, arg):
        sql = 'select id, name, youtube, iqiyi from playlist where name="%s"' % (arg['name'])
        data = yield self.db.get(sql)
        raise Return(data)

    # 添加playlist表的数据
    @coroutine
    def add_playlist(self, arg):
        sql = 'insert into playlist(name, %s) values("%s", "%s") on duplicate key update %s="%s"' % (arg['fild'], arg['name'], arg['pid'], arg['fild'], arg['pid'])
        num = yield self.db.execute(sql)
        raise Return(num)

    # 添加playlist_details表的数据
    @coroutine
    def add_playlist_details(self, arg):
        import time
        v_expire_t = int(time.time() + 170)
        type = '未知'
        # sql = 'insert into playlist_details(pid, pl_expired, v_expire_t, title, img, type, plays, intro) values ("%s", 0, "%s", "%s", "%s", "%s", "%s", "%s") on duplicate key update title = "%s", img = "%s", intro = "%s" ' % (
        sql = 'insert into playlist_details(pid, v_expire_t, title, img, type, plays) values ("%s", "%s", "%s", "%s", "%s", "%s") on duplicate key update title = "%s"' % (arg['pid'], v_expire_t, arg['title'], arg['img'], type, get_plays(), arg['title'])
        num = yield self.db.execute(sql)
        raise Return(num)

    # 添加videos表的数据
    @coroutine
    def add_videos(self, arg):
        arg['vid'] = int(arg['vid'])
        # print('---add videos arg---', arg)
        if '\\' in arg['vimg']:
            arg['vimg'].replace('\\', '')
        sql = 'insert into videos(pid, vid, vtitle, vimg, vpurl, vvurl) values ("%s", "%s", "%s", "%s", "%s", "%s") on duplicate key update vtitle="%s", vimg="%s"' % (arg['pid'], arg['vid'], arg['vtitle'], arg['vimg'], arg['vpurl'], arg['vvurl'], arg['vtitle'], arg['vimg'])
        num = yield self.db.execute(sql)
        raise Return(num)

    # 查询playlist表的数据(按名字--标签）
    @coroutine
    def get_playlist_by_name(self, name):
        sql = "select id, name, youtube, bilibili from playlist where name='%s'" % name
        data = yield self.db.get(sql)
        raise Return(data)

    # 模糊查询playlist表的数据(按名字--标签）
    @coroutine
    def get_playlist_by_key(self, name):
        sql = "select id, name, youtube, bilibili from playlist where name like '%%{}%%'".format(name)
        data = yield self.db.query(sql)
        raise Return(data)

    # 查询playlist_details表的数据(按pid）
    @coroutine
    def get_playlist_details(self, pid):
        sql = "select pid, title, img, type, plays, intro from playlist_details where pid='%s'" % pid
        data = yield self.db.get(sql)
        obj = yield self.findTagByPid(pid)
        data['tag'] = obj[0]['name'] if obj else ''
        v_obj = yield self.get_videos(pid)
        sum = len(v_obj)
        i = 0
        for v in v_obj:
            if v['oss_status'] == '1': i+=1
            v['success'] = str(i)+'/'+str(sum)
            # print(v['success'])
        raise Return(data)

    # 查询playlist_details表的总页数
    @coroutine
    def detailPageCount(self, page_num):
        sql = 'select count(id) from playlist_details'
        ret = yield self.db.query(sql)
        num = ret[0]['count(id)']
        quotient, remainder = divmod(num, page_num)
        if remainder > 0:
            pageCount = quotient + 1
        else:
            pageCount = quotient
        raise Return(pageCount)

    # 查询pid 对应的tag
    @coroutine
    def findTagByPid(self, val):
        sql = 'select name from playlist where youtube = "%s"' % val
        obj = yield self.db.query(sql)
        # if not obj:
        #     sql = 'select name from playlist where youku = "%s"' % val
        #     obj = yield self.db.query(sql)
        raise Return(obj)

    # 查询playlist_details表所有的数据
    @coroutine
    def get_all_playlist_details(self, curr_page, page_num):
        start = (curr_page - 1) * page_num
        sql = "select * from playlist_details limit %d, %d" % (start, page_num)
        data = yield self.db.query(sql)
        for v in data:
            obj = yield self.findTagByPid(v['pid'])
            v['tag'] = obj[0]['name'] if obj else ''
            v_obj = yield self.get_videos(v['pid'])
            sum = len(v_obj)
            i = 0
            for vv in v_obj:
                if vv['oss_status'] == '1': i += 1
            v['success'] = str(i) + '/' + str(sum)
            # print(v['success'])
        raise Return(data)

    # 查询videos表的数据(按pid）
    @coroutine
    def get_videos(self, pid):
        sql = "select pid, vid, vtitle, vimg, vpurl, vvurl, oss_status from videos where pid='%s'" % pid
        video = yield self.db.query(sql)
        raise Return(video)

    # 查询videos表的数据(按pid, vid）
    @coroutine
    def get_video_by_key(self, arg):
        sql = "select pid, vid, vtitle, vimg, vpurl, vvrul, oss_status from videos where pid='%s' and vid=%d" % (arg['pid'], arg['vid'])
        obj = yield self.db.get(sql)
        # print('obj----', obj)
        raise Return(obj)

    # 查询videos表的数据(按vvurl）
    @coroutine
    def get_video_by_vvurl(self, vvurl):
        sql = "select pid, vid, vtitle, vimg, vpurl, vvrul, oss_status  from videos where vvurl='%s' " % vvurl
        obj = yield self.db.get(sql)
        raise Return(obj)

    # 修改上传下载videos表 oss_status
    @coroutine
    def updateStatus(self, arg):
        print('-----------------------youtub_video service start updateStatus----------------------------')
        # print(arg['oss_status'], type(arg['oss_status']))
        sql = 'update videos set vimg="%s", oss_status="%s" where vvurl="%s" and vpurl="%s"' % (arg['vimg'], str(arg['oss_status']), arg['vvurl'], arg['vpurl'])
        obj = yield self.db.execute(sql)
        raise Return(obj)