# 基于母版重建 PPT

## 概述

基于现有模板生成新 PPT 的核心策略：**以母版为单位思考**。用户不关心模板里有多少页，只关心有哪些母版（开始、目录、正文、标题等），以及每种母版长什么样。⚠️⚠️严格按照工作流完成。

## 设计理念

**不要创建无聊的幻灯片。** 白色背景上的普通项目符号无法打动任何人。为每张幻灯片参考以下设计理念。

### 开始之前

- **选择大胆且与内容相关的色彩方案**: 配色方案应感觉专为本主题设计。如果将您的颜色替换到完全不同的演示文稿中仍然"适用"，说明您的选择不够具体。
- **主次分明**: 一种颜色应占主导地位（60-70%视觉权重），配以1-2种辅助色调和一个醒目的强调色。永远不要给所有颜色相同的权重。
- **明暗对比**: 标题+结论幻灯片使用深色背景，内容幻灯片使用浅色背景（"三明治"结构）。或者整体采用深色以获得高端质感。
- **坚持视觉主题**: 选择一个独特的元素并重复使用——圆角图片框、彩色圆圈中的图标、厚单边边框。在每张幻灯片中保持一致。

### 色彩方案

选择与您主题匹配的颜色——不要默认使用通用蓝色。使用这些方案作为灵感：

| 主题 | 主色 | 辅助色 | 强调色 |
|------|------|--------|--------|
| **午夜行政** | `1E2761` (海军蓝) | `CADCFC` (冰蓝) | `FFFFFF` (白色) |
| **森林苔藓** | `2C5F2D` (森林绿) | `97BC62` (苔藓绿) | `F5F5F5` (米白) |
| **珊瑚活力** | `F96167` (珊瑚红) | `F9E795` (金色) | `2F3C7E` (海军蓝) |
| **暖陶土** | `B85042` (陶土红) | `E7E8D1` (沙色) | `A7BEAE` (鼠尾草绿) |
| **海洋渐变** | `065A82` (深蓝) | `1C7293` (青绿) | `21295C` (午夜蓝) |
| **炭灰极简** | `36454F` (炭灰) | `F2F2F2` (灰白) | `212121` (黑色) |
| **青绿信任** | `028090` (青绿) | `00A896` (海泡绿) | `02C39A` (薄荷绿) |
| **浆果奶油** | `6D2E46` (浆果紫) | `A26769` (灰玫瑰) | `ECE2D0` (奶油色) |
| **鼠尾草宁静** | `84B59F` (鼠尾草绿) | `69A297` (桉树绿) | `50808E` (石板蓝) |
| **樱桃大胆** | `990011` (樱桃红) | `FCF6F5` (灰白) | `2F3C7E` (海军蓝) |

### 每张幻灯片的要求

**每张幻灯片都需要视觉元素**——图片、图表、图标或形状。纯文字幻灯片容易被遗忘。

**布局选项：**
- 双栏布局（左侧文字，右侧插图）
- 图标+文字行（彩色圆圈中的图标，粗体标题，下方描述）
- 2x2或2x3网格（一侧图片，另一侧内容块网格）
- 半出血图片（完整左侧或右侧）配内容叠加

**数据展示：**
- 大数字突出显示（大数字60-72pt，下方小标签）
- 对比列（前后对比、优缺点、并排选项）
- 时间线或流程图（编号步骤、箭头）

**视觉美化：**
- 小彩色圆圈中的图标放在章节标题旁边
- 斜体强调文字用于关键统计数据或标语

### 字体排版

**选择有趣的字体配对**——不要默认使用Arial。选择有个性的标题字体并搭配简洁的正文字体。

| 标题字体 | 正文字体 |
|----------|----------|
| Georgia | Calibri |
| Arial Black | Arial |
| Calibri | Calibri Light |
| Cambria | Calibri |
| Trebuchet MS | Calibri |
| Impact | Arial |
| Palatino | Garamond |
| Consolas | Calibri |

| 元素 | 字号 |
|------|------|
| 幻灯片标题 | 36-44pt 粗体 |
| 章节标题 | 20-24pt 粗体 |
| 正文 | 14-16pt |
| 说明文字 | 10-16pt 浅色 |

