import os
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import quote_plus

import click
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, func, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

load_dotenv()

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIST / "assets"),
    static_url_path="/assets",
)
app.json.ensure_ascii = False

secret_key = os.getenv("SECRET_KEY")

if not secret_key:
    raise RuntimeError("缺少SECRET_KEY，请先在.env文件中配置")

app.config["SECRET_KEY"] = secret_key
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)

database_url = os.getenv("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    db_user = os.getenv("DB_USER", "root")
    db_password = quote_plus(os.getenv("DB_PASSWORD", ""))
    db_host = os.getenv("DB_HOST", "127.0.0.1")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "flask_user_api")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{db_user}:{db_password}"
        f"@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    )
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_no = db.Column(db.String(30), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    major = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)
    enrollment_year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    scores = db.relationship(
        "Score",
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_no": self.student_no,
            "name": self.name,
            "gender": self.gender,
            "major": self.major,
            "class_name": self.class_name,
            "enrollment_year": self.enrollment_year,
            "created_at": self.created_at.isoformat(),
        }


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String(30), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Numeric(3, 1), nullable=False)
    teacher = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    scores = db.relationship(
        "Score",
        back_populates="course",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "course_code": self.course_code,
            "name": self.name,
            "credits": float(self.credits),
            "teacher": self.teacher,
            "created_at": self.created_at.isoformat(),
        }


class Score(db.Model):
    __tablename__ = "scores"
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "course_id",
            "semester",
            name="uq_score_student_course_semester",
        ),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    score = db.Column(db.Numeric(5, 2), nullable=False)
    semester = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
        onupdate=db.func.now(),
    )
    student = db.relationship("Student", back_populates="scores")
    course = db.relationship("Course", back_populates="scores")

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_no": self.student.student_no,
            "student_name": self.student.name,
            "course_id": self.course_id,
            "course_code": self.course.course_code,
            "course_name": self.course.name,
            "score": float(self.score),
            "semester": self.semester,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


def insert_user(username, password):
    try:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user is not None:
            return "duplicate"

        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return user.id
    except IntegrityError:
        db.session.rollback()
        return "duplicate"
    except SQLAlchemyError:
        db.session.rollback()
        raise


def select_user_by_id(user_id):
    return db.session.get(User, user_id)


def select_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_all_users():
    return User.query.order_by(User.id.desc()).all()


def update_username(user_id, username):
    try:
        user = db.session.get(User, user_id)
        if user is None:
            return "not_found"

        user.username = username
        db.session.commit()
        return "updated"
    except IntegrityError:
        db.session.rollback()
        return "duplicate"
    except SQLAlchemyError:
        db.session.rollback()
        raise


def delete_user(user_id):
    try:
        user = db.session.get(User, user_id)
        if user is None:
            return False

        db.session.delete(user)
        db.session.commit()
        return True
    except SQLAlchemyError:
        db.session.rollback()
        raise


def get_json_object():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify({"message": "请求体必须是JSON对象"}), 400)
    return data, None


def require_login():
    user_id = session.get("user_id")
    if user_id is None:
        return None, (jsonify({"message": "请先登录"}), 401)

    user = select_user_by_id(user_id)
    if user is None:
        session.clear()
        return None, (jsonify({"message": "登录状态已经失效"}), 401)
    return user, None


def parse_pagination():
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=10, type=int)
    if page is None or page < 1:
        return None, (jsonify({"message": "page必须是大于等于1的整数"}), 400)
    if page_size is None or page_size < 1 or page_size > 100:
        return None, (jsonify({"message": "page_size必须是1到100之间的整数"}), 400)
    return (page, page_size), None


def paginated_response(pagination):
    return {
        "items": [item.to_dict() for item in pagination.items],
        "pagination": {
            "page": pagination.page,
            "page_size": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        },
    }


def clean_string(data, field, label, max_length):
    value = data.get(field)
    if not isinstance(value, str):
        return None, f"{label}必须是字符串"
    value = value.strip()
    if not value:
        return None, f"{label}不能为空"
    if len(value) > max_length:
        return None, f"{label}不能超过{max_length}个字符"
    return value, None


def parse_integer(data, field, label, minimum=None, maximum=None):
    value = data.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        return None, f"{label}必须是整数"
    if minimum is not None and value < minimum:
        return None, f"{label}不能小于{minimum}"
    if maximum is not None and value > maximum:
        return None, f"{label}不能大于{maximum}"
    return value, None


