#!/usr/bin/env python3
"""把 pawpulse-system.html 加上「互動拆解流程」面板，輸出 pawpulse-teardown.html。

用法： python3 tools/make_teardown.py
來源頁與輸出頁都在同一個資料夾；不修改原本的 system 頁。

設計原則：
- 不改幾何，只驅動既有的 PARTS / camera / controls
- 每一步只顯示一個零件，標籤與引線同步（用 .td-hide + !important 壓過頁面每幀的重繪）
- 步驟資料寫在 STEPS，改內容只要改這個檔
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "pawpulse-system.html")
DST = os.path.join(HERE, "..", "pawpulse-teardown.html")

SCORE = "可維修 7.0 / 10"

# (零件 id, 標題, 工具, 時間, 警告, 設計註記)
STEPS = [
    ("screw", "背蓋螺絲 M1.6 ×2", "十字 M1.6 起子", "1 分",
     "兩顆螺絲先拆，別用電動起子——M1.6 扭力上限約 0.15 N·m，鎖爆銅螺母就整組報廢。",
     "這是改版後新增的可拆路徑：換電池只需這一支起子。"),
    ("back", "可拆背蓋（2 螺絲 + 2 卡扣）", "塑膠撬棒", "2 分",
     "螺絲拆完還有兩個懸臂卡扣（L≈12 mm），沿長邊縫隙推開，不要從走帶槽那端硬扳。",
     "卡扣應變設計在 1.25%，可反覆拆裝；ABS 自攻柱已改熱熔銅螺母。"),
    ("oring", "防水 O 環（Ø1.0）", "鑷子", "1 分",
     "拆下來就換新環——壓縮過的矽膠不會回復原狀，重裝會漏水。",
     "O 環溝 1.3 × 0.72，壓縮 28%、填充率 84%；這是 IPX6 的唯一密封面。"),
    ("batt", "鋰聚合物電池 500 mAh", "斜口鉗 + 焊台", "5 分",
     "鋁塑膜禁止用金屬撬；先剪線再取，兩條線分開剪，避免短路。",
     "電池仍是焊在 BAT 焊盤上——下一版改 JST-SH 1.25 座，換電池才真的不用焊台。"),
    ("motor", "震動馬達 Ø10", "鑷子", "1 分",
     "漆包線拉到就斷，從 Ø10 圓槽側面輕推出來。",
     "震動經中框傳導；裝回要貼平，否則會有異音。"),
    ("pogo", "充電 pogo pin ×2", "鑷子", "2 分",
     "Ø1.5 mm、彈簧行程 0.8 mm，歪 0.1 mm 就接觸不良。",
     "IPX6 靠 pin 座 O 環＋背蓋 O 環；兩道一起失效才會進水。"),
    ("mag", "磁吸定位磁鐵 ×2", "鑷子", "1 分",
     "磁極方向錯了會排斥，拆前先做記號；Ø5×2 會被起子吸走。",
     "磁鐵槽是點膠固定，重裝要重新點膠。"),
    ("pcb", "主電路板（4 層）", "十字 M1.4 起子", "3 分",
     "取出前先斷電池線，否則拆裝時會短路。",
     "四角是 M1.4 熱熔銅螺母，可重複拆裝 20 次以上（原本 ABS 自攻只有 3–5 次）。"),
    ("fpc", "FPC 軟排線（12 pin）", "鑷子", "1 分",
     "ZIF 扣往上掀 90°，不是往後拉；金手指方向只有一種。",
     "彎折半徑 ≥1 mm；裝回時不要壓在電池上方。"),
    ("mid", "中框（螢幕支架）", "十字 M1.4 起子", "2 分",
     "中框同時是遮光件與 PCB 定位基準，裝回前確認四個銅螺母沒有被頂出。",
     "中框是更換螢幕的必經件；這也是為什麼螢幕只給 1 分。"),
    ("screen", "2.5 吋螢幕模組", "十字 M1.4 起子 + 鑷子", "3 分",
     "先解 ZIF 再抬螢幕，不要直接拉排線。",
     "螢幕與玻璃是兩件；玻璃獨立的好處是刮傷不用換整片。"),
    ("lid", "上蓋玻璃（滿版黑玻璃）", "加熱台 60°C + 吸盤 + 薄刀片", "6–10 分",
     "沿邊緣 360° 均勻加熱，刀片只進 0.5 mm；玻璃 0.55 mm 厚，翹超過 5° 就裂。",
     "玻璃是膠合的，不是螺絲；這是全機唯一還需要加熱分離的位置。"),
    ("strap", "錶帶（20 mm 織帶）", "—", "1 分",
     "走帶槽改深 6.0 mm、高 4.5 mm、邊緣 R2.5，織帶不用再被折 180°。",
     "改版前槽深只有 2.4 mm，折彎半徑 1.2 mm、外緣應變 51%，是磨損來源。"),
    ("cradle", "磁吸套框（僅嘉蘭二號）", "—", "1 分",
     "表頭吸在套框上，拔起即充電；套框不參與防水，水氣由背蓋 O 環擋住。",
     "二號多這一層模組化：表頭可整顆拔下，配戴與充電都不必拆機。"),
]

INJECT = """
<style>
#tdp{position:fixed;left:0;right:0;bottom:0;z-index:40;background:rgba(18,20,17,.95);
  backdrop-filter:blur(10px);color:#eceae4;font-family:-apple-system,"Noto Sans TC",sans-serif;
  border-top:1px solid rgba(255,255,255,.14);max-height:46vh;overflow:auto}
