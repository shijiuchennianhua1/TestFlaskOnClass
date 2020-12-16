from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, SelectField, TextAreaField, \
    FileField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from app.models import User, Province, City, Area, Role
from .. import avatar


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('保持我的登录状态')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(message='请输入邮箱'), Length(1, 64),
                                          Email(message='请输入正确的邮箱!')])
    username = StringField('用户名', validators=[DataRequired(message='请输入用户名'), Length(1, 64),
                                              Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名只能包含字母，数字，点或下划线')])
    password = PasswordField('密码', validators=[DataRequired(message='请输入密码'),
                                               EqualTo('password2', message='密码必须一致!')])
    password2 = PasswordField('确认密码', validators=[DataRequired(message='请确认密码')])
    submit = SubmitField('注册')

    @staticmethod
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    @staticmethod
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被占用')


class ForgetPasswordEmailForm(FlaskForm):
    """忘记密码用户的邮箱"""
    email = StringField('邮箱', validators=[DataRequired(message='请输入邮箱'), Length(1, 64), Email()])
    submit = SubmitField('确认')

    @staticmethod
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('请输入正确的邮箱!')


class ForgetPasswordResetPasswordForm(FlaskForm):
    """忘记密码重置密码"""
    old_password = PasswordField('旧密码', validators=[DataRequired(message='请输入旧密码')])
    new_password = PasswordField('新密码', validators=[DataRequired(message='请输入新密码'),
                                                    EqualTo('re_new_password', message='两次密码必须保持一致')])
    re_new_password = PasswordField('重复新密码', validators=[DataRequired(message='请重复新密码')])
    submit = SubmitField('确认')


class ResetEmailForm(FlaskForm):
    """重设邮箱"""
    new_email = StringField('新邮箱', validators=[DataRequired(message='请输入新邮箱'), Length(1, 64), Email()])
    submit = SubmitField('确认')

    @staticmethod
    def validate_new_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')


class UpdateUserInformationForm(FlaskForm):
    """修改用户资料"""
    nickname = StringField(u'昵称', validators=[Length(0, 20, message='昵称长度必须在0~20个字符之间')])
    province = SelectField('省', coerce=str, default=0, validators=[DataRequired(message='请选择您所在的省')])
    city = SelectField('市', coerce=str, default=0, validators=[DataRequired(message='请选择您所在的市')])
    area = SelectField('区', coerce=str, default=0, validators=[DataRequired(message='请选择您所在的区')])
    about_me = TextAreaField(u'关于我', validators=[Length(0, 300, message='超出字数限制(300字)!')])
    role = SelectField('身份', coerce=str, default=0, validators=[DataRequired()])
    avatar = FileField('上传头像', validators=[FileAllowed(avatar, '只能上传图片!')])
    submit = SubmitField(u'确认')
    
    def __init__(self, *args, **kwargs):
        super(UpdateUserInformationForm, self).__init__(*args, **kwargs)
        self.province.choices = [('', '')]
        for province in Province.query.order_by(Province.id).all():
            self.province.choices.append((province.name, province.name))
        self.city.choices = [('', '')]
        for city in City.query.order_by(City.id).all():
            self.city.choices.append((city.name, city.name))
        self.area.choices = [('', '')]
        for area in Area.query.order_by(Area.id).all():
            self.area.choices.append((area.name, area.name))
        self.role.choices = []
        for role in Role.query.order_by(Role.id).all():
            self.role.choices.append((role.id, role.name))