def parse_decimal(data, field, label, minimum, maximum):
    value = data.get(field)
    if isinstance(value, bool):
        return None, f"{label}必须是数字"
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None, f"{label}必须是数字"
    if not number.is_finite() or number < Decimal(str(minimum)) or number > Decimal(str(maximum)):
        return None, f"{label}必须在{minimum}到{maximum}之间"
    return number, None


def validate_student(data):
    values = {}
    for field, label, length in [
        ("student_no", "学号", 30),
        ("name", "姓名", 50),
        ("gender", "性别", 10),
        ("major", "专业", 100),
        ("class_name", "班级", 50),
    ]:
        values[field], error = clean_string(data, field, label, length)
        if error:
            return None, error

    if values["gender"] not in {"男", "女", "其他"}:
        return None, "性别只能是男、女或其他"

    values["enrollment_year"], error = parse_integer(
        data, "enrollment_year", "入学年份", 2000, 2100
    )
    if error:
        return None, error
    return values, None


def validate_course(data):
    values = {}
    for field, label, length in [
        ("course_code", "课程编号", 30),
        ("name", "课程名称", 100),
        ("teacher", "授课教师", 50),
    ]:
        values[field], error = clean_string(data, field, label, length)
        if error:
            return None, error

    values["credits"], error = parse_decimal(data, "credits", "学分", 0.5, 20)
    if error:
        return None, error
    return values, None


def validate_score(data):
    values = {}
    values["student_id"], error = parse_integer(data, "student_id", "学生ID", 1)
    if error:
        return None, error
    values["course_id"], error = parse_integer(data, "course_id", "课程ID", 1)
    if error:
        return None, error
    values["score"], error = parse_decimal(data, "score", "成绩", 0, 100)
    if error:
        return None, error
    values["semester"], error = clean_string(data, "semester", "学期", 30)
    if error:
        return None, error
    return values, None


@app.post("/auth/register")
def register():
    data, error_response = get_json_object()
    if error_response:
        return error_response

    username = data.get("username")
    password = data.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"message": "username和password必须是字符串"}), 400

    username = username.strip()
    if not username:
        return jsonify({"message": "用户名不能为空"}), 400
    if len(username) > 50:
        return jsonify({"message": "用户名不能超过50个字符"}), 400
    if not password:
        return jsonify({"message": "密码不能为空"}), 400
    if len(password) < 6 or len(password) > 128:
        return jsonify({"message": "密码长度必须在6到128个字符之间"}), 400

    result = insert_user(username, password)
    if result == "duplicate":
        return jsonify({"message": "用户名已经存在"}), 409
    return jsonify({"message": "注册成功", "id": result, "username": username}), 201


@app.post("/auth/login")
def login():
    data, error_response = get_json_object()
    if error_response:
        return error_response

    username = data.get("username")
    password = data.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"message": "username和password必须是字符串"}), 400

    username = username.strip()
    if not username or not password:
        return jsonify({"message": "用户名和密码不能为空"}), 400

    user = select_user_by_username(username)
    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "用户名或密码错误"}), 401

    session.clear()
    session.permanent = True
    session["user_id"] = user.id
    return jsonify({"message": "登录成功", "id": user.id, "username": user.username}), 200


@app.get("/auth/me")
def current_user():
    user, error_response = require_login()
    if error_response:
        return error_response
    return jsonify({
        "id": user.id,
        "username": user.username,
        "created_at": user.created_at.isoformat(),
    }), 200


@app.post("/auth/logout")
def logout():
    session.clear()
    return jsonify({"message": "退出成功"}), 200


@app.get("/users")
def list_users():
    _user, error_response = require_login()
    if error_response:
        return error_response
    return jsonify([
        {"id": user.id, "username": user.username, "created_at": user.created_at.isoformat()}
        for user in get_all_users()
    ]), 200


@app.get("/users/<int:user_id>")
def get_user(user_id):
    _user, error_response = require_login()
    if error_response:
        return error_response

    user = select_user_by_id(user_id)
    if user is None:
        return jsonify({"message": "用户不存在"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "created_at": user.created_at.isoformat(),
    }), 200


