<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  DataAnalysis,
  Fold,
  Menu as MenuIcon,
  Reading,
  School,
  Setting,
  SwitchButton,
  Tickets,
  User,
} from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import api from "../api";

const route = useRoute();
const router = useRouter();
const collapsed = ref(false);
const mobileOpen = ref(false);
const user = ref({ username: "加载中" });
const title = computed(() => route.meta.title || "管理系统");

const menus = [
  { path: "/dashboard", label: "数据概览", icon: DataAnalysis },
  { path: "/students", label: "学生管理", icon: User },
  { path: "/courses", label: "课程管理", icon: Reading },
  { path: "/scores", label: "成绩管理", icon: Tickets },
  { path: "/profile", label: "账户设置", icon: Setting },
];

async function loadUser() {
  const { data } = await api.get("/auth/me");
  user.value = data;
}

async function logout() {
  await api.post("/auth/logout");
  ElMessage.success("已安全退出");
  router.replace("/login");
}

function navigate(path) {
  router.push(path);
  mobileOpen.value = false;
}

onMounted(loadUser);
</script>

<template>
  <div class="admin-app">
    <aside class="sidebar" :class="{ collapsed }">
      <div class="brand">
        <div class="brand-mark"><School /></div>
        <div v-show="!collapsed" class="brand-copy">
          <strong>知衡</strong>
          <span>Academic Console</span>
        </div>
      </div>

      <nav class="nav-list">
        <button
          v-for="item in menus"
          :key="item.path"
          :class="['nav-item', { active: route.path === item.path }]"
          :title="collapsed ? item.label : ''"
          @click="navigate(item.path)"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span v-show="!collapsed">{{ item.label }}</span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <button class="nav-item" @click="logout">
          <el-icon><SwitchButton /></el-icon>
          <span v-show="!collapsed">退出登录</span>
        </button>
      </div>
    </aside>

    <el-drawer v-model="mobileOpen" direction="ltr" size="270px" :with-header="false" class="mobile-drawer">
      <div class="mobile-brand">
        <div class="brand-mark"><School /></div>
        <div><strong>知衡</strong><span>学生成绩管理系统</span></div>
      </div>
      <nav class="nav-list mobile-nav">
        <button
          v-for="item in menus"
          :key="item.path"
          :class="['nav-item', { active: route.path === item.path }]"
          @click="navigate(item.path)"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
        </button>
      </nav>
    </el-drawer>

    <main class="main-area">
      <header class="topbar">
        <button class="icon-button desktop-toggle" @click="collapsed = !collapsed">
          <el-icon><Fold v-if="!collapsed" /><MenuIcon v-else /></el-icon>
        </button>
        <button class="icon-button mobile-toggle" @click="mobileOpen = true">
          <el-icon><MenuIcon /></el-icon>
        </button>
        <div class="topbar-title">
          <span>学生成绩管理系统</span>
          <strong>{{ title }}</strong>
        </div>
        <div class="user-chip" @click="router.push('/profile')">
          <div class="avatar">{{ user.username?.slice(0, 1).toUpperCase() }}</div>
          <div class="user-meta">
            <strong>{{ user.username }}</strong>
            <span>系统管理员</span>
          </div>
        </div>
      </header>
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.admin-app { min-height: 100vh; display: flex; }
.sidebar { position: fixed; inset: 0 auto 0 0; z-index: 20; width: 244px; display: flex; flex-direction: column; background: linear-gradient(180deg, #102544 0%, #132e50 58%, #0d203b 100%); color: white; transition: width .22s ease; box-shadow: 8px 0 30px rgba(16, 37, 68, .12); }
.sidebar.collapsed { width: 82px; }
.brand { height: 84px; display: flex; align-items: center; gap: 13px; padding: 0 21px; border-bottom: 1px solid rgba(255,255,255,.08); }
.brand-mark { width: 42px; height: 42px; flex: 0 0 42px; display: grid; place-items: center; color: white; border-radius: 13px; background: linear-gradient(135deg, #4079ff, #21c1d6); box-shadow: 0 8px 20px rgba(44, 123, 255, .28); }
.brand-mark :deep(svg) { width: 23px; height: 23px; }
.brand-copy { display: flex; flex-direction: column; white-space: nowrap; }
.brand-copy strong { font-size: 21px; letter-spacing: 2px; }
.brand-copy span { margin-top: 2px; font-size: 10px; color: #92a8c5; letter-spacing: 1px; }
.nav-list { display: flex; flex-direction: column; gap: 7px; padding: 24px 13px; }
.nav-item { width: 100%; height: 48px; display: flex; align-items: center; gap: 14px; padding: 0 15px; border: 0; border-radius: 12px; color: #a9bdd5; background: transparent; cursor: pointer; transition: .18s ease; white-space: nowrap; }
.nav-item:hover { color: white; background: rgba(255,255,255,.08); transform: translateX(2px); }
.nav-item.active { color: white; background: linear-gradient(90deg, rgba(66,121,255,.9), rgba(41,177,213,.75)); box-shadow: 0 10px 24px rgba(39, 106, 215, .25); }
.nav-item .el-icon { flex: 0 0 auto; font-size: 20px; }
.nav-item span { font-size: 14px; font-weight: 600; }
.sidebar-footer { margin-top: auto; padding: 12px 13px 22px; border-top: 1px solid rgba(255,255,255,.08); }
.main-area { width: calc(100% - 244px); min-height: 100vh; margin-left: 244px; transition: .22s ease; }
.collapsed + .main-area { width: calc(100% - 82px); margin-left: 82px; }
.topbar { height: 84px; display: flex; align-items: center; gap: 18px; padding: 0 30px; background: rgba(255,255,255,.94); border-bottom: 1px solid #e9eef6; backdrop-filter: blur(12px); }
.icon-button { width: 40px; height: 40px; display: grid; place-items: center; border: 1px solid #e4eaf3; border-radius: 11px; background: white; color: #52647e; cursor: pointer; }
.topbar-title { display: flex; flex-direction: column; }
.topbar-title span { color: #8c9ab0; font-size: 11px; }
.topbar-title strong { margin-top: 2px; color: #14243f; font-size: 17px; }
.user-chip { margin-left: auto; display: flex; align-items: center; gap: 11px; padding: 7px 10px 7px 7px; border-radius: 13px; cursor: pointer; transition: .18s; }
.user-chip:hover { background: #f2f6fc; }
.avatar { width: 39px; height: 39px; display: grid; place-items: center; border-radius: 12px; color: white; font-weight: 700; background: linear-gradient(135deg, #2f6bff, #20b8c9); }
.user-meta { display: flex; flex-direction: column; }
.user-meta strong { font-size: 13px; color: #263751; }
.user-meta span { margin-top: 2px; font-size: 10px; color: #94a0b3; }
.mobile-toggle { display: none; }
.mobile-brand { display: flex; gap: 12px; align-items: center; padding: 22px 10px 15px; }
.mobile-brand > div:last-child { display: flex; flex-direction: column; color: #14243f; }
.mobile-brand span { font-size: 11px; color: #8694a9; }
.mobile-nav .nav-item { color: #52647e; }
.mobile-nav .nav-item.active { color: white; }
@media (max-width: 900px) {
  .sidebar { display: none; }
  .main-area, .collapsed + .main-area { width: 100%; margin-left: 0; }
  .topbar { padding: 0 16px; }
  .desktop-toggle { display: none; }
  .mobile-toggle { display: grid; }
}
@media (max-width: 520px) {
  .user-meta { display: none; }
  .topbar-title span { display: none; }
}
</style>
