#!/bin/bash
# 出圖：基地台三視圖（組裝／爆炸／尺寸）
set -e
cd "$(dirname "$0")/.."
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
U="http://localhost:8765/3D%E5%BB%BA%E6%A8%A1/2026-10-21/collar-base-system.html?shot=1"
shoot () {
  local q="$1"; local out="$2"
  "$CH" --headless=new --no-sandbox --hide-scrollbars --use-angle=swiftshader \
    --enable-unsafe-swiftshader --disable-gpu-sandbox --virtual-time-budget=9000 \
    --window-size=1400,900 --screenshot="$out" "${U}&${q}" >/dev/null 2>&1 || true
  echo "$out $(stat -f%z "$out" 2>/dev/null || echo FAIL)"
}
shoot "view=asm"      preview-base-asm.png
shoot "view=exploded" preview-base-exploded.png
shoot "view=dims"     preview-base-dims.png
