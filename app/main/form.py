from wtforms import StringField, SubmitField 
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm



class NameForm(FlaskForm):
        name = StringField('你的名字?', validators=[DataRequired(message='请输入你的名字')])
        submit = SubmitField('Submit')