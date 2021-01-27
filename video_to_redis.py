import logging
import multiprocessing
from multiprocessing import Queue
import redis
import cv2
import numpy as np
import image2pipe
from tqdm import tqdm
import yaml
import sys
from config import Config
import gevent
import signal
import os
import json
import base64
from psutil import virtual_memory


logging.basicConfig()

def signal_handler(signal, frame):
    print('Now exiting...')
    sys.exit(0)


def watchdog(rdb):
    """
    :param rdb: Redis connection
    :type rdb: redis.StrictRedis
    :return:
    """
    while True:
        rdb.setex(Config.REDIS_PREFIX + ":feeder:alive", 5, 1)
        gevent.sleep(5)


def producer(rdb, queue: Queue, cam_name=None, cam_url=None, fps=None):

    # Redis channel
    t = tqdm(None, desc='file= %s\tframe= %s\ttime=%s' % (None, 0, 0), leave=True)
    redis_channel = '{}/frame'.format(cam_name)

    while True:
        try:
            fn, img = queue.get()
            if fn == -1:
                file_name = img
                continue
            ret, buf = cv2.imencode('.jpg', img)
            img_bytes = np.array(buf).tostring()

            # rdb.rpush(redis_channel, img_bytes)
            image = base64.b64encode(img_bytes)
            mydict = {
                'file': file_name,
                'time': fn / fps,
                'data': image.decode()
            }
            jdict = json.dumps(mydict)
            rdb.rpush(redis_channel, jdict)

            t.set_description('file= %s\tframe= %s\ttime=%s' % (file_name, fn, fn / fps))
            t.refresh()
        except Exception as ex:
            print("EOF %s" % file_name)
            # sys.exit()
def out_of_memory():
    mem = virtual_memory()
    while mem.free <= 2048 * 10 ** 6:
        print('Out of memory')
        gevent.sleep(5)


def main():

    # Register exit handler
    signal.signal(signal.SIGINT, signal_handler)
    # print('Press Ctrl+C to exit.')

    # Load the cameras configuration
    data = yaml.load(open(Config.CAMS_YML, 'r'))
    cams = data['cams']  # type: dict
    print("Loaded {}".format(Config.CAMS_YML))

    # Connect to the redis instance
    rdb = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB, decode_responses=True)
    # TODO: Consider whether we should read in some other way.
    # Clear keys so that the stats are right.
    for key in rdb.scan_iter("{}:*".format(Config.REDIS_PREFIX)):
        # print("Deleting: {}".format(key))
        rdb.delete(key)

    # Create every cam feeder
    for cam_name, cam in cams.items():
        print('Adding cam {0} to the dict'.format(cam_name))
        cam_url = cam.get('cam_url')
        fps = cam.get('fps')

        queue = Queue()
        p = multiprocessing.Process(target=producer, args=(rdb, queue, cam_name, cam_url, fps))
        p.start()

        if os.path.isdir(cam_url):
            while True:
                lst_file = os.listdir(cam_url)
                for file in lst_file:
                    out_of_memory()
                    file_url = os.path.join(cam_url, file)
                    queue.put((-1, file))
                    cf = image2pipe.images_from_url(q=queue, video_url=file_url, fps=fps, scale=(1920, 1080))
                    cf.start()
                    while cf.is_alive() is True:
                        gevent.sleep(1)
                    os.remove(file_url)
                print('Wait for new file')
                gevent.sleep(5)
        elif os.path.isfile(cam_url):
            queue.put((-1, cam_url))
            cf = image2pipe.images_from_url(q=queue, video_url=cam_url, fps=fps, scale=(1920, 1080))
            cf.start()

    watchdog(rdb)


if __name__ == '__main__':
    main()
    print('_____________Finish_____________')
