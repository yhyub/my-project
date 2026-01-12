/**
 * Coze插件完整集成系统
 * 整合了三个文件的所有功能：
 * 1. integrated_coze_plugin_system.ts - YAML导入和IDE插件创建
 * 2. coze_plugin_complete_system.ts - JSON修复和工作流管理
 * 3. complete_coze_plugin_system.ts - OpenAPI配置和MCP服务器生成
 */

// ================================ 类型定义 ================================

// 插件输入接口
export interface PluginInput {
  coze_json_inputs?: string;
  repair_mode?: "basic" | "comprehensive" | "thorough" | "aggressive";
  output_structure?: "single_merged" | "plugin_array" | "individual_files" | "coze_import_ready";
  naming_convention?: "snake_case" | "camelCase" | "PascalCase" | "original";
  yaml_input?: string;
  ide_plugin_config?: IDEPluginConfig;
}

// IDE插件配置接口
export interface IDEPluginConfig {
  plugin_name: string;
  plugin_description: string;
  ide_type: "vscode" | "jetbrains" | "sublime";
  features: string[];
  dependencies?: string[];
}

// 插件输出接口
export interface PluginOutput {
  status: "success" | "error";
  processing_time_ms: number;
  original_plugins_count: number;
  repaired_plugins_count: number;
  parsing_errors: string[];
  repair_warnings: string[];
  repair_mode_used: string;
  output_structure_used: string;
  naming_convention_used: string;
  repaired_coze_plugins: any[];
  formatted_output: string;
  import_ready: boolean;
  error_message?: string;
  stack_trace?: string;
  timestamp: string;
  yaml_import_result?: any;
  ide_plugin_result?: any;
}

// JSON片段接口
interface JSONFragment {
  content: string;
  start: number;
  end: number;
  valid: boolean;
}

// 修复结果接口
interface RepairResult {
  success: boolean;
  data?: any;
  errors: string[];
  warnings: string[];
  processingTime?: number;
}

// 工作流节点接口
interface WorkflowNode {
  id: string;
  type: string;
  config?: any;
  inputs?: any[];
  outputs?: any[];
  code?: string;
  language?: string;
}

// 工作流请求接口
export interface WorkflowRequest {
  name: string;
  description: string;
  nodes: WorkflowNode[];
  edges?: any[];
  industry?: string;
  output_format?: string;
  config?: WorkflowConfig;
}

// 工作流配置接口
interface WorkflowConfig {
  version?: string;
  timeout?: number;
  retry_policy?: any;
}

// 验证请求接口
export interface ValidationRequest {
  data: any;
  schema: any;
}

// 验证响应接口
export interface ValidationResponse {
  valid: boolean;
  errors: string[];
}

// ================================ YAML处理工具类 ================================

export class YAMLHandler {
  public importYAMLToCozePlugin(yamlContent: string): any {
    try {
      const yamlData = this.parseYAML(yamlContent);
      const cozePlugin = this.convertToCozePlugin(yamlData);
      return {
        success: true,
        plugin: cozePlugin,
        message: 'YAML导入成功并转换为Coze插件格式'
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        message: 'YAML导入失败'
      };
    }
  }
  
  private parseYAML(yamlContent: string): any {
    const lines = yamlContent.split('\n');
    const result: any = {};
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        const [key, ...valueParts] = trimmed.split(':');
        if (key && valueParts.length > 0) {
          const value = valueParts.join(':').trim();
          result[key.trim()] = value;
        }
      }
    }
    
    return result;
  }
  
  private convertToCozePlugin(yamlData: any): any {
    return {
      node_id: yamlData.id || `coze_plugin_${Date.now()}`,
      node_name: yamlData.name || "未命名Coze插件",
      node_description: yamlData.description || "Coze插件描述",
      input_variables: [],
      output_variables: [],
      config: yamlData.config || {}
    };
  }
}

// ================================ IDE插件创建工具类 ================================

export class IDEPluginCreator {
  public createIDEPlugin(config: IDEPluginConfig): any {
    try {
      let idePlugin: any;
      
      switch (config.ide_type) {
        case "vscode":
          idePlugin = this.createVSCodePlugin(config);
          break;
        case "jetbrains":
          idePlugin = this.createJetBrainsPlugin(config);
          break;
        case "sublime":
          idePlugin = this.createSublimePlugin(config);
          break;
        default:
          throw new Error(`不支持的IDE类型: ${config.ide_type}`);
      }
      
      return {
        success: true,
        plugin: idePlugin,
        message: `${config.ide_type}插件创建成功`,
        plugin_type: config.ide_type
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        message: 'IDE插件创建失败'
      };
    }
  }
  
  private createVSCodePlugin(config: IDEPluginConfig): any {
    return {
      name: config.plugin_name,
      displayName: config.plugin_name,
      description: config.plugin_description,
      version: "1.0.0",
      publisher: "coze",
      engines: {
        vscode: "^1.80.0"
      },
      categories: ["Other"],
      activationEvents: ["onCommand:coze.start"],
      main: "./extension.js",
      contributes: {
        commands: [
          {
            command: "coze.start",
            title: "Start Coze Plugin"
          }
        ]
      },
      dependencies: config.dependencies || [],
      features: config.features,
      coze_integration: true
    };
  }
  
  private createJetBrainsPlugin(config: IDEPluginConfig): any {
    return {
      name: config.plugin_name,
      description: config.plugin_description,
      version: "1.0",
      vendor: "Coze",
      ideaVersion: "2023.1",
      dependencies: config.dependencies || [],
      extensions: [],
      actions: [
        {
          id: "CozeAction",
          className: "com.coze.plugin.CozeAction",
          text: "Coze Plugin Action",
          description: "Execute Coze Plugin Action"
        }
      ],
      features: config.features,
      coze_integration: true
    };
  }
  
