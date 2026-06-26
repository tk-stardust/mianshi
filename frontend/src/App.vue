<template>
  <div class="app">
    <header>
      <h1>面试题管理</h1>
      <nav>
        <button :class="{ active: tab === 'list' }" @click="tab = 'list'">题库</button>
        <button :class="{ active: tab === 'study' }" @click="tab = 'study'">背诵模式</button>
        <button :class="{ active: tab === 'stats' }" @click="tab = 'stats'; loadStats()">统计</button>
        <button :class="{ active: tab === 'knowledge' }" @click="tab = 'knowledge'">知识巩固</button>
      </nav>
    </header>

    <!-- 知识巩固固定侧边栏 -->
    <KnowledgeNav
      v-if="tab === 'knowledge' && knowledgeMode === 'docs'"
      @select-doc="scrollDoc = { key: $event, ts: Date.now() }"
      :activeDoc="scrollDoc.key"
    />

    <main>
      <QuestionList
        v-if="tab === 'list'"
        @add="openForm()"
        @edit="openForm"
        ref="listRef"
      />
      <StudyMode v-if="tab === 'study'" />
      <KnowledgeView v-if="tab === 'knowledge'" :scrollDoc="scrollDoc" @update:mode="knowledgeMode = $event" />
      <div v-if="tab === 'stats'" class="stats">
        <div class="stat-cards">
          <div class="stat-card"><strong>总题数</strong><span>{{ stats.total }}</span></div>
          <div class="stat-card master"><strong>已掌握</strong><span>{{ stats.mastered }}</span></div>
          <div class="stat-card review"><strong>需复习</strong><span>{{ stats.need_review }}</span></div>
          <div class="stat-card unmaster"><strong>未掌握</strong><span>{{ stats.unmastered }}</span></div>
        </div>
        <h3>分类掌握进度</h3>
        <div class="category-progress" v-if="stats.by_category?.length">
          <div class="cat-row" v-for="c in stats.by_category" :key="c.category">
            <div class="cat-header">
              <span class="cat-name">{{ c.category }}</span>
              <span class="cat-num">{{ c.mastered }}/{{ c.total }}</span>
            </div>
            <div class="cat-bar">
              <div class="cat-fill" :style="{ width: (c.total > 0 ? Math.round(c.mastered / c.total * 100) : 0) + '%' }"></div>
            </div>
          </div>
        </div>
        <div v-else class="empty">暂无数据</div>
      </div>
    </main>

    <QuestionForm
      v-if="showForm"
      :question="editingQ"
      @close="showForm = false"
      @saved="onSaved"
    />

  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { ElMessage } from "element-plus";
import QuestionList from "./components/QuestionList.vue";
import StudyMode from "./components/StudyMode.vue";
import QuestionForm from "./components/QuestionForm.vue";
import KnowledgeView from "./components/KnowledgeView.vue";
import KnowledgeNav from "./components/KnowledgeNav.vue";
import { fetchStats } from "./api.js";

const tab = ref("list");
const scrollDoc = ref({ key: "", ts: 0 });
const knowledgeMode = ref("concepts");
const showForm = ref(false);
const editingQ = ref(null);
const listRef = ref(null);
const stats = reactive({ total: 0, mastered: 0, need_review: 0, unmastered: 0, by_category: [] });

function openForm(q) {
  editingQ.value = q || null;
  showForm.value = true;
}

function onSaved() {
  const isEdit = !!editingQ.value;
  showForm.value = false;
  editingQ.value = null;
  ElMessage.success(isEdit ? "已更新" : "添加成功");
  if (listRef.value) {
    listRef.value.loadFilters();
    listRef.value.loadQuestions();
  }
}

async function loadStats() {
  Object.assign(stats, await fetchStats());
}
</script>
