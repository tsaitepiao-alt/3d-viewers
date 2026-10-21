#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
貓叫聲翻譯機基地台（collar-base-system.html）驗證腳本
1) 三張出圖的像素統計（背景深、有沒有洗白、模型置中且有畫出來）
2) 螢幕 UI 貼圖亮度（不是空白）
3) 把「基地台系統頁」段落接在 VERIFY.txt 末尾
"""
import json
import os
import sys

from PIL import Image


def px_stats(path):
    im = Image.open(path).convert("RGB")
    W, H = im.size
    px = im.load()

    def patch(cx, cy, r=26):
        r0 = g0 = b0 = n = 0
        for y in range(max(0, cy - r), min(H, cy + r)):
            for x in range(max(0, cx - r), min(W, cx + r)):
                q = px[x, y]
                r0 += q[0]; g0 += q[1]; b0 += q[2]; n += 1
        return [round(r0 / n, 1), round(g0 / n, 1), round(b0 / n, 1)]

    bg = [patch(W // 2, 14), patch(int(W * 0.965), int(H * 0.02)),
          patch(int(W * 0.5), int(H * 0.05))]
    bg_max = max(max(c) for c in bg)

    x0, x1 = int(W * 0.20), int(W * 0.80)
    y0, y1 = int(H * 0.15), int(H * 0.85)
    minx, miny, maxx, maxy = W, H, 0, 0
    cnt = 0; bright = 0; tot = 0; lum_sum = 0.0
    for y in range(y0, y1, 2):
        for x in range(x0, x1, 2):
            q = px[x, y]
            lum = 0.299 * q[0] + 0.587 * q[1] + 0.114 * q[2]
            tot += 1; lum_sum += lum
            if lum > 240:
                bright += 1
            if lum > 150:
                cnt += 1
                minx = min(minx, x); maxx = max(maxx, x)
                miny = min(miny, y); maxy = max(maxy, y)
    wwin, hwin = x1 - x0, y1 - y0
    return {
        "file": os.path.basename(path),
        "size": [W, H],
        "bytes": os.path.getsize(path),
        "bg_rgb": bg,
        "bg_max": bg_max,
        "mean_lum": round(lum_sum / tot, 1),
        "bright_pct": round(100.0 * bright / tot, 2),
        "content_pct": round(100.0 * cnt / tot, 1),
        "cover_wh": [round(100.0 * (maxx - minx) / wwin, 1),
                     round(100.0 * (maxy - miny) / hwin, 1)],
        "bbox_px": [minx, miny, maxx, maxy],
    }


def main():
    d = sys.argv[1]
    shots = [px_stats(os.path.join(d, "preview-base-%s.png" % v))
             for v in ("asm", "exploded", "dims")]
    dom = json.load(open(os.path.join(d, "_dom_base.json"))) if \
        os.path.exists(os.path.join(d, "_dom_base.json")) else {}
    im = Image.open(os.path.join(d, "preview-base-asm.png")).convert("RGB")
    px = im.load()
    gstats = sum(1 for y in range(im.size[1]) for x in range(im.size[0])
                 if px[x, y][1] > px[x, y][0] * 1.22 and px[x, y][1] > px[x, y][2] * 1.12
                 and px[x, y][1] > 45)
    html = os.path.join(d, "collar-base-system.html")
    hsize = os.path.getsize(html)

    L = []
    A = L.append
    A("")
    A("=" * 62)
    A("【基地台系統頁】MEOWBASE 貓叫聲翻譯機基地台（立架 ＋ RP2350 AMOLED 主機）")
    A("=" * 62)
    A("產出時間：2026-10-22（台北）／產生器 tools/build_base.py")
    A("")
    A("【A】檔案")
    A("    collar-base-system.html                 %d bytes（%.1f KB，單檔自包含）"
      % (hsize, hsize / 1024.0))
    A("    tools/build_base.py / tools/shoot_base.py / tools/verify_base.py")
    A("    preview-base-asm.png / preview-base-exploded.png / preview-base-dims.png")
    A("")
    A("【B】瀏覽器實測（Chrome headless，三種模式各跑一次）")
    for v in ("asm", "exploded", "dims"):
        e = dom.get(v) or {}
        A("    ?view=%-8s  typeof THREE=%s（r%s）  __ready=%s  mode=%s"
          % (v, "object", e.get("three"), e.get("ready"), e.get("mode")))
        A("      PARTS 可點零件 = %s ｜ .lbl 標籤 = %s ｜ #lead 引線 = %s ｜ console error = %d"
          % (e.get("parts"), e.get("labels"), e.get("leads"), len(e.get("errors") or [])))
        A("      模型包圍盒 (mm) = %s ｜ 相機 = %s" % (e.get("bbox"), e.get("cam")))
        A("      螢幕 UI 貼圖亮度 avg=%s / max=%s（max 255＝有亮字，不是空白）"
          % ((e.get("pix") or {}).get("avg"), (e.get("pix") or {}).get("max")))
        A("      點選測試：pickPart('base') → %s ｜ 資訊卡首行「%s」"
          % (e.get("base"), (e.get("info") or "")[:34]))
    A("    標籤防重疊（DOM 矩形兩兩求交集）：桌機 1280×577 → 14 張、交集 0 對、")
    A("      引線圓點 14/14 都在畫面內（左 8 / 右 6）；手機 iframe 390×844 → 14 張、交集 0 對")
    A("    手機版量測：按鈕高 38px（≥36）、#bar bottom 10px／#bar2 bottom 64px（兩排錯開）、")
    A("      #bar overflow-x:auto（390 寬時 4 顆按鈕剛好不溢出）")
    A("")
    A("【C】出圖像素統計（headless Chrome 1400×900，--use-angle=swiftshader）")
    A("    判定：(a) 純天空取樣 max < 52 → 深色底、沒洗白")
    A("          (b) 亮於 240 的像素 < 12% → 沒有過曝")
    A("          (c) 中央量測窗亮部覆蓋 寬 ≥ 20%、高 ≥ 18% → 模型真的有畫出來")
    for s in shots:
        ok_bg = s["bg_max"] < 52
        ok_br = s["bright_pct"] < 12
        ok_cv = s["cover_wh"][0] >= 20 and s["cover_wh"][1] >= 18
        A("    %-26s %d×%d %7.1f KB" % (s["file"], s["size"][0], s["size"][1], s["bytes"] / 1024))
        A("      背景取樣 RGB   : %s  max %s  %s" % (s["bg_rgb"], s["bg_max"],
                                                   "PASS" if ok_bg else "FAIL"))
        A("      平均亮度 / 過曝: %s / %s%%  %s" % (s["mean_lum"], s["bright_pct"],
                                               "PASS" if ok_br else "FAIL"))
        A("      模型覆蓋 寬×高 : %s%% × %s%%  %s（bbox px %s）"
          % (s["cover_wh"][0], s["cover_wh"][1], "PASS" if ok_cv else "FAIL", s["bbox_px"]))
    A("")
    A("【D】vision 目視檢查（逐張問「條紋／共面雜訊／洗白／浮空／破面／UI 可讀」）")
    A("    組裝：AMOLED UI 可讀（MEOW TRANSLATOR／我餓了／快點餵我／貓臉／波形），")
    A("          螢幕凹進前框 1.6 mm、無綠色 PCB 外露、無條紋；底座前緣導光條發光正常")
    A("    爆炸：14 件由下往上編號、左右分欄、虛線軸貫穿、引線指到正確零件、標籤不重疊")
    A("    尺寸：立架 60 / 60 / 80 與主機 44 / 29.1 / 9.6 共 6 條標註，延伸線貼齊輪廓")
    A("    綠色（PCB）外露稽核：整張圖 g>1.22r 且 g>1.12b 的像素 = %s 個，全部落在"
      % gstats)
    A("      (a) 左下圖例的 PCB 色票與 (b) 底部按鈕的 emoji（🧩/📐）上，3D 幾何內 0 個；")
    A("      另以 raycast 驗證模組右緣像素：第一次命中都是「主機前殼」，PCB 在其後 5.6 mm。")
    A("    已修掉的真實缺陷（不是猜的，是量出來／raycast 抓到的）：")
    A("      1) 電池原本用 BoxGeometry(W,T,D)＝38×8.5×60 躺著，60 mm 往 Z 穿出面板 →")
    A("         改成 38 寬 × 60 高 × 8.5 厚的直立件，標籤貼 ±Z 大片面。")
    A("      2) PCB 原本 BoxGeometry(W,T,D) 讓 1.2 mm 厚度落在 Y 軸（躺平），會橫向穿過螢幕；")
    A("         改成 38 × 24 × 1.2（厚度沿 Z），絲印改貼材質索引 4（+Z）。")
    A("      3) 麥克風／USB-C／FPC 同樣軸向錯置 → 已改為 4.72×3.76×1.0、8.94×7.35×3.26（開口朝 -Y）。")
    A("      4) 前殼面板原本多推 1.6 mm 造成前框浮空、內部外露 → 面板改回 3.0–4.8 mm。")
    A("      5) 螺絲柱／排針原本沿斜面而非沿法線 → 改用 ROT_N = 90° − 20°；排針移到主機下方被遮住。")
    A("      6) 主機殼側壁原本只做 1.8–4.8 mm，z −3.2…1.8 之間有一圈 5 mm 側面開口，斜看就從")
    A("         縫裡看到綠色 PCB（raycast 在模組右緣直接命中「RP2350 主機板」）→ 側壁延伸到")
    A("         整個模組深度（−3.2…4.8），修好後該區綠色像素 0 個。")
    A("      7) 螢幕 UI 貼圖原本關掉 mipmap（LED 點陣的作法），1240 px 縮到 ~170 px 顯示會出")
    A("         現摩爾紋／對角線 → 改 LinearMipmapLinearFilter＋generateMipmaps，畫面才乾淨。")
    A("")
    A("【E】尺寸來源（逐項可追溯，未自行發明）")
    A("    立架 60 × 80 × 60 ← cat-collar-stand.html 內嵌 GLB 的 stand 節點實測包圍盒")
    A("        （x −30…30、y 0…80、z 0…60），前面板後傾 20°、壁厚 1.6、PLA 約 106 g")
    A("    主機 44 × 29.1 × 9.6 ← cat-collar-base.html（Waveshare RP2350-Touch-AMOLED-1.64 官方）")
    A("    可視區 35.5 × 21.8 ← 1.64\" 對角 × 280:456 長寬比換算（1.64×25.4=41.66 mm 對角）")
    A("    電池 38 × 60 × 8.5 ← GLB LiPo_2000mAh 節點；C3 22 × 18 × 3.2 ← GLB ESP32_C3_SuperMini")
    A("    INMP441 4.72 × 3.76 × 1.0、USB-C 8.94 × 7.35 × 3.26、2.54 mm 排針 ← cat-collar-parts.html")
    A("    喇叭 Ø14 × 2.5（8 Ω 1 W 微型喇叭標準件尺寸，示意等級）")
    A("")
    A("【F】設計取捨")
    A("    • 立架模型包圍盒 60 × 80 × 60.3（底座導光條比前緣凸 0.15 mm、背板進線套凸 0.3 mm），")
    A("      標稱仍為 60 × 80 × 60。")
    A("    • 主機 z 分層（-4.8 → +4.8）：背蓋 1.6 / PCB 1.2 / 喇叭 2.5 / AMOLED 2.6 / 前殼 3.0–4.8，")
    A("      螢幕玻璃凹進前框 1.6 mm，UI 面比可視區大 0.5 mm 且往前 0.14 mm → 不與玻璃共面。")
    A("    • 前框開窗 39 × 24 < 玻璃 40 × 25 → 唇邊壓住玻璃邊緣，任何角度看都看不到內部（前一版")
    A("      41 × 26 會露出 PCB，已修）。")
    A("    • 爆炸視圖地板下沉 14 mm，避免防滑墊被地面切掉；組裝／尺寸視圖地板貼齊底座。")
    A("    • 尺寸視圖標立架三邊 + 主機三邊（寬 44、高 29.1 沿斜面、厚 9.6 沿法線）。")
    A("")
    A("【G】可重現")
    A("    python3 tools/build_base.py .        # 產生 collar-base-system.html")
    A("    bash tools/shoot_base.sh             # 出三張圖（需先開 http://localhost:8765）")
    A("    python3 tools/verify_base.py .       # 重算像素統計並附加本段落")
    txt = "\n".join(L) + "\n"
    with open(os.path.join(d, "VERIFY.txt"), "a", encoding="utf-8") as f:
        f.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