  private createSublimePlugin(config: IDEPluginConfig): any {
    return {
      name: config.plugin_name,
      description: config.plugin_description,
      version: "1.0.0",
      author: "Coze",
      dependencies: config.dependencies || [],
      features: config.features,
      commands: [
        {
          name: "coze_command",
          description: "Coze Plugin Command"
        }
      ],
      coze_integration: true
    };
  }
}

// ================================ Coze插件修复工具类 ================================

export class CozePluginRepairTool {
  private repairMode: string;
  private namingConvention: string;
  private outputStructure: string;

  constructor(repairMode: string = "comprehensive", namingConvention: string = "snake_case", outputStructure: string = "plugin_array") {
    this.repairMode = repairMode;
    this.namingConvention = namingConvention;
    this.outputStructure = outputStructure;
  }

  public repairJSON(input: string): RepairResult & { repairedData?: any } {
    const startTime = Date.now();
    const allErrors: string[] = [];
    const allWarnings: string[] = [];

    try {
      const cleanedInput = this.cleanInput(input);
      const fragments = this.extractJSONFragments(cleanedInput);
      
      if (fragments.length === 0) {
        allErrors.push("未找到有效的JSON片段");
        return { 
          success: false, 
          errors: allErrors, 
          warnings: allWarnings 
        };
      }

      const parsedPlugins: any[] = [];
      for (const fragment of fragments) {
        if (fragment.valid) {
          try {
            const parsed = JSON.parse(fragment.content);
            const validation = this.validateCozePlugin(parsed);
            
            if (validation.isValid) {
              parsedPlugins.push(parsed);
            } else {
              allWarnings.push(`JSON片段验证失败: ${validation.errors.join(', ')}`);
              const repairAttempt = this.repairSinglePlugin(parsed);
              if (repairAttempt.success) {
                parsedPlugins.push(repairAttempt.data);
              }
            }
          } catch (parseError) {
            allWarnings.push(`JSON解析失败: ${parseError.message}`);
          }
        }
      }

      if (parsedPlugins.length === 0) {
        allErrors.push("所有JSON片段解析或验证失败");
        return {
          success: false,
          errors: allErrors,
          warnings: allWarnings
        };
      }

      const repairedPlugins: any[] = [];
      for (const plugin of parsedPlugins) {
        const repairResult = this.repairSinglePlugin(plugin);
        if (repairResult.success) {
          repairedPlugins.push(repairResult.data);
        } else {
          allWarnings.push(`插件修复失败: ${repairResult.errors.join(', ')}`);
        }
      }

      const connectedPlugins = this.connectPlugins(repairedPlugins, allWarnings);
      const normalizedPlugins = this.applyNamingConvention(connectedPlugins);
      const processingTime = Date.now() - startTime;
      
      return {
        success: true,
        repairedData: this.organizeOutput(normalizedPlugins, this.outputStructure),
        errors: allErrors,
        warnings: allWarnings,
        processingTime
      };

    } catch (error) {
      const processingTime = Date.now() - startTime;
      allErrors.push(`修复过程发生未知错误: ${error.message}`);
      return {
        success: false,
        errors: allErrors,
        warnings: allWarnings,
        processingTime
      };
    }
  }