@app.patch("/users/<int:user_id>")
def change_username(user_id):
    current, error_response = require_login()
    if error_response:
        return error_response
    if current.id != user_id:
        return jsonify({"message": "只能修改自己的账户"}), 403

    data, error_response = get_json_object()
    if error_response:
        return error_response
    username, error = clean_string(data, "username", "用户名", 50)
    if error:
        return jsonify({"message": error}), 400

    status = update_username(user_id, username)
    if status == "not_found":
        session.clear()
        return jsonify({"message": "用户不存在"}), 404
    if status == "duplicate":
        return jsonify({"message": "用户名已经存在"}), 409
    return jsonify({"message": "用户名修改成功", "id": user_id, "username": username}), 200


@app.delete("/users/<int:user_id>")
def remove_user(user_id):
    current, error_response = require_login()
    if error_response:
        return error_response
    if current.id != user_id:
        return jsonify({"message": "只能删除自己的账户"}), 403
    if not delete_user(user_id):
        session.clear()
        return jsonify({"message": "用户不存在"}), 404
    session.clear()
    return "", 204


@app.get("/api/dashboard")
def dashboard():
    _user, error_response = require_login()
    if error_response:
        return error_response

    average_score = db.session.query(func.avg(Score.score)).scalar()
    distribution = {"excellent": 0, "good": 0, "pass": 0, "fail": 0}
    grouped_scores = db.session.query(Score.score, func.count(Score.id)).group_by(Score.score).all()
    for value, count in grouped_scores:
        number = float(value)
        if number >= 90:
            distribution["excellent"] += count
        elif number >= 80:
            distribution["good"] += count
        elif number >= 60:
            distribution["pass"] += count
        else:
            distribution["fail"] += count

    course_averages = (
        db.session.query(Course.name, func.avg(Score.score))
        .join(Score, Course.id == Score.course_id)
        .group_by(Course.id, Course.name)
        .order_by(func.avg(Score.score).desc())
        .limit(8)
        .all()
    )
    return jsonify({
        "student_count": Student.query.count(),
        "course_count": Course.query.count(),
        "score_count": Score.query.count(),
        "average_score": round(float(average_score), 2) if average_score is not None else 0,
        "score_distribution": distribution,
        "course_averages": [
            {"course_name": name, "average_score": round(float(average), 2)}
            for name, average in course_averages
        ],
    }), 200


@app.get("/api/students")
def list_students():
    _user, error_response = require_login()
    if error_response:
        return error_response
    page_data, error_response = parse_pagination()
    if error_response:
        return error_response

    keyword = request.args.get("keyword", "").strip()
    query = Student.query
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(or_(
            Student.student_no.like(pattern),
            Student.name.like(pattern),
            Student.major.like(pattern),
            Student.class_name.like(pattern),
        ))

    page, page_size = page_data
    pagination = query.order_by(Student.id.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )
    return jsonify(paginated_response(pagination)), 200


@app.post("/api/students")
def create_student():
    _user, error_response = require_login()
    if error_response:
        return error_response
    data, error_response = get_json_object()
    if error_response:
        return error_response
    values, error = validate_student(data)
    if error:
        return jsonify({"message": error}), 400

    try:
        student = Student(**values)
        db.session.add(student)
        db.session.commit()
        return jsonify({"message": "学生创建成功", "student": student.to_dict()}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "学号已经存在"}), 409


@app.get("/api/students/<int:student_id>")
def get_student(student_id):
    _user, error_response = require_login()
    if error_response:
        return error_response
    student = db.session.get(Student, student_id)
    if student is None:
        return jsonify({"message": "学生不存在"}), 404
    result = student.to_dict()
    result["scores"] = [score.to_dict() for score in student.scores]
    return jsonify(result), 200


@app.patch("/api/students/<int:student_id>")
def update_student(student_id):
    _user, error_response = require_login()
    if error_response:
        return error_response
    student = db.session.get(Student, student_id)
    if student is None:
        return jsonify({"message": "学生不存在"}), 404
    data, error_response = get_json_object()
    if error_response:
        return error_response
    values, error = validate_student(data)
    if error:
        return jsonify({"message": error}), 400

    try:
        for field, value in values.items():
            setattr(student, field, value)
        db.session.commit()
        return jsonify({"message": "学生信息修改成功", "student": student.to_dict()}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "学号已经存在"}), 409


