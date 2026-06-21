# 算法过程可视化实验平台

本项目根据上级目录中的《算法过程可视化系统需求分析报告》和旧版纯前端 Demo 进行全面重构与实现。将算法教学以直观的动态步骤可视化流程呈现，极大降低了数据结构与算法的学习门槛。

## 🌐 在线体验

本项目已部署至公网，欢迎点击下方链接在线体验：

👉 **[算法过程可视化实验平台 (Online Live)](https://algorithm-visual-lab.onrender.com)**

*(注：因部署在 Render 免费实例上，若首次访问加载较慢，可能是容器正在从休眠中唤醒，请等待 1-2 分钟。)*

## 技术栈

| 层次 | 技术 |
| --- | --- |
| 前端 | Vue 3 + Vite + TypeScript |
| 图标 | @lucide/vue |
| 后端 | Python 3.11 + FastAPI |
| 存储 | 本地 JSON 文件 |
| 测试 | pytest + vue-tsc/Vite build |

## 已实现功能

| 需求 | 实现情况 |
| --- | --- |
| 统一算法入口 | 左侧统一算法选择，保留旧 Demo 布局风格 |
| 3 类算法可视化 | 快速排序、Dijkstra、迷宫 DFS |
| 第 4 类算法 | 哈夫曼树构造 |
| CNN 扩展 | 简化 CNN 前向推理，可视化预处理、卷积、ReLU、池化、Softmax |
| 手写数字识别 | 提供画板输入，加载已训练小型 CNN 模型，输出 0-9 概率柱状图 |
| 输入来源 | 手动输入、随机生成、内置测试用例 |
| 播放控制 | 单步、上一步、自动播放、暂停、重置、速度调节 |
| 步骤讲解 | 可开关讲解模式 |
| 自定义数据 | 保存、加载、删除自定义输入 |
| 日志导出 | 导出当前算法或排序对比日志 |
| 算法对比 | 冒泡排序 vs 快速排序并排展示 |
| 输入校验 | 后端统一校验并返回错误提示 |

## 目录结构

```text
algorithm_visual_lab/
  backend/
    app/
      algorithms.py   # 算法步骤生成
      main.py         # FastAPI 接口
      models.py       # 请求和响应模型
      storage.py      # 本地 JSON 存储
      digit_cnn.py    # 已训练 CNN 模型推理
    ml/
      train_digit_cnn.py
    models/
      digit_cnn_model.pt
    tests/
      test_algorithms.py
    requirements.txt
  frontend/
    src/
      App.vue
      api.ts
      styles.css
      types.ts
    package.json
```

## 运行环境

当前开发环境使用 conda 的 `ld` 环境。

```bash
conda activate ld
```

首次运行安装依赖：

```bash
cd /home/zyb/日志/lesson_design/algorithm_visual_lab
python -m pip install -r backend/requirements.txt
cd frontend
npm install
```

## 启动项目

Docker 打包和 Render 部署方式见 [DOCKER.md](./DOCKER.md)。公网部署版本可直接通过 **[在线体验链接](https://algorithm-visual-lab.onrender.com)** 访问。

本地开发启动方式如下：

启动后端：

```bash
cd /home/zyb/日志/lesson_design/algorithm_visual_lab/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动前端：

```bash
cd /home/zyb/日志/lesson_design/algorithm_visual_lab/frontend
npm run dev -- --port 5173
```

访问：

```text
http://localhost:5173
```

API 文档：

```text
http://localhost:8000/docs
```

## 测试方式

后端测试：

```bash
cd /home/zyb/日志/lesson_design/algorithm_visual_lab/backend
pytest -q
```

前端构建：

```bash
cd /home/zyb/日志/lesson_design/algorithm_visual_lab/frontend
npm run build
```

当前验证结果：

```text
backend: 9 passed
frontend: vite build success
npm audit: 0 vulnerabilities
```

## CNN 训练模型

项目保留原有 CNN 演示动画，同时增加了真实训练模型的手写数字识别：

1. 训练脚本会下载 MNIST 原始 IDX 数据集到 `backend/data/mnist/`。
2. 模型使用 PyTorch 训练，结构为 `Conv16 -> Conv32 -> FC128 -> FC10`。
3. 训练阶段自动使用 CUDA GPU；后端推理阶段用 CPU 加载 `backend/models/digit_cnn_model.pt`。
4. 前端 CNN 页面提供画板，用户写数字后点击“启动模型推理”，后端会裁剪、居中、卷积推理，并返回 0 到 9 的概率柱状图。

当前模型指标：

```text
train_accuracy: 0.9932
test_accuracy: 0.9901
epochs: 7
train_device: cuda
```

说明：该模型用于课程设计中的推理过程可视化，重点展示训练权重、卷积特征和概率输出。

重新训练模型：

```bash
cd /home/zyb/日志/lesson_design/algorithm_visual_lab
python backend/ml/train_digit_cnn.py
```

## 示例输入

快速排序：

```text
8, 3, 5, 1, 9, 2, 7
```

Dijkstra：

```text
A; A-B:4, A-C:2, C-B:1, B-D:5, C-D:8, C-E:10, D-E:2
```

迷宫 DFS：

```text
0 0 1 0 0 0
1 0 1 0 1 0
0 0 0 0 1 0
0 1 1 0 0 0
0 0 0 1 1 0
1 1 0 0 0 0
```

哈夫曼树：

```text
A:5, B:9, C:12, D:13, E:16, F:45
```

CNN：

```text
digit_3
digit_7
```

## 主要接口

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/api/algorithms` | GET | 获取算法元信息 |
| `/api/algorithms/{id}/random` | GET | 生成随机输入 |
| `/api/algorithms/{id}/run` | POST | 生成算法步骤 |
| `/api/custom-data` | GET/POST | 查询或保存自定义数据 |
| `/api/custom-data/{id}` | DELETE | 删除自定义数据 |
| `/api/logs/export` | POST | 导出执行日志 |
| `/api/compare/sort` | POST | 排序算法对比 |
| `/api/cnn/predict` | POST | CNN 推理过程 |
| `/api/cnn/draw-predict` | POST | 画板手写数字识别 |
