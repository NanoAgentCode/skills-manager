# 外部连接节点：http-request / tool / knowledge-retrieval

## HTTP Request 节点

`type: http-request`；调用外部 HTTP 接口，URL 和 body 中均可用 `{{#node.field#}}` 引用变量。

```yaml
data:
  authorization:
    type: no-auth         # no-auth | api-key | bearer | basic
  body:
    data: ''
    type: none            # none | json | form-data | x-www-form-urlencoded | raw-text
  desc: ''
  headers: ''
  method: GET             # GET | POST | PUT | DELETE | PATCH
  params: ''
  retry_config:
    enabled: false
    max_retries: 1
    retry_interval: 1000
    exponential_backoff:
      enabled: false
      multiplier: 2
      max_interval: 10000
  timeout:
    connect: 10
    read: 30
    write: 30
  title: 调用接口
  type: http-request
  url: 'http://example.com/api/{{#start.user_id#}}'
```

输出变量：`body`（string）、`status_code`（number）、`headers`（object）。

JSON body 示例：

```yaml
  body:
    type: json
    data: '{"key": "{{#start.value#}}"}'
```

带 Bearer Token 鉴权示例：

```yaml
  authorization:
    type: bearer
    config:
      token: '{{#env.API_TOKEN#}}'
```

---

## Tool 节点

`type: tool`；调用内置工具或插件工具。`provider_type: builtin` 为内置工具。

```yaml
data:
  desc: ''
  provider_id: time
  provider_name: time
  provider_type: builtin
  title: 获取当前时间
  tool_configurations:
    format:
      type: constant
      value: '%Y-%m-%d %H:%M:%S'
    timezone:
      type: constant
      value: Asia/Shanghai
  tool_description: A tool for getting the current time.
  tool_label: Current Time
  tool_name: current_time
  tool_node_version: '2'
  tool_parameters: {}
  type: tool
```

插件工具 `provider_type: api`，`provider_id` 为插件 ID。`tool_configurations` 的每个参数值可以是：
- `type: constant`：固定值
- `type: variable`：引用工作流变量（需在 `tool_parameters` 中配置 selector）
- `type: mixed`：包含模板变量的字符串

---

## Knowledge Retrieval 节点

`type: knowledge-retrieval`；从知识库检索相关文档片段。`dataset_ids` 在 DSL 导出时已加密，导入时自动解密。

```yaml
data:
  dataset_ids:
  - <dataset_id>
  multiple_retrieval_config:
    reranking_enable: false
    reranking_mode: weighted_score
    score_threshold: null
    top_k: 4
    weights:
      keyword_setting:
        keyword_weight: 0
      vector_setting:
        embedding_model_name: text-embedding-3-large
        embedding_provider_name: langgenius/openai/openai
        vector_weight: 1
      weight_type: customized
  query_variable_selector:
  - start
  - query
  retrieval_mode: multiple    # multiple | single
  title: 知识检索
  type: knowledge-retrieval
```

输出变量：`result`（array[object]，`value_selector: [retrieval_node, result]`）。
