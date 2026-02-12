#!/usr/bin/env python3
"""
批量翻譯 events.csv 和 npc_dialog.csv 中未翻譯的 zh 欄位。
"""

import csv
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "text"

# ============================================================
# 翻譯表：KEY -> 新的 zh 翻譯
# ============================================================

EVENTS_TRANSLATIONS = {
    # === EVENT_FOUNTAIN ===
    "EVENT_FOUNTAIN_REW3_N": "{catname} 感覺頭骨被一股可怕的擠壓感緊縮，頭部縮小了！它們發出可憐的「喵」聲，腦袋變成了小貓的模樣。",
    "EVENT_FOUNTAIN_REW4": "其他貓咪驚訝地看著 {catname} 喝了噴泉的水後縮小成了一隻小貓咪！",
    "EVENT_FOUNTAIN_LEAVE": "{catname} 不渴。",

    # === EVENT_BOXWITHAHOLE ===
    "EVENT_BOXWITHAHOLE_NAME": "有洞的箱子",
    "EVENT_LEGINSIDE_ANSW": "把 {his} 腿伸進洞裡",
    "EVENT_ARMINSIDE_ANSW": "把 {his} 手伸進洞裡",
    "EVENT_TAILINSIDE_ANSW": "把 {his} 尾巴伸進洞裡",
    "EVENT_BOXWITHAHOLE_QUES": "{catname} 發現了一個有洞的紙箱。{He} 好奇裡面會有什麼！{He} 該怎麼做？",
    "EVENT_BOXWITHAHOLE_QUES_N": "{catname} 發現了一個有洞的紙箱。它們好奇裡面會有什麼！該怎麼做？",
    "EVENT_BOXWITHAHOLE_REW1": "{catname} 把 {his} 腿伸進洞裡……{He} 感受到一陣奇怪的刺痛，{his} 的腿發生了突變！",
    "EVENT_BOXWITHAHOLE_REW1_N": "{catname} 把腿伸進洞裡……它們感受到一陣奇怪的刺痛，腿發生了突變！",
    "EVENT_BOXWITHAHOLE_REW2": "{catname} 把 {his} 腿伸進紙箱裡。{He} 感受到一股溫暖湧上來，{his} 的腿感覺棒極了！",
    "EVENT_BOXWITHAHOLE_REW2_N": "{catname} 把腿伸進紙箱裡。它們感受到一股溫暖湧上來，腿感覺棒極了！",
    "EVENT_BOXWITHAHOLE_REW3": "{catname} 把 {his} 腿塞進洞裡，隨即傳來一聲嘎吱巨響，有什麼東西夾住了它！",
    "EVENT_BOXWITHAHOLE_REW4": "{catname} 把 {his} 腿伸進紙箱裡。有什麼東西猛地抓住了它！當 {he} 拼命想要抽出腿時，箱子裡的東西扭了一下……",
    "EVENT_BOXWITHAHOLE_REW4_N": "{catname} 把腿伸進紙箱裡。有什麼東西猛地抓住了它！當它們拼命想要抽出腿時，箱子裡的東西扭了一下……",
    "EVENT_BOXWITHAHOLE_REW5": "{catname} 小心翼翼地把 {his} 爪子伸進洞裡。裡面有什麼東西戳了一下，當 {he} 把爪子抽回來時，{catname} 發現它被強化了！",
    "EVENT_BOXWITHAHOLE_REW5_N": "{catname} 小心翼翼地把爪子伸進洞裡。裡面有什麼東西戳了一下，當它們把爪子抽回來時，{catname} 發現它被強化了！",
    "EVENT_BOXWITHAHOLE_REW6": "{catname} 把 {his} 手伸進紙箱裡。就在那一刻，{catname} 感受到一股力量湧上來，{his} 的爪子發生了突變！",
    "EVENT_BOXWITHAHOLE_REW6_N": "{catname} 把手伸進紙箱裡。就在那一刻，{catname} 感受到一股力量湧上來，爪子發生了突變！",

    # === EVENT_GIANTSLEEPINGSHARK ===
    "EVENT_GIANTSLEEPINGSHARK_NAME": "巨型沉睡鯊魚",
    "EVENT_GIANTSLEEPINGSHARK_QUES": "一隻巨型沉睡鯊魚擋在 {catname} 前方的路上！",
    "EVENT_GIANTSLEEPINGSHARK_REW1": "{catname} 悄悄地繞過去，小心翼翼地不去打擾這隻打盹的鯊魚……",
    "EVENT_GIANTSLEEPINGSHARK_REW2": "當 {catname} 悄悄繞過去時，{he} 成功偷走了鯊魚的寶藏！\n",
    "EVENT_GIANTSLEEPINGSHARK_REW3": "鯊魚醒來並咬向 {catname}！\n\n巨大的牙齒深深地刺進 {catname} 的身體，鮮血四濺。\n",
    "EVENT_GIANTSLEEPINGSHARK_REW4": "鯊魚被 {catname} 激怒了，用{his}巨大的利齒狠狠咬住了 {him}！\n",
    "EVENT_GIANTSLEEPINGSHARK_REW5": "{catname} 成功地從巨型鯊魚身邊逃脫了！",

    # === EVENT_MYSTERIOUSCHAMBER ===
    "EVENT_MYSTERIOUSCHAMBER_REW6": "{catname} 感受到一波平靜感湧上全身，{his} 的病痛全被洗去了。\n",
    "EVENT_MYSTERIOUSCHAMBER_REW7": "密室開始瘋狂地嗶嗶響，然後用一根針筒刺向了 {catname}！\n",
    "EVENT_MYSTERIOUSCHAMBER_REW8": "密室內伸出的機械手臂抓住了 {catname}，往 {him} 體內注射了什麼可怕的東西！\n",
    "EVENT_MYSTERIOUSCHAMBER_REW9": "密室亮了起來，{catname} 被傳送到了一個新的地方！\n",
    "EVENT_MYSTERIOUSCHAMBER_REW10": "密室發出勝利般的嗶嗶聲，然後在一道耀眼的閃光中將 {catname} 傳送走了！\n\n根據密室的反應，{catname} 猜測 {he} 已經在某種程度上獲得了下一場事件的強化……",
    "EVENT_MYSTERIOUSCHAMBER_REW10_N": "密室發出勝利般的嗶嗶聲，然後在一道耀眼的閃光中將 {catname} 傳送走了！\n\n根據密室的反應，{catname} 猜測它們已經在某種程度上獲得了下一場事件的強化……",
    "EVENT_MYSTERIOUSCHAMBER_REW11": "大門砰地關上，{catname} 被送到了一個新的地方……\n\n直接落入了埋伏之中！",
    "EVENT_MYSTERIOUSCHAMBER_REW12": "警報聲響起，密室的大門砰地關上。\n\n當大門開始緩緩滑開時，{catname} 感受到一股恐懼感席捲了 {him}……",

    # === EVENT_MYSTERIOUSMACHINE ===
    "EVENT_MYSTERIOUSMACHINE_NAME": "神秘機器",
    "EVENT_MYSTERIOUSMACHINE_QUES": "{catname} 發現了一台伸出紙張的神秘機器。",
    "EVENT_MYSTERIOUSMACHINE_TURNITON_ANSW": "啟動它",
    "EVENT_MYSTERIOUSMACHINE_REW1": "{catname} 試著敲打機器讓它運作，但什麼都沒發生。\n\n{catname} 更加賣力地再試了一次，結果把機器砸爛了。\n",
    "EVENT_MYSTERIOUSMACHINE_REW2": "{catname} 在機器背面找到一個開關並打開了它。\n\n機器發出一連串響亮的嗶嗶聲和機械聲……",
    "EVENT_MYSTERIOUSMACHINE_REW3": "{catname} 試著按按鈕，還把 {his} 爪子伸進各種洞裡……\n\n{catname} 在電弧從機器中竄出並擊暈 {him} 時嚎叫起來！\n",
    "EVENT_MYSTERIOUSMACHINE_REW4": "{catname} 按了各種按鈕，然後狠狠地拍了機器一下。\n\n機器發出憤怒般的嗶嗶聲，嗡嗡作響地啟動了！",
    "EVENT_MYSTERIOUSMACHINE_REW5": "{catname} 決定不去碰這台奇怪的機器。\n\n{He} 不確定這台機器有什麼用，但紙張聽起來不怎麼實用。",
    "EVENT_MYSTERIOUSMACHINE_REW5_N": "{catname} 決定不去碰這台奇怪的機器。\n\n它們不確定這台機器有什麼用，但紙張聽起來不怎麼實用。",
    "EVENT_MYSTERIOUSMACHINE_COPY_ANSW": "複製",
    "EVENT_MYSTERIOUSMACHINE_SCALE_ANSW": "縮放",
    "EVENT_MYSTERIOUSMACHINE_PRINT_ANSW": "列印",
}

