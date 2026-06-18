<template>
  <div class="app-shell">
    <aside class="sidebar" aria-label="算法选择">
      <div class="brand">
        <span class="brand-mark">AV</span>
        <div>
          <p class="eyebrow">课程设计项目</p>
          <h1>算法过程可视化实验平台</h1>
        </div>
      </div>

      <nav class="algorithm-list">
        <button
          v-for="algorithm in algorithms"
          :key="algorithm.id"
          class="algorithm-tab"
          :class="{ active: mode === 'algorithm' && selectedId === algorithm.id }"
          type="button"
          @click="selectAlgorithm(algorithm.id)"
        >
          <strong>{{ algorithm.title }}</strong>
          <span>{{ algorithm.type }} · {{ algorithm.difficulty }}</span>
        </button>
        <button
          class="algorithm-tab compare-tool"
          :class="{ active: mode === 'compare' }"
          type="button"
          @click="openCompare"
        >
          <strong>排序算法对比</strong>
          <span>冒泡排序 vs 快速排序</span>
        </button>
      </nav>

      <section class="requirement-card">
        <p class="eyebrow">覆盖指导书 3.1</p>
        <ul>
          <li>4 类核心算法与 CNN 扩展</li>
          <li>统一入口与旧 Demo 风格</li>
          <li>手动输入 / 随机生成 / 测试用例</li>
          <li>播放控制、保存数据、导出日志</li>
        </ul>
      </section>
    </aside>

    <main class="workspace">
      <header class="topbar">
        <div>
          <p class="eyebrow">{{ topType }}</p>
          <h2>{{ topTitle }}</h2>
        </div>
        <div class="status-strip" aria-label="当前执行状态">
          <span>Step {{ totalSteps ? stepIndex + 1 : 0 }} / {{ totalSteps }}</span>
          <span>{{ statusText }}</span>
        </div>
      </header>

      <section class="control-grid">
        <div class="panel input-panel">
          <div class="panel-heading">
            <h3>输入数据</h3>
            <button class="ghost-button icon-text" type="button" @click="randomizeInput">
              <Shuffle :size="16" />
              随机生成
            </button>
          </div>
          <label class="input-label" for="dataInput">{{ inputLabel }}</label>
          <textarea id="dataInput" v-model="inputText" rows="4" spellcheck="false" @input="markInputDirty"></textarea>
          <p class="hint">{{ inputHint }}</p>
          <div class="confirm-row">
            <button class="primary-button wide-button" type="button" @click="confirmInputAndStart">
              确定并开始
            </button>
            <span :class="{ dirty: inputDirty }">{{ inputStateText }}</span>
          </div>
          <div class="case-row" v-if="selectedAlgorithm">
            <button
              v-for="testCase in selectedAlgorithm.test_cases"
              :key="testCase.name"
              class="plain-button"
              type="button"
              @click="useTestCase(testCase.value)"
            >
              {{ testCase.name }}
            </button>
          </div>
          <div v-if="mode === 'algorithm' && selectedId === 'cnn'" class="draw-panel">
            <div class="draw-heading">
              <strong>手写数字画板</strong>
              <span>训练模型推理</span>
            </div>
            <canvas
              ref="canvasRef"
              class="digit-canvas"
              width="280"
              height="280"
              @pointerdown="beginDraw"
              @pointermove="drawMove"
              @pointerup="endDraw"
              @pointerleave="endDraw"
              @pointercancel="endDraw"
            ></canvas>
            <div class="draw-actions">
              <button class="primary-button icon-text" type="button" @click="runCanvasInference">
                <Play :size="16" />
                启动模型推理
              </button>
              <button class="plain-button icon-text" type="button" @click="clearCanvas">
                <RotateCcw :size="16" />
                清空画板
              </button>
            </div>
            <p class="hint">在画板写 0 到 9，系统会裁剪笔迹、缩放到 8x8，并加载已训练 CNN 输出概率柱状图。</p>
          </div>
          <div class="custom-box">
            <div class="custom-save-row">
              <input v-model="customName" class="custom-name" type="text" maxlength="50" placeholder="自定义数据名称" />
              <button class="plain-button icon-text" type="button" @click="saveCustom">
                <Save :size="16" />
                保存
              </button>
            </div>
            <div class="saved-list" v-if="customItems.length">
              <button
                v-for="item in customItems"
                :key="item.id"
                class="saved-item"
                type="button"
                @click="loadCustom(item.input)"
              >
                <span>{{ item.name }}</span>
                <Trash2 :size="15" @click.stop="deleteCustom(item.id)" />
              </button>
            </div>
          </div>
          <p class="error-text" role="alert">{{ errorText }}</p>
        </div>

        <div class="panel theory-panel">
          <div class="panel-heading">
            <h3>算法说明</h3>
            <label class="switch">
              <input v-model="showExplain" type="checkbox" />
              <span>讲解</span>
            </label>
          </div>
          <p id="algorithmSummary">{{ summaryText }}</p>
          <dl class="complexity-list">
            <div>
              <dt>时间复杂度</dt>
              <dd>{{ timeComplexity }}</dd>
            </div>
            <div>
              <dt>空间复杂度</dt>
              <dd>{{ spaceComplexity }}</dd>
            </div>
          </dl>
          <div class="metric-strip" v-if="metricItems.length">
            <span v-for="metric in metricItems" :key="metric.key">{{ metric.label }}：{{ metric.value }}</span>
          </div>
        </div>

        <div class="panel controls-panel">
          <div class="transport" aria-label="播放控制">
            <button class="icon-button" type="button" title="上一步" :disabled="!canPrev" @click="previousStep">
              <StepBack :size="19" />
            </button>
            <button class="primary-button icon-text" type="button" :disabled="totalSteps <= 1" @click="togglePlay">
              <Pause v-if="playing" :size="17" />
              <Play v-else :size="17" />
              {{ playing ? "暂停" : "播放" }}
            </button>
            <button class="icon-button" type="button" title="下一步" :disabled="!canNext" @click="nextStep">
              <StepForward :size="19" />
            </button>
            <button class="plain-button icon-text" type="button" @click="resetSteps">
              <RotateCcw :size="16" />
              重置
            </button>
          </div>
          <label class="speed-control" for="speedRange">
            <span>速度</span>
            <input id="speedRange" v-model.number="speed" type="range" min="250" max="1800" step="50" />
          </label>
          <div class="action-row">
            <button class="plain-button icon-text" type="button" @click="applyInput">
              <RefreshCcw :size="16" />
              刷新步骤
            </button>
            <button class="ghost-button icon-text" type="button" :disabled="!totalSteps" @click="exportCurrentLog">
              <Download :size="16" />
              导出日志
            </button>
            <button class="plain-button icon-text" type="button" @click="openCompare">
              <GitCompare :size="16" />
              排序对比
            </button>
          </div>
        </div>
      </section>

      <section class="visual-layout">
        <div class="panel visual-panel">
          <div class="panel-heading">
            <h3>过程视图</h3>
            <span class="pill">{{ phaseText }}</span>
          </div>
          <div class="visual-stage" aria-live="polite">
            <div v-if="!totalSteps" class="empty-state">生成步骤后会在这里展示算法状态变化。</div>

            <div v-else-if="mode === 'compare' && compareData" class="compare-stage">
              <div class="compare-summary">
                <span>结果一致：{{ compareData.summary.sameResult ? "是" : "否" }}</span>
                <span>快排步骤：{{ compareData.summary.quickSteps }}</span>
                <span>冒泡步骤：{{ compareData.summary.bubbleSteps }}</span>
              </div>
              <div class="compare-grid">
                <div class="compare-card">
                  <div class="compare-head">
                    <strong>快速排序</strong>
                    <span>{{ compareData.summary.quickCompare }} 比较 / {{ compareData.summary.quickSwap }} 交换</span>
                  </div>
                  <SortBars :step="compareQuickStep" :show-explain="showExplain" />
                </div>
                <div class="compare-card">
                  <div class="compare-head">
                    <strong>冒泡排序</strong>
                    <span>{{ compareData.summary.bubbleCompare }} 比较 / {{ compareData.summary.bubbleSwap }} 交换</span>
                  </div>
                  <SortBars :step="compareBubbleStep" :show-explain="showExplain" />
                </div>
              </div>
            </div>

            <SortBars
              v-else-if="currentStep?.state.kind === 'sort'"
              :step="currentStep"
              :show-explain="showExplain"
            />

            <div v-else-if="currentStep?.state.kind === 'graph'" class="graph-stage">
              <svg class="graph-canvas" viewBox="0 0 640 360" role="img" aria-label="Dijkstra 图状态">
                <template v-for="edge in currentStep.state.graph.edges" :key="`${edge.from}-${edge.to}`">
                  <line
                    :class="graphEdgeClass(currentStep.state, edge)"
                    :x1="layoutGraph(currentStep.state.graph.nodes)[edge.from].x"
                    :y1="layoutGraph(currentStep.state.graph.nodes)[edge.from].y"
                    :x2="layoutGraph(currentStep.state.graph.nodes)[edge.to].x"
                    :y2="layoutGraph(currentStep.state.graph.nodes)[edge.to].y"
                  />
                  <text
                    class="edge-label"
                    :x="(layoutGraph(currentStep.state.graph.nodes)[edge.from].x + layoutGraph(currentStep.state.graph.nodes)[edge.to].x) / 2"
                    :y="(layoutGraph(currentStep.state.graph.nodes)[edge.from].y + layoutGraph(currentStep.state.graph.nodes)[edge.to].y) / 2 - 8"
                  >
                    {{ edge.weight }}
                  </text>
                </template>
                <template v-for="node in currentStep.state.graph.nodes" :key="node">
                  <circle
                    :class="graphNodeClass(currentStep.state, node)"
                    :cx="layoutGraph(currentStep.state.graph.nodes)[node].x"
                    :cy="layoutGraph(currentStep.state.graph.nodes)[node].y"
                    r="24"
                  />
                  <text
                    class="node-text"
                    :x="layoutGraph(currentStep.state.graph.nodes)[node].x"
                    :y="layoutGraph(currentStep.state.graph.nodes)[node].y"
                  >
                    {{ node }}
                  </text>
                </template>
              </svg>
              <div>
                <div class="table-box">
                  <table>
                    <thead>
                      <tr>
                        <th>顶点</th>
                        <th>距离</th>
                        <th>前驱</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="node in currentStep.state.graph.nodes" :key="node">
                        <td>{{ node }}</td>
                        <td>{{ formatDistance(currentStep.state.distances[node]) }}</td>
                        <td>{{ currentStep.state.previous[node] || "-" }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p v-if="showExplain" class="explain-box">{{ currentStep.explain }}</p>
              </div>
            </div>

            <div v-else-if="currentStep?.state.kind === 'maze'" class="maze-stage">
              <div class="maze-grid" :style="{ gridTemplateColumns: `repeat(${currentStep.state.grid[0].length}, 1fr)` }">
                <template v-for="(row, rowIndex) in currentStep.state.grid" :key="rowIndex">
                  <div
                    v-for="(_cell, colIndex) in row"
                    :key="`${rowIndex}-${colIndex}`"
                    :class="mazeCellClass(currentStep.state, rowIndex, colIndex)"
                  >
                    {{ mazeCellLabel(currentStep.state, rowIndex, colIndex) }}
                  </div>
                </template>
              </div>
              <div class="legend">
                <div class="legend-item"><span class="swatch"></span><span>可通行</span></div>
                <div class="legend-item"><span class="swatch wall"></span><span>墙</span></div>
                <div class="legend-item"><span class="swatch visited"></span><span>已访问</span></div>
                <div class="legend-item"><span class="swatch current"></span><span>当前位置</span></div>
                <div class="legend-item"><span class="swatch path"></span><span>当前路径</span></div>
                <p v-if="showExplain" class="explain-box">{{ currentStep.explain }}</p>
              </div>
            </div>

            <div v-else-if="currentStep?.state.kind === 'huffman'" class="huffman-stage">
              <div class="queue-panel">
                <p class="mini-title">优先队列</p>
                <div class="queue-list">
                  <span
                    v-for="nodeId in currentStep.state.queue"
                    :key="nodeId"
                    :class="huffmanQueueClass(currentStep.state, nodeId)"
                  >
                    {{ huffmanNode(currentStep.state, nodeId)?.label }}
                    <b>{{ huffmanNode(currentStep.state, nodeId)?.weight }}</b>
                  </span>
                </div>
                <p v-if="showExplain" class="explain-box">{{ currentStep.explain }}</p>
              </div>
              <svg v-if="huffmanLayout(currentStep.state).nodes.length" class="huffman-tree" viewBox="0 0 660 330">
                <line
                  v-for="edge in huffmanLayout(currentStep.state).edges"
                  :key="`${edge.from}-${edge.to}`"
                  class="tree-edge"
                  :x1="edge.x1"
                  :y1="edge.y1"
                  :x2="edge.x2"
                  :y2="edge.y2"
                />
                <g v-for="node in huffmanLayout(currentStep.state).nodes" :key="node.id">
                  <circle :class="node.className" :cx="node.x" :cy="node.y" r="24" />
                  <text class="tree-label" :x="node.x" :y="node.y - 4">{{ node.label }}</text>
                  <text class="tree-weight" :x="node.x" :y="node.y + 12">{{ node.weight }}</text>
                </g>
              </svg>
              <div v-if="Object.keys(currentStep.state.codes || {}).length" class="code-table">
                <span v-for="(code, label) in currentStep.state.codes" :key="label">{{ label }}: {{ code }}</span>
              </div>
            </div>

            <div v-else-if="currentStep?.state.kind === 'cnn'" class="cnn-stage">
              <div class="cnn-matrix-panel">
                <p class="mini-title">输入图像</p>
                <div class="image-matrix" :style="{ gridTemplateColumns: `repeat(${currentStep.state.image[0].length}, 1fr)` }">
                  <span
                    v-for="(value, index) in flatten(currentStep.state.image)"
                    :key="index"
                    :style="matrixCellStyle(value)"
                  ></span>
                </div>
              </div>
              <div class="cnn-detail">
                <p class="mini-title">{{ currentStep.phase }}</p>
                <p v-if="showExplain" class="explain-box">{{ currentStep.explain }}</p>
                <div v-if="currentStep.state.featureMaps" class="feature-maps">
                  <div v-for="(map, index) in currentStep.state.featureMaps" :key="index" class="feature-map">
                    <span>特征图 {{ index + 1 }}</span>
                    <div class="small-matrix" :style="{ gridTemplateColumns: `repeat(${map[0].length}, 1fr)` }">
                      <i
                        v-for="(value, cellIndex) in flatten(map)"
                        :key="cellIndex"
                        :style="matrixCellStyle(value)"
                      ></i>
                    </div>
                  </div>
                </div>
                <div v-if="currentStep.state.probabilities" class="prob-list">
                  <div v-for="item in currentStep.state.probabilities" :key="item.label" class="prob-row">
                    <span>{{ item.label }}</span>
                    <b :style="{ width: `${Math.max(4, item.value * 100)}%` }"></b>
                    <em>{{ Math.round(item.value * 100) }}%</em>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel step-panel">
          <div class="panel-heading">
            <h3>步骤记录</h3>
            <span id="logCount">{{ totalSteps }} 条</span>
          </div>
          <ol v-if="mode !== 'compare'" class="step-list">
            <li
              v-for="(step, index) in runData?.steps || []"
              :key="step.index"
              :class="{ active: index === stepIndex }"
              @click="jumpTo(index)"
            >
              {{ step.message }}
            </li>
          </ol>
          <ol v-else class="step-list">
            <li
              v-for="index in totalSteps"
              :key="index"
              :class="{ active: index - 1 === stepIndex }"
              @click="jumpTo(index - 1)"
            >
              <b>{{ index }}.</b>
              快排：{{ compareData?.quick.steps[Math.min(index - 1, compareData.quick.steps.length - 1)]?.phase || "-" }}
              /
              冒泡：{{ compareData?.bubble.steps[Math.min(index - 1, compareData.bubble.steps.length - 1)]?.phase || "-" }}
            </li>
          </ol>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import {
  Download,
  GitCompare,
  Pause,
  Play,
  RefreshCcw,
  RotateCcw,
  Save,
  Shuffle,
  StepBack,
  StepForward,
  Trash2
} from "@lucide/vue";
import { api } from "./api";
import type { AlgorithmInfo, CustomData, RunResponse, SortCompareResponse, Step } from "./types";

type Mode = "algorithm" | "compare";

const SortBars = defineComponent({
  props: {
    step: { type: Object as () => Step | null, required: false, default: null },
    showExplain: { type: Boolean, required: true }
  },
  setup(props) {
    const className = (index: number) => {
      const state = props.step?.state || {};
      const classes = ["bar"];
      if ((state.compare || []).includes(index)) classes.push("compare");
      if (state.pivot === index) classes.push("pivot");
      if ((state.swap || []).includes(index)) classes.push("swap");
      if ((state.sorted || []).includes(index)) classes.push("sorted");
      return classes.join(" ");
    };
    const height = (value: number) => {
      const values = props.step?.state.values || [1];
      const max = Math.max(...values, 1);
      return `${Math.max(18, (value / max) * 265)}px`;
    };
    return () => {
      if (!props.step) {
        return h("div", { class: "empty-state" }, "暂无步骤。");
      }
      const values = props.step.state.values || [];
      return h("div", { class: "bar-stage" }, [
        h(
          "div",
          { class: "bars" },
          values.map((value: number, index: number) =>
            h("div", { class: "bar-wrap", key: index }, [
              h("div", { class: className(index), style: { height: height(value) } }, String(value)),
              h("div", { class: "bar-label" }, String(index))
            ])
          )
        ),
        props.showExplain ? h("div", { class: "explain-box" }, props.step.explain) : null
      ]);
    };
  }
});

const algorithms = ref<AlgorithmInfo[]>([]);
const selectedId = ref("quicksort");
const mode = ref<Mode>("algorithm");
const inputText = ref("");
const lastSortInput = ref("8, 3, 5, 1, 9, 2, 7");
const inputDirty = ref(false);
const inputStateText = ref("等待加载");
const customName = ref("");
const customItems = ref<CustomData[]>([]);
const runData = ref<RunResponse | null>(null);
const compareData = ref<SortCompareResponse | null>(null);
const stepIndex = ref(0);
const playing = ref(false);
const speed = ref(850);
const showExplain = ref(true);
const errorText = ref("");
const canvasRef = ref<HTMLCanvasElement | null>(null);
const drawing = ref(false);
const canvasStarted = ref(false);
let timer: number | null = null;

const selectedAlgorithm = computed(() => algorithms.value.find((algorithm) => algorithm.id === selectedId.value) || null);
const currentStep = computed(() => runData.value?.steps[stepIndex.value] || null);
const compareQuickStep = computed(() => compareStep(compareData.value?.quick.steps || []));
const compareBubbleStep = computed(() => compareStep(compareData.value?.bubble.steps || []));
const totalSteps = computed(() => {
  if (mode.value === "compare" && compareData.value) {
    return Math.max(compareData.value.quick.steps.length, compareData.value.bubble.steps.length);
  }
  return runData.value?.steps.length || 0;
});
const canPrev = computed(() => totalSteps.value > 0 && stepIndex.value > 0);
const canNext = computed(() => totalSteps.value > 0 && stepIndex.value < totalSteps.value - 1);
const topType = computed(() => (mode.value === "compare" ? "算法对比" : selectedAlgorithm.value?.type || "算法"));
const topTitle = computed(() => (mode.value === "compare" ? "冒泡排序 vs 快速排序" : selectedAlgorithm.value?.title || "加载中"));
const statusText = computed(() => {
  if (playing.value) return "自动播放中";
  if (mode.value === "compare") return compareQuickStep.value?.status || "等待运行";
  return currentStep.value?.status || "等待运行";
});
const phaseText = computed(() => {
  if (mode.value === "compare") return compareQuickStep.value?.phase || "未开始";
  return currentStep.value?.phase || "未开始";
});
const inputLabel = computed(() => (mode.value === "compare" ? "对比数组元素" : selectedAlgorithm.value?.input_label || ""));
const inputHint = computed(() =>
  mode.value === "compare"
    ? "输入 3 到 30 个整数。系统会用同一组数据并排生成快速排序和冒泡排序步骤。"
    : selectedAlgorithm.value?.input_hint || ""
);
const summaryText = computed(() =>
  mode.value === "compare"
    ? "同一组输入分别交给快速排序和冒泡排序，比较它们的步骤数量、比较次数和交换次数。"
    : selectedAlgorithm.value?.summary || ""
);
const timeComplexity = computed(() =>
  mode.value === "compare" ? "快排平均 O(n log n)，冒泡 O(n^2)" : selectedAlgorithm.value?.time_complexity || ""
);
const spaceComplexity = computed(() =>
  mode.value === "compare" ? "快排 O(log n)，冒泡 O(1)" : selectedAlgorithm.value?.space_complexity || ""
);
const metricItems = computed(() => {
  const metrics = mode.value === "compare" ? compareData.value?.summary : runData.value?.metrics;
  if (!metrics) return [];
  return Object.entries(metrics).map(([key, value]) => ({ key, label: metricLabel(key), value }));
});

onMounted(async () => {
  try {
    algorithms.value = await api.listAlgorithms();
    const first = algorithms.value.find((algorithm) => algorithm.id === "quicksort") || algorithms.value[0];
    if (first) {
      selectedId.value = first.id;
      inputText.value = first.test_cases[0]?.value || "";
      lastSortInput.value = inputText.value;
      await loadCustomData();
      await generateSteps();
      await nextTick();
      initCanvas();
    }
  } catch (error) {
    errorText.value = error instanceof Error ? error.message : "后端服务连接失败。";
  }
});

onBeforeUnmount(stopPlayback);

watch(speed, () => {
  if (playing.value) {
    stopPlayback();
    startPlayback();
  }
});

async function selectAlgorithm(id: string) {
  stopPlayback();
  mode.value = "algorithm";
  selectedId.value = id;
  canvasStarted.value = false;
  compareData.value = null;
  const algorithm = selectedAlgorithm.value;
  inputText.value = algorithm?.test_cases[0]?.value || "";
  stepIndex.value = 0;
  errorText.value = "";
  customName.value = "";
  await loadCustomData();
  await generateSteps();
  await nextTick();
  initCanvas();
}

async function openCompare() {
  stopPlayback();
  const previousId = selectedId.value;
  const defaultInput = getDefaultSortInput();
  const candidate =
    mode.value === "compare" || isSortAlgorithm(previousId) ? inputText.value : lastSortInput.value;

  mode.value = "compare";
  selectedId.value = "quicksort";
  runData.value = null;
  compareData.value = null;
  stepIndex.value = 0;
  customName.value = "";
  inputText.value = isSortableArrayText(candidate) ? candidate : defaultInput;
  await loadCustomData();
  await runCompare();
}

function markInputDirty() {
  inputDirty.value = true;
  inputStateText.value = "自定义数据未应用";
}

async function applyInput() {
  if (mode.value === "compare") {
    await runCompare();
  } else {
    await generateSteps();
  }
}

async function confirmInputAndStart() {
  await applyInput();
  if (totalSteps.value > 1) startPlayback();
}

async function useTestCase(value: string) {
  inputText.value = value;
  await confirmInputAndStart();
}

async function randomizeInput() {
  try {
    const algorithmId = mode.value === "compare" ? "quicksort" : selectedId.value;
    const response = await api.randomInput(algorithmId);
    inputText.value = response.input;
    await confirmInputAndStart();
  } catch (error) {
    errorText.value = error instanceof Error ? error.message : "随机数据生成失败。";
  }
}

async function generateSteps() {
  stopPlayback();
  try {
    runData.value = await api.runAlgorithm(selectedId.value, inputText.value);
    compareData.value = null;
    if (isSortAlgorithm(selectedId.value)) {
      lastSortInput.value = inputText.value;
    }
    stepIndex.value = 0;
    inputDirty.value = false;
    inputStateText.value = "当前数据已生成步骤";
    errorText.value = "";
  } catch (error) {
    runData.value = null;
    stepIndex.value = 0;
    inputDirty.value = true;
    errorText.value = error instanceof Error ? error.message : "步骤生成失败。";
  }
}

async function runCompare() {
  stopPlayback();
  try {
    compareData.value = await api.compareSort(inputText.value);
    runData.value = null;
    lastSortInput.value = inputText.value;
    stepIndex.value = 0;
    inputDirty.value = false;
    inputStateText.value = "当前数据已生成对比步骤";
    errorText.value = "";
  } catch (error) {
    compareData.value = null;
    runData.value = null;
    stepIndex.value = 0;
    inputDirty.value = true;
    errorText.value = error instanceof Error ? error.message : "对比步骤生成失败。";
  }
}

async function loadCustomData() {
  try {
    customItems.value = await api.listCustomData(selectedId.value);
  } catch {
    customItems.value = [];
  }
}

async function saveCustom() {
  if (!inputText.value.trim()) {
    errorText.value = "请先填写需要保存的输入数据。";
    return;
  }
  try {
    const name = customName.value.trim() || `${topTitle.value} 数据 ${customItems.value.length + 1}`;
    await api.saveCustomData(selectedId.value, name, inputText.value);
    customName.value = "";
    await loadCustomData();
    errorText.value = "";
  } catch (error) {
    errorText.value = error instanceof Error ? error.message : "保存自定义数据失败。";
  }
}

async function deleteCustom(id: number) {
  try {
    await api.deleteCustomData(id);
    await loadCustomData();
  } catch (error) {
    errorText.value = error instanceof Error ? error.message : "删除自定义数据失败。";
  }
}

async function loadCustom(value: string) {
  inputText.value = value;
  await applyInput();
}

function compareStep(steps: Step[]) {
  if (!steps.length) return null;
  return steps[Math.min(stepIndex.value, steps.length - 1)];
}

function isSortAlgorithm(id: string) {
  return id === "quicksort" || id === "bubble_sort";
}

function getDefaultSortInput() {
  const quicksort = algorithms.value.find((algorithm) => algorithm.id === "quicksort");
  return quicksort?.test_cases[0]?.value || "8, 3, 5, 1, 9, 2, 7";
}

function isSortableArrayText(text: string) {
  const raw = text
    .split(/[\s,，]+/)
    .map((item) => item.trim())
    .filter(Boolean);
  if (raw.length < 3 || raw.length > 30) return false;
  return raw.every((item) => /^-?\d+$/.test(item));
}

function nextStep() {
  if (stepIndex.value < totalSteps.value - 1) {
    stepIndex.value += 1;
  } else {
    stopPlayback();
  }
}

function previousStep() {
  if (stepIndex.value > 0) stepIndex.value -= 1;
}

function jumpTo(index: number) {
  stepIndex.value = Math.max(0, Math.min(index, totalSteps.value - 1));
}

function resetSteps() {
  stopPlayback();
  stepIndex.value = 0;
}

function togglePlay() {
  if (playing.value) {
    stopPlayback();
  } else {
    startPlayback();
  }
}

function startPlayback() {
  if (totalSteps.value <= 1) return;
  if (stepIndex.value >= totalSteps.value - 1) {
    stepIndex.value = 0;
  }
  playing.value = true;
  timer = window.setInterval(nextStep, speed.value);
}

function stopPlayback() {
  playing.value = false;
  if (timer !== null) {
    window.clearInterval(timer);
    timer = null;
  }
}

async function exportCurrentLog() {
  try {
    if (mode.value === "compare" && compareData.value) {
      const lines = [
        "算法：冒泡排序 vs 快速排序",
        `输入：${compareData.value.input}`,
        "",
        "对比指标：",
        ...Object.entries(compareData.value.summary).map(([key, value]) => `- ${metricLabel(key)}: ${value}`),
        "",
        "快速排序步骤：",
        ...compareData.value.quick.steps.map((step) => `${step.index}. [${step.phase}] ${step.message}`),
        "",
        "冒泡排序步骤：",
        ...compareData.value.bubble.steps.map((step) => `${step.index}. [${step.phase}] ${step.message}`)
      ];
      downloadText("sort-compare-log.txt", lines.join("\n"));
      return;
    }
    if (runData.value) {
      const response = await api.exportLog(runData.value);
      downloadText(response.filename, response.content);
    }
  } catch (error) {
    errorText.value = error instanceof Error ? error.message : "导出日志失败。";
  }
}

function downloadText(filename: string, content: string) {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function metricLabel(key: string) {
  const labels: Record<string, string> = {
    stepCount: "步骤",
    compareCount: "比较",
    swapCount: "交换",
    relaxCount: "松弛",
    visitedCount: "访问",
    mergeCount: "合并",
    featureCount: "特征",
    sameResult: "结果一致",
    quickSteps: "快排步骤",
    bubbleSteps: "冒泡步骤",
    quickCompare: "快排比较",
    bubbleCompare: "冒泡比较",
    quickSwap: "快排交换",
    bubbleSwap: "冒泡交换"
  };
  return labels[key] || key;
}

function layoutGraph(nodes: string[]) {
  const centerX = 320;
  const centerY = 180;
  const radius = 130;
  const positions: Record<string, { x: number; y: number }> = {};
  nodes.forEach((node, index) => {
    const angle = -Math.PI / 2 + (index / nodes.length) * Math.PI * 2;
    positions[node] = {
      x: Math.round(centerX + Math.cos(angle) * radius),
      y: Math.round(centerY + Math.sin(angle) * radius)
    };
  });
  return positions;
}

function edgeKey(a: string, b: string) {
  return [a, b].sort().join("-");
}

function graphEdgeClass(state: Record<string, any>, edge: Record<string, any>) {
  const classes = ["edge"];
  const active = state.activeEdge ? edgeKey(state.activeEdge[0], state.activeEdge[1]) : "";
  const current = edgeKey(edge.from, edge.to);
  const pathKeys = new Set((state.pathEdges || []).map((item: string[]) => edgeKey(item[0], item[1])));
  if (current === active) classes.push("active");
  if (pathKeys.has(current)) classes.push("path");
  return classes.join(" ");
}

function graphNodeClass(state: Record<string, any>, node: string) {
  const classes = ["node-circle"];
  const visited = new Set(state.visited || []);
  const pathNodes = new Set<string>();
  (state.pathEdges || []).forEach((edge: string[]) => {
    pathNodes.add(edge[0]);
    pathNodes.add(edge[1]);
  });
  if (state.current === node) classes.push("current");
  if (visited.has(node)) classes.push("done");
  if (pathNodes.has(node)) classes.push("path");
  return classes.join(" ");
}

function formatDistance(value: unknown) {
  return value === null || value === undefined ? "∞" : value;
}

function mazeCellClass(state: Record<string, any>, row: number, col: number) {
  const classes = ["cell"];
  const pathKeys = new Set((state.path || []).map((point: number[]) => `${point[0]},${point[1]}`));
  const currentKey = state.current ? `${state.current[0]},${state.current[1]}` : "";
  if (state.grid[row][col] === 1) classes.push("wall");
  if (state.visited[row][col] && state.grid[row][col] === 0) classes.push("visited");
  if (pathKeys.has(`${row},${col}`)) classes.push("path");
  if (`${row},${col}` === currentKey) classes.push("current");
  if (row === 0 && col === 0) classes.push("start");
  if (row === state.grid.length - 1 && col === state.grid[0].length - 1) classes.push("end");
  return classes.join(" ");
}

function mazeCellLabel(state: Record<string, any>, row: number, col: number) {
  if (row === 0 && col === 0) return "S";
  if (row === state.grid.length - 1 && col === state.grid[0].length - 1) return "T";
  return "";
}

function huffmanNode(state: Record<string, any>, nodeId: string) {
  return (state.nodes || []).find((node: Record<string, any>) => node.id === nodeId);
}

function huffmanQueueClass(state: Record<string, any>, nodeId: string) {
  const classes = ["queue-chip"];
  if ((state.selected || []).includes(nodeId)) classes.push("selected");
  if (state.merged === nodeId) classes.push("merged");
  return classes.join(" ");
}

function huffmanLayout(state: Record<string, any>) {
  const allNodes = state.nodes || [];
  const byId = new Map<string, Record<string, any>>(allNodes.map((node: Record<string, any>) => [node.id, node]));
  const children = new Set<string>();
  allNodes.forEach((node: Record<string, any>) => {
    if (node.left) children.add(node.left);
    if (node.right) children.add(node.right);
  });
  const root =
    state.merged ||
    allNodes
      .filter((node: Record<string, any>) => (node.left || node.right) && !children.has(node.id))
      .at(-1)?.id;
  if (!root || !byId.has(root)) return { nodes: [], edges: [] };
  let leafIndex = 0;
  const nodes: Array<Record<string, any>> = [];
  const edges: Array<Record<string, any>> = [];
  const positions = new Map<string, { x: number; y: number }>();

  function walk(nodeId: string, depth: number): number {
    const node = byId.get(nodeId);
    if (!node) return 80;
    const left = node.left as string | null;
    const right = node.right as string | null;
    let x: number;
    if (!left && !right) {
      x = 70 + leafIndex * 78;
      leafIndex += 1;
    } else {
      const leftX = left ? walk(left, depth + 1) : 70 + leafIndex * 78;
      const rightX = right ? walk(right, depth + 1) : leftX + 78;
      x = (leftX + rightX) / 2;
    }
    const y = 45 + depth * 72;
    positions.set(nodeId, { x, y });
    const classParts = ["tree-node"];
    if ((state.selected || []).includes(nodeId)) classParts.push("selected");
    if (state.merged === nodeId) classParts.push("merged");
    nodes.push({
      id: nodeId,
      label: String(node.label).length > 4 ? String(node.label).slice(0, 4) : node.label,
      weight: node.weight,
      x,
      y,
      className: classParts.join(" ")
    });
    return x;
  }

  walk(root, 0);
  allNodes.forEach((node: Record<string, any>) => {
    const from = positions.get(node.id);
    if (!from) return;
    [node.left, node.right].forEach((child: string | null) => {
      if (!child) return;
      const to = positions.get(child);
      if (to) edges.push({ from: node.id, to: child, x1: from.x, y1: from.y + 24, x2: to.x, y2: to.y - 24 });
    });
  });
  return { nodes, edges };
}

function flatten(matrix: number[][]) {
  return matrix.flat();
}

function matrixCellStyle(value: number) {
  const amount = Math.min(0.92, 0.08 + Math.abs(value) * 0.18);
  return {
    backgroundColor: value < 0 ? `rgba(223, 74, 63, ${amount})` : `rgba(15, 139, 122, ${amount})`
  };
}

function initCanvas() {
  if (selectedId.value !== "cnn" || !canvasRef.value) return;
  const context = canvasRef.value.getContext("2d");
  if (!context || canvasStarted.value) return;
  context.fillStyle = "#fff";
  context.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height);
  context.lineCap = "round";
  context.lineJoin = "round";
  context.strokeStyle = "#111816";
  context.lineWidth = 18;
}

function clearCanvas() {
  const canvas = canvasRef.value;
  const context = canvas?.getContext("2d");
  if (!canvas || !context) return;
  context.fillStyle = "#fff";
  context.fillRect(0, 0, canvas.width, canvas.height);
  canvasStarted.value = false;
}

function beginDraw(event: PointerEvent) {
  const canvas = canvasRef.value;
  const context = canvas?.getContext("2d");
  if (!canvas || !context) return;
  event.preventDefault();
  canvas.setPointerCapture(event.pointerId);
  const point = canvasPoint(event);
  context.beginPath();
  context.moveTo(point.x, point.y);
  context.lineTo(point.x + 0.1, point.y + 0.1);
  context.stroke();
  drawing.value = true;
  canvasStarted.value = true;
}

function drawMove(event: PointerEvent) {
  const canvas = canvasRef.value;
  const context = canvas?.getContext("2d");
  if (!drawing.value || !canvas || !context) return;
  event.preventDefault();
  const point = canvasPoint(event);
  context.lineTo(point.x, point.y);
  context.stroke();
}

function endDraw(event?: PointerEvent) {
  const canvas = canvasRef.value;
  if (event && canvas?.hasPointerCapture(event.pointerId)) {
    canvas.releasePointerCapture(event.pointerId);
  }
  drawing.value = false;
}

function canvasPoint(event: PointerEvent) {
  const canvas = canvasRef.value as HTMLCanvasElement;
  const rect = canvas.getBoundingClientRect();
  return {
    x: ((event.clientX - rect.left) / rect.width) * canvas.width,
    y: ((event.clientY - rect.top) / rect.height) * canvas.height
  };
}

function captureCanvasMatrix() {
  const canvas = canvasRef.value;
  if (!canvas) return [];
  const small = document.createElement("canvas");
  small.width = 28;
  small.height = 28;
  const context = small.getContext("2d");
  if (!context) return [];
  context.fillStyle = "#fff";
  context.fillRect(0, 0, 28, 28);
  context.drawImage(canvas, 0, 0, 28, 28);
  const pixels = context.getImageData(0, 0, 28, 28).data;
  const matrix: number[][] = [];
  for (let row = 0; row < 28; row += 1) {
    const line: number[] = [];
    for (let col = 0; col < 28; col += 1) {
      const index = (row * 28 + col) * 4;
      const alpha = pixels[index + 3] / 255;
      const brightness = (pixels[index] + pixels[index + 1] + pixels[index + 2]) / (255 * 3);
      line.push(Number(Math.max(0, Math.min(1, (1 - brightness) * alpha)).toFixed(4)));
    }
    matrix.push(line);
  }
  return matrix;
}

async function runCanvasInference() {
  stopPlayback();
  try {
    const image = captureCanvasMatrix();
    runData.value = await api.predictDrawnDigit(image);
    compareData.value = null;
    mode.value = "algorithm";
    selectedId.value = "cnn";
    stepIndex.value = runData.value.steps.length - 1;
    inputStateText.value = "画板数据已完成模型推理";
    inputDirty.value = false;
    errorText.value = "";
  } catch (error) {
    errorText.value = error instanceof Error ? error.message : "画板推理失败。";
  }
}
</script>
