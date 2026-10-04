<script setup>
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import api, { errorMessage } from "../api";

const router = useRouter();
const loading = ref(true);
const saving = ref(false);
const user = reactive({ id: null, username: "", created_at: "" });
const username = ref("");

async function loadUser() {
  loading.value = true;
  try {
    const { data } = await api.get("/auth/me");
    Object.assign(user, data);
    username.value = data.username;
  } finally {
    loading.value = false;
  }
}

async function updateUsername() {
  saving.value = true;
  try {
    const { data } = await api.patch(`/users/${user.id}`, { username: username.value });
    user.username = data.username;
    username.value = data.username;
    ElMessage.success("用户名修改成功");
  } catch (error) {
    ElMessage.error(errorMessage(error));
  } finally {
    saving.value = false;
  }
}

async function deleteAccount() {
  try {
    await ElMessageBox.confirm(
      "删除账户后无法恢复，但学生、课程和成绩业务数据不会被删除。",
      "确认删除账户",
      { type: "error", confirmButtonText: "永久删除", cancelButtonText: "取消" },
    );
    await api.delete(`/users/${user.id}`);
    ElMessage.success("账户已删除");
    router.replace("/login");
  } catch (error) {
    if (error !== "cancel") ElMessage.error(errorMessage(error));
  }
}

onMounted(loadUser);
</script>

<template>
  <div class="page-shell" v-loading="loading">
    <div class="page-heading"><div><h1>账户设置</h1><p>查看当前账户信息并修改用户名。</p></div></div>
    <div class="profile-grid">
      <section class="profile-card panel">
        <div class="profile-banner"></div>
        <div class="profile-content">
          <div class="large-avatar">{{ user.username?.slice(0, 1).toUpperCase() }}</div>
          <h2>{{ user.username }}</h2>
          <p>系统管理员</p>
          <dl>
            <div><dt>账户 ID</dt><dd>#{{ user.id }}</dd></div>
            <div><dt>注册时间</dt><dd>{{ user.created_at ? new Date(user.created_at).toLocaleString() : '-' }}</dd></div>
            <div><dt>认证方式</dt><dd>Session Cookie</dd></div>
          </dl>
        </div>
      </section>

      <div class="settings-stack">
        <section class="settings-card panel">
          <h3>基本信息</h3><p>用户名用于登录和页面展示。</p>
          <el-form label-position="top">
            <el-form-item label="用户名"><el-input v-model="username" maxlength="50" show-word-limit /></el-form-item>
            <el-button type="primary" :loading="saving" @click="updateUsername">保存修改</el-button>
          </el-form>
        </section>
        <section class="settings-card danger-zone panel">
          <h3>危险操作</h3><p>删除账户后将立即退出，且不能使用原账户登录。</p>
          <el-button type="danger" plain @click="deleteAccount">删除当前账户</el-button>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-grid { display: grid; grid-template-columns: minmax(270px, .72fr) minmax(420px, 1.28fr); gap: 20px; }
.profile-card { overflow: hidden; }
.profile-banner { height: 96px; background: radial-gradient(circle at 20% 0, rgba(73,138,255,.8), transparent 42%), linear-gradient(135deg, #18385f, #102542); }
.profile-content { padding: 0 28px 30px; }
.large-avatar { width: 82px; height: 82px; display: grid; place-items: center; margin-top: -42px; border: 5px solid white; border-radius: 25px; background: linear-gradient(135deg, #3974f5, #26bdcf); color: white; font-size: 30px; font-weight: 800; box-shadow: 0 10px 24px rgba(45,106,224,.24); }
.profile-content h2 { margin: 18px 0 4px; color: #182944; }
.profile-content > p { margin: 0; color: #8b98aa; font-size: 13px; }
dl { margin: 28px 0 0; }
dl div { display: flex; justify-content: space-between; gap: 18px; padding: 15px 0; border-top: 1px solid #edf1f6; font-size: 12px; }
dt { color: #8a97aa; } dd { margin: 0; color: #2d3e58; font-weight: 600; text-align: right; }
.settings-stack { display: flex; flex-direction: column; gap: 20px; }
.settings-card { padding: 26px; }
.settings-card h3 { margin: 0; color: #1b2c47; font-size: 17px; }
.settings-card > p { margin: 7px 0 23px; color: #8a97aa; font-size: 12px; }
.danger-zone { border-color: #f2dfe2; }
.danger-zone h3 { color: #d74f60; }
@media (max-width: 860px) { .profile-grid { grid-template-columns: 1fr; } }
</style>
