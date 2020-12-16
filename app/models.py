import hashlib
from datetime import datetime

import bleach
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from . import login_manager


class Permissions:
    """权限常量

    :Attribute FOLLOW: 关注用户权限
    :Attribute DOWNLOAD: 下载附件权限
    :Attribute COMMIT: 在他人的文章中发表评论
    :Attribute WRITE: 写文章
    :Attribute MODERATE: 管理他人发表的评论
    :Attribute ADMIN: 管理员权限
    """
    FOLLOW = 1
    DOWNLOAD = 2
    COMMIT = 4
    WRITE = 8
    MODERATE = 16
    ADMIN = 32


class Role(db.Model, UserMixin):
    """用户身份"""
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    user = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        """在未给构造函数提供参数时，把permissions字段的值设为0

        :param kwargs:参数
        """
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return '<Role %r>' % self.name

    def has_permission(self, perm):
        """检查是否包含权限perm

        :param perm: 要检查的是否已经存在的权限
        :return:包含返回True，不包含返回False
        """
        return self.permissions & perm == perm

    def add_permission(self, perm):
        """ 添加权限

        :param perm:要添加的权限
        """
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        """删除权限

        :param perm:要删除的权限
        """
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self):
        """重置权限"""
        self.permissions = 0

    @staticmethod
    def insert_roles():
        """向数据库中插入几个角色"""
        roles = {
            'User': [Permissions.FOLLOW, Permissions.COMMIT, Permissions.WRITE, Permissions.DOWNLOAD],
            'Moderator': [Permissions.FOLLOW, Permissions.COMMIT, Permissions.WRITE, Permissions.MODERATE,
                          Permissions.DOWNLOAD],
            'Administrator': [Permissions.FOLLOW, Permissions.COMMIT, Permissions.WRITE, Permissions.MODERATE,
                              Permissions.ADMIN, Permissions.DOWNLOAD],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permission()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


class Follows(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_time = db.Column(db.DateTime(), default=datetime.utcnow(), index=True)


class User(db.Model, UserMixin):
    """用户"""
    default_location = '北京'
    default_province = '北京市'
    default_city = '市辖区'
    default_area = '东城区'
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    __password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    email = db.Column(db.String(64), unique=True, index=True)
    confirmed = db.Column(db.Boolean, default=False)
    # 昵称
    nickname = db.Column(db.String(64))
    province = db.Column(db.String(64), default=default_province)
    city = db.Column(db.String(64), default=default_city)
    area = db.Column(db.String(64), default=default_area)
    about_me = db.Column(db.Text())
    # 注册日期, db.Column的default可以接收函数作为默认值，每次需要生成默认值的时候都会调用这个函数
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    # 最后访问日期
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    # 头像
    avatar_name = db.Column(db.String(64), unique=True)
    fans_number = db.Column(db.Integer, index=True, default=0)
    followed_number = db.Column(db.Integer, index=True, default=0)
    tools = db.relationship('Tools', backref='auth')
    comments = db.relationship('Comments', backref='auth')
    followed = db.relationship('Follows', foreign_keys=[Follows.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')
    follower = db.relationship('Follows', foreign_keys=[Follows.followed_id],
                               backref=db.backref('followed', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role_id is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role_id = Role.query.filter_by(name='Administrator').first()
            if self.role_id is None:
                self.role_id = Role.query.filter_by(default=True).first().id
        self.fans_number = self.follower.count()
        self.followed_number = self.followed.count()

    def __repr__(self):
        return '<User %r>' % self.username

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    @property
    def password(self):
        """当访问password属性时提示"""
        raise AttributeError('密码不可见!')

    @password.setter
    def password(self, password):
        """设定密码，传入密码原文加密后存储到password_hash中

        :param password:密码原文
        """
        self.__password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """ 验证传入的密码

        :param password:需要验证的密码
        :return:密码验证是否通过
        """
        return check_password_hash(self.__password_hash, password)

    def get_password_hash(self):
        """获取密码的hash值

        :return:存储在User中的密码的hash值
        """
        return self.__password_hash

    def change_password(self, new_password):
        """更改密码

        :param new_password:新密码
        """
        self.__password_hash = generate_password_hash(new_password)

    def can(self, perm):
        """检查用户是否有perm权限

        :param perm: 要检查的权限
        :return: 用户权限字段有数据且权限中有perm权限
        """
        role = Role.query.filter_by(id=self.role_id).first()
        return role is not None and role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permissions.ADMIN)

    def ping(self):
        """生成最后访问时间"""
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def is_following(self, user):
        """判断是否关注user了

        :param user: 要判断的用户
        :return:是否关注user
        """
        if user is None:
            return False
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed(self, user):
        """判断是否被user关注

        :param user:要判断的用户
        :return:是否被user关注
        """
        if user is None:
            return False
        return self.follower.filter_by(follower_id=user.id).first() is not None

    def follow(self, user):
        """关注用户

        :param user:将被关注的用户
        """
        if not self.is_following(user):
            f = Follows(follower=self, followed=user, followed_time=datetime.utcnow())
            db.session.add(f)
            self.followed_number += 1
            user.fans_number += 1
            db.session.commit()

    def unfollow(self, user):
        """取消关注

        :param user:将要被取关的用户
        """
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            self.followed_number -= 1
            user.fans_number -= 1
            db.session.commit()

    # def follower_number(self):
    #     """获取粉丝数量
    #
    #     :return:粉丝数量
    #     """
    #     return self.follower.count()
    #
    # def followed_number(self):
    #     """获取你关注的用户的数量
    #
    #     :return:你关注的用户的数量
    #     """
    #     return self.followed.count()


class AnonymousUser(AnonymousUserMixin):
    """匿名用户"""
    def can(self, permission):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Province(db.Model):
    __tablename__ = 'provinces'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)


class City(db.Model):
    __tablename__ = 'city'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'), index=True)


class Area(db.Model):
    __tablename__ = 'areas'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), index=True)


class Tools(db.Model):
    __tablename__ = 'tools'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    contents = db.Column(db.Text())
    contents_html = db.Column(db.Text())
    file_name = db.Column(db.String(64), index=True)
    file_old_name = db.Column(db.String(256), index=True)
    title = db.Column(db.String(20), index=True)
    introduction = db.Column(db.String(300))
    upload_time = db.Column(db.DateTime(), default=datetime.utcnow(), index=True)
    comments = db.relationship('Comments', backref='tools')
    pictures = db.relationship('Pictures', backref='tools')

    @staticmethod
    def on_changed_contents(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.contents_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'), tags=allowed_tags, strip=True))


db.event.listen(Tools.contents, 'set', Tools.on_changed_contents)


class Comments(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), index=True)
    contents = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    upload_time = db.Column(db.DateTime(), default=datetime.utcnow(), index=True)


class Pictures(db.Model):
    __tablename__ = 'pictures'
    id = db.Column(db.Integer, primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tools.id'), index=True)
    file_name = db.Column(db.String(64), index=True)


# TODO 添加Tag表， tools-tags表, Tags表与Tools表多对多关系