NPC_TRANSLATIONS = {
    # === NPC_BUTCH_UPGRADE_STORAGE_2 ===
    "NPC_BUTCH_UPGRADE_STORAGE_2_1": "[m:happy]你送來的那些貓真是太好用了！",
    "NPC_BUTCH_UPGRADE_STORAGE_2_2": "[m:whispering]我一直在訓練牠們去偷那些老糊塗的藥物。",
    "NPC_BUTCH_UPGRADE_STORAGE_2_3": "[m:default]如約定的，我又幫你升級了物品儲存！",
    "NPC_BUTCH_UPGRADE_STORAGE_2_4": "[m:default]不過下次我需要更強的貓！",
    "NPC_BUTCH_UPGRADE_STORAGE_2_5": "[m:pondering]要有實戰經驗的。\n我說的是去過洞穴或那座老墓地的貓。",
    "NPC_BUTCH_UPGRADE_STORAGE_2_6": "[m:default]謝了，兄弟。",

    # === NPC_BUTCH_UPGRADE_STORAGE_3 ===
    "NPC_BUTCH_UPGRADE_STORAGE_3_1": "[m:default]我的貓軍團持續壯大中！",
    "NPC_BUTCH_UPGRADE_STORAGE_3_2": "[m:default]有了你的幫助，我已經從小偷小摸升級成直接綁架了！",
    "NPC_BUTCH_UPGRADE_STORAGE_3_3": "[m:happy]沒錯，我已經訓練你給我的那些貓去偷老人了！",
    "NPC_BUTCH_UPGRADE_STORAGE_3_4": "[m:whispering]後面那個垃圾桶裡大概塞了六個老人……",
    "NPC_BUTCH_UPGRADE_STORAGE_3_5": "[m:pondering]還不確定要拿他們怎麼辦，但我在想搞個親親攤位什麼的……",
    "NPC_BUTCH_UPGRADE_STORAGE_3_6": "[m:default]我也不知道，反正他們在那裡，需要的時候再說。",
    "NPC_BUTCH_UPGRADE_STORAGE_3_7": "[m:pondering]如果我想更上一層樓，就需要更好的貓……",
    "NPC_BUTCH_UPGRADE_STORAGE_3_8": "[m:default]我只收去過西邊那個碉堡或隕石坑的貓。",
    "NPC_BUTCH_UPGRADE_STORAGE_3_9": "[m:angry]快去辦！",

    # === NPC_BUTCH_UPGRADE_STORAGE_4 ===
    "NPC_BUTCH_UPGRADE_STORAGE_4_1": "[m:happy]聽好了，我已經訓練那些貓騎在我偷來的老人身上了！",
    "NPC_BUTCH_UPGRADE_STORAGE_4_2": "[m:shocked]想像一下一早醒來看到那個畫面！\n",

    # === NPC_STEVEN ===
    "NPC_STEVEN_STEVEN_INTRODUCTION_15": "總之，大概就是這樣了。",
    "NPC_STEVEN_STEVEN_INTRODUCTION_16": "至少在 DLC 出來之前……",
}


