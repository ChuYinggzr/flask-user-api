import os
import unittest


os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import app, db  # noqa: E402


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register_and_login(self, username="tester"):
        register_response = self.client.post(
            "/auth/register",
            json={"username": username, "password": "123456"},
        )
        self.assertEqual(register_response.status_code, 201)

        login_response = self.client.post(
            "/auth/login",
            json={"username": username, "password": "123456"},
        )
        self.assertEqual(login_response.status_code, 200)

    def test_register_login_and_current_user(self):
        self.register_and_login()

        response = self.client.get("/auth/me")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["username"], "tester")

    def test_business_endpoints_require_login(self):
        response = self.client.get("/api/students")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["message"], "请先登录")

    def test_student_course_score_crud_and_dashboard(self):
        self.register_and_login()

        student_response = self.client.post(
            "/api/students",
            json={
                "student_no": "20230001",
                "name": "张三",
                "gender": "男",
                "major": "计算机科学与技术",
                "class_name": "计科2301",
                "enrollment_year": 2023,
            },
        )
        self.assertEqual(student_response.status_code, 201)
        student_id = student_response.get_json()["student"]["id"]

        course_response = self.client.post(
            "/api/courses",
            json={
                "course_code": "CS101",
                "name": "Python程序设计",
                "credits": 3,
                "teacher": "陈老师",
            },
        )
        self.assertEqual(course_response.status_code, 201)
        course_id = course_response.get_json()["course"]["id"]

        score_response = self.client.post(
            "/api/scores",
            json={
                "student_id": student_id,
                "course_id": course_id,
                "score": 92.5,
                "semester": "2025-2026-1",
            },
        )
        self.assertEqual(score_response.status_code, 201)
        score_id = score_response.get_json()["score"]["id"]

        list_response = self.client.get("/api/scores?keyword=张三")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.get_json()["pagination"]["total"], 1)

        update_response = self.client.patch(
            f"/api/scores/{score_id}",
            json={
                "student_id": student_id,
                "course_id": course_id,
                "score": 95,
                "semester": "2025-2026-1",
            },
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.get_json()["score"]["score"], 95.0)

        dashboard_response = self.client.get("/api/dashboard")
        dashboard = dashboard_response.get_json()
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertEqual(dashboard["student_count"], 1)
        self.assertEqual(dashboard["course_count"], 1)
        self.assertEqual(dashboard["score_count"], 1)
        self.assertEqual(dashboard["score_distribution"]["excellent"], 1)

        delete_response = self.client.delete(f"/api/students/{student_id}")
        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(self.client.get("/api/scores").get_json()["pagination"]["total"], 0)

    def test_duplicate_and_validation_responses(self):
        self.register_and_login()

        invalid_response = self.client.post(
            "/api/students",
            json={
                "student_no": "",
                "name": "张三",
                "gender": "男",
                "major": "计算机科学与技术",
                "class_name": "计科2301",
                "enrollment_year": 2023,
            },
        )
        self.assertEqual(invalid_response.status_code, 400)

        payload = {
            "student_no": "20230001",
            "name": "张三",
            "gender": "男",
            "major": "计算机科学与技术",
            "class_name": "计科2301",
            "enrollment_year": 2023,
        }
        self.assertEqual(self.client.post("/api/students", json=payload).status_code, 201)
        self.assertEqual(self.client.post("/api/students", json=payload).status_code, 409)


if __name__ == "__main__":
    unittest.main()
