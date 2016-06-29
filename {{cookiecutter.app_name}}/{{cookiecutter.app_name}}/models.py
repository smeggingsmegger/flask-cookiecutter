import json

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from {{cookiecutter.app_name}}.mixin import OurMixin

db = SQLAlchemy()

from sqlalchemy.ext.associationproxy import association_proxy
# from {{cookiecutter.app_name}}.utils import uuid


def _role_find_or_create(r):
    role = Role.query.filter_by(name=r).first()
    if not(role):
        role = Role(name=r)
        db.session.add(role)
    return role


user_role_table = db.Table('user_role',
                           db.Column(
                               'user_id', db.VARCHAR(36),
                               db.ForeignKey('user.id')),
                           db.Column(
                               'role_id', db.VARCHAR(36),
                               db.ForeignKey('role.id'))
                           )

role_ability_table = db.Table('role_ability',
                              db.Column(
                                  'role_id', db.VARCHAR(36),
                                  db.ForeignKey('role.id')),
                              db.Column(
                                  'ability_id', db.VARCHAR(36),
                                  db.ForeignKey('ability.id'))
                              )


def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))


class Role(OurMixin, db.Model):

    """
    Subclass this for your roles
    """
    __tablename__ = 'role'
    id = db.Column(db.VARCHAR(length=36), primary_key=True)
    name = db.Column(db.String(120), unique=True)
    abilities = db.relationship(
        'Ability', secondary=role_ability_table, backref='roles')

    def __init__(self, name):
        self.name = name.lower()
        # self.id = uuid()
        super(Role, self).__init__()

    def add_abilities(self, *abilities):
        for ability in abilities:
            existing_ability = Ability.query.filter_by(
                name=ability).first()
            if not existing_ability:
                existing_ability = Ability(ability)
                db.session.add(existing_ability)
                #  db.session.commit()
            self.abilities.append(existing_ability)

    def remove_abilities(self, *abilities):
        for ability in abilities:
            existing_ability = Ability.query.filter_by(name=ability).first()
            if existing_ability and existing_ability in self.abilities:
                self.abilities.remove(existing_ability)

    def __repr__(self):
        return '<Role {}>'.format(self.name)

    def __str__(self):
        return self.name


class Ability(OurMixin, db.Model):

    """
    Subclass this for your abilities
    """
    __tablename__ = 'ability'

    id = db.Column(db.VARCHAR(length=36), primary_key=True)
    name = db.Column(db.String(120), unique=True)

    def __init__(self, name):
        self.name = name.lower()
        # self.id = uuid()
        super(Ability, self).__init__()

    def __repr__(self):
        return '<Ability {}>'.format(self.name)

    def __str__(self):
        return self.name


class ApiKey(OurMixin, db.Model):
    __tablename__ = 'api_key'

    id = db.Column(db.VARCHAR(length=36), primary_key=True)
    key = db.Column(db.VARCHAR(length=512))
    name = db.Column(db.VARCHAR(length=512))


class Log(OurMixin, db.Model):
    __tablename__ = 'log'

    id = db.Column(db.VARCHAR(length=36), primary_key=True)
    action = db.Column(db.VARCHAR(length=5120))
    user_id = db.Column(db.Integer(),
                        db.ForeignKey('user.id', ondelete='CASCADE'),
                        nullable=False)
    user = db.relationship("User", cascade='delete')


class User(UserMixin, OurMixin, db.Model):
    id = db.Column(db.VARCHAR(length=36), primary_key=True)
    username = db.Column(db.String())
    firstname = db.Column(db.String(32))
    lastname = db.Column(db.String(32))
    password = db.Column(db.String())

    _roles = db.relationship(
        'Role', secondary=user_role_table, backref='users')
    type = db.Column(db.String(50))

    roles = association_proxy('_roles', 'name', creator=_role_find_or_create)

    def __init__(self, **kwargs):
        # A bit of duplication here keeps the kwargs being
        # set but encrypts the password.
        for k, v in kwargs.items():
            if k != 'password':
                setattr(self, k, v)
            else:
                self.set_password(v)

        OurMixin.__init__(self)
        UserMixin.__init__(self)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, value):
        return check_password_hash(self.password, value)

    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def add_roles(self, *roles):
        self.roles.extend([role for role in roles if role not in self.roles])

    def remove_roles(self, *roles):
        self.roles = [role for role in self.roles if role not in roles]

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User {}:{}>'.format(self.id, self.username)


class Setting(OurMixin, db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.VARCHAR(length=36), primary_key=True)
    name = db.Column(db.VARCHAR(length=128), nullable=False)
    section = db.Column(db.VARCHAR(length=128), nullable=False,
                        default='main', server_default='main')
    human_name = db.Column(db.TEXT(), nullable=True,
                           default='', server_default='')
    value = db.Column(db.TEXT(), nullable=True, default='', server_default='')
    vartype = db.Column(db.Enum('int', 'str', 'bool', 'float'), nullable=False)
    allowed = db.Column(db.Text, nullable=True)
    system = db.Column(db.Boolean(), default=False, server_default='0')
    description = db.Column(db.TEXT(), nullable=True,
                            default='', server_default='')

    @property
    def title(self):
        if self.human_name:
            return self.human_name
        else:
            return self.name.replace('-', ' ').title()

    @property
    def choices(self):
        return json.loads(self.allowed)

    @property
    def val(self):
        """
        Gets the value as the proper type.
        """
        return __builtins__[self.vartype](self.value)


class Tag(OurMixin, db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.VARCHAR(length=36), primary_key=True)
    name = db.Column(db.VARCHAR(length=64), nullable=False)


class File(OurMixin, db.Model):
    __tablename__ = 'files'

    id = db.Column(db.VARCHAR(length=36), primary_key=True)
    name = db.Column(db.VARCHAR(length=256), nullable=False)
    path = db.Column(db.VARCHAR(length=512), nullable=True)
    thumbnail_name = db.Column(db.VARCHAR(length=256), nullable=True)
    thumbnail_path = db.Column(db.VARCHAR(length=512), nullable=True)
    width = db.Column(db.Integer(), default=0, server_default='0')
    height = db.Column(db.Integer(), default=0, server_default='0')
    size = db.Column(db.Integer(), default=0, server_default='0')
    mimetype = db.Column(db.VARCHAR(length=256), nullable=False)
