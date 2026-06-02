# 基础节点：start / end / answer

## Start 节点

`type: start`；workflow 模式声明输入参数，advanced-chat 无需 variables。

```yaml
data:
  desc: ''
  title: 输入参数
  type: start
  variables:
  - default: ''
    hint: ''
    label: 用户ID
    max_length: 256
    options: []
    required: true
    type: text-input      # text-input | paragraph | number | select | file | file-list
    variable: user_id
```

---

## End 节点

`type: end`；仅用于 workflow 模式的最终输出。

```yaml
data:
  desc: ''
  outputs:
  - value_selector:
    - code_node
    - content
    value_type: string    # string | number | object | array[string] | array[number] | array[object]
    variable: content
  title: 输出
  type: end
```

---

## Answer 节点

`type: answer`；仅用于 advanced-chat 模式的流式输出，支持变量模板语法 `{{#node_id.field#}}`。

```yaml
data:
  answer: '{{#llm_node.text#}}'
  desc: ''
  title: 回复
  type: answer
  variables: []
```
