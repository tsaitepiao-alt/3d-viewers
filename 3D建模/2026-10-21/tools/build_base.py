#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEOWBASE 貓叫聲翻譯機 基地台 — 立架 ＋ RP2350 AMOLED 主機
單檔 three.js 互動模型頁產生器（three.js r128 + OrbitControls 內嵌，可離線雙擊）

三模式：組裝 / 爆炸 / 尺寸（操作邏輯與 ELDERCHAT、PawPulse 完全一致）

尺寸來源（不自行發明）：
  立架  cat-collar-stand.html 內嵌 GLB 實測包圍盒：
        stand 節點 x[-30,30] y[0,80] z[0,60] → 60 × 80 × 60 mm、前面板後傾 20°、
        壁厚 1.6、PLA 約 106 g（cat-collar-base.html 進度表）
        背蓋節點 54 × 12 × 24；玻璃節點 40 × 25；PCB 節點 44 × 11.1 × 27.8
  主機  cat-collar-base.html：Waveshare RP2350-Touch-AMOLED-1.64
        44 × 29.1 × 9.6 mm、1.64" 觸控 AMOLED 280 × 456、
        板載 microSD / QMI8658 / PCF85063 / MX1.25 電池座
        可視區 35.5 × 21.8（1.64" 對角、280:456 長寬比換算）
  電池  GLB LiPo_2000mAh 節點 38 × 60 × 8.5 mm
  C3    GLB ESP32_C3_SuperMini 節點 22 × 18 × 3.2 mm（SuperMini 實物 22.5 × 18）
  元件  cat-collar-parts.html：INMP441 4.72 × 3.76 × 1.0、USB-C 16P 母座 8.94 × 7.35 × 3.26、
        排針 2.54 mm pitch、WS2812B 5 × 5 × 1.6、Ø14 微型喇叭 2.5 mm

用法：python3 build_base.py <輸出資料夾> [--libs /path/to/libs]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LIBS = "/Users/william/cat-translator/3d/_libs"

HTML_HEAD = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>貓語翻譯基地台 MEOWBASE ｜ 嘉蘭智慧科技 · 3D 組裝・爆炸・尺寸</title>
<style>
  :root{
    --coral:#ff8a5c; --coral2:#e8734a; --amber:#ffc266; --sky:#7bd3ff;
    --ink:#0b0705; --bg:#080b0d; --txt:#f2ece6; --dim:#a08f84;
    --panel:rgba(20,17,15,.86); --line:rgba(255,138,92,.30);
  }
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{margin:0;height:100%;overflow:hidden;background:var(--bg);color:var(--txt);
    font-family:"PingFang TC","Noto Sans TC","Heiti TC","Microsoft JhengHei",system-ui,sans-serif}
  #app{position:fixed;inset:0}
  canvas{display:block}
  .panel{background:var(--panel);border:1px solid rgba(255,255,255,.09);border-radius:14px;
    backdrop-filter:blur(9px);-webkit-backdrop-filter:blur(9px);box-shadow:0 10px 30px rgba(0,0,0,.45)}

  /* ── 左上標題 ── */
  #hud{position:fixed;left:14px;top:14px;padding:11px 15px;z-index:20;max-width:min(46vw,340px)}
  #hud b{font-size:15px;letter-spacing:.4px;display:block;color:#fff}
  #hud b i{font-style:normal;color:var(--coral)}
  #hud span{font-size:11.5px;color:var(--dim);line-height:1.55;display:block;margin-top:4px}
  #hud .tag{display:inline-block;margin-top:7px;font-size:10.5px;color:var(--coral);
    border:1px solid var(--line);border-radius:999px;padding:2px 9px}
  #hud .tag b{display:inline;font-size:10.5px;color:var(--coral)}

  /* ── 右上資訊卡 ── */
  #finfo{position:fixed;right:14px;top:14px;width:min(336px,44vw);padding:13px 15px 14px;
    display:none;flex-direction:column;gap:7px;z-index:40;border-color:rgba(255,138,92,.35)}
  #finfo h4{margin:0;font-size:15px;color:#fff;display:flex;align-items:center;gap:8px}
  #finfo h4 .n{display:inline-flex;width:22px;height:22px;border-radius:50%;background:var(--coral);
    color:#2a1108;font-size:12px;font-weight:800;align-items:center;justify-content:center;flex:0 0 auto}
  #finfo h4 .x{margin-left:auto;cursor:pointer;color:var(--dim);font-size:15px;padding:0 2px}
  #finfo .row{font-size:12px;line-height:1.62;color:#e6ddd6;display:flex;gap:7px}
  #finfo .row u{text-decoration:none;color:var(--dim);flex:0 0 42px}
  #finfo .row b{font-weight:600;color:#fff}
  #finfo .hint{font-size:10.5px;color:var(--dim);border-top:1px solid rgba(255,255,255,.08);padding-top:7px}

  /* ── 零件標籤（爆炸圖） ── */
  #lblLayer{position:fixed;inset:0;pointer-events:none;z-index:15;display:none}
  #lead{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
  #lead polyline{fill:none;stroke:rgba(255,138,92,.58);stroke-width:1;stroke-dasharray:3 3}
  #lead circle{fill:var(--coral)}
  .lbl{position:absolute;transform:translateY(-50%);display:flex;gap:7px;align-items:flex-start;
    font-size:11.5px;line-height:1.32;color:#f0e7e0;pointer-events:none;
    text-shadow:0 1px 3px rgba(0,0,0,.9)}
  .lbl.left{left:0;padding-right:12px;justify-content:flex-end;text-align:right}
  .lbl.left .b{order:2}
  .lbl.right{right:0;padding-left:12px;justify-content:flex-start;text-align:left}
  .lbl .t{max-width:236px}
  .lbl .b{flex:0 0 auto;width:19px;height:19px;border-radius:50%;background:var(--coral);color:#2a1108;
    font-size:10.5px;font-weight:800;display:flex;align-items:center;justify-content:center;margin-top:1px}
  .lbl .t b{display:block;font-weight:600;font-size:11.8px;color:#fff}
  .lbl .t i{font-style:normal;font-size:10.5px;color:#b6a79d}

  /* ── 底部控制列 ── */
  #bar{position:fixed;left:0;right:0;bottom:10px;padding:0 10px;display:flex;justify-content:center;
    gap:7px;z-index:30;overflow-x:auto;flex-wrap:nowrap;scrollbar-width:none}
  #bar::-webkit-scrollbar{display:none}
  #bar button{flex:0 0 auto;height:38px;min-width:76px;padding:0 14px;border-radius:11px;cursor:pointer;
    border:1px solid rgba(255,255,255,.13);background:rgba(24,19,16,.9);color:#e2d7cf;
    font-size:12.5px;font-family:inherit;font-weight:600;letter-spacing:.3px;
    backdrop-filter:blur(9px);-webkit-backdrop-filter:blur(9px);transition:.16s}
  #bar button:hover{border-color:var(--line);color:#fff}
  #bar button.on{background:var(--coral);color:#2a1108;border-color:var(--coral);
    box-shadow:0 6px 18px rgba(255,138,92,.22)}
  #bar2{position:fixed;left:0;right:0;bottom:60px;display:flex;justify-content:center;z-index:30;
    padding:0 12px;pointer-events:none}
  #bar2 .wrap{pointer-events:auto;display:flex;align-items:center;gap:10px;padding:6px 14px;
    border-radius:11px;background:rgba(20,16,13,.84);border:1px solid rgba(255,255,255,.09);
    backdrop-filter:blur(9px);-webkit-backdrop-filter:blur(9px);font-size:11.5px;color:var(--dim)}
  #bar2 input[type=range]{-webkit-appearance:none;appearance:none;width:min(38vw,210px);height:3px;
    background:rgba(255,255,255,.18);border-radius:2px;outline:none}
  #bar2 input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:15px;height:15px;
    border-radius:50%;background:var(--coral);border:2px solid #2a1108;cursor:pointer}
  #bar2 #exv{color:var(--coral);font-weight:700;min-width:34px;text-align:right;font-variant-numeric:tabular-nums}

  /* ── 圖例 ── */
  #legend{position:fixed;left:14px;bottom:112px;padding:10px 13px;font-size:11px;color:var(--dim);
    line-height:1.8;z-index:18;max-width:244px}
  #legend b{color:#fff;font-size:11.5px;display:block;margin-bottom:3px}
  #legend .sw{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:6px;
    vertical-align:-1px}

  #err{position:fixed;left:50%;top:14px;transform:translateX(-50%);background:#7d1f18;color:#fff;
    padding:8px 14px;border-radius:9px;font-size:12px;display:none;z-index:99;max-width:80vw}

  @media (max-width:760px){
    #hud{max-width:60vw;padding:9px 12px}
    #hud span{display:none}
    #hud .tag{margin-top:4px;font-size:9.5px}
    #legend{display:none}
    #finfo{width:min(280px,62vw);right:10px;top:62px;padding:10px 12px}
    .lbl{font-size:10.5px}
    #bar{gap:6px;padding:0 8px;justify-content:flex-start}
    #bar button{min-width:68px;height:38px;font-size:12px;padding:0 11px}
    #bar2{bottom:64px}
  }
  /* ── 外殼顏色 ── */
  #csw{position:fixed;right:14px;bottom:112px;z-index:24;display:flex;align-items:center;gap:8px;
    padding:8px 12px;border-radius:12px;background:rgba(17,23,20,.84);
    border:1px solid rgba(255,255,255,.10);backdrop-filter:blur(9px);
    -webkit-backdrop-filter:blur(9px);font-size:11px;color:#c3ccc6;letter-spacing:.3px}
  #csw s{text-decoration:none;opacity:.75}
  #csw b{width:20px;height:20px;border-radius:50%;display:block;cursor:pointer;
    border:2px solid rgba(255,255,255,.20);transition:.15s;box-sizing:border-box}
  #csw b:hover{transform:scale(1.14)}
  #csw b.on{border-color:#fff;box-shadow:0 0 0 2px rgba(255,255,255,.30)}
  @media (max-width:760px){
    #csw{bottom:120px;right:10px;gap:6px;padding:6px 9px;font-size:10px}
    #csw b{width:17px;height:17px}
  }
  /* ── 顯示健康狀態（?diag=1） ── */
  #diag{position:fixed;left:8px;top:8px;z-index:98;display:none;pointer-events:none;
    font:10px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;color:#9fd9c0;
    background:rgba(0,0,0,.55);padding:4px 7px;border-radius:6px;white-space:pre;max-width:60vw}
</style>
</head>
<body>
<div id="app"></div>

<div id="hud" class="panel">
  <b>貓語翻譯基地台 <i>MEOWBASE · 嘉蘭智慧科技</i></b>
  <span>立架 ＋ RP2350 AMOLED 主機・1 格 = 1 mm<br>拖曳旋轉 · 滾輪縮放 · 點零件看規格</span>
  <div class="tag" id="hudtag"><b>立架 60 × 80 × 60</b> ｜ 主機 44 × 29.1 × 9.6 mm</div>
</div>

<div id="finfo" class="panel"></div>

<div id="lblLayer">
  <svg id="lead" xmlns="http://www.w3.org/2000/svg"></svg>
</div>

<div id="legend" class="panel">
  <b>顏色語彙</b>
  <div><span class="sw" style="background:#e9e0d4"></span>立架 PLA 霧白／暖灰</div>
  <div><span class="sw" style="background:#2a2e33"></span>主機殼 PC+ABS 霧黑</div>
  <div><span class="sw" style="background:#1e6b3c"></span>PCB 綠板＋金焊盤</div>
  <div><span class="sw" style="background:#cfd6dc"></span>鋁塑電池／鎳層金屬</div>
  <div><span class="sw" style="background:#ff8a5c"></span>AMOLED UI／狀態導光條</div>
</div>

<div id="bar2"><div class="wrap">
  <span>爆炸程度</span><input id="exr" type="range" min="0" max="100" value="0" step="1"><span id="exv">0%</span>
</div></div>

<div id="bar">
  <button data-mode="asm" class="on">🏠 組裝</button>
  <button data-mode="exploded">🧩 爆炸</button>
  <button data-mode="dims">📐 尺寸</button>
  <button id="breset">↺ 重置視角</button>
  <button id="bfocus">🎯 取消特寫</button>
</div>
<div id="csw"><s>外殼顏色</s></div>


<div id="diag"></div>
<div id="err"></div>
"""

HTML_TAIL = r"""
</script>
</body>
</html>
"""

APP_JS = r"""
<script>
(function(){
"use strict";
var errEl=document.getElementById('err');
window.__errors=[];
window.onerror=function(m,s,l,c,e){window.__errors.push(String(m));errEl.style.display='block';
  errEl.textContent='JS 錯誤：'+m;};

var QS=location.search||'';
var SHOT=/[?&]shot=1/.test(QS);
var VIEW=((QS.match(/[?&]view=([a-z]+)/)||[])[1])||'asm';
/* 出圖驗證用：?polar=<弧度>&az=<弧度> 指定視角（polar 同 phi） */
var QPOLAR=parseFloat(((QS.match(/[?&](?:polar|phi)=([0-9.]+)/)||[])[1]));
var QAZ=parseFloat(((QS.match(/[?&](?:az|theta)=(-?[0-9.]+)/)||[])[1]));

/* ═══════════════ 場景 ═══════════════ */
var app=document.getElementById('app');
var renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,2));
renderer.setSize(window.innerWidth,window.innerHeight);
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=0.88;
renderer.outputEncoding=THREE.sRGBEncoding;
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
app.appendChild(renderer.domElement);
window.renderer=renderer;

var scene=new THREE.Scene();
scene.background=new THREE.Color(0x080b0d);
window.scene=scene;
scene.fog=new THREE.Fog(0x080b0d,240,760);

var camera=new THREE.PerspectiveCamera(38,window.innerWidth/window.innerHeight,1,5000);
var controls=new THREE.OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;controls.dampingFactor=0.075;
controls.minDistance=40;controls.maxDistance=1200;
controls.maxPolarAngle=Math.PI*0.995;controls.minPolarAngle=0.005;  /* 完整 360°：可轉到底部看元件底盤 */
controls.enablePan=false;
window.camera=camera;window.controls=controls;

/* ── 環境反射（中性灰，不能帶色，否則零件被染色） ── */
try{
  var ec=document.createElement('canvas');ec.width=32;ec.height=128;
  var ex=ec.getContext('2d');
  var eg=ex.createLinearGradient(0,0,0,128);
  eg.addColorStop(0,'#b9c2c4');eg.addColorStop(.34,'#7d868a');
  eg.addColorStop(.72,'#3a4046');eg.addColorStop(1,'#14171a');
  ex.fillStyle=eg;ex.fillRect(0,0,32,128);
  var etex=new THREE.CanvasTexture(ec);
  etex.mapping=THREE.EquirectangularReflectionMapping;
  var pmrem=new THREE.PMREMGenerator(renderer);
  scene.environment=pmrem.fromEquirectangular(etex).texture;
}catch(e){console.warn('env',e);}

