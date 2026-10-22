#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智賢1號（嘉蘭智慧科技）— 單檔 three.js 互動模型頁產生器
輸出：elderchat-system.html（three.js r128 + OrbitControls 內嵌，可離線雙擊）

用法：
  python3 build_elderchat.py <輸出資料夾> [--libs /path/to/libs]
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
<title>智賢1號 ｜ 嘉蘭智慧科技 · 3D 組裝・爆炸・尺寸</title>
<style>
  :root{
    --cream:#f3ecdd; --cream2:#e7dcc4; --wood:#8a5b38; --wood2:#6f4527;
    --lime:#cbf24c; --brass:#c9a227; --ink:#161614; --bg:#0b100e;
    --panel:rgba(18,24,22,.86); --line:rgba(203,242,76,.28);
    --txt:#eae4d4; --dim:#9aa79c;
  }
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{margin:0;height:100%;overflow:hidden;background:var(--bg);color:var(--txt);
    font-family:"PingFang TC","Noto Sans TC","Heiti TC","Microsoft JhengHei",system-ui,sans-serif}
  #app{position:fixed;inset:0}
  canvas{display:block}
  .panel{background:var(--panel);border:1px solid rgba(255,255,255,.09);border-radius:14px;
    backdrop-filter:blur(9px);-webkit-backdrop-filter:blur(9px);box-shadow:0 10px 30px rgba(0,0,0,.42)}

  /* ── 左上標題 ── */
  #hud{position:fixed;left:14px;top:14px;padding:11px 15px;z-index:20;max-width:min(52vw,340px)}
  #hud b{font-size:15px;letter-spacing:.5px;display:block;color:#fff}
  #hud b i{font-style:normal;color:var(--lime)}
  #hud span{font-size:11.5px;color:var(--dim);line-height:1.55;display:block;margin-top:4px}
  #hud .tag{display:inline-block;margin-top:7px;font-size:10.5px;color:var(--lime);
    border:1px solid var(--line);border-radius:999px;padding:2px 8px}

  /* ── 右上資訊卡 ── */
  #finfo{position:fixed;right:14px;top:14px;width:min(330px,44vw);padding:13px 15px 14px;
    display:none;flex-direction:column;gap:7px;z-index:40;border-color:rgba(203,242,76,.35)}
  #finfo h4{margin:0;font-size:15px;color:#fff;display:flex;align-items:center;gap:8px}
  #finfo h4 .n{display:inline-flex;width:22px;height:22px;border-radius:50%;background:var(--lime);
    color:#12160f;font-size:12px;font-weight:800;align-items:center;justify-content:center;flex:0 0 auto}
  #finfo h4 .x{margin-left:auto;cursor:pointer;color:var(--dim);font-size:15px;padding:0 2px}
  #finfo .row{font-size:12px;line-height:1.62;color:#d9d3c2;display:flex;gap:7px}
  #finfo .row u{text-decoration:none;color:var(--dim);flex:0 0 46px}
  #finfo .row b{font-weight:600;color:#fff}
  #finfo .hint{font-size:10.5px;color:var(--dim);border-top:1px solid rgba(255,255,255,.08);padding-top:7px}

  /* ── 零件標籤（爆炸圖） ── */
  #lblLayer{position:fixed;inset:0;pointer-events:none;z-index:15;display:none}
  #lead{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
  #lead polyline{fill:none;stroke:rgba(203,242,76,.55);stroke-width:1;stroke-dasharray:3 3}
  #lead circle{fill:var(--lime)}
  .lbl{position:absolute;transform:translateY(-50%);display:flex;gap:7px;align-items:flex-start;
    font-size:11.5px;line-height:1.32;color:#e9e3d3;pointer-events:none;
    text-shadow:0 1px 3px rgba(0,0,0,.85)}
  .lbl.left{left:0;padding-right:12px;justify-content:flex-end;text-align:right}
  .lbl.left .b{order:2}
  .lbl.right{right:0;padding-left:12px;justify-content:flex-start;text-align:left}
  .lbl .t{max-width:236px}
  .lbl .b{flex:0 0 auto;width:19px;height:19px;border-radius:50%;background:var(--lime);color:#12160f;
    font-size:10.5px;font-weight:800;display:flex;align-items:center;justify-content:center;margin-top:1px}
  .lbl .t b{display:block;font-weight:600;font-size:11.8px;color:#fff}
  .lbl .t i{font-style:normal;font-size:10.5px;color:#b8c4b6}

  /* ── 底部控制列 ── */
  #bar{position:fixed;left:0;right:0;bottom:10px;padding:0 10px;display:flex;justify-content:center;
    gap:7px;z-index:30;overflow-x:auto;flex-wrap:nowrap;scrollbar-width:none}
  #bar::-webkit-scrollbar{display:none}
  #bar button{flex:0 0 auto;height:38px;min-width:74px;padding:0 13px;border-radius:11px;cursor:pointer;
    border:1px solid rgba(255,255,255,.13);background:rgba(20,27,24,.9);color:#dfd9c9;
    font-size:12.5px;font-family:inherit;font-weight:600;letter-spacing:.3px;
    backdrop-filter:blur(9px);-webkit-backdrop-filter:blur(9px);transition:.16s}
  #bar button:hover{border-color:var(--line);color:#fff}
  #bar button.on{background:var(--lime);color:#12160f;border-color:var(--lime);
    box-shadow:0 6px 18px rgba(203,242,76,.22)}
  #bar2{position:fixed;left:0;right:0;bottom:60px;display:flex;justify-content:center;z-index:30;
    padding:0 12px;pointer-events:none}
  #bar2 .wrap{pointer-events:auto;display:flex;align-items:center;gap:10px;padding:6px 14px;
    border-radius:11px;background:rgba(17,23,20,.82);border:1px solid rgba(255,255,255,.09);
    backdrop-filter:blur(9px);-webkit-backdrop-filter:blur(9px);font-size:11.5px;color:var(--dim)}
  #bar2 input[type=range]{-webkit-appearance:none;appearance:none;width:min(38vw,210px);height:3px;
    background:rgba(255,255,255,.18);border-radius:2px;outline:none}
  #bar2 input[type=range]::-webkit-slider-thumb{-webkit-appearance:none;width:15px;height:15px;
    border-radius:50%;background:var(--lime);border:2px solid #12160f;cursor:pointer}
  #bar2 #exv{color:var(--lime);font-weight:700;min-width:34px;text-align:right;font-variant-numeric:tabular-nums}

  /* ── 圖例／說明 ── */
  #legend{position:fixed;left:14px;bottom:112px;padding:10px 13px;font-size:11px;color:var(--dim);
    line-height:1.8;z-index:18;max-width:230px}
  #legend b{color:#fff;font-size:11.5px;display:block;margin-bottom:3px}
  #legend .sw{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:6px;
    vertical-align:-1px}

  #err{position:fixed;left:50%;top:14px;transform:translateX(-50%);background:#7d1f18;color:#fff;
    padding:8px 14px;border-radius:9px;font-size:12px;display:none;z-index:99;max-width:80vw}

  @media (max-width:760px){
    #hud{max-width:64vw;padding:9px 12px}
    #hud span{display:none}
    #hud .tag{margin-top:4px;font-size:9.5px}
    #legend{display:none}
    #finfo{width:min(280px,62vw);right:10px;top:10px;padding:10px 12px}
    .lbl{font-size:10.5px}
    #bar{gap:6px;padding:0 8px;justify-content:flex-start}
    #bar button{min-width:66px;height:38px;font-size:12px;padding:0 10px}
    #bar2{bottom:62px}
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
  <b>智賢1號 <i>ZHIXIAN 1</i></b>
  <span>桌上型老人陪伴／對話裝置・1 格 = 1 mm<br>拖曳旋轉 · 滾輪縮放 · 點零件看規格</span>
  <div class="tag">3D 列印外殼 200 × 150 × 95 mm</div>
</div>

<div id="finfo" class="panel"></div>

<div id="lblLayer">
  <svg id="lead" xmlns="http://www.w3.org/2000/svg"></svg>
</div>

<div id="legend" class="panel">
  <b>顏色語彙</b>
  <div><span class="sw" style="background:#f3ecdd"></span>奶油白 PLA 外殼</div>
  <div><span class="sw" style="background:#8a5b38"></span>胡桃木側板</div>
  <div><span class="sw" style="background:#cbf24c"></span>萊姆綠 × 黃銅飾條</div>
  <div><span class="sw" style="background:#d8342a"></span>緊急呼叫（紅）</div>
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

var SHOT=/[?&]shot=1/.test(location.search);
var VIEW=(location.search.match(/[?&]view=([a-z]+)/)||[])[1]||'asm';
/* 出圖驗證用：?polar=<弧度>&az=<弧度> 指定視角（polar 同 phi） */
var QPOLAR=parseFloat(((location.search.match(/[?&](?:polar|phi)=([0-9.]+)/)||[])[1]));
var QAZ=parseFloat(((location.search.match(/[?&](?:az|theta)=(-?[0-9.]+)/)||[])[1]));

/* ═══════════════ 基本場景 ═══════════════ */
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
scene.background=new THREE.Color(0x0b100e);
window.scene=scene;
scene.fog=new THREE.Fog(0x0b100e,900,2200);

var camera=new THREE.PerspectiveCamera(38,window.innerWidth/window.innerHeight,1,4000);
var controls=new THREE.OrbitControls(camera,renderer.domElement);
controls.enableDamping=true;controls.dampingFactor=0.075;
controls.minDistance=80;controls.maxDistance=1600;
controls.maxPolarAngle=Math.PI*0.995;controls.minPolarAngle=0.005;  /* 完整 360°：可轉到底部看元件底盤 */
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

/* ── 光源（洗白過一次，數值是實測值，別調高） ── */
var hemi=new THREE.HemisphereLight(0xdde8e2,0x4a5a55,0.50);scene.add(hemi);  /* 地面色提亮：轉到底部時朝下的面才看得到細節（正面實測亮度不變） */
var key=new THREE.DirectionalLight(0xfff6e8,1.45);
key.position.set(230,320,260);key.castShadow=true;
key.shadow.mapSize.set(2048,2048);
key.shadow.camera.left=-280;key.shadow.camera.right=280;
key.shadow.camera.top=320;key.shadow.camera.bottom=-160;
key.shadow.camera.near=1;key.shadow.camera.far=1100;
key.shadow.bias=-0.0009;key.shadow.normalBias=1.0;
scene.add(key);
var fill=new THREE.DirectionalLight(0xcfe0ff,0.30);fill.position.set(-280,140,180);scene.add(fill);
var rim=new THREE.DirectionalLight(0xcbf24c,0.42);rim.position.set(-160,110,-260);scene.add(rim);
var back=new THREE.DirectionalLight(0xffffff,0.55);back.position.set(60,60,-300);scene.add(back);

/* ── 地板 ── */
var floor=new THREE.Mesh(new THREE.CircleGeometry(760,64),
  new THREE.MeshStandardMaterial({color:0x070b0a,roughness:.96,metalness:0,envMapIntensity:0.12}));
floor.rotation.x=-Math.PI/2;floor.position.y=-3.6;floor.receiveShadow=true;scene.add(floor);
var grid=new THREE.GridHelper(1200,60,0x2a3a33,0x18241f);
grid.position.y=-3.55;grid.material.transparent=true;grid.material.opacity=.45;scene.add(grid);

/* ═══════════════ 材質 ═══════════════ */
function mat(o){var m=new THREE.MeshStandardMaterial(o);m.side=THREE.DoubleSide;
  m.envMapIntensity=(o.metalness&&o.metalness>0.6)?1.25:0.20;return m;}
var M={
  cream:   mat({color:0xf3ecdd,roughness:.62,metalness:.02}),
  cream2:  mat({color:0xe6dbc3,roughness:.66,metalness:.02}),
  wood:    mat({color:0x8a5b38,roughness:.70,metalness:.02}),
  wood2:   mat({color:0x6f4527,roughness:.74,metalness:.02}),
  brass:   mat({color:0xc9a227,roughness:.30,metalness:.95}),
  alu:     mat({color:0xb9bec2,roughness:.34,metalness:.90}),
  aluDark: mat({color:0x8b9297,roughness:.42,metalness:.85}),
  ink:     mat({color:0x1d1c1a,roughness:.52,metalness:.12}),
  inkSoft: mat({color:0x2a2a27,roughness:.70,metalness:.05}),
  glass:   mat({color:0x0a0e10,roughness:.16,metalness:.30}),
  pcb:     mat({color:0x1e6b3c,roughness:.56,metalness:.05}),
  pcbDark: mat({color:0x14512c,roughness:.58,metalness:.05}),
  gold:    mat({color:0xd8b45a,roughness:.28,metalness:.95}),
  red:     mat({color:0xbe2419,roughness:.44,metalness:.03}),
  redDark: mat({color:0x7d140e,roughness:.54,metalness:.05}),
  lime:    mat({color:0xcbf24c,roughness:.42,metalness:.05,emissive:0x3d5510,emissiveIntensity:.55}),
  rubber:  mat({color:0x24241f,roughness:.94,metalness:0}),
  grille:  mat({color:0x2f2f2b,roughness:.88,metalness:.05}),
  white:   mat({color:0xf6f2e6,roughness:.75,metalness:0}),
  woodEdge:mat({color:0x5f3c22,roughness:.76,metalness:.02})
};

/* ═══════════════ 畫布貼圖 ═══════════════ */
function screenTex(){
  var W=1024,H=572,cv=document.createElement('canvas');cv.width=W;cv.height=H;
  var c=cv.getContext('2d');
  var g=c.createLinearGradient(0,0,0,H);g.addColorStop(0,'#fffdf7');g.addColorStop(1,'#f1e9d7');
  c.fillStyle=g;c.fillRect(0,0,W,H);
  /* 頂部狀態列 */
  c.fillStyle='#e8dfc8';c.fillRect(0,0,W,54);
  c.fillStyle='#7e8a72';c.font='500 22px "PingFang TC",sans-serif';
  c.fillText('嘉蘭 · 智賢1號',34,36);
  c.fillStyle='#1f6b3c';c.beginPath();c.arc(W-60,27,9,0,7);c.fill();
  c.fillStyle='#6e7a66';c.font='500 21px "PingFang TC",sans-serif';c.textAlign='right';
  c.fillText('Wi-Fi 已連線　電量 82%',W-80,35);c.textAlign='left';
  /* 大字時鐘 */
  c.fillStyle='#161614';c.font='bold 168px "PingFang TC","Helvetica Neue",sans-serif';
  c.fillText('08:30',44,238);
  c.fillStyle='#6f6d60';c.font='500 34px "PingFang TC",sans-serif';
  c.fillText('10月21日 星期三',50,296);
  /* 台語問候 */
  c.fillStyle='#161614';c.font='bold 62px "PingFang TC",sans-serif';
  c.fillText('阿嬤，食飽未？',48,392);
  c.fillStyle='#cbf24c';c.fillRect(50,410,470,12);
  /* 大按鈕 */
  (function(){var x=678,y=330,w=286,h=160,r=40;
    c.beginPath();c.moveTo(x+r,y);c.lineTo(x+w-r,y);c.quadraticCurveTo(x+w,y,x+w,y+r);
    c.lineTo(x+w,y+h-r);c.quadraticCurveTo(x+w,y+h,x+w-r,y+h);c.lineTo(x+r,y+h);
    c.quadraticCurveTo(x,y+h,x,y+h-r);c.lineTo(x,y+r);c.quadraticCurveTo(x,y,x+r,y);
    c.closePath();
    var bg=c.createLinearGradient(x,y,x,y+h);bg.addColorStop(0,'#d6fa62');bg.addColorStop(1,'#b4dd35');
    c.fillStyle=bg;c.fill();
  })();
  /* 麥克風圖示 */
  c.fillStyle='#1b1e14';
  c.beginPath();c.ellipse(752,382,15,26,0,0,7);c.fill();
  c.strokeStyle='#1b1e14';c.lineWidth=7;c.lineCap='round';
  c.beginPath();c.arc(752,392,30,0.15*Math.PI,0.85*Math.PI);c.stroke();
  c.beginPath();c.moveTo(752,422);c.lineTo(752,436);c.stroke();
  c.font='bold 60px "PingFang TC",sans-serif';c.fillText('講話',822,432);
  c.fillStyle='#8b8a7a';c.font='500 21px "PingFang TC",sans-serif';
  c.fillText('按住說話・放開送出',700,522);
  /* 右下角提示 */
  c.fillStyle='#9c9a88';c.font='500 20px "PingFang TC",sans-serif';
  c.fillText('緊急時按右下紅鈕',48,522);
  var t=new THREE.CanvasTexture(cv);t.anisotropy=8;t.encoding=THREE.sRGBEncoding;return t;
}

function ledTex(){
  var NX=64,NY=32,S=11;
  /* 高解析繪製 → 降採樣 → 逐點畫 LED，避免小畫布直接寫字造成的糊化與摩爾紋 */
  var hi=document.createElement('canvas');hi.width=NX*8;hi.height=NY*8;
  var h=hi.getContext('2d');
  h.fillStyle='#000';h.fillRect(0,0,hi.width,hi.height);
  h.fillStyle='#fff';h.textAlign='center';h.textBaseline='middle';
  h.font='bold 150px ui-monospace,"SF Mono",Menlo,monospace';
  h.fillText('08:30',hi.width/2,hi.height*0.44);
  var s2=document.createElement('canvas');s2.width=NX;s2.height=NY;
  var x2=s2.getContext('2d');
  x2.imageSmoothingEnabled=true;x2.imageSmoothingQuality='high';
  x2.drawImage(hi,0,0,NX,NY);
  var d=x2.getImageData(0,0,NX,NY).data;

  var cv=document.createElement('canvas');cv.width=NX*S;cv.height=NY*S;
  var c=cv.getContext('2d');
  c.fillStyle='#05080a';c.fillRect(0,0,cv.width,cv.height);
  for(var j=0;j<NY;j++)for(var i=0;i<NX;i++){
    var v=d[(j*NX+i)*4]/255;
    var cx=i*S+S/2,cy=j*S+S/2;
    c.beginPath();c.arc(cx,cy,S*0.34,0,7);
    if(v>0.16){
      c.fillStyle='rgba(203,242,76,'+(0.25+0.75*v).toFixed(3)+')';c.fill();
      c.beginPath();c.arc(cx,cy,S*0.15,0,7);
      c.fillStyle='rgba(248,255,224,'+(0.40+0.60*v).toFixed(3)+')';c.fill();
    }else{
      c.fillStyle='rgba(38,58,42,0.50)';c.fill();
    }
  }
  var t=new THREE.CanvasTexture(cv);t.magFilter=THREE.NearestFilter;t.minFilter=THREE.LinearFilter;
  t.encoding=THREE.sRGBEncoding;t.generateMipmaps=false;return t;
}

function woodTex(){
  var cv=document.createElement('canvas');cv.width=128;cv.height=128;
  var c=cv.getContext('2d');
  c.fillStyle='#8a5b38';c.fillRect(0,0,128,128);
  for(var i=0;i<90;i++){
    var y=Math.random()*128,h=0.5+Math.random()*1.7;
    c.strokeStyle='rgba('+(70+Math.random()*60|0)+','+(40+Math.random()*35|0)+','+(22+Math.random()*22|0)+','+(0.20+Math.random()*0.35).toFixed(2)+')';
    c.lineWidth=h;c.beginPath();
    var yy=y;c.moveTo(0,yy);
    for(var xx=0;xx<=128;xx+=16){yy+= (Math.random()-0.5)*2.2;c.lineTo(xx,yy);}
    c.stroke();
  }
  var t=new THREE.CanvasTexture(cv);t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(3,2);
  t.encoding=THREE.sRGBEncoding;return t;
}
M.wood.map=woodTex();M.wood.needsUpdate=true;
M.wood2.map=M.wood.map;

/* ═══════════════ 幾何小工具 ═══════════════ */
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
/* 圓角矩形實心板（可在 XY 面，沿 +Z 擠出，置中厚度） */
function plate(w,h,t,r,seg){
  var g=new THREE.ExtrudeGeometry(rrShape(w,h,r),{depth:t,bevelEnabled:false,curveSegments:seg||16});
  g.translate(0,0,-t/2);
  return g;
}
/* 圓角矩形環（中間開窗） */
function frameGeom(w,h,t,r,ww,wh,wr){
  var s=rrShape(w,h,r);s.holes.push(rrPath(ww,wh,wr));
  var g=new THREE.ExtrudeGeometry(s,{depth:t,bevelEnabled:false,curveSegments:18});
  g.translate(0,0,-t/2);
  return g;
}
function mesh(g,m){var o=new THREE.Mesh(g,m);o.castShadow=true;o.receiveShadow=true;return o;}
function box(w,h,d,m){return mesh(new THREE.BoxGeometry(w,h,d),m);}
function cylY(r1,r2,h,m,seg){return mesh(new THREE.CylinderGeometry(r1,r2,h,seg||32),m);}

/* ═══════════════ 零件建構 ═══════════════ */
/* 面板（前框＋螢幕）的擺放：底部邊緣落在機殼頂面前緣，往後傾 12° */
var TILT=-12*Math.PI/180;
var PANEL_C=new THREE.Vector3(0,138.2,31.3);
function panelVec(lx,ly,lz){
  var v=new THREE.Vector3(lx,ly,lz);
  v.applyAxisAngle(new THREE.Vector3(1,0,0),TILT);
  return v.add(PANEL_C);
}

/* 1. 主機殼 */
function buildShell(){
  var g=new THREE.Group();
  var outer=rrShape(200,150,8);outer.holes.push(rrPath(195,145,5.5));
  var walls=extY(outer,95,16);
  walls.translate(0,0,0);
  var w=mesh(walls,M.cream);g.add(w);
  /* 頂板（嵌在內腔，避免共面） */
  var top=extY(rrShape(194.6,144.6,5.3),2.5,14);top.translate(0,92.5,0);
  g.add(mesh(top,M.cream));
  /* 斜面板出線環：讓面板「穿過」一個深墨框，藏住平面交線 */
  var coll=mesh(frameGeom(176,116,10,6,166,106,4),M.ink);
  coll.position.copy(panelVec(0,-45,0));coll.rotation.x=TILT;g.add(coll);
  /* 內部支撐肋（兩片） */
  [-62,62].forEach(function(x){
    var rib=box(4,60,26,M.cream2);rib.position.set(x,64,-52);g.add(rib);
  });
  return g;
}

/* 2. 前框（螢幕斜面板） */
function buildFrame(){
  var g=new THREE.Group();
  g.add(mesh(frameGeom(165,105,6,5,154,86,2.5),M.ink));
  return g;
}

/* 3. 7 吋觸控螢幕模組 */
var scrMat=null;
function buildScreen(){
  var g=new THREE.Group();
  scrMat=mat({color:0x14171a,roughness:.28,metalness:.15});
  var body=box(165,100,5,scrMat);body.position.z=-2.5;g.add(body);
  var ui=new THREE.Mesh(new THREE.PlaneGeometry(156,88),
    new THREE.MeshStandardMaterial({map:screenTex(),emissive:0xffffff,emissiveMap:null,
      emissiveIntensity:0,roughness:.42,metalness:0,side:THREE.DoubleSide}));
  ui.material.map.encoding=THREE.sRGBEncoding;
  ui.material.emissiveMap=ui.material.map;ui.material.emissiveIntensity=0.78;
  ui.material.color.set(0x8e8e8e);
  ui.position.z=0.16;g.add(ui);
  /* 排線 */
  var ff=box(26,2,14,M.white);ff.position.set(0,-46,-6);g.add(ff);
  return g;
}

/* 4. LED 點陣面板 64×32 P5 */
function buildLed(){
  var g=new THREE.Group();
  var body=box(160,80,12,M.ink);body.position.z=-6;g.add(body);
  var face=new THREE.Mesh(new THREE.PlaneGeometry(160,80),
    new THREE.MeshStandardMaterial({map:ledTex(),emissive:0xffffff,emissiveIntensity:0.85,
      roughness:.55,metalness:.05,side:THREE.DoubleSide}));
  face.material.emissiveMap=face.material.map;
  face.material.map.encoding=THREE.sRGBEncoding;
  face.position.z=0.25;g.add(face);
  /* 邊框 */
  var fg=frameGeom(164,84,2,1.5,156,76,1.2);
  var f=mesh(fg,M.aluDark);f.position.z=1.2;g.add(f);
  return g;
}

/* 5. 樹莓派 Zero 2W */
function buildPi(){
  var g=new THREE.Group();
  var p=box(65,30,5,M.pcb);g.add(p);
  /* SoC */
  var soc=box(15,15,1.4,M.ink);soc.position.set(-2,2,3.2);g.add(soc);
  /* 記憶體 */
  var ram=box(9,9,1.1,M.inkSoft);ram.position.set(-2,-11,3.1);g.add(ram);
  /* GPIO 排針 */
  var hdr=box(51,5,8.5,M.ink);hdr.position.set(-4,14.5,2.6);g.add(hdr);
  var pins=box(49,3.2,1.2,M.gold);pins.position.set(-4,14.5,7.4);g.add(pins);
  /* USB / 電源接頭 */
  var u1=box(8,7.5,3,M.alu);u1.position.set(30,-8,5);g.add(u1);
  var u2=box(8,7.5,3,M.alu);u2.position.set(30,3,5);g.add(u2);
  /* microSD */
  var sd=box(13,11,1.2,M.aluDark);sd.position.set(-30,-12,3);g.add(sd);
  /* 固定孔 */
  [[-29,12],[-29,-12],[29,-12],[27,12]].forEach(function(a){
    var h=cylY(1.6,1.6,5.2,M.cream2,12);h.rotation.x=Math.PI/2;
    h.position.set(a[0],a[1],0);g.add(h);
  });
  return g;
}

/* 6. 散熱片 15×15×8 */
function buildHeatsink(){
  var g=new THREE.Group();
  var base=box(15,15,2,M.alu);base.position.z=1;g.add(base);
  for(var i=0;i<5;i++){
    var f=box(15,1.5,6,M.alu);f.position.set(0,-6+i*3,5);g.add(f);
  }
  return g;
}

/* 7. 喇叭 40mm（Ø40×12，正面朝 +X） */
function buildSpeaker(){
  var g=new THREE.Group();
  /* 法蘭環（Ø48/Ø41），蓋住木板上 Ø44 孔的邊緣 */
  var fl=new THREE.Mesh(new THREE.RingGeometry(20.5,24,56),
    new THREE.MeshStandardMaterial({color:0x2b2b28,roughness:.55,metalness:.35,
      side:THREE.DoubleSide,envMapIntensity:.2}));
  fl.rotation.y=Math.PI/2;fl.position.x=0.28;g.add(fl);
  var fl2=mesh(new THREE.TorusGeometry(23.6,0.8,8,56),M.aluDark);
  fl2.rotation.y=Math.PI/2;fl2.position.x=0.34;g.add(fl2);
  /* 懸邊 */
  var sur=mesh(new THREE.TorusGeometry(17.4,1.7,10,48),M.rubber);
  sur.rotation.y=Math.PI/2;sur.position.x=-0.55;g.add(sur);
  /* 錐盆（往內凹） */
  var cone=mesh(new THREE.CylinderGeometry(17.2,7.5,7,44,1,true),M.grille);
  cone.rotation.z=Math.PI/2;cone.position.x=-4.2;g.add(cone);
  /* 防塵罩 */
  var dome=new THREE.SphereGeometry(5.4,24,12,0,Math.PI*2,0,Math.PI/2);
  dome.rotateZ(-Math.PI/2);dome.translate(-7.4,0,0);
  g.add(mesh(dome,M.ink));
  /* 磁鐵＋框 */
  var mag=cylY(9.5,9.5,4.6,M.inkSoft,28);mag.rotation.z=Math.PI/2;mag.position.x=-9.3;g.add(mag);
  var term=box(2.4,5,3.4,M.gold);term.position.set(-9,-12,-2);g.add(term);
  return g;
}

/* 8. MEMS 麥克風板 20×15×1.6 */
function buildMic(){
  var g=new THREE.Group();
  var p=box(20,15,1.6,M.pcbDark);g.add(p);
  var can=box(4.2,3.4,1.1,M.alu);can.position.set(0,0,1.3);g.add(can);
  var pot=cylY(0.7,0.7,1.4,M.ink,12);pot.rotation.x=Math.PI/2;pot.position.set(0,0,1.6);g.add(pot);
  var conn=box(6,4,1.2,M.white);conn.position.set(-7,-6,1.1);g.add(conn);
  return g;
}

/* 9. 緊急呼叫按鈕 Ø60 高 25 */
function buildButton(){
  var g=new THREE.Group();
  var boss=cylY(32,32,5,M.cream2,48);boss.rotation.x=Math.PI/2;boss.position.z=2.5;g.add(boss);
  var ring=mesh(new THREE.TorusGeometry(31,1.4,10,52),M.brass);
  ring.position.z=5.4;g.add(ring);
  var skirt=cylY(30,29,7,M.redDark,48);skirt.rotation.x=Math.PI/2;skirt.position.z=8.5;g.add(skirt);
  var dome=new THREE.SphereGeometry(30,44,18,0,Math.PI*2,0,Math.PI/2);
  dome.rotateX(Math.PI/2);dome.scale(1,1,13/30);dome.translate(0,0,12);  /* 總高 25mm */
  g.add(mesh(dome,M.red));
  /* 表面凸字「SOS」用三顆小凸點表示 */
  return g;
}

/* 10. USB-C 孔 */
function buildUsbc(){
  var g=new THREE.Group();
  var shellBox=box(9,3.5,1.6,M.alu);g.add(shellBox);
  var slot=box(6.6,1.4,1.2,M.ink);slot.position.z=0.5;g.add(slot);
  var tongue=box(4.6,0.7,1.0,M.gold);tongue.position.set(0,0,0.55);g.add(tongue);
  return g;
}

/* 11. 電源開關 */
function buildSwitch(){
  var g=new THREE.Group();
  var body=box(15,10,1.8,M.ink);g.add(body);
  var cap=box(9,5.4,2.6,M.cream2);cap.position.z=1.6;g.add(cap);
  var led=cylY(1.1,1.1,0.9,M.lime,14);led.rotation.x=Math.PI/2;led.position.set(5.2,3.2,1.2);g.add(led);
  return g;
}

/* 12. 防滑墊 Ø12×3 */
function buildFoot(){
  var g=new THREE.Group();
  var pad=cylY(6,5.4,3,M.rubber,28);g.add(pad);
  return g;
}

/* 13. 散熱孔陣列 6×4 Ø4 */
function buildVents(){
  var g=new THREE.Group();
  for(var i=0;i<6;i++)for(var j=0;j<4;j++){
    var h=cylY(2,2,1.6,M.ink,18);
    h.rotation.x=Math.PI/2;h.position.set(-30+i*12,-15+j*10,0);
    g.add(h);
    var lip=mesh(new THREE.TorusGeometry(2,0.35,6,18),M.aluDark);
    lip.position.set(-30+i*12,-15+j*10,0.8);g.add(lip);
  }
  return g;
}

/* 14. 木質側板 150×95×4（右側開喇叭孔） */
function buildWood(hole){
  var g=new THREE.Group();
  var s=rrShape(149.6,94.6,7);   /* 比殼面內縮 0.2~0.4mm，避免與殼共面 z-fighting */
  if(hole){s.holes.push(new THREE.Path().absarc(0,-2.5,22,0,Math.PI*2,true));}
  var geo=new THREE.ExtrudeGeometry(s,{depth:4,bevelEnabled:false,curveSegments:18});
  geo.translate(0,0,-4);geo.rotateY(Math.PI/2);geo.translate(2,0,0);
  /* 側面（4mm 邊）用純色，避免擠出 UV 在邊緣拉伸成亮點 */
  var m=mesh(geo,[M.wood,M.woodEdge]);g.add(m);
  if(hole){
    var gr=cylY(21,21,1.2,M.grille,40);gr.rotation.z=Math.PI/2;gr.position.set(0.4,0,-2.5);g.add(gr);
  }
  return g;
}

/* 15. 黃銅飾條 200×3×2 */
function buildBrass(){
  var g=new THREE.Group();
  var b=box(200,3,2,M.brass);g.add(b);
  /* 兩端小螺絲 */
  [-92,92].forEach(function(x){
    var sc=cylY(1.2,1.2,2.4,M.alu,10);sc.rotation.x=Math.PI/2;
    sc.position.set(x,0,1.1);g.add(sc);
  });
  return g;
}

/* ═══════════════ 零件表 ═══════════════ */
/* p=位置, r=旋轉, ex=爆炸位移(100%), info=規格 */
var DEFS=[
 {id:'shell',name:'主機殼（3D 列印件）',dim:'200 × 150 × 95 mm',mat:'PLA 奶油白 #f3ecdd・壁厚 2.5・R8',
  use:'一體成形外殼，底部開口可裝底板；兩側銑 4mm 嵌板槽給木質側板。',
  build:buildShell,p:[0,0,0],r:[0,0,0],ex:[0,0,0]},
 {id:'frame',name:'前框／螢幕斜面板',dim:'165 × 105 × 6 mm',mat:'ABS 深墨 #161614・R5',
  use:'固定 7 吋螢幕並壓住防塵；整片後傾 12°，長輩坐著平視不反光。',
  build:buildFrame,p:[0,0,0],r:[0,0,0],ex:[0,26,120],panel:true},
 {id:'screen',name:'7 吋觸控螢幕模組',dim:'165 × 100 × 5 mm（可視區 154 × 86）',mat:'IPS 面板＋鋼化玻璃・排線 30pin',
  use:'1024×600 顯示大字時鐘、台語問候與「講話」大按鈕。',
  build:buildScreen,p:[0,0,0],r:[0,0,0],ex:[0,9,40],panel:true,off:[0,0,-5.5]},
 {id:'led',name:'LED 點陣面板 64×32 P5',dim:'160 × 80 × 12 mm',mat:'P5 全彩模組・HUB75',
  use:'正面下緣的跑馬燈：顯示時間、提醒與愛心圖案，遠看也清楚。',
  build:buildLed,p:[-16,45,75.3],r:[0,0,0],ex:[0,-78,190]},
 {id:'pi',name:'樹莓派 Zero 2W',dim:'65 × 30 × 5 mm',mat:'FR-4 綠板・BCM2710A1 四核 1GHz',
  use:'主控：跑台語語音辨識、離線 TTS 與螢幕 UI。',
  build:buildPi,p:[0,50,-68],r:[0,0,0],ex:[0,110,-95]},
 {id:'hs',name:'鋁擠散熱片',dim:'15 × 15 × 8 mm',mat:'6063 鋁・陽極本色',
  use:'貼在 SoC 上，被動散熱；密閉殼內靠對流孔排出。',
  build:buildHeatsink,p:[0,52,-65.5],r:[0,0,0],ex:[0,215,-95]},
 {id:'spk',name:'喇叭 40 mm',dim:'Ø40 × 12 mm（4Ω 3W）',mat:'釹鐵硼磁鐵＋紙盆＋金屬框',
  use:'側面出聲，播報提醒與對話回覆；右側木板的 Ø44 孔就是出音口。',
  build:buildSpeaker,p:[100.4,45,-18],r:[0,0,0],ex:[205,55,60]},
 {id:'micL',name:'MEMS 麥克風板（左）',dim:'20 × 15 × 1.6 mm',mat:'FR-4＋MEMS 麥克風（I²S）',
  use:'雙麥克風陣列左聲道，間距 90mm 做指向性收音、壓低電視噪音。',
  build:buildMic,p:[-45,74,71.2],r:[0,0,0],ex:[-165,150,75]},
 {id:'micR',name:'MEMS 麥克風板（右）',dim:'20 × 15 × 1.6 mm',mat:'FR-4＋MEMS 麥克風（I²S）',
  use:'雙麥克風陣列右聲道，與左麥相距 90mm。',
  build:buildMic,p:[45,74,71.2],r:[0,0,0],ex:[165,150,75]},
 {id:'btn',name:'緊急呼叫按鈕',dim:'Ø60 × 25 mm',mat:'ABS 紅色圓頂＋黃銅飾環',
  use:'一按直接撥號給家人／照護中心，長按 3 秒啟動；凸出 25mm 好摸。',
  build:buildButton,p:[68,41,75],r:[0,0,0],ex:[168,-52,175]},
 {id:'usbc',name:'USB-C 電源孔',dim:'9 × 3.5 mm（面板型母座）',mat:'不鏽鋼殼＋鍍金舌片',
  use:'背面 USB-C 面板母座：維修供電／螢幕觸控 USB 走線；主電源由 12V DC 5.5×2.1 進。',
  build:buildUsbc,p:[-40,32,-75],r:[0,0,0],ex:[-105,5,-215]},
 {id:'pwr',name:'電源開關',dim:'15 × 10 mm',mat:'PA66 本體＋萊姆指示燈',
  use:'背面實體總開關，關機不斷電（維持 RTC）；指示燈呼吸表示待機。',
  build:buildSwitch,p:[30,32,-75],r:[0,0,0],ex:[130,5,-215]},
 {id:'foot',name:'底部防滑墊 ×4',dim:'Ø12 × 3 mm',mat:'矽膠 60 度・黑色',
  use:'四角落止滑並抬高 3mm 進氣；對應底座 4 個 Ø12.3 凹槽。',
  build:buildFoot,p:[-80,-1.5,-52],r:[0,0,0],ex:[0,-95,0],copies:[[80,-1.5,-52],[-80,-1.5,52],[80,-1.5,52]]},
 {id:'vent',name:'散熱孔陣列 6×4',dim:'Ø4 × 24 孔（間距 12/10mm）',mat:'殼體直接開孔',
  use:'背面對流孔，配合內部肋板形成煙囪效應；總開孔率 12%。',
  build:buildVents,p:[0,67,-75],r:[0,0,0],ex:[-40,20,-205]},
 {id:'woodL',name:'木質側板（左）',dim:'150 × 95 × 4 mm',mat:'胡桃木實木薄板・油蠟塗裝',
  use:'左右各一，遮住列印接縫、握感溫潤；左板為整片。',
  build:function(){return buildWood(false);},p:[-98.2,47.4,0],r:[0,0,0],ex:[-235,40,0]},
 {id:'woodR',name:'木質側板（右）',dim:'150 × 95 × 4 mm（Ø44 出音孔）',mat:'胡桃木實木薄板・油蠟塗裝',
  use:'右板開 Ø44 圓孔對齊喇叭，內襯深色網布。',
  build:function(){return buildWood(true);},p:[98.2,47.4,0],r:[0,0,0],ex:[235,40,0]},
 {id:'brass',name:'黃銅飾條',dim:'200 × 3 × 2 mm',mat:'H62 黃銅・拉絲＋透明漆',
  use:'正面下緣收邊，視覺上把奶油白殼「壓」在桌上。',
  build:buildBrass,p:[0,4.5,76],r:[0,0,0],ex:[-30,-45,255]}
];

var model=new THREE.Group();scene.add(model);
var PARTS=[];
DEFS.forEach(function(d){
  var g=d.build();
  g.userData.info={t:d.name,rows:[['尺寸',d.dim],['材質',d.mat],['用途',d.use]]};
  var pos=new THREE.Vector3().fromArray(d.p);
  var rot=d.r;
  if(d.panel){
    var pv=panelVec(d.p[0],d.p[1],d.p[2]);
    if(d.off){pv.add(new THREE.Vector3(d.off[0],d.off[1],d.off[2]).applyAxisAngle(new THREE.Vector3(1,0,0),TILT));}
    pos.copy(pv);rot=[TILT,0,0];
  }
  g.position.copy(pos);g.rotation.set(rot[0],rot[1],rot[2]);
  model.add(g);
  var rec={id:d.id,def:d,g:g,home:pos.clone(),rot:rot.slice(),ex:new THREE.Vector3().fromArray(d.ex)};
  g.userData.rec=rec;
  PARTS.push(rec);
  /* 額外副本（防滑墊 4 顆） */
  if(d.copies){
    d.copies.forEach(function(cp){
      var c2=d.build();
      c2.userData.info=g.userData.info;
      c2.position.fromArray(cp);
      var r2={id:d.id,def:d,g:c2,home:c2.position.clone(),rot:[0,0,0],
        ex:new THREE.Vector3().fromArray(d.ex),ghost:true};
      c2.userData.rec=r2;
      model.add(c2);PARTS.push(r2);
    });
  }
});
window.PARTS=PARTS;

/* 標籤只給「主體零件」（防滑墊 4 顆算一個標籤） */
var LABELED=PARTS.filter(function(p){return !p.ghost;});

/* ═══════════════ 爆炸軸 ═══════════════ */
var axisMat=new THREE.LineDashedMaterial({color:0x2f8fff,dashSize:6,gapSize:5,
  transparent:true,opacity:.9});
var axisGeo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,-150,0),
  new THREE.Vector3(0,290,0)]);
