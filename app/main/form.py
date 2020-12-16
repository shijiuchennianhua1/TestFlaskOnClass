# 表单
from wtforms import StringField, SubmitField, FileField, MultipleFileField
from wtforms.validators import DataRequired, Length, Regexp, ValidationError
from flask_wtf import FlaskForm
from ..models import User
from flask_pagedown.fields import PageDownField
from flask_wtf.file import FileRequired, FileAllowed
from .. import files, avatar, pictures


class NameForm(FlaskForm):
    name = StringField('你的名字?', validators=[DataRequired(message='请输入你的名字')])
    submit = SubmitField('Submit')


class UpdatePersonalInformationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='请输入用户名'), Length(1, 64),
                                              Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, '用户名只能包含字母，数字，点或下划线')])
    submit = SubmitField('确认')

    @staticmethod
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被占用')


class ChangeUserInformationForm(FlaskForm):
    nickname = StringField('昵称', validators=[DataRequired(message='请输入昵称'), Length(1, 64)])


class WhiteReview(FlaskForm):
    review = StringField('评论', validators=[DataRequired(message='请输入评论'), Length(1, 200)])
    submit = SubmitField('确认')


class WhiteTools(FlaskForm):
    title = StringField('标题', validators=[DataRequired('请输入标题'), Length(1, 50)])
    introduction = StringField('工具的简介', validators=[DataRequired('请输入工具的简介'), Length(1, 300)])
    contents = PageDownField('工具的详细介绍', validators=[DataRequired('请输入工具的详细介绍')])
    pictures = MultipleFileField('上传介绍图片', validators=[FileAllowed(pictures, message='只能上传图片')])
    file = FileField('上传工具', validators=[FileRequired(), FileAllowed(files)])
    submit = SubmitField('确认')