/* ── 光源（實測值，別調高：會把零件洗成半透明） ── */
var hemi=new THREE.HemisphereLight(0xe2e7e6,0x4a5a55,0.50);scene.add(hemi);  /* 地面色提亮：轉到底部時朝下的面才看得到細節（正面實測亮度不變） */
var key=new THREE.DirectionalLight(0xfff4e6,1.45);
key.position.set(150,240,170);key.castShadow=true;
key.shadow.mapSize.set(2048,2048);
key.shadow.camera.left=-180;key.shadow.camera.right=180;
key.shadow.camera.top=220;key.shadow.camera.bottom=-90;
key.shadow.camera.near=1;key.shadow.camera.far=900;
key.shadow.bias=-0.0006;key.shadow.normalBias=0.6;
scene.add(key);
var fill=new THREE.DirectionalLight(0xd6e4ff,0.30);fill.position.set(-190,90,120);scene.add(fill);
var rim=new THREE.DirectionalLight(0x7bd3ff,0.42);rim.position.set(-110,80,-180);scene.add(rim);
var back=new THREE.DirectionalLight(0xffffff,0.55);back.position.set(50,50,-200);scene.add(back);

/* ── 地板：極深色（0x010405）＋ fog，避免整片被染亮 ── */
var FLOOR_Y=-1.5;
var floor=new THREE.Mesh(new THREE.CircleGeometry(460,64),
  new THREE.MeshStandardMaterial({color:0x010405,roughness:.99,metalness:0,envMapIntensity:0.03}));
floor.rotation.x=-Math.PI/2;floor.position.y=FLOOR_Y;floor.receiveShadow=true;scene.add(floor);
var grid=new THREE.GridHelper(760,76,0x2a2320,0x141a1c);
grid.position.y=FLOOR_Y+0.02;grid.material.transparent=true;grid.material.opacity=.28;scene.add(grid);

/* ═══════════════ 材質 ═══════════════ */
function mat(o){var m=new THREE.MeshStandardMaterial(o);m.side=THREE.DoubleSide;
  m.envMapIntensity=(o.metalness&&o.metalness>0.6)?1.22:0.20;return m;}
var M={
  stand:   mat({color:0xe9e0d4,roughness:.62,metalness:.02}),   /* 立架 PLA 霧白 */
  stand2:  mat({color:0xdcd1c2,roughness:.68,metalness:.02}),
  standIn: mat({color:0xc9bdac,roughness:.74,metalness:.02}),
  hostShell:mat({color:0x2a2e33,roughness:.52,metalness:.06}),  /* 主機殼 PC+ABS */
  hostShell2:mat({color:0x1d2126,roughness:.58,metalness:.06}),
  glass:   mat({color:0x07090d,roughness:.10,metalness:.42}),
  pcb:     mat({color:0x1e6b3c,roughness:.56,metalness:.05}),
  pcbEdge: mat({color:0x17512d,roughness:.60,metalness:.05}),
  gold:    mat({color:0xd8b45a,roughness:.28,metalness:.95}),
  gold2:   mat({color:0xe8c877,roughness:.22,metalness:1.20}),
  steel:   mat({color:0xcfd4d8,roughness:.24,metalness:1.10}),
  nickel:  mat({color:0xd7dce0,roughness:.20,metalness:1.30}),
  aluDark: mat({color:0x8b9297,roughness:.42,metalness:.85}),
  pouch:   mat({color:0xcfd6dc,roughness:.30,metalness:.70}),
  pouch2:  mat({color:0xb9c2c9,roughness:.38,metalness:.66}),
  ink:     mat({color:0x14171a,roughness:.48,metalness:.08}),
  inkSoft: mat({color:0x24282c,roughness:.66,metalness:.05}),
  rubber:  mat({color:0x181c1e,roughness:.95,metalness:0}),
  red:     mat({color:0xc22a1c,roughness:.52,metalness:.04}),
  black:   mat({color:0x15181b,roughness:.62,metalness:.05}),
  white:   mat({color:0xe8e6e1,roughness:.60,metalness:.04}),
  fpc:     mat({color:0xd08b3a,roughness:.48,metalness:.10}),
  lcdBody: mat({color:0x0d1013,roughness:.36,metalness:.14}),
  emitC:   mat({color:0xffa87a,roughness:.30,metalness:.10,emissive:0xff6a2a,emissiveIntensity:2.2}),
  emitW:   mat({color:0xffd9a8,roughness:.40,metalness:.05,emissive:0x8a4a10,emissiveIntensity:.55})
};

/* ═══════════════ 幾何工具 ═══════════════ */
function rrShape(w,h,r){
  var s=new THREE.Shape(),x=-w/2,y=-h/2;
  s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);
  s.lineTo(x+w,y+h-r);s.quadraticCurveTo(x+w,y+h,x+w-r,y+h);
  s.lineTo(x+r,y+h);s.quadraticCurveTo(x,y+h,x,y+h-r);
  s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);
  return s;
}
function rrPath(w,h,r){
  var s=new THREE.Path(),x=-w/2,y=-h/2;
  s.moveTo(x+r,y);s.lineTo(x+w-r,y);s.quadraticCurveTo(x+w,y,x+w,y+r);
  s.lineTo(x+w,y+h-r);s.quadraticCurveTo(x+w,y+h,x+w-r,y+h);
  s.lineTo(x+r,y+h);s.quadraticCurveTo(x,y+h,x,y+h-r);
  s.lineTo(x,y+r);s.quadraticCurveTo(x,y,x+r,y);
  return s;
}
function mesh(g,m){var o=new THREE.Mesh(g,m);o.castShadow=true;o.receiveShadow=true;return o;}
function box(w,h,d,m){return mesh(new THREE.BoxGeometry(w,h,d),m);}
function cylY(r1,r2,h,m,seg){return mesh(new THREE.CylinderGeometry(r1,r2,h,seg||28),m);}
function cylZ(r1,r2,h,m,seg){
  var o=cylY(r1,r2,h,m,seg);o.rotation.x=Math.PI/2;return o;
}
function disc(r,h,m,seg){return mesh(new THREE.CylinderGeometry(r,r,h,seg||32),m);}
/* 板（XY 平面，厚度沿 Z 置中） */
function plate(w,h,t,r,seg){
  var g=new THREE.ExtrudeGeometry(rrShape(w,h,r||0),{depth:t,bevelEnabled:false,curveSegments:seg||18});
  g.translate(0,0,-t/2);return g;
}
/* 開窗板（XY 平面，厚度沿 Z 置中，窗在中間） */
function winPlate(w,h,t,r,ww,wh,wr){
  var s=rrShape(w,h,r||0);s.holes.push(rrPath(ww,wh,wr||0));
  var g=new THREE.ExtrudeGeometry(s,{depth:t,bevelEnabled:false,curveSegments:22});
  g.translate(0,0,-t/2);return g;
}
/* 側面輪廓 (z,y) 沿 X 擠出寬 w、置中於 xc */
function wedgeZY(pts,w,xc){
  var s=new THREE.Shape();
  for(var i=0;i<pts.length;i++){
    var z=pts[i][0],y=pts[i][1];
    if(i)s.lineTo(z,y);else s.moveTo(z,y);
  }
  s.closePath();
  var g=new THREE.ExtrudeGeometry(s,{depth:w,bevelEnabled:false,curveSegments:10});
  g.translate(0,0,-w/2);
  g.rotateY(-Math.PI/2);   /* shape.x → world z；擠出 → world -x */
  g.translate(xc,0,0);
  return g;
}

/* ═══════════════ 尺寸常數（全部來自既有頁面／GLB 實測） ═══════════════ */
var SW=60, SD=60, SH=80;            /* 立架 60 × 80 × 60 */
var FOOT_H=1.5, BASE_H=12;          /* 腳墊 1.5、底座 12 */
var Y_BASE=FOOT_H+BASE_H;           /* 13.5 塔身底面 */
var WALL=1.6;                        /* 立架壁厚 1.6 */
var PANEL_T=2.4;
var TILT=20*Math.PI/180;             /* 前面板後傾 20° */
var ZFB=10;                          /* 前斜板在塔底的 z */
var ZFT=ZFB-(SH-Y_BASE)*Math.tan(TILT);
var SLOPE=Math.sqrt(Math.pow(ZFB-ZFT,2)+Math.pow(SH-Y_BASE,2));
var PNL_C=new THREE.Vector3(0,(Y_BASE+SH)/2,(ZFB+ZFT)/2);   /* 斜板面中點 */

/* 主機 44 × 29.1 × 9.6 */
var HW=44, HD=29.1, HT=9.6;
var N=new THREE.Vector3(0,Math.sin(TILT),Math.cos(TILT));   /* 面板法線（前上方） */
var UP=new THREE.Vector3(0,Math.cos(TILT),-Math.sin(TILT)); /* 面板上坡方向 */
var HOST_C=PNL_C.clone().addScaledVector(N,HT/2);
var HOST_ROT=-TILT;
var ROT_N=Math.PI/2-TILT;      /* 讓圓柱軸向對齊面板法線 N */
/* 主機內部 z 分層（-4.8 背 → +4.8 前） */
var Z_BACK=-4.0, Z_PCB=-2.6, Z_SPK=-0.7, Z_AMO=1.3, Z_GL=2.6, Z_SHELL=3.9;
var WIN_W=39, WIN_H=24;              /* 前框開窗（玻璃 40 × 25 被唇邊壓住） */
var ACT_W=35.5, ACT_H=21.8;          /* 1.64" 280×456 可視區 */

