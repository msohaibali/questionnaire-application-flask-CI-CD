from myapp.model.db_extension import db


class MetaForms(db.Model):
    __tablename__ = "meta_forms"

    meta_form_id = db.Column(db.Integer, primary_key=True)
    meta_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )
    # meta_system_id = db.Column(
    #     db.Integer,
    #     db.ForeignKey("MetaSystems.meta_system_id"),
    #     nullable=False,
    # )
    created_at = db.Column(db.DateTime, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False)

    meta_user = db.relationship(
        "User",
        backref="meta_form",
    )

    # meta_system = db.relationship(
    #     "MetaSystems",
    #     backref="meta_form",
    # )
