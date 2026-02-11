# Mewgenics 繁體中文本地化 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 將 Mewgenics 遊戲的 19 個 CSV 翻譯檔從簡體中文轉換為台灣繁體中文，包含字形、詞彙及語氣的完整本地化。

**Architecture:** 兩階段混合方案——先用 OpenCC `s2twp` 批次自動轉換所有檔案（處理字形+台灣慣用詞），再逐檔人工審校調整語感和遊戲術語。轉換腳本只修改 CSV 中的 `en` 和 `zh` 兩欄，保護其他語言欄位、KEY 欄、遊戲標記語法（`[m:happy]`、`[b]`、`{catname}` 等）不受影響。

**Tech Stack:** Python 3 + OpenCC (PyPI: `opencc-python-reimplemented`)

---

## 專案結構

```
Mewgenics_CN_patch/data/text/
├── additions.csv        (437 行, 47KB)
├── additions2.csv       (254 行, 23KB)
├── additions3.csv       (8 行, 650B)
├── pronouns.csv         (41 行, 3.6KB)
├── progression.csv      (193 行, 63KB)
├── mutations.csv        (289 行, 104KB)
├── teamnames.csv        (353 行, 38KB)
├── weather.csv          (448 行, 44KB)
├── keyword_tooltips.csv (613 行, 168KB)
├── cutscene_text.csv    (662 行, 155KB)
├── misc.csv             (883 行, 121KB)
├── furniture.csv        (1270 行, 122KB)
├── enemy_abilities.csv  (2399 行, 52KB)
├── passives.csv         (2706 行, 686KB)
├── units.csv            (3001 行, 311KB)
├── abilities.csv        (5150 行, 1.2MB)
├── items.csv            (5153 行, 785KB)
├── npc_dialog.csv       (6509 行, 1.6MB)
└── events.csv           (22734 行, 2.0MB)
```

**CSV 格式:** `KEY,en,notes,sp,fr,de,it,pt-br,zh`
- 轉換目標：`en` 欄（index 1）和 `zh` 欄（index 8）
- 保護不動：`KEY`（index 0）、`notes`（index 2）、其他語言欄（index 3-7）

## 翻譯原則

- **風格定位：** 台灣繁體中文，忠於原文黑色幽默，不淡化不加料
- **字形：** 簡體→繁體（OpenCC 自動處理）
- **詞彙：** 使用台灣慣用詞（OpenCC `s2twp` 自動處理大部分，如 信息→資訊）
- **語氣：** 在不偏離原意的前提下，微調不自然的表達
- **遊戲標記：** `[m:xxx]`、`[s:xxx]`、`[b]`、`[/b]`、`[a:xxx]`、`[/a]`、`{catname}`、`{he}`、`{his}` 等一律保持原樣
- **專有名詞：** 角色名（Guillotina、Pyrophina、Thomas A. Beanies 等）保持原樣

---

## Task 1: 安裝 OpenCC 並驗證環境

**Files:**
- 無檔案修改

**Step 1: 安裝 OpenCC**

Run: `pip3 install opencc-python-reimplemented`

**Step 2: 驗證安裝成功**

Run:
```python
python3 -c "from opencc import OpenCC; cc = OpenCC('s2twp'); print(cc.convert('信息软件鼠标'))"
```
Expected: `資訊軟體滑鼠`

---

## Task 2: 編寫批次轉換腳本

**Files:**
- Create: `scripts/convert_s2twp.py`

**Step 1: 編寫轉換腳本**

腳本需求：
- 讀取 `Mewgenics_CN_patch/data/text/` 下所有 CSV 檔案
- 使用 Python `csv` 模組正確解析 CSV（處理引號內的逗號和換行）
- 只對 index 1 (`en`) 和 index 8 (`zh`) 欄位執行 OpenCC `s2twp` 轉換
- 跳過空行和註釋行（以 `//` 開頭的 KEY）
- 保護遊戲標記語法不被錯誤轉換（標記內的英文本身不含中文，所以不需特殊處理）
- 寫回原檔案，保持 CSV 格式完整（注意：原始檔案使用 CSV 引號包裹含逗號/換行的欄位）
- 輸出轉換統計（檔案名、處理行數、修改行數）

