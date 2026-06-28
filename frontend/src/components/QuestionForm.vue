<template>
  <div class="form-overlay" @click.self="$emit('close')">
    <div class="form-card">
      <h3>{{ isEdit ? "编辑题目" : "添加题目" }}</h3>

      <label>题目</label>
      <input v-model="form.title" placeholder="请输入面试题目" :class="{ 'input-error': errors.title }" @input="errors.title = ''" />
      <span class="err-msg" v-if="errors.title">{{ errors.title }}</span>

      <label>领域</label>
      <select v-model="form.domain" @change="onDomainChange" :class="{ 'input-error': errors.domain }">
        <option value="">--- 选择领域 ---</option>
        <option v-for="d in domains" :key="d" :value="d">{{ d }}</option>
        <option value="__custom__">+ 自定义领域...</option>
      </select>
      <input
        v-if="form.domain === '__custom__'"
        v-model="customDomain"
        placeholder="输入新领域名称"
        style="margin-top: 4px;"
        @input="onCustomDomainChange"
      />
      <span class="err-msg" v-if="errors.domain">{{ errors.domain }}</span>

      <label>分类</label>
      <select
        v-model="selectedCategory"
        @change="onCategoryChange; errors.category = ''"
        :class="{ 'input-error': errors.category }"
        :disabled="!form.domain || form.domain === '__custom__'"
      >
        <option value="">{{ catPlaceholder }}</option>
        <option v-for="c in subCats" :key="c" :value="c">{{ c }}</option>
        <option value="__custom__">+ 新建分类...</option>
      </select>
      <div v-if="selectedCategory === '__custom__'" class="custom-cat">
        <span class="cat-prefix">{{ effectiveDomain }}-{{ nextCode }} </span>
        <input
          v-model="customCatDesc"
          placeholder="输入分类描述，如：安全防护"
          @input="onCustomCatDesc"
        />
        <div class="cat-preview" v-if="customCatDesc.trim()">
          预览：<b>{{ effectiveDomain }}-{{ nextCode }} {{ customCatDesc.trim() }}</b>
        </div>
      </div>
      <span class="err-msg" v-if="errors.category">{{ errors.category }}</span>

      <label>难度</label>
      <select v-model="form.level">
        <option value="必会">必会</option>
        <option value="重点">重点</option>
        <option value="了解">了解</option>
      </select>

      <label>答案</label>
      <textarea v-model="form.answer" rows="8" placeholder="请输入参考答案..." :class="{ 'input-error': errors.answer }" @input="errors.answer = ''"></textarea>
      <span class="err-msg" v-if="errors.answer">{{ errors.answer }}</span>

      <div class="form-actions">
        <button class="btn-primary" @click="save">保存</button>
        <button class="btn-cancel" @click="$emit('close')">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { createQuestion, updateQuestion, fetchFilters } from "../api.js";

const props = defineProps({ question: Object });
const emit = defineEmits(["close", "saved"]);

const categories = ref({});
const domains = ref([]);
const isEdit = !!props.question;
const form = reactive({
  title: props.question?.title || "",
  answer: props.question?.answer || "",
  domain: props.question?.domain || "",
  category: props.question?.category || "",
  level: props.question?.level || "重点",
});
const selectedCategory = ref("");
const customDomain = ref("");
const customCatDesc = ref("");
const errors = reactive({ title: "", answer: "", category: "", domain: "" });

const catPlaceholder = computed(() => {
  if (!form.domain || form.domain === '__custom__') return "--- 请先选择领域 ---";
  return "--- 选择已有分类 ---";
});

const effectiveDomain = computed(() => {
  if (form.domain === '__custom__') return customDomain.value;
  return form.domain;
});

const subCats = computed(() => {
  const d = form.domain;
  if (!d || d === '__custom__') return [];
  return categories.value?.[d] || [];
});

const nextCode = computed(() => {
  const d = form.domain;
  if (!d || d === '__custom__') return 'C1';
  const existing = categories.value?.[d] || [];
  let maxNum = 0;
  for (const cat of existing) {
    const m = cat.match(/-C(\d+)/);
    if (m) maxNum = Math.max(maxNum, parseInt(m[1]));
  }
  return 'C' + (maxNum + 1);
});

function onDomainChange() {
  selectedCategory.value = '';
  customCatDesc.value = '';
  form.category = '';
  if (form.domain !== '__custom__') {
    customDomain.value = '';
  }
}

function onCustomDomainChange() {
  form.category = '';
  selectedCategory.value = '';
  customCatDesc.value = '';
}

function onCategoryChange() {
  customCatDesc.value = '';
  if (selectedCategory.value === "__custom__") {
    form.category = '';
  } else if (selectedCategory.value) {
    form.category = selectedCategory.value;
  }
}

function onCustomCatDesc() {
  if (customCatDesc.value.trim()) {
    form.category = `${effectiveDomain.value}-${nextCode.value} ${customCatDesc.value.trim()}`;
  } else {
    form.category = '';
  }
}

function validate() {
  errors.title = errors.answer = errors.category = errors.domain = '';
  let ok = true;
  if (!form.title.trim()) { errors.title = "请输入题目"; ok = false; }
  if (!form.domain.trim() || form.domain === '__custom__' && !customDomain.value.trim()) {
    errors.domain = "请选择或输入领域";
    ok = false;
  }
  if (!form.category.trim()) { errors.category = "请选择或输入分类"; ok = false; }
  if (!form.answer.trim()) { errors.answer = "请输入答案"; ok = false; }
  return ok;
}

onMounted(async () => {
  const data = await fetchFilters();
  domains.value = data.domains || [];
  categories.value = data.categories || {};
  if (form.category && data.categories) {
    for (const [dom, cats] of Object.entries(data.categories)) {
      if (cats.includes(form.category)) {
        if (!form.domain) form.domain = dom;
        selectedCategory.value = form.category;
        return;
      }
    }
    selectedCategory.value = "__custom__";
  } else if (form.category) {
    selectedCategory.value = "__custom__";
  }
});

async function save() {
  if (!validate()) return;
  if (isEdit) {
    await updateQuestion(props.question.id, form);
  } else {
    await createQuestion(form);
  }
  emit("saved");
}
</script>
