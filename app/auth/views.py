from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user

from app.redirect_back import redirect_back
from . import auth
from ..models import User, Province, City, Area, Follows
from .forms import LoginForm, RegistrationForm, ForgetPasswordEmailForm, ForgetPasswordResetPasswordForm, ResetEmailForm\
    , UpdateUserInformationForm
from .. import db, avatar
from ..email import send_email
from flask import jsonify, current_app
import json
from datetime import datetime
from werkzeug.datastructures import FileStorage
import os


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        flash('用户名或密码无效')
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data, username=form.username.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, '确认你的账号', 'auth/mail/confirm', user=user, token=token)
        flash('一个确认邮件已经发到了您的邮箱中')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('您已确认您的帐户。谢谢！')
    else:
        flash('确认链接无效或已过期。')
    return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已经登出了')
    return redirect(url_for('main.index'))


@auth.route('/secret')
@login_required
def secret():
    return '仅允许通过身份验证的用户通过'


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', user=current_user)


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, '确认您的账号', 'auth/mail/confirm',
               user=current_user, token=token)
    flash('一个新的确认邮件已经被发送到您的邮箱.')
    return redirect(url_for('main.index'))


@auth.route('/forgetPassword', methods=['GET', 'POST'])
def forget_password():
    form = ForgetPasswordEmailForm()
    if form.validate_on_submit():
        u = User.query.filter_by(email=form.email.data).first()
        send_email(form.email.data, '重置密码', 'auth/mail/forgetPassword'
                   , token=u.generate_confirmation_token(), email=u.email, user=u)
        flash('一个重置密码的文件已经被发送到了您的邮箱中，请注意查收.')
    return render_template('auth/forgetPassword/getEmail.html', form=form)


@auth.route('/forgetPassword/<token>/<email>', methods=['GET', 'POST'])
def forget_password_reset(token, email):
    form = ForgetPasswordResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user is not None and user.verify_password(form.old_password.data):
            user.change_password(form.new_password.data)
            db.session.commit()
            send_email(user.email, '密码已修改', 'auth/mail/passwordIsUpdate', user=user)
            return redirect(url_for('auth.login'))
        flash('密码错误!')
    return render_template('auth/resetPassword.html', form=form)


@auth.route('/updateUserInformation')
@login_required
def update_user_information_email():
    send_email(current_user.email, '修改邮箱', 'auth/mail/updateUserInfoEmail', user=current_user,
               token=current_user.generate_confirmation_token())
    flash('修改邮箱请求邮件已经发送到您的邮箱中，请注意查收')
    return redirect(url_for('main.update_user_information'))


@auth.route('/updateUserInformation/<token>/<email>', methods=['GET', 'POST'])
@login_required
def update_user_information_reset_email(token, email):
    user = User.query.filter_by(email=email).first()
    if not current_user.confirm(token):
        flash('验证失败')
        return redirect(url_for('main.index'))
    form = ResetEmailForm()
    if form.validate_on_submit():
        # 将验证状态转变为False
        user.confirmed = False
        user.email = form.new_email.data
        db.session.commit()
        send_email(form.new_email.data, '修改邮箱', 'auth/mail/confirm',  user=user, token=token)
        flash('一个验证邮件已经发送到了您的新邮箱中')
        return redirect(url_for('main.index'))
    return render_template('auth/resetEmail.html', form=form, email=email)


@auth.route('/updateUserInformationPassword', methods=['GET', 'POST'])
@login_required
def update_user_information_password():
    form = ForgetPasswordResetPasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.change_password(form.new_password.data)
            db.session.commit()
            flash('修改密码成功,请重新登录!')
            return redirect(url_for('auth.logout'))
        flash('密码错误!')
    return render_template('auth/resetPassword.html', form=form)


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/updateUserInfo/<username>', methods=['GET', 'POST'])
@login_required
def update_user_information(username):
    form = UpdateUserInformationForm()
    user = User.query.filter_by(username=username).first()
    if form.validate_on_submit():
        if current_user.is_administrator():
            user.role_id = form.role.data
        user.nickname = form.nickname.data
        user.province = form.province.data
        user.city = form.city.data
        user.area = form.area.data
        user.about_me = form.about_me.data
        if form.avatar.data is not None and form.avatar.data.filename != '':
            file = form.avatar.data
            file.filename = datetime.now().strftime("%Y%m%d%H%M%S") + os.path.splitext(file.filename)[-1]
            name = avatar.save(file)
            if user.avatar_name is not None:
                old_avatar_name = user.avatar_name
                user.avatar_name = name
                db.session.commit()
                os.remove(current_app.config['UPLOADED_AVATAR_DEST'] + old_avatar_name)
            else:
                user.avatar_name = name
        db.session.commit()
        flash('资料修改成功!')
        return redirect(url_for('main.index'))
    return render_template('updateUserInformation.html', form=form, user=user)


@auth.route('/selectCity', methods=['GET', 'POST'])
def select_city():
    if request.method == 'POST':
        data = json.loads(request.data)
        if data is not None:
            name = data['name']
            if name != '' and name is not None:
                province = Province.query.filter_by(name=name).first()
                citys = [city.name for city in City.query.filter_by(province_id=province.id).all()]
                return jsonify(citys)
            else:
                citys = []
                return jsonify(citys)
        else:
            citys = []
            return jsonify(citys)


@auth.route('/selectArea', methods=['GET', 'POST'])
def select_area():
    if request.method == 'POST':
        data = json.loads(request.data)
        if data is not None:
            name = data['name']
            if name != '' and name is not None:
                city = City.query.filter_by(name=name).first()
                areas = [area.name for area in Area.query.filter_by(city_id=city.id).all()]
                return jsonify(areas)
            else:
                areas = []
                return jsonify(areas)
        else:
            areas = []
            return jsonify(areas)


@auth.route('fansData/<int:user_id>/<int:page_number>')
def show_fans(user_id, page_number=1):
    per_page_number = 20
    user = User.query.filter_by(id=user_id).first()
    fans = user.follower.order_by(Follows.followed_time.desc()).paginate(page=page_number, per_page=per_page_number)
    return render_template('auth/showFans.html', fans_pagination=fans, user_id=user_id)


@auth.route('followedData/<int:user_id>/<int:page_number>')
def show_followed_users(user_id, page_number=1):
    per_page_number = 20
    user = User.query.filter_by(id=user_id).first()
    followed = user.followed.order_by(Follows.followed_time.desc()).paginate(page=page_number, per_page=per_page_number)
    return render_template('auth/showFollowed.html', fans_pagination=followed, user_id=user_id)

