<template>
  <div class="study-mode">
    <!-- 筛选 -->
    <div class="toolbar">
      <select v-model="filterCategory" @change="onFilterChange">
        <option value="">全部分类</option>
        <option v-for="c in filters.categories" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="filterLevel" @change="onFilterChange">
        <option value="">全部难度</option>
        <option v-for="l in filters.levels" :key="l" :value="l">{{ l }}</option>
      </select>
      <select v-model="filterStatus" @change="onFilterChange">
        <option value="">全部状态</option>
        <option v-for="s in filters.statuses" :key="s" :value="s">{{ s }}</option>
      </select>
      <select v-model="limit" @change="startStudy">
        <option :value="5">5 题</option>
        <option :value="10">10 题</option>
        <option :value="20">20 题</option>
        <option :value="50">50 题</option>
      </select>
      <button class="btn-primary" @click="startStudy">重新抽题</button>
      <button class="btn-sm" :class="{ active: weakMode }" @click="toggleWeak">{{ weakMode ? '✓ 错题模式' : '只复习错题' }}</button>
      <label class="fav-filter"><input type="checkbox" v-model="favOnly" @change="startStudy" /> 仅收藏</label>
    </div>

    <!-- 每日目标 -->
    <div class="daily-goal" v-if="dailyTarget > 0">
      <div class="goal-text">
        今日目标 {{ dailyCount }} / {{ dailyTarget }}
        <span class="goal-set" @click="setDailyTarget" title="修改每日目标">⚙</span>
      </div>
      <div class="goal-bar"><div class="goal-fill" :style="{ width: goalPercent + '%' }"></div></div>
    </div>

    <!-- 进度 -->
    <span class="progress" v-if="questions.length">
      {{ currentIndex + 1 }} / {{ questions.length }}
    </span>

    <!-- 卡片 -->
    <div v-if="questions.length === 0" class="empty">点击"重新抽题"开始背诵</div>
    <div v-else class="study-card">
      <div class="card-meta">
        <span class="tag category" :title="currentQ.category">{{ currentQ.category }}</span>
        <span class="tag" :class="'level-' + currentQ.level">{{ currentQ.level }}</span>
      </div>
      <h3>{{ currentQ.title }}</h3>
      <div class="answer-section" v-show="showAnswer">
        <pre>{{ currentQ.answer }}</pre>
      </div>
      <div class="study-actions">
        <button class="btn-primary" v-if="!showAnswer" @click="showAnswer = true">
          查看答案
        </button>
        <template v-else>
          <button class="btn-master" @click="mark('已掌握')">✓ 掌握</button>
          <button class="btn-review" @click="mark('需复习')">↻ 需复习</button>
          <button class="btn-unmaster" @click="mark('未掌握')">✗ 未掌握</button>
        </template>
      </div>
      <div class="nav-btns">
        <button class="btn-nav" :disabled="currentIndex <= 0" @click="prev">← 上一题</button>
        <button class="btn-nav" :disabled="currentIndex >= questions.length - 1" @click="next">下一题 →</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { fetchStudy, fetchFilters, updateQuestion } from "../api.js";

const filters = ref({ categories: [], levels: [], statuses: ["未掌握", "需复习", "已掌握"] });
const filterCategory = ref("");
const filterLevel = ref("");
const filterStatus = ref("");
const weakMode = ref(false);
const favOnly = ref(false);
const limit = ref(10);
const questions = ref([]);
const currentIndex = ref(0);
const showAnswer = ref(false);

const currentQ = computed(() => questions.value[currentIndex.value] || {});

// 每日目标
const STORAGE_KEY = "daily_study_goal";
const dailyTarget = ref(Number(localStorage.getItem(STORAGE_KEY) || 30));
const dailyCount = ref(Number(localStorage.getItem("daily_study_count") || 0));
const today = new Date().toDateString();
const lastDate = localStorage.getItem("daily_study_date");

// 跨天清零
if (lastDate !== today) {
  dailyCount.value = 0;
  localStorage.setItem("daily_study_count", "0");
  localStorage.setItem("daily_study_date", today);
}

const goalPercent = computed(() => Math.min(100, Math.round((dailyCount.value / dailyTarget.value) * 100)));

function toggleWeak() {
  weakMode.value = !weakMode.value;
  if (weakMode.value) {
    filterStatus.value = "需复习,未掌握";
  } else {
    filterStatus.value = "";
  }
  startStudy();
}

function onFilterChange() {
  // 手动改筛选条件时，取消错题模式
  weakMode.value = false;
  startStudy();
}

function setDailyTarget() {
  const val = prompt("设置每日背诵目标（题数）:", String(dailyTarget.value));
  if (val && Number(val) > 0) {
    dailyTarget.value = Number(val);
    localStorage.setItem(STORAGE_KEY, String(dailyTarget.value));
  }
}

async function startStudy() {
  const params = {
    category: filterCategory.value,
    level: filterLevel.value,
    status: filterStatus.value,
    limit: limit.value,
  };
  if (favOnly.value) params.favorite = true;
  questions.value = await fetchStudy(params);
  currentIndex.value = 0;
  showAnswer.value = false;
}

function prev() {
  if (currentIndex.value > 0) {
    currentIndex.value--;
    showAnswer.value = false;
  }
}

function next() {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++;
    showAnswer.value = false;
  }
}

async function mark(status) {
  await updateQuestion(currentQ.value.id, { status });
  questions.value[currentIndex.value].status = status;
  // 每日计数 +1
  dailyCount.value++;
  localStorage.setItem("daily_study_count", String(dailyCount.value));
  localStorage.setItem("daily_study_date", today);
  // 自动跳下一题
  if (currentIndex.value < questions.value.length - 1) {
    next();
  }
}

onMounted(async () => {
  filters.value = await fetchFilters();
});
</script>
