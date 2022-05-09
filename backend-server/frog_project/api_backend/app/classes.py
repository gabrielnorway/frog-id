from .secrets import Secrets
import bcrypt
from sqlalchemy import MetaData, ForeignKey, DateTime, Column, String, Integer, Numeric, Boolean
from sqlalchemy.orm import declarative_base
from .common import _print
import datetime
try:
    from flask_login import UserMixin
    from .exts import db
except:
    class UserMixin:
        pass
    class db:
        Model = declarative_base()



pepper = Secrets.password_pepper
Base = declarative_base()


class Frog(db.Model):
    __tablename__ = 'frogs'
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    name = Column(String)
    comment = Column(String)


class Image(db.Model):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    frog_id = Column(Integer, ForeignKey('frogs.id'), nullable=True)
    filename = Column(String, nullable=False)
    user = Column(Integer, ForeignKey('users.id'), nullable=True)
    ml_status = Column(String, default="null")
    datetime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    lat = Column(Numeric(precision=10, scale=8))
    lng = Column(Numeric(precision=11, scale=8))
    site = Column(String)
    comment = Column(String)


def pw_encode(password):
    return "".join((password, pepper)).encode('utf8')


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    is_admin = Column(Boolean, default=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String)

    def verify_password(self, password):
        return bcrypt.checkpw(pw_encode(password), self.password)

    def set_password(self, password):
        self.password = bcrypt.hashpw(pw_encode(password), bcrypt.gensalt())


def add_user(db_obj, user_dict):
    if not User.query.filter(User.username == user_dict["username"]).first():
        new_user = User(username=user_dict["username"])
        new_user.set_password(user_dict["password"])
        if "is_admin" in user_dict:
            new_user.is_admin = user_dict["is_admin"]
        db_obj.session.add(new_user)
        db_obj.session.commit()
        _print(f"[SQL] Added user: {new_user.username}")



