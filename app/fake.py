from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Tools, Comments, Follows


def users(count=100):
    fake = Faker()
    i = 0
    while i < count:
        u = User(
            email=fake.email(),
            username=fake.user_name(),
            password='password',
            confirmed=True,
            about_me=fake.text(),
            member_since=fake.past_date(),
            nickname=fake.name())
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def tools(count=100):
    fake = Faker()
    i = 0
    user_count = User.query.count()

    while i < count:
        tool = Tools(
            user_id=User.query.offset(randint(0, user_count-1)).first().id,
            contents=fake.text(),
            title=fake.word(),
            upload_time=fake.past_date(),
            introduction=fake.text()
        )
        db.session.add(tool)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def comments(count=100):
    fake = Faker()
    i = 0
    tool_count = Tools.query.count()
    user_count = User.query.count()

    while i < count:
        comment = Comments(
            tool_id=Tools.query.offset(randint(0, tool_count-1)).first().id,
            contents=fake.text(),
            user_id=User.query.offset(randint(0, user_count-1)).first().id,
            upload_time=fake.past_date()
        )

        db.session.add(comment)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def comments_with_tool_id(count=100, tool_id=1):
    fake = Faker()
    i = 0
    user_count = User.query.count()

    while i < count:
        comment = Comments(
            tool_id=tool_id,
            contents=fake.text(),
            user_id=User.query.offset(randint(0, user_count-1)).first().id,
            upload_time=fake.past_date()
        )

        db.session.add(comment)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def follower_with_user_id(count=100, user_id=50):
    follower = User.query.filter_by(id=user_id).first()
    user_count = User.query.count()
    if count < user_count:
        users = User.query.limit(count).all()
    else:
        print('因为用户数量不足，只能添加'+str(user_count)+'个关注')
        users = User.query.all()
    for user in users:
        if user is follower:
            continue
        user.follow(follower)
    db.session.commit()


def follower():
    users = User.query.all()
    users_count = User.query.count()
    for user in users:
        follower_with_user_id(randint(0, users_count), user.id)
