from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from myapp.model.MetaChoices import MetaChoices


class AnswersSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MetaChoices
