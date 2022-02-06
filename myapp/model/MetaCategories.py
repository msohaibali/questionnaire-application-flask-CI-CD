from myapp.model.db_extension import db


class MetaCategories(db.Model):
    __tablename__ = "meta_categories"

    meta_cat_id = db.Column(db.Integer, primary_key=True)
    cat_name = db.Column(db.String(45), nullable=False)
