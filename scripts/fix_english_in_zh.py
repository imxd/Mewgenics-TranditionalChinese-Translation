#!/usr/bin/env python3
"""
修正 zh 欄位中夾雜的英文詞。
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "text"

# (檔案, KEY, 舊片段, 新片段) — 針對 zh 欄位做字串替換
FIXES = [
    # items.csv
    ("items.csv", "SETBONUS_CAVEMAN_DESC", "獲得 Brace 5", "獲得護甲 5"),
    ("items.csv", "ARMOR_SLIMYHAT_DESC", "施加僵 immobilize 1", "施加定身 1"),
    ("items.csv", "ARMOR_SLIMYMASK_DESC", "施加僵 immobilize 1", "施加定身 1"),
    ("items.csv", "ARMOR_SLIMYNECKLACE_DESC", "施加僵 immobilize 1", "施加定身 1"),
    ("items.csv", "ITEM_SLAGTIGHT_DESC", "Brace 1。 你的基本攻擊造成 Bruise 1", "護甲 1。 你的基本攻擊造成挫傷 1"),
    ("items.csv", "ARMOR_BUBBLEBOY_DESC", "附帶 Knockback 5 效果", "附帶擊退 5 效果"),
    ("items.csv", "ARMOR_FARTFACE_DESC", "施加 Poison 1", "施加中毒 1"),

    # events.csv
    ("events.csv", "EVENT_HAPPENING_ERUPTION_REW", "巨大丘 mound 流出", "巨大土丘流出"),
    ("events.csv", "EVENT_BEARTRAP_REW2", "憑藉 lightning 快速的反應", "憑藉閃電般快速的反應"),

    # passives.csv
    ("passives.csv", "PASSIVE_BOWLINGBALL_DESC", "加成技能 Bowl。", "加成技能碗。"),
    ("passives.csv", "PASSIVE_BOWLINGBALL2_DESC", "加成技能 Bowl+。", "加成技能碗+。"),
]


def main():
    # 按檔案分組
    files = {}
    for filename, key, old, new in FIXES:
        files.setdefault(filename, []).append((key, old, new))

    total = 0
    for filename, fixes in files.items():
        filepath = DATA_DIR / filename
        with open(filepath, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)

        count = 0
        for i, row in enumerate(rows):
            if len(row) < 9:
                continue
            for key, old_str, new_str in fixes:
                if row[0] == key and old_str in row[8]:
                    row[8] = row[8].replace(old_str, new_str)
                    count += 1
                    print(f"  [{key}] {old_str} → {new_str}")

        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerows(rows)

        print(f"  {filename}: {count} 筆修正\n")
        total += count

    print(f"總計: {total} 筆修正")


if __name__ == "__main__":
    main()