/* ═══════════════ 畫布貼圖：AMOLED UI（貓語翻譯機） ═══════════════ */
function spaced(c,txt,x,y,sp,fill){
  c.fillStyle=fill;c.textAlign='left';c.textBaseline='middle';
  for(var i=0;i<txt.length;i++){c.fillText(txt[i],x,y);x+=c.measureText(txt[i]).width+sp;}
}
function drawCat(c,cx,cy,r){
  /* 耳朵 */
  [-1,1].forEach(function(s){
    c.save();c.translate(cx+s*r*0.66,cy-r*0.70);c.rotate(s*0.26);
    c.fillStyle='#eaa063';c.beginPath();
    c.moveTo(-r*0.36,0);c.lineTo(0,-r*0.62);c.lineTo(r*0.36,0);c.closePath();c.fill();
    c.fillStyle='#c9754c';c.beginPath();
    c.moveTo(-r*0.19,-r*0.08);c.lineTo(0,-r*0.42);c.lineTo(r*0.19,-r*0.08);c.closePath();c.fill();
    c.restore();
  });
  /* 頭 */
  var hg=c.createRadialGradient(cx-r*0.36,cy-r*0.42,r*0.10,cx,cy,r*1.22);
  hg.addColorStop(0,'#ffdcaa');hg.addColorStop(.55,'#f0ae6e');hg.addColorStop(1,'#cf7c42');
  c.fillStyle=hg;c.beginPath();c.arc(cx,cy,r,0,7);c.fill();
  /* 額頭條紋 */
  c.strokeStyle='rgba(176,105,58,.85)';c.lineWidth=Math.max(2,r*0.062);c.lineCap='round';
  [-1,0,1].forEach(function(k){
    c.beginPath();
    c.moveTo(cx+k*r*0.30,cy-r*0.86);
    c.lineTo(cx+k*r*0.44,cy-r*0.56);
    c.stroke();
  });
  /* 眼睛（大眼＋高光，遠看也認得出是貓） */
  [-1,1].forEach(function(s){
    c.fillStyle='#1a1108';
    c.beginPath();c.ellipse(cx+s*r*0.36,cy-r*0.06,r*0.135,r*0.185,0,0,7);c.fill();
    c.fillStyle='#ffffff';
    c.beginPath();c.arc(cx+s*r*0.40,cy-r*0.14,r*0.058,0,7);c.fill();
    c.fillStyle='rgba(255,255,255,.65)';
    c.beginPath();c.arc(cx+s*r*0.31,cy+r*0.02,r*0.030,0,7);c.fill();
  });
  /* 鼻子 */
  c.fillStyle='#d9744f';
  c.beginPath();c.moveTo(cx,cy+r*0.24);c.lineTo(cx-r*0.115,cy+r*0.10);
  c.lineTo(cx+r*0.115,cy+r*0.10);c.closePath();c.fill();
  /* 嘴巴 */
  c.strokeStyle='#3a2415';c.lineWidth=Math.max(2,r*0.055);
  c.beginPath();c.arc(cx-r*0.10,cy+r*0.30,r*0.15,0.05,Math.PI*0.92);c.stroke();
  c.beginPath();c.arc(cx+r*0.10,cy+r*0.30,r*0.15,Math.PI*0.08,Math.PI*0.95);c.stroke();
  /* 鬍鬚 */
  c.strokeStyle='rgba(255,240,220,.55)';c.lineWidth=Math.max(1.5,r*0.032);
  [-1,1].forEach(function(s){
    for(var k=0;k<3;k++){
      var yy=cy+r*(0.14+k*0.14);
      c.beginPath();c.moveTo(cx+s*r*0.34,yy);
      c.lineTo(cx+s*r*(0.95+k*0.04),yy+r*(k-1)*0.10);
      c.stroke();
    }
  });
}
var WAVE=[6,10,15,9,13,18,11,7,14,20,16,9,12,17,10,6,13,19,15,8,11,16,21,13,7,12,18,10,14,9,6,11];
function uiTex(){
  var UW=ACT_W,UH=ACT_H;
  var W=1240,H=Math.round(W*UH/UW);   /* 1240 × 761 */
  var cv=document.createElement('canvas');cv.width=W;cv.height=H;
  var c=cv.getContext('2d');
  var u=H/100;                         /* 1u ≈ 7.6px */
  /* 背景 */
  var g=c.createLinearGradient(0,0,0,H);
  g.addColorStop(0,'#0b1a2c');g.addColorStop(.5,'#061020');g.addColorStop(1,'#03070e');
  c.fillStyle=g;c.fillRect(0,0,W,H);
  var vg=c.createRadialGradient(W/2,H*0.44,H*0.15,W/2,H*0.44,H*0.95);
  vg.addColorStop(0,'rgba(30,70,110,.22)');vg.addColorStop(1,'rgba(0,0,0,.55)');
  c.fillStyle=vg;c.fillRect(0,0,W,H);

  c.textBaseline='middle';
  /* ── 頂列 ── */
  c.font='bold '+(5.6*u)+'px "Helvetica Neue",Arial,sans-serif';
  spaced(c,'MEOW TRANSLATOR',5.2*u,7.4*u,0.85*u,'#ff9a6c');
  c.textAlign='right';
  c.font='bold '+(5.4*u)+'px "Helvetica Neue",Arial,sans-serif';
  c.fillStyle='#cfe0ea';c.fillText('20:41',W-20.2*u,7.4*u);
  /* 電量 */
  var bx=W-8.9*u,by=4.8*u,bw=8.4*u,bh=4.9*u;
  c.strokeStyle='#ffc98a';c.lineWidth=Math.max(1.5,0.55*u);
  c.beginPath();c.rect(bx,by,bw,bh);c.stroke();
  c.fillStyle='#ffc98a';c.fillRect(bx+bw,by+bh*0.30,1.3*u,bh*0.40);
  c.fillStyle='#ffc266';c.fillRect(bx+0.8*u,by+0.8*u,(bw-1.6*u)*0.8,bh-1.6*u);
  c.font='bold '+(4.4*u)+'px Arial';c.fillStyle='#d8fff1';
  c.fillText('78%',bx-1.2*u,by+bh*0.55);
  /* 分隔線 */
  c.strokeStyle='rgba(120,180,210,.22)';c.lineWidth=Math.max(1,0.3*u);
  c.beginPath();c.moveTo(5*u,13.2*u);c.lineTo(W-5*u,13.2*u);c.stroke();

  /* ── 貓臉 ── */
  drawCat(c,24*u,41*u,13.2*u);

  /* ── 右側翻譯區 ── */
  c.textAlign='left';
  var X0=45*u;
  c.font='500 '+(4.8*u)+'px "PingFang TC","Noto Sans TC",sans-serif';
  c.fillStyle='#7fa3b8';c.fillText('剛剛聽到',X0,21.5*u);

  c.font='bold '+(13.4*u)+'px "PingFang TC","Noto Sans TC",sans-serif';
  c.fillStyle='#ffffff';c.fillText('我餓了',X0,33.5*u);
  c.fillStyle='#ffd9a8';c.fillText('快點餵我',X0,50.0*u);

  /* 信心度標籤 */
  var cy0=58.0*u;
  c.font='bold '+(5.2*u)+'px "PingFang TC",sans-serif';
  var t1='餓  87%';
  var tw=c.measureText(t1).width+5.0*u;
  c.fillStyle='rgba(255,138,92,.20)';
  c.beginPath();
  var rx=X0,ry=cy0-3.0*u,rw=tw,rh=6.2*u,rr=3.1*u;
  c.moveTo(rx+rr,ry);c.lineTo(rx+rw-rr,ry);c.quadraticCurveTo(rx+rw,ry,rx+rw,ry+rr);
  c.lineTo(rx+rw,ry+rh-rr);c.quadraticCurveTo(rx+rw,ry+rh,rx+rw-rr,ry+rh);
  c.lineTo(rx+rr,ry+rh);c.quadraticCurveTo(rx,ry+rh,rx,ry+rh-rr);
  c.lineTo(rx,ry+rr);c.quadraticCurveTo(rx,ry,rx+rr,ry);c.fill();
  c.fillStyle='#ff9a6c';c.fillText(t1,X0+2.5*u,cy0);
  c.font='500 '+(4.6*u)+'px "PingFang TC",sans-serif';
  c.fillStyle='#8fb0c2';
  c.fillText('橘虎斑・3 歲・離 0.8 m',X0+tw+2.6*u,cy0);

  /* ── 音量／情緒波形 ── */
  var n=WAVE.length, x0=8*u, x1=W-8*u, span=(x1-x0)/n, bwid=span*0.56;
  var base=88.5*u;
  for(var i=0;i<n;i++){
    var hgt=WAVE[i]*u*0.62;
    var lg=c.createLinearGradient(0,base,0,base-hgt);
    lg.addColorStop(0,'rgba(255,138,92,.35)');
    lg.addColorStop(.55,'#ff8a5c');
    lg.addColorStop(1,'#ffd08a');
    c.fillStyle=(i<n*0.72)?lg:'rgba(255,138,92,.32)';
    var bx2=x0+i*span+ (span-bwid)/2;
    c.fillRect(bx2,base-hgt,bwid,hgt);
  }
  c.strokeStyle='rgba(255,180,140,.30)';c.lineWidth=Math.max(1,0.3*u);
  c.beginPath();c.moveTo(x0,base+0.4*u);c.lineTo(x1,base+0.4*u);c.stroke();
  c.font='500 '+(4.2*u)+'px "PingFang TC",sans-serif';
  c.fillStyle='#7fa3b8';
  c.textAlign='left';c.fillText('音量 / 情緒波形',x0,95.0*u);
  c.textAlign='right';c.fillStyle='#ff9a6c';
  c.fillText('連續 6 秒・峰值 −12 dB',x1,95.0*u);
  c.textAlign='left';

  var t=new THREE.CanvasTexture(cv);
  /* UI 貼圖是「照片級」內容，從 1240 px 縮到約 170 px 顯示 → 一定要開 mipmap，
     否則小尺寸會出現摩爾紋／對角線條（LED 點陣才用 NearestFilter＋關 mipmap） */
  t.anisotropy=8;t.encoding=THREE.sRGBEncoding;
  t.minFilter=THREE.LinearMipmapLinearFilter;
  t.generateMipmaps=true;
  return t;
}
function uiMat(){
  var tex=uiTex();
  var m=new THREE.MeshStandardMaterial({map:tex,emissive:0xffffff,emissiveMap:tex,
    emissiveIntensity:0.92,color:0x9a9a9a,roughness:.44,metalness:0,side:THREE.DoubleSide});
  m.envMapIntensity=0.05;
  return m;
}

/* ═══════════════ 畫布貼圖：PCB 絲印 / 電池標籤 / 面板字樣 ═══════════════ */
function pcbTex(w,d){
  var W=1024,H=Math.round(1024*d/w);
  var cv=document.createElement('canvas');cv.width=W;cv.height=H;
  var c=cv.getContext('2d');
  c.fillStyle='#1e6b3c';c.fillRect(0,0,W,H);
  for(var i=0;i<22;i++){
    c.fillStyle='rgba(255,255,255,.035)';
    c.fillRect((i*137)%W,(i*211)%H,20+((i*53)%90),8+((i*29)%40));
  }
  c.strokeStyle='rgba(210,235,200,.20)';
  for(var k=0;k<60;k++){
    c.lineWidth=1+((k*7)%2);
    c.beginPath();
    var x=(k*173)%W,y=(k*97)%H;
    c.moveTo(x,y);
    for(var s=0;s<4;s++){x+=(((k+s)*61)%100-50)*W*0.004;y+=(((k+s)*37)%100-50)*H*0.006;c.lineTo(x,y);}
    c.stroke();
  }
  c.fillStyle='#d8b45a';
  for(var p=0;p<42;p++){
    var px=(p*191)%W,py=(p*127)%H,r=3+((p*13)%7);
    c.beginPath();c.arc(px,py,r,0,7);c.fill();
  }
  c.fillStyle='rgba(245,250,240,.92)';
  c.font='bold 40px "Helvetica Neue",Arial,sans-serif';
  c.fillText('MEOWBASE  RP2350  v1.0',W*0.055,H*0.19);
  c.font='25px "Helvetica Neue",Arial,sans-serif';
  c.fillText('RP2350A  \u00b7  QSPI  \u00b7  QMI8658  \u00b7  PCF85063',W*0.055,H*0.29);
  c.font='21px "Helvetica Neue",Arial,sans-serif';
  c.fillText('2026-10  REV.A  CAT-TRANSLATOR BASE',W*0.055,H*0.87);
  c.strokeStyle='rgba(245,250,240,.5)';c.lineWidth=4;
  c.strokeRect(W*0.02,H*0.03,W*0.96,H*0.94);
  var t=new THREE.CanvasTexture(cv);t.anisotropy=8;t.encoding=THREE.sRGBEncoding;
  return t;
}
function battTex(){
  var cv=document.createElement('canvas');cv.width=512;cv.height=768;
  var c=cv.getContext('2d');
  c.fillStyle='#dfe5e9';c.fillRect(0,0,512,768);
  var g=c.createLinearGradient(0,0,512,0);
  g.addColorStop(0,'rgba(0,0,0,.12)');g.addColorStop(.35,'rgba(255,255,255,.24)');
  g.addColorStop(.7,'rgba(0,0,0,.07)');g.addColorStop(1,'rgba(0,0,0,.14)');
  c.fillStyle=g;c.fillRect(0,0,512,768);
  c.fillStyle='#26303a';
  c.font='bold 48px "Helvetica Neue",Arial,sans-serif';
  c.fillText('Li-Po  2000mAh',30,150);
  c.font='31px "Helvetica Neue",Arial,sans-serif';
  c.fillText('3.7V  \u00b7  7.4Wh',30,208);
  c.fillText('MEOWBASE BASE  \u00b7  PCM',30,254);
  c.strokeStyle='#c22a1c';c.lineWidth=5;
  c.strokeRect(22,300,140,64);
  c.fillStyle='#c22a1c';c.font='bold 34px Arial';c.fillText('+',46,348);
  c.strokeStyle='#26303a';c.strokeRect(300,300,140,64);
  c.fillStyle='#26303a';c.fillText('\u2013',324,348);
  c.font='22px "Helvetica Neue",Arial,sans-serif';c.fillStyle='#5a6672';
  c.fillText('DO NOT PUNCTURE / 2026-10',30,470);
  c.fillText('38 \u00d7 60 \u00d7 8.5 mm',30,516);
  var t=new THREE.CanvasTexture(cv);t.anisotropy=4;t.encoding=THREE.sRGBEncoding;
  return t;
}
function panelText(){       /* 面板上的品牌字樣（透明底） */
  var W=1024,H=200;
  var cv=document.createElement('canvas');cv.width=W;cv.height=H;
  var c=cv.getContext('2d');
  c.clearRect(0,0,W,H);
  c.textBaseline='middle';c.textAlign='center';
  c.font='bold 84px "Helvetica Neue",Arial,sans-serif';
  spaced2(c,'MEOWBASE',W/2,H*0.40,10,'rgba(52,44,38,.92)');
  c.font='500 40px "PingFang TC","Noto Sans TC",sans-serif';
  c.fillStyle='rgba(96,84,74,.85)';
  c.fillText('貓語翻譯機 基地台',W/2,H*0.78);
  var t=new THREE.CanvasTexture(cv);t.anisotropy=8;t.encoding=THREE.sRGBEncoding;
  return t;
}
function spaced2(c,txt,cx,cy,sp,fill){
  c.fillStyle=fill;
  var tot=0,i;
  for(i=0;i<txt.length;i++)tot+=c.measureText(txt[i]).width+sp;
  tot-=sp;
  var x=cx-tot/2;
  for(i=0;i<txt.length;i++){
    c.textAlign='left';
    c.fillText(txt[i],x,cy);
    x+=c.measureText(txt[i]).width+sp;
  }
}
var BTEX=battTex(),PTEX=panelText();

