# 错误处理
from flask import render_template, flash, redirect, url_for
from . import main
from flask_login import current_user


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@main.app_errorhandler(413)
def file_to_big(e):
    flash('您上传的文件超过限制，请重新上传')
    print(e)
    return redirect(url_for('main.user', username=current_user.username)), 413

