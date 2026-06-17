---
name: wechat-format
description: 公众号完整内容生产管线：排版、封面、推送。Use when the user asks to format Markdown, plain text, rough notes, or articles into WeChat official-account compatible HTML, generate or insert a WeChat article cover, publish to WeChat drafts, handle comment replies, or run WeChat article production workflows.
---

# wechat-format

公众号一键排版技能。把任意文本内容（Markdown、纯文本、格式粗糙的笔记）转成微信公众号兼容的排版 HTML，AI 自动理解内容结构并增强排版，可视化选择主题后一键复制粘贴到微信后台。可选生成封面图、推送草稿箱。

## Skill Description For Claude

公众号完整管线：排版 → 封面（可选）→ 推送（可选）。把 Markdown 文章转为微信公众号兼容的内联样式 HTML，支持纯文本输入，AI 自动补充结构和排版增强。当用户说"排版""微信排版""格式化文章""format"时使用。

## 脚本目录

`{baseDir}` = 本 SKILL.md 所在目录。执行脚本时用 `{baseDir}/scripts/xxx.py` 替换为实际绝对路径。

| 脚本 | 用途 |
|------|------|
| `scripts/check_dependencies.py` | 检测依赖；带 `--install` 时安装缺失 Python 包 |
| `scripts/format.py` | 排版：Markdown → 微信兼容 HTML |
| `scripts/publish.py` | 推送：HTML → 公众号草稿箱 |
| `scripts/comment_reply.py` | 评论自动回复（可选） |
| `scripts/generate.py` | 封面生成脚本（需配合 `wechat-cover/config.json`） |

## 配置

纯排版无需创建 `config.json`。如果文件不存在，脚本会使用内置默认配置：

- 输出目录：`{baseDir}/output`
- Vault 根目录：当前用户主目录
- 默认主题：`newspaper`

发布草稿箱、评论回复、封面生成或自定义输出目录时，再创建 `config.json`（参考 `config.example.json`）：

```json
{
  "output_dir": "/tmp/wechat-format",
  "vault_root": "/path/to/your/obsidian/vault",
  "image_search_paths": [],
  "settings": {
    "default_theme": "newspaper",
    "auto_open_browser": true
  },
  "wechat": {
    "app_id": "YOUR_APP_ID",
    "app_secret": "YOUR_APP_SECRET",
    "author": "作者名"
  },
  "cover": {
    "output_dir": "~/Documents/covers",
    "image_generation_script": ""
  },
  "ai": {
    "url": "",
    "api_key": "",
    "model": ""
  }
}
```

- `wechat` 部分仅推送或评论回复时需要，纯排版可不填
- `cover` 部分仅生成封面时需要
- `config.json` 已在 `.gitignore` 中，不会被提交

## Instructions

### 触发条件

用户说以下任何一种：
- `/format 文件路径`
- `排版这篇文章`
- `微信排版`
- `格式化为公众号格式`
- `把这篇转成微信格式`

### 完整工作流

#### 第 0 步：依赖检测

首次使用，或用户环境不确定时，先检测依赖：

```bash
python3 {baseDir}/scripts/check_dependencies.py
```

如果提示缺少依赖，先询问用户是否允许安装。用户同意后执行：

```bash
python3 {baseDir}/scripts/check_dependencies.py --install
```

不要在未获得用户确认时自动安装依赖。安装完成后再继续排版或发布流程。

#### 第 1 步：确认文章

1. 如果用户给了文件路径，直接读取
2. 如果没给路径，问用户要文章路径
3. 读取文章内容，确认标题和字数

#### 第 1.5 步：结构化预处理（仅在需要时）

读取文章后，先检测输入内容的 Markdown 结构完整度，决定是否需要 AI 结构化预处理。

**检测方法**：扫描全文，统计 `##` 标题、`**加粗**`、`- 列表`、`> 引用`、`` ` 代码 ` `` 等格式标记的数量。

**判断规则**：
- 有 `##` 标题且格式标记分布合理 → **跳过**，直接进入第 2 步
- 缺少 `##` 标题，或几乎没有格式标记（纯文本/粗糙笔记）→ **执行结构化**