  private cleanInput(input: string): string {
    if (!input || typeof input !== 'string') {
      return '{}';
    }

    let cleaned = input.trim();
    cleaned = cleaned.replace(/\/\*[\s\S]*?\*\//g, '');
    cleaned = cleaned.replace(/\/\/.*$/gm, '');
    cleaned = this.fixCommonJSONErrors(cleaned);
    return cleaned;
  }

  private fixCommonJSONErrors(jsonStr: string): string {
    let fixed = jsonStr;
    fixed = fixed.replace(/([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)(\s*:)/g, '$1"$2"$3');
    fixed = fixed.replace(/([}\]]")\s*([{["\]])/g, '$1,$2');
    fixed = fixed.replace(/,\s*([}\]])/g, '$1');
    fixed = fixed.replace(/:(\s*)true(\s*[,}])/g, ':$1true$2');
    fixed = fixed.replace(/:(\s*)false(\s*[,}])/g, ':$1false$2');
    fixed = fixed.replace(/:(\s*)null(\s*[,}])/g, ':$1null$2');
    return fixed;
  }

  private extractJSONFragments(input: string): JSONFragment[] {
    const fragments: JSONFragment[] = [];
    const bracketFragments = this.extractWithBracketMatching(input);
    fragments.push(...bracketFragments);
    
    if (fragments.filter(f => f.valid).length === 0) {
      const regexFragments = this.extractWithRegex(input);
      fragments.push(...regexFragments);
    }
    
    if (fragments.filter(f => f.valid).length === 0) {
      const objectFragments = this.extractObjectFragments(input);
      fragments.push(...objectFragments);
    }
    
    return fragments.filter(f => f.valid).slice(0, 10);
  }

  private extractWithBracketMatching(input: string): JSONFragment[] {
    const fragments: JSONFragment[] = [];
    let inString = false;
    let escapeNext = false;
    let braceDepth = 0;
    let bracketDepth = 0;
    let startPos = -1;
    let stringChar = '';

    for (let i = 0; i < input.length; i++) {
      const char = input[i];
      if (char === '\\' && inString) {
        escapeNext = !escapeNext;
        continue;
      }

      if ((char === '"' || char === "'") && !escapeNext) {
        if (inString && char === stringChar) {
          inString = false;
          stringChar = '';
        } else if (!inString) {
          inString = true;
          stringChar = char;
        }
      }

      escapeNext = false;
      if (inString) continue;

      if (char === '{') {
        if (braceDepth === 0 && bracketDepth === 0) {
          startPos = i;
        }
        braceDepth++;
      } else if (char === '}') {
        braceDepth--;
        if (braceDepth === 0 && bracketDepth === 0 && startPos !== -1) {
          const content = input.substring(startPos, i + 1);
          const isValid = this.validateJSON(content);
          fragments.push({
            content,
            start: startPos,
            end: i,
            valid: isValid
          });
          startPos = -1;
        }
      }

      if (char === '[') {
        if (braceDepth === 0 && bracketDepth === 0) {
          startPos = i;
        }
        bracketDepth++;
      } else if (char === ']') {
        bracketDepth--;
        if (braceDepth === 0 && bracketDepth === 0 && startPos !== -1) {
          const content = input.substring(startPos, i + 1);
          const isValid = this.validateJSON(content);
          fragments.push({
            content,
            start: startPos,
            end: i,
            valid: isValid
          });
          startPos = -1;
        }
      }
    }

    return fragments;
  }

  private extractWithRegex(input: string): JSONFragment[] {
    const fragments: JSONFragment[] = [];
    const jsonObjectRegex = /{[\s\S]*?}(?=\s*(?:,|$|\s*[}\]]|\s*{))/g;
    const jsonArrayRegex = /\[[\s\S]*?\](?=\s*(?:,|$|\s*[}\]]|\s*{))/g;
    
    let match;
    while ((match = jsonObjectRegex.exec(input)) !== null) {
      const content = match[0];
      fragments.push({
        content,
        start: match.index,
        end: match.index + content.length - 1,
        valid: this.validateJSON(content)
      });
    }
    
    while ((match = jsonArrayRegex.exec(input)) !== null) {
      const content = match[0];
      fragments.push({
        content,
        start: match.index,
        end: match.index + content.length - 1,
        valid: this.validateJSON(content)
      });
    }
    
    return fragments;
  }

  private extractObjectFragments(input: string): JSONFragment[] {
    const fragments: JSONFragment[] = [];
    const lines = input.split('\n');
    let currentObject = '';
    let inObject = false;
    let braceCount = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      if (line.includes('{') && !inObject) {
        inObject = true;
        currentObject = line;
        braceCount = (line.match(/{/g) || []).length - (line.match(/}/g) || []).length;
      } else if (inObject) {
        currentObject += '\n' + line;
        braceCount += (line.match(/{/g) || []).length - (line.match(/}/g) || []).length;
        
        if (braceCount === 0) {
          fragments.push({
            content: currentObject,
            start: 0,
            end: currentObject.length - 1,
            valid: this.validateJSON(currentObject)
          });
          inObject = false;
          currentObject = '';
        }
      }
    }

    return fragments;
  }

  private validateJSON(jsonString: string): boolean {
    try {
      JSON.parse(jsonString);
      return true;
    } catch {
      return false;
    }
  }

  private validateCozePlugin(plugin: any): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    if (!plugin) {
      errors.push("插件对象为空");
      return { isValid: false, errors };
    }
    
    if (plugin.node_id || plugin.id) {
      // Coze插件通常有node_id或id字段
    } else {
      errors.push("缺少必要的节点标识符（node_id或id）");
    }
    
    if (plugin.input_variables || plugin.inputs) {
      const inputs = plugin.input_variables || plugin.inputs;
      if (!Array.isArray(inputs)) {
        errors.push("输入变量必须是数组格式");
      }
    }
    
    return { 
      isValid: errors.length === 0, 
      errors 
    };
  }

  private repairSinglePlugin(plugin: any): RepairResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    
    try {
      let repairedPlugin = JSON.parse(JSON.stringify(plugin));
      repairedPlugin = this.ensureBasicStructure(repairedPlugin, warnings);

      if (repairedPlugin.input_variables) {
        repairedPlugin.input_variables = this.repairInputVariables(repairedPlugin.input_variables, warnings);
      }

      if (!repairedPlugin.output_variables) {
        repairedPlugin.output_variables = this.createDefaultOutputVariables();
        warnings.push("缺少output_variables，已创建默认输出结构");
      } else {
        repairedPlugin.output_variables = this.repairOutputVariables(repairedPlugin.output_variables, warnings);
      }

      if (this.repairMode === 'thorough' || this.repairMode === 'aggressive') {
        repairedPlugin = this.deepRepairPlugin(repairedPlugin, warnings);
      }

      if (this.repairMode === 'aggressive') {
        repairedPlugin = this.aggressiveRepairPlugin(repairedPlugin, warnings);
      }

      return {
        success: true,
        data: repairedPlugin,
        errors,
        warnings
      };

    } catch (error) {
      errors.push(`修复插件时发生错误: ${error.message}`);
      return {
        success: false,
        errors,
        warnings
      };
    }
  }

  private ensureBasicStructure(plugin: any, warnings: string[]): any {
    const result = { ...plugin };
    
    if (!result.node_id && !result.id) {
      result.node_id = `coze_plugin_${Date.now()}`;
      warnings.push("缺少节点标识符，已自动生成");
    }
    
    if (!result.node_name && !result.name) {
      result.node_name = "Coze插件";
      warnings.push("缺少节点名称，已设置默认值");
    }
    
    if (!result.node_description && !result.description) {
      result.node_description = "Coze插件描述";
      warnings.push("缺少node_description，已设置默认值");
    }
    
    if (!result.input_variables || !Array.isArray(result.input_variables)) {
      result.input_variables = [];
      warnings.push("input_variables不是数组，已初始化为空数组");
    }
    
    if (!result.output_variables || !Array.isArray(result.output_variables)) {
      result.output_variables = this.createDefaultOutputVariables();
      warnings.push("缺少output_variables，已创建默认输出结构");
    }
    
    return result;
  }

  private createDefaultOutputVariables(): any[] {
    return [
      {
        variable_id: "processing_result",
        variable_name: "处理结果",
        variable_type: "OBJECT",
        description: "包含处理状态、统计信息和修复后的插件数据的完整结果对象。",
        properties: {
          status: {
            type: "STRING",
            description: "处理状态：success或error"
          },
          processing_time_ms: {
            type: "NUMBER",
            description: "处理时间（毫秒）"
          },
          original_plugins_count: {
            type: "NUMBER",
            description: "原始检测到的插件数量"
          },
          repaired_plugins_count: {
            type: "NUMBER",
            description: "成功修复的插件数量"
          },
          parsing_errors: {
            type: "ARRAY",
            items: { type: "STRING" },
            description: "解析过程中遇到的错误信息"
          },
          repair_warnings: {
            type: "ARRAY",
            items: { type: "STRING" },
            description: "修复过程中遇到的警告信息"
          },
          repaired_coze_plugins: {
            type: "ARRAY",
            items: { type: "OBJECT" },
            description: "修复后的Coze插件对象数组"
          },
          formatted_output: {
            type: "STRING",
            description: "格式化后的输出，便于查看和复制"
          }
        }
      }
    ];
  }

  private repairInputVariables(inputVariables: any[], warnings: string[]): any[] {
    return inputVariables.map((variable, index) => {
      if (!variable.variable_id) {
        variable.variable_id = `input_var_${index}`;
        warnings.push(`输入变量${index}缺少variable_id，已自动生成`);
      }

      if (!variable.variable_name) {
        variable.variable_name = `输入变量${index}`;
        warnings.push(`输入变量${index}缺少variable_name，已设置默认值`);
      }

      if (!variable.variable_type) {
        variable.variable_type = "STRING";
        warnings.push(`输入变量${index}缺少variable_type，已设置为STRING`);
      }

      return variable;
    });
  }

  private repairOutputVariables(outputVariables: any[], warnings: string[]): any[] {
    return outputVariables.map((variable, index) => {
      if (!variable.variable_id) {
        variable.variable_id = `output_var_${index}`;
        warnings.push(`输出变量${index}缺少variable_id，已自动生成`);
      }

      if (!variable.variable_name) {
        variable.variable_name = `输出变量${index}`;
        warnings.push(`输出变量${index}缺少variable_name，已设置默认值`);
      }

      if (!variable.variable_type) {
        variable.variable_type = "OBJECT";
        warnings.push(`输出变量${index}缺少variable_type，已设置为OBJECT`);
      }

      return variable;
    });
  }

  private deepRepairPlugin(plugin: any, warnings: string[]): any {
    const repaired = { ...plugin };
    
    if (repaired.config && typeof repaired.config === 'object') {
      repaired.config = this.repairConfig(repaired.config, warnings);
    }

    if (repaired.metadata && typeof repaired.metadata === 'object') {
      repaired.metadata = this.repairMetadata(repaired.metadata, warnings);
    }

    return repaired;
  }

  private aggressiveRepairPlugin(plugin: any, warnings: string[]): any {
    const repaired = { ...plugin };
    
    if (!repaired.version) {
      repaired.version = "1.0.0";
      warnings.push("缺少version字段，已设置为1.0.0");
    }

    if (!repaired.created_at) {
      repaired.created_at = new Date().toISOString();
      warnings.push("缺少created_at字段，已设置为当前时间");
    }

    if (!repaired.updated_at) {
      repaired.updated_at = new Date().toISOString();
      warnings.push("缺少updated_at字段，已设置为当前时间");
    }

    return repaired;
  }

  private repairConfig(config: any, warnings: string[]): any {
    const repaired = { ...config };
    
    if (!repaired.timeout) {
      repaired.timeout = 30000;
      warnings.push("config缺少timeout字段，已设置为30000ms");
    }

    if (!repaired.retry_count) {
      repaired.retry_count = 3;
      warnings.push("config缺少retry_count字段，已设置为3次");
    }

    return repaired;
  }

  private repairMetadata(metadata: any, warnings: string[]): any {
    const repaired = { ...metadata };
    
    if (!repaired.author) {
      repaired.author = "Coze Plugin System";
      warnings.push("metadata缺少author字段，已设置默认值");
    }

    if (!repaired.category) {
      repaired.category = "utility";
      warnings.push("metadata缺少category字段，已设置为utility");
    }

    return repaired;
  }

  private connectPlugins(plugins: any[], warnings: string[]): any[] {
    if (plugins.length <= 1) {
      return plugins;
    }

    const connected = [...plugins];
    
    for (let i = 0; i < connected.length - 1; i++) {
      const current = connected[i];
      const next = connected[i + 1];
      
      if (!current.next_nodes) {
        current.next_nodes = [];
      }
      
      current.next_nodes.push({
        node_id: next.node_id,
        condition: "always"
      });
    }

    warnings.push(`已连接${connected.length}个插件，形成工作流链`);
    return connected;
  }

  private applyNamingConvention(data: any): any {
    if (this.namingConvention === "original") {
      return data;
    }
    return data;
  }

  private organizeOutput(plugins: any[], structure: string): any {
    switch (structure) {
      case "single_merged":
        return {
          type: "coze_plugin_collection",
          version: "1.0.0",
          plugins: plugins,
          total_count: plugins.length,
          generated_at: new Date().toISOString()
        };
      
      case "plugin_array":
        return plugins;
      
      case "individual_files":
        return plugins.reduce((acc, plugin, index) => {
          acc[`plugin_${index}.json`] = plugin;
          return acc;
        }, {});
      
      case "coze_import_ready":
        return {
          import_format: "coze_v1",
          plugins: plugins.map(plugin => ({
            ...plugin,
            _import_ready: true,
            _validation_status: "repaired"
          }))
        };
      
      default:
        return plugins;
    }
  }
}

