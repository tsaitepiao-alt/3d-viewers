#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
嘉蘭一號／二號 智慧頸環 — 雙型號 單檔 three.js 互動模型頁產生器（嘉蘭智慧科技）
輸出：pawpulse-system.html（three.js r128 + OrbitControls 內嵌，可離線雙擊）

三模式：組裝 / 爆炸 / 尺寸；型號切換：A 版（1.47" LCD）/ B 版（2.4" 滿版玻璃）

尺寸來源（不自行發明）：
  A 版  case-oled.html  DIMS 表：63×39×15、上蓋 6.8、下蓋 8.2、內腔 59.4×35.4、
                        壁厚 1.8、R7、PCB 58.1×34.1×1.6、LCD 視窗 33×18 R3、
                        電池槽 32×21×4.5（500mAh）、mic 2×⌀1.0、磁吸孔 2×⌀2.4、走帶槽 3.0
  B 版  collar.html / pawpulse-3d.html：表頭 56×44×17.8、可視 48.96×36.72、
                        背蓋 7.2、中框 6.0、螢幕 52×40×2.4、上蓋 3.0、電池 34×26×5.4、
                        PCB 38×30×1.2、FPC 12 線、振膜 ⌀28 外凸 5、套框 60×48×3.2 開窗 46×30、
                        磁鐵 ⌀6×2、pogo 孔 ⌀2.4 距 14、頸帶 20mm 織帶 2.5 厚
  元件   cat-collar-parts.html：XIAO ESP32S3 21×17.8×1.2、INMP441 4.72×3.76×1.0、
                        LSM6DS3TR-C 2.5×3.0×0.83、震動馬達 ⌀10×3.4、磁鐵 ⌀5×2、pogo ⌀1.5×5

用法：python3 build_pawpulse.py <輸出資料夾> [--libs /path/to/libs]
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
<title>嘉蘭一號・二號 智慧頸環 ｜ 嘉蘭智慧科技 · 3D 組裝・爆炸・尺寸</title>
<style>
  :root{
    --mint:#4be3a8; --mint2:#2fc98d; --coral:#ff7a59; --sky:#7bd3ff;
    --ink:#06100f; --bg:#070d10; --txt:#e6f2ee; --dim:#8fa5a0;
    --panel:rgba(12,22,22,.86); --line:rgba(75,227,168,.30);
  }
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{margin:0;height:100%;overflow:hidden;background:var(--bg);color:var(--txt);
    font-family:"PingFang TC","Noto Sans TC","Heiti TC","Microsoft JhengHei",system-ui,sans-serif}
  #app{position:fixed;inset:0}
  canvas{display:block}
  .panel{background:var(--panel);border:1px solid rgba(255,255,255,.09);border-radius:14px;
    backdrop-filter:blur(9px);-webkit-backdrop-filter:blur(9px);box-shadow:0 10px 30px rgba(0,0,0,.45)}

  /* ── 左上標題 ── */
  #hud{position:fixed;left:14px;top:14px;padding:11px 15px;z-index:20;max-width:min(46vw,336px)}
  #hud b{font-size:15px;letter-spacing:.4px;display:block;color:#fff}
  #hud b i{font-style:normal;color:var(--mint)}
  #hud span{font-size:11.5px;color:var(--dim);line-height:1.55;display:block;margin-top:4px}
  #hud .tag{display:inline-block;margin-top:7px;font-size:10.5px;color:var(--mint);
    border:1px solid var(--line);border-radius:999px;padding:2px 9px}
  #hud .tag b{display:inline;font-size:10.5px;color:var(--mint)}

  /* ── 型號切換 ── */
  #vsw{position:fixed;left:50%;top:14px;transform:translateX(-50%);display:flex;gap:5px;
    padding:5px;z-index:36}
  #vsw button{height:32px;padding:0 15px;border-radius:9px;border:1px solid rgba(255,255,255,.13);
    background:transparent;color:#cfe6de;font:600 12.5px/1 inherit;font-family:inherit;
    cursor:pointer;transition:.15s;letter-spacing:.3px}
  #vsw button small{display:block;font-size:9px;font-weight:500;color:var(--dim);margin-top:1px;letter-spacing:0}
  #vsw button.on{background:var(--mint);color:#06231b;border-color:var(--mint)}
  #vsw button.on small{color:#0a3a2c}

  /* ── 右上資訊卡 ── */
  #finfo{position:fixed;right:14px;top:14px;width:min(330px,44vw);padding:13px 15px 14px;
    display:none;flex-direction:column;gap:7px;z-index:40;border-color:rgba(75,227,168,.35)}
  #finfo h4{margin:0;font-size:15px;color:#fff;display:flex;align-items:center;gap:8px}
  #finfo h4 .n{display:inline-flex;width:22px;height:22px;border-radius:50%;background:var(--mint);
    color:#06231b;font-size:12px;font-weight:800;align-items:center;justify-content:center;flex:0 0 auto}
  #finfo h4 .x{margin-left:auto;cursor:pointer;color:var(--dim);font-size:15px;padding:0 2px}
  #finfo .row{font-size:12px;line-height:1.62;color:#d5e6e0;display:flex;gap:7px}
  #finfo .row u{text-decoration:none;color:var(--dim);flex:0 0 42px}
  #finfo .row b{font-weight:600;color:#fff}
  #finfo .hint{font-size:10.5px;color:var(--dim);border-top:1px solid rgba(255,255,255,.08);padding-top:7px}

  /* ── 零件標籤（爆炸圖） ── */
  #lblLayer{position:fixed;inset:0;pointer-events:none;z-index:15;display:none}
  #lead{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
  #lead polyline{fill:none;stroke:rgba(75,227,168,.58);stroke-width:1;stroke-dasharray:3 3}
  #lead circle{fill:var(--mint)}
  .lbl{position:absolute;transform:translateY(-50%);display:flex;gap:7px;align-items:flex-start;
    font-size:11.5px;line-height:1.32;color:#e4f0ec;pointer-events:none;
    text-shadow:0 1px 3px rgba(0,0,0,.9)}
  .lbl.left{left:0;padding-right:12px;justify-content:flex-end;text-align:right}
  .lbl.left .b{order:2}
  .lbl.right{right:0;padding-left:12px;justify-content:flex-start;text-align:left}
  .lbl .t{max-width:236px}
  .lbl .b{flex:0 0 auto;width:19px;height:19px;border-radius:50%;background:var(--mint);color:#06231b;
    font-size:10.5px;font-weight:800;display:flex;align-items:center;justify-content:center;margin-top:1px}
  .lbl .t b{display:block;font-weight:600;font-size:11.8px;color:#fff}
  .lbl .t i{font-style:normal;font-size:10.5px;color:#a8bdb6}

  /* ── 底部控制列 ── */
  #bar{position:fixed;left:0;right:0;bottom:10px;padding:0 10px;display:flex;justify-content:center;
    gap:7px;z-index:30;overflow-x:auto;flex-wrap:nowrap;scrollbar-width:none}
  #bar::-webkit-scrollbar{display:none}
  #bar button{flex:0 0 auto;height:38px;min-width:76px;padding:0 14px;border-radius:11px;cursor:pointer;
    border:1px solid rgba(255,255,255,.13);background:rgba(13,25,24,.9);color:#d7e8e2;
    font-size:12.5px;font-family:inherit;font-weight:600;letter-spacing:.3px;
    backdrop-filter:blur(9px);-webkit-backdrop-filter:blur(9px);transition:.16s}
  #bar button:hover{border-color:var(--line);color:#fff}
  #bar button.on{background:var(--mint);color:#06231b;border-color:var(--mint);
    box-shadow:0 6px 18px rgba(75,227,168,.22)}
  #bar2{position:fixed;left:0;right:0;bottom:60px;display:flex;justify-content:center;z-index:30;
    padding:0 12px;pointer-events:none}
  #bar2 .wrap{pointer-events:auto;display:flex;align-items:center;gap:10px;padding:6px 14px;
    border-radius:11px;background:rgba(11,22,21,.82);border:1px solid rgba(255,255,255,.09);
    backdrop-filter:blur(9px);-webkit-backdrop-filter:blur(9px);font-size:11.5px;color:var(--dim)}
  #bar2 input[type=range]{-webkit-appearance:none;appearance:none;width:min(38vw,210px);height:3px;
    background:rgba(255,255,255,.18);border-radius:2px;outline:none}
  #bar2 input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:15px;height:15px;
    border-radius:50%;background:var(--mint);border:2px solid #06231b;cursor:pointer}
  #bar2 #exv{color:var(--mint);font-weight:700;min-width:34px;text-align:right;font-variant-numeric:tabular-nums}

  /* ── 圖例 ── */
  #legend{position:fixed;left:14px;bottom:112px;padding:10px 13px;font-size:11px;color:var(--dim);
    line-height:1.8;z-index:18;max-width:238px}
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
    #vsw{left:auto;right:10px;transform:none;top:10px;padding:4px}
    #vsw button{height:34px;padding:0 11px;font-size:11.5px}
    #vsw button small{display:none}
    .lbl{font-size:10.5px}
    #bar{gap:6px;padding:0 8px;justify-content:flex-start}
    #bar button{min-width:68px;height:38px;font-size:12px;padding:0 11px}
    #bar2{bottom:64px}
  }
</style>
</head>
<body>
<div id="app"></div>

<div id="hud" class="panel">
  <b>嘉蘭一號 · 二號 <i>智慧頸環</i></b>
  <span>穿戴式心率／體溫／活動量監測・1 格 = 1 mm<br>拖曳旋轉 · 滾輪縮放 · 點零件看規格</span>
  <div class="tag" id="hudtag"><b>嘉蘭一號</b> ｜ 63 × 39 × 15 mm</div>
</div>

<div id="vsw" class="panel">
  <button data-v="a" class="on">嘉蘭一號<small>1.47 吋 LCD</small></button>
  <button data-v="b">嘉蘭二號<small>2.4 吋滿版玻璃</small></button>
</div>

<div id="finfo" class="panel"></div>

<div id="lblLayer">
  <svg id="lead" xmlns="http://www.w3.org/2000/svg"></svg>
</div>

