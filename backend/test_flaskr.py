import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "The square of 4 is?", 
            "answer": "16", 
            "difficulty": 1, 
            "category": 1
        }

        self.search_question = {"searchTerm": "entitled"}

        self.quiz = {
            'previous_questions': [6, 37],
            'quiz_category': {
                'type': 'Science', 
                'id': 1
            }
        }
        self.quiz_fail = {
            'previous_questions': [6, 27],
            'quiz_category': {
                'type': 'abc',
                'id': 'z'
            }
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertGreater(len(data["categories"]),0)

    def test_get_categories_fail(self):
        res = self.client().get("/categories/abc")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertGreater(len(data["questions"]),0)
        self.assertGreater(data["total_questions"],0)
        self.assertGreater(len(data["categories"]),0)

    def test_get_questions_fail(self):
        res = self.client().get("/questions?page=99")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    def test_delete_question(self):
        test_question = Question(question = "test question", answer="test answer", difficulty = 1, category= 1)
        test_question.insert()

        deleted_id = test_question.id

        res = self.client().delete(f"/questions/{test_question.id}")
        data = json.loads(res.data)
        del_question = Question.query.filter(Question.id == test_question.id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], deleted_id)
        self.assertEqual(del_question, None)
    
    def test_delete_question_fail(self):
        res = self.client().delete("/questions/abc")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    # def test_create_question(self):
    #     res = self.client().post("/questions", json = self.new_question)
    #     data = json.loads(res.data)

    #     created_question_count = Question.query.filter(Question.question == self.new_question["question"]).count()
    #     self.assertEqual(res.status_code, 200)
    #     self.assertEqual(data["success"], True)
    #     self.assertEqual(created_question_count, 1)

    def test_create_question_fail(self):
        res = self.client().post("/questions", json = {"question": ""})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
    
    def test_search_question(self):
        res = self.client().post("/questions/search", json=self.search_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertGreater(len(data["questions"]),0)
        self.assertGreater(data["total_questions"],0)

    def test_search_question_fail(self):
        res = self.client().post("/questions/search", json = {"searchTerm": "zzzzzz"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    def test_get_category_based_questions(self):
        category_id = 1
        res = self.client().get("/categories/"+str(category_id)+"/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertGreater(len(data["questions"]),0)
        self.assertGreater(data["total_questions"],0)
        self.assertEqual(data["current_category"], category_id)

    def test_get_category_based_questions_fail(self):
        category_id = 99
        res = self.client().get("/categories/"+str(category_id)+"/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_quiz_questions(self):
        res = self.client().post("/quizzes", json=self.quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question']['category'], 1)
    
    def test_quiz_questions_fail(self):
        
        res = self.client().post('/quizzes', json=self.quiz_fail)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()