from marshmallow import fields, post_dump
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from myapp.schemas.AnswersSchema import AnswersSchema
from myapp.schemas.QuestionareSchema import QuestionareSchema


class DescriptionSchema(SQLAlchemyAutoSchema):
    fields.Integer()
    fields.String()


class ResponseSchema(SQLAlchemyAutoSchema):
    # meta_form_id = fields.Integer()
    # meta_response_id = fields.Integer()
    # meta_user_id = fields.Integer()
    # meta_ques = fields.Nested(
    #     QuestionareSchema,
    #     only=("meta_question_id", "meta_question"),
    # )
    # meta_ans = fields.Nested(
    #     AnswersSchema,
    #     only=("meta_choices_id", "meta_choice_desc"),
    # )
    meta_ques = fields.Pluck(QuestionareSchema, "meta_question_id")
    meta_ans = fields.Pluck(AnswersSchema, "meta_choices_id")
    meta_response_description = fields.String()

    @post_dump
    def data_serializer(self, data, **kwargs):
        return data
