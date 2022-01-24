from marshmallow import fields
from flask_sqlalchemy import model
from flask_login import UserMixin
from myapp.model.db_extension import db
from myapp.model.ma_extension import ma
from sqlalchemy import Integer, String, Column, DateTime, func

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(128), nullable=False, unique=True)
    password = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())

class UserSchema(ma.Schema):
    username = fields.Str()
    # email = fields.Email()
    # role = fields.Str()
    # status = fields.Str()
    created_at = fields.DateTime()
