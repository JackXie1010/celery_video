# coding: utf8
import celery
import time
import oss
import index


broker = 'redis://localhost:6379/1'
backend = 'redis://localhost:6379/2'
app = celery.Celery('my_tasks', broker=broker, backend=backend)


@app.task
def downAndUpload(arg):
    print('----------------------------start downAndUpload---------------------')
    for obj in arg:
        img_name = str(int(time.time() * 1000)) + '.jpg'
        try:
            ret = oss.uploadLocalFileToOss(obj['vvurl'], obj['vpurl'])
            oss.uploadNetFileToOss(obj['vimg'], img_name)
        except:
            ret = ''
        if ret:
            obj['vimg'], obj['oss_status'] = img_name, 1
            num = index.UpdateStatus.updateStatus(obj)
            print('----------------update finish--------------', num)
            break