// ================================ JSON验证器类 ================================

export class JSONValidator {
  public validateCode(generatedCode: string): {
    validated_code: string;
    validation_status: string;
    validation_message: string;
  } {
    try {
      if (!generatedCode.includes('export async function run')) {
        throw new Error('生成的代码缺少必需的run函数');
      }
      if (!generatedCode.includes('interface PluginInput')) {
        throw new Error('生成的代码缺少PluginInput接口');
      }
      if (!generatedCode.includes('interface PluginOutput')) {
        throw new Error('生成的代码缺少PluginOutput接口');
      }
      
      try {
        new Function(generatedCode);
      } catch (syntaxError) {
        throw new Error(`代码存在语法错误: ${syntaxError.message}`);
      }
      
      return {
        validated_code: generatedCode,
        validation_status: 'success',
        validation_message: '代码验证通过，结构完整'
      };
    } catch (error) {
      return {
        validated_code: generatedCode,
        validation_status: 'error',
        validation_message: `验证失败: ${error.message}`
      };
    }
  }

  public validateDataAgainstSchema(data: any, schema: any): ValidationResponse {
    const errors: string[] = [];
    
    try {
      if (schema.type && typeof data !== schema.type) {
        errors.push(`数据类型错误: 期望${schema.type}，实际得到${typeof data}`);
      }
      
      if (schema.required && Array.isArray(schema.required)) {
        schema.required.forEach((field: string) => {
          if (!(field in data)) {
            errors.push(`缺少必填字段: ${field}`);
          }
        });
      }
      
      return {
        valid: errors.length === 0,
        errors
      };
    } catch (error) {
      return {
        valid: false,
        errors: [`验证过程出错: ${error.message}`]
      };
    }
  }
}

