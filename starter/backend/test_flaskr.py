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
        self.database_path = "postgres://postgres:01121188626Dd@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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
    def test_get_paginated_questions(self):
        res=self.client().get('/questions')
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_questions'])
        #self.assertEqual(data['current_category'],None)
        #self.assertTrue(data['NO of questions per page'])

        
    
    def test_404_requesting_invalid_page(self):
        res=self.client().get('/questions?page=1000')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['message'],'Not Found')
        
    def test_get_categories(self):
        res=self.client().get('/categories')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['categories']))
        #self.assertTrue(data['No of categories'])
 

    def test_get_categories_with_wrong_method(self):
        res=self.client().post('/categories', json={"category":"4"})
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],405)
        self.assertEqual(data['message'],'Method Not Allowed')

    def test_delete_question(self):
        res=self.client().delete('/6')
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],6)
    
    def test_404_question_Not_found(self):
        res=self.client().delete('/1000')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['message'],'Not Found')

    def test_get_questions_per_category(self):
        res=self.client().get('/categories/6/questions')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'],6)


    def test_get_questions_per_category_with_wrong_method(self):
        res=self.client().post('/categories/5/questions')
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],405)
        self.assertEqual(data['message'],'Method Not Allowed')


    def test_search_specific_question(self):
        res=self.client().post('/search', json={"searchTerm":"who"})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])


    def test_search_specefic_questions_with_wrong_method(self):
        res=self.client().get('/search')
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],405)
        self.assertEqual(data['message'],'Method Not Allowed')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
