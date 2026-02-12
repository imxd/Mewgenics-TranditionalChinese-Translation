#!/usr/bin/env python3
"""
掃描 UI tooltip 類 CSV 的 zh 欄位，
找出連續超過 10 個中文字之間沒有任何標點符號的段落。
"""

import csv
import re
from pathlib import Path

THRESHOLD = 10

TARGET_FILES = [
    "abilities.csv",
    "enemy_abilities.csv",
    "passives.csv",
    "items.csv",
    "keyword_tooltips.csv",
    "mutations.csv",
    "units.csv",
]

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "text"

# 移除遊戲標記：[b]...[/b], [s:.7]...[/s], [c:red]...[/c], [a:wave]...[/a],
# [img:shield], [br], [m:happy], {variable} 等
TAG_PATTERN = re.compile(
    r"\[/?[a-z]+(?::[^\]]*)?\]"  # [tag], [tag:param], [/tag]
    r"|"
    r"\{[a-zA-Z_]+\}"  # {variable}
)

# 匹配連續 CJK 字元（中間不含任何標點、空格、數字、英文）
CJK_RUN = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]+")


def strip_tags(text: str) -> str:
    """移除遊戲標記，保留純文本。"""
    return TAG_PATTERN.sub("", text)


def scan_file(filepath: Path) -> list[dict]:
    """掃描單一 CSV 檔案，回傳問題列表。"""
    issues = []
    with open(filepath, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 9:
                continue
            key = row[0]
            if key.startswith("//") or key == "KEY":
                continue
            zh = row[8].strip()
            if not zh:
                continue

            cleaned = strip_tags(zh)
            # 找出所有連續 CJK 字元的片段
            for match in CJK_RUN.finditer(cleaned):
                run = match.group()
                if len(run) > THRESHOLD:
                    issues.append({
                        "key": key,
                        "segment": run,
                        "cjk_count": len(run),
                    })
    return issues


def main():
    total = 0
    for filename in TARGET_FILES:
        filepath = DATA_DIR / filename
        if not filepath.exists():
            print(f"[跳過] {filename} 不存在")
            continue

        issues = scan_file(filepath)
        if not issues:
            continue

        print(f"\n{'='*60}")
        print(f"  {filename} ({len(issues)} 筆)")
        print(f"{'='*60}")
        for item in issues:
            print(f"\n  KEY: {item['key']}")
            print(f"  字數: {item['cjk_count']}")
            print(f"  段落: {item['segment']}")
        total += len(issues)

    print(f"\n{'='*60}")
    print(f"總計: {total} 筆連續超過 {THRESHOLD} 個中文字無任何符號")

if __name__ == "__main__":
    main()
