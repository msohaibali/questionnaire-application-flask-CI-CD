from marshmallow import fields
from marshmallow import pre_dump
from myapp.model.MetaQuestions import MetaQuestions
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from myapp.schemas.AnswersSchema import AnswersSchema
from myapp.schemas.CategoriesSchema import CategoriesSchema


class QuestionareSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MetaQuestions

    meta_cat = fields.Pluck(CategoriesSchema, "cat_name")
    choices = fields.List(fields.Nested(AnswersSchema))

    @pre_dump
    def data_serializer(self, data, **kwargs):
        data.choices = data.meta_ans
        return data
