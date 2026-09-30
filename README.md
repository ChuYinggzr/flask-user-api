# Flask 用户账户管理 API

这是一个基于 Flask 和 MySQL 的 JSON API 学习项目。项目实现用户注册、登录、退出、登录状态查询以及基础用户管理功能，不包含 HTML 页面。

## 技术栈

- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- MySQL / PyMySQL
- Werkzeug 密码哈希
- Cookie / Session

## 主要功能

- 注册时校验用户名、密码及密码长度，并对密码进行哈希存储。
- 登录时校验密码，通过 Session 保存登录状态。
- 查询当前登录用户、全部用户以及指定用户。
- 用户只能修改或删除自己的账户。
- 区分参数错误、未登录、无权操作、资源不存在和用户名重复等情况。
- 数据库写操作包含提交、异常回滚和唯一约束处理。
- 登录和账户权限判断直接写在接口函数内，未登录返回401，修改或删除他人账户返回403。
- API 只返回 JSON，不返回密码及密码哈希。

## 项目结构

```text
flask_user_api/
├─ app.py                  配置、模型、CRUD、路由和错误处理
├─ blueprints/
│  ├─ __init__.py          蓝图包标识文件
│  └─ api.py               蓝图功能演示
├─ .env.example            环境变量示例
├─ .gitignore
├─ migrations/             数据库迁移文件
└─ requirements.txt
```

## 运行方法

### 1. 创建数据库

在 MySQL 中执行：

```sql
CREATE DATABASE flask_user_api
DEFAULT CHARACTER SET utf8mb4;
```

### 2. 安装依赖

```powershell
python -m pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 并改名为 `.env`，填写自己的 MySQL 密码和随机 `SECRET_KEY`。

真实 `.env` 已被 `.gitignore` 排除，不能上传到 GitHub。

### 4. 应用数据库迁移

仓库已经包含`migrations`目录，首次运行项目时只需要执行：

```powershell
python -m flask --app app:app db upgrade
```

以后修改`User`模型时，再执行：

```powershell
python -m flask --app app:app db migrate -m "说明本次修改"
python -m flask --app app:app db upgrade
```

不要再次执行`db init`，否则会与仓库中已有的迁移目录冲突。

### 5. 启动项目

```powershell
python -m flask --app app:app run
```

访问 `http://127.0.0.1:5000/` 可以查看接口列表。

## 接口

| 请求 | 地址 | 功能 | 是否需要登录 |
|---|---|---|---|
| POST | `/auth/register` | 注册 | 否 |
| POST | `/auth/login` | 登录 | 否 |
| POST | `/auth/logout` | 退出 | 否 |
| GET | `/auth/me` | 当前用户 | 是 |
| GET | `/users` | 用户列表 | 是 |
| GET | `/users/<user_id>` | 指定用户 | 是 |
| PATCH | `/users/<user_id>` | 修改自己的用户名 | 是 |
| DELETE | `/users/<user_id>` | 删除自己的账户 | 是 |

注册请求示例：

```json
{
  "username": "zhangsan",
  "password": "123456"
}
```

## 蓝图功能演示

`blueprints/api.py`复制了`app.py`中的八个业务路由，用来展示Blueprint如何组织接口。认证和用户接口分别使用以下蓝图：

```python
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
users_bp = Blueprint("users", __name__, url_prefix="/users")
```

例如`@auth_bp.post("/login")`对应`/auth/login`，`@users_bp.get("/<int:user_id>")`对应`/users/<int:user_id>`。文件复用`app.py`中的数据库操作函数，末尾以注释列出`app.register_blueprint(...)`注册方式。

该文件是功能演示，当前应用未注册此蓝图。完整业务代码仍保留在`app.py`中，项目日常运行使用`app.py`。

## AI 辅助说明

- `User` 模型、用户 CRUD、注册登录、Session 状态以及用户查询等主体业务逻辑，来源于作者此前独立完成的 Flask 学习练习。
- AI 协助整理原来的代码顺序和格式；项目规模较小，因此配置、模型、CRUD和全部路由统一保留在`app.py`中，方便连续阅读。
- AI 将现有接口另行复制为`blueprints/api.py`中的蓝图对照版本；`app.py`完整保留主体业务功能。
- 环境变量、数据库连接配置、项目说明文档、统一错误处理和接口内的登录权限检查由 AI 辅助编写。
- AI 同时修复了原练习代码中的查询方法拼写、遗漏返回值和部分接口逻辑不完整等问题。作者需要能够独立运行、解释并修改最终代码。
