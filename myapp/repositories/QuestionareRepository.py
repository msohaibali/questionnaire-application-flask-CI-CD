from typing import List, Optional
from myapp.model.MetaChoices import MetaChoices
from myapp.model.MetaQuestions import MetaQuestions
from myapp.model.MetaResponses import MetaResponses
from myapp.model.MetaForms import MetaForms
from myapp.model.MetaSystems import MetaSystems
from myapp.schemas.MetaFormSchema import MetaFormSchema
from myapp.schemas.QuestionareSchema import QuestionareSchema
from myapp.model.db_extension import db
from sqlalchemy.orm import joinedload

from myapp.schemas.ResponseSchema import ResponseSchema


class QuestionareRepository:
    @staticmethod
    def get_questions_data():
        response = db.session.query(MetaQuestions).outerjoin(
            (
                MetaChoices,
                MetaQuestions.meta_question_id == MetaChoices.meta_question_id,
            ),
        )
        return response.all()

    @staticmethod
    def get_questions_count():
        response = db.session.query(MetaQuestions).count()
        return response

    @staticmethod
    def get_forms(user_id: int = None, form_id: int = None):
        response = db.session.query(MetaForms)
        if user_id:
            response = response.filter(MetaForms.meta_user_id == user_id)
        if form_id:
            response = response.filter(MetaForms.meta_form_id == form_id)
            response = response.first()
            return response

        response = response.all()
        return response

    @staticmethod
    def get_responses(user_id: int = None, form_id: int = None):
        response = db.session.query(MetaResponses)
        if user_id:
            response = response.filter(MetaResponses.meta_user_id == user_id)
        if form_id:
            response = response.filter(MetaResponses.meta_form_id == form_id)

        response = response.all()
        return response

    @staticmethod
    def get_systems():
        response = db.session.query(MetaSystems)
        response = response.all()
        return response

    @staticmethod
    def get_response_data(meta_form_id: int = None):
        response = db.session.query(MetaResponses).options(
            joinedload(MetaResponses.meta_form),
            joinedload(MetaResponses.meta_ans),
            joinedload(MetaResponses.meta_ques),
        )
        if meta_form_id:
            response = response.filter(
                MetaResponses.meta_form_id == meta_form_id,
            )
        return response.all()

    @staticmethod
    def get_form_list(user_id: int = None, form_id: int = None):
        response = db.session.query(MetaForms).options(
            joinedload(MetaForms.meta_user),
        )
        if user_id:
            response = response.filter(MetaForms.meta_user_id == user_id)
        if form_id:
            response = response.filter(MetaForms.meta_form_id == form_id)
        return response.all()

    @staticmethod
    def delete_responses(responses_list: list = []):
        try:
            for single_item in responses_list:
                db.session.delete(single_item)
            db.session.flush()
        except Exception as ex:
            print(ex)
            db.session.rollback()
            raise ValueError()

    @staticmethod
    def delete_responses_by_id(form_id: int = None):
        try:
            if form_id:
                db.session.query(MetaResponses).filter(
                    MetaResponses.meta_form_id == form_id
                ).delete(synchronize_session=False)
                db.session.flush()
        except Exception as ex:
            print(ex)
            db.session.rollback()
            raise ValueError()

    @staticmethod
    def delete_form(form: MetaForms = None):
        try:
            db.session.delete(form)
            db.session.flush()
        except Exception as ex:
            print(ex)
            db.session.rollback()
            raise ValueError()

    @staticmethod
    def add_responses(responses_list: list):
        try:
            db.session.add_all(responses_list)
            return responses_list
        except Exception as ex:
            print(ex)
            db.session.rollback()
            raise ValueError()

    @staticmethod
    def get_schema(only_fields: Optional[List] = None, many=True):
        """
        Return the schema which can be used to serialize the
        Questionare Type objects.
        """
        return QuestionareSchema(only=only_fields, many=many)

    @staticmethod
    def get_form_schema(only_fields: Optional[List] = None, many=True):
        """
        Return the schema which can be used to serialize the
        MetaForm Type objects.
        """
        return MetaFormSchema(only=only_fields, many=many)

    @staticmethod
    def get_response_schema(only_fields: Optional[List] = None, many=True):
        """
        Return the schema which can be used to serialize the
        MetaResponse Type objects.
        """
        return ResponseSchema(only=only_fields, many=many)
