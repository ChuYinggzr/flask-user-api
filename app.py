import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from flask import Flask, jsonify, request, session
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash


load_dotenv()

app = Flask(__name__)
app.json.ensure_ascii = False

secret_key = os.getenv("SECRET_KEY")

if not secret_key:
    raise RuntimeError("缺少SECRET_KEY，请先在.env文件中配置")

app.config["SECRET_KEY"] = secret_key
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

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

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )
    username = db.Column(
        db.String(50),
        nullable=False,
        unique=True,
    )
    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now(),
    )


def insert_user(username, password):
    try:
        existing_user = User.query.filter_by(username=username).first()

        if existing_user is not None:
            return "duplicate"

        user = User(
            username=username,
            password_hash=generate_password_hash(password),
        )
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


@app.post("/auth/register")
def register():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "请求体必须是JSON对象"}), 400

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

    return jsonify({
        "message": "注册成功",
        "id": result,
        "username": username,
    }), 201


@app.post("/auth/login")
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "请求体必须是JSON对象"}), 400

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
    session["user_id"] = user.id

    return jsonify({
        "message": "登录成功",
        "id": user.id,
        "username": user.username,
    }), 200


@app.get("/auth/me")
def current_user():
    user_id = session.get("user_id")

    if user_id is None:
        return jsonify({"message": "未登录"}), 401

    user = select_user_by_id(user_id)

    if user is None:
        session.clear()
        return jsonify({"message": "登录状态已经失效"}), 401

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
    if session.get("user_id") is None:
        return jsonify({"message": "请先登录"}), 401

    users = get_all_users()
    result = []

    for user in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "created_at": user.created_at.isoformat(),
        })

    return jsonify(result), 200


@app.get("/users/<int:user_id>")
def get_user(user_id):
    if session.get("user_id") is None:
        return jsonify({"message": "请先登录"}), 401

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
    if session.get("user_id") is None:
        return jsonify({"message": "请先登录"}), 401

    if session["user_id"] != user_id:
        return jsonify({"message": "只能修改自己的账户"}), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"message": "请求体必须是JSON对象"}), 400

    username = data.get("username")

    if not isinstance(username, str):
        return jsonify({"message": "username必须是字符串"}), 400

    username = username.strip()

    if not username:
        return jsonify({"message": "用户名不能为空"}), 400

    if len(username) > 50:
        return jsonify({"message": "用户名不能超过50个字符"}), 400

    status = update_username(user_id, username)

    if status == "not_found":
        session.clear()
        return jsonify({"message": "用户不存在"}), 404

    if status == "duplicate":
        return jsonify({"message": "用户名已经存在"}), 409

    return jsonify({
        "message": "用户名修改成功",
        "id": user_id,
        "username": username,
    }), 200


@app.delete("/users/<int:user_id>")
def remove_user(user_id):
    if session.get("user_id") is None:
        return jsonify({"message": "请先登录"}), 401

    if session["user_id"] != user_id:
        return jsonify({"message": "只能删除自己的账户"}), 403

    if not delete_user(user_id):
        session.clear()
        return jsonify({"message": "用户不存在"}), 404

    session.clear()
    return "", 204


@app.get("/")
def index():
    return jsonify({
        "message": "Flask用户账户管理API运行正常",
        "endpoints": [
            "POST /auth/register",
            "POST /auth/login",
            "POST /auth/logout",
            "GET /auth/me",
            "GET /users",
            "GET /users/<user_id>",
            "PATCH /users/<user_id>",
            "DELETE /users/<user_id>",
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
