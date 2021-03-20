import os
from flask import Flask, request, abort, jsonify
from flask.globals import session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import *

QUESTIONS_PER_PAGE = 10


def pagination(request, questions):
    page = request.args.get('page', 1, type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions_formate = [Q.format() for Q in questions]
    current_questions = questions_formate[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    '''@TODO: Set up CORS. Allow '*' for origins.
          Delete the sample route after completing the TODOs'''
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''@TODO: Use the after_request decorator to set Access-Control-Allow'''

    @app.after_request
    def after_request(response):
        response.headers.add(
          'Access_Control_Allow_Headers', 'Content-Type, Authorization')
        response.headers.add(
          'Access_Control_Allow_Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories')
    def get_Categories():
        if request.method != 'GET':
            abort(405)
        final_Categories = {}
        Categories = Category.query.all()
        for cat in Categories:
            final_Categories[cat.id] = cat.type

        return jsonify({
          'success': True,
          'categories': final_Categories,
        })
    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and
    pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions')
    def get_questions():
        final_categories = {}
        questions = Question.query.all()
        formatted_questions = [q.format() for q in questions]
        Categories = Category.query.all()
        for cat in Categories:
            final_categories[cat.id] = cat.type

        current_questions = pagination(request, questions)
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(formatted_questions),
            'categories': final_categories,
        })
    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question,
    the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''

    @app.route('/<id>', methods=['DELETE'])
    def delete_question(id):
        try:
            Question.query.filter(Question.id == id).one_or_none().delete()

            return jsonify({
                'success': True,
                'deleted': id
            })
        except Exception as error:
            db.session.rollback()
            print("question hasn't been deleted")
            abort(404)
        finally:
            db.session.close()
    '''
    @TODO: npm
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and
    the question will appear at the end of the last page
    of the questions list in the "List" tab.
    '''

    @app.route('/questions', methods=['POST'])
    def add_questions():
        try:
            body = request.get_json()
            q = body.get('question', None)
            answer = body.get('answer', None)
            Cat = body.get('category', None)
            difficulty = body.get('difficulty', None)
            new_question = Question(question=q, answer=answer,
                                    category=Cat, difficulty=difficulty)
            new_question.insert()

            return jsonify({
                'success': True,
                'question': new_question.question,
                'answer': new_question.answer,
                'difficulty': new_question.difficulty,
                'category': new_question.category
            })
        except Exception as error:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()
    '''
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''
    @app.route('/search', methods=['POST'])
    def search():
        body = request.get_json()
        search_term = body.get('searchTerm', None)
        search_questions = Question.query.filter(
          Question.question.ilike(f'%{search_term}%')).all()
        all_searched_questions = [s.format() for s in search_questions]
        return jsonify({
            'success': True,
            'questions': all_searched_questions,
            'total_questions': len(all_searched_questions),
        })

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:id>/questions')
    def get_questions_per_category(id):
        questions = Question.query.filter(Question.category == id).all()
        formatted_questions = [q.format() for q in questions]
        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'total_questions': len(formatted_questions),
            'current_category': id
        })
    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quiz', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()

            if not ('quiz_category' in body and 'previous_questions' in body):
                abort(422)
            category = body.get('quiz_category', None)
            previous_questions_ids = body.get('previous_questions', None)

            if ((category is None) or (previous_questions_ids is None)):
                abort(400)

            if category['type'] == 'click':
                questions_per_said_category = Question.query.filter(
                  Question.id.notin_((previous_questions_ids))).all()
            else:
                questions_per_said_category = Question.query.filter(
                  Question.category == category['id']).filter(
                  Question.id.notin_((previous_questions_ids))).all()
            '''if (len(previous_questions_ids) == 0):
                  total = len(questions_per_said_category)'''

            if (len(questions_per_said_category) == 0):
                    return jsonify({
                            'success': True,
                            'question': False,
                    })

            current_question = questions_per_said_category[random.randrange(
                0, len(questions_per_said_category))].format()if len(
                  questions_per_said_category) > 0 else None
            '''if (len(previous_questions_ids) == total):
                  return jsonify({
                      'success': True
                  })'''

            print("questions_per_said_category",questions_per_said_category)
            return jsonify({
                'success': True,
                'question': current_question,
                'question-id': current_question['id'],
                'category-id': category['id'],
            })

        except Exception as error:
            abort(422)
        finally:
            db.session.close()
    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not Found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "unprocessable"
        }), 422

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method Not Allowed'
        }), 405

    return app
