/* qfn-build.js v2 — 寫實 QFN-48（6.0 × 6.0 × 0.85 mm，JEDEC MO-220 風格）
   v2 重點：
   ・焊墊與側壁改用 InstancedMesh（繪製次數 388 → 12，手機才跑得動）
   ・刻字貼圖只產生一次（共用）
   ・建構失敗時退回簡單方塊，頁面絕不會空白
   尺寸完全依原頁標示，不改比例。 */
(function () {
  if (!window.THREE) { console.warn('[qfn] 需要 THREE'); return; }
  var T = window.THREE;
  var _tex = null;

  function markingTexture() {
    if (_tex) return _tex;
    var W = 1024, c = document.createElement('canvas');
    c.width = c.height = W;
    var x = c.getContext('2d');
    x.fillStyle = '#0b0c0f'; x.fillRect(0, 0, W, W);
    var g = x.createRadialGradient(W * 0.4, W * 0.35, W * 0.05, W * 0.5, W * 0.5, W * 0.78);
    g.addColorStop(0, 'rgba(52,56,64,0.16)');
    g.addColorStop(1, 'rgba(0,0,0,0)');
    x.fillStyle = g; x.fillRect(0, 0, W, W);
    x.textAlign = 'center'; x.textBaseline = 'middle';
    x.fillStyle = 'rgba(198,205,214,0.88)';
    x.font = '700 150px ui-monospace,Menlo,monospace';
    x.fillText('QFN48', W * 0.5, W * 0.40);
    x.font = '500 72px ui-monospace,Menlo,monospace';
    x.fillStyle = 'rgba(160,168,180,0.8)';
    x.fillText('6×6  MO-220', W * 0.5, W * 0.55);
    x.font = '500 60px ui-monospace,Menlo,monospace';
    x.fillStyle = 'rgba(140,148,160,0.7)';
    x.fillText('2601  TW', W * 0.5, W * 0.66);
    x.strokeStyle = 'rgba(140,148,160,0.5)'; x.lineWidth = 7;
    x.beginPath(); x.arc(W * 0.22, W * 0.20, 44, 0, Math.PI * 2); x.stroke();
    x.beginPath(); x.moveTo(W * 0.22 - 25, W * 0.20); x.lineTo(W * 0.22 + 25, W * 0.20); x.stroke();
    _tex = new T.CanvasTexture(c);
    _tex.anisotropy = 4;
    return _tex;
  }

  function fallbackBox(S, H) {
    var m = new T.Mesh(new T.BoxGeometry(S, H, S),
      new T.MeshStandardMaterial({ color: 0x0b0c0f, roughness: 0.62, metalness: 0.05 }));
    m.position.y = H / 2; m.name = 'QFN48_real';
    return m;
  }

  window.buildQFN48 = function (opt) {
    opt = opt || {};
    var S = opt.size || 6.0, H = opt.height || 0.85;
    var PINS = 12, PITCH = S / PINS;          // 0.5 mm
    try {
      var g = new T.Group();
      g.name = 'QFN48_real';

      var tex = markingTexture();
      var mBody = new T.MeshStandardMaterial({ map: tex, roughness: 0.62, metalness: 0.05, envMapIntensity: 0.22 });
      var mSide = new T.MeshStandardMaterial({ color: 0x07080a, roughness: 0.74, metalness: 0.03, envMapIntensity: 0.18 });
      var mGold = new T.MeshStandardMaterial({ color: 0xd8b45c, roughness: 0.26, metalness: 1.0 });
      var mGoldDull = new T.MeshStandardMaterial({ color: 0xb9994c, roughness: 0.38, metalness: 1.0 });

      // ── 本體 ──
      var body = new T.Mesh(new T.BoxGeometry(S, H, S),
        [mSide, mSide, mBody, mSide, mSide, mSide]);   // +x,-x,頂,-y,+z,-z
      body.position.y = H / 2; g.add(body);

      // ── 48 焊墊（2 個 InstancedMesh：x 向 24 個、z 向 24 個）──
      var padW = PITCH * 0.55, padD = 0.25, padH = 0.016;
      var padGeoX = new T.BoxGeometry(padD, padH, padW);
      var padGeoZ = new T.BoxGeometry(padW, padH, padD);
      var padsX = new T.InstancedMesh(padGeoX, mGold, PINS * 2);
      var padsZ = new T.InstancedMesh(padGeoZ, mGold, PINS * 2);
      var wallGeoX = new T.BoxGeometry(0.012, H * 0.34, padW * 0.92);
      var wallGeoZ = new T.BoxGeometry(padW * 0.92, H * 0.34, 0.012);
      var wallsX = new T.InstancedMesh(wallGeoX, mGoldDull, PINS * 2);
      var wallsZ = new T.InstancedMesh(wallGeoZ, mGoldDull, PINS * 2);
      var mx = new T.Matrix4(), ix = 0, iz = 0, wx = 0, wz = 0;
      var hw = S / 2, wy = H * 0.17, wOff = hw - 0.004, y0 = padH / 2 + 0.001;

      for (var i = 0; i < PINS; i++) {
        var t = (i - (PINS - 1) / 2) * PITCH;
        // x 向兩側
        mx.makeTranslation(hw - padD / 2, y0, t); padsX.setMatrixAt(ix++, mx);
        mx.makeTranslation(-hw + padD / 2, y0, t); padsX.setMatrixAt(ix++, mx);
        mx.makeTranslation(wOff, wy, t); wallsX.setMatrixAt(wx++, mx);
        mx.makeTranslation(-wOff, wy, t); wallsX.setMatrixAt(wx++, mx);
        // z 向兩側
        mx.makeTranslation(t, y0, hw - padD / 2); padsZ.setMatrixAt(iz++, mx);
        mx.makeTranslation(t, y0, -hw + padD / 2); padsZ.setMatrixAt(iz++, mx);
        mx.makeTranslation(t, wy, wOff); wallsZ.setMatrixAt(wz++, mx);
        mx.makeTranslation(t, wy, -wOff); wallsZ.setMatrixAt(wz++, mx);
      }
      padsX.instanceMatrix.needsUpdate = true; padsZ.instanceMatrix.needsUpdate = true;
      wallsX.instanceMatrix.needsUpdate = true; wallsZ.instanceMatrix.needsUpdate = true;
      g.add(padsX, padsZ, wallsX, wallsZ);

      // ── 外露散熱墊 ──
      var ep = new T.Mesh(new T.BoxGeometry(4.2, 0.012, 4.2), mGold);
      ep.position.y = 0.008; g.add(ep);

      // ── pin-1 凹點 ──
      var dot = new T.Mesh(new T.CylinderGeometry(0.11, 0.09, 0.03, 16), mSide);
      dot.position.set(-hw + 0.42, H - 0.004, -hw + 0.42); g.add(dot);

      g.userData.meshCount = 1 + 4 + 1 + 1;   // 本體＋4 instanced＋散熱墊＋凹點
      return g;
    } catch (e) {
      console.warn('[qfn] 建構失敗，退回簡單方塊：', e && e.message);
      return fallbackBox(S, H);
    }
  };
})();
