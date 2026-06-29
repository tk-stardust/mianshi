<template>
  <div class="question-list">
    <!-- 搜索 & 筛选 -->
    <div class="toolbar">
      <input v-model="keyword" placeholder="搜索题目/答案..." @input="search" />
      <select v-model="filterDomain" @change="onDomainChange">
        <option value="">全部领域</option>
        <option v-for="d in filters.domains" :key="d" :value="d">{{ d }}</option>
      </select>
      <select v-model="filterCategory" @change="search" class="cat-select">
        <option value="">全部分类</option>
        <option v-for="c in subCategories" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="filterLevel" @change="search">
        <option value="">全部难度</option>
        <option v-for="l in filters.levels" :key="l" :value="l">{{ l }}</option>
      </select>
      <select v-model="filterStatus" @change="search">
        <option value="">全部状态</option>
        <option v-for="s in filters.statuses" :key="s" :value="s">{{ s }}</option>
      </select>
      <label class="fav-filter"><input type="checkbox" v-model="filterFavorite" @change="search" /> 仅收藏</label>
      <button class="btn-primary" @click="$emit('add')">+ 添加题目</button>
      <button class="btn-sm" @click="handleExport" title="导出当前筛选结果为 JSON">导出</button>
      <button class="btn-sm" @click="triggerImport">导入</button>
      <input type="file" ref="importFile" accept=".json" style="display:none" @change="handleImport" />
    </div>

    <!-- 题目列表 -->
    <div v-if="loading && questions.length === 0" class="empty">加载中...</div>
    <div v-else-if="!loading && questions.length === 0" class="empty">暂无题目，点击"添加题目"开始</div>
    <div v-else class="question-card" v-for="q in questions" :key="q.id">
      <div class="card-header">
        <span class="card-title">{{ q.title }}</span>
        <span class="card-meta">
          <span class="fav-star" :class="{ active: q.favorite }" @click.stop="toggleFav(q)" :title="q.favorite ? '取消收藏' : '收藏'">{{ q.favorite ? '⭐' : '☆' }}</span>
          <span class="tag domain-tag" v-if="q.domain">{{ q.domain }}</span>
          <span class="tag category" :title="q.category">{{ q.category }}</span>
          <span class="tag" :class="'level-' + q.level">{{ q.level }}</span>
          <span class="tag" :class="'status-' + q.status">{{ q.status }}</span>
        </span>
      </div>
      <div class="card-body" v-show="expanded === q.id">
        <pre class="answer">{{ q.answer }}</pre>
      </div>
      <div class="card-actions">
        <button class="btn-sm" @click="toggleExpand(q.id)">{{ expanded === q.id ? '收起' : '展开答案' }}</button>
        <button class="btn-sm btn-master" @click="quickStatus(q, '已掌握')">✓ 掌握</button>
        <button class="btn-sm btn-review" @click="quickStatus(q, '需复习')">↻ 复习</button>
        <button class="btn-sm btn-unmaster" @click="quickStatus(q, '未掌握')">✗ 未掌握</button>
        <button class="btn-sm" @click="$emit('edit', q)">编辑</button>
        <button class="btn-sm btn-danger" @click="handleDelete(q.id)">删除</button>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-bar" v-if="total > 0">
      <div class="pagination-left">
        共 <b>{{ total }}</b> 条，第 <b>{{ page }}/{{ totalPages }}</b> 页
      </div>
      <div class="pagination-center">
        <button class="page-btn" :disabled="page === 1" @click="goPage(1)" title="首页">«</button>
        <button class="page-btn" :disabled="page === 1" @click="goPage(page - 1)" title="上一页">‹</button>
        <template v-for="p in pageNumbers" :key="p">
          <span v-if="p === '...'" class="page-ellipsis">...</span>
          <button v-else class="page-btn" :class="{ active: p === page }" @click="goPage(p)">{{ p }}</button>
        </template>
        <button class="page-btn" :disabled="page === totalPages" @click="goPage(page + 1)" title="下一页">›</button>
        <button class="page-btn" :disabled="page === totalPages" @click="goPage(totalPages)" title="尾页">»</button>
      </div>
      <div class="pagination-right">
        <span class="size-label">每页</span>
        <select v-model.number="pageSize" @change="onPageSizeChange" class="size-select">
          <option :value="10">10 条</option>
          <option :value="20">20 条</option>
          <option :value="50">50 条</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { ElMessageBox, ElMessage } from "element-plus";
import { fetchQuestions, fetchFilters, updateQuestion, deleteQuestion, toggleFavorite, fetchExport, fetchExportMd, importQuestions } from "../api.js";

const emit = defineEmits(["add", "edit"]);