<div id="legend" class="panel">
  <b>顏色語彙</b>
  <div><span class="sw" style="background:#f4f1ea"></span>機殼白 PLA／滿版黑玻璃</div>
  <div><span class="sw" style="background:#1f6b3c"></span>PCB 綠板＋金焊盤</div>
  <div><span class="sw" style="background:#cfd6dc"></span>鋁塑電池／鎳層磁鐵</div>
  <div><span class="sw" style="background:#4be3a8"></span>螢幕 UI／發光指示</div>
</div>

<div id="bar2"><div class="wrap">
  <span>爆炸程度</span><input id="exr" type="range" min="0" max="100" value="0" step="1"><span id="exv">0%</span>
</div></div>

<div id="bar">
  <button data-mode="asm" class="on">🏠 組裝</button>
  <button data-mode="exploded">🧩 爆炸</button>
  <button data-mode="dims">📐 尺寸</button>
  <button id="breset">↺ 重置視角</button>
</div>

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
var VKEY=((QS.match(/[?&]variant=([ab])/)||[])[1])||'a';

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
scene.background=new THREE.Color(0x070d10);
window.scene=scene;
scene.fog=new THREE.Fog(0x070d10,190,620);

var camera=new THREE.PerspectiveCamera(38,window.innerWidth/window.innerHeight,1,4000);
var controls=new THREE.OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;controls.dampingFactor=0.075;
controls.minDistance=40;controls.maxDistance=900;
controls.maxPolarAngle=Math.PI*0.56;controls.minPolarAngle=0.10;
controls.enablePan=false;
window.camera=camera;window.controls=controls;

/* ── 環境反射（中性灰，不能帶綠） ── */
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

/* ── 光源（實測值，別調高：會把零件洗成薄荷綠半透明） ── */
var hemi=new THREE.HemisphereLight(0xdde8e2,0x1b2320,0.50);scene.add(hemi);
var key=new THREE.DirectionalLight(0xfff6e8,1.45);
key.position.set(120,190,140);key.castShadow=true;
key.shadow.mapSize.set(2048,2048);
key.shadow.camera.left=-140;key.shadow.camera.right=140;
key.shadow.camera.top=160;key.shadow.camera.bottom=-90;
key.shadow.camera.near=1;key.shadow.camera.far=700;
key.shadow.bias=-0.0006;key.shadow.normalBias=0.55;
scene.add(key);
var fill=new THREE.DirectionalLight(0xcfe0ff,0.30);fill.position.set(-150,70,95);scene.add(fill);
var rim=new THREE.DirectionalLight(0x7bd3ff,0.42);rim.position.set(-85,60,-140);scene.add(rim);
var back=new THREE.DirectionalLight(0xffffff,0.55);back.position.set(40,40,-160);scene.add(back);

/* ── 地板（移遠讓陰影柔和，太近會像第二組零件） ── */
var floor=new THREE.Mesh(new THREE.CircleGeometry(420,64),
  new THREE.MeshStandardMaterial({color:0x010405,roughness:.98,metalness:0,envMapIntensity:0.05}));
floor.rotation.x=-Math.PI/2;floor.position.y=-72;floor.receiveShadow=true;scene.add(floor);
var grid=new THREE.GridHelper(700,70,0x1b2b29,0x0e1a19);
grid.position.y=-71.9;grid.material.transparent=true;grid.material.opacity=.30;scene.add(grid);

/* ═══════════════ 材質 ═══════════════ */
function mat(o){var m=new THREE.MeshStandardMaterial(o);m.side=THREE.DoubleSide;
  m.envMapIntensity=(o.metalness&&o.metalness>0.6)?1.20:0.20;return m;}
var M={
  shell:   mat({color:0xf4f1ea,roughness:.52,metalness:.02}),   /* 白 PLA 上/下蓋 */
  shell2:  mat({color:0xe6e1d6,roughness:.58,metalness:.02}),
  ink:     mat({color:0x14171a,roughness:.46,metalness:.10}),
  inkSoft: mat({color:0x24282c,roughness:.66,metalness:.05}),
  frame:   mat({color:0x2a2e33,roughness:.62,metalness:.06}),   /* 中框黑 ABS */
  glass:   mat({color:0x080b10,roughness:.14,metalness:.34}),
  glassBig:mat({color:0x0a0d12,roughness:.10,metalness:.42}),
  alu:     mat({color:0xb9bec2,roughness:.34,metalness:.90}),
  aluDark: mat({color:0x8b9297,roughness:.42,metalness:.85}),
  steel:   mat({color:0xcfd4d8,roughness:.24,metalness:1.10}),
  nickel:  mat({color:0xd7dce0,roughness:.20,metalness:1.30}),
  gold:    mat({color:0xd8b45a,roughness:.28,metalness:.95}),
  gold2:   mat({color:0xe8c877,roughness:.22,metalness:1.20}),
  pcb:     mat({color:0x1e6b3c,roughness:.56,metalness:.05}),
  pcbEdge: mat({color:0x17512d,roughness:.60,metalness:.05}),
  pouch:   mat({color:0xcfd6dc,roughness:.30,metalness:.70}),   /* 鋁塑膜 */
  pouch2:  mat({color:0xb9c2c9,roughness:.38,metalness:.66}),
  fpc:     mat({color:0xd08b3a,roughness:.48,metalness:.10}),
  motor:   mat({color:0xc3c9ce,roughness:.28,metalness:1.05}),
  red:     mat({color:0xc22a1c,roughness:.52,metalness:.04}),
  black:   mat({color:0x15181b,roughness:.62,metalness:.05}),
  strap:   mat({color:0x2f6360,roughness:.92,metalness:.0}),
  strap2:  mat({color:0x27524f,roughness:.94,metalness:.0}),
  buckle:  mat({color:0x2b3238,roughness:.52,metalness:.20}),
  emitG:   mat({color:0x45ffa8,roughness:.30,metalness:.10,emissive:0x18e07f,emissiveIntensity:2.0}),
  emitM:   mat({color:0x4be3a8,roughness:.40,metalness:.05,emissive:0x12694a,emissiveIntensity:.55}),
  rubber:  mat({color:0x1d2224,roughness:.94,metalness:0}),
  lcdBody: mat({color:0x0d1013,roughness:.36,metalness:.14})
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
/* 平面輪廓沿 +Y 擠出（y 由 0 起算） */
function extY(shape,h,seg){
  var g=new THREE.ExtrudeGeometry(shape,{depth:h,bevelEnabled:false,curveSegments:seg||16});
  g.rotateX(-Math.PI/2);
  return g;
}
/* 水平板（XZ 面，厚度沿 Y 置中） */
function hplate(w,d,t,r,seg){
  var g=new THREE.ExtrudeGeometry(rrShape(w,d,r),{depth:t,bevelEnabled:false,curveSegments:seg||16});
  g.translate(0,0,-t/2);g.rotateX(-Math.PI/2);
  return g;
}
/* 水平開窗框板材 */
function hframe(w,d,t,r,ww,wd,wr){
  var s=rrShape(w,d,r);s.holes.push(rrPath(ww,wd,wr));
  var g=new THREE.ExtrudeGeometry(s,{depth:t,bevelEnabled:false,curveSegments:20});
  g.translate(0,0,-t/2);g.rotateX(-Math.PI/2);
  return g;
}
function mesh(g,m){var o=new THREE.Mesh(g,m);o.castShadow=true;o.receiveShadow=true;return o;}
function box(w,h,d,m){return mesh(new THREE.BoxGeometry(w,h,d),m);}
function cylY(r1,r2,h,m,seg){return mesh(new THREE.CylinderGeometry(r1,r2,h,seg||28),m);}
function disc(r,h,m,seg){return mesh(new THREE.CylinderGeometry(r,r,h,seg||32),m);}

/* 帶狀物：沿曲線擠出扁平斷面（寬度 w 沿世界 +Z，厚度 t 沿徑向） */
function ribbon(pts,w,t,seg){
  var curve=new THREE.CatmullRomCurve3(pts,false,'catmullrom',0.35);
  var N=seg||80,pos=[],idx=[],UP=new THREE.Vector3(0,0,1);
  for(var i=0;i<=N;i++){
    var u=i/N,p=curve.getPoint(u),tg=curve.getTangent(u).normalize();
    var side=new THREE.Vector3().crossVectors(tg,UP).normalize();
    var upv=new THREE.Vector3().crossVectors(side,tg).normalize();
    var cor=[[-t/2,-w/2],[t/2,-w/2],[t/2,w/2],[-t/2,w/2]];
    for(var k=0;k<4;k++){
      pos.push(p.x+side.x*cor[k][0]+upv.x*cor[k][1],
               p.y+side.y*cor[k][0]+upv.y*cor[k][1],
               p.z+side.z*cor[k][0]+upv.z*cor[k][1]);
    }
  }
  for(var j=0;j<N;j++){
    var b=j*4,n=(j+1)*4;
    for(var q=0;q<4;q++){var q2=(q+1)%4;idx.push(b+q,b+q2,n+q2,b+q,n+q2,n+q);}
  }
  var g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(pos,3));
  g.setIndex(idx);g.computeVertexNormals();
  return g;
}