@app.delete("/api/students/<int:student_id>")
def delete_student(student_id):
    _user, error_response = require_login()
    if error_response:
        return error_response
    student = db.session.get(Student, student_id)
    if student is None:
        return jsonify({"message": "学生不存在"}), 404
    db.session.delete(student)
    db.session.commit()
    return "", 204


@app.get("/api/courses")
def list_courses():
    _user, error_response = require_login()
    if error_response:
        return error_response
    page_data, error_response = parse_pagination()
    if error_response:
        return error_response

    keyword = request.args.get("keyword", "").strip()
    query = Course.query
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(or_(
            Course.course_code.like(pattern),
            Course.name.like(pattern),
            Course.teacher.like(pattern),
        ))
    page, page_size = page_data
    pagination = query.order_by(Course.id.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )
    return jsonify(paginated_response(pagination)), 200


@app.post("/api/courses")
def create_course():
    _user, error_response = require_login()
    if error_response:
        return error_response
    data, error_response = get_json_object()
    if error_response:
        return error_response
    values, error = validate_course(data)
    if error:
        return jsonify({"message": error}), 400

    try:
        course = Course(**values)
        db.session.add(course)
        db.session.commit()
        return jsonify({"message": "课程创建成功", "course": course.to_dict()}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "课程编号已经存在"}), 409


@app.patch("/api/courses/<int:course_id>")
def update_course(course_id):
    _user, error_response = require_login()
    if error_response:
        return error_response
    course = db.session.get(Course, course_id)
    if course is None:
        return jsonify({"message": "课程不存在"}), 404
    data, error_response = get_json_object()
    if error_response:
        return error_response
    values, error = validate_course(data)
    if error:
        return jsonify({"message": error}), 400

    try:
        for field, value in values.items():
            setattr(course, field, value)
        db.session.commit()
        return jsonify({"message": "课程信息修改成功", "course": course.to_dict()}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "课程编号已经存在"}), 409


@app.delete("/api/courses/<int:course_id>")
def delete_course(course_id):
    _user, error_response = require_login()
    if error_response:
        return error_response
    course = db.session.get(Course, course_id)
    if course is None:
        return jsonify({"message": "课程不存在"}), 404
    db.session.delete(course)
    db.session.commit()
    return "", 204


@app.get("/api/scores")
def list_scores():
    _user, error_response = require_login()
    if error_response:
        return error_response
    page_data, error_response = parse_pagination()
    if error_response:
        return error_response

    query = Score.query.join(Student).join(Course)
    keyword = request.args.get("keyword", "").strip()
    semester = request.args.get("semester", "").strip()
    student_id = request.args.get("student_id", type=int)
    course_id = request.args.get("course_id", type=int)
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(or_(
            Student.student_no.like(pattern),
            Student.name.like(pattern),
            Course.course_code.like(pattern),
            Course.name.like(pattern),
        ))
    if semester:
        query = query.filter(Score.semester == semester)
    if student_id:
        query = query.filter(Score.student_id == student_id)
    if course_id:
        query = query.filter(Score.course_id == course_id)

    page, page_size = page_data
    pagination = query.order_by(Score.id.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )
    return jsonify(paginated_response(pagination)), 200


@app.post("/api/scores")
def create_score():
    _user, error_response = require_login()
    if error_response:
        return error_response
    data, error_response = get_json_object()
    if error_response:
        return error_response
    values, error = validate_score(data)
    if error:
        return jsonify({"message": error}), 400
    if db.session.get(Student, values["student_id"]) is None:
        return jsonify({"message": "学生不存在"}), 404
    if db.session.get(Course, values["course_id"]) is None:
        return jsonify({"message": "课程不存在"}), 404

    try:
        score = Score(**values)
        db.session.add(score)
        db.session.commit()
        return jsonify({"message": "成绩录入成功", "score": score.to_dict()}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "该学生在此学期已经录入过这门课程"}), 409


