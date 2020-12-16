from urllib.request import urlopen, quote
import json
import requests


def get_map_location(address):
    """根据传入的地址返回对应的地址编码

    :param address:详细地址
    :return:对应地点的地址编码
    """
    url = 'https://restapi.amap.com/v3/geocode/geo'
    output = 'json'
    key = '51087efef5b53e73d939bad91cf21a40'
    address = quote(address)
    uri = url + '?address=' + address + '&output=' + output + '&key=' + key
    # print(uri)
    res = requests.get(uri).text
    json_text = json.loads(res)
    return json_text['geocodes'][0]['location']

