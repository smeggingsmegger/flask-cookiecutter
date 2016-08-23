import pytest

from {{cookiecutter.app_name}} import create_app
from {{cookiecutter.app_name}}.models import db, User, Role
from {{cookiecutter.app_name}}.mixin import safe_commit


@pytest.fixture()
def testapp(request):
    app = create_app('{{cookiecutter.app_name}}.settings.TestConfig')
    client = app.test_client()

    db.app = app
    db.create_all()

    if getattr(request.module, "create_user", True):
        admin = User(username="admin", password="supersafepassword")
        admin.insert()
        my_role = Role(name='admin')
        my_role.insert()
        admin.add_roles('admin')

        non_admin = User(username="non_admin", password="supersafepassword")
        non_admin.insert()

        safe_commit()

    def teardown():
        db.session.remove()
        db.drop_all()

    request.addfinalizer(teardown)

    return client
