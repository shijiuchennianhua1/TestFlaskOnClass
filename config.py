import os
from flask_uploads import IMAGES
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dusk*DUGASK'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '465'))
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '3157684388@qq.com')
    # todo 这里应该只用环境变量， 不能使用显式赋值
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'inbrawhtarefdgjg')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASK_MAIL_SENDER = 'FLASKY Admin <3157684388@qq.com>'
    # todo 这里应该用环境变量，暂时使用显式赋值
    FLASK_ADMIN = '3157684388@qq.com'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_AVATAR_DEST = basedir+'\\app\\static\\file\\avatar\\'
    UPLOADED_FILES_DEST = basedir + '\\files\\toolFiles\\'
    UPLOADED_PICTURES_DEST = basedir + '\\app\\static\\file\\pictures\\'
    MAX_CONTENT_LENGTH = 1024 * 1024 * 1024
    UPLOADED_PHOTOS_ALLOW = IMAGES

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """ 开发者数据库配置.
    继承了Config类

    Attributes:
        DEBUG: 开启调试.
        SQLALCHEMY_DATABASE_URI: 数据库地址.
    """
    DEBUG = 1
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or 'postgresql://' \
                                                                    'chenxuan:zhimakaimen@127.0.0.1/devBlog'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URL = os.environ.get('TEST_DATABASE_URL') or 'postgresql://' \
                                                                     'chenxuan:zhimakaimen@127.0.0.1/testBlog'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL') or 'postgresql://chenxuan:zhimakaimen@127.0.0.1/pblog'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

if __name__ == '__main__':
    print(basedir+'\\static\\avatar')