/* ═══════════════ 立架零件 ═══════════════ */
/* ① 防滑墊 ×4（Ø12 × 1.5） */
function bFeet(){
  var g=new THREE.Group();
  [[-22,-22],[22,-22],[-22,22],[22,22]].forEach(function(p){
    var pad=disc(6,FOOT_H,M.rubber,36);pad.position.set(p[0],FOOT_H/2,p[1]);g.add(pad);
    var ring=mesh(new THREE.TorusGeometry(4.1,0.34,8,30),M.inkSoft);
    ring.rotation.x=-Math.PI/2;ring.position.set(p[0],FOOT_H*0.72,p[1]);g.add(ring);
    var rim=disc(6.6,0.4,M.rubber,30);rim.position.set(p[0],FOOT_H*0.9,p[1]);g.add(rim);
  });
  return g;
}
/* ② 立架底座 60 × 12 × 60（R8，含電源孔） */
function bBase(){
  var g=new THREE.Group();
  var gg=new THREE.ExtrudeGeometry(rrShape(57.6,57.6,7),
    {depth:BASE_H,bevelEnabled:true,bevelSize:1.2,bevelThickness:1.2,
     bevelSegments:2,curveSegments:26});
  gg.rotateX(-Math.PI/2);
  var body=mesh(gg,M.stand);
  body.position.y=FOOT_H;
  g.add(body);
  /* 與塔身接合處的暗色墊線（避免共面又讀得出分模） */
  var gas=new THREE.Mesh(plate(59.4,59.4,0.5,7.6,26),
    new THREE.MeshStandardMaterial({color:0x3a332c,roughness:.9,metalness:0,
      side:THREE.DoubleSide,envMapIntensity:0.12}));
  gas.rotation.x=-Math.PI/2;gas.position.y=Y_BASE-0.22;g.add(gas);
  /* 背面電源孔（USB-C 進線）＋ 應力消除套 */
  var port=box(9.6,3.8,1.2,M.ink);port.position.set(0,7.0,-29.6);g.add(port);
  var ring=mesh(new THREE.TorusGeometry(3.0,0.5,8,26),M.rubber);
  ring.position.set(0,7.0,-29.7);g.add(ring);
  var lip=box(11.0,5.0,0.6,M.standIn);lip.position.set(0,7.0,-29.85);g.add(lip);
  /* 底部凹槽（4 個腳墊窩） */
  [[-22,-22],[22,-22],[-22,22],[22,22]].forEach(function(p){
    var pock=disc(6.3,0.9,M.standIn,28);pock.position.set(p[0],FOOT_H+0.35,p[1]);g.add(pock);
  });
  return g;
}
/* ③ 狀態指示燈（導光條 26 × 2.6 ＋ WS2812B） */
function bLed(){
  var g=new THREE.Group();
  var bar=box(26,2.6,1.4,M.emitC);bar.position.set(0,8.2,29.4);g.add(bar);
  var bez=box(26.8,3.4,0.8,M.inkSoft);bez.position.set(0,8.2,28.9);g.add(bez);
  var chip=box(5,5,1.6,M.ink);chip.position.set(0,8.2,27.0);g.add(chip);
  var dpad=box(4.2,4.2,0.2,M.gold2);dpad.position.set(0,8.2,26.1);g.add(dpad);
  var hold=box(9,9,2.2,M.inkSoft);hold.position.set(0,8.2,25.0);g.add(hold);
  [[-1.5],[1.5]].forEach(function(o){
    var w=box(0.6,0.6,6.4,o[0]<0?M.red:M.black);
    w.position.set(o[0],8.2,21.6);g.add(w);
  });
  return g;
}
/* ④ ESP32-C3 SuperMini 22 × 18 × 3.2（無線橋） */
function bC3(){
  var g=new THREE.Group();
  var tx=pcbTex(22.5,18);
  var side=mat({color:0x17512d,roughness:.62,metalness:.05});
  var top=mat({color:0xffffff,roughness:.52,metalness:.08,map:tx});
  top.envMapIntensity=0.18;
  var board=new THREE.Mesh(new THREE.BoxGeometry(22.5,1.0,18),[side,side,top,side,side,side]);
  board.castShadow=true;board.receiveShadow=true;g.add(board);
  /* 屏蔽罩 */
  var sh=box(12,1.3,10,M.aluDark);sh.position.set(-1,1.15,1);g.add(sh);
  var sh2=box(11.2,0.3,9.2,M.steel);sh2.position.set(-1,1.85,1);g.add(sh2);
  /* 天線（陶瓷天線 ＋ 蛇形走線） */
  var ant=box(6,0.5,3.2,M.white);ant.position.set(-6.5,0.75,-7);g.add(ant);
  for(var i=0;i<5;i++){
    var m=box(1.4,0.12,3.0,M.gold2);m.position.set(2.6+i*1.9,0.6,-6.6);g.add(m);
  }
  /* USB-C（朝 -Z 出線） */
  var usb=box(8.94,3.26,5.0,M.steel);usb.position.set(0,0.6,-9.6);g.add(usb);
  var um=box(6.8,1.2,1.2,M.ink);um.position.set(0,0.6,-11.6);g.add(um);
  /* 排針（2×4 兩側） */
  [-1,1].forEach(function(s){
    for(var k=0;k<4;k++){
      var p=box(1.0,0.9,1.0,M.gold2);
      p.position.set(s*10.4,0.0,-4.5+k*3.0);g.add(p);
    }
  });
  /* RGB LED */
  var led=box(2.0,0.7,2.0,M.emitC);led.position.set(7.5,0.75,5.0);g.add(led);
  /* 電源 IC */
  var ic=box(3.2,0.6,2.4,M.ink);ic.position.set(6.0,0.7,-3.0);g.add(ic);
  return g;
}
/* ⑤ 鋰電池 2000 mAh（直立：38 寬 × 60 高 × 8.5 厚） */
function bBatt(){
  var g=new THREE.Group();
  var W=38,Hh=60,T=8.5;              /* X × Y × Z */
  var lab=mat({color:0xffffff,roughness:.62,metalness:.10,map:BTEX});
  lab.envMapIntensity=0.22;
  var ms=mat({color:0xd8dee3,roughness:.30,metalness:.62});
  /* 大片面（±Z）貼標籤，四邊是鋁塑封邊 */
  var body=new THREE.Mesh(new THREE.BoxGeometry(W,Hh,T),[ms,ms,ms,ms,lab,lab]);
  body.castShadow=true;body.receiveShadow=true;g.add(body);
  /* 邊緣封條（比本體厚 0.3，讀得出鋁塑膜壓邊） */
  var seal=box(W-0.6,0.9,T+0.3,M.pouch2);seal.position.set(0,Hh/2-0.45,0);g.add(seal);
  var seal2=box(W-0.6,0.9,T+0.3,M.pouch2);seal2.position.set(0,-Hh/2+0.45,0);g.add(seal2);
  /* 保護板（上端） */
  var pcm=box(W*0.55,3.2,0.9,M.pcbEdge);pcm.position.set(0,Hh/2+1.2,T/2-1.4);g.add(pcm);
  var ic=box(2.6,2.2,0.55,M.ink);ic.position.set(0,Hh/2+1.2,T/2-1.4);g.add(ic);
  /* 紅黑線（往上繞向主機） */
  [[-3.0,M.red],[2.6,M.black]].forEach(function(o){
    var pts=[new THREE.Vector3(o[0],Hh/2+2.2,T/2-1.4),
             new THREE.Vector3(o[0],Hh/2+4.4,T/2+1.0),
             new THREE.Vector3(o[0]*0.5,Hh/2+5.0,T/2+4.6)];
    var cu=new THREE.CatmullRomCurve3(pts);
    var t2=new THREE.Mesh(new THREE.TubeGeometry(cu,22,0.34,8,false),o[1]);
    t2.castShadow=true;g.add(t2);
  });
  return g;
}
/* ⑥ 立架立柱／背板（20° 前斜板 ＋ 主機安裝框） */
function bTower(){
  var g=new THREE.Group();
  var prof=[[-SD/2,Y_BASE],[ZFB,Y_BASE],[ZFT,SH],[-SD/2,SH]];
  [1,-1].forEach(function(s){
    g.add(mesh(wedgeZY(prof,WALL,s*(SD/2-WALL/2)),M.stand));
  });
  /* 後壁 */
  var rw=box(SW-2*WALL,SH-Y_BASE,WALL,M.stand);
  rw.position.set(0,(Y_BASE+SH)/2,-SD/2+WALL/2);g.add(rw);
  /* 頂蓋 */
  var topD=(ZFT+SD/2);
  var tp=box(SW-0.6,WALL,topD-0.2,M.stand);
  tp.position.set(0,SH-WALL/2,(-SD/2+ZFT)/2);g.add(tp);
  /* 前斜板（含 6P 排針走線槽） */
  var pan=mesh((function(){
    var s=rrShape(SW-0.3,SLOPE-0.3,3);s.holes.push(rrPath(31,7.5,2.6));
    var gg=new THREE.ExtrudeGeometry(s,{depth:PANEL_T,bevelEnabled:false,curveSegments:22});
    gg.translate(0,0,-PANEL_T);return gg;
  })(),M.stand);
  pan.rotation.x=HOST_ROT;pan.position.copy(PNL_C);g.add(pan);
  /* 主機安裝框（凸 1.2 mm 的唇邊，主機坐進去） */
  var lip=mesh((function(){
    var s=rrShape(HW+2,HD+2,4.0);s.holes.push(rrPath(HW+0.6,HD+0.6,3.6));
    var gg=new THREE.ExtrudeGeometry(s,{depth:1.2,bevelEnabled:false,curveSegments:22});
    gg.translate(0,0,-1.2);return gg;
  })(),M.stand2);
  lip.rotation.x=HOST_ROT;
  lip.position.copy(PNL_C).addScaledVector(N,1.2);
  g.add(lip);
  /* 面板字樣 */
  var txt=new THREE.Mesh(new THREE.PlaneGeometry(HW,11),
    new THREE.MeshBasicMaterial({map:PTEX,transparent:true,alphaTest:0.02,
      side:THREE.DoubleSide,depthWrite:false}));
  txt.rotation.x=HOST_ROT;
  txt.position.copy(PNL_C).addScaledVector(N,0.10).addScaledVector(UP,HD/2+9.5);
  txt.renderOrder=2;g.add(txt);
  /* 四顆螺絲柱（面板內側） */
  [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(function(s){
    var b=cylY(2.4,2.4,7,M.standIn,16);
    b.position.copy(PNL_C).addScaledVector(N,-PANEL_T-3.4)
      .addScaledVector(new THREE.Vector3(1,0,0),s[0]*(HW/2-3.2))
      .addScaledVector(UP,s[1]*(HD/2-3.2));
    b.rotation.x=ROT_N;g.add(b);
    var hole=cylY(1.1,1.1,7.4,M.ink,14);
    hole.position.copy(b.position);hole.rotation.x=ROT_N;g.add(hole);
  });
  /* 面板內側補強肋 */
  [-1,1].forEach(function(s){
    var rb=box(2.4,SLOPE*0.72,WALL,M.standIn);
    rb.rotation.x=HOST_ROT;
    rb.position.copy(PNL_C).addScaledVector(N,-PANEL_T-WALL/2)
      .addScaledVector(new THREE.Vector3(1,0,0),s*(SW/2-WALL-1.2))
      .addScaledVector(UP,-2);
    g.add(rb);
  });
  return g;
}
/* ⑦ 排針 1×6（2.54 mm）— 主機插接用，鎖在面板內側 */
function bHeader(){
  var g=new THREE.Group();
  /* 整組進面板座標系：+y → 斜面上坡、+z → 面板法線 */
  g.rotation.x=HOST_ROT;
  g.position.copy(PNL_C).addScaledVector(N,-PANEL_T-1.4)
    .addScaledVector(UP,-(HD/2-3.0));
  var body=box(15.24,2.5,2.54,M.ink);body.position.z=0;g.add(body);
  for(var i=0;i<6;i++){
    var x=-6.35+i*2.54;
    var pin=cylZ(0.32,0.32,6.0,M.gold2,10);
    pin.position.set(x,0,2.6);g.add(pin);
    var base=box(1.9,1.9,0.5,M.inkSoft);
    base.position.set(x,0,-1.5);g.add(base);
  }
  var groove=box(14.0,1.2,0.6,M.gold2);groove.position.set(0,0,-1.3);g.add(groove);
  return g;
}

/* ═══════════════ 主機零件（區域座標，原點＝模組中心，+Z 朝前） ═══════════════ */
/* ⑧ 主機背蓋 44 × 29.1 × 1.6 */
function bBackCover(){
  var g=new THREE.Group();
  var p=mesh(plate(HW,HD,1.6,3.4),M.hostShell);p.position.z=Z_BACK;g.add(p);
  /* 內側止口 */
  var lip=mesh(winPlate(HW-1.2,HD-1.2,1.0,3.0,HW-3.2,HD-3.2,2.6),M.hostShell2);
  lip.position.z=Z_BACK+1.0;g.add(lip);
  /* 喇叭柵孔 7 孔 */
  for(var i=0;i<7;i++){
    var h=cylZ(0.7,0.7,0.5,M.ink,12);
    h.position.set(-12.5, -6.0+ (i%4)*3.2, Z_BACK-0.15-(i*0.001));
    h.position.x=-12.5+Math.floor(i/4)*3.0;
    g.add(h);
  }
  /* 線材出口 */
  var slot=box(11,4.6,0.9,M.ink);slot.position.set(9,-8.2,Z_BACK-0.1);g.add(slot);
  /* 測試點 */
  for(var k=0;k<4;k++){
    var tp=disc(0.9,0.25,M.gold2,14);
    tp.rotation.x=Math.PI/2;tp.position.set(6+k*3.0,10.5,Z_BACK-0.1);g.add(tp);
  }
  /* 四顆螺絲孔環 */
  [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(function(s){
    var r=mesh(new THREE.TorusGeometry(1.9,0.35,6,18),M.inkSoft);
    r.rotation.x=Math.PI/2;
    r.position.set(s[0]*(HW/2-3.2),s[1]*(HD/2-3.2),Z_BACK-0.12);g.add(r);
  });
  /* 側邊散熱縫 */
  for(var v=0;v<5;v++){
    var s2=box(0.9,4.0,1.2,M.inkSoft);
    s2.position.set(HW/2-0.3,6.5-v*2.6,Z_BACK+0.95);g.add(s2);
  }
  return g;
}
/* ⑨ RP2350 主機板 38 × 24 × 1.2（厚度沿 Z，絲印貼 +Z 面） */
function bPcb(){
  var g=new THREE.Group();
  var W=38,D=24,T=1.2;
  var tx=pcbTex(W,D);
  var side=mat({color:0x17512d,roughness:.62,metalness:.05});
  var top=mat({color:0xffffff,roughness:.52,metalness:.08,map:tx});
  top.envMapIntensity=0.18;
  var board=new THREE.Mesh(new THREE.BoxGeometry(W,D,T),[side,side,side,side,top,side]);
  board.castShadow=true;board.receiveShadow=true;board.position.z=Z_PCB;g.add(board);
  var fz=Z_PCB+T/2, bz=Z_PCB-T/2;
  /* RP2350A（QFN-80 10 × 10） */
  var mcu=box(10,10,0.9,M.ink);mcu.position.set(-6,2.5,fz+0.45);g.add(mcu);
  var ring=mesh(winPlate(10.8,10.8,0.2,0.5,9.2,9.2,0.5),M.gold2);
  ring.position.set(-6,2.5,fz+0.03);g.add(ring);
  var dot=cylZ(0.55,0.55,0.14,M.emitW,12);dot.position.set(-10.2,6.0,fz+0.95);g.add(dot);
  /* QSPI Flash 5 × 6 */
  var fl=box(5,6,0.8,M.ink);fl.position.set(3.5,7,fz+0.42);g.add(fl);
  var fld=cylZ(0.4,0.4,0.1,M.emitW,10);fld.position.set(2.0,8.6,fz+0.86);g.add(fld);
  /* QMI8658 IMU 2.5 × 3.0 */
  var imu=box(2.5,3.0,0.62,M.ink);imu.position.set(8.6,1.2,fz+0.34);g.add(imu);
  /* PCF85063 RTC 3 × 3 ＋ 32.768k 晶體 */
  var rtc=box(3,3,0.6,M.inkSoft);rtc.position.set(-14,-4.6,fz+0.32);g.add(rtc);
  var xtal=box(2.0,1.6,0.5,M.steel);xtal.position.set(-14,-8.0,fz+0.28);g.add(xtal);
  /* AMOLED FPC 座 20 pin 12 × 4 */
  var fc=box(12,4,1.6,M.ink);fc.position.set(0,-10.2,fz+0.8);g.add(fc);
  var fcg=box(11.0,1.0,0.4,M.gold2);fcg.position.set(0,-11.6,fz+1.62);g.add(fcg);
  /* 貼片被動元件 */
  for(var k=0;k<16;k++){
    var cx2=-16.5+((k*7)%33), cxy=-9+((k*11)%19);
    if(Math.abs(cx2+6)<6.5&&Math.abs(cxy-2.5)<6.5)continue;
    var c3=box(1.1,0.55,0.42,(k%3===0)?M.aluDark:M.inkSoft);
    c3.position.set(cx2,cxy,fz+0.21);g.add(c3);
  }
  /* 背面：microSD 卡座 13.2 × 11 */
  var sd=box(13.2,11,1.0,M.aluDark);sd.position.set(9.0,3.0,bz-0.5);g.add(sd);
  var sds=box(11.6,8.4,0.3,M.ink);sds.position.set(9.0,3.0,bz-1.05);g.add(sds);
  var sdg=box(1.6,4.0,0.4,M.gold2);sdg.position.set(2.0,3.0,bz-1.2);g.add(sdg);
  /* MX1.25 電池座 6 × 4.5 */
  var mx=box(6,4.5,3.6,M.white);mx.position.set(-14.5,6.0,bz-1.8);g.add(mx);
  var mxp=box(4.0,2.6,1.0,M.gold2);mxp.position.set(-14.5,6.0,bz-3.4);g.add(mxp);
  /* 背側金焊盤 */
  for(var i=0;i<9;i++){
    var p2=box(1.6,2.2,0.2,M.gold2);
    p2.position.set(-16+i*3.4,-10.4,bz-0.1);g.add(p2);
  }
  /* 固定孔（金環） */
  [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(function(s){
    var r=mesh(new THREE.TorusGeometry(1.5,0.42,6,16),M.gold2);
    r.position.set(s[0]*(W/2-3.0),s[1]*(D/2-3.0),fz+0.05);g.add(r);
  });
  return g;
}
/* ⑩ 麥克風 INMP441 4.72 × 3.76 × 1.0 */
function bMic(){
  var g=new THREE.Group();
  var chip=box(4.72,3.76,1.0,M.ink);
  chip.position.set(12.0,8.0,Z_PCB+1.2);g.add(chip);
  var lid=box(4.2,3.3,0.18,M.aluDark);lid.position.set(12.0,8.0,Z_PCB+1.78);g.add(lid);
  var port=cylZ(0.42,0.42,0.26,M.gold2,12);
  port.position.set(12.0,8.0,Z_PCB+1.94);g.add(port);
  for(var i=0;i<4;i++){
    var p=box(0.7,0.5,0.25,M.gold2);
    p.position.set(10.6+i*1.3,6.4,Z_PCB+0.75);g.add(p);
  }
  return g;
}
/* ⑪ USB-C 16P 母座 8.94 × 7.35 × 3.26（開口朝 -Y） */
function bUsbC(){
  var g=new THREE.Group();
  /* 8.94 寬 × 7.35 高 × 3.26 厚，插入方向沿 -Y */
  var shell=box(8.94,7.35,3.26,M.steel);
  shell.position.set(0,-10.9,-1.9);g.add(shell);
  var mouth=box(8.1,5.6,1.6,M.ink);
  mouth.position.set(0,-14.0,-1.9);g.add(mouth);
  /* 24 個金接點（舌片上下各 12） */
  for(var i=0;i<12;i++){
    [-1,1].forEach(function(s){
      var p=box(0.55,1.4,0.16,M.gold2);
      p.position.set(-3.7+i*0.67,-12.4,-1.9+s*0.62);g.add(p);
    });
  }
  /* 固定腳（兩側） */
  [-4.3,4.3].forEach(function(x){
    var l=box(0.8,2.2,0.9,M.steel);
    l.position.set(x,-7.6,-1.9);g.add(l);
  });
  return g;
}
/* ⑫ 喇叭 Ø14 × 2.5 */
function bSpeaker(){
  var g=new THREE.Group();
  var can=cylZ(7,7,2.1,M.steel,40);
  can.position.set(-12.5,-6.5,Z_SPK);g.add(can);
  var face=cylZ(6.6,6.6,0.3,M.inkSoft,40);
  face.position.set(-12.5,-6.5,Z_SPK+1.15);g.add(face);
  var ring=mesh(new THREE.TorusGeometry(6.9,0.4,8,40),M.rubber);
  ring.position.set(-12.5,-6.5,Z_SPK-1.1);g.add(ring);
  /* 振膜同心紋 */
  for(var i=1;i<=3;i++){
    var t=mesh(new THREE.TorusGeometry(i*1.5,0.09,6,36),M.ink);
    t.position.set(-12.5,-6.5,Z_SPK+1.3);g.add(t);
  }
  /* 端子 */
  [[-2.0],[2.0]].forEach(function(o){
    var p=box(1.2,0.5,0.6,M.gold2);
    p.position.set(-12.5+o[0],-6.5-6.4,Z_SPK+0.2);g.add(p);
  });
  return g;
}
/* ⑬ AMOLED 螢幕模組（玻璃 40 × 25 ＋ 可視 35.5 × 21.8） */
function bAmoled(){
  var g=new THREE.Group();
  var body=box(40,25,1.4,M.lcdBody);body.position.z=Z_AMO;g.add(body);
  var gl=box(40,25,1.2,M.glass);gl.position.z=Z_GL;g.add(gl);
  /* 螢幕 UI：比可視區大 0.5 mm、往前 0.14 mm，不與玻璃共面 */
  var ui=new THREE.Mesh(new THREE.PlaneGeometry(ACT_W+0.5,ACT_H+0.5),uiMat());
  ui.position.z=Z_GL+0.6+0.14;g.add(ui);
  /* FPC 排線（往下折） */
  var tail=box(11,5.2,0.22,M.fpc);tail.position.set(0,-12.3,Z_AMO-1.0);g.add(tail);
  var conn=box(11.4,1.2,0.42,M.gold2);conn.position.set(0,-14.0,Z_AMO-1.0);g.add(conn);
  /* 驅動 IC */
  var drv=box(13,1.5,0.5,M.ink);drv.position.set(0,-10.4,Z_AMO-0.9);g.add(drv);
  return g;
}
/* ⑭ 主機前殼（44 × 29.1 × 3.0 框 ＋ 1.8 面板） */
function bShell(){
  var g=new THREE.Group();
  /* 側壁框：從背蓋前緣 -3.2 一路到前緣 +4.8（內腔 41 × 26）
     原本只做 1.8 → 4.8，會留下一圈 5 mm 的側面開口，斜看就從縫裡看到綠色 PCB */
  var ring=mesh(winPlate(HW-0.4,HD-0.4,8.0,3.2,HW-3.0,HD-3.0,3.0),M.hostShell);
  ring.position.z=0.8;g.add(ring);
  /* 前面板（3.0 → 4.8，開窗 39 × 24，唇邊壓住 40 × 25 玻璃） */
  var face=mesh(winPlate(HW,HD,1.8,3.4,WIN_W,WIN_H,2.6),M.hostShell);
  face.position.z=Z_SHELL;g.add(face);
  /* 開窗內壁（黑色，深 1.2 mm，讀得出螢幕凹進去） */
  var well=mesh(winPlate(WIN_W+2.2,WIN_H+2.2,1.2,2.4,WIN_W+0.5,WIN_H+0.5,2.2),M.hostShell2);
  well.position.z=Z_SHELL-0.6;g.add(well);
  /* 四顆螺絲柱 */
  [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(function(s){
    var b=cylZ(2.1,2.1,4.6,M.hostShell2,16);
    b.position.set(s[0]*(HW/2-3.2),s[1]*(HD/2-3.2),Z_SHELL-2.6);g.add(b);
  });
  /* 頂緣麥克風收音孔（2 × Ø1.0，孔距 1.4，貫穿前面板） */
  [-0.7,0.7].forEach(function(x){
    var h=cylZ(0.5,0.5,2.0,M.ink,12);
    h.position.set(x,HD/2-1.5,Z_SHELL+0.4);g.add(h);
    var rim=mesh(new THREE.TorusGeometry(0.72,0.16,6,16),M.hostShell2);
    rim.position.set(x,HD/2-1.5,Z_SHELL+0.92);g.add(rim);
  });
  return g;
}

/* ═══════════════ 零件定義（組裝順序＝編號順序，由下往上） ═══════════════ */
var DEFS=[
 {id:'feet', f:bFeet, host:false, n:'防滑墊 ×4',
  d:'Ø12 × 1.5 mm（孔位 44 × 44）', mt:'矽膠 60 Shore A・背膠',
  u:'四角各一顆，讓立架在桌面不滑動也不刮桌面；Ø12 對應 60 × 60 底座的 44 mm 孔距，受力落在四角而不是中央。',
  ex:[0,-12,0]},
 {id:'base', f:bBase, host:false, n:'立架底座',
  d:'60.0 × 12.0 × 60.0 mm（R8・壁厚 1.6）', mt:'PLA 霧白・0.4 mm 噴嘴・3 層牆',
  u:'整片配重底盤，內部走線；後方留 9.6 × 3.8 mm 進線孔配應力消除套，USB-C 供電線從背面進來。',
  ex:[0,-2,0]},
 {id:'led', f:bLed, host:false, n:'狀態指示燈（導光條）',
  d:'導光條 26 × 2.6 mm・WS2812B 5 × 5 × 1.6', mt:'壓克力導光＋RGB LED・PWM 呼吸',
  u:'底座前方 26 mm 導光條：待機慢呼吸橘光、收到叫聲事件閃兩下、斷線轉紅。發光面比底座前緣凸 0.2 mm，不做動畫也不會有共面雜訊。',
  ex:[0,-4,26]},
 {id:'c3', f:bC3, host:false, n:'ESP32-C3 SuperMini（無線橋）',
  d:'22.5 × 18.0 × 3.2 mm', mt:'FR-4 綠板＋金屬屏蔽罩',
  u:'RP2350 這塊板子沒有 WiFi/BT，所以另外掛一顆 C3 專做 BLE Central ＋ WiFi 上傳，用 UART 115200（GP16/GP17）跟主機對接。',
  pos:[0,16.8,-6.5], ex:[-56,-4,10]},
 {id:'batt', f:bBatt, host:false, n:'鋰聚合物電池 2000 mAh',
  d:'38.0 × 60.0 × 8.5 mm', mt:'鋁塑膜・3.7 V 7.4 Wh・附保護板',
  u:'直立在背板內側、貼著 20° 斜背，重心落在底座範圍內不會倒。斷電備援 4–5 天（待機 15–25 mA）。',
  pos:[0,44,-22], ex:[48,2,8]},
 {id:'tower', f:bTower, host:false, n:'立架立柱／背板',
  d:'60.0 × 66.5 × 40.0 mm（前面板後傾 20°）', mt:'PLA 霧白・壁厚 1.6・M3 螺絲柱',
  u:'主體結構：20° 斜面板讓桌面視角正對螢幕，背面 25 mm 深腔放電池與 C3；面板內側四顆 M3 螺絲柱鎖住主機安裝框。',
  ex:[0,62,-8]},
 {id:'hdr', f:bHeader, host:false, n:'排針 1 × 6（2.54 mm）',
  d:'15.24 × 2.54 × 8.5 mm', mt:'黃銅鍍金 pin＋PBT 本體',
  u:'主機插上立架的電源／UART 介面：5V、GND、TX、RX、兩條備用。針穿過面板 31 × 7.5 mm 走線槽插進主機背面。',
  ex:[-38,10,20]},
 {id:'back', f:bBackCover, host:true, n:'主機背蓋',
  d:'44.0 × 29.1 × 1.6 mm', mt:'PC+ABS 霧黑・超音波熔接',
  u:'背面：喇叭柵孔 7 孔、電池線出口、4 個測試點、側邊 5 道散熱縫；四角 M2 螺絲孔對鎖前殼。',
  ex:[0,10,8]},
 {id:'pcb', f:bPcb, host:true, n:'RP2350 主機板',
  d:'38.0 × 24.0 × 1.2 mm（4 層）', mt:'FR-4 綠板＋ENIG 金焊盤',
  u:'RP2350A ＋ QSPI Flash ＋ QMI8658（6 軸）＋ PCF85063（RTC）＋ microSD 卡座 ＋ MX1.25 電池座；AMOLED 走 20 pin FPC。',
  ex:[0,32,16]},
 {id:'mic', f:bMic, host:true, n:'麥克風 INMP441',
  d:'4.72 × 3.76 × 1.0 mm（9-pin LGA）', mt:'MEMS 麥克風・I²S 數位輸出',
  u:'基地台自己的耳朵：I²S 24-bit、60 Hz–15 kHz，用來現場收音再交給 RP2350 做分類，不倚賴項圈麥克風。',
  ex:[28,22,14]},
 {id:'usbc', f:bUsbC, host:true, n:'USB-C 16P 母座',
  d:'8.94 × 7.35 × 3.26 mm', mt:'不鏽鋼殼＋鍍金接點・24 pin',
  u:'主供電（5 V / 2 A）與韌體燒錄；接座藏在背蓋下緣，插著線也能立在桌上。',
  ex:[-40,14,18]},
 {id:'spk', f:bSpeaker, host:true, n:'微型喇叭 Ø14',
  d:'Ø14.0 × 2.5 mm', mt:'鎳鐵氧體＋PET 振膜・8 Ω 1 W',
  u:'播放翻譯語音（「我餓了」）與提示音；從背蓋柵孔出聲，背腔在背蓋與 PCB 之間留 1.5 mm。',
  ex:[-32,42,22]},
 {id:'amoled', f:bAmoled, host:true, n:'1.64 吋 AMOLED 模組',
  d:'玻璃 40.0 × 25.0 mm（可視 35.5 × 21.8）', mt:'280 × 456 AMOLED・QSPI・觸控',
  u:'主畫面：貓臉表情 ＋ 一行翻譯結果 ＋ 音量／情緒波形。模組凹進前框 1.6 mm，斜看也不會漏光。',
  ex:[0,54,30]},
 {id:'shell', f:bShell, host:true, n:'主機前殼（螢幕框）',
  d:'44.0 × 29.1 × 3.0 mm（開窗 39 × 24）', mt:'PC+ABS 霧黑・噴砂咬花',
  u:'開窗 39 × 24 的唇邊壓住 40 × 25 玻璃邊緣 0.5 mm，斜看也不會露出內部；玻璃凹進框內 1.6 mm，頂緣兩孔 Ø1.0 給麥克風進音。',
  ex:[0,72,44]}
];

/* ═══════════════ 建構 ═══════════════ */
var model=new THREE.Group();scene.add(model);
var PARTS=[],LBL=[];
window.PARTS=PARTS;

var axisMat=new THREE.LineDashedMaterial({color:0x2f8fff,dashSize:5,gapSize:4,
  transparent:true,opacity:.9});
var axisGeo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,-40,0),
  new THREE.Vector3(0,170,0)]);
var axisLine=new THREE.Line(axisGeo,axisMat);
axisLine.computeLineDistances();axisLine.visible=false;scene.add(axisLine);

/* 尺寸標註 */
var dimGroup=new THREE.Group();dimGroup.visible=false;scene.add(dimGroup);
function sprLabel(text,size,fg,bg){
  var fs=64,pad=18;
  var c=document.createElement('canvas').getContext('2d');
  var ff='bold '+fs+'px "PingFang TC","Noto Sans TC",sans-serif';
  c.font=ff;
  var w=Math.ceil(c.measureText(text).width)+pad*2,h=fs+pad*2;
  var cv=document.createElement('canvas');cv.width=w;cv.height=h;
  c=cv.getContext('2d');c.font=ff;
  var r=18;c.fillStyle=bg||'#ff8a5c';c.beginPath();
  c.moveTo(r,0);c.lineTo(w-r,0);c.quadraticCurveTo(w,0,w,r);c.lineTo(w,h-r);
  c.quadraticCurveTo(w,h,w-r,h);c.lineTo(r,h);c.quadraticCurveTo(0,h,0,h-r);
  c.lineTo(0,r);c.quadraticCurveTo(0,0,r,0);c.closePath();c.fill();
  c.fillStyle=fg||'#2a1108';c.textBaseline='middle';c.fillText(text,pad,h/2+2);
  var t=new THREE.CanvasTexture(cv);t.minFilter=THREE.LinearFilter;t.encoding=THREE.sRGBEncoding;
  var sp=new THREE.Sprite(new THREE.SpriteMaterial({map:t,depthTest:false,depthWrite:false,
    transparent:true}));
  sp.scale.set(size*w/h,size,1);sp.renderOrder=999;
  return sp;
}
function rod(a,b,r,col){
  var d=new THREE.Vector3().subVectors(b,a),len=d.length();
  if(len<1e-5)return null;
  var m=new THREE.Mesh(new THREE.CylinderGeometry(r,r,len,8),
    new THREE.MeshBasicMaterial({color:col,transparent:true,opacity:.95,depthTest:false}));
  m.position.copy(a).add(d.clone().multiplyScalar(.5));
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),d.clone().normalize());
  m.renderOrder=998;return m;
}
function V(x,y,z){return new THREE.Vector3(x,y,z);}
function addDim(a,b,label,size){
  var col=0xff8a5c;
  var m=rod(a,b,0.30,col);if(m)dimGroup.add(m);
  var dir=new THREE.Vector3().subVectors(b,a).normalize();
  var perp=new THREE.Vector3(0,1,0);
  if(Math.abs(dir.dot(perp))>0.9)perp.set(1,0,0);
  [a,b].forEach(function(p){
    var c1=p.clone().add(new THREE.Vector3().crossVectors(dir,perp).multiplyScalar(1.9));
    var c2=p.clone().add(new THREE.Vector3().crossVectors(dir,perp).multiplyScalar(-1.9));
    var t=rod(c1,c2,0.28,col);if(t)dimGroup.add(t);
  });
  var lb=sprLabel(label,size||3.4);
  lb.position.copy(a).add(b).multiplyScalar(.5);
  dimGroup.add(lb);
}
function extLine(from,to){
  var m=rod(from,to,0.14,0xff8a5c);if(m)dimGroup.add(m);
}
function buildDims(){
  while(dimGroup.children.length){dimGroup.remove(dimGroup.children[0]);}
  var sz=3.2;
  /* 立架三尺寸 */
  var yT=SH+8, zR=-SD/2-10, xR=SW/2+12;
  addDim(V(-SW/2,yT,-SD/2),V(SW/2,yT,-SD/2),'立架寬 60 mm',sz);
  [-SW/2,SW/2].forEach(function(x){extLine(V(x,SH,zR),V(x,yT,-SD/2));});
  addDim(V(xR,yT,-SD/2),V(xR,yT,SD/2),'深 60 mm',sz);
  [-SD/2,SD/2].forEach(function(z){extLine(V(xR,SH,z),V(xR,yT,z));});
  addDim(V(xR,0,SD/2+8),V(xR,SH,SD/2+8),'總高 80 mm',sz);
  [0,SH].forEach(function(y){extLine(V(SW/2,y,SD/2),V(xR,y,SD/2+8));});
  /* 主機三尺寸（沿面板座標） */
  var X=new THREE.Vector3(1,0,0);
  var hs=(function(){return 2.7;})();
  var front=HOST_C.clone().addScaledVector(N,HT/2);
  var topA=front.clone().addScaledVector(UP,HD/2).addScaledVector(N,4);
  addDim(topA.clone().addScaledVector(X,-HW/2),topA.clone().addScaledVector(X,HW/2),
    '主機寬 44 mm',hs);
  [1,-1].forEach(function(s){
    extLine(front.clone().addScaledVector(X,s*HW/2).addScaledVector(UP,HD/2),
            topA.clone().addScaledVector(X,s*HW/2));
  });
  var rEdge=front.clone().addScaledVector(X,HW/2+6);
  addDim(rEdge.clone().addScaledVector(UP,-HD/2),rEdge.clone().addScaledVector(UP,HD/2),
    '高 29.1 mm',hs);
  [1,-1].forEach(function(s){
    extLine(front.clone().addScaledVector(X,HW/2).addScaledVector(UP,s*HD/2),
            rEdge.clone().addScaledVector(UP,s*HD/2));
  });
  var tA=front.clone().addScaledVector(X,HW/2+6).addScaledVector(UP,HD/2+5);
  addDim(tA.clone().addScaledVector(N,-HT),tA.clone().addScaledVector(N,0),'厚 9.6 mm',hs);
  extLine(front.clone().addScaledVector(X,HW/2).addScaledVector(UP,HD/2),
          tA.clone().addScaledVector(N,0));
  extLine(HOST_C.clone().addScaledVector(X,HW/2).addScaledVector(UP,HD/2).addScaledVector(N,-HT/2),
          tA.clone().addScaledVector(N,-HT));
}

