from myapp.model.db_extension import db
from sqlalchemy import Integer, String, Column

class MetaCategories(db.Model):
    __tablename__ = 'meta_caetgories'

    meta_cat_id = Column(Integer, primary_key=True)
    cat_name = Column(String(45), nullable=False)
