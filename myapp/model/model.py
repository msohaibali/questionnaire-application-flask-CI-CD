from marshmallow import fields
from flask_login import UserMixin
from myapp.model.db_extension import db
from myapp.model.ma_extension import ma
from sqlalchemy import Integer, func


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=func.current_timestamp())


class UserSchema(ma.Schema):
    username = fields.Str()
    created_at = fields.DateTime()