var axisLine=new THREE.Line(axisGeo,axisMat);
axisLine.computeLineDistances();axisLine.visible=false;scene.add(axisLine);

/* ═══════════════ 尺寸標註 ═══════════════ */
var dimGroup=new THREE.Group();dimGroup.visible=false;scene.add(dimGroup);
function sprLabel(text,size,fg,bg){
  var fs=64,pad=18;
  var c=document.createElement('canvas').getContext('2d');
  var ff='bold '+fs+'px "PingFang TC",sans-serif';
  c.font=ff;
  var w=Math.ceil(c.measureText(text).width)+pad*2,h=fs+pad*2;
  var cv=document.createElement('canvas');cv.width=w;cv.height=h;
  c=cv.getContext('2d');c.font=ff;
  var r=18;c.fillStyle=bg||'#cbf24c';c.beginPath();
  c.moveTo(r,0);c.lineTo(w-r,0);c.quadraticCurveTo(w,0,w,r);c.lineTo(w,h-r);
  c.quadraticCurveTo(w,h,w-r,h);c.lineTo(r,h);c.quadraticCurveTo(0,h,0,h-r);
  c.lineTo(0,r);c.quadraticCurveTo(0,0,r,0);c.closePath();c.fill();
  c.fillStyle=fg||'#12160f';c.textBaseline='middle';c.fillText(text,pad,h/2+2);
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
  var col=0xcbf24c;
  dimGroup.add(rod(a,b,0.55,col));
  var dir=new THREE.Vector3().subVectors(b,a).normalize();
  var perp=new THREE.Vector3(0,1,0);
  if(Math.abs(dir.dot(perp))>0.9)perp.set(1,0,0);
  var t1=a.clone().add(new THREE.Vector3().crossVectors(dir,perp).multiplyScalar(4));
  var t2=a.clone().add(new THREE.Vector3().crossVectors(dir,perp).multiplyScalar(-4));
  dimGroup.add(rod(t1,t2,0.55,col));
  t1=b.clone().add(new THREE.Vector3().crossVectors(dir,perp).multiplyScalar(4));
  t2=b.clone().add(new THREE.Vector3().crossVectors(dir,perp).multiplyScalar(-4));
  dimGroup.add(rod(t1,t2,0.55,col));
  var lb=sprLabel(label,size||13);
  lb.position.copy(a).add(b).multiplyScalar(.5);
  dimGroup.add(lb);
}
(function buildDims(){
  var c=0xcbf24c;
  /* 寬 200（前方，y=-22） */
  addDim(new THREE.Vector3(-100,-22,108),new THREE.Vector3(100,-22,108),'寬 200 mm',13);
  [-100,100].forEach(function(x){dimGroup.add(rod(new THREE.Vector3(x,-3,78),new THREE.Vector3(x,-22,108),0.35,c));});
  /* 深 150（右側，y=-22） */
  addDim(new THREE.Vector3(128,-22,-75),new THREE.Vector3(128,-22,75),'深 150 mm',13);
  [-75,75].forEach(function(z){dimGroup.add(rod(new THREE.Vector3(102,-3,z),new THREE.Vector3(128,-22,z),0.35,c));});
  /* 高 95（右後，x=128） */
  addDim(new THREE.Vector3(128,0,-88),new THREE.Vector3(128,95,-88),'高 95 mm',13);
  [0,95].forEach(function(y){dimGroup.add(rod(new THREE.Vector3(102,y,-78),new THREE.Vector3(128,y,-88),0.35,c));});
  /* 螢幕斜背高度（虛線參考） */
  var lb=sprLabel('總高 191（含斜背）',9,'#e9e3d3','rgba(20,26,22,.9)');
  lb.position.set(0,205,30);dimGroup.add(lb);
})();

