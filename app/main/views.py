# 路由处理
import json
import os
from datetime import datetime

from flask import make_response, abort, render_template, url_for, redirect, flash, current_app, \
    send_from_directory, request, jsonify
from flask_login import current_user, login_required

from app.main.form import UpdatePersonalInformationForm, WhiteReview, WhiteTools
from . import main
from .map import get_map_location
from .. import db, files, pictures
from ..decorators import admin_required, permission_required
from ..models import Permissions
from ..models import User, Tools, Comments, Pictures
from ..redirect_back import redirect_back


@main.route('/', methods=['POST', 'GET'])
@main.route('/index', methods=['POST', 'GET'])
@main.route('/index/<int:number>', methods=['POST', 'GET'])
@main.route('/index/<int:number>/<int:show_type>', methods=['POST', 'GET'])
@main.route('/index/<int:number>/<int:show_type>/<int:id>', methods=['POST', 'GET'])
def index(number=1, show_type=0, id=-1):
    global tools, search
    global tools_number
    if request.method == 'GET':
        if request.args.get('isDeal') != 'false' or not request.args.get('isDeal'):
            search = request.args.get('search')
            if search:
                search = list(search)
                search_num = search.__len__()
                for i in range(0, search_num):
                    search.insert(i+i, '%')
    response = make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('answer', '42')
    if show_type == 0:
        if search:
            tools = Tools.query.filter(Tools.title.ilike(''.join(search)+'%')).order_by(Tools.upload_time.desc()).\
                offset((number-1)*10).limit(10).all()
            tools_number = Tools.query.filter(Tools.title.ilike(''.join(search)+'%')).count()
        else:
            tools = Tools.query.order_by(Tools.upload_time.desc()).offset((number-1)*10).limit(10).all()
            tools_number = Tools.query.count()
    elif show_type == 1:
        followed = current_user.followed.all()
        user_id = []
        for follow in followed:
            user_id.append(follow.followed.id)
        if search:
            tools = Tools.query.filter(Tools.title.ilike(''.join(search) + '%')).filter(Tools.user_id.in_(user_id)).\
                order_by(Tools.upload_time.desc()).offset((number-1)*10).limit(10).all()
            tools_number = Tools.query.filter(Tools.title.ilike(''.join(search) + '%')).\
                filter(Tools.user_id.in_(user_id)).count()
        else:
            tools = (Tools.query.filter(Tools.user_id.in_(user_id)).order_by(Tools.upload_time.desc())).\
                offset((number-1)*10).limit(10).all()
            tools_number = Tools.query.filter(Tools.user_id.in_(user_id)).count()
    elif show_type == 2:
        if id == -1:
            id = current_user.id
        if search:
            tools = Tools.query.filter(Tools.title.ilike(''.join(search) + '%')).filter_by(user_id=id).order_by(Tools.upload_time.desc()).\
                offset((number-1)*10).limit(10).all()
            tools_number = Tools.query.filter(Tools.title.ilike(''.join(search) + '%')).filter_by(user_id=id).count()
        else:
            tools = Tools.query.filter_by(user_id=id).order_by(Tools.upload_time.desc()).\
                offset((number-1)*10).limit(10).all()
            tools_number = Tools.query.filter_by(user_id=id).count()
    pagination_show_number = 5
    for i, tool in enumerate(tools):
        tools[i] = [tool, tool.auth]
    if tools_number % 10 != 0:
        page_number = int(tools_number / 10) + 1
    else:
        page_number = tools_number / 10
    users = User.query.order_by(User.fans_number.desc()).limit(10).all()
    if search:
        search = ''.join(search)
    return render_template('index.html', content='FLASK', user=current_user, tools=tools, pageNumber=int(page_number),
                           current_number=number, pagination_show_number=pagination_show_number, users=users,
                           show_type=show_type, search=search)


