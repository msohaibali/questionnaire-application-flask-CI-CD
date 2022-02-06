from myapp.model.db_extension import db
from myapp.model.MetaCategories import MetaCategories


class MetaQuestions(db.Model):
    __tablename__ = "meta_questions"

    meta_question_id = db.Column(db.Integer, primary_key=True)
    meta_question = db.Column(db.String(200), nullable=False)
    checkbox = db.Column(db.Boolean, default=False)
    meta_cat_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "meta_categories.meta_cat_id",
        ),
        nullable=False,
    )

    meta_cat = db.relationship("MetaCategories", backref="meta_ques")