/* ═══════════════ 取景（解析式 fitBox） ═══════════════ */
var bboxCache=new THREE.Box3();
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
  camera.near=Math.max(pr/2000,0.02);
  camera.far=pr*80;
  camera.updateProjectionMatrix();
  controls.target.copy(c);
  camera.position.copy(c).addScaledVector(d,dist);
  camera.lookAt(c);
  controls.update();
  return b;
}
var DIRS={
  asm:new THREE.Vector3(0.62,0.40,0.68),
  exploded:new THREE.Vector3(0.55,0.30,0.78),
  dims:new THREE.Vector3(0.52,0.34,0.79)
};
var PADS={asm:1.16,exploded:1.30,dims:1.22};
function padOf(mode){
  var narrow=window.innerWidth<760;
  if(mode==='exploded')return narrow?1.85:1.30;
  if(mode==='dims')return narrow?1.55:1.22;
  return narrow?1.22:1.16;
}
var userMoved=false;
controls.addEventListener('start',function(){userMoved=true;});

/* ═══════════════ 模式 ═══════════════ */
var MODE='asm',EX=0,EXT=0,MODE_TWEEN=0;
var exr=document.getElementById('exr'),exv=document.getElementById('exv');
var lblLayer=document.getElementById('lblLayer'),leadSvg=document.getElementById('lead');