/* ═══════════════ 畫布貼圖：螢幕 UI ═══════════════ */
function drawDog(c,cx,cy,r){
  /* 耳朵 */
  [-1,1].forEach(function(s){
    c.save();c.translate(cx+s*r*0.84,cy-r*0.60);c.rotate(s*0.34);
    c.fillStyle='#c07f3a';c.beginPath();c.ellipse(0,0,r*0.30,r*0.50,0,0,7);c.fill();
    c.fillStyle='#945c26';c.beginPath();c.ellipse(0,r*0.04,r*0.16,r*0.30,0,0,7);c.fill();
    c.restore();
  });
  /* 頭 */
  var hg=c.createRadialGradient(cx-r*0.30,cy-r*0.36,r*0.16,cx,cy,r*1.18);
  hg.addColorStop(0,'#fbe3b6');hg.addColorStop(1,'#dda45c');
  c.fillStyle=hg;c.beginPath();c.arc(cx,cy,r,0,7);c.fill();
  /* 口鼻 */
  c.fillStyle='#fdf0d6';c.beginPath();c.ellipse(cx,cy+r*0.40,r*0.62,r*0.44,0,0,7);c.fill();
  /* 眼 */
  [-1,1].forEach(function(s){
    c.fillStyle='#20160f';
    c.beginPath();c.ellipse(cx+s*r*0.37,cy-r*0.12,r*0.115,r*0.150,0,0,7);c.fill();
    c.fillStyle='#ffffff';
    c.beginPath();c.arc(cx+s*r*0.40,cy-r*0.19,r*0.045,0,7);c.fill();
  });
  /* 鼻 */
  c.fillStyle='#20160f';
  c.beginPath();c.ellipse(cx,cy+r*0.20,r*0.145,r*0.115,0,0,7);c.fill();
  /* 嘴 */
  c.strokeStyle='#20160f';c.lineWidth=Math.max(2,r*0.055);c.lineCap='round';
  c.beginPath();c.arc(cx-r*0.13,cy+r*0.33,r*0.155,0.10,Math.PI*0.96);c.stroke();
  c.beginPath();c.arc(cx+r*0.13,cy+r*0.33,r*0.155,Math.PI*0.04,Math.PI*0.90);c.stroke();
  /* 舌 */
  c.fillStyle='#ff8092';
  c.beginPath();c.ellipse(cx,cy+r*0.63,r*0.125,r*0.165,0,0,7);c.fill();
}
function spaced(c,txt,x,y,sp,fill){
  c.fillStyle=fill;c.textAlign='left';c.textBaseline='middle';
  for(var i=0;i<txt.length;i++){c.fillText(txt[i],x,y);x+=c.measureText(txt[i]).width+sp;}
}
function uiTex(){
  var UW=V.ui.w,UH=V.ui.h;
  var W=1024,H=Math.round(W*UH/UW);
  var cv=document.createElement('canvas');cv.width=W;cv.height=H;
  var c=cv.getContext('2d');
  var u=H/100;
  var g=c.createLinearGradient(0,0,0,H);
  g.addColorStop(0,'#08202a');g.addColorStop(.55,'#04131c');g.addColorStop(1,'#020a10');
  c.fillStyle=g;c.fillRect(0,0,W,H);
  /* 螢幕邊緣內陰影 */
  var vg=c.createRadialGradient(W/2,H/2,H*0.2,W/2,H/2,H*0.85);
  vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(0,0,0,.55)');
  c.fillStyle=vg;c.fillRect(0,0,W,H);

  c.textBaseline='middle';
  /* ── 頂列：PAWPULSE ＋ 電量 ── */
  c.font='bold '+(8.4*u)+'px "Helvetica Neue",Arial,sans-serif';
  spaced(c,'JIALAN-1',5.5*u,8.5*u,1.5*u,'#4be3a8');
  /* 電量圖示 */
  var bx=W-20.5*u,by=5.6*u,bw=9.5*u,bh=5.6*u;
  c.strokeStyle='#9fe8cf';c.lineWidth=Math.max(1.4,0.7*u);
  c.beginPath();c.rect(bx,by,bw,bh);c.stroke();
  c.fillRect(bx+bw,by+bh*0.28,1.5*u,bh*0.44);
  c.fillStyle='#4be3a8';c.fillRect(bx+0.9*u,by+0.9*u,(bw-1.8*u)*0.78,bh-1.8*u);
  c.font='bold '+(6.4*u)+'px "Helvetica Neue",Arial,sans-serif';
  c.fillStyle='#d8fff1';c.textAlign='right';c.fillText('78%',bx-2.0*u,by+bh*0.55);

  /* ── 狗臉 ── */
  drawDog(c,W/2,H*0.455,H*0.175);

  /* ── 體溫小標籤（左上，狗臉旁） ── */
  c.font='bold '+(5.6*u)+'px "Helvetica Neue",Arial,sans-serif';
  c.textAlign='left';
  c.fillStyle='#ffcf8a';
  c.fillText('38.4\u00b0C',5.5*u,20.5*u);
  c.fillStyle='#6e8b86';
  c.font='500 '+(4.4*u)+'px "Helvetica Neue",Arial,sans-serif';
  c.fillText('BODY TEMP',5.5*u,25.5*u);

  /* ── 底部兩欄數據 ── */
  var dy=H*0.775;
  c.strokeStyle='rgba(120,190,170,.22)';c.lineWidth=Math.max(1,0.45*u);
  c.beginPath();c.moveTo(W/2,dy-6.5*u);c.lineTo(W/2,dy+9.5*u);c.stroke();
  /* 心率 */
  c.fillStyle='#ff6b83';
  (function(hx,hy,s){c.beginPath();
    c.moveTo(hx,hy+s*0.9);
    c.bezierCurveTo(hx-s*1.5,hy-s*0.25,hx-s*0.55,hy-s*1.1,hx,hy-s*0.35);
    c.bezierCurveTo(hx+s*0.55,hy-s*1.1,hx+s*1.5,hy-s*0.25,hx,hy+s*0.9);
    c.closePath();c.fill();})(6.5*u,dy-5.0*u,3.4*u);
  c.textAlign='left';
  c.fillStyle='#ffffff';c.font='bold '+(13.5*u)+'px "Helvetica Neue",Arial,sans-serif';
  c.fillText('92',12.5*u,dy);
  c.fillStyle='#8aa8a2';c.font='500 '+(4.8*u)+'px "Helvetica Neue",Arial,sans-serif';
  c.fillText('bpm',12.5*u+c.measureText('').width,dy+6.0*u);
  /* 步數 */
  c.fillStyle='#7bd3ff';
  c.font='bold '+(13.5*u)+'px "Helvetica Neue",Arial,sans-serif';
  c.textAlign='right';
  c.fillText('3,412',W-5.5*u,dy);
  c.fillStyle='#8aa8a2';c.font='500 '+(4.8*u)+'px "Helvetica Neue",Arial,sans-serif';
  c.fillText('STEPS',W-5.5*u,dy+6.0*u);
  c.textAlign='left';

  var t=new THREE.CanvasTexture(cv);
  t.anisotropy=8;t.encoding=THREE.sRGBEncoding;
  return t;
}
function uiMat(){
  var tex=uiTex();
  var m=new THREE.MeshStandardMaterial({map:tex,emissive:0xffffff,emissiveMap:tex,
    emissiveIntensity:0.95,color:0x9a9a9a,roughness:.44,metalness:0,side:THREE.DoubleSide});
  m.envMapIntensity=0.05;
  return m;
}

/* ═══════════════ 畫布貼圖：PCB 絲印 / 電池標籤 ═══════════════ */
function pcbTex(w,d){
  var W=1024,H=Math.round(1024*d/w);
  var cv=document.createElement('canvas');cv.width=W;cv.height=H;
  var c=cv.getContext('2d');
  c.fillStyle='#1e6b3c';c.fillRect(0,0,W,H);
  /* 阻焊深淺塊 */
  for(var i=0;i<26;i++){
    c.fillStyle='rgba(255,255,255,.035)';
    c.fillRect(Math.random()*W,Math.random()*H,20+Math.random()*90,8+Math.random()*40);
  }
  /* 走線 */
  c.strokeStyle='rgba(210,235,200,.20)';
  for(var k=0;k<70;k++){
    c.lineWidth=1+Math.random()*1.6;c.beginPath();
    var x=Math.random()*W,y=Math.random()*H;
    c.moveTo(x,y);
    for(var s=0;s<4;s++){x+=(Math.random()-0.5)*W*0.30;y+=(Math.random()-0.5)*H*0.30;c.lineTo(x,y);}
    c.stroke();
  }
  /* 金色焊盤 */
  c.fillStyle='#d8b45a';
  for(var p=0;p<46;p++){
    var px=Math.random()*W,py=Math.random()*H,r=4+Math.random()*8;
    c.beginPath();c.arc(px,py,r,0,7);c.fill();
  }
  /* 絲印 */
  c.fillStyle='rgba(245,250,240,.90)';
  c.font='bold 42px "Helvetica Neue",Arial,sans-serif';
  c.fillText('JIALAN-1  v1.0',W*0.055,H*0.20);
  c.font='26px "Helvetica Neue",Arial,sans-serif';
  c.fillText('ESP32-S3  \u00b7  PPG  \u00b7  IMU  \u00b7  BLE 5.0',W*0.055,H*0.30);
  c.font='22px "Helvetica Neue",Arial,sans-serif';
  c.fillText('2026-10  REV.A',W*0.055,H*0.86);
  /* 板邊白框 */
  c.strokeStyle='rgba(245,250,240,.55)';c.lineWidth=4;
  c.strokeRect(W*0.02,H*0.03,W*0.96,H*0.94);
  var t=new THREE.CanvasTexture(cv);t.anisotropy=8;t.encoding=THREE.sRGBEncoding;
  return t;
}
function battTex(){
  var cv=document.createElement('canvas');cv.width=512;cv.height=512;
  var c=cv.getContext('2d');
  c.fillStyle='#dfe5e9';c.fillRect(0,0,512,512);
  var g=c.createLinearGradient(0,0,512,0);
  g.addColorStop(0,'rgba(0,0,0,.10)');g.addColorStop(.35,'rgba(255,255,255,.22)');
  g.addColorStop(.7,'rgba(0,0,0,.06)');g.addColorStop(1,'rgba(0,0,0,.13)');
  c.fillStyle=g;c.fillRect(0,0,512,512);
  c.fillStyle='#26303a';
  c.font='bold 46px "Helvetica Neue",Arial,sans-serif';
  c.fillText('Li-Po  500mAh',28,120);
  c.font='30px "Helvetica Neue",Arial,sans-serif';
  c.fillText('3.7V  \u00b7  1.85Wh',28,172);
  c.fillText('JIALAN-1  \u00b7  PCM',28,214);
  c.strokeStyle='#c22a1c';c.lineWidth=5;
  c.strokeRect(20,254,140,64);
  c.fillStyle='#c22a1c';c.font='bold 34px Arial';c.fillText('+',42,302);
  c.strokeStyle='#26303a';c.strokeRect(300,254,140,64);
  c.fillStyle='#26303a';c.fillText('\u2013',322,302);
  c.font='22px "Helvetica Neue",Arial,sans-serif';c.fillStyle='#5a6672';
  c.fillText('DO NOT PUNCTURE / 2026-10',28,420);
  var t=new THREE.CanvasTexture(cv);t.anisotropy=4;t.encoding=THREE.sRGBEncoding;
  return t;
}
var BTEX=battTex();

/* ═══════════════ 型號資料 ═══════════════ */
/* A：63 × 39 × 15（上蓋 6.8 / 下蓋 8.2 / 壁厚 1.8 / R7）
   B：56 × 44 × 17.8（背蓋 7.2 / 中框 6.0 / 螢幕 2.4 / 上蓋玻璃 3.0） */
var VD={
 a:{
  key:'a',label:'嘉蘭一號',tag:'1.47 吋彩色 LCD',size:'63 × 39 × 15 mm',
  W:63,D:39,H:15,cr:7,wall:1.8,
  win:{w:33,h:18,r:3},
  ui:{w:33,h:18},
  parts:[
   {id:'strap',o:1,f:'strap',n:'錶帶（20 mm 織帶）',
    d:'20 × 2.5 mm 織帶（頸圍示意 Ø68）',mt:'尼龍織帶＋側壓快扣',
    u:'穿過機殼兩端 3.0 mm 高的走帶槽；側壓快扣受拉力會脫開，避免貓咪勾到勒傷。',
    ex:[0,-56,20]},
   {id:'back',o:2,f:'back',n:'下蓋／背蓋',
    d:'63.0 × 39.0 × 8.2 mm（內腔 59.4 × 35.4）',mt:'白色 PLA・壁厚 1.8・R7 全圓角',
    u:'容納 500 mAh 電池與震動馬達；底面開 2 × Ø2.4 磁吸充電孔與麥克風進音孔。',
    ex:[18,-34,-12]},
   {id:'batt',o:3,f:'batt',n:'鋰聚合物電池 500 mAh',
    d:'32.0 × 21.0 × 4.5 mm（電池槽）',mt:'鋁塑膜・3.7 V 500 mAh・附保護板',
    u:'續航約 2.5 天（心率 1 Hz＋藍牙廣播）；紅黑線接主板的 BAT 焊盤。',
    ex:[-20,-12,12]},
   {id:'motor',o:4,f:'motor',n:'震動馬達（幣型 ERM）',
    d:'Ø10 × 3.4 mm',mt:'鎳殼＋偏心錘・3 V 驅動',
    u:'行為訓練提醒與「該回家了」震動提示；由 MOSFET 低側開關，佔空比控制強弱。',
    ex:[32,6,18]},
   {id:'pcb',o:5,f:'pcb',n:'主電路板（4 層）',
    d:'58.1 × 34.1 × 1.6 mm',mt:'FR-4 綠板＋ENIG 金焊盤・XIAO ESP32S3 主控',
    u:'上面掛 ESP32-S3（21.0 × 17.8 × 1.2）、INMP441 麥克風（4.72 × 3.76）與 LSM6DS3TR-C。',
    ex:[-16,22,-10]},
   {id:'fpc',o:6,f:'fpc',n:'FPC 軟排線（12 pin）',
    d:'12 pin × 0.2 mm 厚 × 18 mm',mt:'聚亞醯胺（PI）＋補強金手指',
    u:'連接主板與 LCD 模組，負責 SPI 顯示與背光；彎折半徑 ≥ 1 mm 避免斷線。',
    ex:[24,40,12]},
   {id:'mag',o:7,f:'mag',n:'磁吸定位磁鐵 ×2',
    d:'Ø5 × 2 mm（距 28 mm）',mt:'N35 釹鐵硼・鎳銅鎳三層電鍍',
    u:'與充電座的磁鐵互吸，讓 pogo pin 自動對位；拉力約 0.4 kg。',
    ex:[40,-22,-20]},
   {id:'pogo',o:8,f:'pogo',n:'磁吸充電 pogo pin ×2',
    d:'Ø1.5 × 5 mm（孔 Ø2.4・距 14 mm）',mt:'黃銅鍍金・彈簧行程 0.8 mm',
    u:'5 V / 0.5 A 充電接點；防水靠 pin 座 O 環與背蓋超音波熔接。',
    ex:[-40,-24,-18]},
   {id:'mid',o:9,f:'mid',n:'中框（螢幕支架）',
    d:'59.0 × 35.0 × 2.6 mm（配 59.4 × 35.4 內腔）',mt:'黑色 ABS・遮光',
    u:'壓住 LCD 四周避免漏光，同時當 PCB 的定位基準；四角落有 M1.4 自攻柱。',
    ex:[-14,56,-6]},
   {id:'screen',o:10,f:'screen',n:'1.47 吋 IPS 彩色螢幕',
    d:'模組 36.0 × 21.0 × 2.2 mm（可視 33.0 × 18.0）',mt:'172 × 320 IPS・SPI 介面',
    u:'顯示狗臉表情、心率／步數／體溫；平時 30 秒熄屏，靠近才亮。',
    ex:[16,74,8]},
   {id:'lid',o:11,f:'lid',n:'上蓋（螢幕視窗）',
    d:'63.0 × 39.0 × 6.8 mm（視窗 33.0 × 18.0 R3）',mt:'白色 PLA・12 條邊全圓角 R7',
    u:'與下蓋 1.8 mm 止口對接；上方留 Ø1.6 導光孔與 2 × Ø1.0 麥克風孔。',
    ex:[0,96,0]}
  ]
 },
 b:{
  key:'b',label:'嘉蘭二號',tag:'2.4 吋滿版玻璃',size:'56 × 44 × 17.8 mm',
  W:56,D:44,H:17.8,cr:7,wall:1.8,
  win:{w:48.96,h:36.72,r:2.0},
  ui:{w:48.96,h:36.72},
  parts:[
   {id:'strap',o:1,f:'strap',n:'錶帶（20 mm 織帶）',
    d:'20 × 2.5 mm 織帶（頸圍示意 Ø68）',mt:'尼龍織帶＋側壓快扣',
    u:'穿過套框兩側夾帶翼（9 × 26 mm）；帶子止於套框，不經過感測器下方。',
    ex:[0,-58,22]},
   {id:'cradle',o:2,f:'cradle',n:'磁吸套框（固定於頸帶）',
    d:'60.0 × 48.0 × 3.2 mm（開窗 46 × 30）',mt:'PC+ABS 霧黑・4 顆 Ø6.2 磁鐵槽',
    u:'表頭拔下即充電、吸上即配戴；開窗 46 × 30 讓 PPG 與聽診器振膜直接貼皮膚。',
    ex:[14,-36,-10]},
   {id:'back',o:3,f:'back',n:'背蓋（PPG／聽診器）',
    d:'56.0 × 44.0 × 7.2 mm（振膜 Ø28 外凸 5）',mt:'PC+ABS 霧黑・PPG 窗 Ø15',
    u:'貼皮膚面：Ø28 聽診器式振膜收心音／呼吸音，12 孔聲學陣列，兩側雙波長 PPG。',
    ex:[-16,-14,10]},
   {id:'batt',o:4,f:'batt',n:'鋰聚合物電池 500 mAh',
    d:'34.0 × 26.0 × 5.4 mm',mt:'鋁塑膜・3.7 V 500 mAh・附保護板',
    u:'放在背蓋腔體內、主板正下方，重心貼皮膚，跑動時晃動最小。',
    ex:[22,4,-14]},
   {id:'motor',o:5,f:'motor',n:'震動馬達（幣型 ERM）',
    d:'Ø10 × 3.4 mm',mt:'鎳殼＋偏心錘・3 V 驅動',
    u:'藏在中框右側的 Ø10 圓槽，震動經中框傳到整片背蓋，貼皮膚感受更明顯。',
    ex:[-30,18,16]},
   {id:'pcb',o:6,f:'pcb',n:'主電路板（4 層）',
    d:'38.0 × 30.0 × 1.2 mm',mt:'FR-4 綠板＋ENIG 金焊盤・4 層',
    u:'ESP32-S3＋PPG 類比前端＋IMU；天線開窗朝上蓋玻璃方向，避開皮膚與電池。',
    ex:[24,34,-8]},
   {id:'fpc',o:7,f:'fpc',n:'FPC 軟排線（12 pin）',
    d:'12 pin × 0.5 mm 厚 × 14 mm',mt:'聚亞醯胺（PI）＋補強金手指',
    u:'主板到 2.4 吋螢幕的 MIPI／SPI 排線；從主板左側翻上中框，避開電池。',
    ex:[-26,50,14]},
   {id:'mag',o:8,f:'mag',n:'磁吸定位磁鐵 ×4',
    d:'Ø6 × 2 mm（距 44 × 36 mm）',mt:'N35 釹鐵硼・鎳銅鎳三層電鍍',
    u:'四角互吸，套框與表頭只有一個裝法；拔起時有明確「咔」的回饋。',
    ex:[38,-26,-18]},
   {id:'pogo',o:9,f:'pogo',n:'磁吸充電 pogo pin ×2',
    d:'Ø1.5 × 5 mm（孔 Ø2.4・距 14 mm）',mt:'黃銅鍍金・彈簧行程 0.8 mm',
    u:'與套框上的簧片接觸充電；IPX6 靠 pin 座 O 環與背蓋熔接。',
    ex:[-38,-28,-16]},
   {id:'mid',o:10,f:'mid',n:'中框（收音／揚聲開孔）',
    d:'56.0 × 44.0 × 6.0 mm',mt:'PC+ABS 霧黑・揚聲 Ø28 腔體',
    u:'撐住螢幕與主板，底面留 Ø28 揚聲腔與 Ø1 收音孔；同時當電池的擋牆。',
    ex:[-14,66,-4]},
   {id:'screen',o:11,f:'screen',n:'2.4 吋螢幕模組',
    d:'52.0 × 40.0 × 2.4 mm（可視 48.96 × 36.72）',mt:'240 × 320 IPS・MIPI',
    u:'滿版玻璃下幾乎無邊框；顯示狗臉表情與三項生理數據。',
    ex:[16,80,6]},
   {id:'lid',o:12,f:'lid',n:'上蓋（滿版黑玻璃）',
    d:'56.0 × 44.0 × 3.0 mm（可視 48.96 × 36.72）',mt:'康寧玻璃＋AF 鍍膜・R7 圓角',
    u:'2.5D 邊緣、與機身齊平；玻璃開窗 48.96 × 36.72 讓螢幕亮度幾乎不打折。',
    ex:[0,100,0]}
  ]
 }
};

