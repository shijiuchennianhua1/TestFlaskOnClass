import unittest
from app.models import Role, Permissions


class RoleModelTestCase(unittest.TestCase):
    def test_has_permission(self):
        """测试三个关于权限的方法是否正确"""
        r = Role(name='User')
        r.add_permission(Permissions.FOLLOW)
        r.add_permission(Permissions.ADMIN)
        r.add_permission(Permissions.MODERATE)
        self.assertTrue(r.has_permission(Permissions.FOLLOW))
        self.assertTrue(r.has_permission(Permissions.ADMIN))
        self.assertTrue(r.has_permission(Permissions.MODERATE))
        self.assertFalse(r.has_permission(Permissions.COMMIT))
        self.assertFalse(r.has_permission(Permissions.WRITE))
        r.remove_permission(Permissions.ADMIN)
        self.assertFalse(r.has_permission(Permissions.ADMIN))
        r.reset_permission()
        self.assertFalse(r.has_permission(Permissions.FOLLOW))
        self.assertFalse(r.has_permission(Permissions.MODERATE))