@app.patch("/api/scores/<int:score_id>")
def update_score(score_id):
    _user, error_response = require_login()
    if error_response:
        return error_response
    record = db.session.get(Score, score_id)
    if record is None:
        return jsonify({"message": "成绩记录不存在"}), 404
    data, error_response = get_json_object()
    if error_response:
        return error_response
    values, error = validate_score(data)
    if error:
        return jsonify({"message": error}), 400
    if db.session.get(Student, values["student_id"]) is None:
        return jsonify({"message": "学生不存在"}), 404
    if db.session.get(Course, values["course_id"]) is None:
        return jsonify({"message": "课程不存在"}), 404

    try:
        for field, value in values.items():
            setattr(record, field, value)
        db.session.commit()
        return jsonify({"message": "成绩修改成功", "score": record.to_dict()}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "该学生在此学期已经录入过这门课程"}), 409


@app.delete("/api/scores/<int:score_id>")
def delete_score(score_id):
    _user, error_response = require_login()
    if error_response:
        return error_response
    record = db.session.get(Score, score_id)
    if record is None:
        return jsonify({"message": "成绩记录不存在"}), 404
    db.session.delete(record)
    db.session.commit()
    return "", 204


@app.cli.command("seed-demo")
@click.option("--clear", is_flag=True, help="先清空学生、课程和成绩演示数据")
def seed_demo(clear):
    """写入便于展示页面和统计图表的示例数据。"""
    if clear:
        Score.query.delete()
        Student.query.delete()
        Course.query.delete()
        db.session.commit()

    if Student.query.first() or Course.query.first() or Score.query.first():
        click.echo("数据库中已有业务数据，未重复写入。需要重置时请使用 --clear。")
        return

    students = [
        Student(student_no="20230001", name="张三", gender="男", major="计算机科学与技术", class_name="计科2301", enrollment_year=2023),
        Student(student_no="20230002", name="李四", gender="女", major="计算机科学与技术", class_name="计科2301", enrollment_year=2023),
        Student(student_no="20230003", name="王五", gender="男", major="软件工程", class_name="软工2302", enrollment_year=2023),
        Student(student_no="20240001", name="赵六", gender="女", major="数据科学与大数据技术", class_name="数据2401", enrollment_year=2024),
    ]
    courses = [
        Course(course_code="CS101", name="Python程序设计", credits=Decimal("3.0"), teacher="陈老师"),
        Course(course_code="CS201", name="数据结构", credits=Decimal("3.5"), teacher="周老师"),
        Course(course_code="DB301", name="数据库原理与设计", credits=Decimal("2.5"), teacher="刘老师"),
    ]
    db.session.add_all(students + courses)
    db.session.flush()

    scores = [
        Score(student_id=students[0].id, course_id=courses[0].id, score=Decimal("92"), semester="2025-2026-1"),
        Score(student_id=students[0].id, course_id=courses[1].id, score=Decimal("86"), semester="2025-2026-1"),
        Score(student_id=students[1].id, course_id=courses[0].id, score=Decimal("88"), semester="2025-2026-1"),
        Score(student_id=students[1].id, course_id=courses[2].id, score=Decimal("95"), semester="2025-2026-1"),
        Score(student_id=students[2].id, course_id=courses[1].id, score=Decimal("78"), semester="2025-2026-1"),
        Score(student_id=students[3].id, course_id=courses[2].id, score=Decimal("59"), semester="2025-2026-1"),
    ]
    db.session.add_all(scores)
    db.session.commit()
    click.echo("演示数据写入完成：4名学生、3门课程、6条成绩。")


@app.get("/")
def index():
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return send_from_directory(FRONTEND_DIST, "index.html")

    return jsonify({
        "message": "学生成绩管理系统API运行正常",
        "frontend": "请进入frontend目录启动Vue开发服务器，或先执行npm run build",
        "endpoints": [
            "POST /auth/register",
            "POST /auth/login",
            "POST /auth/logout",
            "GET /auth/me",
            "GET /api/dashboard",
            "GET|POST /api/students",
            "GET|PATCH|DELETE /api/students/<student_id>",
            "GET|POST /api/courses",
            "PATCH|DELETE /api/courses/<course_id>",
            "GET|POST /api/scores",
            "PATCH|DELETE /api/scores/<score_id>",
        ],
    }), 200


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"message": "接口或资源不存在"}), 404


@app.errorhandler(405)
def method_not_allowed(_error):
    return jsonify({"message": "请求方法不允许"}), 405


@app.errorhandler(500)
def internal_server_error(_error):
    db.session.rollback()
    return jsonify({"message": "服务器内部错误"}), 500


if __name__ == "__main__":
    app.run(debug=True)
