from myapp.model.db_extension import db


class MetaSystems(db.Model):
    __tablename__ = "meta_system"

    meta_system_id = db.Column(db.Integer, primary_key=True)
    system_name = db.Column(db.String(45), nullable=False)
