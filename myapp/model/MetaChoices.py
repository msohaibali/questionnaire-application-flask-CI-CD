from myapp.model.db_extension import db


class MetaChoices(db.Model):
    __tablename__ = "meta_choices"

    meta_choices_id = db.Column(db.Integer, primary_key=True)
    meta_choice_desc = db.Column(db.String(100), nullable=False)
    meta_question_id = db.Column(
        db.Integer,
        db.ForeignKey("meta_questions.meta_question_id"),
        nullable=False,
    )

    meta_ques = db.relationship(
        "MetaQuestions",
        backref="meta_ans",
    )