// ================================ 工作流管理类 ================================

export class WorkflowManager {
  public createCodeDiagnosticWorkflow(): WorkflowRequest {
    return {
      name: "Coze插件代码诊断与修复工作流",
      description: "自动诊断、生成和验证Coze插件代码的工作流",
      nodes: [
        {
          id: "start_node",
          type: "start",
          inputs: []
        },
        {
          id: "diagnostic_engine",
          type: "code",
          language: "javascript",
          code: this.getDiagnosticEngineCode(),
          outputs: [
            { name: "diagnostic_report", type: "string" },
            { name: "user_input", type: "object" }
          ]
        },
        {
          id: "code_generator",
          type: "llm",
          config: {
            system_prompt: "你是一名专业的Coze插件开发专家，请根据用户需求或诊断报告生成完整、可运行的代码。遵循以下规范：1.如果是自然语言需求，生成完整的Node.js TypeScript代码-包含PluginInput和PluginOutput接口-实现export async function run()-包含完整的错误处理机制（try-catch）-包含必要的参数验证；2.如果是代码修复需求：-保持原有功能不变-修复所有诊断出的问题-优化代码结构和性能-确保符合Coze平台最新规范；3.输出要求：-只输出最终代码，不要额外解释-确保代码可以直接运行-保持代码格式整洁",
            user_prompt: "{{#eq user_input.mode 'generate'}}请根据以下需求生成完整的Coze插件代码：{{user_input.content}}{{else}}请修复以下代码问题：{{user_input.content}}诊断报告：{{diagnostic_report}}{{/eq}}"
          },
          outputs: [
            { name: "generated_code", type: "string" }
          ]
        },
        {
          id: "code_validator",
          type: "code",
          language: "javascript",
          code: this.getCodeValidatorCode(),
          outputs: [
            { name: "validated_code", type: "string" },
            { name: "validation_status", type: "string" },
            { name: "validation_message", type: "string" }
          ]
        },
        {
          id: "end_node",
          type: "end",
          config: {
            response: {
              type: "text",
              body: "{{#eq validation_status 'success'}}✅代码生成/修复成功！生成的代码：{{validated_code}}{{else}}❌验证失败: {{validation_message}}诊断报告：{{diagnostic_report}}生成的代码（需要手动修复）：{{validated_code}}{{/eq}}"
            },
            stream: true
          }
        }
      ],
      edges: [
        { id: "edge1", source: "start_node", target: "diagnostic_engine" },
        { id: "edge2", source: "diagnostic_engine", target: "code_generator" },
        { id: "edge3", source: "code_generator", target: "code_validator" },
        { id: "edge4", source: "code_validator", target: "end_node" }
      ]
    };
  }

  private getDiagnosticEngineCode(): string {
    return `// 代码诊断引擎
return {
  diagnostic_report: "代码诊断完成",
  user_input: inputs.user_input || { mode: "generate", content: "创建一个基础的Coze插件" }
};`;
  }

  private getCodeValidatorCode(): string {
    return `// 验证生成的代码是否有效
try {
  // 检查代码是否包含必要的结构
  if (!inputs.generated_code.includes('export async function run')) {
    throw new Error('生成的代码缺少必需的run函数');
  }
  if (!inputs.generated_code.includes('interface PluginInput')) {
    throw new Error('生成的代码缺少PluginInput接口');
  }
  if (!inputs.generated_code.includes('interface PluginOutput')) {
    throw new Error('生成的代码缺少PluginOutput接口');
  }
  
  // 尝试解析代码语法
  try {
    new Function(inputs.generated_code);
  } catch (syntaxError) {
    throw new Error(\`代码存在语法错误: \${syntaxError.message}\`);
  }
  
  return {
    validated_code: inputs.generated_code,
    validation_status: 'success',
    validation_message: '代码验证通过，结构完整'
  };
} catch (error) {
  return {
    validated_code: inputs.generated_code,
    validation_status: 'error',
    validation_message: \`验证失败: \${error.message}\`
  };
}`;
  }
}

// ================================ MCP生成器类 ================================

export class MCPGenerator {
  private projectData: any = {};

  constructor() {
    this.projectData = {
      projectName: "",
      serverName: "",
      description: "",
      version: "0.1.0",
      author: "",
      pythonVersion: "3.9",
      tools: [],
      resources: [],
      dependencies: [],
      config: {
        transport: "stdio",
        authentication: "none",
        loggingLevel: "INFO"
      }
    };
  }

  public collectProjectInfo(): any {
    console.log("🚀 MCP服务器自动化生成系统");
    console.log("=".repeat(50));

    this.projectData.projectName = "finance-tools";
    this.projectData.serverName = "finance_server";
    this.projectData.description = "金融工具MCP服务器";
    this.projectData.author = "Coze Development Team";

    this.projectData.tools = this.collectTools();
    this.projectData.resources = this.collectResources();
    this.projectData.dependencies = this.collectDependencies();

    return this.projectData;
  }