DEFS.forEach(function(d){
  var g=(d.host?d.f():d.f());
  if(d.host){g.rotation.x=HOST_ROT;g.position.copy(HOST_C);}
  else if(d.pos){g.position.set(d.pos[0],d.pos[1],d.pos[2]);}
  g.userData.info={t:d.n,rows:[['尺寸',d.d],['材質',d.mt],['用途',d.u]]};
  model.add(g);
  var rec={id:d.id,def:d,g:g,num:0,ex:new THREE.Vector3().fromArray(d.ex),
    home:g.position.clone()};
  g.userData.rec=rec;PARTS.push(rec);
});

buildDims();
buildLabels();

/* ═══════════════ 標籤（左右分欄＋引線） ═══════════════ */
function buildLabels(){
  var lead=document.getElementById('lead');
  lead.innerHTML='';
  PARTS.slice().sort(function(a,b){return a.def.ex?0:0;});
  PARTS.forEach(function(p,i){
    p.num=i+1;
    var el=document.createElement('div');
    el.className='lbl';
    var b=document.createElement('div');b.className='b';b.textContent=String(i+1);
    var t=document.createElement('div');t.className='t';
    var nb=document.createElement('b');nb.textContent=p.def.n;
    var ii=document.createElement('i');ii.textContent=p.def.d;
    t.appendChild(nb);t.appendChild(ii);
    el.appendChild(b);el.appendChild(t);
    el.style.display='none';
    document.getElementById('lblLayer').appendChild(el);
    var line=document.createElementNS('http://www.w3.org/2000/svg','polyline');
    var dot=document.createElementNS('http://www.w3.org/2000/svg','circle');
    dot.setAttribute('r','2.6');
    lead.appendChild(line);lead.appendChild(dot);
    LBL.push({p:p,el:el,line:line,dot:dot,side:'L',ty:0,ay:0});
  });
}
function projPoint(v){
  var q=v.clone().project(camera);
  return {x:(q.x*.5+.5)*window.innerWidth,y:(-q.y*.5+.5)*window.innerHeight,z:q.z};
}
function updateLabels(){
  if(MODE!=='exploded')return;
  var W=window.innerWidth,H=window.innerHeight,cx=W/2;
  var narrow=W<760;
  var pad=64,padB=narrow?128:64;
  /* 底部界線＝控制列上緣（不能只用視窗高度，否則最下方標籤會壓到按鈕列／被切掉） */
  var _barEl=document.getElementById('bar');
  var LIM=(_barEl?_barEl.getBoundingClientRect().top:window.innerHeight)-12;
  var lead=document.getElementById('lead');
  lead.setAttribute('width',W);lead.setAttribute('height',H);
  LBL.forEach(function(L){
    var bb=new THREE.Box3().setFromObject(L.p.g);
    var ctr=bb.getCenter(new THREE.Vector3());
    var pr=projPoint(ctr);
    L.ax=pr.x;L.ay=pr.y;
    L.side=(pr.x<cx)?'L':'R';
    L.el.style.display='flex';
  });
  var colW=narrow?Math.max(118,Math.min(166,W*0.40)):Math.min(310,Math.max(150,W*0.235));
  ['L','R'].forEach(function(side){
    var arr=LBL.filter(function(L){return L.side===side;})
      .sort(function(a,b){return a.ay-b.ay;});
    var n=arr.length,avail=Math.max(120,LIM-pad),gap=narrow?46:54;
    if(n>1&&(n-1)*gap>avail)gap=avail/(n-1);
    var hh0=n?(arr[n-1].el.offsetHeight||56):0;
    var need=n?((n-1)*gap+hh0):0;
    if(n&&need>avail){
      /* 視窗太矮、放不下：平均分佈，寧可標籤靠緊也不要跑到畫面外 */
      var g2=Math.max(10,(avail-hh0)/Math.max(1,n-1));
      var y0=Math.max(pad,LIM-hh0-(n-1)*g2);
      for(var q=0;q<n;q++)arr[q].ty=y0+q*g2;
    }else{
      /* 1) 由上往下推開  2) 底部夾住  3) 由下往上回推  4) 整組下移避免超出上緣 */
      for(var i=0;i<n;i++){
        arr[i].ty=arr[i].ay;
        if(i>0&&arr[i].ty-arr[i-1].ty<gap)arr[i].ty=arr[i-1].ty+gap;
      }
      if(n){var _h=arr[n-1].el.offsetHeight||56;arr[n-1].ty=Math.min(arr[n-1].ty,LIM-_h);}
      for(var k=n-2;k>=0;k--){
        if(arr[k].ty>arr[k+1].ty-gap)arr[k].ty=arr[k+1].ty-gap;
      }
      if(n&&arr[0].ty<pad){
        var d=pad-arr[0].ty;
        for(var j=0;j<n;j++)arr[j].ty+=d;
      }
      if(n){
        var _hh=arr[n-1].el.offsetHeight||56;
        var _ov=(arr[n-1].ty+_hh)-LIM;
        if(_ov>0){for(var j2=0;j2<n;j2++)arr[j2].ty-=_ov;}
      }
    }
    arr.forEach(function(L){
      L.el.className='lbl '+(side==='L'?'left':'right');
      L.el.style.width=colW+'px';
      L.el.style.top=Math.round(L.ty)+'px';
      var edgeX=(side==='L')?(colW-10):(W-colW+10);
      L.line.setAttribute('points',
        (edgeX+(side==='L'?4:-4)).toFixed(0)+','+Math.round(L.ty)+' '+
        (edgeX+(side==='L'?26:-26)).toFixed(0)+','+Math.round(L.ty)+' '+
        (L.ax+(side==='L'?9:-9)).toFixed(0)+','+L.ay.toFixed(0));
      L.dot.setAttribute('cx',L.ax.toFixed(1));L.dot.setAttribute('cy',L.ay.toFixed(1));
    });
  });
}

