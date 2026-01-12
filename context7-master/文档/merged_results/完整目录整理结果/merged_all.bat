# 测试工作流自动化
curl -X POST "https://api.coze-automation.com/v1/automation/execute" \
  -H "Content-Type: application/json" \
  -H "X-Coze-API-Key: your-api-key-here" \
  -d '{
    "user_input": "创建数据同步工作流，每天凌晨同步数据库数据到数据仓库",
    "operation_type": "workflow_management",
    "enable_auto_processing": true,
    "auto_repair_level": "full",
    "workflow_config": {
      "name": "数据同步工作流",
      "description": "每天凌晨同步数据库数据到数据仓库",
      "triggers": [
        {
          "type": "schedule",
          "config": {
            "cron": "0 0 * * *"
          }
        }
      ]
    }
  }'

# 测试插件生成
curl -X POST "https://api.coze-automation.com/v1/automation/execute" \
  -H "Content-Type: application/json" \
  -H "X-Coze-API-Key: your-api-key-here" \
  -d '{
    "user_input": "创建实时股票监控插件：输入股票代码+波动阈值，价格超阈值时发送邮件警报",
    "operation_type": "plugin_generation",
    "enable_auto_processing": true,
    "plugin_config": {
      "plugin_name": "股票监控插件",
      "description": "实时监控股票价格并发送警报",
      "auto_register": true
    }
  }'