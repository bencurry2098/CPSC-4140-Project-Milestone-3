from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    avg_time = db.Column(db.Float)
    accuracy = db.Column(db.Float)
    mode = db.Column(db.String(32))  # "normal" or "simulated"
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Integer)
    total_questions = db.Column(db.Integer)
    csv_data = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class QuizQuestion:
    def __init__(self, prompt: str, choices: list[str], answer: int):
        self.prompt = prompt
        self.choices = choices
        self.answer = answer

    def is_correct(self, chosen: int) -> bool:
        return self.answer == chosen


class Quiz:
    def __init__(self, questions: list[QuizQuestion]):
        self.questions = questions
        self.current_question_index = 0
        self.num_questions = len(questions)

    def current_question(self) -> QuizQuestion:
        return self.questions[self.current_question_index]

    def next_question(self) -> None:
        self.current_question_index += 1
