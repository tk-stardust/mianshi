<template>
  <aside class="kn-sidebar">
    <div class="sidebar-title">课件导航</div>
    <div class="sidebar-tree">
      <template v-for="(phase, pi) in navTree" :key="pi">
        <div class="nav-phase" @click="toggleExpand('p', pi)">
          <span class="nav-arrow">{{ expandedState['p'+pi] ? '▾' : '▸' }}</span>
          {{ phase.label }}
        </div>
        <div v-show="expandedState['p'+pi]">
          <template v-for="(mod, mi) in phase.modules" :key="mi">
            <div class="nav-module" @click="toggleExpand('m', pi, mi)">
              <span class="nav-arrow">{{ expandedState['m'+pi+'-'+mi] ? '▾' : '▸' }}</span>
              {{ mod.label }}
            </div>
            <div v-show="expandedState['m'+pi+'-'+mi]" class="nav-docs">
              <div
                v-for="(doc, di) in mod.docs"
                :key="di"
                class="nav-doc"
                :class="{ active: activeDoc === doc.key }"
                @click="selectDoc(doc.key)"
              >
                <span class="nav-dot">·</span>
                {{ doc.label }}
                <span class="nav-count" v-if="doc.count > 0">{{ doc.count }}</span>
              </div>
            </div>
          </template>
        </div>
      </template>
    </div>
  </aside>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { fetchKnowledge } from "../api.js";

const emit = defineEmits(["selectDoc"]);
const props = defineProps({ activeDoc: String });

const data = ref({ concepts: [] });
const activeDoc = ref("");
const expandedState = reactive({});

// 默认展开第一层
const initExpand = () => {
  for (let pi = 0; pi < 2; pi++) expandedState["p" + pi] = true;
};

function toggleExpand(type, pi, mi) {
  const key = type === "p" ? "p" + pi : "m" + pi + "-" + mi;
  expandedState[key] = !expandedState[key];
}

function selectDoc(key) {
  activeDoc.value = key;
  emit("selectDoc", key);
}