**结构化规则（底线：只加标记，不改内容）**：

1. **加标题**：识别文章的逻辑段落和主题转换点，在转换处插入 `##` 标题。标题从内容中提炼，不编造。三段内容不硬拆五个标题——尊重原文信息密度
2. **分段落**：确保段落之间有空行分隔，长段落在语义转换处拆分
3. **加列表**：识别并列/枚举性质的内容，加 `- ` 或 `1. ` 标记
4. **加强调**：识别关键词、产品名、核心概念，加 `**加粗**`
5. **清理格式**：去除多余空行、修正缩进、统一标点
6. **不改措辞**：不调语序、不增删内容、不润色文字。用户写什么就是什么，只加结构标记

**保存与告知**：
- 结构化后保存为 `/tmp/wechat-format/xxx-structured.md`
- 告知用户："检测到输入缺少 Markdown 格式标记，已自动补充标题和结构，保存在 xxx-structured.md，可检查调整"
- 后续第 2 步基于 structured.md 继续处理

---

#### 第 2 步：AI 内容分析 + 自动套格式

读取文章（或上一步输出的 structured.md），Claude 分析内容结构，在 Markdown 层面自动套用合适的排版容器。这是我们比纯手动排版工具强的核心——AI 理解内容，自动匹配最佳呈现方式。

**分析维度**：文章类型（访谈/教程/产品介绍/深度分析）、内容元素（对话/图片/代码/数据）、节奏感（密集段 vs 留白段）。

**自动套用规则**（按优先级）：

1. **对话/访谈** → `:::dialogue[标题]`
   - 检测到 `**名字：**` 或 `名字：` 交替出现 → 用 `:::dialogue` 包裹
   - 格式：`名字: 对话内容`（中英文冒号都支持）
   - 不是所有对话都要套——独白段落、叙述性段落保持原样
   - 同一场景的连续对话放一个 dialogue 块，换场景换一个新块

2. **连续多图** → `:::gallery[标题]`
   - 3张以上连续图片 → 自动套 `:::gallery`，横向滚动浏览
   - 适合产品截图、对比图、系列图

3. **超长图片** → `:::longimage[标题]`
   - 流程图、架构图、长截图 → 固定高度容器，纵向滚动
   - 一般需要用户标注或 AI 判断图片内容

4. **核心观点/金句** → callout 格式
   - 核心观点 → `> [!important] 标题`
   - 小技巧/提示 → `> [!tip] 标题`
   - 注意事项 → `> [!warning] 标题`
   - 普通引用 → `> [!callout] 标题`（使用主题色）
   - 不要过度使用，一篇文章 1-3 处即可

5. **分隔符** → 在章节转换处确保有 `---` 分隔

6. **图说标记** → 图片后紧跟的说明用斜体：`*这是图片说明*`

7. **外部链接** → 无需处理（脚本自动转脚注）

**处理完成后**，把增强后的 Markdown 保存为临时文件（`/tmp/wechat-format/xxx-enhanced.md`）。

#### 第 2.5 步：推荐主题

根据内容分析结果，推荐 3 个最适合的主题：

| 内容类型 | 推荐主题 |
|----------|----------|
| 深度阅读/行业分析 | newspaper, magazine, coffee-house |
| 技术产品/AI工具 | apple-code, github, bytedance, sspai |
| 生活灵感/对话体 | terracotta, mint-fresh, sunset-amber |
| 教程/操作指南 | github, apple-code, sspai |
| 文艺/随笔/观点 | terracotta, sunset-amber, lavender-dream, chinese |
| 活力/通用/速报 | sports, wechat-native, bold-blue |

推荐的主题 ID 通过 `--recommend` 参数传给脚本，在 gallery 中高亮显示。

#### 第 3 步：打开主题画廊（默认流程）

```bash
python3 {baseDir}/scripts/format.py \
  --input "文章路径.md" \
  --gallery \
  --recommend newspaper magazine coffee-house
```

