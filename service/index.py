# coding: utf8
from tornado.gen import Return, coroutine
from .base import BaseService


class IndexService(BaseService):
    # 查询playlist表的总页数
    @coroutine
    def pageCount(self, page_num):
        pageCount = yield self.index_model.pageCount(page_num)
        raise Return(pageCount)

    # 查询playlist表所有的name(标签+序列号）
    @coroutine
    def findName(self, curr_page, page_num):
        data = yield self.index_model.findName(curr_page, page_num)
        raise Return(data)

    # 查询playlist表是否有重复数据
    @coroutine
    def findByKey(self, arg):
        data = yield self.index_model.findByKey(arg)
        raise Return(data)

    # 添加playlist表的数据
    @coroutine
    def add_playlist(self, arg):
        num = yield self.index_model.add_playlist(arg)
        raise Return(num)

    # 添加playlist_details表的数据
    @coroutine
    def add_playlist_details(self, arg):
        num = yield self.index_model.add_playlist_details(arg)
        raise Return(num)

    # 添加videos表的数据
    @coroutine
    def add_videos(self, arg):
        num = yield self.index_model.add_videos(arg)
        raise Return(num)

    # 查询playlist表的数据(按名字）
    @coroutine
    def get_playlist_by_name(self, name):
        data = yield self.index_model.get_playlist_by_name(name)
        raise Return(data)

    # 模糊查询playlist表的数据(按名字--标签）
    @coroutine
    def get_playlist_by_key(self, name):
        data = yield self.index_model.get_playlist_by_key(name)
        raise Return(data)

    # 查询playlist_details表的数据(按pid）
    @coroutine
    def get_playlist_details(self, pid):
        data = yield self.index_model.get_playlist_details(pid)
        raise Return(data)

    # 查询playlist_details表的总页数
    @coroutine
    def detailPageCount(self, page_num):
        pageCount = yield self.index_model.detailPageCount(page_num)
        raise Return(pageCount)

    # 查询playlist_details表所有的数据
    @coroutine
    def get_all_playlist_details(self, curr_page, page_num):
        data = yield self.index_model.get_all_playlist_details(curr_page, page_num)
        raise Return(data)

    # 查询videos表的数据(按pid）
    @coroutine
    def get_videos(self, pid):
        video = yield self.index_model.get_videos(pid)
        raise Return(video)

    # 查询videos表的数据(按pid, vid）
    @coroutine
    def get_video_by_key(self, arg):
        obj = yield self.index_model.get_video_by_key(arg)
        raise Return(obj)

    # 查询videos表的数据(按vvurl）
    @coroutine
    def get_video_by_vvurl(self, arg):
        obj = yield self.index_model.get_video_by_vvurl(arg)
        raise Return(obj)

    # 修改上传下载videos表 oss_status
    @coroutine
    def updateStatus(self, arg):
        num = yield self.index_model.updateStatus(arg)
        raise Return(num)