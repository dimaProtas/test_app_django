import json

from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.shortcuts import render
from django.db import connection


def head_index(request):
    return render(request, 'head_index.html')

def index_view(request):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT id, title FROM app_survey;""")
        tests = cursor.fetchall()
    tests_data = [{'id': row[0], 'title': row[1]} for row in tests]
    return render(request, 'index.html', {'data': tests_data})


def get_next_question(request, survey_id, question_index):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT id, text, survey_id, parent_question_id FROM app_question WHERE survey_id=%s AND parent_question_id IS NULL;""", [survey_id])
        questions = cursor.fetchall()

        if question_index < len(questions):
            question = questions[question_index]
            question_id = question[0]
            cursor.execute("""SELECT ac.id, ac.text, aq.dependent_question_id  
                        FROM app_choice ac
                        INNER JOIN app_questiondependency aq ON aq.parent_choice_id = ac.id 
                        WHERE question_id=%s;""", [question_id])
            choices = cursor.fetchall()
            choices_data = [{"id": choice[0], "text": choice[1], "dependent_question_id": choice[2]} for choice in choices]
            question_data = {"id": question[0], "text": question[1], "parent_question_id": question[3], "choices": choices_data, "survey_id": question[2], "question_index": question_index +1}
        else:
            user_id = request.user.id
            cursor.execute("""WITH QuestionRanks AS (
                        SELECT 
                            question_id,
                            DENSE_RANK() OVER (ORDER BY total_responses DESC) AS question_rank
                        FROM (
                            SELECT 
                                question_id,
                                COUNT(*) AS total_responses
                            FROM 
                                app_userresponse
                            GROUP BY 
                                question_id
                        ) AS Counts
                    )
                    SELECT
                        UQ.question_text,
                        UQ.responce_text,
                        (SELECT text FROM app_choice WHERE id = UQ.choice_id) AS choise_text,
                        (SELECT COUNT(*) FROM app_userresponse WHERE question_id = UQ.question_id AND survey_id = UQ.survey_id) AS total_responses,
                        (SELECT COUNT(DISTINCT user_id) FROM app_userresponse WHERE survey_id = UQ.survey_id) AS users_count,
                        (SELECT (SELECT COUNT(*) FROM app_userresponse WHERE question_id = UQ.question_id) * 100.0 / COUNT(DISTINCT user_id)  FROM app_userresponse WHERE survey_id = UQ.survey_id) AS procent,
                        QR.question_rank
                    FROM (
                        SELECT 
                            aq.id AS question_id, 
                            aq.text AS question_text, 
                            au.text_response AS responce_text, 
                            au.survey_id AS survey_id, 
                            au.choice_id AS choice_id
                        FROM 
                            app_userresponse au
                        INNER JOIN 
                            app_question aq ON au.question_id = aq.id 
                        WHERE 
                            au.user_id=%s AND au.survey_id=%s
                    ) AS UQ
                    LEFT JOIN 
    QuestionRanks QR ON UQ.question_id = QR.question_id ORDER BY QR.question_rank;""", [user_id, survey_id])
            result = cursor.fetchall()
            result_data = [{'question': row[0], 'responce': row[1], 'choise_text': row[2], 'total_responses': row[3], 'users_count': row[4], 'procent': row[5], 'question_rank': row[6]} for row in result]
            question_data = {'text': 'Teст окончен!\nСпасибо за ваши ответы!', 'question_index': None, 'result_data': result_data}

        cursor.execute("""SELECT id, title FROM app_survey WHERE id=%s;""", [survey_id])
        survey = cursor.fetchone()

    survey_data = {'id': survey[0], 'title': survey[1]} if survey else None

    return render(request, 'test.html', {'question': question_data, 'survey': survey_data})


def save_questions(request):
    if request.method == 'POST':
        body_data = json.loads(request.body.decode('utf-8'))
        survey_id = body_data['survey_id']
        user_id = request.user.id
        question_id = body_data['question_id']
        choice_id = body_data['choice_id']
        text_response = body_data['text_response']
        print(survey_id, user_id, question_id, choice_id, text_response)

        with connection.cursor() as cursor:
            if choice_id is not None:  # Проверяем, есть ли значение choice_id
                text_response = ''
                print(survey_id, user_id, question_id, choice_id, text_response)
                cursor.execute("""
                    INSERT INTO app_userresponse (survey_id, user_id, question_id, choice_id, text_response)
                    VALUES (%s, %s, %s, %s, %s)
                """, [survey_id, user_id, question_id, choice_id, text_response])
            else:
                cursor.execute("""
                    INSERT INTO app_userresponse (survey_id, user_id, question_id, text_response)
                    VALUES (%s, %s, %s, %s)
                """, [survey_id, user_id, question_id, text_response])

            # Проверяем успешность выполнения запроса
            if cursor.rowcount > 0:
                data = {'success': 'OK'}
            else:
                data = {'error': 'Failed to save user response'}


        return JsonResponse(data)


def get_child_auestion(request, survey_id, child_id, question_index):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT id, text, survey_id, parent_question_id FROM app_question WHERE id=%s;""", [child_id])
        questions = cursor.fetchone()

        print(questions)
        question_id = questions[0]

        cursor.execute("""SELECT ac.id, ac.text, aq.dependent_question_id  
                                FROM app_choice ac
                                INNER JOIN app_questiondependency aq ON aq.parent_choice_id = ac.id 
                                WHERE question_id=%s;""", [question_id])
        choices = cursor.fetchall()
        choices_data = [{"id": choice[0], "text": choice[1], "dependent_question_id": choice[2]} for choice in choices]
        question_data = {"id": questions[0], "text": questions[1], "parent_question_id": questions[3],
                         "choices": choices_data, "survey_id": questions[2], "question_index": question_index}

        cursor.execute("""SELECT id, title FROM app_survey WHERE id=%s;""", [survey_id])
        survey = cursor.fetchone()

    survey_data = {'id': survey[0], 'title': survey[1]} if survey else None

    return render(request, 'test.html', {'question': question_data, 'survey': survey_data})


class MyLoginView(LoginView):
    next_page = '/head_index'