```python
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
```

**Step 2: 確認腳本語法正確**

Run: `python3 -c "import ast; ast.parse(open('scripts/convert_s2twp.py').read()); print('OK')"`
Expected: `OK`

---

## Task 3: 執行轉換並驗證結果

**Step 1: 備份原始檔案**

Run: `cp -r Mewgenics_CN_patch/data/text Mewgenics_CN_patch/data/text_backup`

**Step 2: 執行轉換腳本**

Run: `python3 scripts/convert_s2twp.py`
Expected: 列出 19 個檔案的轉換統計

**Step 3: 驗證 CSV 結構完整性**

用 Python 驗證所有轉換後的 CSV 都能正確解析，且行數與轉換前一致：

Run:
```python
python3 -c "
import csv, os
text_dir = 'Mewgenics_CN_patch/data/text'
backup_dir = 'Mewgenics_CN_patch/data/text_backup'
for f in sorted(os.listdir(text_dir)):
    if not f.endswith('.csv'): continue
    with open(os.path.join(text_dir, f)) as a, open(os.path.join(backup_dir, f)) as b:
        ra, rb = list(csv.reader(a)), list(csv.reader(b))
        status = 'OK' if len(ra) == len(rb) else 'MISMATCH'
        print(f'{f:30s} {len(ra):6d} rows  {status}')
"
```
Expected: 所有檔案顯示 `OK`

**Step 4: 抽查轉換品質**

用 diff 檢查幾個代表性檔案的轉換差異：

Run: `diff Mewgenics_CN_patch/data/text_backup/misc.csv Mewgenics_CN_patch/data/text/misc.csv | head -60`

確認：
- 繁體字形轉換正確（发→發、进→進 等）
- 台灣詞彙替換正確（如有）
- 遊戲標記完整無損
- 其他語言欄位未被修改
- KEY 欄位未被修改

**Step 5: 刪除備份**

確認沒問題後：
Run: `rm -rf Mewgenics_CN_patch/data/text_backup`

**Step 6: Commit**

```bash
git add Mewgenics_CN_patch/data/text/*.csv scripts/convert_s2twp.py
git commit -m "feat: OpenCC s2twp 批次轉換簡體中文為繁體中文（台灣）"
```

---

## Task 4: 審校小型檔案（< 500 行，共 8 個）

**Files:**
- Review & modify: `additions3.csv`, `pronouns.csv`, `progression.csv`, `additions2.csv`, `mutations.csv`, `teamnames.csv`, `additions.csv`, `weather.csv`

**審校重點：**
- OpenCC 誤轉檢查（「干」→「乾/幹」、「发」→「髮/發」等多音字）
- 台灣用語自然度（讀起來是否像台灣人會說的話）
- 遊戲術語一致性
- `teamnames.csv` 的形容詞/名詞在隊名組合中是否通順

**Step 1: 逐檔閱讀並修正**

逐一讀取每個檔案，標記並修正不自然的翻譯。

**Step 2: Commit**

```bash
git add Mewgenics_CN_patch/data/text/*.csv
git commit -m "refine: 審校小型檔案繁體中文翻譯"
```

---

## Task 5: 審校中型檔案（500-3000 行，共 6 個）

**Files:**
- Review & modify: `keyword_tooltips.csv`, `cutscene_text.csv`, `misc.csv`, `furniture.csv`, `enemy_abilities.csv`, `passives.csv`

**審校重點：**
- 同 Task 4
- `cutscene_text.csv` 注意敘事語氣
- `misc.csv` 注意 UI 文字的簡潔性
- `keyword_tooltips.csv` 注意遊戲機制說明的準確性
- 建立術語對照表，確保戰鬥相關用語統一（如：傷害、減益、增益、護盾等）