### 间距

- 0.5英寸最小边距
- 内容块之间0.3-0.5英寸
- 留出呼吸空间——不要填满每一寸

### 避免（常见错误）

- **不要重复相同的布局**——在幻灯片之间变化列、卡片和突出显示
- **不要居中正文**——左对齐段落和列表；仅标题居中
- **不要吝啬字号对比**——标题需要36pt+才能与14-16pt正文区分开
- **不要默认蓝色**——选择反映特定主题的颜色
- **不要随机混合间距**——选择0.3英寸或0.5英寸间距并保持一致
- **不要只设计一张幻灯片而其余保持普通**——要么全部投入，要么保持简单
- **不要创建纯文字幻灯片**——添加图片、图标、图表或视觉元素；避免普通标题+项目符号
- **不要忘记文本框内边距**——当将线条或形状与文本边缘对齐时，在文本框上设置`margin: 0`或偏移形状以考虑内边距
- **不要使用低对比度元素**——图标和文本都需要与背景形成强烈对比；避免浅色背景上的浅色文字或深色背景上的深色文字
- **永远不要在标题下使用强调线**——这是AI生成幻灯片的标志；改用空白或背景颜色

## Officecli 适配指南

使用officecli创建专业幻灯片时，以下是一些实用的命令示例和技巧：

### 基础幻灯片结构

```bash
# 创建新的PPTX文件
officecli create presentation.pptx

# 添加新幻灯片
officecli add presentation.pptx /slide --type slide

# 添加形状（标题）
officecli add presentation.pptx /slide[1] --type shape --prop text="标题文字" --prop size=36pt --prop bold=true --prop fill=1E2761 --prop color=FFFFFF

# 添加正文内容
officecli add presentation.pptx /slide[1] --type shape --prop text="正文内容" --prop size=16pt --prop x=1cm --prop y=5cm --prop width=20cm --prop height=10cm
```

### 色彩方案应用

```bash
# 设置背景颜色
officecli set presentation.pptx /slide[1] --prop fill=1E2761

# 设置文字颜色
officecli set presentation.pptx /slide[1]/shape[1] --prop color=FFFFFF

# 设置形状填充
officecli set presentation.pptx /slide[1]/shape[2] --prop fill=CADCFC

# 设置边框颜色和样式
officecli set presentation.pptx /slide[1]/shape[1] --prop line=FFFFFF:2:solid
```

### 字体和排版

```bash
# 设置字体
officecli set presentation.pptx /slide[1]/shape[1] --prop font=Arial --prop font.latin=Arial --prop font.ea=微软雅黑

# 设置字号
officecli set presentation.pptx /slide[1]/shape[1] --prop size=36pt

# 设置粗体
officecli set presentation.pptx /slide[1]/shape[1] --prop bold=true

# 设置斜体
officecli set presentation.pptx /slide[1]/shape[1] --prop italic=true

# 设置文本对齐
officecli set presentation.pptx /slide[1]/shape[1] --prop align=center

# 设置行间距
officecli set presentation.pptx /slide[1]/shape[1] --prop lineSpacing=1.5x
```

### 布局和定位

```bash
# 精确设置位置
officecli set presentation.pptx /slide[1]/shape[1] --prop x=2cm --prop y=3cm

# 设置尺寸
officecli set presentation.pptx /slide[1]/shape[1] --prop width=10cm --prop height=5cm

# 设置垂直对齐
officecli set presentation.pptx /slide[1]/shape[1] --prop valign=middle

# 设置内边距
officecli set presentation.pptx /slide[1]/shape[1] --prop margin=0.5cm
```

### 视觉效果

```bash
# 设置透明度
officecli set presentation.pptx /slide[1]/shape[1] --prop opacity=0.8

# 设置渐变填充
officecli set presentation.pptx /slide[1]/shape[1] --prop gradient="1E2761-CADCFC-90"

# 设置阴影
officecli set presentation.pptx /slide[1]/shape[1] --prop shadow=000000

# 设置发光效果
officecli set presentation.pptx /slide[1]/shape[1] --prop glow=4472C4

# 设置圆角
officecli set presentation.pptx /slide[1]/shape[1] --prop geometry=roundRect

# 设置3D效果
officecli set presentation.pptx /slide[1]/shape[1] --prop bevel=circle-6-6 --prop depth=10
```

### 高级技巧

```bash
# 添加动画
officecli set presentation.pptx /slide[1]/shape[1] --prop animation=fade

# 设置链接
officecli set presentation.pptx /slide[1]/shape[1] --prop link=https://example.com --prop tooltip="点击访问"

# 设置列表样式
officecli set presentation.pptx /slide[1]/shape[1] --prop list=bullet

# 设置字符间距
officecli set presentation.pptx /slide[1]/shape[1] --prop spacing=200

# 设置反射效果
officecli set presentation.pptx /slide[1]/shape[1] --prop reflection=half

# 设置软边缘
officecli set presentation.pptx /slide[1]/shape[1] --prop softEdge=5

# 设置材质
officecli set presentation.pptx /slide[1]/shape[1] --prop material=metal

# 设置灯光
officecli set presentation.pptx /slide[1]/shape[1] --prop lighting=threePt
```

### 批量操作和查询

```bash
# 查询所有形状
officecli query presentation.pptx shape

# 查询特定属性
officecli query presentation.pptx "shape[bold=true]"

# 获取详细信息
officecli get presentation.pptx /slide[1]/shape[1] --json

# 批量修改多个元素
officecli batch presentation.pptx --json '[{"command":"set","path":"/slide[1]/shape[1]","props":{"fill":"1E2761"}},{"command":"set","path":"/slide[1]/shape[2]","props":{"color":"FFFFFF"}}]'
```

### 最佳实践总结

1. **色彩一致性**: 选择一套主色方案，贯穿整个演示文稿
2. **字体层次**: 使用不同的字号和字重创建清晰的视觉层次
3. **留白艺术**: 合理使用间距，避免内容过于拥挤
4. **视觉平衡**: 每张幻灯片至少包含一个视觉元素
5. **对比度**: 确保文字和背景之间有足够的对比度
6. **主题呼应**: 所有设计元素都应与内容主题相呼应
7. **避免模板感**: 通过变化布局和元素位置，避免幻灯片看起来像模板

通过合理运用officecli的这些属性和命令，您可以创建出专业、美观且符合设计理念的演示文稿，而不仅仅是普通的文字堆砌。

## 工作流

### 前提准备：

1. 按照Design Ideas，根据主题制作大纲和布局，大纲需要包括每页内容，每页布局，一共几页。
2. 将大纲保存在任务工作区，便于逐页执行和复核。
3. 对多页任务维护逐页进度，至少覆盖页面规划、各页制作、验证和修复。

### 一、页面规划

⚠️⚠️ 严格按照顺序执行。

1. 将模板复制到工作目录；不要直接修改唯一的源模板。
2. 从仓库根目录运行 `scripts/pptx_master_analysis.py <工作副本.pptx>`，列出布局并清空工作副本中的现有幻灯片。
3. 结合脚本输出判断每个布局的用途：封面、目录、正文、结尾等。
4. 打开工作副本，确保内存驻留：`officecli open <工作副本.pptx>`。
5. 新建目标数量的页面并按用途分配布局：`officecli add <工作副本.pptx> / --type slide --prop layout="<布局N>"`。

### 二、填充内容

按照Design Ideas设计并实施，相关操作帮助：office help pptx

### 三、验证

⚠️必须逐项运行，如果出现问题，或有主题无关内容需要调整后重新验证。

- XML完整性：`officecli validate <工作副本.pptx>`
- 检查模板残留文字：`officecli view <工作副本.pptx> text`
- 检查格式问题：`officecli view <工作副本.pptx> issues`

## 注意事项

1. **索引漂移**：删除、添加、移动页面都会改变后续页的索引。删除多页时始终删第 1 页。
2. **不要并行操作**：逐页顺序执行，避免索引冲突。
3. **文本换行**：使用 `\\n` 表示换行符。
4. **特殊字符**：`$` 等特殊字符用单引号包裹。
5. **批处理**：重复简单操作可用 `officecli batch <工作副本.pptx> --input updates.json --force --json`，执行后需再次确认状态。