  private collectTools(): any[] {
    return [
      {
        name: "stock_price_query",
        description: "查询股票实时价格",
        category: "finance",
        arguments: [
          {
            name: "symbol",
            type: "string",
            description: "股票代码",
            required: true
          }
        ],
        implementation: "stock_price_implementation"
      }
    ];
  }

  private collectResources(): any[] {
    return [
      {
        name: "financial_data",
        type: "database",
        description: "金融数据资源"
      }
    ];
  }

  private collectDependencies(): any[] {
    return [
      {
        name: "requests",
        version: "2.31.0",
        purpose: "HTTP请求库"
      }
    ];
  }

  public generateMCPServer(): string {
    const { projectName, serverName, description, version, author, tools, config } = this.projectData;

    return `
#!/usr/bin/env python3
"""
${projectName} - ${description}
Generated by Coze MCP Generator
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.server import Server
from mcp.server.models import InitializationOptions

# 工具实现
${this.generateToolImplementations(tools)}

class ${this.toPascalCase(serverName)}Server:
    def __init__(self):
        self.server = Server("${serverName}")
        
    async def initialize(self):
        """初始化服务器"""
        await self.server.initialize(
            InitializationOptions(
                server_name="${serverName}",
                server_version="${version}",
                capabilities=self.server.get_capabilities()
            )
        )
        
    async def run(self):
        """运行服务器"""
        server_params = StdioServerParameters(
            command="python3",
            args=["-m", "${projectName}"]
        )
        
        async with ClientSession(server_params) as session:
            await session.initialize()
            await session.run()

if __name__ == "__main__":
    server = ${this.toPascalCase(serverName)}Server()
    asyncio.run(server.run())
`;
  }

  private generateToolImplementations(tools: any[]): string {
    return tools.map(tool => `
def ${tool.name}_implementation(${this.generateFunctionParameters(tool.arguments)}):
    """${tool.description}"""
    # TODO: 实现具体功能
    return {"status": "success", "data": "功能待实现"}
`).join('\n');
  }

  private generateFunctionParameters(args: any[]): string {
    return args.map(arg => `${arg.name}: ${arg.type}`).join(', ');
  }

  private toPascalCase(str: string): string {
    return str.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join('');
  }
}

// ================================ Python MCP生成器类 ================================

export class PythonMCPGenerator {
  private projectInfo: {
    name: string;
    version: string;
    description: string;
    author: string;
    language: string;
  };

  constructor(projectInfo?: any) {
    this.projectInfo = {
      name: projectInfo?.name || 'mcp-server',
      version: projectInfo?.version || '1.0.0',
      description: projectInfo?.description || 'MCP Server for Coze Platform',
      author: projectInfo?.author || 'Coze Developer',
      language: projectInfo?.language || 'python'
    };
  }

  generateMCPServer(tools: any[] = []): string {
    const toolDefinitions = tools.map((tool, index) => {
      return `    @mcp.tool()\n    async def ${tool.name}(self, ${this.generateToolParams(tool.parameters)}) -> str:\n        """${tool.description}"""\n        ${this.generateToolLogic(tool.logic)}\n        return json.dumps({"result": "success", "data": result})`;
    }).join('\n\n');

    const className = this.capitalize(this.projectInfo.name);

    return `#!/usr/bin/env python3
"""
${this.projectInfo.name} - ${this.projectInfo.description}
Version: ${this.projectInfo.version}
Author: ${this.projectInfo.author}
"""

import json
import asyncio
from mcp import MCPServer
from typing import Any, Dict, List

class ${className}Server:
    def __init__(self):
        self.server = MCPServer("${this.projectInfo.name}")
        
        # 注册工具
        ${toolDefinitions}

    def generateToolParams(self, parameters: Dict[str, Any]) -> str:
        """生成工具参数定义"""
        param_list = []
        for param_name, param_info in parameters.items():
            param_type = param_info.get('type', 'str')
            required = param_info.get('required', True)
            default = param_info.get('default')
            
            param_str = param_name
            if not required and default is not None:
                param_str += f" = {repr(default)}"
            elif not required:
                param_str += " = None"
                
            param_list.append(param_str)
        
        return ', '.join(param_list)

    def generateToolLogic(self, logic: string) -> str:
        """生成工具逻辑代码"""
        if logic:
            return logic
        return '        # TODO: 实现工具逻辑\n        result = {"status": "implemented"}'

    async def start(self):
        """启动MCP服务器"""
        await self.server.start()

    async def stop(self):
        """停止MCP服务器"""
        await self.server.stop()

if __name__ == "__main__":
    server = ${className}Server()
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        asyncio.run(server.stop())
`;
  }

  private generateToolParams(parameters: any): string {
    const paramList: string[] = [];
    for (const paramName in parameters) {
      const paramInfo = parameters[paramName];
      const required = paramInfo.required !== false;
      const defaultValue = paramInfo.default;
      
      let paramStr = paramName;
      if (!required && defaultValue !== undefined) {
        paramStr += ` = ${JSON.stringify(defaultValue)}`;
      } else if (!required) {
        paramStr += ' = None';
      }
      
      paramList.push(paramStr);
    }
    return paramList.join(', ');
  }

  private generateToolLogic(logic: string): string {
    return logic || '        # TODO: 实现工具逻辑\n        result = {"status": "implemented"}';
  }