这会用用户的**真实文章**渲染 26 个全量主题，在浏览器打开画廊页面。用户点按钮切换主题预览，选中后点「用这个风格排版」一键复制到剪贴板。若 `--recommend` 传入了不存在的主题，脚本会提示并跳过。

#### 第 3 步（备选）：直接指定主题排版

如果用户已经知道想用哪个主题，可以跳过画廊直接排版：

```bash
python3 {baseDir}/scripts/format.py \
  --input "文章路径.md" \
  --theme terracotta
```

#### 第 4 步：确认结果

告诉用户：
- Gallery 模式：在浏览器中切换主题预览，选中后点按钮复制，粘贴到公众号后台
- 直接模式：在浏览器中检查预览，点「复制到微信」按钮

---

### 封面图生成（可选）

排版完成后，用户说"配封面""生成封面"时执行。

#### 封面提示词模板

```
请根据提供的内容创建一张吸引眼球的公众号封面图，遵循以下规范：

视觉风格
- Notion插画风格，比例为 2.35:1（公众号封面标准尺寸）
- 色彩鲜明、对比强烈，确保在小尺寸预览时依然醒目
- 风格统一，避免写实元素，保持整体手绘质感

构图要求
- 主视觉元素居中或偏左（右侧预留标题区域）
- 添加 1-2 个简洁的卡通形象、图标或知名人物剪影，增强记忆点
- 大量留白，突出核心信息，避免画面拥挤

文字处理
- 标题文字大而醒目，控制在 8 字以内
- 可添加 1 行副标题或关键词标签
- 字体风格与手绘插画协调统一

吸引力法则
- 使用悬念、数字、痛点等钩子元素激发点击欲望
- 视觉元素夸张有反差
- 色彩搭配参考爆款封面：橙黄、蓝紫、红黑等高对比组合

语言
- 除非另有说明，默认使用中文
- 画面内所有可读文字必须使用简体中文，英文只能作为点缀出现

内容主题：{从文章中提炼的一句话主题描述}
```

#### 封面工作流

1. 从文章提炼一句话主题
2. 用上述模板生成提示词，保存为 `prompt.md`（YAML 头 `aspect_ratio: "21:9"`, `image_size: "2K"`）
3. 调用图片生成服务（需在 `config.json` 中配置 `cover.image_generation_script`，或手动使用任意 AI 生图工具）
4. 生成后默认插入文章标题下方

---

### 推送到公众号草稿箱（可选）

排版完成后，用户说"推送""发公众号"时执行。需要在 `config.json` 配置 `wechat.app_id` 和 `wechat.app_secret`。

```bash
python3 {baseDir}/scripts/publish.py \
  --dir "排版输出目录" \
  --cover "封面图路径（可选）"
```

推送流程：
1. 读取排版后的 HTML（`article.html`）
2. 上传文章内图片到微信 CDN
3. 上传封面图为素材
4. 创建草稿（自动填充标题、摘要、作者）
5. 返回 media_id，可在公众号后台「内容管理→草稿箱」查看

也支持从 Markdown 直接推送（自动排版再推）：

```bash
python3 {baseDir}/scripts/publish.py \
  --input "文章.md" \
  --theme terracotta
```

---

### 参数说明

**format.py**：
- `--input` / `-i`：Markdown 文件路径（必须）
- `--gallery`：打开主题画廊（推荐，默认使用）
- `--theme` / `-t`：直接指定主题名（跳过画廊）
- `--output` / `-o`：输出目录（默认 /tmp/wechat-format）
- `--vault-root`：Obsidian Vault 根目录（用于搜索 wikilink 图片）
- `config.json.image_search_paths`：额外图片搜索目录（用于 `![[image.jpg]]`）
- `--recommend`：推荐的主题 ID 列表，gallery 中高亮显示
- `--no-open`：不自动打开浏览器
- `--format`：输出格式 wechat/html/plain

**publish.py**：
- `--dir`：排版输出目录路径（已排版好的 HTML）
- `--input`：Markdown 文件路径（自动排版再推送）
- `--cover` / `-c`：封面图路径（可选，默认搜索目录内 cover.*）
- `--title` / `-t`：文章标题（默认从 HTML 提取）
- `--theme`：排版主题（仅 `--input` 模式有效）
- `--author` / `-a`：作者名（默认读 config.json）
- `--dry-run`：只做排版和图片上传，不推送草稿箱

