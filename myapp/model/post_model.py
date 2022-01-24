from marshmallow import fields
from flask_sqlalchemy import model
from myapp.model.db_extension import db
from myapp.model.ma_extension import ma
from sqlalchemy import Integer, String, DateTime, Column, func, ForeignKey

class Posts(db.Model):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(200))
    created_at = Column(DateTime, default=func.current_timestamp())
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='posts', lazy=True)


class PostsSchema(ma.Schema):
    # class meta:
    #     model = Posts
    #     fields = ('title', 'description', 'created_at', 'user_id')
    #     include_fk = True
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    created_at = fields.DateTime()
    user_id = fields.Integer()