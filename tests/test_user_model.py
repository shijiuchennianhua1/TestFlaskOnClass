import unittest
from app.models import User, Permissions, AnonymousUser


class UserModelTestCase(unittest.TestCase):

    def test_password_setter(self):
        """测试password是否可以成功赋值"""
        u = User(password='cat')
        self.assertTrue(u.get_password_hash() is not None)

    def test_no_password_getter(self):
        """测试直接获取password会弹出报错"""
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password()

    def test_password_verification(self):
        """测试密码验证功能是否正确"""
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        """测试生成的密码hash值是不是随机的"""
        u1 = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u1.get_password_hash() != u2.get_password_hash())

    def test_user_role(self):
        """测试用户默认身份是否正确"""
        u = User(password='cat')
        self.assertTrue(u.can(Permissions.FOLLOW))
        self.assertTrue(u.can(Permissions.COMMIT))
        self.assertTrue(u.can(Permissions.WRITE))
        self.assertFalse(u.can(Permissions.ADMIN))
        self.assertFalse(u.can(Permissions.MODERATE))

    def test_anonymous_user(self):
        """测试匿名用户身份是否正确"""
        u = AnonymousUser()
        self.assertFalse(u.can(Permissions.FOLLOW))
        self.assertFalse(u.can(Permissions.COMMIT))
        self.assertFalse(u.can(Permissions.WRITE))
        self.assertFalse(u.can(Permissions.MODERATE))
        self.assertFalse(u.can(Permissions.ADMIN))




