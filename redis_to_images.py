import logging
import json
import cv2
import numpy as np
import redis
from config import Config
import base64
logging.basicConfig()

class redis_to_images():

    def get_redis_image(self, rdb):
        redis_channel = '{}/frame'.format('cam_54')
        while True:
            mydict = rdb.lpop(redis_channel)
            if mydict is None:
                return
            mydict = json.loads(mydict.decode("utf-8"))
            img_bytes = mydict['data']
            frame_bytes = base64.b64decode(img_bytes)
            img_bytes = np.frombuffer(frame_bytes, dtype=np.uint8)
            img = cv2.imdecode(img_bytes, flags=1)
            cv2.imshow("frame", img)
            cv2.waitKey(1)

if __name__ == '__main__':
    print("Running.")

    # Connect to the redis instance
    rdb = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB, decode_responses=False)

    redis_to_images().get_redis_image(rdb)