**check_dependencies.py**：
- 无参数：检测 Python 版本、`markdown`、`requests`
- `--install`：用当前 Python 解释器执行 `pip install` 安装缺失包

### 可用主题（26 个）

#### 深度阅读（3 个）

| 主题 | 命令值 | 风格 |
|------|--------|------|
| 报纸 | newspaper | 纽约时报风，严肃深度 |
| 杂志 | magazine | 超大留白，品质长文 |
| 咖啡 | coffee-house | 棕色暖调，稳重温馨 |

#### 技术产品（4 个）

| 主题 | 命令值 | 风格 |
|------|--------|------|
| 苹果代码 | apple-code | macOS 深色代码窗口，粉紫渐变外框，苹果蓝紫强调 |
| GitHub | github | 开发者风，浅色代码块 |
| 字节蓝 | bytedance | 蓝青渐变，科技现代 |
| 少数派 | sspai | 中文科技媒体红 |

#### 生活灵感（5 个）

| 主题 | 命令值 | 风格 |
|------|--------|------|
| 赤陶 | terracotta | 暖橙色，满底圆角标题，左边框渐变 |
| 薄荷 | mint-fresh | 薄荷绿，清爽健康 |
| 日落 | sunset-amber | 琥珀暖调，温暖感性 |
| 薰衣草 | lavender-dream | 紫色梦幻，浪漫诗意 |
| 中国风 | chinese | 朱砂红，古典雅致 |

#### 活力通用（2 个）

| 主题 | 命令值 | 风格 |
|------|--------|------|
| 运动 | sports | 渐变色带，活力动感 |
| 微信原生 | wechat-native | 微信绿，传统阅读 |

#### 模板系列（12 个，布局×配色）

| 分类 | 命令值 | 风格 |
|------|--------|------|
| 极简商务 | minimal-blue / minimal-navy / minimal-red | 无装饰标题，适合商务/科技/专业内容 |
| 品牌聚焦 | focus-blue / focus-gold / focus-red | 居中标题+上下线，适合品牌/展示/营销内容 |
| 精致杂志 | elegant-blue / elegant-green / elegant-navy | 左侧双线边框+渐变表头，适合杂志/设计/高端内容 |
| 醒目公告 | bold-blue / bold-green / bold-navy | 填充标题+色块 h3，适合新闻/公告/重点内容 |

### 内置排版增强

脚本自动处理以下内容：
- **CJK 间距修复**：中英文/中数字之间自动加空格
- **加粗标点修复**：`**文字，**` → `**文字**，`，中文标点移到标记外
- **纯内联样式**：所有 CSS 直接写在每个标签的 `style="..."` 属性上
- **列表模拟**：`<ul>/<ol>` 改为 `<section>` + flexbox 模拟
- **外链转脚注**：`[text](url)` 自动变成正文 `text[1]` + 文末脚注列表
- **图片处理**：`![[image.jpg]]` 自动搜索 Vault 并复制到输出目录
- **多类型提示框**：`[!tip]`/`[!note]`/`[!important]`/`[!warning]`/`[!caution]` 各有独立配色
- **图说识别**：图片后紧跟的斜体段落自动变为居中灰色图说
- **对话气泡**：`:::dialogue[标题]` → 左右交替聊天气泡
- **图片画廊**：`:::gallery[标题]` → 横向滚动多图容器
- **长图展示**：`:::longimage[标题]` → 固定高度纵向滚动容器

### 注意事项

- 依赖可用 `scripts/check_dependencies.py` 检测；缺失时，经用户确认后用 `scripts/check_dependencies.py --install` 安装
- 图片在预览中可见，但粘贴到微信后需要手动上传（或用推送功能自动上传）
- 如果用户对排版不满意，可以切换主题重新生成
- 画廊模式渲染 26 个全量主题，用的是用户的真实文章
