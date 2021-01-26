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

    time_format = '%d-%m-%Y:%H-%M-%S'
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    CAMS_YML = os.environ.get("CAMS_YML", "./cams.yml")


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    IMAGE_EXPIRE_TIME = 90


class BenchmarkConfig(Config):
    REDIS_PREFIX = 'wilsa'
    REDIS_HOST = os.environ.get('REDIS_HOST', 'newplunder')
    REDIS_PORT = 6379
    REDIS_DB = 0


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
    'benchmark': BenchmarkConfig
}
