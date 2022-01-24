from myapp.model.db_extension import db
from sqlalchemy import Integer, String, Column, ForeignKey

class MetaQuestions(db.Model):
    __tablename__ = 'meta_questions'

    meta_question_id = Column(Integer, primary_key=True)
    meta_question = Column(String(200), nullable=False)
    meta_cat_id = Column(Integer, ForeignKey('meta_categories.meta_cat_id'), nullable=False)
    
    meta_cat = db.relationship('MetaCategories', backref='meta_ques', lazy=True)
    meta_ans = db.relationship('MetaChoices', backref='meta_ques', lazy=True)