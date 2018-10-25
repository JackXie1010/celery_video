# coding: utf8
import os
import oss2
import requests
import sys

ossAccessKeyId = 'xxxx'
ossAccessKeySecret = 'xxxxx'
endpoint = 'oss-cn-shanghai.aliyuncs.com'
bucketName = 'video-backups'
bucket = oss2.Bucket(oss2.Auth(ossAccessKeyId, ossAccessKeySecret), endpoint, bucketName)
path = os.path.dirname(os.path.dirname(__file__))


def percentage(consumed_bytes, total_bytes):
    # 进度条回调函数， 计算当前完成的百分比:param content: 文件内容 :return 文件名
    if total_bytes:
        rate = int(100*(float(consumed_bytes) / float(total_bytes)))
        print('已上传{}%'.format(rate))
        sys.stdout.flush()


def uploadLocalFileToOss(vvurl, name):
    youtube_res = os.popen('youtube-dl -f 18 ' + vvurl)
    youtube_res = youtube_res.read()
    print(youtube_res, '-------youtube res-----------')
    # if 0 == youtube_res or 1 == youtube_res:
    if '100%' in youtube_res:
        file_list = os.listdir(os.path.dirname(os.path.dirname(__file__)))
        for v in file_list:
            if '.mp4' in v:
                try:
                    try:
                        pathname = path + '/' + v
                        ret = oss2.resumable_upload(bucket, name, pathname, part_size=100*1024, num_threads=5, progress_callback=percentage)
                    except:
                        pathname = path + '/' + v
                        ret = oss2.resumable_upload(bucket, name, pathname, part_size=100 * 1024, num_threads=5, progress_callback=percentage)
                except Exception:
                    print('file name have chinese')
                    pathname = path + '/' + v.decode('gbk')
                    ret = oss2.resumable_upload(bucket, name, pathname, part_size=100 * 1024, num_threads=5, progress_callback=percentage)
                rm = os.remove(path + '/' + v) if ret else 0
                if rm: os.remove(path + '/' + v)
                if ret: print('%s上传成功-----------' % vvurl)
        res = 1 if ret else 0
    else:
        print('%s下载失败----------------'% vvurl)
        res = 0
    return res


def uploadNetFileToOss(img, img_name):
    print('-----------------------------------------start upload vimg---------------------------------------------')
    auth = oss2.Auth(ossAccessKeyId, ossAccessKeySecret)
    bucket = oss2.Bucket(auth, endpoint, bucketName)
    input = requests.get(img)
    ret = bucket.put_object(img_name, input)
    # print(ret)
    return ret


def get_oss_url(name):
    auth = oss2.Auth(ossAccessKeyId, ossAccessKeySecret)
    bucket = oss2.Bucket(auth, endpoint, bucketName)
    url = bucket.sign_url('GET', name, 3600)
    url = 'https' + url[4:]
    return url


if __name__ == '__main__':
    url = get_oss_url('sJtl5OFAUAA.mp4')
    print(url)


