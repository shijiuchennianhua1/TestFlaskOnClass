from . import mail
from flask_mail import Message
from flask import render_template
from threading import Thread
from config import Config


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    """发送邮件

    :param to:邮件发送的目的地址
    :param subject:邮件主题
    :param template:邮件主体模板路径
    :param kwargs:其他邮件主体模板必要的参数
    :return:线程
    """
    msg = Message(Config.FLASKY_MAIL_SUBJECT_PREFIX + subject
                  , sender=Config.FLASK_MAIL_SENDER, recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    from flasky import total_app
    thr = Thread(target=send_async_email, args=[total_app, msg])
    thr.start()
    return thr