#tdp .hd{display:flex;align-items:center;gap:10px;padding:10px 14px 6px}
#tdp .hd b{font-size:14px}
#tdp .score{font-size:12px;color:#c9f24d;border:1px solid #c9f24d55;border-radius:99px;padding:2px 9px}
#tdp .step{padding:0 14px 4px;font-size:12px;color:#9aa093}
#tdp .body{padding:0 14px 14px}
#tdp h3{margin:4px 0 8px;font-size:16px}
#tdp .meta{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}
#tdp .meta span{font-size:11.5px;background:rgba(255,255,255,.08);border-radius:99px;padding:3px 9px;color:#d8d5cc}
#tdp p{margin:6px 0;font-size:13px;line-height:1.65;color:#d8d5cc}
#tdp p.warn{color:#ffb4a2}
#tdp p.note{color:#a9d5c4;border-left:2px solid #2f6f5e;padding-left:8px}
#tdp .nav{display:flex;gap:8px;padding:0 14px 14px;position:sticky;bottom:0;
  background:linear-gradient(transparent,rgba(18,20,17,.96) 40%)}
#tdp button{flex:1;font:inherit;font-size:13.5px;padding:10px 0;border-radius:10px;
  border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.06);color:#eceae4}
#tdp button:disabled{opacity:.35}
#tdp .dots{display:flex;gap:4px;padding:0 14px 8px;flex-wrap:wrap}
#tdp .dots i{width:18px;height:4px;border-radius:2px;background:rgba(255,255,255,.18)}
#tdp .dots i.on{background:#c9f24d}
#tdp .hint{font-size:11px;color:#8a9084;padding:0 14px 8px}
.lbl.td-hide{display:none !important}
#lead polyline.td-hide{display:none !important}
@media(max-width:560px){#tdp{max-height:56vh}#tdp h3{font-size:15px}}
</style>
<div id="tdp" hidden>
  <div class="hd"><b>拆解流程・嘉蘭一號</b><span class="score">__SCORE__</span></div>
  <div class="step" id="tdstep"></div>
  <div class="dots" id="tddots"></div>
  <div class="body">
    <h3 id="tdtitle"></h3>
    <div class="meta"><span id="tdtool"></span><span id="tdtime"></span></div>
    <p class="warn" id="tdwarn"></p>
    <p class="note" id="tdnote"></p>
  </div>
  <div class="nav">
    <button id="tdprev">← 上一步</button>
    <button id="tdnext">下一步 →</button>
  </div>
  <div class="hint">拖曳可旋轉；只有當前步驟的零件留在畫面上。← → 也可切換。</div>
</div>
<script>
(function(){
  var STEPS=__STEPS__;
  var i=0, tdp=document.getElementById('tdp'), on=false;
  function parts(){return window.PARTS||[];}
  function find(id){return parts().filter(function(p){return p.def&&p.def.id===id;})[0];}
  function list(){return STEPS.filter(function(s){return !!find(s.id);});}
  function frame(rec){
    try{
      var g=rec.g, box=new THREE.Box3().setFromObject(g);
      var c=box.getCenter(new THREE.Vector3()), sz=box.getSize(new THREE.Vector3());
      var r=Math.max(sz.x,sz.y,sz.z)||10, d=Math.max(r*2.6,55);
      controls.target.copy(c);
      camera.position.set(c.x+d*0.55,c.y+d*0.62,c.z+d*0.95);
      camera.lookAt(c); controls.update();
    }catch(e){}
  }
  function syncLbl(){
    var o=window.__tdO||0, L=document.querySelectorAll('.lbl'), P=document.querySelectorAll('#lead polyline'), i;
    for(i=0;i<L.length;i++) L[i].classList.toggle('td-hide', i!==o-1);
    for(i=0;i<P.length;i++) P[i].classList.toggle('td-hide', !(i===2*(o-1)||i===2*(o-1)+1));
  }
  function show(k){
    var arr=list();
    i=Math.max(0,Math.min(arr.length-1,k));
    var st=arr[i], rec=find(st.id);
    parts().forEach(function(p){ if(p.g) p.g.visible=false; });
    if(rec&&rec.g) rec.g.visible=true;
    window.__tdO = rec && rec.def ? rec.def.o : 0;
    document.getElementById('tdstep').textContent='步驟 '+(i+1)+' / '+arr.length;
    document.getElementById('tdtitle').textContent=st.n;
    document.getElementById('tdtool').textContent='工具：'+st.tool;
    document.getElementById('tdtime').textContent='時間：'+st.t;
    document.getElementById('tdwarn').textContent='⚠ '+st.w;
    document.getElementById('tdnote').textContent=st.note;
    document.getElementById('tdprev').disabled=(i===0);
    document.getElementById('tdnext').disabled=(i===arr.length-1);
    document.getElementById('tddots').innerHTML=arr.map(function(_,k){
      return '<i class="'+(k===i?'on':'')+'"></i>';}).join('');
    if(rec) frame(rec);
    syncLbl();
  }
  function start(){
    if(on) return; on=true; tdp.hidden=false;
    var b=document.querySelector('#bar button[data-mode="exploded"]'); if(b) b.click();
    setTimeout(function(){ show(i); },260);
  }
  (function tick(){ if(on) syncLbl(); requestAnimationFrame(tick); })();
  var mo=new MutationObserver(function(){ if(on) syncLbl(); });
  ['#labels','#lead'].forEach(function(sel){ var el=document.querySelector(sel); if(el) mo.observe(el,{childList:true,subtree:true}); });
  window.__td={start:start,show:show,sync:syncLbl,get i(){return i;},
    get steps(){return list().length;},
    get visible(){return parts().filter(function(p){return p.g&&p.g.visible;}).length;}};
  document.getElementById('tdprev').onclick=function(){show(i-1);};
  document.getElementById('tdnext').onclick=function(){show(i+1);};
  document.addEventListener('keydown',function(e){
    if(!on) return;
    if(e.key==='ArrowRight'){show(i+1);e.preventDefault();}
    if(e.key==='ArrowLeft'){show(i-1);e.preventDefault();}
  });
  (function auto(){
    if(window.__ready && (window.PARTS||[]).length){ start(); return; }
    setTimeout(auto,400);
  })();
})();
</script>
"""


def main():
    html = open(SRC, encoding="utf-8").read()
    steps = [{"id": a, "n": b, "tool": c, "t": d, "w": e, "note": f} for a, b, c, d, e, f in STEPS]
    block = (INJECT.replace("__SCORE__", SCORE)
                   .replace("__STEPS__", json.dumps(steps, ensure_ascii=False)))
    assert "</body>" in html
    out = html.replace("</body>", block + "\n</body>")
    open(DST, "w", encoding="utf-8").write(out)
    print(f"{DST}  {len(out.encode())} bytes  steps={len(STEPS)}")


if __name__ == "__main__":
    main()