/* ═══════════════ 相機取景（解析式 fitBox） ═══════════════ */
function modelBox(){
  var b=new THREE.Box3();
  model.children.forEach(function(o){if(o.visible)b.expandByObject(o);});
  if(dimGroup.visible)b.union(new THREE.Box3().setFromObject(dimGroup));
  return b;
}
function fitBox(dir,pad){
  var b=modelBox();
  var c=b.getCenter(new THREE.Vector3()),size=b.getSize(new THREE.Vector3());
  var d=dir.clone().normalize();
  var up=new THREE.Vector3(0,1,0);
  var right=new THREE.Vector3().crossVectors(up,d).normalize();
  if(right.lengthSq()<1e-6)right.set(1,0,0);
  var upv=new THREE.Vector3().crossVectors(d,right).normalize();
  var tanV=Math.tan(camera.fov*Math.PI/360),tanH=tanV*camera.aspect;
  var hu=0,hr=0,hf=0,p=new THREE.Vector3();
  for(var i=0;i<8;i++){
    p.set(i&1?b.max.x:b.min.x,i&2?b.max.y:b.min.y,i&4?b.max.z:b.min.z).sub(c);
    hf=Math.max(hf,-p.dot(d));
    hr=Math.max(hr,Math.abs(p.dot(right)));
    hu=Math.max(hu,Math.abs(p.dot(upv)));
  }
  var dist=Math.max(hu/tanV,hr/tanH)*pad+hf;
  var pr=Math.max(size.x,size.y,size.z);
  /* near/far 隨尺度，但比例要收斂（near 太小會讓 0.1 mm 級間隙 z-fighting） */
  camera.near=Math.min(Math.max(pr*0.012,0.35),6);
  camera.far=pr*45;
  camera.updateProjectionMatrix();
  controls.target.copy(c);
  camera.position.copy(c).addScaledVector(d,dist);
  camera.lookAt(c);
  controls.update();
  return b;
}
var DIRS={
  asm:new THREE.Vector3(0.62,0.46,0.80),
  exploded:new THREE.Vector3(0.46,0.30,0.90),
  dims:new THREE.Vector3(0.58,0.40,0.82)
};
function padOf(mode){
  var narrow=window.innerWidth<760;
  if(mode==='exploded')return narrow?1.92:1.40;
  if(mode==='dims')return narrow?1.60:1.22;
  return narrow?1.28:1.14;
}
var userMoved=false;
controls.addEventListener('start',function(){userMoved=true;});

/* ═══════════════ 模式 ═══════════════ */
var MODE='asm',EX=0,EXT=0,EXK=1.0;
var exr=document.getElementById('exr'),exv=document.getElementById('exv');
var lblLayer=document.getElementById('lblLayer');

function setMode(m,instant){
  MODE=m;
  var bs=document.querySelectorAll('#bar button[data-mode]');
  for(var i=0;i<bs.length;i++)bs[i].className=(bs[i].getAttribute('data-mode')===m)?'on':'';
  axisLine.visible=(m==='exploded');
  lblLayer.style.display=(m==='exploded')?'block':'none';
  dimGroup.visible=(m==='dims');
  /* 爆炸圖要留左右標籤欄，圖例會壓到左下標籤 → 收起 */
  document.getElementById('legend').style.display=(m==='exploded')?'none':'';
  if(m==='exploded'){EXT=(exr.value|0)/100;if(EXT<0.35){EXT=1;exr.value=100;}}
  else{EXT=0;exr.value=0;}
  exv.textContent=Math.round(EXT*100)+'%';
  if(instant)EX=EXT;
  clearFocus(true);
  applyExplode();
  userMoved=false;
  fitBox(DIRS[m]||DIRS.asm,padOf(m));
  MODEFIT[m]=camera.position.distanceTo(controls.target);
  updateLabels();
  hideInfo();
  syncSlider();
  try{renderer.render(scene,camera);}catch(e){}
  window.__bs.mode=m;
}
function applyExplode(){
  var t=EX*EXK;
  for(var i=0;i<PARTS.length;i++){
    var p=PARTS[i];
    p.g.position.copy(p.home).addScaledVector(p.ex,t);
    /* 特寫：選中的零件沿相機方向再往前推，成為最前層 */
    if(FOCUS.rec&&p===FOCUS.rec&&FOCUS.t>0.0005)
      p.g.position.addScaledVector(FOCUS.dir,FOCUS.push*FOCUS.t);
  }
  model.updateMatrixWorld(true);
  /* 爆炸時地板下沉，讓零件不被地面切掉 */
  floor.position.y=(MODE==='exploded')?FLOOR_Y-14:FLOOR_Y;
  grid.position.y=floor.position.y+0.02;
}





/* ═══════════════ 特寫（爆炸圖：點零件 → 推到最前層＋相機特寫） ═══════════════ */
var FOCUS={rec:null,t:0,tgt:0,fade:0,fadeTgt:0,push:0,dir:new THREE.Vector3(),
  camDir:new THREE.Vector3(),camDist:0,lockCam:false,homeCam:null,homeTgt:null};
