# 知衡——学生成绩管理平台

这是一个前后端分离的学生成绩管理项目。后端使用 Flask 提供 JSON API，前端使用 Vue 3 构建管理工作台，数据保存在 MySQL 中。系统把原有的用户账户管理 API 与学生成绩管理功能整合到一套完整流程中：用户登录后，可以维护学生、课程和成绩，并在首页查看统计结果。

## 项目功能

- 账户注册、登录、退出和当前登录用户查询。
- 使用 Werkzeug 对密码进行哈希存储与校验。
- 使用 Flask Session 保存登录状态，并对业务接口进行登录检查。
- 学生档案的新增、查询、修改、删除、关键词搜索和分页。
- 课程信息的新增、查询、修改、删除、关键词搜索和分页。
- 成绩记录的录入、筛选、修改、删除和重复录入校验。
- 按学生、课程、学期和关键词筛选成绩。
- 首页展示学生数、课程数、成绩记录数、平均成绩、成绩区间分布和课程平均分。
- 对参数错误、未登录、无权操作、资源不存在和唯一值冲突返回对应 HTTP 状态码。
- 数据库写操作包含事务提交、异常回滚、外键和唯一约束。
- 提供数据库迁移、演示数据命令和自动化接口测试。
- Vue 管理端支持桌面端和移动端响应式布局。

## 技术栈

### 后端

- Python 3
- Flask
- Flask-SQLAlchemy
- Flask-Migrate / Alembic
- MySQL / PyMySQL
- Werkzeug 密码哈希
- Cookie / Session

### 前端

- Vue 3
- Vue Router
- Axios
- Element Plus
- ECharts
- Vite

## 项目结构

```text
flask_user_api/
├─ app.py                         后端配置、模型、CRUD、路由、校验和演示数据命令
├─ blueprints/
│  ├─ __init__.py
│  └─ api.py                      Blueprint写法对照演示，不参与主程序注册
├─ frontend/
│  ├─ src/
│  │  ├─ layouts/                 管理后台公共布局
│  │  ├─ views/                   登录、首页、学生、课程、成绩和账户页面
│  │  ├─ api.js                   Axios请求与错误处理
│  │  ├─ router.js                页面路由与登录守卫
│  │  └─ styles.css               全局样式与响应式规则
│  ├─ package.json
│  └─ vite.config.js
├─ migrations/                    数据库迁移记录
├─ tests/test_api.py              后端接口自动化测试
├─ .env.example                   环境变量示例
├─ .gitignore
└─ requirements.txt
```

## 本地运行

### 1. 创建 MySQL 数据库

```sql
CREATE DATABASE flask_user_api
DEFAULT CHARACTER SET utf8mb4;
```

### 2. 安装后端依赖

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，再填写本机数据库信息和随机密钥：

```ini
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=flask_user_api
SECRET_KEY=一段足够长且随机的字符串
```

真实 `.env` 已被 `.gitignore` 排除，不能上传到 GitHub。

### 4. 应用数据库迁移

```powershell
python -m flask --app app db upgrade
```

仓库已经包含 `migrations`，不要重复执行 `db init`。以后修改模型时再执行：

```powershell
python -m flask --app app db migrate -m "说明本次修改"
python -m flask --app app db upgrade
```

### 5. 写入演示数据（可选）

```powershell
python -m flask --app app seed-demo
```

如果希望清空原有学生、课程和成绩后重新生成演示数据：

```powershell
python -m flask --app app seed-demo --clear
```

该命令不会删除账户数据。

### 6. 启动后端

```powershell
python -m flask --app app run
```

后端默认运行在 `http://127.0.0.1:5000`。

### 7. 启动前端开发服务器

另开一个 PowerShell 窗口：

```powershell
cd frontend
pnpm install
pnpm dev
```

也可以使用 `npm install` 和 `npm run dev`。开发页面默认运行在 `http://127.0.0.1:5173`，Vite 会把 `/auth`、`/users` 和 `/api` 请求代理到 Flask。

## 生产构建

```powershell
cd frontend
pnpm build
cd ..
python -m flask --app app run
```

生成的 `frontend/dist` 会由 Flask 在根地址直接提供，因此构建后访问 `http://127.0.0.1:5000` 即可进入完整页面。

## 自动化测试

测试使用临时 SQLite 内存数据库，不会修改本机 MySQL 数据：

```powershell
python -m unittest discover -s tests -v
```

测试覆盖注册登录、接口登录保护、学生/课程/成绩 CRUD、数据校验、重复数据和首页统计。

## 主要接口

| 方法 | 地址 | 功能 | 需要登录 |
|---|---|---|---|
| POST | `/auth/register` | 注册账户 | 否 |
| POST | `/auth/login` | 登录 | 否 |
| POST | `/auth/logout` | 退出 | 否 |
| GET | `/auth/me` | 当前用户 | 是 |
| GET | `/users` | 用户列表 | 是 |
| GET | `/users/<user_id>` | 查询用户 | 是 |
| PATCH | `/users/<user_id>` | 修改自己的用户名 | 是 |
| DELETE | `/users/<user_id>` | 删除自己的账户 | 是 |
| GET | `/api/dashboard` | 首页统计 | 是 |
| GET / POST | `/api/students` | 学生列表 / 新增学生 | 是 |
| GET / PATCH / DELETE | `/api/students/<student_id>` | 查询 / 修改 / 删除学生 | 是 |
| GET / POST | `/api/courses` | 课程列表 / 新增课程 | 是 |
| PATCH / DELETE | `/api/courses/<course_id>` | 修改 / 删除课程 | 是 |
| GET / POST | `/api/scores` | 成绩列表 / 录入成绩 | 是 |
| PATCH / DELETE | `/api/scores/<score_id>` | 修改 / 删除成绩 | 是 |

注册请求示例：

```json
{
  "username": "zhangsan",
  "password": "123456"
}
```

录入成绩示例：

```json
{
  "student_id": 1,
  "course_id": 1,
  "score": 92.5,
  "semester": "2025-2026-1"
}
```

## Blueprint 功能演示

`blueprints/api.py` 保留了用户认证与用户接口的 Blueprint 对照写法，用于说明 `Blueprint`、`url_prefix` 和 `app.register_blueprint()` 的工作方式。主程序没有注册该文件，避免同一路由重复；实际运行逻辑仍集中在 `app.py` 中，便于连续阅读。

## 开发与 AI 协作说明

- 原有用户模型、用户 CRUD、注册登录、Session 状态和基础数据库练习来自作者此前完成的 Flask 学习项目。
- 作者确定整合方向、业务功能、数据字段和验收要求，并负责运行、接口验证、结果检查与后续维护。
- AI Coding Agent 辅助完成 Vue 管理端、响应式样式、前后端联调、目录整理和 README 编写。
- 学生、课程、成绩和统计模块是在原练习基础上的扩展实现；作者应在用于简历或面试前逐个理解、复习并能够独立解释和修改。

该说明用于如实记录开发过程。项目重点仍然是 Flask JSON API、数据库建模、CRUD、认证状态和前后端接口协作。