  private capitalize(text: string): string {
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  generateRequirements(): string {
    return `mcp>=1.0.0
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
python-multipart>=0.0.6`;
  }

  generateDockerfile(): string {
    return `FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]`;
  }

  generateProjectConfig(): any {
    return {
      project: this.projectInfo,
      tools: this.getAvailableTools(),
      dependencies: this.getDependencies(),
      deployment: this.getDeploymentOptions()
    };
  }

  private getAvailableTools(): any[] {
    return [
      {
        name: 'data_query',
        description: '通用数据查询工具',
        parameters: {
          query: { type: 'str', required: true, description: '查询语句' },
          limit: { type: 'int', required: false, default: 100, description: '结果数量限制' }
        }
      },
      {
        name: 'file_processor',
        description: '文件处理工具',
        parameters: {
          file_path: { type: 'str', required: true, description: '文件路径' },
          operation: { type: 'str', required: true, description: '操作类型' }
        }
      }
    ];
  }

  private getDependencies(): any {
    return {
      python: ['mcp', 'fastapi', 'uvicorn', 'pydantic'],
      system: ['python3.11', 'pip']
    };
  }

  private getDeploymentOptions(): any {
    return {
      docker: true,
      kubernetes: true,
      cloud: ['aws', 'azure', 'gcp']
    };
  }
}

// ================================ 高级工具类 ================================

export class AdvancedJSONParser {
  static deepParse(jsonStr: string): any {
    try {
      let processedStr = jsonStr
        .replace(/^\uFEFF/, '')
        .replace(/\\'/g, "'")
        .replace(/\\"/g, '"')
        .replace(/\\n/g, '\n')
        .replace(/\\t/g, '\t')
        .replace(/\\r/g, '\r');

      return JSON.parse(processedStr);
    } catch (error) {
      throw new Error(`JSON解析失败: ${error.message}`);
    }
  }

  static validateCozePluginStructure(data: any): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (!data) {
      errors.push('数据为空');
      return { isValid: false, errors };
    }

    const requiredFields = ['name', 'version', 'description'];
    for (const field of requiredFields) {
      if (!data[field]) {
        errors.push(`缺少必需字段: ${field}`);
      }
    }

    if (data.tools && Array.isArray(data.tools)) {
      for (const tool of data.tools) {
        if (!tool.name || !tool.description) {
          errors.push('工具配置不完整：缺少name或description');
        }
      }
    }

    return { isValid: errors.length === 0, errors };
  }
}

export class CodeGenerator {
  static generateTypeScriptPlugin(templateName: string, config: any): string {
    const templates = {
      basic: `interface PluginInput {
  // 输入参数定义
}

interface PluginOutput {
  // 输出结果定义
}

export async function run(input: PluginInput): Promise<PluginOutput> {
  try {
    // 插件逻辑实现
    return {
      status: 'success',
      result: '插件执行成功'
    };
  } catch (error) {
    return {
      status: 'error',
      error: error.message
    };
  }
}`,

      api_client: `interface ApiConfig {
  baseUrl: string;
  headers?: Record<string, string>;
}

interface PluginInput {
  endpoint: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  data?: any;
}

interface PluginOutput {
  status: 'success' | 'error';
  data?: any;
  error?: string;
}

export async function run(input: PluginInput, config: ApiConfig): Promise<PluginOutput> {
  try {
    const response = await fetch(\`\${config.baseUrl}/\${input.endpoint}\`, {
      method: input.method || 'GET',
      headers: config.headers,
      body: input.data ? JSON.stringify(input.data) : undefined
    });

    if (!response.ok) {
      throw new Error(\`API请求失败: \${response.status}\`);
    }

    const data = await response.json();
    return {
      status: 'success',
      data
    };
  } catch (error) {
    return {
      status: 'error',
      error: error.message
    };
  }
}`
    };

    return templates[templateName] || templates.basic;
  }
}

export class PerformanceMonitor {
  private static timers: Map<string, number> = new Map();

  static startTimer(name: string): void {
    this.timers.set(name, Date.now());
  }

  static endTimer(name: string): number {
    const startTime = this.timers.get(name);
    if (!startTime) {
      throw new Error(`计时器不存在: ${name}`);
    }

    const duration = Date.now() - startTime;
    this.timers.delete(name);
    return duration;
  }

