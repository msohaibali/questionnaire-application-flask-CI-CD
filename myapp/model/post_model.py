from marshmallow import fields
from myapp.model.db_extension import db
from myapp.model.ma_extension import ma
from sqlalchemy import func


class Posts(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=func.current_timestamp())

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    meta_user = db.relationship("User", lazy=True)


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
