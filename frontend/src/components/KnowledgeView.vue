<template>
  <div class="knowledge-view kn-main">
    <!-- 分类筛选 -->
    <div class="toolbar">
      <select v-model="filterCat">
        <option value="">全部分类</option>
        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
      </select>
      <button :class="{ active: mode === 'concepts' }" @click="mode = 'concepts'">概念卡片 ({{ filteredConcepts.length }})</button>
      <select v-if="mode === 'concepts'" v-model="tierFilter" style="width:auto;margin-left:4px">
        <option value="all">全部 ({{ conceptsTotal }})</option>
        <option value="core">核心 ({{ coreCount }})</option>
        <option value="extended">扩展 ({{ extendedCount }})</option>
      </select>
      <button :class="{ active: mode === 'docs' }" @click="mode = 'docs'">按文档 ({{ docGroups.length }})</button>
      <button :class="{ active: mode === 'flowcharts' }" @click="mode = 'flowcharts'">流程图 ({{ filteredFlows.length }})</button>
      <button :class="{ active: mode === 'mindmaps' }" @click="mode = 'mindmaps'">思维导图 ({{ filteredMaps.length }})</button>
    </div>

    <!-- 概念卡片 — 直接展示 -->
    <div v-if="mode === 'concepts'" class="concept-grid">
      <div class="concept-card" v-for="c in filteredConcepts" :key="c.title">
        <div class="concept-header">
          <span class="concept-title">{{ c.title }}</span>
          <span class="concept-cat">{{ c.category }}</span>
        </div>
        <div class="concept-def">{{ c.definition }}</div>
        <div class="concept-detail" v-show="expanded === c.title">
          <div class="detail-row" v-if="c.definition"><b>定义</b>{{ c.definition }}</div>
          <div class="detail-row" v-if="c.mechanism"><b>原理机制</b>{{ c.mechanism }}</div>
          <div class="detail-row" v-if="c.useCase"><b>作用/场景</b>{{ c.useCase }}</div>
          <div class="detail-row" v-if="c.comparison"><b>对比区分</b>{{ c.comparison }}</div>
          <div class="detail-row" v-if="c.limitation"><b>局限/缺点</b>{{ c.limitation }}</div>
          <div class="detail-row interview" v-if="c.interview"><b>常见面试问法</b>{{ c.interview }}</div>
        </div>
        <button class="btn-sm" @click="toggle(c.title)">{{ expanded === c.title ? '收起' : '展开详情' }}</button>
      </div>
    </div>

    <!-- 按文档视图 -->
    <div v-if="mode === 'docs'" class="doc-list">
      <div class="doc-group" v-for="g in docGroups" :key="g.source" :id="'doc-' + g.source.replace(/\s+/g, '-')">
        <div class="doc-source">{{ g.label || g.source }}</div>
        <div class="doc-concepts">
          <div class="doc-card" v-for="c in g.concepts" :key="c.title">
            <div class="doc-card-title">{{ c.title }}</div>
            <div class="doc-card-def">{{ c.definition }}</div>
            <div class="doc-card-detail" v-show="expanded === c.title">
              <div class="detail-row" v-if="c.mechanism"><b>原理机制</b>{{ c.mechanism }}</div>
              <div class="detail-row" v-if="c.useCase"><b>作用/场景</b>{{ c.useCase }}</div>
              <div class="detail-row" v-if="c.comparison"><b>对比区分</b>{{ c.comparison }}</div>
              <div class="detail-row" v-if="c.limitation"><b>局限/缺点</b>{{ c.limitation }}</div>
              <div class="detail-row interview" v-if="c.interview"><b>常见面试问法</b>{{ c.interview }}</div>
            </div>
            <button class="btn-sm" @click="toggle(c.title)">{{ expanded === c.title ? '收起' : '展开详情' }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 流程图 / 思维导图 — 列表 + 模态框 -->
    <div v-if="mode === 'flowcharts'" class="item-list">
      <div class="item-card" v-for="f in filteredFlows" :key="f.title" @click="openModal('flow', f)">
        <div class="item-title">{{ f.title }}</div>
        <div class="item-desc">{{ f.description }}</div>
        <span class="item-badge">流程图</span>
      </div>
    </div>

    <div v-if="mode === 'mindmaps'" class="item-list">
      <div class="item-card" v-for="m in filteredMaps" :key="m.title" @click="openModal('map', m)">
        <div class="item-title">{{ m.title }}</div>
        <div class="item-desc">{{ m.description }}</div>
        <span class="item-badge mindmap">思维导图</span>
      </div>
    </div>

    <!-- 模态框 -->
    <div class="modal-overlay" v-if="modalShow" @click.self="closeModal">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ modalTitle }}</h3>
          <div class="modal-actions">
            <button class="zoom-btn" @click="zoomOut" title="缩小">−</button>
            <span class="zoom-pct">{{ Math.round(scale * 100) }}%</span>
            <button class="zoom-btn" @click="zoomIn" title="放大">+</button>
            <button class="zoom-btn" @click="zoomReset" title="重置">↺</button>
            <button class="modal-close" @click="closeModal">✕</button>
          </div>
        </div>
        <p class="modal-desc" v-if="modalDesc">{{ modalDesc }}</p>
        <div class="zoom-area">
          <div :style="{ transform: 'scale(' + scale + ')', transformOrigin: 'top left' }">
            <div v-if="modalType === 'flow'" class="mermaid-wrap" ref="mermaidEl"></div>
            <div v-if="modalType === 'map'" class="markmap-wrap" ref="markmapEl"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from "vue";
