-- 创建默认管理员用户
INSERT INTO users (username, email, password_hash) VALUES ('admin', 'admin@coze.com', '$2a$10$N.zmdr9k7uOCQb376NoUnuTBQVxPwNl.7fv376NoUnuTBQVxPwNl.7');

-- 插入示例插件
INSERT INTO plugins (name, description, version, definition) VALUES 
('Weather Plugin', '天气查询插件', '1.0.0', '{"name": "Weather Plugin", "version": "1.0.0", "description": "天气查询插件", "api": {"url": "https://api.weather.com/v1/current", "method": "GET"}}'),
('Translation Plugin', '翻译插件', '1.0.0', '{"name": "Translation Plugin", "version": "1.0.0", "description": "翻译插件", "api": {"url": "https://api.translation.com/v1/translate", "method": "POST"}}');

-- 插入示例工作流（关联到管理员用户）
INSERT INTO workflows (name, description, user_id, definition) VALUES 
('天气查询工作流', '查询指定城市天气', 1, '{"name": "天气查询工作流", "steps": [{"name": "输入城市", "type": "input"}, {"name": "查询天气", "type": "plugin", "plugin_id": 1}, {"name": "返回结果", "type": "output"}]}'),
('翻译工作流', '翻译文本', 1, '{"name": "翻译工作流", "steps": [{"name": "输入文本", "type": "input"}, {"name": "选择目标语言", "type": "input"}, {"name": "执行翻译", "type": "plugin", "plugin_id": 2}, {"name": "返回结果", "type": "output"}]}');

-- 插入示例机器人配置
INSERT INTO bot_configs (name, description, user_id, config) VALUES 
('默认聊天机器人', '默认聊天机器人配置', 1, '{"name": "默认聊天机器人", "description": "默认聊天机器人配置", "model": "gpt-3.5-turbo", "temperature": 0.7}'),
('客服机器人', '客服机器人配置', 1, '{"name": "客服机器人", "description": "客服机器人配置", "model": "gpt-4", "temperature": 0.5}');
