# 处理节点：code / template-transform / parameter-extractor

## Code 节点

`type: code`；执行 Python3 或 JavaScript，声明输入 `variables` 和 `outputs`。

```yaml
data:
  code: "import json\n\ndef main(user_id: str, raw: str) -> dict:\n    return {\"content\": f\"id:{user_id}\"}\n"
  code_language: python3    # python3 | javascript
  desc: ''
  outputs:
    content:
      children: null
      type: string          # string | number | object | array[string] | array[number] | array[object]
  title: 代码处理
  type: code
  variables:
  - value_selector:
    - start
    - user_id
    value_type: string
    variable: user_id
  - value_selector:
    - http_node
    - body
    value_type: string
    variable: raw
```

输出变量通过 `[code_node, <output_key>]` 引用。

---

## Template Transform 节点

`type: template-transform`；Jinja2 模板渲染，适合简单字符串拼接，无需写 Python。

```yaml
data:
  desc: ''
  template: '用户：{{ user_id }}，结果：{{ result }}'
  title: 模板渲染
  type: template-transform
  variables:
  - value_selector:
    - start
    - user_id
    value_type: string
    variable: user_id
  - value_selector:
    - code_node
    - content
    value_type: string
    variable: result
```

输出变量：`output`（`value_selector: [template_node, output]`）。

---

## Parameter Extractor 节点

`type: parameter-extractor`；用 LLM 从自然语言文本中提取结构化参数，输出字段由 `parameters` 定义。

```yaml
data:
  description: 从用户输入中提取参数
  model:
    mode: chat
    name: gpt-4o
    provider: langgenius/openai/openai
  parameters:
  - description: 城市名称
    name: city
    required: true
    type: string    # string | number | bool | array[string] | array[number] | array[object] | object
  - description: 日期范围
    name: date_range
    required: false
    type: string
  query:
  - start
  - query
  reasoning_mode: function_call   # function_call | prompt
  title: 参数提取
  type: parameter-extractor
```

输出变量通过 `[extractor_node, <parameter_name>]` 引用，例如 `[extractor_node, city]`。