import mermaid from "mermaid";
import { Markmap } from "markmap-view";
import { Transformer } from "markmap-lib";
import { fetchKnowledge } from "../api.js";

const props = defineProps({ scrollDoc: Object });
const emit = defineEmits(["update:mode"]);

// 通知父组件当前子模式
const mode = ref("concepts");
watch(mode, (v) => emit("update:mode", v));

const data = ref({ concepts: [], flowcharts: [], mindmaps: [] });
const filterCat = ref("");
const tierFilter = ref("all");
const expanded = ref(null);

// Modal
const modalShow = ref(false);
const modalType = ref("");
const modalTitle = ref("");
const modalDesc = ref("");
const modalData = ref(null);
const mermaidEl = ref(null);
const markmapEl = ref(null);
const scale = ref(1);

function zoomIn() { scale.value = Math.min(3, scale.value + 0.2); }
function zoomOut() { scale.value = Math.max(0.3, scale.value - 0.2); }
function zoomReset() { scale.value = 1; }
function onWheel(e) {
  scale.value = Math.max(0.3, Math.min(3, scale.value + (e.deltaY > 0 ? -0.1 : 0.1)));
}

const categories = computed(() => {
  const s = new Set();
  data.value.concepts.forEach(c => s.add(c.category));
  return [...s].sort();
});

const catFiltered = computed(() => filterCat.value ? data.value.concepts.filter(c => c.category === filterCat.value) : data.value.concepts);

const conceptsTotal = computed(() => catFiltered.value.length);
const coreCount = computed(() => catFiltered.value.filter(c => c.tier === 'core').length);
const extendedCount = computed(() => catFiltered.value.filter(c => c.tier === 'extended').length);

const filteredConcepts = computed(() => {
  let arr = catFiltered.value;
  if (tierFilter.value !== 'all') arr = arr.filter(c => c.tier === tierFilter.value);
  return arr;
});
const filteredFlows = computed(() =>
  filterCat.value ? data.value.flowcharts.filter(f => f.category === filterCat.value) : data.value.flowcharts
);
const filteredMaps = computed(() =>
  filterCat.value ? data.value.mindmaps.filter(m => m.category === filterCat.value) : data.value.mindmaps
);

// 按导航树顺序的文档列表（从 KnowledgeNav 的 key 推断）
const docOrder = [
  "认知阶段", "大模型微调", "提示词",
  "Embeddings", "向量数据库", "RAG五大范式", "Navtive_RAG", "Advance RAG", "Self-RAG", "CorrectiveRAG", "Modular RAG", "知识图谱", "Agentic RAG", "RAG评估", "多模态RAG",
  "智能体介绍", "LangChain核心组件", "LangGraph",
  "Single Agent", "ReAct", "Plan&Execute", "Router+Skill", "Multi_Agent", "Blackboard", "Graph_Workflow",
  "CrewAI", "AutoGen",
  "LangSmith", "DeepAgent", "MCP入门", "MCP进阶", "Coze", "Vibe Coding", "Claude code",
  "机器学习介绍", "线性回归+逻辑回归", "决策树+随机森林+XGBoost", "SVM+KNN+朴素贝叶斯", "聚类+降维",
  "深度学习介绍", "CNN", "NLP处理", "RNN", "LSTM", "GRU", "Seq2Seq", "Attention+Transformer",
  "微调入门", "微调进阶", "微调实操", "模型量化", "知识蒸馏", "UnSloth", "Docker",
];