/* ═══════════════ 零件建構（絕對座標，原點＝機身中心） ═══════════════ */
var V=null;

/* 上蓋：A＝白殼（側壁＋頂板開窗）；B＝滿版黑玻璃（開窗） */
function bLid(){
  var g=new THREE.Group(),W=V.W,D=V.D;
  if(V.key==='a'){
    var out=rrShape(W,D,7);out.holes.push(rrPath(W-3.6,D-3.6,5.2));
    var wa=extY(out,5.2,22);wa.translate(0,0.7,0);g.add(mesh(wa,M.shell));
    var tp=mesh(hframe(W,D,1.6,V.cr,V.win.w,V.win.h,V.win.r),M.shell);
    tp.position.y=6.7;g.add(tp);
    /* 止口（與下蓋對接的 1.8 mm 唇邊） */
    var lip=mesh(hframe(W-0.4,D-0.4,1.2,6.8,W-3.6,D-3.6,5.2),M.shell2);
    lip.position.y=1.3;g.add(lip);
    /* 導光孔＋麥克風孔（長在頂板上） */
    var led=cylY(0.8,0.8,1.7,M.emitM,16);led.position.set(16,6.75,-12);g.add(led);
    [-0.7,0.7].forEach(function(dx){
      var h=cylY(0.5,0.5,1.7,M.ink,14);h.position.set(dx,6.75,12.5);g.add(h);});
  }else{
    var gl=mesh(hframe(W,D,3.0,V.cr,V.win.w,V.win.h,V.win.r),M.glassBig);
    gl.position.y=7.4;g.add(gl);
    /* 玻璃下緣的黑色遮光框，避免從側面看到玻璃邊緣透光 */
    var sk=mesh(hframe(W-0.6,D-0.6,0.6,6.6,V.win.w,V.win.h,V.win.r),M.ink);
    sk.position.y=5.6;g.add(sk);
  }
  return g;
}

/* 螢幕模組（含 CanvasTexture UI 面） */
function bScreen(){
  var g=new THREE.Group();
  if(V.key==='a'){
    var body=box(36,2.2,21,M.lcdBody);body.position.y=4.5;g.add(body);
    var ui=new THREE.Mesh(new THREE.PlaneGeometry(34.6,19.6),uiMat());
    ui.rotation.x=-Math.PI/2;ui.position.y=5.74;g.add(ui);
    var tail=box(9,0.16,7,M.fpc);tail.position.set(0,3.42,-11.5);g.add(tail);
    var conn=box(11,0.5,3.2,M.gold);conn.position.set(0,3.5,-15.2);g.add(conn);
  }else{
    var body2=box(52,2.4,40,M.lcdBody);body2.position.y=4.4;g.add(body2);
    var ui2=new THREE.Mesh(new THREE.PlaneGeometry(50.4,38.2),uiMat());
    ui2.rotation.x=-Math.PI/2;ui2.position.y=5.74;g.add(ui2);
    var tail2=box(14,0.5,6,M.fpc);tail2.position.set(-14,3.2,-22);g.add(tail2);
    /* 驅動 IC 與背光框 */
    var drv=box(16,0.5,2.4,M.ink);drv.position.set(0,3.15,19.2);g.add(drv);
  }
  return g;
}

/* 中框 */
function bMid(){
  var g=new THREE.Group();
  if(V.key==='a'){
    var fr=mesh(hframe(59.0,35.0,2.6,5.0,37.0,22.0,3.4),M.frame);
    fr.position.y=4.1;g.add(fr);
    [[-27,-14.5],[27,-14.5],[-27,14.5],[27,14.5]].forEach(function(a){
      var b=cylY(1.5,1.5,3.2,M.frame,12);b.position.set(a[0],3.9,a[1]);g.add(b);
    });
  }else{
    var out=rrShape(V.W,V.D,V.cr);out.holes.push(rrPath(46,34,4));
    var ri=extY(out,6.0,22);ri.translate(0,-1.7,0);g.add(mesh(ri,M.frame));
    /* 螢幕座（內縮 1.1 mm 的肩部） */
    var sh=mesh(hframe(52.4,40.4,1.1,5.0,46,34,4),M.frame);
    sh.position.y=3.75;g.add(sh);
    /* 揚聲腔 Ø28 */
    var spk=disc(13.6,0.8,M.inkSoft,36);spk.position.set(-3,1.3,-13.5);g.add(spk);
    for(var i=0;i<12;i++){
      var a=i*Math.PI/6;
      var h=cylY(1.0,1.0,1.4,M.ink,12);
      h.position.set(-3+Math.cos(a)*9.2,1.2,-13.5+Math.sin(a)*9.2);g.add(h);
    }
    /* 收音孔 */
    var mic=cylY(0.8,0.8,1.4,M.ink,12);mic.position.set(18,1.2,14);g.add(mic);
  }
  return g;
}

/* 主 PCB（綠板＋金焊盤＋主要 IC） */
function bPcb(){
  var g=new THREE.Group();
  var W=(V.key==='a')?58.1:38.0, D=(V.key==='a')?34.1:30.0, T=(V.key==='a')?1.6:1.2;
  var Y=(V.key==='a')?0.8:-0.9;
  var tx=pcbTex(W,D);
  var side=mat({color:0x17512d,roughness:.62,metalness:.05});
  var top=mat({color:0xffffff,roughness:.52,metalness:.08,map:tx});
  top.envMapIntensity=0.18;
  var mats=[side,side,top,side,side,side];
  var board=new THREE.Mesh(new THREE.BoxGeometry(W,T,D),mats);
  board.castShadow=true;board.receiveShadow=true;board.position.y=Y;g.add(board);

  var ty=Y+T/2;   /* 頂面 */
  /* XIAO ESP32S3 21.0 × 17.8 × 1.2 */
  var xw=21.0, xd=17.8;
  var xiao=box(xw,1.2,xd,M.ink);xiao.position.set(W*0.12,ty+0.6,0);g.add(xiao);
  var shield=box(xw-3.2,0.35,xd-3.6,M.aluDark);shield.position.set(W*0.12,ty+1.24,0);g.add(shield);
  var usb=box(7.2,2.6,3.2,M.steel);usb.position.set(W*0.12+xw/2+1.4,ty+0.4,0);g.add(usb);
  var usbIn=box(5.4,1.0,2.4,M.ink);usbIn.position.set(W*0.12+xw/2+1.6,ty+1.0,0);g.add(usbIn);
  /* 排針 */
  var hdr=box(2.2,0.9,xd-2,M.gold2);hdr.position.set(W*0.12-xw/2+0.4,ty+0.5,0);g.add(hdr);

  /* INMP441 4.72 × 3.76 × 1.0 */
  var m1=box(4.72,1.0,3.76,M.ink);m1.position.set(-W*0.30,ty+0.5,D*0.24);g.add(m1);
  var m1p=cylY(0.45,0.45,0.3,M.ink,10);m1p.position.set(-W*0.30,ty+1.05,D*0.24);g.add(m1p);
  /* LSM6DS3TR-C 2.5 × 3.0 × 0.83 */
  var m2=box(3.0,0.83,2.5,M.ink);m2.position.set(-W*0.30,ty+0.42,-D*0.10);g.add(m2);
  /* 電源管理 IC */
  var m3=box(5.0,0.9,5.0,M.ink);m3.position.set(W*0.30,ty+0.45,-D*0.24);g.add(m3);
  var m4=box(3.2,0.7,3.2,M.inkSoft);m4.position.set(W*0.05,ty+0.35,-D*0.30);g.add(m4);
  /* 電池焊盤 */
  var bp=box(4.0,0.25,3.0,M.gold2);bp.position.set(-W*0.16,ty+0.13,-D*0.36);g.add(bp);
  /* 邊緣金手指（焊盤陣列） */
  for(var i=0;i<9;i++){
    var p=box(1.8,0.22,2.6,M.gold2);
    p.position.set(-W/2+2.5+i*3.2,ty+0.12,D/2-2.2);g.add(p);
  }
  /* 固定孔環 */
  [[-1,-1],[1,-1],[-1,1],[1,1]].forEach(function(s){
    var r=mesh(new THREE.TorusGeometry(1.5,0.45,6,16),M.gold2);
    r.rotation.x=-Math.PI/2;
    r.position.set(s[0]*(W/2-4),ty+0.06,s[1]*(D/2-4));g.add(r);
  });
  return g;
}

/* 電池 */
function bBatt(){
  var g=new THREE.Group();
  var W=(V.key==='a')?31.6:34.0, D=(V.key==='a')?20.6:26.0, T=(V.key==='a')?4.3:5.4;
  var Y=(V.key==='a')?-3.45:-4.30, Z=(V.key==='a')?5.0:0;
  var lab=mat({color:0xffffff,roughness:.62,metalness:.10,map:BTEX});
  lab.envMapIntensity=0.22;
  var matSide=mat({color:0xd8dee3,roughness:.30,metalness:.62});
  var mats=[lab,lab,matSide,matSide,lab,lab];
  var body=new THREE.Mesh(new THREE.BoxGeometry(W,T,D),mats);
  body.castShadow=true;body.receiveShadow=true;body.position.set(0,Y,Z);g.add(body);
  /* 封邊 */
  var edge=box(W+0.5,T*0.9,D+0.5,M.pouch2);edge.position.set(0,Y,Z);edge.visible=false;g.add(edge);
  /* 保護板 */
  var pcm=box(W*0.55,0.8,3.2,M.pcbEdge);
  pcm.position.set(0,Y+T/2+0.4,Z-D/2+1.6);g.add(pcm);
  var ic=box(2.4,0.5,2.0,M.ink);ic.position.set(0,Y+T/2+0.95,Z-D/2+1.6);g.add(ic);
  /* 紅黑線（往主板上方繞） */
  var redPts=[new THREE.Vector3(-3,Y+T/2+0.6,Z-D/2+0.6),
              new THREE.Vector3(-3,Y+T/2+1.6,Z-D/2-1.2),
              new THREE.Vector3(-5,Y+T/2+2.2,Z-D/2-3.0)];
  var blkPts=[new THREE.Vector3(1.6,Y+T/2+0.6,Z-D/2+0.6),
              new THREE.Vector3(1.6,Y+T/2+1.5,Z-D/2-1.4),
              new THREE.Vector3(0.4,Y+T/2+2.0,Z-D/2-3.2)];
  [['r',redPts,M.red],['k',blkPts,M.black]].forEach(function(o){
    var cu=new THREE.CatmullRomCurve3(o[1]);
    var t2=new THREE.Mesh(new THREE.TubeGeometry(cu,24,0.34,8,false),o[2]);
    t2.castShadow=true;g.add(t2);
  });
  return g;
}

/* FPC 軟排線 */
function bFpc(){
  var g=new THREE.Group();
  if(V.key==='a'){
    var v=box(12,3.2,0.2,M.fpc);v.position.set(-20,3.35,-9.6);g.add(v);
    var h=box(12,0.2,7,M.fpc);h.position.set(-20,1.78,-13.6);g.add(h);
    var f1=box(10,0.3,1.6,M.gold2);f1.position.set(-20,1.80,-16.9);g.add(f1);
    var f2=box(10,0.3,1.6,M.gold2);f2.position.set(-20,5.06,-9.6);g.add(f2);
    /* 補強板 */
    var st=box(12,0.35,2.2,M.inkSoft);st.position.set(-20,5.25,-9.6);g.add(st);
  }else{
    var v2=box(14,5.0,0.5,M.fpc);v2.position.set(-14,1.1,-18.0);g.add(v2);
    var h2=box(14,0.5,6.5,M.fpc);h2.position.set(-14,-0.05,-14.5);g.add(h2);
    var f3=box(12,0.35,1.8,M.gold2);f3.position.set(-14,-0.05,-11.4);g.add(f3);
    var f4=box(12,0.35,1.8,M.gold2);f4.position.set(-14,3.62,-18.0);g.add(f4);
    var st2=box(14,0.4,2.4,M.inkSoft);st2.position.set(-14,3.75,-18.0);g.add(st2);
  }
  return g;
}

/* 震動馬達（幣型 ERM） */
function bMotor(){
  var g=new THREE.Group();
  var P=(V.key==='a')?[-22,-3.6,12.5]:[19,1.4,13.0];
  var can=cylY(5,5,3.4,M.motor,32);can.position.set(P[0],P[1],P[2]);g.add(can);
  var top=cylY(4.6,4.6,0.3,M.aluDark,32);top.position.set(P[0],P[1]+1.82,P[2]);g.add(top);
  /* 偏心錘 */
  var wt=box(7.4,0.8,3.4,M.inkSoft);wt.position.set(P[0]+1.8,P[1]+2.1,P[2]);g.add(wt);
  var wt2=cylY(1.9,1.9,0.8,M.inkSoft,20);wt2.position.set(P[0]+3.2,P[1]+2.1,P[2]);g.add(wt2);
  /* 引線 */
  [[-2.6,M.red],[2.6,M.black]].forEach(function(o){
    var w=box(0.6,0.6,4.2,o[1]);
    w.position.set(P[0]+o[0],P[1]+0.2,P[2]-6.0);g.add(w);
  });
  var pad=box(4.4,0.4,2.2,M.pcbEdge);pad.position.set(P[0],P[1]-1.85,P[2]);g.add(pad);
  return g;
}

/* 磁鐵 */
function bMag(){
  var g=new THREE.Group();
  var list,r,h,Y;
  if(V.key==='a'){
    list=[[-14,13],[14,13]];r=2.5;h=2.0;Y=-6.45;
  }else{
    list=[[-22,-18],[22,-18],[-22,18],[22,18]];r=3.0;h=2.0;Y=-7.9;
  }
  list.forEach(function(p){
    var cu=cylY(r,r,h,M.nickel,32);cu.position.set(p[0],Y,p[1]);g.add(cu);
    var ch=mesh(new THREE.TorusGeometry(r*0.86,0.16,6,26),M.alu);
    ch.rotation.x=-Math.PI/2;ch.position.set(p[0],Y+h/2, p[1]);g.add(ch);
    var ch2=mesh(new THREE.TorusGeometry(r*0.86,0.16,6,26),M.alu);
    ch2.rotation.x=-Math.PI/2;ch2.position.set(p[0],Y-h/2,p[1]);g.add(ch2);
  });
  return g;
}

/* pogo pin */
function bPogo(){
  var g=new THREE.Group();
  var Y=(V.key==='a')?-6.2:-8.0;
  [-7,7].forEach(function(x){
    var barrel=cylY(0.75,0.75,3.4,M.gold,20);barrel.position.set(x,Y+1.0,13);g.add(barrel);
    var spring=cylY(0.62,0.62,1.2,M.aluDark,16);spring.position.set(x,Y-0.9,13);g.add(spring);
    var tip=mesh(new THREE.SphereGeometry(0.75,16,12),M.gold2);
    tip.scale.set(1,0.72,1);tip.position.set(x,Y-1.75,13);g.add(tip);
    var base=cylY(1.35,1.35,0.8,M.rubber,20);base.position.set(x,Y+2.6,13);g.add(base);
  });
  return g;
}

/* 背蓋（A：白殼底面＋充電孔；B：PPG／聽診器面） */
function bBack(){
  var g=new THREE.Group(),W=V.W,D=V.D;
  if(V.key==='a'){
    var fl=mesh(hplate(W,D,1.8,V.cr,22),M.shell);fl.position.y=-6.6;g.add(fl);
    var out=rrShape(W,D,V.cr);out.holes.push(rrPath(59.4,35.4,5.0));
    var wa=extY(out,6.4,22);wa.translate(0,-5.7,0);g.add(mesh(wa,M.shell));
    /* 內側電池擋牆 */
    [[0,-15.5],[0,15.5]].forEach(function(p){
      var b=box(34,3.2,1.6,M.shell2);b.position.set(p[0],-4.2,p[1]);g.add(b);
    });
    [-25.5,25.5].forEach(function(x){
      var b=box(1.6,3.2,26,M.shell2);b.position.set(x,-4.2,0);g.add(b);
    });
    /* 磁吸充電孔 Ø2.4 ×2（距 14） */
    [-7,7].forEach(function(x){
      var hole=cylY(1.2,1.2,0.9,M.black,18);hole.position.set(x,-6.55,13);g.add(hole);
      var rim=mesh(new THREE.TorusGeometry(1.5,0.22,8,20),M.gold);
      rim.rotation.x=-Math.PI/2;rim.position.set(x,-5.72,13);g.add(rim);
    });
    /* 麥克風進音孔 2 × Ø1.0（孔距 1.4） */
    [-0.7,0.7].forEach(function(x){
      var h=cylY(0.5,0.5,0.9,M.black,12);h.position.set(x,-6.55,-14.5);g.add(h);
    });
    /* 走帶槽（22 × 3.0）兩端 */
    [-1,1].forEach(function(s){
      var slot=box(2.4,3.0,22,M.inkSoft);
      slot.position.set(s*(W/2-0.8),-3.2,0);g.add(slot);
    });
    /* 磁鐵槽 */
    [-14,14].forEach(function(x){
      var p=cylY(3.1,3.1,0.5,M.inkSoft,24);p.position.set(x,-5.75,13);g.add(p);
    });
  }else{
    var fl2=mesh(hplate(W,D,1.8,V.cr,22),M.frame);fl2.position.y=-8.0;g.add(fl2);
    var out2=rrShape(W,D,V.cr);out2.holes.push(rrPath(52.4,40.4,5));
    var wa2=extY(out2,5.4,22);wa2.translate(0,-7.1,0);g.add(mesh(wa2,M.frame));
    /* 聽診器式振膜 Ø28 × 5（外凸） */
    var bell=cylY(14,13.2,5.0,M.steel,56);bell.position.y=-11.4;g.add(bell);
    var bface=cylY(13.6,13.6,0.8,M.nickel,56);bface.position.y=-13.9;g.add(bface);
    var brim=mesh(new THREE.TorusGeometry(14.6,0.7,10,56),M.steel);
    brim.rotation.x=-Math.PI/2;brim.position.y=-9.0;g.add(brim);
    var bgroove=mesh(new THREE.TorusGeometry(9.4,0.3,8,48),M.aluDark);
    bgroove.rotation.x=-Math.PI/2;bgroove.position.y=-14.2;g.add(bgroove);
    /* 12 孔聲學陣列 */
    for(var i=0;i<12;i++){
      var a=i*Math.PI/6;
      var h2=cylY(0.95,0.95,1.0,M.black,12);
      h2.position.set(Math.cos(a)*12.2,-14.15,Math.sin(a)*12.2);g.add(h2);
    }
    /* 雙波長 PPG（綠 530 / 紅外 660・940） */
    [-19.5,19.5].forEach(function(x){
      for(var k=-1;k<=1;k+=2){
        var glassDisc=cylY(2.9,2.9,0.9,M.glass,28);
        glassDisc.position.set(x,-8.55,k*7.0);g.add(glassDisc);
        var em=cylY(1.7,1.7,0.5,M.emitG,24);
        em.position.set(x,-8.95,k*7.0);g.add(em);
      }
    });
    /* 磁鐵槽 */
    [[-22,-18],[22,-18],[-22,18],[22,18]].forEach(function(p){
      var pk=cylY(3.6,3.6,0.6,M.inkSoft,26);
      pk.position.set(p[0],-8.35,p[1]);g.add(pk);
    });
    /* pogo 孔 Ø2.4 ×2 */
    [-7,7].forEach(function(x){
      var hole2=cylY(1.2,1.2,1.0,M.black,18);hole2.position.set(x,-8.4,13);g.add(hole2);
      var rim2=mesh(new THREE.TorusGeometry(1.5,0.22,8,20),M.gold);
      rim2.rotation.x=-Math.PI/2;rim2.position.set(x,-7.05,13);g.add(rim2);
    });
  }
  return g;
}

