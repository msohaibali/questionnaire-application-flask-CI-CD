from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from myapp.model.MetaForms import MetaForms


class MetaFormSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MetaForms
        include_fk = True
