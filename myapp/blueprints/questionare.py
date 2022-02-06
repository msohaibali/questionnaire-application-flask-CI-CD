from http import HTTPStatus
from webargs import fields
from flask_login import login_required
from myapp.model.db_extension import db
from webargs.flaskparser import use_args
from flask import request, redirect, url_for
from flask import Blueprint, jsonify, render_template
from myapp.bl.QuestionnaireBLC import QuestionnaireBLC
from myapp.repositories.QuestionareRepository import QuestionareRepository


questionare = Blueprint("questionare", __name__)


@questionare.route("/get_form_data", methods=["GET"])
# @login_required
def get_form_data():
    data = QuestionareRepository.get_questions_data()
    schema = QuestionareRepository.get_schema(many=True)
    mixed_result = schema.dump(data)
    result = QuestionnaireBLC.data_serialization(mixed_result)

    return jsonify(result), HTTPStatus.OK


@questionare.route("/get_form_list", methods=["GET"])
@login_required
def get_submissions_data():
    data = QuestionareRepository.get_form_list()
    schema = QuestionareRepository.get_form_schema(many=True)
    result = schema.dump(data)
    return jsonify(result), HTTPStatus.OK


def get_data_by_user_form_id(meta_form_id):
    data = QuestionareRepository.get_response_data(meta_form_id)
    if not data:
        return jsonify([]), HTTPStatus.NO_CONTENT
    schema = QuestionareRepository.get_response_schema(many=True)
    mixed_result = schema.dump(data)

    return mixed_result


@questionare.route("/post_data", methods=["POST", "GET"])
@login_required
def post_form_data():
    breakpoint()
    total_questions_len = QuestionareRepository.get_questions_count()
    submissions_count = QuestionnaireBLC.submissions_count(request.form)

    if submissions_count != total_questions_len:
        return redirect(request.referrer)
    incoming_args = request.form
    try:
        ques_list, ans_list, desc_dict = QuestionnaireBLC.get_required_params(
            incoming_args,
        )
    except Exception as _:
        return redirect(request.referrer)
        print(_)

    response_data = {
        "questions_list": ques_list,
        "answers_list": ans_list,
        "description_list": desc_dict,
    }
    response_list = QuestionnaireBLC.data_serializer(data=response_data)
    _ = QuestionareRepository.add_responses(response_list)
    db.session.commit()
    return redirect(url_for("main.home_page"))


@questionare.route("/show_form/", methods=["GET", "POST"])
@login_required
def get_questionnaire_form():
    result = get_form_data()
    systems = QuestionareRepository.get_systems()
    years_list = QuestionnaireBLC.get_years()
    return render_template(
        "meta_data_form.html",
        all_categories=result[0].json,
        all_systems=systems,
        years_list=years_list,
    )


@questionare.route("/show_history/", methods=["GET", "POST"])
@login_required
def get_history():
    result = get_submissions_data()
    headers_list = ["FORM", "Created On", "Updated On", "Action"]
    return render_template(
        "data_history.html",
        all_submissions=result[0].json,
        all_headers=headers_list,
    )


@questionare.route("/deleteform", methods=["GET"])
@login_required
def delete_post():
    form_id = request.args.get("meta_form_id")
    breakpoint()
    target_form = QuestionareRepository.get_forms(form_id=form_id)
    if target_form:
        QuestionareRepository.delete_responses_by_id(form_id=form_id)
        QuestionareRepository.delete_form(target_form)
        db.session.commit()
        return redirect(url_for("questionare.get_history"))
    else:
        return redirect(url_for("questionare.get_history"))


@questionare.route("/edit_form/", methods=["GET"])
@login_required
def edit_questionnaire_form():
    result = get_form_data()
    result = result[0].json

    form_id = request.args.get("meta_form_id")
    responses_list = get_data_by_user_form_id(form_id)
    response_data = QuestionnaireBLC.responses_obj_generator(responses_list)
    data = QuestionnaireBLC.merge_answers_in_questions(result, response_data)
    systems = QuestionareRepository.get_systems()
    years_list = QuestionnaireBLC.get_years()
    return render_template(
        "meta_data_edit_form.html",
        all_categories=data,
        form_id=form_id,
        all_systems=systems,
        years_list=years_list,
    )


@questionare.route("/edit_data", methods=["POST", "GET"])
@login_required
@use_args({"form_id": fields.Integer(required=True)}, location="query")
def edit_form_data(args: dict):
    form_id = args["form_id"]
    incoming_args = request.form
    breakpoint()
    try:
        ques_list, ans_list, desc_dict = QuestionnaireBLC.get_required_params(
            incoming_args,
        )
    except Exception as _:
        return redirect(request.referrer)
        print(_)

    response_data = {
        "questions_list": ques_list,
        "answers_list": ans_list,
        "description_list": desc_dict,
    }
    QuestionareRepository.delete_responses_by_id(form_id=form_id)
    response_list = QuestionnaireBLC.data_serializer(
        data=response_data,
        form_id=form_id,
        session=db.session,
    )
    _ = QuestionareRepository.add_responses(response_list)
    db.session.commit()
    return redirect(url_for("questionare.get_history"))
