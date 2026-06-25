# 算法过程可视化实验平台 (Algorithm Process Visualization Lab)

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green.svg?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7.2-blue.svg?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![Vue](https://img.shields.io/badge/Vue-3.5.13-brightgreen.svg?style=flat-square&logo=vue.js)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Vite-6.4.3-purple.svg?style=flat-square&logo=vite)](https://vite.dev/)

本项目根据上级目录中的《算法过程可视化系统需求分析报告》和旧版纯前端 Demo 进行全面重构与实现。将算法教学以直观的动态步骤可视化流程呈现，极大降低了数据结构与算法的学习门槛。

---

## 🌐 在线体验

本项目已部署至公网，欢迎在线体验：

👉 **[算法过程可视化实验平台 (Online Live)](https://algorithm-visual-lab.onrender.com)**

> [!NOTE]
> 因部署在 Render 免费实例上，若首次访问加载较慢，可能是容器正在从休眠中唤醒，请耐心等待 1-2 分钟。

---

## 🛠️ 技术栈与编译/运行环境要求

本项目由前端与后端两部分组成，其开发与运行所需的语言版本及环境要求如下：

### 1. 后端 (Backend)
- **编程语言与编译器**：Python 3.11+
- **核心框架**：FastAPI 0.115.6
- **核心依赖**：
  - PyTorch 2.12.1 (机器学习模型推理)
  - NumPy 2.2.6
  - Pydantic 2.10.4
  - Uvicorn 0.34.0 (ASGI 服务器)
- **测试工具**：Pytest 8.3.4

### 2. 前端 (Frontend)
- **编程语言**：TypeScript 5.7.2
- **构建环境**：Node.js v18+ (推荐 v22.23.1)
- **应用框架**：Vue 3.5.13 + Vite 6.4.3
- **编译工具**：vue-tsc 2.2.0 (用于严格类型检查和构建编译)
- **图标库**：@lucide/vue 1.21.0

---

## 📂 目录结构

项目采用清晰的前后端分离目录结构。核心源码位于 `src/` (前端) 及 `app/` (后端，即后端源码目录)，测试代码位于 `tests/` (即后端测试目录) 中。

```text
algorithm_visual_lab/
├── backend/                   # 后端服务目录
│   ├── app/                   # 后端业务源码 (src/)
│   │   ├── algorithms.py      # 算法步骤生成逻辑
│   │   ├── main.py            # FastAPI 应用入口及接口定义
│   │   ├── models.py          # 请求和响应的数据模型
│   │   ├── storage.py         # 本地 JSON 数据持久化
│   │   └── digit_cnn.py       # CNN 手写数字识别模型推理
│   ├── ml/                    # 机器学习模型训练脚本
│   │   └── train_digit_cnn.py # CNN 模型训练脚本
│   ├── models/                # 模型权重及模型文件
│   │   └── digit_cnn_model.pt # 训练好的 PyTorch 权重文件
│   ├── tests/                 # 后端测试代码目录 (test/)
│   │   └── test_algorithms.py # 算法生成逻辑单元测试
│   └── requirements.txt       # 后端 Python 依赖清单
├── frontend/                  # 前端服务目录
│   ├── src/                   # 前端应用源码 (src/)
│   │   ├── App.vue            # 单页面主组件
│   │   ├── api.ts             # API 请求封装
│   │   ├── styles.css         # 全局样式
│   │   └── types.ts           # 前端 TypeScript 类型定义
│   └── package.json           # 前端依赖配置及编译脚本
└── README.md                  # 项目自述文件
```

---

## ✨ 已实现功能

| 分类 | 需求描述 | 实现情况 |
| :--- | :--- | :--- |
| **算法入口** | 统一算法入口 | 左侧统一算法选择，保留旧 Demo 布局风格 |
| **算法可视化**| 3 类算法可视化 | 快速排序、Dijkstra、迷宫 DFS 动态演示 |
| **Huffman**  | 第 4 类算法 | 动态哈夫曼树构造步骤及可视化 |
| **CNN 扩展**  | 简化 CNN 前向推理 | 可视化预处理、卷积、ReLU、池化、Softmax 过程 |
| **手写识别**  | 画板手写数字识别 | 提供画板输入，加载训练好的 CNN 模型，输出 0-9 概率柱状图 |
| **数据源**   | 多源数据输入 | 支持手动输入、随机生成、内置测试用例 |
| **播放控制**  | 播放状态调节 | 支持单步、上一步、自动播放、暂停、重置、速度调节 |
| **讲解说明**  | 步骤讲解模式 | 可开关详细讲解文字描述 |
| **自定义数据**| 数据管理 | 保存、加载、删除自定义输入数据 |
| **日志与对比**| 数据导出与对比 | 导出算法执行/对比日志；支持冒泡排序 vs 快速排序并排对比 |
| **参数校验**  | 输入校验 | 后端统一校验参数并返回友好错误提示 |

---

## 🚀 本地快速开始

### 1. 依赖安装

**安装后端依赖**
```bash
python -m pip install -r backend/requirements.txt
```

**安装前端依赖**
```bash
cd frontend
npm install
cd ..
```

### 2. 启动服务

**启动后端 API 服务**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
> 后端启动后可访问 API 交互文档：[http://localhost:8000/docs](http://localhost:8000/docs)

**启动前端开发服务器**
```bash
cd frontend
npm run dev -- --port 5173
```
> 前端启动后访问地址：[http://localhost:5173](http://localhost:5173)

---

## 🧪 测试与构建

**后端单元测试**
```bash
cd backend
pytest -q
```
目前测试验证结果：`9 passed`。

**前端类型检查与打包构建**
```bash
cd frontend
npm run build
```
前端使用 `vue-tsc` 进行严格的 TypeScript 静态类型检查，并通过 Vite 完成高效构建打包。

---

## 🧠 CNN 训练与模型说明

项目在保留原有 CNN 步骤演示动画的同时，引入了真实训练的 CNN 模型进行手写数字识别：

1. **数据集**：训练脚本会自动下载 MNIST 原始数据集并解压至 `backend/data/mnist/`。
2. **模型结构**：使用 PyTorch 搭建，架构为 `Conv16 -> Conv32 -> FC128 -> FC10`。
3. **硬件加速**：训练阶段若有 CUDA GPU 则自动使用 GPU 加速，后端推理阶段则使用 CPU 载入 `backend/models/digit_cnn_model.pt`。
4. **识别流程**：用户在前端画布上手写数字，点击推理后，图像数据传给后端，后端执行图像裁剪、中心对齐、缩放（28x28），经由卷积网络前向传播计算，返回 0 到 9 的概率分布，并渲染为概率柱状图。

**重新训练模型命令**
```bash
python backend/ml/train_digit_cnn.py
```
> **当前模型训练指标**：
> - 训练轮次 (Epochs): 7
> - 训练准确率 (Train Accuracy): 99.32%
> - 测试准确率 (Test Accuracy): 99.01%
> - 训练设备: CUDA

---

## 📝 示例输入格式说明

在进行算法可视化演示时，可使用以下格式的数据进行手动输入：

* **快速排序 (Quick Sort)**
  ```text
  8, 3, 5, 1, 9, 2, 7
  ```
* **Dijkstra 最短路径**
  ```text
  A; A-B:4, A-C:2, C-B:1, B-D:5, C-D:8, C-E:10, D-E:2
  ```
* **迷宫 DFS** (0 表示通路，1 表示障碍物，空格分隔)
  ```text
  0 0 1 0 0 0
  1 0 1 0 1 0
  0 0 0 0 1 0
  0 1 1 0 0 0
  0 0 0 1 1 0
  1 1 0 0 0 0
  ```
* **哈夫曼树构造 (Huffman Tree)**
  ```text
  A:5, B:9, C:12, D:13, E:16, F:45
  ```
* **CNN 推理图像选择**
  ```text
  digit_3
  digit_7
  ```

---

## 🔗 主要 API 接口参考

| 接口路径 | 请求方法 | 描述 |
| :--- | :---: | :--- |
| `/api/algorithms` | `GET` | 获取系统支持的所有算法的元数据 |
| `/api/algorithms/{id}/random` | `GET` | 随机生成适用于该算法的合法输入数据 |
| `/api/algorithms/{id}/run` | `POST` | 执行算法并获取分步的执行步骤 data |
| `/api/custom-data` | `GET` / `POST` | 查询或保存用户的自定义算法输入数据 |
| `/api/custom-data/{id}` | `DELETE` | 删除已保存的特定自定义输入数据 |
| `/api/logs/export` | `POST` | 导出当前算法的运行日志或对比日志 |
| `/api/compare/sort` | `POST` | 排序算法对比分析（如冒泡 vs 快速排序） |
| `/api/cnn/predict` | `POST` | CNN 前向传播各层特征图与推理结果预测 |
| `/api/cnn/draw-predict` | `POST` | 接收画板手写图片数据进行 CNN 模型推理 |