function setMode(m,instant){
  MODE=m;
  var bs=document.querySelectorAll('#bar button[data-mode]');
  for(var i=0;i<bs.length;i++)bs[i].className=(bs[i].getAttribute('data-mode')===m)?'on':'';
  axisLine.visible=(m==='exploded');
  lblLayer.style.display=(m==='exploded')?'block':'none';
  dimGroup.visible=(m==='dims');
  if(m==='exploded'){EXT=(exr.value|0)/100;if(EXT<0.35){EXT=1;exr.value=100;}}
  else{EXT=0;exr.value=0;}
  exv.textContent=Math.round(EXT*100)+'%';
  if(instant){EX=EXT;}
  /* 先套用位移再取景 */
  clearFocus(true);
  applyExplode();
  if(m==='exploded'){userMoved=false;fitBox(DIRS.exploded,padOf('exploded'));}
  else if(m==='dims'){userMoved=false;fitBox(DIRS.dims,padOf('dims'));}
  else{userMoved=false;fitBox(DIRS.asm,padOf('asm'));}
  MODEFIT[m]=camera.position.distanceTo(controls.target);
  updateLabels(true);
  hideInfo();
  try{renderer.render(scene,camera);}catch(e){}
  window.__mode=m;
}
var EXK=0.84;   /* 爆炸總幅度係數：太大零件會變小、標籤引線拉太長 */
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
}

