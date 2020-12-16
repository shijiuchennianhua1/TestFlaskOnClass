# 创建蓝本main
__all__ = ['errors', 'form', 'views']
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors

