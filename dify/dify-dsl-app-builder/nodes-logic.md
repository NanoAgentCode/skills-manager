# 逻辑控制节点：if-else / variable-aggregator / iteration

## IF/ELSE 节点

`type: if-else`；条件分支，`true` 和 `false` 两个出口（sourceHandle）。

```yaml
data:
  cases:
  - case_id: 'true'
    conditions:
    - comparison_operator: contains   # = | != | > | < | contains | not contains | starts with | ends with | empty | not empty
      id: <uuid>
      value: hello
      varType: string
      variable_selector:
      - start
      - query
    id: 'true'
    logical_operator: and
  desc: ''
  title: 条件判断
  type: if-else
```

Edge 出口示例：

```yaml
- source: 'if_node'
  sourceHandle: 'true'
  target: 'end_true'
- source: 'if_node'
  sourceHandle: 'false'
  target: 'end_false'
```

---

## Variable Aggregator 节点

`type: variable-aggregator`；聚合多条分支的变量为统一输出。

```yaml
data:
  desc: ''
  output_type: string
  title: 变量聚合
  type: variable-aggregator
  variables:
  - - branch_true_node
    - output
  - - branch_false_node
    - output
```

输出变量：`output`（`value_selector: [aggregator_node, output]`）。

如需按分组聚合，加 `advanced_settings`：

```yaml
  advanced_settings:
    group_enabled: true
    groups:
    - groupId: <uuid>
      group_name: Group1
      output_type: string
      variables:
      - - branch_a
        - output
      - - branch_b
        - output
```

---

## Iteration 节点

`type: iteration`；对数组逐项迭代，内部包含一个 `iteration-start` 子节点。

**容器节点**：

```yaml
data:
  error_handle_mode: terminated   # terminated | continue | remove-abnormal-output
  is_parallel: false
  iterator_input_type: array[string]
  iterator_selector:
  - code_node
  - result
  output_selector:
  - inner_template_node
  - output
  output_type: array[string]
  parallel_nums: 10
  start_node_id: iter_node_start
  title: 迭代
  type: iteration
height: 178
id: iter_node
width: 388
zIndex: 1
```

**内部 iteration-start 子节点**（固定在容器左侧，不可拖动）：

```yaml
data:
  title: ''
  type: iteration-start
draggable: false
height: 48
id: iter_node_start
parentId: iter_node
position:
  x: 24
  y: 68
positionAbsolute:
  x: 708   # iter_node.position.x + 24
  y: 350   # iter_node.position.y + 68
selectable: false
sourcePosition: right
targetPosition: left
type: custom-iteration-start
width: 44
zIndex: 1002
```

**内部 edge 规则**：

```yaml
data:
  isInIteration: true
  isInLoop: false
  iteration_id: iter_node
  sourceType: iteration-start
  targetType: template-transform
zIndex: 1002
```

**内部节点规则**：加 `parentId: iter_node`、`zIndex: 1002`。

迭代当前项通过 `value_selector: [iter_node, item]` 引用，类型与 `iterator_input_type` 的元素类型一致。
