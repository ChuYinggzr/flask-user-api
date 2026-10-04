<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import * as echarts from "echarts";
import { Collection, DataLine, Reading, User } from "@element-plus/icons-vue";
import api, { errorMessage } from "../api";
import { ElMessage } from "element-plus";

const loading = ref(true);
const data = ref({
  student_count: 0,
  course_count: 0,
  score_count: 0,
  average_score: 0,
  score_distribution: { excellent: 0, good: 0, pass: 0, fail: 0 },
  course_averages: [],
});
const distributionEl = ref(null);
const courseEl = ref(null);
let distributionChart;
let courseChart;
let chartResizeObserver;

const cards = [
  { key: "student_count", label: "学生总数", unit: "人", icon: User, tone: "blue" },
  { key: "course_count", label: "课程总数", unit: "门", icon: Reading, tone: "cyan" },
  { key: "score_count", label: "成绩记录", unit: "条", icon: Collection, tone: "purple" },
  { key: "average_score", label: "平均成绩", unit: "分", icon: DataLine, tone: "orange" },
];

function renderCharts() {
  distributionChart?.dispose();
  courseChart?.dispose();
  distributionChart = echarts.init(distributionEl.value);
  courseChart = echarts.init(courseEl.value);
  chartResizeObserver?.disconnect();
  chartResizeObserver?.observe(distributionEl.value);
  chartResizeObserver?.observe(courseEl.value);

  const d = data.value.score_distribution;
  distributionChart.setOption({
    tooltip: { trigger: "item" },
    legend: { bottom: 0, icon: "circle", textStyle: { color: "#6f7f96" } },
    series: [{
      type: "pie",
      radius: ["52%", "74%"],
      center: ["50%", "43%"],
      itemStyle: { borderColor: "#fff", borderWidth: 4, borderRadius: 7 },
      label: { show: false },
      data: [
        { value: d.excellent, name: "优秀 90+", itemStyle: { color: "#3d77f4" } },
        { value: d.good, name: "良好 80-89", itemStyle: { color: "#25bdd0" } },
        { value: d.pass, name: "及格 60-79", itemStyle: { color: "#f3aa44" } },
        { value: d.fail, name: "不及格", itemStyle: { color: "#ef6675" } },
      ],
    }],
    graphic: [{
      type: "text", left: "center", top: "37%",
      style: { text: String(data.value.score_count), fontSize: 28, fontWeight: 700, fill: "#1c2d48" },
    }, {
      type: "text", left: "center", top: "49%",
      style: { text: "成绩记录", fontSize: 11, fill: "#8b98ab" },
    }],
  });

  const courses = data.value.course_averages;
  courseChart.setOption({
    grid: { left: 42, right: 20, top: 20, bottom: 52 },
    tooltip: { trigger: "axis" },
    xAxis: {
      type: "category",
      data: courses.map((item) => item.course_name),
      axisLine: { lineStyle: { color: "#dfe6f0" } },
      axisLabel: { color: "#77869b", interval: 0, rotate: courses.length > 5 ? 24 : 0 },
      axisTick: { show: false },
    },
    yAxis: {
      type: "value", min: 0, max: 100,
      splitLine: { lineStyle: { color: "#edf1f6", type: "dashed" } },
      axisLabel: { color: "#8c98aa" },
    },
    series: [{
      type: "bar",
      data: courses.map((item) => item.average_score),
      barMaxWidth: 34,
      itemStyle: {
        borderRadius: [8, 8, 0, 0],
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: "#3b76f6" },
          { offset: 1, color: "#69cddd" },
        ]),
      },
    }],
  });
}

function resizeCharts() {
  distributionChart?.resize();
  courseChart?.resize();
}

async function loadData() {
  loading.value = true;
  try {
    const response = await api.get("/api/dashboard");
    data.value = response.data;
    await nextTick();
    renderCharts();
  } catch (error) {
    ElMessage.error(errorMessage(error, "概览数据加载失败"));
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
  window.addEventListener("resize", resizeCharts);
  chartResizeObserver = new ResizeObserver(resizeCharts);
});
onBeforeUnmount(() => {
  window.removeEventListener("resize", resizeCharts);
  chartResizeObserver?.disconnect();
  distributionChart?.dispose();
  courseChart?.dispose();
});
</script>

<template>
  <div class="page-shell" v-loading="loading">
    <div class="page-heading">
      <div>
        <h1>数据概览</h1>
        <p>查看学生、课程与成绩数据的整体运行情况。</p>
      </div>
      <el-button type="primary" plain @click="loadData">刷新数据</el-button>
    </div>

    <section class="metric-grid">
      <article v-for="card in cards" :key="card.key" class="metric-card panel">
        <div :class="['metric-icon', card.tone]"><el-icon><component :is="card.icon" /></el-icon></div>
        <div>
          <p>{{ card.label }}</p>
          <strong>{{ data[card.key] }}<small>{{ card.unit }}</small></strong>
        </div>
      </article>
    </section>

    <section class="chart-grid">
      <article class="chart-card panel">
        <div class="card-heading"><div><h3>成绩分布</h3><p>各分数区间的记录数量</p></div></div>
        <div ref="distributionEl" class="chart"></div>
      </article>
      <article class="chart-card panel wide">
        <div class="card-heading"><div><h3>课程平均成绩</h3><p>最多展示平均分最高的8门课程</p></div></div>
        <div v-if="data.course_averages.length" ref="courseEl" class="chart"></div>
        <el-empty v-else description="录入成绩后将显示课程分析" />
      </article>
    </section>
  </div>
</template>

<style scoped>
.metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }
.metric-card { display: flex; align-items: center; gap: 17px; min-height: 124px; padding: 23px; }
.metric-icon { width: 54px; height: 54px; display: grid; place-items: center; border-radius: 16px; font-size: 25px; }
.metric-icon.blue { color: #326cf1; background: #eaf0ff; }
.metric-icon.cyan { color: #18a7bb; background: #e4f8fa; }
.metric-icon.purple { color: #8a63e7; background: #f1ebff; }
.metric-icon.orange { color: #e9942e; background: #fff2df; }
.metric-card p { margin: 0 0 7px; color: #8491a4; font-size: 12px; }
.metric-card strong { color: #172842; font-size: 30px; line-height: 1; }
.metric-card small { margin-left: 5px; color: #9aa6b7; font-size: 11px; font-weight: 500; }
.chart-grid { display: grid; grid-template-columns: minmax(300px, .8fr) minmax(480px, 1.4fr); gap: 18px; margin-top: 18px; }
.chart-card { min-height: 390px; padding: 22px 22px 14px; }
.card-heading h3 { margin: 0; color: #1d2d47; font-size: 17px; }
.card-heading p { margin: 5px 0 0; color: #98a3b4; font-size: 11px; }
.chart { width: 100%; height: 305px; margin-top: 8px; }
@media (max-width: 1180px) { .metric-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 860px) { .chart-grid { grid-template-columns: 1fr; } }
@media (max-width: 560px) { .metric-grid { grid-template-columns: 1fr; } .metric-card { min-height: 104px; } }
</style>