const navTree = computed(() => {
  const getCount = (pattern) => {
    let c = 0;
    for (const item of data.value.concepts) {
      if ((item.source && item.source.includes(pattern)) ||
          (item.title && item.title.includes(pattern))) c++;
    }
    return c;
  };
  return [
    {
      label: "第二阶段", expanded: true, modules: [
        { label: "01 认知阶段", expanded: false, docs: [{ key: "认知阶段", label: "大模型介绍、调用、RAG、Agent", count: getCount("认知阶段") }] },
        { label: "02 大模型微调", expanded: false, docs: [{ key: "大模型微调", label: "大模型微调", count: getCount("大模型微调") || getCount("微调进阶") || getCount("微调入门") }] },
        { label: "03 提示词", expanded: false, docs: [{ key: "提示词", label: "提示词工程", count: getCount("提示词") }] },
        { label: "04 RAG", expanded: false, docs: [
          { key: "Embeddings", label: "Embeddings", count: getCount("Embeddings") },
          { key: "向量数据库", label: "向量数据库", count: getCount("向量数据库") },
          { key: "RAG五大范式", label: "RAG五大范式", count: getCount("RAG的五大范式") || getCount("RAG五大范式") },
          { key: "Navtive_RAG", label: "Naive RAG", count: getCount("Navtive_RAG") },
          { key: "Advance RAG", label: "Advance RAG", count: getCount("Advance RAG") || getCount("AdvanceRAG") },
          { key: "Self-RAG", label: "Self-RAG", count: getCount("Self-RAG") },
          { key: "CorrectiveRAG", label: "Corrective RAG", count: getCount("CorrectiveRAG") },
          { key: "Modular RAG", label: "Modular RAG", count: getCount("Modular RAG") },
          { key: "知识图谱", label: "Graph RAG", count: getCount("知识图谱") || getCount("GraphRag") },
          { key: "Agentic RAG", label: "Agentic RAG", count: getCount("Agentic RAG") },
          { key: "RAG评估", label: "RAG评估", count: getCount("RAG评估") },
          { key: "多模态RAG", label: "多模态RAG", count: getCount("多模态RAG") },
        ]},
        { label: "05 Agent_LangChain", expanded: false, docs: [
          { key: "智能体介绍", label: "智能体介绍", count: getCount("智能体介绍") },
          { key: "LangChain核心组件", label: "LangChain核心组件", count: getCount("LangChain的核心组件") || getCount("核心组件") },
          { key: "LangGraph", label: "LangGraph", count: getCount("LangGraph") || getCount("langgraph") },
        ]},
        { label: "06 Agent七大架构", expanded: false, docs: [
          { key: "Single Agent", label: "单Agent", count: getCount("Single Agent") },
          { key: "ReAct", label: "ReAct", count: getCount("ReAct") },
          { key: "Plan&Execute", label: "Plan&Execute", count: getCount("Plan&Execute") },
          { key: "Router+Skill", label: "Router+Skill", count: getCount("Router+Skill") },
          { key: "Multi_Agent", label: "Multi-Agent", count: getCount("Multi_Agent") },
          { key: "Blackboard", label: "Blackboard", count: getCount("Blackboard") },
          { key: "Graph_Workflow", label: "Graph Workflow", count: getCount("Graph_Workflow") || getCount("Graph工作流") },
        ]},
        { label: "07 多智能体框架", expanded: false, docs: [
          { key: "CrewAI", label: "CrewAI", count: getCount("CrewAI") },
          { key: "AutoGen", label: "AutoGen", count: getCount("AutoGen") },
        ]},
        { label: "08 LangSmith", expanded: false, docs: [{ key: "LangSmith", label: "LangSmith", count: getCount("LangSmith") }] },
        { label: "09 DeepAgent", expanded: false, docs: [{ key: "DeepAgent", label: "DeepAgent", count: getCount("DeepAgent") }] },
        { label: "10 MCP", expanded: false, docs: [
          { key: "MCP入门", label: "MCP入门", count: getCount("JSON-RPC") + getCount("MCP(模型") },
          { key: "MCP进阶", label: "MCP进阶", count: getCount("Server与Client") },
        ]},
        { label: "11 Coze", expanded: false, docs: [{ key: "Coze", label: "Coze", count: getCount("coze") || getCount("Coze") }] },
        { label: "12 Claude_Code", expanded: false, docs: [
          { key: "Vibe Coding", label: "Vibe Coding", count: getCount("Vibe Coding") },
          { key: "Claude code", label: "Claude Code", count: getCount("Claude code") || getCount("Claude Code") },
        ]},
      ],
    },
    {
      label: "第三阶段", expanded: true, modules: [
        { label: "01 传统机器学习", expanded: false, docs: [
          { key: "机器学习介绍", label: "机器学习介绍", count: getCount("机器学习介绍") },
          { key: "线性回归+逻辑回归", label: "线性回归+逻辑回归", count: getCount("监督学习") || getCount("线性回归") },
          { key: "决策树+随机森林+XGBoost", label: "决策树+随机森林+XGBoost", count: getCount("决策树") || getCount("随机森林") || getCount("XGBoost") },
          { key: "SVM+KNN+朴素贝叶斯", label: "SVM+KNN+朴素贝叶斯", count: getCount("SVM") || getCount("KNN") || getCount("朴素贝叶斯") },
          { key: "聚类+降维", label: "聚类+降维", count: getCount("聚类") || getCount("PCA") },
        ]},
        { label: "02 深度学习", expanded: false, docs: [
          { key: "深度学习介绍", label: "深度学习介绍+PyTorch", count: getCount("深度学习介绍") },
          { key: "CNN", label: "CNN", count: getCount("CNN") },
          { key: "NLP处理", label: "NLP处理", count: getCount("NLP") },
          { key: "RNN", label: "RNN", count: getCount("RNN") },
          { key: "LSTM", label: "LSTM", count: getCount("LSTM") },
          { key: "GRU", label: "GRU", count: getCount("GRU") },
          { key: "Seq2Seq", label: "Seq2Seq", count: getCount("Seq2Seq") },
          { key: "Attention+Transformer", label: "Attention+Transformer", count: getCount("注意力机制") || getCount("Transformer") },
        ]},
        { label: "03 微调进阶", expanded: false, docs: [
          { key: "微调入门", label: "微调入门", count: getCount("微调入门") },
          { key: "微调进阶", label: "微调进阶", count: getCount("微调进阶") },
          { key: "微调实操", label: "微调实操", count: getCount("微调实操") },
          { key: "模型量化", label: "模型量化", count: getCount("量化") || getCount("PTQ") || getCount("QAT") },
          { key: "知识蒸馏", label: "知识蒸馏", count: getCount("蒸馏") },
          { key: "UnSloth", label: "UnSloth+EvalScope", count: getCount("UnSloth") || getCount("EvalScope") },
          { key: "Docker", label: "Docker部署", count: getCount("Docker") },
        ]},
      ],
    },
  ];
});

onMounted(async () => {
  initExpand();
  data.value = await fetchKnowledge();
});
</script>
