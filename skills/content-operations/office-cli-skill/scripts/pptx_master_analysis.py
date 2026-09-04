"""
分析 PPTX 文件的 布局→幻灯片 关系，并清空所有 Slider。
用法: python pptx_master_analysis.py <文件路径.pptx>
"""

import sys
import zipfile
import xml.etree.ElementTree as ET
import re
import os
import shutil
import subprocess
from typing import Dict, List, Optional, Tuple

try:
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

NS = {
    "r": "http://schemas.openxmlformats.org/package/2006/relationships",
}


# ==================== officecli 调用 ====================

def _officecli_cmd(args: List[str]) -> List[str]:
    configured = os.environ.get("OFFICECLI_BIN")
    if configured:
        return [configured] + args
    executable = shutil.which("officecli")
    if executable:
        return [executable] + args
    raise FileNotFoundError(
        "officecli was not found; install it or set OFFICECLI_BIN to the executable path"
    )


def _run_officecli(args: List[str], timeout: int = 120) -> Tuple[int, str]:
    cmd = _officecli_cmd(args)
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout)
        output = result.stdout.decode("utf-8", errors="replace")
        if not output and result.stderr:
            output = result.stderr.decode("utf-8", errors="replace")
        return (result.returncode, output.strip())
    except Exception as e:
        return (1, str(e))


def _run_officecli_checked(args: List[str], timeout: int = 120) -> None:
    """运行 officecli 命令，失败时打印警告"""
    rc, out = _run_officecli(args, timeout)
    if rc != 0:
        print("  警告: officecli 失败: {}".format(out))


# ==================== ZIP 只读分析 ====================

def parse_rels(zf: zipfile.ZipFile, rels_path: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    try:
        with zf.open(rels_path) as f:
            tree = ET.parse(f)
            for rel in tree.findall(".//r:Relationship", NS):
                rid = rel.get("Id")
                target = rel.get("Target")
                if rid and target:
                    result[rid] = target
    except KeyError:
        pass
    return result


def extract_layout_id(target: str) -> Optional[int]:
    m = re.search(r"slideLayout(\d+)\.xml", target)
    return int(m.group(1)) if m else None


def get_file_indices(zf: zipfile.ZipFile, pattern: str) -> List[int]:
    indices = []
    for name in zf.namelist():
        m = re.match(pattern, name)
        if m:
            indices.append(int(m.group(1)))
    return sorted(indices)


def build_slide_to_layout(zf: zipfile.ZipFile, slide_indices: List[int]) -> Dict[int, int]:
    mapping: Dict[int, int] = {}
    for si in slide_indices:
        rels_path = "ppt/slides/_rels/slide{}.xml.rels".format(si)
        for target in parse_rels(zf, rels_path).values():
            lid = extract_layout_id(target)
            if lid is not None:
                mapping[si] = lid
                break
    return mapping


# ==================== 主流程 ====================

def analyze(pptx_path: str) -> None:
    if not os.path.exists(pptx_path):
        print("错误: 文件不存在: {}".format(pptx_path))
        sys.exit(1)

    # 确保没有残留的 resident 进程
    _run_officecli(["close", pptx_path])

    # ====== 第一步：Python 只读分析，找出哪些 layout 被使用了 ======
    with zipfile.ZipFile(pptx_path, "r") as zf:
        slide_indices = get_file_indices(zf, r"ppt/slides/slide(\d+)\.xml$")
        slide_to_layout = build_slide_to_layout(zf, slide_indices)

    used_layouts = sorted(set(slide_to_layout.values()))
    # {原始编号 → 新编号}: Layout 1→1, Layout 3→2
    layout_seq: Dict[int, int] = {}
    for seq, orig in enumerate(used_layouts, 1):
        layout_seq[orig] = seq

    # ====== 第二步：officecli raw-set 重命名使用的 layout ======
    for orig, seq in layout_seq.items():
        part = "ppt/slideLayouts/slideLayout{}.xml".format(orig)
        new_name = "布局{}".format(seq)
        _run_officecli_checked([
            "raw-set", pptx_path, part,
            "--xpath", "/p:sldLayout/p:cSld",
            "--action", "setattr",
            "--xml", "name={}".format(new_name),
        ])

    # ====== 第三步：officecli view text + close ======
    _, text_output = _run_officecli(["view", pptx_path, "text"])
    _run_officecli(["close", pptx_path])

    texts: Dict[int, str] = {}
    blocks = re.split(r"^=== /slide\[(\d+)\] ===\s*$", text_output, flags=re.MULTILINE)
    for i in range(1, len(blocks), 2):
        si = int(blocks[i])
        content = blocks[i + 1] if i + 1 < len(blocks) else ""
        texts[si] = content.strip()

    # ====== 第四步：输出树形图 ======
    layout_slides: Dict[int, List[int]] = {}
    for si, li in slide_to_layout.items():
        layout_slides.setdefault(li, []).append(si)

    print("=" * 60)
    print("原始文件母版及布局使用情况")
    print("=" * 60)

    for orig in used_layouts:
        seq = layout_seq[orig]
        print("    └─ 布局{}".format(seq))
        for si in layout_slides.get(orig, []):
            print("        └─ Slider {}".format(si))
            text = texts.get(si, "")
            if text:
                single_line = text.replace("\n", "\\n").replace("\r", "")
                print("        |      └─ 文本内容: {}".format(single_line))
            else:
                print("        |      └─ 文本内容: ")

    # ====== 第五步：officecli 删除所有 slider ======
    for si in sorted(slide_indices, reverse=True):
        _run_officecli_checked(["remove", pptx_path, "/slide[{}]".format(si)])

    _run_officecli(["close", pptx_path])

    print("\n所有slider已删除，接下来根据文本内容选择从哪个layout新建页面")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python {} <文件路径.pptx>".format(sys.argv[0]))
        sys.exit(1)
    analyze(sys.argv[1])