**Step 1: 逐檔閱讀並修正**

**Step 2: Commit**

```bash
git add Mewgenics_CN_patch/data/text/*.csv
git commit -m "refine: 審校中型檔案繁體中文翻譯"
```

---

## Task 6: 審校大型檔案 — units、abilities、items

**Files:**
- Review & modify: `units.csv` (3001 行), `abilities.csv` (5150 行), `items.csv` (5153 行)

**審校重點：**
- 道具名稱的台灣用語自然度（如「外星爆能枪」→ 確認繁體轉換後是否通順）
- 技能/被動描述中的遊戲機制用語統一
- 確保 Task 5 建立的術語對照表在此處一致應用

**Step 1: 逐檔閱讀並修正**

**Step 2: Commit**

```bash
git add Mewgenics_CN_patch/data/text/*.csv
git commit -m "refine: 審校 units、abilities、items 繁體中文翻譯"
```

---

## Task 7: 審校最大型檔案 — npc_dialog、events

**Files:**
- Review & modify: `npc_dialog.csv` (6509 行), `events.csv` (22734 行)

**審校重點：**
- 這兩個檔案是敘事最密集的，語氣和幽默感最重要
- NPC 對話中角色的說話風格（科學家的瘋狂、各角色的個性）
- 事件敘事的黑色幽默要到位
- `events.csv` 非常大，優先檢查：
  - 含有較長敘事段落的事件
  - 含有幽默/諷刺語氣的事件
  - 簡單機械式描述可快速掃過

**注意：** `events.csv` 有 22734 行，可能需要分批處理。建議按事件類型分段閱讀。

**Step 1: 審校 npc_dialog.csv**

**Step 2: Commit npc_dialog**

```bash
git add Mewgenics_CN_patch/data/text/npc_dialog.csv
git commit -m "refine: 審校 NPC 對話繁體中文翻譯"
```

**Step 3: 審校 events.csv（分批）**

**Step 4: Commit events**

```bash
git add Mewgenics_CN_patch/data/text/events.csv
git commit -m "refine: 審校事件文本繁體中文翻譯"
```

---

## Task 8: 最終驗證與清理

**Step 1: 全檔驗證 CSV 完整性**

Run:
```python
python3 -c "
import csv, os
text_dir = 'Mewgenics_CN_patch/data/text'
for f in sorted(os.listdir(text_dir)):
    if not f.endswith('.csv'): continue
    with open(os.path.join(text_dir, f)) as a:
        rows = list(csv.reader(a))
        print(f'{f:30s} {len(rows):6d} rows  OK')
"
```

**Step 2: 確認無殘留簡體字**

用常見簡體字抽查：

Run: `grep -n '[进发这对与关无还经过该让说认为体问题应该从着对于并将已来于而但与时它没给向被]' Mewgenics_CN_patch/data/text/misc.csv | head -20`

注意：部分簡體字和繁體字共用（如「的」「是」「了」），此處只檢查確定是簡體獨有的字形。

**Step 3: 更新 README**

更新 `README.MD` 說明此為繁體中文翻譯補丁。

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat: 完成 Mewgenics 繁體中文（台灣）本地化翻譯"
```

---

## Session 規劃

| Session | 任務 | 預估 Context 使用 |
|---------|------|-------------------|
| Session 1 | Task 1-3（環境設定 + 自動轉換 + 驗證） | 低，主要是腳本操作 |
| Session 2 | Task 4-5（審校小型 + 中型檔案，共 14 個） | 中高，需讀取約 7000 行文本 |
| Session 3 | Task 6（審校 units + abilities + items） | 高，約 13000 行文本 |
| Session 4 | Task 7（審校 npc_dialog + events） | 很高，約 29000 行，events 需分批 |
| Session 5 | Task 8（最終驗證 + 清理）+ 補漏 | 低 |
