# AI 节点：llm / agent

## LLM 节点

`type: llm`；调用大语言模型生成文本。

```yaml
data:
  context:
    enabled: false
    variable_selector: []
  desc: ''
  memory:
    enabled: false
    window:
      enabled: false
      size: 50
  model:
    mode: chat
    name: gpt-4o
    provider: langgenius/openai/openai
  prompt_template:
  - role: system
    text: 你是一个助手。
  - role: user
    text: '{{#start.query#}}'
  retry_config:
    enabled: false
    max_retries: 1
    retry_interval: 1000
    exponential_backoff:
      enabled: false
      multiplier: 2
      max_interval: 10000
  structured_output:
    enabled: false
  title: LLM
  type: llm
  vision:
    enabled: false
    configs:
      variable_selector: []
```

输出变量：`text`（`value_selector: [llm_node, text]`）；模板引用：`{{#llm_node.text#}}`。

`memory.enabled: true` 时节点会读取对话历史（仅 advanced-chat 模式）。

---

## Agent 节点

`type: agent`；调用插件提供的 Agent 策略执行多轮 tool-use 任务。

`agent_strategy_provider_name` 格式为 `<author>/<plugin>/<provider>`，`agent_strategy_name` 为策略名称。

### Function Calling 策略（内置）

```yaml
data:
  agent_parameters:
    model:
      type: constant
      value:
        completion_params: {}
        mode: chat
        model: gpt-4o            # 与 name 保持一致
        model_type: llm
        name: gpt-4o
        provider: langgenius/openai/openai
        type: model-selector
    tools:
      type: constant
      value:
        - enabled: true          # 必须有 enabled: true
          provider_id: <provider_id>
          provider_name: <provider_name>
          provider_type: builtin
          tool_label: <label>
          tool_name: <tool_name>
          tool_parameters: {}
    query:
      type: constant
      value: '{{#start.query#}}'  # agent 节点用模板语法，不用 type: variable
    max_iterations:
      type: constant
      value: 5
    instruction:
      type: constant
      value: '你是一个助手。'
  agent_strategy_label: Function Calling
  agent_strategy_name: function_calling
  agent_strategy_provider_name: langgenius/agent/agent   # 注意：不是 agent_strategies
  output_schema: {}
  title: Agent
  tool_node_version: '2'
  type: agent
```

**注意事项：**
- `model.value` 必须包含 `completion_params`、`model`（同 `name`）、`model_type: llm`、`type: model-selector`，否则 UI 显示"未选择模型"
- `query` 使用 `type: constant` + 模板语法 `{{#node_id.field#}}`，不能用 `type: variable` 的列表选择器
- 每个 tool 必须包含 `enabled: true`
- `agent_strategy_provider_name` 固定为 `langgenius/agent/agent`（Dify 官方 Agent 策略插件）
- 输出变量：`text`（`value_selector: [agent_node, text]`）；模板引用：`{{#agent_node.text#}}`

### MCP SSE Agent 策略（需安装 junjiem/mcp_see_agent 插件）

支持通过 MCP 协议调用外部工具服务。

```yaml
data:
  agent_parameters:
    model:
      type: constant
      value:
        completion_params: {}
        mode: chat
        model: gpt-4o
        model_type: llm
        name: gpt-4o
        provider: langgenius/openai/openai
        type: model-selector
    tools:
      type: constant
      value:
        - enabled: true
          provider_id: <provider_id>
          provider_name: <provider_name>
          provider_type: builtin
          tool_label: <label>
          tool_name: <tool_name>
          tool_parameters: {}
    query:
      type: constant
      value: '{{#start.query#}}'
    max_iterations:
      type: constant
      value: 5
    instruction:
      type: constant
      value: '你是一个助手。'
    mcp_servers:
      type: constant
      value: |
        {
          "mcpServers": {
            "my-server": {
              "transport": "sse",
              "url": "http://your-mcp-server/sse"
            }
          }
        }
  agent_strategy_label: Function Calling (MCP)
  agent_strategy_name: function_calling
  agent_strategy_provider_name: junjiem/mcp_see_agent/mcp_see_agent
  output_schema: {}
  title: MCP Agent
  tool_node_version: '2'
  type: agent
```

`mcp_servers` 支持两种传输方式：
- SSE：`"transport": "sse"`，`"url": "http://host/sse"`
- Streamable HTTP：`"transport": "streamable_http"`，`"url": "http://host/mcp"`

可以在 `mcpServers` 中配置多个 MCP 服务。

Agent 节点输出变量：`text`（`value_selector: [agent_node, text]`）；模板引用：`{{#agent_node.text#}}`；若 `output_schema` 定义了具体字段，可按字段名引用。

---

## 将 Dify 自身工具暴露为 MCP 服务

[junjiem/mcp_compat_dify_tools](https://marketplace.dify.ai/plugin/junjiem/mcp_compat_dify_tools) 插件（需 Dify 1.2.0+）可以把 Dify 平台上的工具 API 转成 MCP 兼容接口。安装后在插件页添加 Endpoint，选择要暴露的工具列表，即可获得 MCP 服务 URL。

修改已有 Endpoint 的工具列表后，需要先停用再启用才能生效。

获得 URL 后，填入 MCP SSE Agent 的 `mcp_servers` 配置：

**Streamable HTTP 传输（推荐）：**

```json
{
  "mcpServers": {
    "dify-tools": {
      "transport": "streamable_http",
      "url": "https://your-dify.com/e/<endpoint-id>/mcp"
    }
  }
}
```

**SSE 传输（旧版）：**

```json
{
  "mcpServers": {
    "dify-tools": {
      "transport": "sse",
      "url": "https://your-dify.com/e/<endpoint-id>/sse"
    }
  }
}
```

这样 MCP Agent 就可以把 Dify 平台上配置的工具当作 MCP 工具来调用，实现 Dify 工具与 Agent 节点的闭环集成。
