---
name: wechat-history-article-archive
description: Archive or back up historical WeChat official-account mass-send articles for an account the user owns or is explicitly authorized to operate. Use when Codex needs to collect, normalize, and save a公众号's历史群发文章 links, fetch article pages in batch, export local HTML/metadata archives, or build a lawful backup workflow for self-owned WeChat article history without relying on unofficial private APIs.
---

# wechat-history-article-archive

备份自己公众号的历史群发文章，不假设存在“官方一键全量导出历史群发”的通用接口。先用合规方式拿到文章 URL 列表，再批量归档页面和元数据。

## Scope

- 只处理用户**自己拥有**或**明确授权**运营的公众号历史群发文章。
- 优先使用公众号后台里用户可见、可复制、可导出的历史文章链接。
- 不要求 `AppID` / `AppSecret`，因为历史群发文章备份的关键输入通常是**文章 URL 列表**，不是官方素材接口。
- 不把“永久素材导出”误当成“全部历史群发文章导出”。

## Bundled Scripts

- `scripts/extract_mp_urls.py`
  - 从文本、HTML、剪贴后的页面源码、CSV 片段或笔记里提取 `mp.weixin.qq.com/s?...` 文章链接
  - 去重并输出一行一个 URL 的清单
- `scripts/archive_article_urls.py`
  - 读取 URL 清单，批量抓取文章公开页
  - 默认保存 Markdown、元数据 JSON、索引 CSV/JSON 和本地图片
  - 仅在显式传入 `--keep-html` 时保留中间态 `article.html`
- `scripts/convert_archive_to_markdown.py`
  - 把已归档的 `article.html` 批量转换成 `article.md`
  - 下载正文图片到每篇文章目录下的 `images/`
  - 可选用 `--delete-html` 删除历史遗留的 `article.html`

## Workflow

### 1. Confirm the source of the history links

先确认历史群发文章链接从哪里来。优先顺序：

1. 用户从公众号后台“已群发”页手动复制的文章链接
2. 用户从公众号后台导出的表格、页面源码或粘贴文本
3. 当前环境**明确提供**浏览器自动化能力，且用户已经登录自己的公众号后台，此时再做半自动采集

如果当前环境没有可靠浏览器能力，不要编造“官方历史文章接口”；改为让用户提供或导出 URL 列表，再继续归档。

### 2. Normalize the URL list

如果输入不是干净的一行一个链接，先运行：

```powershell
C:\Users\13439\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe `
  .\wechat\wechat-history-article-archive\scripts\extract_mp_urls.py `
  --input .\history-source.txt `
  --output .\wechat\wechat-history-article-archive\output\history-urls.txt
```

可移植形式：

```bash
python3 ./wechat/wechat-history-article-archive/scripts/extract_mp_urls.py \
  --input ./history-source.txt \
  --output ./wechat/wechat-history-article-archive/output/history-urls.txt
```

### 3. Archive the article pages

对整理好的 URL 清单运行：

```powershell
C:\Users\13439\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe `
  .\wechat\wechat-history-article-archive\scripts\archive_article_urls.py `
  --input .\wechat\wechat-history-article-archive\output\history-urls.txt `
  --output-dir .\wechat\wechat-history-article-archive\output\archive
```

可移植形式：

```bash
python3 ./wechat/wechat-history-article-archive/scripts/archive_article_urls.py \
  --input ./wechat/wechat-history-article-archive/output/history-urls.txt \
  --output-dir ./wechat/wechat-history-article-archive/output/archive
```

默认会输出：

- `index.json`
- `index.csv`
- `articles/<slug>/article.md`
- `articles/<slug>/meta.json`
- `articles/<slug>/images/*`

如果已有一批 `article.html`，也可以后处理转换：

```powershell
C:\Users\13439\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe `
  .\wechat\wechat-history-article-archive\scripts\convert_archive_to_markdown.py `
  --archive-dir .\wechat\wechat-history-article-archive\output\archive `
  --delete-html
```

### 4. Review failures and retry carefully

如果部分链接失败：

- 检查 URL 是否失效、是否被删除、是否需要登录态
- 降低抓取速度，避免短时间高频请求
- 不要尝试绕过验证码、风控、登录限制或未公开接口

### 5. Optional follow-up

归档完成后，如用户要继续做内容迁移、排版或二次发布：

- 对单篇或批量文章做结构化整理
- 必要时再衔接 `../wechat-format/SKILL.md`

## Configuration

默认不需要 `config.json`。如需固定参数，可在本 skill 目录下创建本地 `config.json`，参考 `config.example.json`。不要提交真实本地配置。

## Output Expectations

完成任务时，向用户明确说明：

- 一共识别出多少条历史文章 URL
- 成功归档多少篇，失败多少篇
- 归档目录位置
- 是否存在“只有永久素材，没有历史群发全量接口”的边界

## Safety Rules

- 只对用户自己的公众号做历史文章备份。
- 不使用未公开私有接口，不抓取未授权第三方公众号历史数据。
- 不把 Cookie、Token、真实导出数据或本地 `config.json` 提交进仓库。
- 如果需要浏览器自动化，先确认当前环境真的提供该能力，再使用；否则退回到“用户提供 URL 列表”的流程。
