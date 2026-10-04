<script setup>
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Lock, School, User } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import api, { errorMessage } from "../api";

const route = useRoute();
const router = useRouter();
const mode = ref("login");
const loading = ref(false);
const form = reactive({ username: "", password: "", confirmPassword: "" });

async function submit() {
  if (!form.username.trim() || !form.password) {
    ElMessage.warning("请输入用户名和密码");
    return;
  }
  if (mode.value === "register" && form.password !== form.confirmPassword) {
    ElMessage.warning("两次输入的密码不一致");
    return;
  }

  loading.value = true;
  try {
    if (mode.value === "register") {
      await api.post("/auth/register", { username: form.username, password: form.password });
      ElMessage.success("注册成功，请登录");
      mode.value = "login";
      form.password = "";
      form.confirmPassword = "";
    } else {
      await api.post("/auth/login", { username: form.username, password: form.password });
      ElMessage.success("欢迎回来");
      router.replace(route.query.redirect || "/dashboard");
    }
  } catch (error) {
    ElMessage.error(errorMessage(error));
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <main class="login-page">
    <div class="background-grid"></div>
    <section class="intro-panel">
      <div class="intro-content">
        <div class="logo"><School /></div>
        <p class="eyebrow">ACADEMIC MANAGEMENT PLATFORM</p>
        <h1>让每一份成绩<br /><span>清晰、可靠、可追踪</span></h1>
        <p class="intro-text">连接学生、课程与成绩数据，为日常教学管理提供清晰高效的数字化工作台。</p>
        <div class="feature-list">
          <div><strong>01</strong><span>学生档案统一管理</span></div>
          <div><strong>02</strong><span>课程与成绩快速维护</span></div>
          <div><strong>03</strong><span>关键数据可视化分析</span></div>
        </div>
      </div>
    </section>

    <section class="form-panel">
      <div class="form-card">
        <div class="mobile-logo"><div class="logo"><School /></div><strong>知衡</strong></div>
        <p class="form-label">WELCOME BACK</p>
        <h2>{{ mode === 'login' ? '登录管理平台' : '创建管理账户' }}</h2>
        <p class="form-desc">{{ mode === 'login' ? '使用你的账户继续管理教学数据' : '注册后即可进入完整的管理工作台' }}</p>

        <el-form @submit.prevent="submit">
          <el-form-item>
            <el-input v-model="form.username" size="large" placeholder="请输入用户名" :prefix-icon="User" maxlength="50" />
          </el-form-item>
          <el-form-item>
            <el-input v-model="form.password" size="large" type="password" show-password placeholder="请输入密码" :prefix-icon="Lock" @keyup.enter="submit" />
          </el-form-item>
          <el-form-item v-if="mode === 'register'">
            <el-input v-model="form.confirmPassword" size="large" type="password" show-password placeholder="请再次输入密码" :prefix-icon="Lock" @keyup.enter="submit" />
          </el-form-item>
          <el-button class="submit-button" type="primary" size="large" :loading="loading" @click="submit">
            {{ mode === 'login' ? '进入系统' : '立即注册' }}
          </el-button>
        </el-form>

        <div class="switch-mode">
          <span>{{ mode === 'login' ? '还没有账户？' : '已经拥有账户？' }}</span>
          <button @click="mode = mode === 'login' ? 'register' : 'login'">
            {{ mode === 'login' ? '创建账户' : '返回登录' }}
          </button>
        </div>
      </div>
      <p class="copyright">Flask · Vue 3 · MySQL</p>
    </section>
  </main>
</template>

<style scoped>
.login-page { min-height: 100vh; display: grid; grid-template-columns: minmax(420px, 1.08fr) minmax(420px, .92fr); position: relative; overflow: hidden; background: #f7f9fd; }
.background-grid { position: absolute; inset: 0; opacity: .18; background-image: linear-gradient(#dce5f2 1px, transparent 1px), linear-gradient(90deg, #dce5f2 1px, transparent 1px); background-size: 44px 44px; pointer-events: none; }
.intro-panel { position: relative; z-index: 1; display: flex; align-items: center; padding: 70px 9vw; color: white; background: radial-gradient(circle at 20% 15%, rgba(56,125,255,.4), transparent 34%), radial-gradient(circle at 85% 80%, rgba(32,194,213,.22), transparent 28%), linear-gradient(145deg, #0c1f3b, #142f54 70%, #102641); clip-path: polygon(0 0, 92% 0, 100% 100%, 0 100%); }
.intro-content { max-width: 570px; }
.logo { width: 54px; height: 54px; display: grid; place-items: center; border-radius: 16px; color: white; background: linear-gradient(135deg, #3f78ff, #20c0d2); box-shadow: 0 12px 30px rgba(49,120,255,.28); }
.logo :deep(svg) { width: 29px; }
.eyebrow { margin: 34px 0 16px; color: #7fcde5; font-size: 12px; letter-spacing: 2.4px; font-weight: 700; }
h1 { margin: 0; font-size: clamp(40px, 4.4vw, 66px); line-height: 1.15; letter-spacing: -2px; }
h1 span { color: #83d9eb; }
.intro-text { max-width: 500px; margin: 24px 0 42px; color: #afbed1; font-size: 16px; line-height: 1.9; }
.feature-list { display: flex; flex-wrap: wrap; gap: 15px; }
.feature-list div { min-width: 150px; padding: 15px 16px; border: 1px solid rgba(255,255,255,.11); border-radius: 14px; background: rgba(255,255,255,.045); backdrop-filter: blur(8px); }
.feature-list strong { display: block; color: #5fcce0; font-size: 12px; }
.feature-list span { display: block; margin-top: 5px; color: #dce5ef; font-size: 12px; }
.form-panel { position: relative; z-index: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 60px; }
.form-card { width: min(420px, 100%); padding: 46px; border: 1px solid rgba(219,227,239,.85); border-radius: 24px; background: rgba(255,255,255,.88); box-shadow: 0 28px 70px rgba(28,55,95,.13); backdrop-filter: blur(16px); }
.form-label { margin: 0 0 10px; color: #3570f8; font-size: 11px; font-weight: 800; letter-spacing: 2px; }
h2 { margin: 0; color: #172640; font-size: 30px; letter-spacing: -.5px; }
.form-desc { margin: 10px 0 30px; color: #8794a8; font-size: 13px; }
.submit-button { width: 100%; height: 48px; margin-top: 5px; background: linear-gradient(90deg, #3068f4, #3184f7); box-shadow: 0 12px 24px rgba(49,108,245,.22); }
.switch-mode { display: flex; justify-content: center; gap: 5px; margin-top: 24px; color: #8592a6; font-size: 13px; }
.switch-mode button { border: 0; color: #356cfb; background: transparent; font-weight: 700; cursor: pointer; }
.copyright { position: absolute; bottom: 22px; color: #a3afc0; font-size: 11px; letter-spacing: 1px; }
.mobile-logo { display: none; align-items: center; gap: 12px; margin-bottom: 30px; }
.mobile-logo .logo { width: 44px; height: 44px; }
.mobile-logo strong { font-size: 22px; color: #182842; }
@media (max-width: 940px) {
  .login-page { grid-template-columns: 1fr; }
  .intro-panel { display: none; }
  .form-panel { min-height: 100vh; padding: 26px; }
  .mobile-logo { display: flex; }
}
@media (max-width: 520px) {
  .form-card { padding: 32px 24px; }
}
</style>
