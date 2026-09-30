"""蓝图功能演示。

这里复制了app.py中的八个业务路由，用来展示Blueprint写法。
完整业务代码仍保留在app.py中，项目日常运行使用app.py。
此演示蓝图没有在当前应用中注册。
"""

from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash

# 复用app.py中已有的数据库操作函数。
from app import (
    delete_user,
    get_all_users,
    insert_user,
    select_user_by_id,
    select_user_by_username,
    update_username,
)


# 最终地址 = url_prefix + 路由上的路径。
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
users_bp = Blueprint("users", __name__, url_prefix="/users")


@auth_bp.post("/register")
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

@auth_bp.post("/login")
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

@auth_bp.get("/me")
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

@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "退出成功"}), 200

@users_bp.get("")
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

@users_bp.get("/<int:user_id>")
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

@users_bp.patch("/<int:user_id>")
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

@users_bp.delete("/<int:user_id>")
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

# 实际使用蓝图时，在没有重复定义这些路由的应用中注册：
# app.register_blueprint(auth_bp)
# app.register_blueprint(users_bp)