def apply_translations(filename: str, translations: dict[str, str]) -> int:
    """
    對指定 CSV 檔案套用翻譯。
    回傳成功替換的數量。
    """
    filepath = DATA_DIR / filename
    if not filepath.exists():
        print(f"[錯誤] {filename} 不存在")
        return 0

    # 讀取整個檔案
    with open(filepath, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    count = 0
    for i, row in enumerate(rows):
        if len(row) < 9:
            continue
        key = row[0]
        if key in translations:
            old_zh = row[8]
            new_zh = translations[key]
            row[8] = new_zh
            count += 1
            print(f"  [{key}]")
            print(f"    舊: {old_zh[:60]}{'...' if len(old_zh) > 60 else ''}")
            print(f"    新: {new_zh[:60]}{'...' if len(new_zh) > 60 else ''}")

    if count == 0:
        print(f"[警告] {filename} 中沒有找到任何匹配的 KEY")
        return 0

    # 寫回檔案
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(rows)

    return count


def main():
    print("=" * 60)
    print("events.csv")
    print("=" * 60)
    events_count = apply_translations("events.csv", EVENTS_TRANSLATIONS)
    print(f"\n已翻譯 {events_count} 筆\n")

    print("=" * 60)
    print("npc_dialog.csv")
    print("=" * 60)
    npc_count = apply_translations("npc_dialog.csv", NPC_TRANSLATIONS)
    print(f"\n已翻譯 {npc_count} 筆\n")

    print("=" * 60)
    print(f"總計: {events_count + npc_count} 筆翻譯已套用")


if __name__ == "__main__":
    main()
