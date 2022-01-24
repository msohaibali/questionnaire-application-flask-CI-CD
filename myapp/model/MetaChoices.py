from myapp.model.db_extension import db
from sqlalchemy import Integer, String, Column, ForeignKey

class MetaChoices(db.Model):
    __tablename__ = 'meta_choices'

    meta_choices_id = Column(Integer, primary_key=True)
    meta_choice_desc = Column(String(100), nullable=False)
    meta_question_id = Column(Integer, ForeignKey('meta_questions.meta_question_id'), nullable=False)

    meta_ques = db.relationship('MetaQuestions', backref='meta_ans', lazy=True)