const questions = ref([]);
const filters = ref({ categories: [], levels: [], statuses: ["未掌握", "需复习", "已掌握"] });
const keyword = ref("");
const filterDomain = ref("");
const filterCategory = ref("");
const filterLevel = ref("");
const filterStatus = ref("");
const filterFavorite = ref(false);
const importFile = ref(null);
const page = ref(1);
const total = ref(0);
const pageSize = ref(20);
const expanded = ref(null);
const loading = ref(false);

const totalPages = computed(() => Math.ceil(total.value / pageSize.value));

const pageNumbers = computed(() => {
  const pages = [];
  const tp = totalPages.value;
  const cp = page.value;
  if (tp <= 7) { for (let i = 1; i <= tp; i++) pages.push(i); return pages; }
  pages.push(1);
  if (cp > 3) pages.push('...');
  const start = Math.max(2, cp - 1);
  const end = Math.min(tp - 1, cp + 1);
  for (let i = start; i <= end; i++) pages.push(i);
  if (cp < tp - 2) pages.push('...');
  pages.push(tp);
  return pages;
});

const subCategories = computed(() => {
  if (!filterDomain.value) return [];
  return filters.value.categories?.[filterDomain.value] || [];
});

function shortCat(cat) {
  // 截断显示: "Agent-C1 最高频基础：Agent 定义、差异与架构设计" → "C1 最高频基础..."
  const parts = cat.split('：');
  if (parts.length >= 2) return parts[0].replace(/^.+?-/, '') + '：' + parts[1].slice(0, 10) + '...';
  const noPrefix = cat.replace(/^.+?-/, '');
  return noPrefix.length > 18 ? noPrefix.slice(0, 16) + '...' : noPrefix;
}

function onDomainChange() {
  filterCategory.value = "";
  search();
}

function goPage(p) {
  if (typeof p === 'string') return;
  if (p < 1 || p > totalPages.value) return;
  page.value = p;
  loadQuestions();
}

function onPageSizeChange() {
  page.value = 1;
  loadQuestions();
}

async function loadFilters() {
  filters.value = await fetchFilters();
}

async function loadQuestions() {
  loading.value = true;
  const params = {
    keyword: keyword.value,
    domain: filterDomain.value,
    category: filterCategory.value,
    level: filterLevel.value,
    status: filterStatus.value,
    page: page.value,
    page_size: pageSize.value,
  };
  if (filterFavorite.value) params.favorite = true;
  const data = await fetchQuestions(params);
  questions.value = data.items;
  total.value = data.total;
  loading.value = false;
}

function search() {
  page.value = 1;
  loadQuestions();
}

function toggleExpand(id) {
  expanded.value = expanded.value === id ? null : id;
}

const statusLabels = { "已掌握": "✓ 已标记为掌握", "需复习": "↻ 已标记为需复习", "未掌握": "✗ 已标记为未掌握" };

async function quickStatus(q, status) {
  await updateQuestion(q.id, { status });
  q.status = status;
  ElMessage.success(statusLabels[status] || "状态已更新");
  if (filterStatus.value) loadQuestions();
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm("确定删除这道题吗？", "删除确认", {
      confirmButtonText: "删除",
      cancelButtonText: "取消",
      type: "warning",
    });
    await deleteQuestion(id);
    ElMessage.success("已删除");
    loadQuestions();
  } catch {}
}

async function toggleFav(q) {
  q.favorite = !q.favorite;
  await toggleFavorite(q.id, q.favorite);
}

async function handleExport() {
  const params = {};
  if (keyword.value) params.keyword = keyword.value;
  if (filterDomain.value) params.domain = filterDomain.value;
  if (filterCategory.value) params.category = filterCategory.value;
  if (filterLevel.value) params.level = filterLevel.value;
  if (filterStatus.value) params.status = filterStatus.value;
  if (filterFavorite.value) params.favorite = true;

  const md = await fetchExportMd(params);
  const blob = new Blob([md], { type: "text/markdown; charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const label = filterCategory.value || "全部";
  a.download = `面试题库_${label}_${new Date().toISOString().slice(0, 10)}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function triggerImport() {
  importFile.value.click();
}

async function handleImport(e) {
  const file = e.target.files[0];
  if (!file) return;
  try {
    const text = await file.text();
    const data = JSON.parse(text);
    const result = await importQuestions(data);
    ElMessage.success(`导入完成：新增 ${result.added} 条，跳过 ${result.skipped} 条`);
    loadFilters();
    loadQuestions();
  } catch (err) {
    ElMessage.error("导入失败，请检查文件格式");
  }
  importFile.value.value = "";
}

onMounted(() => {
  loadFilters();
  loadQuestions();
});

defineExpose({ loadQuestions, loadFilters });
</script>