/* ═══════════════ 標籤 ═══════════════ */
var LBL=[];
function buildLabels(){
  lblLayer.appendChild(leadSvg);
  /* 依 home.y 由下往上排序 → 組裝順序編號 */
  /* 編號＝組裝順序（對齊 README 第三節「組裝順序」） */
  var ORDER=['foot','shell','pi','hs','spk','micL','micR','btn','led','usbc','pwr','vent',
             'woodL','woodR','frame','screen','brass'];
  var order=LABELED.slice().sort(function(a,b){
    var ia=ORDER.indexOf(a.id),ib=ORDER.indexOf(b.id);
    if(ia<0)ia=99;if(ib<0)ib=99;
    if(ia!==ib)return ia-ib;
    return a.home.y-b.home.y;
  });
  order.forEach(function(p,i){
    p.num=i+1;
    var el=document.createElement('div');
    el.className='lbl';
    var b=document.createElement('div');b.className='b';b.textContent=String(i+1);
    var t=document.createElement('div');t.className='t';
    var nb=document.createElement('b');nb.textContent=p.def.name;
    var ii=document.createElement('i');ii.textContent=p.def.dim;
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
buildLabels();

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
    var rec=L.p;
    var bb=new THREE.Box3().setFromObject(rec.g);
    var ctr=bb.getCenter(new THREE.Vector3());
    var pr=projPoint(ctr);
    L.ax=pr.x;L.ay=pr.y;
    L.side=(pr.x<cx)?'L':'R';
    L.el.style.display='flex';
  });
  var colW=narrow?Math.max(120,Math.min(168,W*0.42)):Math.min(310,Math.max(140,W*0.25));
  ['L','R'].forEach(function(side){
    var arr=LBL.filter(function(L){return L.side===side;})
      .sort(function(a,b){return a.ay-b.ay;});
    var n=arr.length,avail=H-pad-padB,gap=narrow?46:54;
    if(n>1&&(n-1)*gap>avail)gap=avail/(n-1);
    /* 1) 由上往下推開  2) 底部夾住  3) 由下往上回推  4) 整組下移避免超出上緣 */
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
var SHELLM=[{k:'cream',f:1},{k:'cream2',f:0.93}];
var SHELLC=[['奶油白','f3ecdd'],['石墨黑','2f3336'],['霧灰綠','8a9a8d'],['霧藍','7c93a6'],['陶土橘','c8764e']];
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
  /* 黃色外框 */
  clearOutline();
  var bb=new THREE.Box3().setFromObject(rec.g);
  var size=bb.getSize(new THREE.Vector3()),c=bb.getCenter(new THREE.Vector3());
  outline=new THREE.LineSegments(new THREE.EdgesGeometry(
    new THREE.BoxGeometry(size.x*1.04+1,size.y*1.04+1,size.z*1.04+1)),
    new THREE.LineBasicMaterial({color:0xcbf24c,transparent:true,opacity:.95,depthTest:false}));
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
};
var bfocusEl=document.getElementById('bfocus');
if(bfocusEl)bfocusEl.onclick=function(){hideInfo();};   /* 取消特寫：還原材質＋相機回原取景 */
exr.oninput=function(){
  EXT=(this.value|0)/100;
  exv.textContent=Math.round(EXT*100)+'%';
  if(MODE!=='exploded'&&EXT>0.02)setMode('exploded',true);
};
/* 手機：滑桿在爆炸圖才有意義，其他模式淡化 */
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
var spin=SHOT?0:0.055;
var last=performance.now(),frame=0;
var STILL=/[?&]still=1/.test(location.search);  /* 驗證用：只畫前 3 幀，主執行緒才不會被軟體 GL 佔滿 */
function tick(){
  if(!STILL||frame<3)requestAnimationFrame(tick);
  var now=performance.now(),dt=Math.min((now-last)/16.7,3);last=now;
  /* 爆炸補間 */
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
  if(outline){outline.material.opacity=0.72+0.26*Math.sin(now*0.004);}
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
applyExplode();
setMode(VIEW==='exploded'?'exploded':(VIEW==='dims'?'dims':'asm'),true);
applyQueryView();
syncSlider();
tick();

/* ═══════════════ 除錯鉤子 ═══════════════ */
window.__ec={
  __f:__focusDbg(),
  get mode(){return MODE;},
  get labels(){return document.querySelectorAll('.lbl').length;},
  get leads(){return document.querySelectorAll('#lead polyline').length;},
  get parts(){return LABELED.length;},
  get frames(){return frame;},
  get bbox(){var b=modelBox();var s=b.getSize(new THREE.Vector3());
    return [+s.x.toFixed(2),+s.y.toFixed(2),+s.z.toFixed(2)];},
  get cam(){return camera.position.toArray().map(function(v){return +v.toFixed(1);});},
  get info(){var e=document.getElementById('finfo');return e.style.display!=='none'?e.textContent:'';},
  get errors(){return window.__errors;},
  pick:function(x,y){var r=pickAt(x,y);return r?r.def.name:null;},
  setMode:function(m){setMode(m,true);},
  setExplode:function(v){EXT=v;EX=v;applyExplode();}
};
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
    path = os.path.join(outdir, "elderchat-system.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path, len(html.encode("utf-8"))


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    p, n = build(out)
    print(p, n)
