# Docker 部署指南

本文档介绍如何基于提供的容器配置构建并部署 CrewAI 股票分析系统。Docker 镜像默认运行 `src/web_app.py`，启动后即可通过浏览器访问 Web UI。

## 1. 先决条件

- 已安装 Docker Engine 24+（或 Docker Desktop 最新版）
- 可访问互联网以拉取基础镜像和安装依赖
- 拥有可用的 OpenAI API Key（或兼容的模型服务端点），用于运行 CrewAI 相关能力

## 2. 本地构建镜像

1. 在项目根目录执行构建命令：

   ```bash
   docker build -t crewai-stock-analysis:latest .
   ```

2. 构建完成后，验证镜像是否存在：

   ```bash
   docker images | grep crewai-stock-analysis
   ```

## 3. 直接运行容器

```bash
docker run --rm \
  -p 5000:5000 \
  -e OPENAI_API_KEY="your-openai-key" \
  -e OPENAI_BASE_URL="https://api.openai.com/v1" \
  --name crewai-stock-test \
  crewai-stock-analysis:latest
```

- 默认监听 `0.0.0.0:5000`，访问 `http://localhost:5000`
- 若需修改端口，可调整 `-p 8080:5000`
- 可通过 `.env` 文件传入额外配置：

  ```bash
  cp .env.example .env  # 按需修改其中变量

  docker run --rm \
    -p 5000:5000 \
    --env-file .env \
    crewai-stock-analysis:latest
  ```

## 4. 使用 Docker Compose

项目根目录提供 `docker-compose.yml`，默认会：

- 使用同目录下的 `Dockerfile` 构建镜像
- 挂载端口 `5000:5000`
- 自动读取 `.env` 文件中的环境变量，并为关键变量提供默认值

快速启动：

```bash
cp .env.example .env  # 确认已填好 OPENAI_API_KEY 等变量

docker compose up -d
```

重要环境变量说明：

| 变量名 | 作用 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | OpenAI 或兼容服务的密钥 | 无 | **必须**填写，否则相关功能无法调用 |
| `OPENAI_BASE_URL` | OpenAI 接口地址 | `https://api.openai.com/v1` | 使用第三方兼容服务时修改 |
| `WEB_HOST` | Flask 绑定地址 | `0.0.0.0` | 一般保持默认 |
| `WEB_PORT` | Flask 监听端口 | `5000` | 若与宿主端口映射不同，可调整 |
| 其他（Serper、邮箱、缓存等） | 参考 `.env.example` | 视需求填写 | 非必需时可留空 |

停止服务：

```bash
docker compose down
```

## 5. 容器内运行测试或脚本

```bash
docker run --rm -it \
  --entrypoint "/bin/bash" \
  crewai-stock-analysis:latest

# 容器内执行
pytest
python main.py info
```

## 6. 推送到镜像仓库

以 GitHub Container Registry (GHCR) 为例：

```bash
export IMAGE=ghcr.io/<your-user-or-org>/crewai-stock-analysis:latest

docker tag crewai-stock-analysis:latest "$IMAGE"
echo "$GITHUB_TOKEN" | docker login ghcr.io -u <your-user-or-org> --password-stdin

docker push "$IMAGE"
```

- 将 `<your-user-or-org>` 替换为实际账号或组织
- 使用具有 `packages:write` 权限的 `GITHUB_TOKEN` 或 PAT 登录

## 7. GitHub Actions 自动化构建

`.github/workflows/docker-image.yml` 定义了自动化流程：

- 推送到 `main` 分支或手动触发 `workflow_dispatch` 时执行
- 使用 Buildx 构建 `linux/amd64` 镜像并推送到 `ghcr.io/<repo>:latest`
- 启用 GHA 缓存以提升重复构建效率

启用前请确认仓库允许 Actions 推送到 GHCR，如需推送至其他仓库可调整 `REGISTRY` / `IMAGE_NAME`。

## 8. 常见问题

- **无法访问外部 API**：检查宿主网络或为容器配置代理
- **构建缓慢**：开启 BuildKit 缓存、使用国内镜像源或私有 PyPI
- **定制启动命令**：修改 `Dockerfile` 的 `CMD` 或在 `docker compose` 中覆盖 `command`

完成以上步骤后，即可通过 Docker 单机或 Compose 编排方式部署并体验股票分析系统。
