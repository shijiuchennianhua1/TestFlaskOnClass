import unittest
from app.main.map import get_map_location


class GetMapLocationCase(unittest.TestCase):
    def test_get_map_location(self):
        """测试获取地址坐标是否正确"""
        contrast = '124.350398,43.166419'
        res = get_map_location('四平', '四平')
        self.assertTrue(res == contrast)
