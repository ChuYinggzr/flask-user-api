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
const semester = ref("");
const rows = ref([]);
const students = ref([]);
const courses = ref([]);
const formRef = ref(null);
const pagination = reactive({ page: 1, page_size: 10, total: 0 });
const form = reactive({ student_id: null, course_id: null, score: 80, semester: "2026-2027-1" });
const rules = {
  student_id: [{ required: true, message: "请选择学生", trigger: "change" }],
  course_id: [{ required: true, message: "请选择课程", trigger: "change" }],
  semester: [{ required: true, message: "请输入学期", trigger: "blur" }],
};

function scoreType(score) {
  if (score >= 90) return "success";
  if (score >= 80) return "primary";
  if (score >= 60) return "warning";
  return "danger";
}

async function loadOptions() {
  const [studentResponse, courseResponse] = await Promise.all([
    api.get("/api/students", { params: { page_size: 100 } }),
    api.get("/api/courses", { params: { page_size: 100 } }),
  ]);
  students.value = studentResponse.data.items;
  courses.value = courseResponse.data.items;
}

async function loadRows() {
  loading.value = true;
  try {
    const { data } = await api.get("/api/scores", {
      params: {
        keyword: keyword.value,
        semester: semester.value,
        page: pagination.page,
        page_size: pagination.page_size,
      },
    });
    rows.value = data.items;
    Object.assign(pagination, data.pagination);
  } catch (error) {
    ElMessage.error(errorMessage(error, "成绩数据加载失败"));
  } finally {
    loading.value = false;
  }
}

function openCreate() {
  editingId.value = null;
  Object.assign(form, { student_id: null, course_id: null, score: 80, semester: "2026-2027-1" });
  dialogVisible.value = true;
}

function openEdit(row) {
  editingId.value = row.id;
  Object.assign(form, {
    student_id: row.student_id,
    course_id: row.course_id,
    score: row.score,
    semester: row.semester,
  });
  dialogVisible.value = true;
}

async function save() {
  const valid = await formRef.value.validate().catch(() => false);
  if (!valid) return;
  saving.value = true;
  try {
    if (editingId.value) {
      await api.patch(`/api/scores/${editingId.value}`, form);
      ElMessage.success("成绩已更新");
    } else {
      await api.post("/api/scores", form);
      ElMessage.success("成绩录入成功");
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
      `确定删除“${row.student_name} - ${row.course_name}”的成绩记录吗？`,
      "删除确认",
      { type: "warning", confirmButtonText: "确认删除", cancelButtonText: "取消" },
    );
    await api.delete(`/api/scores/${row.id}`);
    ElMessage.success("成绩记录已删除");
    loadRows();
  } catch (error) {
    if (error !== "cancel") ElMessage.error(errorMessage(error));
  }
}

function search() {
  pagination.page = 1;
  loadRows();
}

onMounted(async () => {
  try {
    await Promise.all([loadOptions(), loadRows()]);
  } catch (error) {
    ElMessage.error(errorMessage(error, "基础数据加载失败"));
  }
});
</script>

<template>
  <div class="page-shell">
    <div class="page-heading">
      <div><h1>成绩管理</h1><p>录入、筛选和维护学生的课程成绩记录。</p></div>
      <el-button type="primary" :icon="Plus" :disabled="!students.length || !courses.length" @click="openCreate">录入成绩</el-button>
    </div>

    <el-alert v-if="!students.length || !courses.length" class="data-alert" type="info" show-icon :closable="false" title="请先创建学生和课程，再录入成绩。" />

    <section class="panel">
      <div class="toolbar">
        <el-input v-model="keyword" class="search-input" clearable :prefix-icon="Search" placeholder="搜索学生、学号、课程或编号" @keyup.enter="search" @clear="search" />
        <el-input v-model="semester" class="semester-input" clearable placeholder="筛选学期" @keyup.enter="search" @clear="search" />
        <el-button type="primary" plain @click="search">查询</el-button>
        <span class="record-count">共 {{ pagination.total }} 条记录</span>
      </div>
      <div class="table-wrap">
        <el-table v-loading="loading" :data="rows" stripe>
          <el-table-column prop="student_no" label="学号" min-width="120" />
          <el-table-column prop="student_name" label="学生" min-width="100" />
          <el-table-column prop="course_code" label="课程编号" min-width="120" />
          <el-table-column prop="course_name" label="课程" min-width="160" show-overflow-tooltip />
          <el-table-column prop="semester" label="学期" min-width="120" />
          <el-table-column label="成绩" width="100"><template #default="scope"><el-tag :type="scoreType(scope.row.score)" effect="light">{{ scope.row.score }}</el-tag></template></el-table-column>
          <el-table-column label="操作" width="150" fixed="right"><template #default="scope"><el-button link type="primary" @click="openEdit(scope.row)">编辑</el-button><el-button link type="danger" @click="remove(scope.row)">删除</el-button></template></el-table-column>
          <template #empty><el-empty description="暂无成绩数据" /></template>
        </el-table>
        <div class="pagination-row"><el-pagination v-model:current-page="pagination.page" v-model:page-size="pagination.page_size" background layout="total, sizes, prev, pager, next" :page-sizes="[10, 20, 50]" :total="pagination.total" @change="loadRows" /></div>
      </div>
    </section>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑成绩' : '录入成绩'" width="min(540px, 92vw)" destroy-on-close>
      <el-form ref="formRef" class="dialog-form" :model="form" :rules="rules" label-position="top">
        <el-form-item label="学生" prop="student_id"><el-select v-model="form.student_id" filterable placeholder="选择学生"><el-option v-for="student in students" :key="student.id" :label="`${student.student_no} · ${student.name}`" :value="student.id" /></el-select></el-form-item>
        <el-form-item label="课程" prop="course_id"><el-select v-model="form.course_id" filterable placeholder="选择课程"><el-option v-for="course in courses" :key="course.id" :label="`${course.course_code} · ${course.name}`" :value="course.id" /></el-select></el-form-item>
        <div class="form-grid">
          <el-form-item label="成绩"><el-input-number v-model="form.score" :min="0" :max="100" :precision="1" controls-position="right" /></el-form-item>
          <el-form-item label="学期" prop="semester"><el-input v-model="form.semester" maxlength="30" placeholder="例如：2026-2027-1" /></el-form-item>
        </div>
      </el-form>
      <template #footer><el-button @click="dialogVisible = false">取消</el-button><el-button type="primary" :loading="saving" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<style scoped>
.data-alert { margin-bottom: 18px; }
.semester-input { width: 190px; }
.record-count { margin-left: auto; color: #8a97aa; font-size: 12px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 18px; }
@media (max-width: 600px) { .semester-input { width: 100%; } .record-count { margin-left: 0; } .form-grid { grid-template-columns: 1fr; } }
</style>
