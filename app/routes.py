from flask import Flask, request, jsonify
from app.models import db, User, TestResult, QuizResult
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


# Create database tables before the first request
@app.before_request
def create_tables():
    db.create_all()

# Register a new user
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    # Validate input
    if not data or "username" not in data:
        return jsonify({"error": "invalid input"}), 400

    # Check if user already exists
    user = User.query.filter_by(username=data["username"]).first()
    if user:
        return jsonify({"user_id": user.id})

    # Create new user
    user = User(username=data["username"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"user_id": user.id})

# Upload test results
@app.route("/upload_test", methods=["POST"])
def upload_test():
    data = request.json
    result = TestResult(**data)
    db.session.add(result)
    db.session.commit()
    return jsonify({"status": "saved"})

# Upload quiz results
@app.route("/upload_quiz", methods=["POST"])
def upload_quiz():
    data = request.json
    quiz = QuizResult(
        user_id=data["user_id"],
        score=data["score"],
        total_questions=data["total_questions"],
        csv_data=data.get("csv_data", "")
    )
    db.session.add(quiz)
    db.session.commit()
    return jsonify({"status": "saved"})

# Get quiz CSV data for a user
@app.route("/quiz_csv/<int:user_id>", methods=["GET"])
def get_quiz_csv(user_id):
    quiz = (
        QuizResult.query.filter_by(user_id=user_id)
        .order_by(QuizResult.timestamp.desc())
        .first()
    )
    if not quiz or not quiz.csv_data:
        return jsonify({})
    return jsonify({
        "timestamp": quiz.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "csv_data": quiz.csv_data
    })
