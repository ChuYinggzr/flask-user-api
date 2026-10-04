import { createRouter, createWebHashHistory } from "vue-router";
import api from "./api";
import AdminLayout from "./layouts/AdminLayout.vue";

const LoginView = () => import("./views/LoginView.vue");
const DashboardView = () => import("./views/DashboardView.vue");
const StudentsView = () => import("./views/StudentsView.vue");
const CoursesView = () => import("./views/CoursesView.vue");
const ScoresView = () => import("./views/ScoresView.vue");
const ProfileView = () => import("./views/ProfileView.vue");

const routes = [
  { path: "/login", name: "login", component: LoginView, meta: { public: true } },
  {
    path: "/",
    component: AdminLayout,
    children: [
      { path: "", redirect: "/dashboard" },
      { path: "dashboard", name: "dashboard", component: DashboardView, meta: { title: "数据概览" } },
      { path: "students", name: "students", component: StudentsView, meta: { title: "学生管理" } },
      { path: "courses", name: "courses", component: CoursesView, meta: { title: "课程管理" } },
      { path: "scores", name: "scores", component: ScoresView, meta: { title: "成绩管理" } },
      { path: "profile", name: "profile", component: ProfileView, meta: { title: "账户设置" } },
    ],
  },
  { path: "/:pathMatch(.*)*", redirect: "/dashboard" },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

router.beforeEach(async (to) => {
  if (to.meta.public) return true;
  try {
    await api.get("/auth/me");
    return true;
  } catch {
    return { name: "login", query: { redirect: to.fullPath } };
  }
});

export default router;
