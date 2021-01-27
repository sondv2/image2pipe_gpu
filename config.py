import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    FFMPEG_BIN = os.environ.get("FFMPEG_BIN", "/usr/local/bin/ffmpeg")

    # Path to the cams definition file
    CAMS_YML = os.environ.get("CAMS_YML", "./cams.yml")

    REDIS_PREFIX = 'producer'
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_DB = 0
    SCALE = scale = (1920, 1080)
    IMAGE_EXPIRE_TIME = 180
    FTIME = '%d-%m-%Y:%H-%M-%S'
