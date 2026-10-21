#!/bin/bash
# 出圖：A 版三視圖 + B 版組裝
set -e
cd "$(dirname "$0")/.."
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
U="http://localhost:8765/3D%E5%BB%BA%E6%A8%A1/2026-10-21/pawpulse-system.html?shot=1"
shoot () {
  local q="$1"; local out="$2"
  "$CH" --headless=new --no-sandbox --hide-scrollbars --use-angle=swiftshader \
    --enable-unsafe-swiftshader --disable-gpu-sandbox --virtual-time-budget=9000 \
    --window-size=1400,900 --screenshot="$out" "${U}&${q}" >/dev/null 2>&1 || true
  echo "$out $(stat -f%z "$out" 2>/dev/null || echo FAIL)"
}
shoot "view=asm&variant=a"      preview-collar-a-asm.png
shoot "view=exploded&variant=a" preview-collar-a-exploded.png
shoot "view=dims&variant=a"     preview-collar-a-dims.png
shoot "view=asm&variant=b"      preview-collar-b-asm.png