@main.route('/user/<string:username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    # 坐标
    coordinate = get_map_location(user.province+user.city+user.area)
    return render_template('user.html', user=user, coordinate=coordinate, current_app=current_app)


@main.route('/user1/<id>')
@login_required
def user1(id):
    user = None
    if not user:
        print(123)
        abort(404)
    return 'User:{}'.format(id)


@main.route('/updateUserInformation', methods=['GET', 'POST'])
@login_required
def update_user_information():
    form = UpdatePersonalInformationForm()
    user = current_user
    if form.validate_on_submit():
        user.username = form.username.data
        db.session.commit()
        flash('用户名修改成功')
        return redirect(url_for('main.index'))
    return render_template('updateLoginInformation.html', user=user, form=form)


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return 'For administrators!'


@main.route('/moderator')
@login_required
@permission_required(Permissions.MODERATE)
def for_moderators_only():
    return 'For comment moderators!'


@main.route('/tools/<int:tool_id>', methods=['GET', 'POST'])
def tools_show(tool_id):
    tool = Tools.query.filter_by(id=tool_id).first()
    form = WhiteReview()
    if form.validate_on_submit():
        comment = Comments(tool_id=tool_id, user_id=current_user.id, contents=form.review.data,
                           upload_time=datetime.utcnow())
        db.session.add(comment)
        db.session.commit()
        flash('评论提交成功')
        return redirect(url_for('main.tools_show', tool_id=tool_id))
    return render_template('tool.html', tool=tool, form=form, current_user=current_user)


@main.route('/download/<int:tool_id>', methods=['GET', 'POST'])
@login_required
def download(tool_id):
    filename = Tools.query.filter_by(id=tool_id).first().file_name
    return send_from_directory(current_app.config['UPLOADED_FILES_DEST'], filename, as_attachment=True)


@main.route('/follow/<int:user_id>')
@login_required
def follow(user_id):
    followed_user = User.query.filter_by(id=user_id).first()
    current_user.follow(followed_user)
    flash('关注成功')
    return redirect_back()


@main.route('/unFollow/<int:user_id>')
@login_required
def un_follow(user_id):
    un_followed_user = User.query.filter_by(id=user_id).first()
    current_user.unfollow(un_followed_user)
    flash('取关成功')
    return redirect_back()


@main.route('/uploadTool', methods=['GET', 'POST'])
@login_required
@permission_required(Permissions.WRITE)
def upload_tool():
    form = WhiteTools()
    if form.validate_on_submit():
        file = form.file.data
        file_old_name = file.filename[0:256]
        file.filename = datetime.now().strftime("%Y%m%d%H%M%S") + os.path.splitext(file.filename)[-1]
        name = files.save(file)
        tool = Tools(user_id=current_user.id, contents=form.contents.data, file_name=name, title=form.title.data,
                     upload_time=datetime.utcnow(), introduction=form.introduction.data, file_old_name=file_old_name)
        db.session.add(tool)
        db.session.commit()
        # 将小工具对应的图片上传到数据库
        picture_list = form.pictures.data
        for picture in picture_list:
            picture.filename = datetime.now().strftime("%Y%m%d%H%M%S") + os.path.splitext(picture.filename)[-1]
            picture_name = pictures.save(picture)
            pic = Pictures(tool_id=tool.id, file_name=picture_name)
            db.session.add(pic)
            db.session.commit()
        flash('上传成功!')
        return redirect(url_for('main.tools_show', tool_id=tool.id))
    return render_template('uploadTool.html', form=form)


@main.route('/changeIndexModel', methods=['GET', 'POST'])
def change_index_model():
    if request.method == 'POST':
        verification = json.loads(request.data)
        if verification == 0:
            tools = Tools.query.order_by(Tools.upload_time.desc()).all()
            tools_id = [tool.id for tool in tools]
            return jsonify(tools_id)
        elif verification == 1:
            followed = current_user.followed.all()
            user_id = []
            for follow in followed:
                user_id.append(follow.followed.id)
            tools = Tools.query.filter(Tools.id.in_(user_id)).order_by(Tools.upload_time.desc()).all()
            tools_id = [tool.id for tool in tools]
            return jsonify(tools_id)
        elif verification == 2:
            tools = Tools.query.filter_by(id=current_user.id).order_by(Tools.upload_time.desc()).all()
            tools_id = [tool.id for tool in tools]
            return jsonify(tools_id)
        else:
            tools = []
            return jsonify(tools)



@main.app_context_processor
def inject_permission():
    """模板上下文，定义一个字典对所有模板可见

    :return: 一个字典 -- {'Permissions' : <class 'app.models.Permissions'>}
    """
    return dict(Permissions=Permissions)

