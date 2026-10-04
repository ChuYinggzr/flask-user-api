<script setup>
import { onMounted, reactive, ref } from "vue";
import { Plus, Search } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import api, { errorMessage } from "../api";

const loading = ref(false);
const dialogVisible = ref(false);
const saving = ref(false);
const editingId = ref(null);
const keyword = ref("");
const rows = ref([]);
const pagination = reactive({ page: 1, page_size: 10, total: 0 });
const form = reactive({
  student_no: "",
  name: "",
  gender: "男",
  major: "计算机科学与技术",
  class_name: "",
  enrollment_year: new Date().getFullYear(),
});

const rules = {
  student_no: [{ required: true, message: "请输入学号", trigger: "blur" }],
  name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
  major: [{ required: true, message: "请输入专业", trigger: "blur" }],
  class_name: [{ required: true, message: "请输入班级", trigger: "blur" }],
};
const formRef = ref(null);

async function loadRows() {
  loading.value = true;
  try {
    const { data } = await api.get("/api/students", {
      params: { keyword: keyword.value, page: pagination.page, page_size: pagination.page_size },
    });
    rows.value = data.items;
    Object.assign(pagination, data.pagination);
  } catch (error) {
    ElMessage.error(errorMessage(error, "学生数据加载失败"));
  } finally {
    loading.value = false;
  }
}

function resetForm() {
  Object.assign(form, {
    student_no: "",
    name: "",
    gender: "男",
    major: "计算机科学与技术",
    class_name: "",
    enrollment_year: new Date().getFullYear(),
  });
}

function openCreate() {
  editingId.value = null;
  resetForm();
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
      await api.patch(`/api/students/${editingId.value}`, form);
      ElMessage.success("学生信息已更新");
    } else {
      await api.post("/api/students", form);
      ElMessage.success("学生创建成功");
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
      `确定删除学生“${row.name}”吗？关联成绩也会一并删除。`,
      "删除确认",
      { type: "warning", confirmButtonText: "确认删除", cancelButtonText: "取消" },
    );
    await api.delete(`/api/students/${row.id}`);
    ElMessage.success("学生已删除");
    if (rows.value.length === 1 && pagination.page > 1) pagination.page -= 1;
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
      <div><h1>学生管理</h1><p>维护学生基本档案，并快速查询专业和班级信息。</p></div>
      <el-button type="primary" :icon="Plus" @click="openCreate">新增学生</el-button>
    </div>

    <section class="panel">
      <div class="toolbar">
        <el-input
          v-model="keyword"
          class="search-input"
          clearable
          :prefix-icon="Search"
          placeholder="搜索学号、姓名、专业或班级"
          @keyup.enter="search"
          @clear="search"
        />
        <el-button type="primary" plain @click="search">查询</el-button>
        <span class="record-count">共 {{ pagination.total }} 名学生</span>
      </div>
      <div class="table-wrap">
        <el-table v-loading="loading" :data="rows" stripe>
          <el-table-column prop="student_no" label="学号" min-width="125" />
          <el-table-column prop="name" label="姓名" min-width="100" />
          <el-table-column prop="gender" label="性别" width="76" />
          <el-table-column prop="major" label="专业" min-width="170" show-overflow-tooltip />
          <el-table-column prop="class_name" label="班级" min-width="125" />
          <el-table-column prop="enrollment_year" label="入学年份" width="100" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button link type="primary" @click="openEdit(scope.row)">编辑</el-button>
              <el-button link type="danger" @click="remove(scope.row)">删除</el-button>
            </template>
          </el-table-column>
          <template #empty><el-empty description="暂无学生数据" /></template>
        </el-table>
        <div class="pagination-row">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.page_size"
            background
            layout="total, sizes, prev, pager, next"
            :page-sizes="[10, 20, 50]"
            :total="pagination.total"
            @change="loadRows"
          />
        </div>
      </div>
    </section>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑学生' : '新增学生'" width="min(560px, 92vw)" destroy-on-close>
      <el-form ref="formRef" class="dialog-form" :model="form" :rules="rules" label-position="top">
        <div class="form-grid">
          <el-form-item label="学号" prop="student_no"><el-input v-model="form.student_no" maxlength="30" /></el-form-item>
          <el-form-item label="姓名" prop="name"><el-input v-model="form.name" maxlength="50" /></el-form-item>
          <el-form-item label="性别"><el-select v-model="form.gender"><el-option label="男" value="男" /><el-option label="女" value="女" /><el-option label="其他" value="其他" /></el-select></el-form-item>
          <el-form-item label="入学年份"><el-input-number v-model="form.enrollment_year" :min="2000" :max="2100" controls-position="right" /></el-form-item>
        </div>
        <el-form-item label="专业" prop="major"><el-input v-model="form.major" maxlength="100" /></el-form-item>
        <el-form-item label="班级" prop="class_name"><el-input v-model="form.class_name" maxlength="50" placeholder="例如：计科2301班" /></el-form-item>
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
