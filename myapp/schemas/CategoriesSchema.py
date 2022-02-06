from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from myapp.model.MetaCategories import MetaCategories


class CategoriesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MetaCategories
