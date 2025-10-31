from flask import Flask, request, jsonify
from app.models import db, User, TestResult, QuizResult
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or "username" not in data:
        return jsonify({"error": "invalid input"}), 400

    user = User.query.filter_by(username=data["username"]).first()
    if user:
        return jsonify({"user_id": user.id})  # already exists

    user = User(username=data["username"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"user_id": user.id})

@app.route("/upload_test", methods=["POST"])
def upload_test():
    data = request.json
    result = TestResult(**data)
    db.session.add(result)
    db.session.commit()
    return jsonify({"status": "saved"})

@app.route("/upload_quiz", methods=["POST"])
def upload_quiz():
    data = request.json
    quiz = QuizResult(**data)
    db.session.add(quiz)
    db.session.commit()
    return jsonify({"status": "saved"})
