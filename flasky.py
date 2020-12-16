import os
from app import create_app, db
from app.models import User, Role
from flask_migrate import Migrate
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class

total_app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(total_app, db)


@total_app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@total_app.cli.command()
def test():
    """运行单元测试, 函数名就是命令行的命令"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    total_app.run(debug=1)