var FADED=[];
var outlineRec=null;
var MODEFIT={asm:0,exploded:0,dims:0};
var _fv=new THREE.Vector3(),_fw=new THREE.Vector3(),_fc=new THREE.Vector3();

function partCenter(rec,out){
  var bb=new THREE.Box3().setFromObject(rec.g);
  return bb.getCenter(out||new THREE.Vector3());
}
function partRadius(rec){
  var s=new THREE.Box3().setFromObject(rec.g).getSize(new THREE.Vector3());
  return Math.max(s.x,s.y,s.z)*0.5;
}
function partById(id){
  for(var i=0;i<PARTS.length;i++)if(PARTS[i].id===id)return PARTS[i];
  return null;
}
/* 其他零件淡化：每個 mesh 一律 clone 材質再改，回位時整組換回原材質 */
function fadeOthers(keep){
  restoreFaded();
  for(var i=0;i<PARTS.length;i++){
    var p=PARTS[i];
    if(p===keep)continue;
    p.g.traverse(function(o){
      if(!o.isMesh||!o.material)return;
      var orig=o.material,cl;
      if(Object.prototype.toString.call(orig)==='[object Array]'){
        cl=[];
        for(var k=0;k<orig.length;k++){
          var c=orig[k].clone();
          c.userData._oop=(orig[k].opacity===undefined?1:orig[k].opacity);
          c.userData._osrc=orig[k].uuid;c.transparent=true;c.depthWrite=false;cl.push(c);
        }
      }else{
        cl=orig.clone();
        cl.userData._oop=(orig.opacity===undefined?1:orig.opacity);
        cl.userData._osrc=orig.uuid;cl.transparent=true;cl.depthWrite=false;
      }
      o.userData._omat=orig;o.material=cl;
      FADED.push({o:o,orig:orig,cl:cl});
    });
  }
}
function restoreFaded(){
  for(var i=0;i<FADED.length;i++){
    var e=FADED[i];
    if(e.o.userData._omat===e.orig)e.o.material=e.orig;
    if(Object.prototype.toString.call(e.cl)==='[object Array]'){
      for(var k=0;k<e.cl.length;k++)e.cl[k].dispose();
    }else e.cl.dispose();
  }
  FADED.length=0;
}
function focusPart(rec){
  if(!rec)return;
  if(!FOCUS.homeCam){
    FOCUS.homeCam=camera.position.clone();
    FOCUS.homeTgt=controls.target.clone();
  }
  FOCUS.rec=rec;FOCUS.tgt=1;FOCUS.fadeTgt=1;FOCUS.lockCam=false;
  FOCUS.dir.subVectors(camera.position,controls.target).normalize();
  FOCUS.camDir.copy(FOCUS.dir);
  /* 推出量：沿相機方向必須超過所有其他零件的中心 */
  var c0=partCenter(rec,_fc);
  var need=0;
  for(var i=0;i<PARTS.length;i++){
    var p=PARTS[i];
    if(p===rec||p.g.visible===false)continue;
    var c1=partCenter(p,_fw);
    var d=_fv.subVectors(c1,c0).dot(FOCUS.dir);
    if(d>need)need=d;
  }
  var r=partRadius(rec);
  FOCUS.push=need+r*1.7+2;
  var d0=MODEFIT[MODE]||camera.position.distanceTo(controls.target);
  /* 特寫距離：以零件大小為主（約佔畫面四成），最遠不超過該模式取景距離的 0.45 */
  var lo=Math.max(r*2.6,controls.minDistance*1.02);
  var hi=Math.max(d0*0.45,r*2.6);
  FOCUS.camDist=Math.max(lo,Math.min(r*6.5,hi));
  fadeOthers(rec);
  outlineRec=rec;
}
function clearFocus(instant){
  if(!FOCUS.rec&&FOCUS.t<0.001&&FOCUS.tgt===0&&!FOCUS.homeCam)return;
  FOCUS.rec=null;FOCUS.tgt=0;FOCUS.fadeTgt=0;FOCUS.lockCam=false;
  outlineRec=null;
  if(instant){
    FOCUS.t=0;FOCUS.fade=0;restoreFaded();
    FOCUS.homeCam=null;FOCUS.homeTgt=null;
    applyExplode();
  }
}
function focusTick(dt){
  var a=1-Math.exp(-dt/0.13);
  var moved=false;
  if(Math.abs(FOCUS.t-FOCUS.tgt)>0.0015){FOCUS.t+=(FOCUS.tgt-FOCUS.t)*a;moved=true;}
  else if(FOCUS.t!==FOCUS.tgt){FOCUS.t=FOCUS.tgt;moved=true;}
  if(Math.abs(FOCUS.fade-FOCUS.fadeTgt)>0.0015){FOCUS.fade+=(FOCUS.fadeTgt-FOCUS.fade)*a;moved=true;}
  else if(FOCUS.fade!==FOCUS.fadeTgt){FOCUS.fade=FOCUS.fadeTgt;moved=true;}
  if(moved)applyExplode();
  if(FADED.length){
    var f=FOCUS.fade;
    for(var i=0;i<FADED.length;i++){
      var cl=FADED[i].cl;
      if(Object.prototype.toString.call(cl)==='[object Array]'){
        for(var k=0;k<cl.length;k++)cl[k].opacity=cl[k].userData._oop*(1-0.78*f);
      }else cl.opacity=cl.userData._oop*(1-0.78*f);
    }
    if(f<0.005)restoreFaded();
  }
  if(FOCUS.rec){
    if(!FOCUS.lockCam){
      partCenter(FOCUS.rec,_fc);
      controls.target.lerp(_fc,a);
      _fv.copy(_fc).addScaledVector(FOCUS.camDir,FOCUS.camDist);
      camera.position.lerp(_fv,a);
    }
  }else if(FOCUS.homeCam){
    controls.target.lerp(FOCUS.homeTgt,a);
    camera.position.lerp(FOCUS.homeCam,a);
    if(camera.position.distanceTo(FOCUS.homeCam)<0.6&&FOCUS.t<0.01){
      FOCUS.homeCam=null;FOCUS.homeTgt=null;
    }
  }
  if(outline&&outlineRec){partCenter(outlineRec,_fc);outline.position.copy(_fc);}
  updateFloorVis();
}
/* 轉到底部時：地板／格線收起、霧距放大、半球光提亮
   （只在 phi>1.75 生效，正面／爆炸／尺寸等既有視角亮度完全不變） */
var FOG0=scene.fog?{near:scene.fog.near,far:scene.fog.far}:null;
var HEMI0={i:hemi.intensity,g:hemi.groundColor.getHex()};
var BOTTOM={low:false};
function updateFloorVis(){
  _fv.subVectors(camera.position,controls.target);
  var len=_fv.length();
  if(len<1e-6)return;
  var phi=Math.acos(Math.max(-1,Math.min(1,_fv.y/len)));
  var low=(phi>1.75);
  if(floor.visible===low){floor.visible=!low;grid.visible=!low;}
  if(low!==BOTTOM.low){
    BOTTOM.low=low;
    if(FOG0){
      scene.fog.near=low?FOG0.near*1.6:FOG0.near;
      scene.fog.far=low?FOG0.far*1.6:FOG0.far;
    }
    hemi.intensity=low?0.80:HEMI0.i;
    hemi.groundColor.setHex(low?0x7d8f88:HEMI0.g);
  }
}
/* 出圖驗證用：?polar=<弧度>&az=<弧度> 直接指定極角／方位角 */
function setPolarView(phi,az){
  _fv.subVectors(camera.position,controls.target);
  var dist=_fv.length();
  var th=(az===undefined||isNaN(az))?Math.atan2(_fv.x,_fv.z):az;
  var sp=Math.sin(phi);
  camera.position.set(controls.target.x+dist*sp*Math.sin(th),
    controls.target.y+dist*Math.cos(phi),
    controls.target.z+dist*sp*Math.cos(th));
  camera.lookAt(controls.target);
  controls.update();
  updateFloorVis();
}
function applyQueryView(){
  if(isNaN(QPOLAR)&&isNaN(QAZ))return;
  _fv.subVectors(camera.position,controls.target);
  var len=_fv.length()||1;
  var phi=isNaN(QPOLAR)?Math.acos(Math.max(-1,Math.min(1,_fv.y/len))):QPOLAR;
  var az=isNaN(QAZ)?Math.atan2(_fv.x,_fv.z):QAZ;
  setPolarView(phi,az);
  userMoved=true;   /* 指定視角後，視窗 resize 不要重新取景蓋掉 */
}
function __focusDbg(){
  return {
    get polar(){return controls.maxPolarAngle;},
    get minPolar(){return controls.minPolarAngle;},
    get phi(){_fv.subVectors(camera.position,controls.target);
      return +(Math.acos(Math.max(-1,Math.min(1,_fv.y/_fv.length())))).toFixed(3);},
    get floorVis(){return floor.visible;},
    get focusId(){return FOCUS.rec?FOCUS.rec.id:null;},
    get focusT(){return +FOCUS.t.toFixed(3);},
    get focusFade(){return +FOCUS.fade.toFixed(3);},
    get push(){return +FOCUS.push.toFixed(2);},
    get camDist(){return +camera.position.distanceTo(controls.target).toFixed(1);},
    setPolar:function(p,a){setPolarView(p,a);},
    /* 驗證用：以固定 16.7ms 步進推進動畫（不需等真實時間） */
    advance:function(sec){var n=Math.max(1,Math.round(sec*1000/16.7));
      for(var i=0;i<n;i++)focusTick(0.0167);
      controls.update();renderer.render(scene,camera);
      return {t:+FOCUS.t.toFixed(3),fade:+FOCUS.fade.toFixed(3)};},
    focus:function(id){var r=partById(id);if(!r)return null;showInfo(r);return r.id;},
    cancel:function(){hideInfo();return true;},
    posOf:function(id){var r=partById(id);if(!r)return null;
      var c=partCenter(r);return [+c.x.toFixed(2),+c.y.toFixed(2),+c.z.toFixed(2)];},
    opacOf:function(id){var r=partById(id);if(!r)return null;
      var v=1;r.g.traverse(function(o){if(o.isMesh&&o.material&&!o.material.length)v=o.material.opacity;});
      return +v.toFixed(3);}
  };
}


/* ═══════════════ 外殼顏色（換色不動幾何，共用材質一起換） ═══════════════ */
var SHELLM=[{k:'stand',f:1},{k:'stand2',f:0.94},{k:'standIn',f:0.88}];
var SHELLC=[['霧白','e9e0d4'],['石墨','2f3336'],['水泥灰','9a968d'],['霧綠','6f8a5f'],['陶土','93522f']];
function shadeHex(hex,f){var c=new THREE.Color(hex);c.multiplyScalar(f);return c;}
function setShellColor(hex){
  if(hex.charAt(0)!=='#')hex='#'+hex;
  var map={},i,j,k;
  /* 這三頁的打光偏亮（實測乳白色外殼渲染後接近 238），中間調色會被洗成白色，
     所以「非預設色」統一乘上 GAIN 壓暗，顏色才看得出來；預設色維持原值不動。 */
  var GAIN=0.52;
  var isDefault=(hex.toLowerCase()==='#'+SHELLC[0][1].toLowerCase());
  var gain=isDefault?1:GAIN;
  for(i=0;i<SHELLM.length;i++){
    var m=M[SHELLM[i].k];if(!m)continue;
    m.color.set(hex);
    var f=(SHELLM[i].f===1?1:SHELLM[i].f)*gain;
    if(f!==1)m.color.multiplyScalar(f);
    map[m.uuid]=m.color.getHex();
  }
  /* 已被淡化的 clone 材質也要一起換色，否則特寫時會殘留舊色 */
  for(i=0;i<FADED.length;i++){
    var cl=FADED[i].cl,arr=(cl.length!==undefined)?cl:[cl];
    for(k=0;k<arr.length;k++){
      var src=arr[k].userData._osrc;
      if(src&&map[src]!==undefined)arr[k].color.setHex(map[src]);
    }
  }
  var els=document.querySelectorAll('#csw b');
  for(j=0;j<els.length;j++)els[j].className=(els[j].getAttribute('data-c')===hex.replace('#',''))?'on':'';
  window.__shellHex=hex;
  if(renderer&&scene)renderer.render(scene,camera);
}
(function wireShell(){
  /* 色球一律由 SHELLC 產生（單一來源），避免 HTML 寫死色號與 JS 不同步 */
  var box=document.getElementById('csw');
  for(var i=0;i<SHELLC.length;i++){
    var b=document.createElement('b');
    b.setAttribute('data-c',SHELLC[i][1]);
    b.setAttribute('title',SHELLC[i][0]);
    b.style.background='#'+SHELLC[i][1];
    b.onclick=function(){setShellColor('#'+this.getAttribute('data-c'));};
    box.appendChild(b);
  }
  setShellColor(SHELLC[0][1]);
})();
/* 出圖／分享用：?shell=<6 碼色號> 直接指定外殼顏色 */
var QSHELL=((location.search||'').match(/[?&]shell=([0-9a-fA-F]{6})/)||[])[1];
if(QSHELL)setShellColor('#'+QSHELL);
window.__shell={set:function(h){setShellColor(h);},
  get hex(){return window.__shellHex;},
  get matHex(){var m=M[SHELLM[0].k];return m?m.color.getHexString():null;},
  get keys(){return SHELLM.map(function(s){return s.k;});},
  matOf:function(k){var m=M[k];return m?m.color.getHexString():null;},
  get list(){return SHELLC.map(function(c){return c[1];});}};

/* ═══════════════ 點選 ═══════════════ */
var ray=new THREE.Raycaster(),ndc=new THREE.Vector2();
var outline=null;
function clearOutline(){
  if(outline){scene.remove(outline);outline.geometry.dispose();outline=null;}
}
function showInfo(rec){
  var el=document.getElementById('finfo');
  if(!rec){el.style.display='none';clearOutline();return;}
  var inf=rec.g.userData.info;
  el.innerHTML='';
  var h=document.createElement('h4');
  var n=document.createElement('span');n.className='n';n.textContent=rec.num||'•';
  var tx=document.createElement('span');tx.textContent=inf.t;
  var x=document.createElement('span');x.className='x';x.textContent='✕';
  x.onclick=function(){hideInfo();};
  h.appendChild(n);h.appendChild(tx);h.appendChild(x);
  el.appendChild(h);
  inf.rows.forEach(function(r){
    var d=document.createElement('div');d.className='row';
    var u=document.createElement('u');u.textContent=r[0];
    var b=document.createElement('b');b.textContent=r[1];
    d.appendChild(u);d.appendChild(b);el.appendChild(d);
  });
  var hh=document.createElement('div');hh.className='hint';
  hh.textContent=(MODE==='exploded')?'已推到最前層特寫 · 點空白處或「取消特寫」回原位':'點空白處可取消選取';
  el.appendChild(hh);
  el.style.display='flex';
  clearOutline();
  var bb=new THREE.Box3().setFromObject(rec.g);
  var size=bb.getSize(new THREE.Vector3()),c=bb.getCenter(new THREE.Vector3());
  outline=new THREE.LineSegments(new THREE.EdgesGeometry(
    new THREE.BoxGeometry(size.x*1.06+1.0,size.y*1.06+1.0,size.z*1.06+1.0)),
    new THREE.LineBasicMaterial({color:0xff8a5c,transparent:true,opacity:.95,depthTest:false}));
  outline.position.copy(c);outline.renderOrder=997;scene.add(outline);
  /* 爆炸圖：點零件 → 飛到最前層特寫；其他零件淡化 */
  if(MODE==='exploded')focusPart(rec);else clearFocus(true);
}
function hideInfo(){document.getElementById('finfo').style.display='none';clearOutline();clearFocus(false);}
window.hideInfo=hideInfo;

