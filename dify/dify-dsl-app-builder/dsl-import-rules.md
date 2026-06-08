# Dify DSL 导入规则参考

这份参考用于生成或检查可导入 Dify 的 workflow / advanced-chat DSL。节点字段模板仍以各 `nodes-*.md` 文件为准；本文重点说明导入时容易失败或导入后 UI 异常的结构规则，尤其是节点类型、edge 连接、迭代内部 edge，以及可抽象为通用 DSL builder 的部分。

## 节点类型信息

Dify workflow 图中的节点通常由外层画布字段和 `data.type` 共同表达：

```yaml
id: code_node
type: custom
data:
  title: 代码处理
  type: code
```

导入校验和 UI 渲染主要依赖 `data.type`。普通业务节点外层 `type` 通常是 `custom`；特殊子节点可能使用专用外层类型，例如 `iteration-start` 子节点使用 `type: custom-iteration-start`。

当前 skill 已覆盖的节点类型：

| 分类 | `data.type` | 连接要点 |
|---|---|---|
| 基础 | `start` | 工作流入口。通常只有出边，没有入边。 |
| 基础 | `end` | workflow 终点。通常只有入边，没有出边。 |
| 基础 | `answer` | advanced-chat 流式回复节点。通常只有入边，可引用上游变量。 |
| 逻辑 | `if-else` | 出边用 `sourceHandle: 'true'` / `'false'` 区分分支。 |
| 逻辑 | `variable-aggregator` | 聚合多个上游变量，常用于分支汇合后统一输出。 |
| 逻辑 | `iteration` | 迭代容器，本身有普通入边和出边，内部还包含子节点与内部 edge。 |
| 逻辑 | `iteration-start` | 迭代容器内部起点，外层 `type: custom-iteration-start`，必须放在容器内。 |
| 处理 | `code` | 通过 `variables` 接收上游输入，通过 `outputs` 声明输出字段。 |
| 处理 | `template-transform` | 通过 Jinja2 模板生成 `output`。 |
| 处理 | `parameter-extractor` | 从文本提取结构化字段，输出字段由 `parameters` 决定。 |
| AI | `llm` | 输出常用 `text`。 |
| AI | `agent` | 输出常用 `text`，工具配置需符合插件策略要求。 |
| 外部 | `http-request` | 输出 `body`、`status_code`、`headers`。 |
| 外部 | `tool` | 调用 Dify 工具或插件工具。 |
| 外部 | `knowledge-retrieval` | 输出 `result`。 |

生成节点时应保证：

- `edge.data.sourceType` / `targetType` 与对应节点的 `data.type` 一致。
- 变量选择器中的第一个元素使用节点 `id`，不是节点标题。
- 画布节点具备稳定的 `position`、`positionAbsolute`、`sourcePosition`、`targetPosition`、`width`、`height`，否则导入后 UI 容易错位。
- 容器内节点必须带 `parentId`，并使用高于普通节点的 `zIndex`。

## Edge 类型与连接规则

当前导出的 Dify workflow 常规 edge 外层 `type` 使用 `custom`。edge 的语义主要由 `source`、`target`、`sourceHandle`、`targetHandle` 和 `data` 内的类型字段决定。

普通串联连接：

```yaml
- data:
    isInIteration: false
    isInLoop: false
    sourceType: start
    targetType: code
  id: start-source-code_node-target
  source: start
  sourceHandle: source
  target: code_node
  targetHandle: target
  type: custom
  zIndex: 0
```

分支连接：

```yaml
- data:
    isInIteration: false
    isInLoop: false
    sourceType: if-else
    targetType: code
  id: if_node-true-branch_a-target
  source: if_node
  sourceHandle: 'true'
  target: branch_a
  targetHandle: target
  type: custom
  zIndex: 0
```

连接规则：

- 普通节点出边默认使用 `sourceHandle: source`。
- 普通节点入边默认使用 `targetHandle: target`。
- `if-else` 的出边必须用 case id 作为 `sourceHandle`，常见为 `'true'` 和 `'false'`。
- `iteration` 容器入口是普通外部 edge：上游节点连接到 `iteration` 容器节点，`isInIteration: false`。
- `iteration` 容器出口也是普通外部 edge：`iteration` 容器节点连接下游节点，`sourceHandle: source`。
- `iteration-start` 只用于容器内部 edge，不应被容器外节点直接连接。
- 不要只写简化 edge 示例导入；实际 DSL 中每条 edge 都应带完整字段。

## 必填 edge 字段

每条可导入 edge 至少保留以下字段：

```yaml
- data:
    isInIteration: false
    isInLoop: false
    sourceType: <源节点 data.type>
    targetType: <目标节点 data.type>
  id: <稳定且唯一的 edge id>
  source: '<source_node_id>'
  sourceHandle: source
  target: '<target_node_id>'
  targetHandle: target
  type: custom
  zIndex: 0
```

字段说明：

