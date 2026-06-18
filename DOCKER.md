# Docker 打包与运行

本项目使用两个容器：

| 服务 | 说明 | 端口 |
| --- | --- | --- |
| backend | FastAPI 后端，CPU 加载 PyTorch MNIST 模型推理 | 8000 |
| frontend | Nginx 托管 Vue 构建产物，并代理 `/api` 到后端 | 8080 |

## 构建镜像

```bash
cd /home/zyb/日志/lesson_design/algorithm_visual_lab
docker compose build
```

如果 PyPI 访问慢，可以临时切换 Python 包索引：

```bash
PYPI_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple docker compose build
```

如果只构建某一个服务：

```bash
docker compose build backend
docker compose build frontend
```

## 启动

如果本地开发服务还在运行并占用了 `8000` 或 `8080`，先停止对应进程，或修改 `docker-compose.yml` 的端口映射。

```bash
docker compose up -d
```

访问地址：

```text
前端：http://localhost:8080
后端 API：http://localhost:8000
API 文档：http://localhost:8000/docs
```

## 查看状态和日志

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
```

## 停止和清理

停止容器：

```bash
docker compose down
```

停止并删除自定义数据卷：

```bash
docker compose down -v
```

## 重新打包

代码修改后重新构建并启动：

```bash
docker compose up -d --build
```

## 说明

- 后端 Docker 镜像默认安装 CPU 版 PyTorch，训练不在容器内执行，推理足够快。
- 已训练模型文件为 `backend/models/digit_cnn_model.pt`，构建镜像时会复制到后端镜像的 `/app/models/`；如果模型文件缺失，后端镜像构建会失败。
- 用户保存的自定义测试数据存放在 Docker volume `backend_data` 中。
- Render 默认文件系统是临时的，重新部署或重启后，本地写入的自定义数据可能丢失；需要长期保存时，在 Render 服务里挂载 Persistent Disk 到 `/app/data`。

## Render 部署

Render 不使用本地 `docker-compose.yml` 编排容器。项目额外提供了 Render 专用的单容器配置：

```text
Dockerfile
Dockerfile.render
render.yaml
render/start.sh
render/nginx.conf.template
```

`Dockerfile` 和 `Dockerfile.render` 作用相同；保留 `Dockerfile.render` 是为了说明这是 Render 单容器部署方案，根目录 `Dockerfile` 用来兼容 Render 或本地 Docker 的默认构建行为。

这个容器会在一个 Render Web Service 中同时运行：

- Nginx：监听 Render 提供的 `$PORT`，托管前端静态文件。
- FastAPI：监听容器内 `127.0.0.1:8000`，由 Nginx 代理 `/api`、`/docs`、`/openapi.json`。

部署方式：

1. 把整个 `algorithm_visual_lab` 项目推到 GitHub。推荐把 `algorithm_visual_lab` 作为仓库根目录。
2. 登录 Render，选择 `New` -> `Blueprint`。
3. 选择该 GitHub 仓库，Render 会读取根目录的 `render.yaml`。
4. 确认创建服务 `algorithm-visual-lab`。
5. 部署完成后访问 Render 给出的 `https://xxx.onrender.com` 地址。

如果你把上级目录 `lesson_design` 作为仓库根目录，需要在 Render 创建 Blueprint 时把 Blueprint 文件路径指定为：

```text
algorithm_visual_lab/render.yaml
```

也可以不用 Blueprint，手动创建一个 Web Service：

```text
Language: Docker
Dockerfile Path: ./Dockerfile.render
Docker Context: .
Health Check Path: /api/health
```

如果页面里没有填写 Dockerfile Path 的地方，保留默认 `Dockerfile` 即可。

如果仓库根目录是 `lesson_design`，手动创建 Web Service 时建议设置：

```text
Root Directory: algorithm_visual_lab
Dockerfile Path: ./Dockerfile.render
Docker Context: .
Health Check Path: /api/health
```

如果构建时 PyPI 访问慢，可以在 Render 的 Environment 中设置：

```text
PYPI_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
```