function pickAt(cx,cy){
  var r=renderer.domElement.getBoundingClientRect();
  ndc.x=((cx-r.left)/r.width)*2-1;ndc.y=-((cy-r.top)/r.height)*2+1;
  ray.setFromCamera(ndc,camera);
  var hits=ray.intersectObjects(model.children,true);
  for(var i=0;i<hits.length;i++){
    var o=hits[i].object;
    while(o&&o!==model){
      if(o.userData&&o.userData.rec)return o.userData.rec;
      o=o.parent;
    }
  }
  return null;
}
var downPt=null;
renderer.domElement.addEventListener('pointerdown',function(e){
  downPt={x:e.clientX,y:e.clientY};
});
renderer.domElement.addEventListener('pointerup',function(e){
  if(!downPt)return;
  var moved=Math.hypot(e.clientX-downPt.x,e.clientY-downPt.y);
  downPt=null;
  if(moved>7)return;
  var rec=pickAt(e.clientX,e.clientY);
  if(rec)showInfo(rec);else hideInfo();
});

/* ═══════════════ UI ═══════════════ */
/* 模式按鈕一律走事件委派：單一入口，出錯會顯示在 #err，不會靜默失效 */
function modeBtnOf(t){
  while(t&&t!==document){
    if(t.getAttribute&&t.getAttribute('data-mode'))return t;
    t=t.parentNode;
  }
  return null;
}
document.getElementById('bar').addEventListener('click',function(ev){
  var b=modeBtnOf(ev.target);if(!b)return;
  try{setMode(b.getAttribute('data-mode'));}
  catch(e){
    var el=document.getElementById('err');
    if(el){el.style.display='block';el.textContent='切換模式失敗：'+(e&&e.message?e.message:e);}
    if(window.console)console.error(e);
  }
});
document.getElementById('breset').onclick=function(){
  userMoved=false;
  clearFocus(true);
  fitBox(DIRS[MODE],padOf(MODE));
  updateLabels();
};
var bfocusEl=document.getElementById('bfocus');
if(bfocusEl)bfocusEl.onclick=function(){hideInfo();};   /* 取消特寫：還原材質＋相機回原取景 */
exr.oninput=function(){
  EXT=(this.value|0)/100;
  exv.textContent=Math.round(EXT*100)+'%';
  if(MODE!=='exploded'&&EXT>0.02)setMode('exploded',true);
};
function syncSlider(){
  var on=(MODE==='exploded');
  exr.disabled=!on;
  document.querySelector('#bar2 .wrap').style.opacity=on?1:0.45;
}
window.addEventListener('resize',function(){
  renderer.setSize(window.innerWidth,window.innerHeight);
  camera.aspect=window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  if(!userMoved)fitBox(DIRS[MODE],padOf(MODE));
  updateLabels();
});

/* ═══════════════ 主迴圈 ═══════════════ */
var spin=SHOT?0:0.05;
var last=performance.now(),frame=0;
var STILL=/[?&]still=1/.test(QS);   /* 驗證用：停止連續渲染，主執行緒才不會被軟體 GL 佔滿 */
function tick(){
  if(!STILL||frame<3)requestAnimationFrame(tick);
  var now=performance.now(),dt=Math.min((now-last)/16.7,3);last=now;
  if(Math.abs(EX-EXT)>0.001){
    EX+=(EXT-EX)*Math.min(0.16*dt,0.55);
    if(Math.abs(EX-EXT)<0.002)EX=EXT;
    applyExplode();
  }
  if(!SHOT&&!userMoved&&MODE==='asm'){
    var off=new THREE.Vector3().subVectors(camera.position,controls.target);
    off.applyAxisAngle(new THREE.Vector3(0,1,0),spin*0.0016*dt*16.7);
    camera.position.copy(controls.target).add(off);
  }
  focusTick(dt*16.7/1000);
  updateFloorVis();
  controls.update();
  if(MODE==='exploded')updateLabels();
  if(outline){outline.material.opacity=0.70+0.28*Math.sin(now*0.004);}
  renderer.render(scene,camera);
  frame++;
  window.__frames=frame;
}

/* ═══════════════ 顯示健康狀態與自動回復 ═══════════════ */
var GLDIAG={lost:false};
var diagEl=document.getElementById('diag');
var DIAGON=/[?&]diag=1/.test(location.search||'');
if(DIAGON&&diagEl)diagEl.style.display='block';
renderer.domElement.addEventListener('webglcontextlost',function(e){
  e.preventDefault();GLDIAG.lost=true;
  var el=document.getElementById('err');
  if(el){el.style.display='block';
    el.textContent='顯示已中止（WebGL context lost）→ 請按 ⌘R 重新整理這一頁';}
},false);
renderer.domElement.addEventListener('webglcontextrestored',function(){
  GLDIAG.lost=false;
  var el=document.getElementById('err');
  if(el&&/context lost/.test(el.textContent))el.style.display='none';
},false);
var _lf=-1,_stall=0;
setInterval(function(){
  var gl=null,ok=false,txt='';
  try{gl=renderer.getContext();ok=!!gl&&!gl.isContextLost();}catch(e){}
  if(frame!==_lf){_lf=frame;_stall=0;}
  else{
    _stall++;
    if(ok&&!document.hidden&&_stall>=4&&!STILL){   /* 主迴圈卡住就再踢一次（出圖模式不踢） */
      _stall=0;requestAnimationFrame(tick);
      try{renderer.render(scene,camera);}catch(e){}
    }
  }
  if(DIAGON&&diagEl){
    try{
      var ext=gl&&gl.getExtension('WEBGL_debug_renderer_info');
      txt=ext?String(gl.getParameter(ext.UNMASKED_RENDERER_WEBGL)):'unknown';
    }catch(e){txt='n/a';}
    diagEl.textContent='frames '+frame+' · mode '+MODE+' · ctx '+(ok?'ok':'LOST')+
      '\nGL '+txt+'\nerrors '+(window.__errors?window.__errors.length:0)+
      ' · shell '+(window.__shellHex||'-');
  }
},500);

/* ═══════════════ 啟動 ═══════════════ */
window.__M=M;
window.__bs={
  mode:'asm',
  M:M,
  __f:__focusDbg(),
  redraw:function(){renderer.render(scene,camera);},
  /* 驗證用：以指定視窗比例重新取景，回傳 NDC 命中的零件與材質色 */
  hitNdc:function(nx,ny,aw,ah){
    camera.aspect=aw/ah;camera.updateProjectionMatrix();
    fitBox(DIRS[MODE],padOf(MODE));
    renderer.render(scene,camera);
    var rc=new THREE.Raycaster();
    rc.setFromCamera(new THREE.Vector2(nx,ny),camera);
    var hits=rc.intersectObjects(model.children,true);
    var out=[];
    for(var i=0;i<Math.min(hits.length,4);i++){
      var o=hits[i].object,rec=null;
      while(o&&o!==model){if(o.userData&&o.userData.rec){rec=o.userData.rec;break;}o=o.parent;}
      var mm=Array.isArray(hits[i].object.material)?hits[i].object.material[0]:hits[i].object.material;
      out.push({part:rec?rec.def.n:'?',geom:hits[i].object.geometry.type,
        col:mm&&mm.color?('#'+mm.color.getHexString()):null,
        emissive:(mm&&mm.emissive&&mm.emissive.getHex())?('#'+mm.emissive.getHexString()):null,
        d:+hits[i].distance.toFixed(1)});
    }
    return out;
  },
  hide:function(id,v){PARTS.forEach(function(p){if(p.id===id)p.g.visible=!v;});
    renderer.render(scene,camera);},
  get labels(){return document.querySelectorAll('.lbl').length;},
  get leads(){return document.querySelectorAll('#lead polyline').length;},
  get parts(){return PARTS.length;},
  get names(){return PARTS.map(function(p){return p.def.n;});},
  get errors(){return window.__errors;},
  get bbox(){var b=modelBox();var s=b.getSize(new THREE.Vector3());
    return [+s.x.toFixed(2),+s.y.toFixed(2),+s.z.toFixed(2)];},
  boxes:function(){return PARTS.map(function(p){var b=new THREE.Box3().setFromObject(p.g);
    return {n:p.def.n,y:[+b.min.y.toFixed(1),+b.max.y.toFixed(1)],
            z:[+b.min.z.toFixed(1),+b.max.z.toFixed(1)],
            x:[+b.min.x.toFixed(1),+b.max.x.toFixed(1)]};});},
  get cam(){return camera.position.toArray().map(function(v){return +v.toFixed(1);});},
  get info(){var e=document.getElementById('finfo');return e.style.display!=='none'?e.textContent:'';},
  view:function(v){setMode(v,true);},
  explode:function(v){EXT=v;EX=v;applyExplode();},
  pick:function(x,y){var r=pickAt(x,y);return r?r.def.n:null;},
  pickPart:function(id){          /* 驗證用：以零件包圍盒中心投影點做 raycast */
    var arr=PARTS.filter(function(p){return p.id===id;});
    if(!arr.length)return 'no-part';
    var bb=new THREE.Box3().setFromObject(arr[0].g);
    var c=bb.getCenter(new THREE.Vector3());
    var q=c.clone().project(camera);
    var x=(q.x*.5+.5)*window.innerWidth,y=(-q.y*.5+.5)*window.innerHeight;
    var r=pickAt(x,y);
    if(r)showInfo(r);
    return r?r.def.n:null;
  },
  screenPix:function(){
    var sp=null;
    PARTS.forEach(function(p){if(p.id==='amoled')sp=p.g;});
    if(!sp)return null;
    var found=null;
    sp.traverse(function(o){if(o.isMesh&&o.material&&o.material.map&&o.material.emissiveMap)found=o;});
    if(!found)return null;
    var img=found.material.map.image;
    var cv=document.createElement('canvas');cv.width=96;cv.height=64;
    var c=cv.getContext('2d');c.drawImage(img,0,0,96,64);
    var d=c.getImageData(0,0,96,64).data;
    var s=0,mx=0;
    for(var i=0;i<d.length;i+=4){var l=(d[i]+d[i+1]+d[i+2])/3;s+=l;if(l>mx)mx=l;}
    return {avg:+(s/(d.length/4)).toFixed(1),max:mx};
  },
  /* 驗證用：以指定視窗比例重新取景並回傳零件的投影矩形（NDC 與解析度無關） */
  projAt:function(id,aw,ah){
    var oldA=camera.aspect;
    camera.aspect=aw/ah;camera.updateProjectionMatrix();
    fitBox(DIRS[MODE],padOf(MODE));
    var b=new THREE.Box3().setFromObject(PARTS.filter(function(p){return p.id===id;})[0].g);
    var x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
    for(var i=0;i<8;i++){
      var q=new THREE.Vector3(i&1?b.max.x:b.min.x,i&2?b.max.y:b.min.y,
        i&4?b.max.z:b.min.z).project(camera);
      var sx=(q.x*.5+.5)*aw,sy=(-q.y*.5+.5)*ah;
      x0=Math.min(x0,sx);x1=Math.max(x1,sx);y0=Math.min(y0,sy);y1=Math.max(y1,sy);
    }
    camera.aspect=oldA;camera.updateProjectionMatrix();
    fitBox(DIRS[MODE],padOf(MODE));
    return [Math.round(x0),Math.round(y0),Math.round(x1),Math.round(y1)];
  },
  uiTexURL:function(){
    var sp=null;
    PARTS.forEach(function(p){if(p.id==='amoled')sp=p.g;});
    if(!sp)return null;
    var found=null;
    sp.traverse(function(o){if(o.isMesh&&o.material&&o.material.map&&o.material.emissiveMap)found=o;});
    return found?found.material.map.image.toDataURL('image/png'):null;
  }
};
window.__pp=window.__bs;
setMode(VIEW==='exploded'?'exploded':(VIEW==='dims'?'dims':'asm'),true);
applyQueryView();
tick();
/* 出圖驗證用：把關鍵零件的投影矩形寫進 DOM（?probe=1） */
if(/[?&]probe=1/.test(QS)){
  setTimeout(function(){
    var out={w:window.innerWidth,h:window.innerHeight,parts:{}};
    PARTS.forEach(function(p){
      var b=new THREE.Box3().setFromObject(p.g);
      var x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
      for(var i=0;i<8;i++){
        var q=new THREE.Vector3(i&1?b.max.x:b.min.x,i&2?b.max.y:b.min.y,
          i&4?b.max.z:b.min.z).project(camera);
        var sx=(q.x*.5+.5)*window.innerWidth,sy=(-q.y*.5+.5)*window.innerHeight;
        x0=Math.min(x0,sx);x1=Math.max(x1,sx);y0=Math.min(y0,sy);y1=Math.max(y1,sy);
      }
      out.parts[p.id]=[Math.round(x0),Math.round(y0),Math.round(x1),Math.round(y1)];
    });
    var d=document.createElement('div');
    d.id='probejson';d.setAttribute('data-json',JSON.stringify(out));
    document.body.appendChild(d);
  },300);
}
window.__ready=true;
})();
</script>
"""


def build(outdir, libs=DEFAULT_LIBS):
    with open(os.path.join(libs, "three.min.js"), encoding="utf-8") as f:
        three = f.read()
    with open(os.path.join(libs, "OrbitControls.js"), encoding="utf-8") as f:
        orbit = f.read()
    html = (HTML_HEAD
            + "\n<script>\n" + three + "\n</script>\n<script>\n" + orbit + "\n</script>\n"
            + APP_JS + HTML_TAIL)
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "collar-base-system.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path, len(html.encode("utf-8"))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    libs = DEFAULT_LIBS
    if "--libs" in sys.argv:
        libs = sys.argv[sys.argv.index("--libs") + 1]
    p, n = build(out, libs)
    print(p, n)
