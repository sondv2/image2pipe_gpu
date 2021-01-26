import logging
import multiprocessing
from multiprocessing import Queue
import redis
import cv2
import numpy as np
import image2pipe_gpu
from tqdm import tqdm
import yaml
import sys
from config import Config
import gevent
import signal
import traceback

cam_feeders = {}
greenthreads = []
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


def spawn(rdb, queue: Queue, cam_name: str, cam_url: str):
    # Redis channel
    t = tqdm(None, desc='%s - %s' % (cam_name, 0), leave=True)
    redis_channel = '{}/frame'.format(cam_name)
    while True:
        try:
            fn, img = queue.get()
            ret, buf = cv2.imencode('.jpg', img)
            img_bytes = np.array(buf).tostring()
            rdb.rpush(redis_channel, img_bytes)
            t.set_description('%s - %s' % (cam_url, fn))
            t.refresh()
        except Exception as ex:
            print("End %s" % cam_url)
            # sys.exit()


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

    global greenthreads

    # Create every cam feeder
    for cam_name, cam in cams.items():
        print('Adding cam {0} to the dict'.format(cam_name))
        cam_url = cam.get('cam_url')
        fps = cam.get('fps')

        queue = Queue()
        cf = image2pipe_gpu.images_from_url(q=queue, video_url=cam_url, fps=fps, scale=(1920, 1080))
        cf.start()

        p = multiprocessing.Process(target=spawn, args=(rdb, queue, cam_name, cam_url))
        p.start()

    watchdog(rdb)
    # gevent.sleep(15)
    # print(cf.is_alive())
    # print(p.is_alive())

    # # Create the watchdog
    # g = gevent.spawn(watchdog, rdb)
    # greenthreads.append(g)
    #
    # # Wait for greenlets
    # for g in greenthreads:
    #     g.join()


if __name__ == '__main__':
    main()
    print('_____________Finish_____________')
