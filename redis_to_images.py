import logging

import cv2
import numpy as np
import redis

SCALE = scale = (320, 160)

VIDEO_URL = "data/cam_64_01-10-2020:21-00-00.mkv"

logging.basicConfig()

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

class redis_to_images():

    def get_redis_image(self, rdb):
        redis_channel = '{}/frame'.format('cam_64')
        i = 0
        while True:
            frame_bytes = rdb.lpop(redis_channel)
            img_bytes = np.frombuffer(frame_bytes, dtype=np.uint8)
            img = cv2.imdecode(img_bytes, flags=1)
            cv2.imshow("frame", img)
            cv2.waitKey(1)

if __name__ == '__main__':
    print("Running.")

    # Connect to the redis instance
    rdb = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=False)

    redis_to_images().get_redis_image(rdb)
