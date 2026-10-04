<script setup>
import { onMounted, reactive, ref } from "vue";
import { Plus, Search } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import api, { errorMessage } from "../api";

const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const editingId = ref(null);
const keyword = ref("");
const rows = ref([]);
const formRef = ref(null);
const pagination = reactive({ page: 1, page_size: 10, total: 0 });
const form = reactive({ course_code: "", name: "", credits: 3, teacher: "" });
const rules = {
  course_code: [{ required: true, message: "请输入课程编号", trigger: "blur" }],
  name: [{ required: true, message: "请输入课程名称", trigger: "blur" }],
  teacher: [{ required: true, message: "请输入授课教师", trigger: "blur" }],
};

async function loadRows() {
  loading.value = true;
  try {
    const { data } = await api.get("/api/courses", {
      params: { keyword: keyword.value, page: pagination.page, page_size: pagination.page_size },
    });
    rows.value = data.items;
    Object.assign(pagination, data.pagination);
  } catch (error) {
    ElMessage.error(errorMessage(error, "课程数据加载失败"));
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  editingId.value = null;
  Object.assign(form, { course_code: "", name: "", credits: 3, teacher: "" });
  dialogVisible.value = true;
}

function openEdit(row) {
  editingId.value = row.id;
  Object.assign(form, row);
  dialogVisible.value = true;
}

async function save() {
  const valid = await formRef.value.validate().catch(() => false);
  if (!valid) return;
  saving.value = true;
  try {
    if (editingId.value) {
      await api.patch(`/api/courses/${editingId.value}`, form);
      ElMessage.success("课程信息已更新");
    } else {
      await api.post("/api/courses", form);
      ElMessage.success("课程创建成功");
    }
    dialogVisible.value = false;
    loadRows();
  } catch (error) {
    ElMessage.error(errorMessage(error));
  } finally {
    saving.value = false;
  }
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(
      `确定删除课程“${row.name}”吗？关联成绩也会一并删除。`,
      "删除确认",
      { type: "warning", confirmButtonText: "确认删除", cancelButtonText: "取消" },
    );
    await api.delete(`/api/courses/${row.id}`);
    ElMessage.success("课程已删除");
    loadRows();
  } catch (error) {
    if (error !== "cancel") ElMessage.error(errorMessage(error));
  }
}

function search() {
  pagination.page = 1;
  loadRows();
}

onMounted(loadRows);
</script>

<template>
  <div class="page-shell">
    <div class="page-heading">
      <div><h1>课程管理</h1><p>维护课程编号、学分和授课教师等基础信息。</p></div>
      <el-button type="primary" :icon="Plus" @click="openCreate">新增课程</el-button>
    </div>

    <section class="panel">
      <div class="toolbar">
        <el-input v-model="keyword" class="search-input" clearable :prefix-icon="Search" placeholder="搜索课程编号、名称或教师" @keyup.enter="search" @clear="search" />
        <el-button type="primary" plain @click="search">查询</el-button>
        <span class="record-count">共 {{ pagination.total }} 门课程</span>
      </div>
      <div class="table-wrap">
        <el-table v-loading="loading" :data="rows" stripe>
          <el-table-column prop="course_code" label="课程编号" min-width="140" />
          <el-table-column prop="name" label="课程名称" min-width="190" />
          <el-table-column prop="credits" label="学分" width="90"><template #default="scope"><el-tag effect="plain">{{ scope.row.credits }}</el-tag></template></el-table-column>
          <el-table-column prop="teacher" label="授课教师" min-width="130" />
          <el-table-column label="创建时间" min-width="170"><template #default="scope">{{ new Date(scope.row.created_at).toLocaleString() }}</template></el-table-column>
          <el-table-column label="操作" width="150" fixed="right"><template #default="scope"><el-button link type="primary" @click="openEdit(scope.row)">编辑</el-button><el-button link type="danger" @click="remove(scope.row)">删除</el-button></template></el-table-column>
          <template #empty><el-empty description="暂无课程数据" /></template>
        </el-table>
        <div class="pagination-row"><el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.page_size" background layout="total, sizes, prev, pager, next" :page-sizes="[10, 20, 50]" :total="pagination.total" @change="loadRows" /></div>
      </div>
    </section>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑课程' : '新增课程'" width="min(520px, 92vw)" destroy-on-close>
      <el-form ref="formRef" class="dialog-form" :model="form" :rules="rules" label-position="top">
        <div class="form-grid">
          <el-form-item label="课程编号" prop="course_code"><el-input v-model="form.course_code" maxlength="30" placeholder="例如：CS101" /></el-form-item>
          <el-form-item label="学分"><el-input-number v-model="form.credits" :min="0.5" :max="20" :step="0.5" :precision="1" controls-position="right" /></el-form-item>
        </div>
        <el-form-item label="课程名称" prop="name"><el-input v-model="form.name" maxlength="100" /></el-form-item>
        <el-form-item label="授课教师" prop="teacher"><el-input v-model="form.teacher" maxlength="50" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" :loading="saving" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<style scoped>
.record-count { margin-left: auto; color: #8a97aa; font-size: 12px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 18px; }
@media (max-width: 600px) { .record-count { margin-left: 0; } .form-grid { grid-template-columns: 1fr; } }
</style>
