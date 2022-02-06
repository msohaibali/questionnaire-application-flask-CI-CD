from myapp.model.db_extension import db
from myapp.model.MetaForms import MetaForms
from myapp.model.MetaChoices import MetaChoices
from myapp.model.model import User


class MetaResponses(db.Model):
    __tablename__ = "meta_responses"

    meta_response_id = db.Column(db.Integer, primary_key=True)
    meta_response_description = db.Column(db.String(256), nullable=False)

    meta_form_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "meta_forms.meta_form_id",
        ),
        nullable=False,
    )

    meta_user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id",
        ),
        nullable=False,
    )

    meta_question_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "meta_questions.meta_question_id",
        ),
        nullable=False,
    )

    meta_answer_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "meta_choices.meta_choices_id",
        ),
        nullable=False,
    )

    meta_ques = db.relationship(
        "MetaQuestions",
        backref="meta_resp",
        lazy=True,
    )
    meta_ans = db.relationship("MetaChoices", backref="meta_resp", lazy=True)
    meta_user = db.relationship("User", backref="meta_resp", lazy=True)
    meta_form = db.relationship("MetaForms", backref="meta_resp", lazy=True)
