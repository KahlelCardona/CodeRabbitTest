import unittest
from datetime import datetime

from app import app, db, Todo

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.db = db
        self.db.create_all()

    def test_add_todo(self):
        with self.app.post('/add', data={'title': 'Test Todo'}) as response:
            self.assertEqual(response.status_code, 302)
            new_todo = Todo.query.filter_by(title='Test Todo').first()
            self.assertIsNotNone(new_todo.created_at)

    def test_update_todo(self):
        new_todo = Todo.query.filter_by(title='Test Todo').first()
        with self.app.get(f'/update/{new_todo.id}') as response:
            self.assertEqual(response.status_code, 302)
            self.assertIsNotNone(new_todo.completed_at)
