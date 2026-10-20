/* parts-real.js — 3D 模型庫「電子元件仿真化」模組
   把原本的白色方塊（XIAO / USB-C / INMP441 / LSM6DS3 / OLED / 鋰電池 / 震動馬達 / 磁鐵 / pogo pin）
   換成有細節的寫實模型：黑色 PCB、金色接腳、金屬屏蔽罩、絲印文字、玻璃面板、鋁箔電池包、偏心錘…
   尺寸完全沿用原本的方塊外框（這頁是「尺寸示意」，比例不能跑掉）。
   原方塊不刪除、改成全透明 → 點選/尺寸標註/射線偵測全部照舊運作。 */
(function () {
  if (window.__partsReal) return; window.__partsReal = true;
  var T = window.THREE; if (!T) return;

  /* ---------- 材質 ---------- */
  function std(o) { return new T.MeshStandardMaterial(o); }
  var M = {
    pcbBlack: std({ color: 0x121417, roughness: .62, metalness: .05 }),
    pcbDark: std({ color: 0x0d0f12, roughness: .58, metalness: .05 }),
    pcbGreen: std({ color: 0x16512f, roughness: .55, metalness: .06 }),
    epoxy: std({ color: 0x0f1013, roughness: .42, metalness: .08 }),
    epoxyTop: std({ color: 0x1a1c20, roughness: .4, metalness: .08 }),
    gold: std({ color: 0xd8b45c, roughness: .3, metalness: 1.0 }),
    silver: std({ color: 0xcfd6dc, roughness: .3, metalness: .95 }),
    steel: std({ color: 0x9aa2a9, roughness: .38, metalness: .9 }),
    nickel: std({ color: 0xb6bec6, roughness: .32, metalness: .95 }),
    glass: std({ color: 0x04060b, roughness: .07, metalness: .3 }),
    glow: std({ color: 0x0a1a2e, roughness: .25, emissive: 0x2f7fd0, emissiveIntensity: .55 }),
    gloss: std({ color: 0x0a0c10, roughness: .12, metalness: .2 }),
    wireRed: std({ color: 0xb3312a, roughness: .7 }),
    wireBlack: std({ color: 0x15161a, roughness: .7 }),
    lipo: std({ color: 0x2b3f6e, roughness: .38, metalness: .55 }),
    lipoSilver: std({ color: 0xb9c0c7, roughness: .35, metalness: .8 }),
    dot: std({ color: 0xe8e8ea, roughness: .5 }),
    blue: std({ color: 0x2b6cff, roughness: .35, metalness: .3 })
  };

  /* ---------- 絲印貼圖（畫布即時繪製，放大不糊） ---------- */
  function silkTex(lines, opt) {
    opt = opt || {};
    var W = opt.w || 512, H = opt.h || 256;
    var c = document.createElement('canvas'); c.width = W; c.height = H;
    var x = c.getContext('2d');
    if (opt.bg !== null) { x.fillStyle = opt.bg || '#121417'; x.fillRect(0, 0, W, H); }
    x.fillStyle = opt.fg || '#e9edf2';
    x.textAlign = opt.align || 'left';
    x.textBaseline = 'middle';
    var fs = opt.fs || 30, y0 = opt.y0 || H * 0.32, gap = opt.gap || fs * 1.5;
    lines.forEach(function (t, i) {
      var bold = t.indexOf('*') === 0;
      x.font = (bold ? '700 ' : '500 ') + (bold ? fs * 1.15 : fs) + 'px ui-monospace,Menlo,monospace';
      x.fillText(bold ? t.slice(1) : t, opt.align === 'center' ? W / 2 : 26, y0 + i * gap);
    });
    var tx = new T.CanvasTexture(c);
    tx.anisotropy = 4;
    return tx;
  }

  function silkMat(lines, opt) {
    var t = silkTex(lines, opt);
    return std({ map: t, roughness: .55, metalness: .05 });
  }

  /* ---------- 小工具 ---------- */
  function box(w, h, d, mat) { return new T.Mesh(new T.BoxGeometry(w, h, d), mat); }
  function cyl(rt, rb, h, seg, mat) { return new T.Mesh(new T.CylinderGeometry(rt, rb, h, seg || 24), mat); }
  function plate(w, h, d, mat, r) {           // 帶倒角的扁平件（用縮放方塊近似）
    var m = box(w, h, d, mat); return m;
  }
  function at(m, x, y, z) { m.position.set(x, y, z); return m; }

  /* 一顆貼片元件（電阻/電容） */
  function smd(w, h, bodyMat) {
    var g = new T.Group();
    g.add(at(box(w, h, .3, bodyMat || M.epoxyTop), 0, 0, .15));
    g.add(at(box(w * 1.25, h * .38, .12, M.silver), 0, h * .31, .06));
    g.add(at(box(w * 1.25, h * .38, .12, M.silver), 0, -h * .31, .06));
    return g;
  }

  /* 一排排針 / 半孔（金色） */
  function pinRow(n, pitch, w, h, z) {
    var g = new T.Group();
    for (var i = 0; i < n; i++) {
      var p = box(w, h, .25, M.gold);
      p.position.set((i - (n - 1) / 2) * pitch, 0, z);
      g.add(p);
    }
    return g;
  }

  /* ---------- 各零件 ---------- */
  var R = {};

  /* XIAO ESP32S3 — 21 × 17.8 × 1.2：黑 PCB ＋ 金屬屏蔽罩 ＋ 兩排半孔 ＋ 貼片 ＋ 絲印 */
  R.XIAO_ESP32S3 = function (w, h, d) {
    var g = new T.Group();
    var t = d;                                   // 板厚（z 方向）
    g.add(at(box(w, h, t, M.pcbBlack), 0, 0, 0));
    // 絲印（貼在 +z 面）
    var lab = new T.Mesh(new T.PlaneGeometry(w * .52, w * .26), silkMat(
      ['XIAO', '*ESP32S3'], { w: 512, h: 256, bg: null, fg: '#dfe6ee', fs: 48, gap: 62, y0: 78 }));
    lab.position.set(-w * .22, h * .22, t / 2 + .03); g.add(lab);
    // 金屬屏蔽罩（模組）
    var shield = at(box(w * .33, h * .42, t + .55, M.silver), -w * .27, h * .06, t / 2 + .25);
    g.add(shield);
    g.add(at(box(w * .30, h * .36, .1, M.steel), -w * .27, h * .06, t / 2 + .53));   // 罩上平面
    // 天線區（陶瓷天線）
    g.add(at(box(w * .2, h * .16, t + .3, M.epoxyTop), w * .3, h * .36, t / 2 + .12));
    // 半孔（兩側各 7 個，金色）
    g.add(at(pinRow(7, w * .105, w * .045, .55, 0), 0, 0, 0).translateY(h / 2 - .2).translateX(w * .02));
    var pr2 = pinRow(7, w * .105, w * .045, .55, 0);
    pr2.position.set(w * .02, -h / 2 + .2, 0); g.add(pr2);
    // 貼片元件
    var xs = [-.36, -.22, .02, .12, .3, .42], ys = [-.34, -.14, .16, .38];
    var i = 0;
    xs.forEach(function (px) { ys.forEach(function (py) {
      if ((i++ % 3) === 0) { var s = smd(w * .055, h * .07); s.position.set(w * px, h * py, t / 2 + .15); g.add(s); }
    }); });
    // USB-C 座（在 +x 邊）
    var usb = new T.Group();
    usb.add(at(box(.5, h * .34, t + .9, M.silver), 0, 0, 0));
    usb.add(at(box(.3, h * .22, t + .5, M.pcbDark), .12, 0, 0));
    usb.position.set(w / 2 + .25, 0, t / 2 + .3); g.add(usb);
    // 底部焊墊
    g.add(at(box(w * .9, h * .9, .06, M.gold), 0, 0, -t / 2 - .03));
    return g;
  };

  /* USB-C 連接器 — 8.9 × 7.3 × 3.2：不鏽鋼外殼 ＋ 內舌片 ＋ 外框彈片 */
  R.USB_C = function (w, h, d) {
    var g = new T.Group();
    g.add(at(box(w, h, d, M.silver), 0, 0, 0));
    // 橢圓插口（內凹）
    var hole = cyl(h * .30, h * .30, d * .92, 24, M.pcbDark);
    hole.rotation.x = Math.PI / 2; hole.scale.set(w / (h * .6), 1, 1);
    g.add(at(hole, 0, 0, d * .06));
    // 內舌片
    g.add(at(box(w * .55, h * .2, d * .6, M.epoxy), 0, 0, d * .05));
    // 端子（金色細排）
    var pins = pinRow(9, w * .075, w * .03, h * .1, 0);
    pins.rotation.z = Math.PI / 2; pins.position.set(0, 0, d * .05); g.add(pins);
    // 外框彈片
    g.add(at(box(w * .96, .18, d * .55, M.steel), 0, h * .52, 0));
    g.add(at(box(w * .96, .18, d * .55, M.steel), 0, -h * .52, 0));
    // 接腳（往下 4 支）
    g.add(at(box(w * .08, h * .22, .3, M.gold), -w * .3, -h * .62, -d * .42));
    g.add(at(box(w * .08, h * .22, .3, M.gold), w * .3, -h * .62, -d * .42));
    return g;
  };

  /* INMP441 麥克風 — 4.7 × 3.8 × 1.0：黑色 LGA ＋ 進音孔 ＋ 底部金色焊盤 */
  R.INMP441_IC = function (w, h, d) {
    var g = new T.Group();
    g.add(at(box(w, h, d, M.epoxy), 0, 0, 0));
    g.add(at(box(w * .96, h * .96, .08, M.epoxyTop), 0, 0, d / 2 + .02));   // 頂面
    // 進音孔
    var port = cyl(.26, .26, d * .6, 20, M.pcbDark);
    port.rotation.x = Math.PI / 2; port.position.set(-w * .16, -h * .12, d / 2 - .05); g.add(port);
    g.add(at(cyl(.32, .32, .06, 20, M.silver), -w * .16, -h * .12, d / 2 + .05)).rotation.x = Math.PI / 2;
    // 絲印
    var lab = new T.Mesh(new T.PlaneGeometry(w * .5, h * .3), silkMat(
      ['*INMP441'], { w: 256, h: 128, bg: null, fg: '#cfd6dd', fs: 40, y0: 66 }));
    lab.position.set(w * .16, h * .22, d / 2 + .035); g.add(lab);
    // 腳位 1 記號
    g.add(at(cyl(.1, .1, .04, 12, M.dot), -w / 2 + .22, h / 2 - .22, d / 2 + .035)).rotation.x = Math.PI / 2;
    // 底部 9 焊盤
    for (var i = 0; i < 3; i++) for (var j = 0; j < 3; j++)
      g.add(at(box(w * .22, h * .22, .06, M.gold), (i - 1) * w * .3, (j - 1) * h * .3, -d / 2 - .03));
    return g;
  };

  /* LSM6DS3TR-C IMU — 2.5 × 3.0 × 0.83 */
  R.LSM6DS3TR_C_IC = function (w, h, d) {
    var g = new T.Group();
    g.add(at(box(w, h, d, M.epoxy), 0, 0, 0));
    g.add(at(box(w * .94, h * .94, .06, M.epoxyTop), 0, 0, d / 2 + .02));
    var lab = new T.Mesh(new T.PlaneGeometry(w * .8, h * .3), silkMat(
      ['*6DS3'], { w: 256, h: 128, bg: null, fg: '#c9d1d8', fs: 42, y0: 64 }));
    lab.position.set(0, h * .18, d / 2 + .035); g.add(lab);
    g.add(at(cyl(.09, .09, .04, 12, M.dot), -w / 2 + .2, h / 2 - .2, d / 2 + .035)).rotation.x = Math.PI / 2;
    for (var i = 0; i < 4; i++) for (var j = 0; j < 3; j++)
      g.add(at(box(w * .16, h * .16, .05, M.gold), (i - 1.5) * w * .22, (j - 1) * h * .3, -d / 2 - .025));
    return g;
  };

  /* SSD1306 OLED 模組 — 27 × 27.3 × 1.6：綠 PCB ＋ 4 pin ＋ 電容 ＋ 排針 */
  R.OLED_096in = R['OLED_0.96in'] = function (w, h, d) {
    var g = new T.Group();
    g.add(at(box(w, h, d, M.pcbGreen), 0, 0, 0));
    // 白色絲印框與文字
    var lab = new T.Mesh(new T.PlaneGeometry(w * .8, h * .22), silkMat(
      ['*0.96" OLED', 'SSD1306 I2C 0x3C'], { w: 512, h: 200, bg: null, fg: '#eef2f6', fs: 40, gap: 54, y0: 62 }));
    lab.position.set(0, -h * .34, d / 2 + .03); g.add(lab);
    // 上方 4 pin 排針（金色針腳 ＋ 黑塑膠座）
    var hdr = new T.Group();
    hdr.add(at(box(w * .52, h * .1, .5, M.pcbDark), 0, 0, 0));
    hdr.add(at(pinRow(4, w * .12, .18, .5, .3), 0, 0, .3));
    hdr.position.set(0, h * .36, d / 2 + .25); g.add(hdr);
    // 貼片元件
    g.add(at(smd(w * .1, h * .06), -w * .34, h * .16, d / 2 + .15));
    g.add(at(smd(w * .07, h * .05), w * .33, h * .1, d / 2 + .15));
    g.add(at(box(w * .16, h * .12, .5, M.epoxyTop), w * .3, h * .22, d / 2 + .25));  // 電荷泵 IC
    // 底部焊盤
    g.add(at(box(w * .9, h * .9, .05, M.gold), 0, 0, -d / 2 - .02));
    return g;
  };

  /* OLED 玻璃面板 — 26 × 19.3 × 2.4：深色玻璃 ＋ 發光像素 ＋ 金屬外框 */
  R.OLED_glass = function (w, h, d) {
    var g = new T.Group();
    g.add(at(box(w, h, d * .82, M.glass), 0, 0, 0));
    // 外框
    var f = M.steel;
    g.add(at(box(w, .16, d * .9, f), 0, h / 2 - .08, 0));
    g.add(at(box(w, .16, d * .9, f), 0, -h / 2 + .08, 0));
    g.add(at(box(.16, h, d * .9, f), w / 2 - .08, 0, 0));
    g.add(at(box(.16, h, d * .9, f), -w / 2 + .08, 0, 0));
    // 發光顯示區（藍白）
    var view = new T.Mesh(new T.PlaneGeometry(w * .86, h * .74), M.glow);
    view.position.set(0, 0, d * .42); g.add(view);
    // 顯示內容示意（白字）
    var txt = new T.Mesh(new T.PlaneGeometry(w * .7, h * .45), silkMat(
      ['• READY', ' 128×64'], { w: 512, h: 256, bg: null, fg: '#dff0ff', fs: 40, gap: 56, y0: 110 }));
    txt.position.set(0, 0, d * .43); g.add(txt);
    return g;
  };

  /* 鋰電池 500mAh — 40 × 25 × 6：鋁箔包 ＋ 標籤 ＋ 保護板 ＋ 紅黑線 */
  R['LiPo_~500mAh'] = R.LiPo_500mAh = function (w, h, d) {
    var g = new T.Group();
    var body = box(w, h, d, M.lipoSilver);
    g.add(body);
    // 標籤（藍底白字）
    var lab = new T.Mesh(new T.PlaneGeometry(w * .82, h * .62), silkMat(
      ['*LiPo 3.7V', '500mAh  •  保護板'], { w: 512, h: 256, bg: '#1f3260', fg: '#dfe8ff', fs: 42, gap: 62, y0: 92, align: 'center' }));
    lab.position.set(0, 0, d / 2 + .03); g.add(lab);
    // 封邊（側面壓紋）
    g.add(at(box(w * .99, h * .04, d * 1.02, M.lipoSilver), 0, h * .3, 0));
    g.add(at(box(w * .99, h * .04, d * 1.02, M.lipoSilver), 0, -h * .3, 0));
    // 保護板（小電路板）
    g.add(at(box(w * .3, h * .5, .35, M.pcbDark), w * .06, -h * .22, d / 2 + .2));
    g.add(at(smd(w * .08, h * .1), w * .02, -h * .22, d / 2 + .42));
    // 紅黑線（出線）
    var wr = cyl(.14, .14, h * .5, 12, M.wireRed); wr.rotation.z = Math.PI / 2;
    wr.position.set(w * .34, -h * .12, d / 2 + .2); g.add(wr);
    var wb = cyl(.14, .14, h * .5, 12, M.wireBlack); wb.rotation.z = Math.PI / 2;
    wb.position.set(w * .34, -h * .3, d / 2 + .2); g.add(wb);
    return g;
  };

  /* 震動馬達 — ⌀10 × 3.4：金屬外殼 ＋ 偏心錘 ＋ 出線 */
  R.Vibration_motor = function (w, h, d) {
    var g = new T.Group();
    var body = cyl(w / 2, w / 2, d * .62, 32, M.nickel);
    body.rotation.x = Math.PI / 2; g.add(body);
    // 端蓋
    var cap = cyl(w / 2 * .96, w / 2 * .96, .12, 32, M.steel);
    cap.rotation.x = Math.PI / 2; cap.position.z = d * .31; g.add(cap);
    // 偏心錘（半圓）
    var wt = cyl(w * .42, w * .42, d * .3, 24, M.steel);
    wt.rotation.x = Math.PI / 2; wt.position.set(w * .12, 0, d * .45); g.add(wt);
    // 軸
    var sh = cyl(.22, .22, d * .3, 12, M.silver);
    sh.rotation.x = Math.PI / 2; sh.position.set(w * .12, 0, d * .3); g.add(sh);
    // 出線
    var w1 = cyl(.15, .15, w * .5, 10, M.wireRed); w1.rotation.z = Math.PI / 2;
    w1.position.set(-w * .6, d * .1, 0); g.add(w1);
    var w2 = cyl(.15, .15, w * .5, 10, M.wireBlack); w2.rotation.z = Math.PI / 2;
    w2.position.set(-w * .6, -d * .1, 0); g.add(w2);
    return g;
  };

  /* 釹磁鐵 ⌀5 × 2：鎳層亮面 ＋ 倒角 */
  R.Magnet_5x2 = function (w, h, d) {
    var g = new T.Group();
    var b = cyl(w / 2, w / 2, d, 32, M.nickel); b.rotation.x = Math.PI / 2; g.add(b);
    var b2 = cyl(w / 2 * .96, w / 2 * .96, d * 1.02, 32, M.silver); b2.rotation.x = Math.PI / 2; g.add(b2);
    return g;
  };

  /* pogo pin ⌀1.5 × 5：黃銅管 ＋ 鍍金凸頭 ＋ 彈簧段 */
  R.Pogo_pin = function (w, h, d) {
    var g = new T.Group();
    var barrel = cyl(w / 2, w / 2, d * .62, 20, M.gold);
    barrel.rotation.x = Math.PI / 2; barrel.position.z = -d * .1; g.add(barrel);
    // 彈簧段（細環）
    for (var i = 0; i < 4; i++) {
      var rin = cyl(w / 2 * .86, w / 2 * .86, .06, 20, M.steel);
      rin.rotation.x = Math.PI / 2; rin.position.z = -d * .3 + i * .16; g.add(rin);
    }
    var tip = cyl(w / 2 * .55, w / 2 * .82, d * .28, 20, M.gold);
    tip.rotation.x = Math.PI / 2; tip.position.z = d * .34; g.add(tip);
    var head = cyl(w / 2 * .5, w / 2 * .5, .1, 16, M.silver);
    head.rotation.x = Math.PI / 2; head.position.z = d * .49; g.add(head);
    return g;
  };

  /* ---------- 套用到場景 ---------- */
  var NAMES = Object.keys(R);

  function findScenes() {
    var out = [];
    function push(v) { if (v && v.isScene && out.indexOf(v) < 0) out.push(v); }
    ['scene', '__scene', 'mainScene', 'SCENE', 'world'].forEach(function (k) { try { push(window[k]); } catch (e) {} });
    // 保險：掃描所有全域變數找 Scene（頁面把 scene 包在 IIFE 裡時也找得到）
    try { for (var k in window) { try { push(window[k]); } catch (e) {} } } catch (e) {}
    return out;
  }

  function realify(root) {
    var done = 0;
    var scenes = root ? [root] : findScenes();
    var targets = [];
    scenes.forEach(function (s) { if (s.traverse) s.traverse(function (o) { if (o.isMesh) targets.push(o); }); });
    targets.forEach(function (m) {
      var base = m.name;
      if (!base || !R[base] || m.userData.__real) return;
      var bb = new T.Box3().setFromObject(m);
      var s = bb.getSize(new T.Vector3());
      var c = bb.getCenter(new T.Vector3());
      if (s.x < 0.01 || s.y < 0.01 || s.z < 0.01) return;      // 尺寸讀不到就跳過
      var parts = R[base](s.x, s.y, s.z);
      parts.name = base + '__real';
      var parent = m.parent || scenes[0];
      var localC = parent.worldToLocal ? parent.worldToLocal(c.clone()) : c;
      parts.position.copy(localC);
      parts.quaternion.copy(m.quaternion);
      parent.add(parts);
      m.userData.__real = true;
      // 原方塊改全透明（點選 / 射線 / 尺寸標註照舊）
      var mats = Array.isArray(m.material) ? m.material : [m.material];
      mats.forEach(function (mm) {
        if (!mm) return;
        mm.transparent = true; mm.opacity = 0; mm.depthWrite = false;
        if (mm.color) mm.color.setHex(0xffffff);
        mm.needsUpdate = true;
      });
      done++;
    });
    if (done && window.console) console.log('[parts-real] 已仿真化 ' + done + ' 個零件');
    return done;
  }
  window.realifyParts = realify;

  // 自動套用：等模型載入後掃描（最多等 60 秒）
  var tries = 0;
  var iv = setInterval(function () {
    tries++;
    var n = realify();
    if (n) { clearInterval(iv); window.__partsRealDone = true; }
    if (tries > 120) clearInterval(iv);
  }, 500);
})();