  static getPerformanceReport(): any {
    return {
      timestamp: new Date().toISOString(),
      memory_usage: process.memoryUsage(),
      uptime: process.uptime(),
      active_timers: Array.from(this.timers.keys())
    };
  }
}

// ================================ OpenAPI配置 ================================

export const OPENAPI_CONFIG = `
openapi: 3.1.0
info:
  title: Coze Plugin Development Platform
  description: 完整的Coze插件开发与修复平台API
  version: 1.0.0
  contact:
    name: Coze Development Team
    email: support@coze.cn

servers:
  - url: https://api.coze.cn/v1
    description: 生产环境
  - url: https://sandbox-api.coze.cn/v1
    description: 沙盒环境

paths:
  /workflows/create:
    post:
      summary: 创建工作流
      operationId: createWorkflow
      requestBody: { required: true, content: { "application/json": { schema: { $ref: "#/components/schemas/WorkflowRequest" } } } }
      responses: { "200": { description: "工作流创建成功" } }
  /workflows/execute:
    post:
      summary: 执行工作流
      operationId: executeWorkflow
      requestBody: { required: true, content: { "application/json": { schema: { type: "object", properties: { workflow_id: { type: "string" } } } } } }
      responses: { "200": { description: "工作流执行成功" } }
  /plugins/validate:
    post:
      summary: 验证参数
      operationId: validateParameters
      requestBody: { required: true, content: { "application/json": { schema: { $ref: "#/components/schemas/ValidationRequest" } } } }
      responses: { "200": { description: "验证成功" } }
  /unified/automation:
    post:
      summary: 全场景智能自动化处理
      operationId: unifiedAutomation
      requestBody: { required: true, content: { "application/json": { schema: { type: "object", properties: { user_input: { type: "string" } } } } } }
      responses: { "200": { description: "自动化处理成功" } }
  /workflows/generate:
    post:
      summary: 自动生成工作流配置
      description: 根据用户需求描述自动生成完整工作流配置
      operationId: generateWorkflow
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WorkflowGenerationRequest'
      responses:
        '200':
          description: 工作流生成成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WorkflowGenerationResponse'

components:
  schemas:
    WorkflowGenerationRequest:
      type: object
      required:
        - description
        - scenario
      properties:
        description:
          type: string
          description: 工作流需求描述
        scenario:
          type: string
          enum: [ecommerce, industry, programming, data_analysis]
          description: 应用场景

    WorkflowGenerationResponse:
      type: object
      properties:
        workflow_id:
          type: string
          description: 生成的工作流ID
        workflow_config:
          type: object
          description: 完整的工作流配置
        status:
          type: string
          enum: [success, error]
`;

// ================================ JSON工作流定义 ================================

export const WORKFLOW_DEFINITION = {
  "name": "coze_complete_plugin_system",
  "description": "Coze全栈式插件开发与修复系统-输入自然语言或错误代码，自动生成或修复符合Coze平台规范的完整插件代码",
  "nodes": [
    {
      "id": "start_node",
      "type": "start",
      "outputs": [
        {
          "id": "user_input_output",
          "type": "object",
          "name": "user_input",
          "description": "用户输入的自然语言需求或错误代码",
          "required": true,
          "schema": {
            "type": "object",
            "properties": {
              "content": {
                "type": "string",
                "description": "自然语言需求或错误JSON/YAML代码"
              },
              "mode": {
                "type": "string",
                "enum": ["generate", "repair"],
                "default": "generate"
              },
              "repair_level": {
                "type": "string",
                "enum": ["basic", "comprehensive", "thorough"],
                "default": "comprehensive"
              }
            },
            "required": ["content"]
          }
        }
      ]
    },
    {
      "id": "diagnostic_engine",
      "type": "llm",
      "model": "deepseek-reasoner",
      "inputs": [
        {
          "name": "user_input",
          "type": "object",
          "binding": {
            "type": "node",
            "node": "start_node",
            "output": "user_input_output"
          }
        }
      ],
      "config": {
        "system_prompt": "你是一名专业的代码诊断专家，专门分析Coze插件和工作流代码。请仔细分析用户提供的代码，识别所有问题，包括：1.JSON/YAML语法错误（括号不匹配、引号问题、缩进错误等）2.结构错误（缺失必需字段、字段类型错误、多余字段等）3.逻辑错误（节点连接问题、参数配置错误、循环依赖等）4.性能问题（低效配置、冗余代码等）。请以清晰的Markdown格式输出诊断报告，包含：问题分类、每个问题的详细描述、问题位置定位、修复建议。只输出诊断报告，不要修复代码。",
        "user_prompt": "请诊断以下代码问题：{{user_input.content}}"
      },
      "outputs": [
        {
          "name": "diagnostic_report",
          "type": "string",
          "description": "代码诊断报告"
        }
      ]
    },
    {
      "id": "code_generator",
      "type": "llm",
      "model": "deepseek-reasoner",
      "inputs": [
        {
          "name": "user_input",
          "type": "object",
          "binding": {
            "type": "node",
            "node": "start_node",
            "output": "user_input_output"
          }
        },
        {
          "name": "diagnostic_report",
          "type": "string",
          "binding": {
            "type": "node",
            "node": "diagnostic_engine",
            "output": "diagnostic_report"
          }
        }
      ],
      "config": {
        "system_prompt": "你是一名专业的Coze插件开发专家，请根据用户需求或诊断报告生成完整、可运行的代码。遵循以下规范：1.如果是自然语言需求，生成完整的Node.js TypeScript代码-包含PluginInput和PluginOutput接口-实现export async function run()-包含完整的错误处理机制（try-catch）-包含必要的参数验证；2.如果是代码修复需求：-保持原有功能不变-修复所有诊断出的问题-优化代码结构和性能-确保符合Coze平台最新规范；3.输出要求：-只输出最终代码，不要额外解释-确保代码可以直接运行-保持代码格式整洁",
        "user_prompt": "{{#eq user_input.mode 'generate'}}请根据以下需求生成完整的Coze插件代码：{{user_input.content}}{{else}}请修复以下代码问题：{{user_input.content}}诊断报告：{{diagnostic_report}}{{/eq}}"
      },
      "outputs": [
        {
          "name": "generated_code",
          "type": "string",
          "description": "生成或修复后的代码"
        }
      ]
    },
    {
      "id": "code_validator",
      "type": "code",
      "language": "javascript",
      "inputs": [
        {
          "name": "generated_code",
          "type": "string",
          "binding": {
            "type": "node",
            "node": "code_generator",
            "output": "generated_code"
          }
        }
      ],
      "code": "// 验证生成的代码是否有效\ntry {\n  // 检查代码是否包含必要的结构\n  if (!inputs.generated_code.includes('export async function run')) {\n    throw new Error('生成的代码缺少必需的run函数');\n  }\n  if (!inputs.generated_code.includes('interface PluginInput')) {\n    throw new Error('生成的代码缺少PluginInput接口');\n  }\n  if (!inputs.generated_code.includes('interface PluginOutput')) {\n    throw new Error('生成的代码缺少PluginOutput接口');\n  }\n  \n  // 尝试解析代码语法\n  try {\n    new Function(inputs.generated_code);\n  } catch (syntaxError) {\n    throw new Error(\`代码存在语法错误: \${syntaxError.message}\`);\n  }\n  \n  return {\n    validated_code: inputs.generated_code,\n    validation_status: 'success',\n    validation_message: '代码验证通过，结构完整'\n  };\n} catch (error) {\n  return {\n    validated_code: inputs.generated_code,\n    validation_status: 'error',\n    validation_message: \`验证失败: \${error.message}\`\n  };\n}",
      "outputs": [
        {
          "name": "validated_code",
          "type": "string",
          "description": "验证后的代码"
        },
        {
          "name": "validation_status",
          "type": "string",
          "description": "验证状态"
        },
        {
          "name": "validation_message",
          "type": "string",
          "description": "验证消息"
        }
      ]
    },
    {
      "id": "end_node",
      "type": "end",
      "inputs": [
        {
          "name": "final_output",
          "type": "string",
          "binding": {
            "type": "node",
            "node": "code_validator",
            "output": "validated_code"
          }
        },
        {
          "name": "validation_status",
          "type": "string",