| 字段 | 要求 |
|---|---|
| `id` | 全图唯一。推荐按 `<source>-<sourceHandle>-<target>-<targetHandle>` 或既有导出格式生成。 |
| `source` | 源节点 `id`。 |
| `target` | 目标节点 `id`。 |
| `sourceHandle` | 源端出口。普通节点为 `source`，分支节点为 case id。 |
| `targetHandle` | 目标端入口。普通节点为 `target`。 |
| `type` | 通常为 `custom`。 |
| `zIndex` | 普通外部 edge 通常为 `0`，迭代内部 edge 通常跟随内部节点使用 `1002`。 |
| `data.isInIteration` | 是否属于迭代容器内部 edge。 |
| `data.isInLoop` | 当前模板默认 `false`；保留该字段以兼容导入结构。 |
| `data.sourceType` | 源节点 `data.type`。 |
| `data.targetType` | 目标节点 `data.type`。 |

建议 builder 在生成 edge 前从节点注册表中读取 `data.type`，统一填充 `sourceType` 和 `targetType`，避免手写时类型不一致。

## 迭代内部 edge 的特殊要求

`iteration` 节点不是普通单节点。一个完整迭代结构至少包含：

- 外层 `iteration` 容器节点，`data.type: iteration`。
- 容器内部 `iteration-start` 子节点，`data.type: iteration-start`，外层 `type: custom-iteration-start`。
- 一个或多个容器内部处理节点，带 `parentId: <iteration_id>`。
- 容器内部 edge，带 `isInIteration: true` 和 `iteration_id`。
- 容器外普通入边和普通出边。

内部 edge 示例：

```yaml
- data:
    isInIteration: true
    isInLoop: false
    iteration_id: iter_node
    sourceType: iteration-start
    targetType: template-transform
  id: iter_node_start-source-inner_template-target
  source: iter_node_start
  sourceHandle: source
  target: inner_template
  targetHandle: target
  type: custom
  zIndex: 1002
```

内部节点要求：

```yaml
id: inner_template
parentId: iter_node
position:
  x: 104
  y: 68
positionAbsolute:
  x: 788
  y: 350
zIndex: 1002
type: custom
data:
  type: template-transform
```

特别注意：

- `iteration-start` 子节点也必须带 `parentId: <iteration_id>`，并设置 `draggable: false`、`selectable: false`。
- 内部 edge 的 `data.iteration_id` 必须等于容器节点 id。
- 内部 edge 的 `data.isInIteration` 必须为 `true`；容器外入边和出边仍为 `false`。
- 内部 edge 的 `sourceType` / `targetType` 依然写两端节点的 `data.type`，不是外层 `type`。
- 内部节点位置是相对容器的 `position` 加绝对画布坐标 `positionAbsolute`；两者要一致。
- 迭代输出由容器节点 `data.output_selector` 指向内部末端节点输出，例如 `[inner_template, output]`。
- 迭代当前项通过 `[iter_node, item]` 引用，不通过 `iteration-start` 引用。

## 可抽象的通用 DSL builder 模式

Dify DSL App Builder 的经验可以抽象成一套通用 builder 模式，适用于其他声明式配置或工作流 DSL：

| 抽象层 | Dify 中的对应物 | 可复用做法 |
|---|---|---|
| 节点注册表 | `nodes-*.md` 中的节点模板 | 按节点类型维护 schema、默认字段、输入输出端口和变量输出。 |
| 图构建器 | `nodes` + `edges` | 用 `addNode` / `connect` 生成稳定 id、位置、类型字段和完整 edge。 |
| 端口规则 | `sourceHandle` / `targetHandle` | 为普通节点、分支节点、容器节点定义标准端口名。 |
| 容器规则 | `iteration` + 内部节点 | 把父子节点、内部 edge、zIndex、相对/绝对坐标封装为容器 builder。 |
| 变量选择器 | `value_selector` / 模板变量 | 统一从节点 id 和输出字段生成引用，避免标题或自然语言混入引用。 |
| 导入校验 | Admin API 导入 + 回读导出 | 导入前做静态检查，导入后重新导出并校验关键节点、边和输出。 |
| 安全策略 | `include_secret=false`、备份旧 DSL | 将密钥、覆盖更新、备份、回滚策略放进平台 API skill，而不是节点模板。 |

推荐的 builder 检查清单：

- 先注册所有节点，再生成 edge，避免连接到不存在的节点。
- 从节点注册表推导 `sourceType` / `targetType`，不要手写重复信息。
- 所有 edge 使用统一函数生成完整字段，不允许临时简写。
- 对分支、迭代、循环等特殊结构使用专门 builder。
- 导入前检查节点 id 唯一、edge id 唯一、edge 两端存在、handle 合法。
- 导入前检查所有变量选择器引用的节点和字段存在。
- 导入后回读远端 DSL，验证关键节点类型、edge 数量、输入变量和输出字段。

这些抽象能让主 `SKILL.md` 保持稳定，只在平台 DSL schema 变化时更新节点模板、连接规则和校验器。
