from myapp.model.db_extension import db
from sqlalchemy import Integer, String, Column, ForeignKey

class MetaResponses(db.Model):
    __tablename__ = 'meta_responses'

    meta_response_id = Column(Integer, primary_key=True)
    meta_response_description = Column(String(256), nullable=False)
    meta_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    meta_question_id = Column(Integer, ForeignKey('meta_questions.meta_question_id'), nullable=False)
    meta_answer_id = Column(Integer, ForeignKey('meta_choices.meta_choices_id'), nullable=False)

    meta_ques = db.relationship('MetaQuestions', backref='meta_resp', lazy=True)
    meta_ans = db.relationship('MetaChoices', backref='meta_resp', lazy=True)
    users = db.relationship('User', backref='meta_resp', lazy=True)