// 监听外部导航点击
watch(() => props.scrollDoc?.ts, () => {
  const key = props.scrollDoc?.key;
  if (!key) return;
  mode.value = "docs";
  nextTick(() => {
    const el = document.getElementById("doc-" + key.replace(/\s+/g, "-"));
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

// 概念 source -> 导航 key 显式映射
const sourceKeyMap = {
  "01_认知阶段": "认知阶段",
  "大模型微调 副本": "大模型微调", "大模型微调进阶": "微调进阶", "大模型微调入门": "微调入门", "大模型微调": "大模型微调",
  "提示词": "提示词",
  "Embeddings": "Embeddings", "向量数据库": "向量数据库",
  "RAG的五大范式": "RAG五大范式", "Navtive_RAG": "Navtive_RAG",
  "Advance RAG": "Advance RAG", "AdvanceRAG": "Advance RAG",
  "Self-RAG": "Self-RAG", "CorrectiveRAG": "CorrectiveRAG",
  "Modular RAG": "Modular RAG",
  "GraphRag": "知识图谱", "知识图谱": "知识图谱",
  "Agentic RAG": "Agentic RAG", "RAG评估": "RAG评估", "多模态RAG": "多模态RAG",
  "智能体介绍": "智能体介绍",
  "LangChain的核心组件": "LangChain核心组件", "核心组件": "LangChain核心组件",
  "LangGraph": "LangGraph", "langgraph": "LangGraph",
  "Single Agent": "Single Agent", "ReAct": "ReAct", "Plan&Execute": "Plan&Execute",
  "Router+Skill": "Router+Skill", "Multi_Agent": "Multi_Agent",
  "Blackboard": "Blackboard", "Graph_Workflow": "Graph_Workflow", "Graph工作流": "Graph_Workflow",
  "CrewAI": "CrewAI", "AutoGen": "AutoGen",
  "LangSmith": "LangSmith", "DeepAgent": "DeepAgent",
  "MCP入门": "MCP入门", "进阶版": "MCP进阶",
  "coze": "Coze", "Coze": "Coze",
  "Vibe Coding": "Vibe Coding", "Claude code": "Claude code", "Claude Code": "Claude code",
  "机器学习介绍": "机器学习介绍", "监督学习": "线性回归+逻辑回归", "线性回归": "线性回归+逻辑回归",
  "决策树": "决策树+随机森林+XGBoost", "随机森林": "决策树+随机森林+XGBoost", "XGBoost": "决策树+随机森林+XGBoost",
  "SVM": "SVM+KNN+朴素贝叶斯", "KNN": "SVM+KNN+朴素贝叶斯", "朴素贝叶斯": "SVM+KNN+朴素贝叶斯",
  "聚类": "聚类+降维", "PCA": "聚类+降维",
  "深度学习介绍": "深度学习介绍",
  "CNN": "CNN", "NLP": "NLP处理",
  "RNN": "RNN", "LSTM": "LSTM", "GRU": "GRU",
  "Seq2Seq": "Seq2Seq", "注意力机制": "Attention+Transformer", "Transformer": "Attention+Transformer",
  "微调入门": "微调入门", "微调进阶": "微调进阶", "微调实操": "微调实操",
  "量化": "模型量化", "PTQ": "模型量化", "QAT": "模型量化",
  "蒸馏": "知识蒸馏",
  "UnSloth": "UnSloth", "EvalScope": "UnSloth",
  "Docker": "Docker",
};

function matchKey(c) {
  // 1. 精确 source 匹配
  const src = c.source || "";
  for (const [pattern, key] of Object.entries(sourceKeyMap)) {
    if (src.includes(pattern)) return key;
  }
  // 2. 按 category 匹配
  const cat = c.category || "";
  if (cat === "传统机器学习") {
    const title = c.title;
    if (title.includes("监督学习") || title.includes("无监督学习")) return "机器学习介绍";
    if (title.includes("线性回归") || title.includes("逻辑回归")) return "线性回归+逻辑回归";
    if (title.includes("决策树") || title.includes("随机森林") || title.includes("XGBoost")) return "决策树+随机森林+XGBoost";
    if (title.includes("SVM") || title.includes("KNN") || title.includes("朴素贝叶斯")) return "SVM+KNN+朴素贝叶斯";
    if (title.includes("K-Means") || title.includes("聚类") || title.includes("PCA")) return "聚类+降维";
    if (title.includes("过拟合") || title.includes("特征工程")) return "机器学习介绍";
    return "机器学习介绍";
  }
  if (cat === "深度学习") {
    const title = c.title;
    if (title.includes("反向传播") || title.includes("激活函数") || title.includes("梯度下降")) return "深度学习介绍";
    if (title.includes("CNN") || title.includes("卷积")) return "CNN";
    if (title.includes("RNN")) return "RNN";
    if (title.includes("LSTM")) return "LSTM";
    if (title.includes("GRU")) return "GRU";
    if (title.includes("Seq2Seq") || title.includes("词向量") || title.includes("NLP")) return "NLP处理";
    if (title.includes("Attention") || title.includes("注意力") || title.includes("Transformer")) return "Attention+Transformer";
    if (title.includes("梯度消失") || title.includes("交叉验证")) return "深度学习介绍";
    return "深度学习介绍";
  }
  if (cat === "模型压缩") {
    const title = c.title;
    if (title.includes("量化") && !title.includes("QLoRA")) return "模型量化";
    if (title.includes("蒸馏")) return "知识蒸馏";
    return "模型量化";
  }
  if (cat === "训练框架与工具") {
    const title = c.title;
    if (title.includes("UnSloth") || title.includes("EvalScope")) return "UnSloth";
    if (title.includes("DeepSpeed")) return "微调进阶";
    if (title.includes("LangSmith")) return "LangSmith";
    if (title.includes("LLaMA-Factory")) return "微调进阶";
    return "微调进阶";
  }
  if (cat === "部署与工程化") {
    if (c.title.includes("Docker")) return "Docker";
    if (c.title.includes("Vibe Coding")) return "Vibe Coding";
    if (c.title.includes("训练三阶段")) return "大模型微调";
    if (c.title.includes("云端API")) return "大模型微调";
    return "大模型微调";
  }
  if (cat === "MCP") {
    if (c.title.includes("Server") || c.title.includes("进阶")) return "MCP进阶";
    return "MCP入门";
  }
  if (cat === "AI应用平台") {
    if (c.title.includes("Coze")) return "Coze";
    if (c.title.includes("Dify")) return "Coze";
    if (c.title.includes("Claude Code")) return "Claude code";
    return "Coze";
  }
  if (cat === "大模型微调") {
    if (c.title.includes("LoRA") || c.title.includes("QLoRA") || c.title.includes("PEFT")) return "微调进阶";
    if (c.title.includes("DoRA") || c.title.includes("Prefix") || c.title.includes("Adapter")) return "微调进阶";
    if (c.title.includes("RLHF") || c.title.includes("DPO") || c.title.includes("PPO") || c.title.includes("RLAIF")) return "微调进阶";
    if (c.title.includes("全参数微调")) return "微调入门";
    if (c.title.includes("灾难性遗忘")) return "微调入门";
    return "微调进阶";
  }
  if (cat === "大模型基础") {
    if (c.title.includes("预训练") || c.title.includes("涌现")) return "认知阶段";
    if (c.title.includes("Token") || c.title.includes("采样") || c.title.includes("上下文")) return "认知阶段";
    if (c.title.includes("Ollama") || c.title.includes("vLLM") || c.title.includes("云端API")) return "认知阶段";
    if (c.title.includes("幻觉") || c.title.includes("灾难性遗忘")) return "认知阶段";
    if (c.title.includes("MoE") || c.title.includes("FlashAttention") || c.title.includes("多模态")) return "认知阶段";
    if (c.title.includes("自监督") || c.title.includes("BLEU")) return "认知阶段";
    return "认知阶段";
  }
  if (cat === "提示工程") {
    if (c.title.includes("提示工程") || c.title.includes("消息角色")) return "提示词";
    if (c.title.includes("Few-shot") || c.title.includes("Zero-Shot")) return "提示词";
    if (c.title.includes("CoT") || c.title.includes("思维链")) return "提示词";
    if (c.title.includes("自我一致性")) return "提示词";
    return "提示词";
  }
  return src;
}

const docGroups = computed(() => {
  const groups = {};
  for (const c of filteredConcepts.value) {
    const matched = matchKey(c);
    if (!groups[matched]) groups[matched] = { source: matched, concepts: [], label: "" };
    groups[matched].concepts.push(c);
  }
  // 按树顺序排列
  const result = [];
  for (const key of docOrder) {
    const g = groups[key];
    if (g && g.concepts.length > 0) result.push(g);
  }
  // 没匹配到的放最后
  for (const key of Object.keys(groups)) {
    if (!docOrder.includes(key) && groups[key].concepts.length > 0) {
      result.push(groups[key]);
    }
  }
  return result;
});

function toggle(title) {
  expanded.value = expanded.value === title ? null : title;
}

function renderDetail(text) {
  let html = text
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/\n/g, "<br>")
    // 加粗英文缩写+中文名模式: LoRA（低秩适配）-> <b>LoRA（低秩适配）</b>
    .replace(/\b([A-Z]{2,}[a-z]*)\b/g, "<b>$1</b>")
    // 加粗中文引号内容: 「xxx」
    .replace(/「([^」]+)」/g, "<b>「$1」</b>")
    // 加粗常见的: xxx：
    .replace(/([^>；。，])(优点|缺点|优势|劣势|作用|原理|方法|步骤|流程|定义|核心|关键|代表|特点|典型|常用|公式|注意|总结|做法|流程)/g, "$1<b>$2</b>")
    // 给每个"1. xxx"分点加换行
    .replace(/<br>(\d+\.\s)/g, "<br><br>$1")
    // 清理多余空行
    .replace(/(<br>){3,}/g, "<br><br>");
  return html;
}

mermaid.initialize({
  startOnLoad: false,
  theme: "default",
  flowchart: { useMaxWidth: true, htmlLabels: true, rankSpacing: 80, nodeSpacing: 60 },
  themeVariables: { fontSize: "16px" },
});

const transformer = new Transformer();

function toMarkmapMd(text) {
  // Handle both \n newlines and any escaped newlines
  const lines = text.replace(/\\n/g, "\n").split("\n").filter(l => l.trim());
  const out = [];
  for (const line of lines) {
    const stripped = line.replace(/^\s+/, "");
    const indent = line.length - stripped.length;
    const level = Math.max(0, Math.floor(indent / 2));
    out.push("  ".repeat(level) + "- " + stripped);
  }
  return "# root\n" + out.join("\n");
}

async function openModal(type, item) {
  scale.value = 1;
  modalType.value = type;
  modalTitle.value = item.title;
  modalDesc.value = item.description || "";
  modalData.value = item;
  modalShow.value = true;
  await nextTick();
  if (type === "flow") {
    renderMermaid(mermaidEl.value, item.mermaid);
  } else {
    renderMarkmap(markmapEl.value, item.markmap);
  }
}

async function renderMermaid(el, code) {
  if (!el) return;
  el.innerHTML = "";
  try {
    const id = "m-" + Math.random().toString(36).slice(2);
    const { svg } = await mermaid.render(id, code);
    // 用容器包裹，统一尺寸
    el.innerHTML = "<div class='mermaid-inner'>" + svg + "</div>";
    const svgEl = el.querySelector("svg");
    if (svgEl) {
      svgEl.removeAttribute("width");
      svgEl.removeAttribute("height");
      svgEl.style.width = "100%";
      svgEl.style.height = "auto";
    }
  } catch (e) {
    el.innerHTML = "<pre>" + code + "</pre>";
  }
}

async function renderMarkmap(el, text) {
  if (!el) return;
  el.innerHTML = "";
  try {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.style.width = "100%";
    svg.style.height = "500px";
    el.appendChild(svg);
    const md = toMarkmapMd(text);
    const { root } = transformer.transform(md);
    const mm = Markmap.create(svg, { autoFit: true, duration: 0 }, root);
    mm.fit();
  } catch (e) {
    console.error(e);
    el.innerHTML = "<pre style='white-space:pre-wrap;font-size:13px;color:#c62828'>" + e.message + "\n\n" + text + "</pre>";
  }
}

function closeModal() {
  modalShow.value = false;
  modalType.value = "";
  modalData.value = null;
}

onMounted(async () => {
  data.value = await fetchKnowledge();
});
</script>