/* 磁吸套框（僅 B 版） */
function bCradle(){
  var g=new THREE.Group();
  var frame=mesh(hframe(60,48,3.2,6.0,46,30,4.5),M.frame);
  frame.position.y=-10.5;g.add(frame);
  /* 夾帶翼（夾住 20 mm 織帶：上下面各一片，寬度沿 Z） */
  [-1,1].forEach(function(s){
    var o=box(9,1.3,26,M.frame);o.position.set(s*30,-8.25,0);g.add(o);
    var i2=box(9,1.3,26,M.frame);i2.position.set(s*30,-12.75,0);g.add(i2);
    var br=box(2.4,4.6,26,M.frame);br.position.set(s*34.2,-10.5,0);g.add(br);
  });
  /* 4 顆 Ø6.2 磁鐵槽 */
  [[-22,-18],[22,-18],[-22,18],[22,18]].forEach(function(p){
    var pk=cylY(3.5,3.5,0.9,M.inkSoft,26);pk.position.set(p[0],-10.5,p[1]);g.add(pk);
    var mg=cylY(3.0,3.0,0.7,M.nickel,26);mg.position.set(p[0],-10.5,p[1]);g.add(mg);
  });
  /* 定位銷 */
  [14,-16].forEach(function(x){
    var pin=cylY(1.25,1.25,3.0,M.steel,18);pin.position.set(x,-10.5,18);g.add(pin);
  });
  var acc=box(44,0.6,1.2,M.emitM);acc.position.set(0,-9.0,-20.5);g.add(acc);
  return g;
}

/* 錶帶（沿曲線擠出，寬度 20 沿 Z） */
function bStrap(){
  var g=new THREE.Group();
  var pts,cx,cy;
  if(V.key==='a'){
    pts=[[31,-3.2,0],[33.5,-13,0],[27,-27,0],[13,-37,0],[0,-40,0],
         [-13,-37,0],[-27,-27,0],[-33.5,-13,0],[-31,-3.2,0]];
    cx=-27;cy=-27;
  }else{
    pts=[[31,-10.2,0],[34,-20,0],[27,-33,0],[13,-43,0],[0,-46,0],
         [-13,-43,0],[-27,-33,0],[-34,-20,0],[-31,-10.2,0]];
    cx=-27;cy=-33;
  }
  var pv=pts.map(function(p){return new THREE.Vector3(p[0],p[1],p[2]);});
  var band=mesh(ribbon(pv,20,2.5,110),M.strap);
  g.add(band);
  /* 車縫線 */
  [-1,1].forEach(function(s){
    var sp=pv.map(function(p){return new THREE.Vector3(p.x,p.y,p.z+s*8.4);});
    var cu=new THREE.CatmullRomCurve3(sp);
    var st=new THREE.Mesh(new THREE.TubeGeometry(cu,90,0.24,6,false),M.strap2);
    g.add(st);
  });
  /* 側壓快扣（放在帶子正後方，切線沿 X 才好對齊） */
  var bky=(V.key==='a')?-40:-46;
  var bk=box(15,6.4,26,M.buckle);bk.position.set(0,bky,0);g.add(bk);
  var bk2=box(17,3.4,28,M.buckle);bk2.position.set(0,bky+4.0,0);g.add(bk2);
  var bk3=box(3.6,6.8,6.0,M.nickel);bk3.position.set(0,bky-0.6,0);g.add(bk3);
  var bk4=box(2.0,6.4,26,M.buckle);bk4.position.set(-10.5,bky,0);g.add(bk4);
  /* 帶環（兩道車縫壓條） */
  [-6,6].forEach(function(dx){
    var lp=box(2.6,4.2,22,M.strap2);lp.position.set(dx,bky,0);g.add(lp);
  });
  return g;
}

var BUILD={lid:bLid,screen:bScreen,mid:bMid,pcb:bPcb,batt:bBatt,fpc:bFpc,
  motor:bMotor,mag:bMag,pogo:bPogo,back:bBack,strap:bStrap,cradle:bCradle};

/* ═══════════════ 建構／切換型號 ═══════════════ */
var model=new THREE.Group();scene.add(model);
var PARTS=[],LBL=[];
window.PARTS=PARTS;

/* 爆炸虛線軸 */
var axisMat=new THREE.LineDashedMaterial({color:0x2f8fff,dashSize:4,gapSize:3,
  transparent:true,opacity:.9});
var axisGeo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,-40,0),
  new THREE.Vector3(0,140,0)]);
var axisLine=new THREE.Line(axisGeo,axisMat);
axisLine.computeLineDistances();axisLine.visible=false;scene.add(axisLine);

