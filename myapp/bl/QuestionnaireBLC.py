from datetime import datetime
from flask_login import current_user
from marshmallow import ValidationError
from myapp.model.MetaForms import MetaForms
from myapp.model.MetaResponses import MetaResponses
from sqlalchemy.orm import scoped_session


class QuestionnaireBLC:
    @staticmethod
    def data_serialization(data_list: list) -> list:
        result = list()
        single_cat = dict()
        category = ""
        for single_item in data_list:
            ques_cat = single_item.pop("meta_cat")
            if not category:
                category = ques_cat
                single_cat["category"] = ques_cat
                single_cat["questions"] = [single_item]
            elif category == ques_cat:
                single_cat["questions"].append(single_item)
            elif category != ques_cat and single_cat:
                result.append(single_cat)
                single_cat = dict()
                category = ques_cat
                single_cat["category"] = ques_cat
                single_cat["questions"] = [single_item]

        if single_cat:
            result.append(single_cat)
            single_cat = dict()

        return result

    @staticmethod
    def submissions_count(req_list):
        chk_list = [key for key, _ in req_list.items() if "ques_" in key]
        return len(set(chk_list))

    @staticmethod
    def get_required_params(incoming_args):
        ques_list = []
        ans_list = []
        desc_dict = {}
        for single_item in incoming_args:
            if "ques_" in single_item:
                ques_list.append(int(single_item.replace("ques_", "")))
                ans_list.append(int(incoming_args.get(single_item)))
            if "desc_" in single_item:
                desc_dict[int(single_item.split("_")[-1])] = incoming_args.get(
                    single_item,
                )

        if not ques_list:
            raise ValidationError("No Questions were Answered")

        return ques_list, ans_list, desc_dict

    @staticmethod
    def data_serializer(
        data,
        form_id: int = None,
        session: scoped_session = None,
    ):
        responses_list = list()
        desc_dict = data.pop("description_list", {})
        if not form_id:
            meta_form = MetaForms(
                meta_user=current_user,
                created_at=datetime.now(),
                last_updated=datetime.now(),
            )
        else:
            meta_form = (
                session.query(MetaForms)
                .filter(
                    MetaForms.meta_form_id == form_id,
                )
                .first()
            )
            meta_form.last_updated = datetime.now()
            session.flush()

        for idx in range(len(data.get("questions_list"))):
            responses_list.append(
                MetaResponses(
                    meta_response_description=desc_dict.get(idx + 1)
                    if desc_dict.get(idx + 1)
                    else None,
                    meta_user=current_user,
                    meta_question_id=data.get("questions_list")[idx],
                    meta_answer_id=data.get("answers_list")[idx],
                    meta_form=meta_form,
                )
            )

        return responses_list

    @staticmethod
    def responses_obj_generator(responses_list):
        data = {}
        for _itm in responses_list:
            if _itm["meta_ques"] not in data.keys():
                data[_itm["meta_ques"]] = {
                    "selection": [_itm["meta_ans"]],
                    "desc": {},
                }
                if _itm["meta_response_description"]:
                    data[_itm["meta_ques"]]["desc"][_itm["meta_ans"]] = _itm[
                        "meta_response_description"
                    ]
            else:
                data[_itm["meta_ques"]]["selection"].append(_itm["meta_ans"])
                if _itm["meta_response_description"]:
                    data[_itm["meta_ques"]]["desc"][_itm["meta_ans"]] = _itm[
                        "meta_response_description"
                    ]

        return data

    @staticmethod
    def merge_answers_in_questions(questionnaire_list, response_obj):
        for single_item in questionnaire_list:
            for single_question in single_item["questions"]:
                single_question.update(
                    response_obj[single_question["meta_question_id"]]
                )

        return questionnaire_list

    @staticmethod
    def get_years():
        current_year = datetime.now().year
        years_list = [index for index in range(1970, (current_year + 1))]
        if years_list:
            years_list.sort(reverse=True)
        return years_list
