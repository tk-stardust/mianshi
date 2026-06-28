<template>
  <div class="form-overlay" @click.self="$emit('close')">
    <div class="form-card">
      <h3>{{ isEdit ? "编辑题目" : "添加题目" }}</h3>
      <label>题目</label>
      <input v-model="form.title" placeholder="请输入面试题目" :class="{ 'input-error': errors.title }" @input="errors.title = ''" />
      <span class="err-msg" v-if="errors.title">{{ errors.title }}</span>
      <label>分类</label>
      <select v-model="selectedCategory" @change="onCategoryChange; errors.category = ''" :class="{ 'input-error': errors.category }">
        <option value="">--- 选择已有分类 ---</option>
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
        <option value="__custom__">+ 自定义分类...</option>
      </select>
      <input
        v-if="selectedCategory === '__custom__'"
        v-model="form.category"
        placeholder="输入新分类名称"
        style="margin-top: 4px;"
        :class="{ 'input-error': errors.category }"
        @input="errors.category = ''"
      />
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
import { reactive, ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { createQuestion, updateQuestion, fetchFilters } from "../api.js";

const props = defineProps({ question: Object });
const emit = defineEmits(["close", "saved"]);

const categories = ref([]);
const isEdit = !!props.question;
const form = reactive({
  title: props.question?.title || "",
  answer: props.question?.answer || "",
  category: props.question?.category || "",
  level: props.question?.level || "重点",
});
const selectedCategory = ref("");
const errors = reactive({ title: "", answer: "", category: "" });

function validate() {
  errors.title = "";
  errors.answer = "";
  errors.category = "";
  let ok = true;
  if (!form.title.trim()) {
    errors.title = "请输入题目";
    ok = false;
  }
  if (!form.category.trim()) {
    errors.category = "请选择或输入分类";
    ok = false;
  }
  if (!form.answer.trim()) {
    errors.answer = "请输入答案";
    ok = false;
  }
  return ok;
}

function onCategoryChange() {
  if (selectedCategory.value === "__custom__") {
    form.category = "";
  } else if (selectedCategory.value) {
    form.category = selectedCategory.value;
  }
}

onMounted(async () => {
  const data = await fetchFilters();
  categories.value = data.categories;
  if (form.category && data.categories.includes(form.category)) {
    selectedCategory.value = form.category;
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
