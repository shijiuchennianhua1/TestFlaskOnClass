__all__ = ['email', 'models', 'auth', 'mail', 'moment', 'main']
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class, ALL
from flask_pagedown import PageDown

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
avatar = UploadSet('avatar', IMAGES)
files = UploadSet('files', ALL)
pictures = UploadSet('pictures', IMAGES)
page_down = PageDown()

login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    # config[config_name] : config.py文件中定义的字典config
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    page_down.init_app(app)

    configure_uploads(app, [avatar, files, pictures])
    patch_request_class(app, app.config['MAX_CONTENT_LENGTH'])

    # 从main目录引入main对象 —— main是一个蓝本对象
    from .main import main as main_blueprint
    from .auth import auth as auth_blueprint
    # 注册蓝本
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    return app

