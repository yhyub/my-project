## 使用 Trae CN 部署 Coze Studio 方案

### 当前状态分析

* 前端项目位于 `c:\Users\Administrator\Desktop\项目\coze-studio-0.2.0\frontend\apps\coze-studio`

* 使用 Rsbuild 构建工具，构建命令 `IS_OPEN_SOURCE=true rsbuild build`

* 开发服务器端口配置为 8888，API 代理到后端

* 后端服务已配置（Redis、Elasticsearch、MinIO、Etcd、Milvus、NSQ 等）

* 支持工作流功能

### 目标状态

* 使用 Trae CN 部署，不依赖 Docker Desktop

* Coze Studio 在 8888 端口访问

* 支持完整工作流功能

* 前后端分离部署

### 实现步骤

1. **构建前端应用**

   * 进入前端项目目录：`c:\Users\Administrator\Desktop\项目\coze-studio-0.2.0\frontend\apps\coze-studio`

   * 安装依赖：`npm install`

   * 构建生产版本：`IS_OPEN_SOURCE=true rsbuild build`

   * 构建产物位于 `dist` 目录

2. **配置后端服务**

   * 确保 `.env` 文件配置正确

   * 直接运行 Go 后端：`c:\Users\Administrator\Desktop\项目\coze-studio-0.2.0\backend\main.go`

   * 确保后端在 8080 端口运行

3. **使用 Trae CN 部署前端**

   * 在 Trae CN 中打开前端项目目录

   * 配置静态文件服务器：

     * 指向构建后的 `dist` 目录

     * 端口设置为 8888

   * 启动前端服务

4. **验证部署**

   * 访问 `http://localhost:8888/` 验证 Coze Studio 访问

   * 测试工作流功能

   * 验证模型管理功能

### 优势

* 不依赖 Docker Desktop，轻量化部署

* 使用 Trae CN 一键部署，操作简单

* 支持完整工作流功能

* 前后端分离，便于维护

### 注意事项

* 确保 Go 环境已配置，可直接运行后端

* 前端构建需要 Node.js 环境

* 后端服务需正常运行以支持工作流功能

