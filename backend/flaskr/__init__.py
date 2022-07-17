import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, questions):
    page =  request.args.get("page", 1, type=int)
    start = (page - 1)* QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formated_questions = [question.format() for question in questions]
    current_questions = formated_questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, true")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")

        return response

    # """
    # @TODO:
    # Create an endpoint to handle GET requests
    # for all available categories.
    # """

    @app.route("/categories")
    def get_categories():
        categories = Category.query.all()

        if len(categories) == 0:
            abort(404)
        formated_categories = {category.id: category.type for category in categories}
        return jsonify(
            {
                "success": True,
                "categories":formated_categories
            }
        )

    # """
    # @TODO:
    # Create an endpoint to handle GET requests for questions,
    # including pagination (every 10 questions).
    # This endpoint should return a list of questions,
    # number of total questions, current category, categories.

    # TEST: At this point, when you start the application
    # you should see questions and categories generated,
    # ten questions per page and pagination at the bottom of the screen for three pages.
    # Clicking on the page numbers should update the questions.
    # """

    @app.route("/questions")
    def get_questions():
        questions = Question.query.all()
        current_questions = paginate_questions(request, questions)
        categories = Category.query.all()
        formated_categories = {category.id: category.type for category in categories}
        if len(current_questions) == 0:
            abort(404)
        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(questions),
                "categories":formated_categories,
                "current_category": None
            }
        )


    # """
    # @TODO:
    # Create an endpoint to DELETE question using a question ID.

    # TEST: When you click the trash icon next to a question, the question will be removed.
    # This removal will persist in the database and when you refresh the page.
    # """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            if Question.query.filter(Question.id == question_id).one_or_none() is None:
                abort(404)
            
            question = Question.query.filter(Question.id == question_id).one_or_none()
            question.delete()
            questions = Question.query.all()
            current_questions = paginate_questions(request, questions)
            categories = Category.query.all()
            formated_categories = {category.id: category.type for category in categories}
            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "message":"Question with ID: "+str(question_id)+ " has been deleted successfully",
                    "questions": current_questions,
                    "total_questions": len(questions),
                    "categories":formated_categories
                }
            )
        except:
            abort(404)


    # """
    # @TODO:
    # Create an endpoint to POST a new question,
    # which will require the question and answer text,
    # category, and difficulty score.

    # TEST: When you submit a question on the "Add" tab,
    # the form will clear and the question will appear at the end of the last page
    # of the questions list in the "List" tab.
    # """

    @app.route("/questions", methods=["POST"])
    def create_question():
        body =  request.get_json()

        question = body.get("question")
        answer = body.get("answer")
        difficulty = body.get("difficulty")
        category = body.get("category")

        if question is None or answer is None or difficulty is None or category is None:
            abort(422)
        try:
            new_question = Question(
                question = question, answer = answer, 
                category = category, difficulty = difficulty
            )
            new_question.insert()

            questions = Question.query.all()
            current_questions = paginate_questions(request, questions)

            return jsonify(
                {
                    "success": True,
                    "created": new_question.id,
                    "current_category": new_question.category,
                    "questions": current_questions,
                    "total_questions": len(questions)
                }
            )
        except:
            abort(404)


    # """
    # @TODO:
    # Create a POST endpoint to get questions based on a search term.
    # It should return any questions for whom the search term
    # is a substring of the question.

    # TEST: Search by any phrase. The questions list will update to include
    # only question that include that string within their question.
    # Try using the word "title" to start.
    # """

    @app.route("/questions/search", methods=["POST"])
    def search_question():
        body = request.get_json()
        search_term = body.get("searchTerm", None)

        try:
            results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            result_questions = paginate_questions(request, results)
            if len(results) == 0:
                abort(404)
            return jsonify(
                {
                    "success": True,
                    "questions": result_questions,
                    "total_questions": len(results),
                    "current_category": None
                }
            )
        except:
            abort(404)
    # """
    # @TODO:
    # Create a GET endpoint to get questions based on category.

    # TEST: In the "List" tab / main screen, clicking on one of the
    # categories in the left column will cause only questions of that
    # category to be shown.
    # """

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_category_based_questions(category_id):
        try:  
            if Question.query.filter(Question.category == str(category_id)).count() > 0:
                category_based_questions =  Question.query.filter(Question.category == str(category_id)).all() 
                result_questions = paginate_questions(request, category_based_questions)
                return jsonify(
                    {
                        "success": True,
                        "questions": result_questions,
                        "total_questions": len(category_based_questions),
                        "current_category": category_id
                    }
                )
            else:
                abort(404)  
        except:
            abort(404)

    # """
    # @TODO:
    # Create a POST endpoint to get questions to play the quiz.
    # This endpoint should take category and previous question parameters
    # and return a random questions within the given category,
    # if provided, and that is not one of the previous questions.

    # TEST: In the "Play" tab, after a user selects "All" or a category,
    # one question at a time is displayed, the user is allowed to answer
    # and shown whether they were correct or not.
    # """
    @app.route("/quizzes", methods=["POST"])
    def quiz_questions():
        body =  request.get_json()
        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')
        try:
            if quiz_category['id'] == 0 and len(previous_questions) == 0:
                questions = Question.query.all()
                count = len(questions)
                formated_questions = paginate_questions(request, questions)
                rand = random.randint(0,(len(formated_questions)-1))
                
            elif quiz_category['id'] == 0 and len(previous_questions) > 0:
                questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
                count = len(Question.query.all())
                formated_questions = paginate_questions(request, questions)
                q_count = len(formated_questions)
                rand = random.randint(0,(q_count-1))

            elif len(previous_questions) > 0 and quiz_category['id'] != 0:
                questions = Question.query.filter_by(category=quiz_category['id']).filter(Question.id.notin_(previous_questions)).all()
                count = len(Question.query.filter_by(category=quiz_category['id']).all())
                q_count = len(questions)
                formated_questions = paginate_questions(request, questions)
                rand = random.randint(0,(q_count-1))

            else:   
                questions = Question.query.filter_by(category=quiz_category['id']).all()
                count = len(questions)
                formated_questions = paginate_questions(request, questions)
                rand = random.randint(0,(count-1))

            question_count = count
            next_question = formated_questions[rand]
            return jsonify(
                {
                    "success": True,
                    "question_count":question_count,
                    "question": next_question,
                }
            )
        except:
            abort(404)
        # except Exception as e:
        #     print(e)

    # """
    # @TODO:
    # Create error handlers for all expected errors
    # including 404 and 422.
    # """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500

    @app.errorhandler(405)
    def invalid_method(error):
        return jsonify({
            "success": False,
            'error': 405,
            "message": "Invalid method!"
        }), 405

    return app

