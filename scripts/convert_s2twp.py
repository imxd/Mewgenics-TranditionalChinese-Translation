#!/usr/bin/env python3
"""
Mewgenics 簡體中文 → 繁體中文（台灣）批次轉換腳本
使用 OpenCC s2twp 配置
"""
import csv
import os
import sys
from opencc import OpenCC


def convert_file(filepath, cc):
    """轉換單一 CSV 檔案的 en 和 zh 欄位"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return 0, 0

    total = 0
    modified = 0

    for i, row in enumerate(rows):
        if i == 0:  # header row
            continue
        if len(row) == 0:
            continue

        changed = False

        # Convert en column (index 1) if it exists and is not empty
        if len(row) > 1 and row[1].strip():
            converted = cc.convert(row[1])
            if converted != row[1]:
                row[1] = converted
                changed = True

        # Convert zh column (index 8) if it exists and is not empty
        if len(row) > 8 and row[8].strip():
            converted = cc.convert(row[8])
            if converted != row[8]:
                row[8] = converted
                changed = True

        total += 1
        if changed:
            modified += 1

    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerows(rows)

    return total, modified


def main():
    cc = OpenCC('s2twp')
    text_dir = os.path.join(os.path.dirname(__file__),
                            '..', 'Mewgenics_CN_patch', 'data', 'text')
    text_dir = os.path.abspath(text_dir)

    csv_files = sorted([f for f in os.listdir(text_dir) if f.endswith('.csv')])

    print(f"找到 {len(csv_files)} 個 CSV 檔案")
    print("-" * 50)

    grand_total = 0
    grand_modified = 0

    for filename in csv_files:
        filepath = os.path.join(text_dir, filename)
        total, modified = convert_file(filepath, cc)
        print(f"{filename:30s}  {total:6d} 行  {modified:6d} 行已修改")
        grand_total += total
        grand_modified += modified

    print("-" * 50)
    print(f"{'總計':30s}  {grand_total:6d} 行  {grand_modified:6d} 行已修改")


if __name__ == '__main__':
    main()
