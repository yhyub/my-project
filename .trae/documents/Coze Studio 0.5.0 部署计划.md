# Coze Studio 0.5.0 部署计划

## 项目分析

- **后端**：Go 语言开发，位于 `c:\Users\Administrator\Desktop\项目\coze-studio-0.5.0\backend`
- **前端**：React + TypeScript + Rsbuild，位于 `c:\Users\Administrator\Desktop\项目\coze-studio-0.5.0\frontend\apps\coze-studio`，使用 monorepo 管理依赖
- **当前状态**：前端已在 8888 端口运行简单 HTTP 服务器

## 部署计划

### 1. 检查并准备开发环境

- 检查 Go 版本和环境配置
- 检查 Node.js 和 npm 版本
- 检查是否已安装 pnpm（monorepo 依赖管理）

### 2. 构建前端应用

- 进入前端项目根目录：`c:\Users\Administrator\Desktop\项目\coze-studio-0.5.0\frontend`
- 安装依赖：使用 pnpm 安装所有 workspace 依赖
- 构建生产版本：`IS_OPEN_SOURCE=true rsbuild build`

### 3. 构建后端应用

- 进入后端目录：`c:\Users\Administrator\Desktop\项目\coze-studio-0.5.0\backend`
- 构建 Go 应用：`go build -o opencoze main.go`

### 4. 配置后端服务

- 复制 `.env.example` 为 `.env` 并配置相关参数
- 确保 Redis、Elasticsearch、MinIO、Etcd、Milvus、NSQ 等服务已启动并配置正确

### 5. 启动后端服务

- 运行构建好的后端应用：`./opencoze`

### 6. 部署前端静态文件

- 使用 Trae CN 托管前端构建产物（`dist` 目录）
- 确保前端服务在 8888 端口运行
- 配置前端 API 代理指向后端服务

### 7. 验证部署

- 访问 `http://localhost:8888` 验证应用是否正常运行
- 测试工作流功能
- 测试模型管理功能

## 注意事项

- 后端是 Go 项目，不是 Python 项目，不需要使用 pip 安装依赖
- 前端是 monorepo 项目，需要在前端根目录使用 pnpm 安装依赖
- 确保所有依赖服务（Redis、Elasticsearch 等）已正确配置
- 前端 API 代理需要指向运行中的后端服务

## 预期结果

- Coze Studio 0.5.0 版本成功部署
- 通过 `http://localhost:8888` 可以访问完整应用
- 支持完整的工作流功能
- 前后端服务正常通信