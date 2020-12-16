import json
from app.models import Province, City, Area
from app import db
import os


def insert_data(path):
    with open(path, 'r', encoding='utf-8') as json_file:
        json_file_text = json_file.read()
        json_text = json.loads(json_file_text)
        for keys in json_text.keys():
            print(keys)
            province = Province(name=keys)
            db.session.add(province)
            db.session.commit()
            for key2 in json_text[keys].keys():
                print('\t' + key2, end='\n\t\t')
                city = City(name=key2, province_id=province.id)
                db.session.add(city)
                db.session.commit()
                for index in json_text[keys][key2]:
                    print(index, end=', ')
                    area = Area(name=index, city_id=city.id)
                    db.session.add(area)
                    db.session.commit()
            print('\n')


if __name__ == '__main__':
    basedir = os.path.abspath(os.path.dirname(__file__))
    print(basedir)
    a = ['a', 'b', 'asd']
    print(a.__len__())