/* 尺寸標註 */
var dimGroup=new THREE.Group();dimGroup.visible=false;scene.add(dimGroup);
function sprLabel(text,size,fg,bg){
  var fs=64,pad=18;
  var c=document.createElement('canvas').getContext('2d');
  var ff='bold '+fs+'px "PingFang TC",sans-serif';
  c.font=ff;
  var w=Math.ceil(c.measureText(text).width)+pad*2,h=fs+pad*2;
  var cv=document.createElement('canvas');cv.width=w;cv.height=h;
  c=cv.getContext('2d');c.font=ff;
  var r=18;c.fillStyle=bg||'#4be3a8';c.beginPath();
  c.moveTo(r,0);c.lineTo(w-r,0);c.quadraticCurveTo(w,0,w,r);c.lineTo(w,h-r);
  c.quadraticCurveTo(w,h,w-r,h);c.lineTo(r,h);c.quadraticCurveTo(0,h,0,h-r);
  c.lineTo(0,r);c.quadraticCurveTo(0,0,r,0);c.closePath();c.fill();
  c.fillStyle=fg||'#06231b';c.textBaseline='middle';c.fillText(text,pad,h/2+2);
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
function addDim(a,b,label,size){
  var col=0x4be3a8;
  dimGroup.add(rod(a,b,0.30,col));
  var dir=new THREE.Vector3().subVectors(b,a).normalize();
  var perp=new THREE.Vector3(0,1,0);
  if(Math.abs(dir.dot(perp))>0.9)perp.set(1,0,0);
  [1,-1].forEach(function(sg){
    [a,b].forEach(function(p){
      var t1=p.clone().add(new THREE.Vector3().crossVectors(dir,perp).multiplyScalar(2.2*sg));
      var t2=p.clone().add(new THREE.Vector3().crossVectors(dir,perp).multiplyScalar(-2.2*sg));
      dimGroup.add(rod(t1,t2,0.30,col));
    });
  });
  var lb=sprLabel(label,size||3.4);
  lb.position.copy(a).add(b).multiplyScalar(.5);
  dimGroup.add(lb);
}
function buildDims(){
  while(dimGroup.children.length){dimGroup.remove(dimGroup.children[0]);}
  var W=V.W,D=V.D,H=V.H,sz=(V.key==='a')?3.2:3.0;
  var yTop=H/2+7, zOut=-D/2-9, xOut=W/2+10;
  var c=0x4be3a8;
  /* 寬（X） */
  addDim(new THREE.Vector3(-W/2,yTop,zOut),new THREE.Vector3(W/2,yTop,zOut),
    '寬 '+W.toFixed(1)+' mm',sz);
  [-W/2,W/2].forEach(function(x){
    dimGroup.add(rod(new THREE.Vector3(x,H/2,zOut+2),new THREE.Vector3(x,yTop,zOut),0.16,c));
  });
  /* 深（Z） */
  addDim(new THREE.Vector3(xOut,yTop,-D/2),new THREE.Vector3(xOut,yTop,D/2),
    '深 '+D.toFixed(1)+' mm',sz);
  [-D/2,D/2].forEach(function(z){
    dimGroup.add(rod(new THREE.Vector3(xOut-2,H/2,z),new THREE.Vector3(xOut,yTop,z),0.16,c));
  });
  /* 厚（Y） */
  addDim(new THREE.Vector3(xOut,-H/2,zOut),new THREE.Vector3(xOut,H/2,zOut),
    '厚 '+H.toFixed(1)+' mm',sz);
  [-H/2,H/2].forEach(function(y){
    dimGroup.add(rod(new THREE.Vector3(xOut-2,y,zOut+2),new THREE.Vector3(xOut,y,zOut),0.16,c));
  });
}

function buildVariant(key,keepMode){
  V=VD[key]||VD.a;
  /* 清舊 */
  for(var i=model.children.length-1;i>=0;i--)model.remove(model.children[i]);
  PARTS.length=0;
  LBL.forEach(function(L){
    if(L.el.parentNode)L.el.parentNode.removeChild(L.el);
    if(L.line.parentNode)L.line.parentNode.removeChild(L.line);
    if(L.dot.parentNode)L.dot.parentNode.removeChild(L.dot);
  });
  LBL.length=0;
  hideInfo();clearOutline();
  buildDims();

  V.parts.forEach(function(d){
    var g=BUILD[d.f]();
    g.userData.info={t:d.n,rows:[['尺寸',d.d],['材質',d.mt],['用途',d.u]]};
    g.position.set(0,0,0);
    model.add(g);
    var rec={id:d.id,def:d,g:g,num:d.o,ex:new THREE.Vector3().fromArray(d.ex)};
    g.userData.rec=rec;PARTS.push(rec);
  });
  buildLabels();
  /* 軸長度 */
  var bb=new THREE.Box3().setFromObject(model);
  axisGeo.setFromPoints([new THREE.Vector3(0,bb.min.y-30,0),
    new THREE.Vector3(0,bb.max.y+150,0)]);
  axisLine.computeLineDistances();
  /* HUD */
  document.getElementById('hudtag').innerHTML='<b>'+V.label+'</b> ｜ '+V.size;
  var bs=document.querySelectorAll('#vsw button');
  for(var j=0;j<bs.length;j++)bs[j].className=(bs[j].getAttribute('data-v')===key)?'on':'';
  applyExplode();
  window.__pp.variant=key;
  window.__pp.win={w:V.win.w,h:V.win.h};
  if(keepMode!==false)setMode(MODE,true);
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
  camera.near=Math.max(pr/150,0.05);
  camera.far=pr*40;
  camera.updateProjectionMatrix();
  controls.target.copy(c);
  camera.position.copy(c).addScaledVector(d,dist);
  camera.lookAt(c);
  controls.update();
  return b;
}
var DIRS={
  asm:new THREE.Vector3(0.48,0.62,0.58),
  exploded:new THREE.Vector3(0.40,0.46,0.79),
  dims:new THREE.Vector3(0.52,0.62,0.59)
};
function padOf(mode){
  var narrow=window.innerWidth<760;
  if(mode==='exploded')return narrow?1.95:1.42;
  if(mode==='dims')return narrow?1.55:1.26;
  return narrow?1.26:1.16;
}
var userMoved=false;
controls.addEventListener('start',function(){userMoved=true;});

/* ═══════════════ 模式 ═══════════════ */
var MODE='asm',EX=0,EXT=0;
var exr=document.getElementById('exr'),exv=document.getElementById('exv');
var lblLayer=document.getElementById('lblLayer'),leadSvg=document.getElementById('lead');

function setMode(m,instant){
  MODE=m;
  var bs=document.querySelectorAll('#bar button[data-mode]');
  for(var i=0;i<bs.length;i++)bs[i].className=(bs[i].getAttribute('data-mode')===m)?'on':'';
  axisLine.visible=(m==='exploded');
  lblLayer.style.display=(m==='exploded')?'block':'none';
  dimGroup.visible=(m==='dims');
  /* 尺寸視圖只看機身：錶帶收起，避免尺寸線被大環拉遠 */
  PARTS.forEach(function(p){if(p.id==='strap')p.g.visible=(m!=='dims');});
  if(m==='exploded'){EXT=(exr.value|0)/100;if(EXT<0.35){EXT=1;exr.value=100;}}
  else{EXT=0;exr.value=0;}
  exv.textContent=Math.round(EXT*100)+'%';
  if(instant)EX=EXT;
  applyExplode();
  userMoved=false;
  fitBox(DIRS[m]||DIRS.asm,padOf(m));
  updateLabels(true);
  hideInfo();
  syncSlider();
  window.__pp.mode=m;
}
var EXK=0.92;
function applyExplode(){
  var t=EX*EXK;
  for(var i=0;i<PARTS.length;i++){
    PARTS[i].g.position.copy(PARTS[i].ex).multiplyScalar(t);
  }
  model.updateMatrixWorld(true);
}

/* ═══════════════ 標籤 ═══════════════ */
function buildLabels(){
  lblLayer.appendChild(leadSvg);
  var order=PARTS.slice().sort(function(a,b){
    var ia=a.def.o||99,ib=b.def.o||99;
    if(ia!==ib)return ia-ib;
    return a.id<b.id?-1:1;
  });
  order.forEach(function(p,i){
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
    lblLayer.appendChild(el);
    var line=document.createElementNS('http://www.w3.org/2000/svg','polyline');
    var dot=document.createElementNS('http://www.w3.org/2000/svg','circle');
    dot.setAttribute('r','2.6');
    leadSvg.appendChild(line);leadSvg.appendChild(dot);
    LBL.push({p:p,el:el,line:line,dot:dot,side:'L',ty:0,ay:0});
  });
}
function projPoint(v){
  var q=v.clone().project(camera);
  return {x:(q.x*.5+.5)*window.innerWidth,y:(-q.y*.5+.5)*window.innerHeight,z:q.z};
}
function updateLabels(force){
  if(MODE!=='exploded')return;
  var W=window.innerWidth,H=window.innerHeight,cx=W/2;
  var narrow=W<760;
  var pad=64,padB=narrow?128:64;
  leadSvg.setAttribute('width',W);leadSvg.setAttribute('height',H);
  LBL.forEach(function(L){
    var bb=new THREE.Box3().setFromObject(L.p.g);
    var ctr=bb.getCenter(new THREE.Vector3());
    var pr=projPoint(ctr);
    L.ax=pr.x;L.ay=pr.y;
    L.side=(pr.x<cx)?'L':'R';
    L.el.style.display='flex';
  });
  var colW=narrow?Math.max(118,Math.min(166,W*0.40)):Math.min(310,Math.max(140,W*0.24));
  ['L','R'].forEach(function(side){
    var arr=LBL.filter(function(L){return L.side===side;})
      .sort(function(a,b){return a.ay-b.ay;});
    var n=arr.length,avail=H-pad-padB,gap=54;
    /* 標籤本身高度可能超過 54px（手機兩行）→ gap 取 max(54, 最高的標籤+4) */
    arr.forEach(function(L){var hh=L.el.offsetHeight||38;if(hh+4>gap)gap=hh+4;});
    if(n>1&&(n-1)*gap>avail)gap=avail/(n-1);
    for(var i=0;i<n;i++){
      arr[i].ty=arr[i].ay;
      if(i>0&&arr[i].ty-arr[i-1].ty<gap)arr[i].ty=arr[i-1].ty+gap;
    }
    if(n){arr[n-1].ty=Math.min(arr[n-1].ty,H-padB);}
    for(var k=n-2;k>=0;k--){
      if(arr[k].ty>arr[k+1].ty-gap)arr[k].ty=arr[k+1].ty-gap;
    }
    if(n&&arr[0].ty<pad){
      var d=pad-arr[0].ty;
      for(var j=0;j<n;j++)arr[j].ty+=d;
    }
    arr.forEach(function(L){
      L.el.className='lbl '+(side==='L'?'left':'right');
      L.el.style.width=colW+'px';
      L.el.style.top=Math.round(L.ty)+'px';
      var edgeX=(side==='L')?(colW-10):(W-colW+10);
      L.line.setAttribute('points',(edgeX+(side==='L'?4:-4)).toFixed(0)+','+Math.round(L.ty)+' '+
        (edgeX+(side==='L'?26:-26)).toFixed(0)+','+Math.round(L.ty)+' '+
        (L.ax+(side==='L'?9:-9)).toFixed(0)+','+L.ay.toFixed(0));
      L.dot.setAttribute('cx',L.ax.toFixed(1));L.dot.setAttribute('cy',L.ay.toFixed(1));
    });
  });
}

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
  hh.textContent='點空白處可取消選取';
  el.appendChild(hh);
  el.style.display='flex';
  clearOutline();
  var bb=new THREE.Box3().setFromObject(rec.g);
  var size=bb.getSize(new THREE.Vector3()),c=bb.getCenter(new THREE.Vector3());
  outline=new THREE.LineSegments(new THREE.EdgesGeometry(
    new THREE.BoxGeometry(size.x*1.05+1.2,size.y*1.05+1.2,size.z*1.05+1.2)),
    new THREE.LineBasicMaterial({color:0x4be3a8,transparent:true,opacity:.95,depthTest:false}));
  outline.position.copy(c);outline.renderOrder=997;scene.add(outline);
}
function hideInfo(){document.getElementById('finfo').style.display='none';clearOutline();}
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
var bmodes=document.querySelectorAll('#bar button[data-mode]');
for(var i=0;i<bmodes.length;i++){
  bmodes[i].onclick=function(){setMode(this.getAttribute('data-mode'));};
}
document.getElementById('breset').onclick=function(){
  userMoved=false;
  fitBox(DIRS[MODE],padOf(MODE));
  updateLabels(true);
};
var vbs=document.querySelectorAll('#vsw button');
for(var vi=0;vi<vbs.length;vi++){
  vbs[vi].onclick=function(){
    var k=this.getAttribute('data-v');
    if(k===V.key)return;
    buildVariant(k,true);
    updateLabels(true);
  };
}
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
  updateLabels(true);
});

/* ═══════════════ 主迴圈 ═══════════════ */
var spin=SHOT?0:0.05;
var last=performance.now(),frame=0;
function tick(){
  requestAnimationFrame(tick);
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
  controls.update();
  if(MODE==='exploded')updateLabels();
  if(outline){outline.material.opacity=0.70+0.28*Math.sin(now*0.004);}
  renderer.render(scene,camera);
  frame++;
  window.__frames=frame;
}

/* ═══════════════ 啟動 ═══════════════ */
window.__pp={
  mode:'asm',variant:VKEY,win:null,
  get labels(){return document.querySelectorAll('.lbl').length;},
  get leads(){return document.querySelectorAll('#lead polyline').length;},
  get parts(){return PARTS.length;},
  get stripParts(){return PARTS.map(function(p){return p.def.n;});},
  get errors(){return window.__errors;},
  get bbox(){var b=modelBox();var s=b.getSize(new THREE.Vector3());
    return [+s.x.toFixed(2),+s.y.toFixed(2),+s.z.toFixed(2)];},
  get cam(){return camera.position.toArray().map(function(v){return +v.toFixed(1);});},
  get info(){var e=document.getElementById('finfo');return e.style.display!=='none'?e.textContent:'';},
  view:function(v){setMode(v,true);},
  setVariant:function(k){buildVariant(k,true);},
  explode:function(v){EXT=v;EX=v;applyExplode();},
  pick:function(x,y){var r=pickAt(x,y);return r?r.def.n:null;},
  screenPix:function(){
    /* 取螢幕 UI 貼圖的平均亮度，驗證不是空白 */
    var sp=null;
    PARTS.forEach(function(p){if(p.id==='screen')sp=p.g;});
    if(!sp)return null;
    var found=null;
    sp.traverse(function(o){if(o.isMesh&&o.material&&o.material.map&&o.material.emissiveMap)found=o;});
    if(!found)return null;
    var img=found.material.map.image;
    var cv=document.createElement('canvas');cv.width=64;cv.height=64;
    var c=cv.getContext('2d');c.drawImage(img,0,0,64,64);
    var d=c.getImageData(0,0,64,64).data;
    var s=0,mx=0;
    for(var i=0;i<d.length;i+=4){var l=(d[i]+d[i+1]+d[i+2])/3;s+=l;if(l>mx)mx=l;}
    return {avg:+(s/(d.length/4)).toFixed(1),max:mx};
  }
};
buildVariant(VKEY,false);
setMode(VIEW==='exploded'?'exploded':(VIEW==='dims'?'dims':'asm'),true);
tick();
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
    path = os.path.join(outdir, "pawpulse-system.html")
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
