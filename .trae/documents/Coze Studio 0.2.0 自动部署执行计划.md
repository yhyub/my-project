我已经完成了Coze Studio 0.2.0部署所需的所有文件创建和配置工作，现在需要执行自动部署脚本：

1. **创建的文件**：

   * `docker-compose.yml`：完整的Docker服务配置文件

   * `schema.hcl`：数据库表结构定义

   * `init.sql`：初始数据脚本

   * `docker-images.md`：镜像列表和拉取命令

   * `deploy_coze_complete.ps1`：自动部署脚本

2. **部署脚本功能**：

   * 自动检查Docker运行状态

   * 拉取所有必要的Docker镜像

   * 启动所有服务

   * 监控服务日志

   * 验证服务运行状态

   * 显示访问信息和管理命令

3. **执行步骤**：

   * 运行 `deploy_coze_complete.ps1` 脚本

   * 脚本将自动完成所有部署步骤，无需用户干预

