/* qfn-build.js — 寫實 QFN-48 封裝（6.0 × 6.0 × 0.85 mm，JEDEC MO-220 風格）
   取代原本 466 頂點的低模方塊：
   ・黑色塑封本體（微亮面）＋ 雷射刻字（canvas 貼圖：QFN48／批號／pin-1 記號）
   ・48 個鍍金焊墊（0.5 mm pitch，底面）＋ 側壁露銅（無腳封裝的真實特徵）
   ・4.2 × 4.2 mm 外露散熱墊（底面，微凹）
   ・pin-1 角落凹點
   尺寸完全依原頁標示，不改比例。 */
(function () {
  if (!window.THREE) { console.warn('[qfn] 需要 THREE'); return; }
  var T = window.THREE;

  function markingTexture() {
    var W = 1024, c = document.createElement('canvas');
    c.width = c.height = W;
    var x = c.getContext('2d');
    // 塑封膠底（黑，帶一點不均勻）
    x.fillStyle = '#0d0e11'; x.fillRect(0, 0, W, W);
    var g = x.createRadialGradient(W * 0.4, W * 0.35, W * 0.05, W * 0.5, W * 0.5, W * 0.75);
    g.addColorStop(0, 'rgba(60,64,72,0.18)');
    g.addColorStop(1, 'rgba(0,0,0,0)');
    x.fillStyle = g; x.fillRect(0, 0, W, W);
    // 雷射刻字（灰白、邊緣略糊）
    x.textAlign = 'center'; x.textBaseline = 'middle';
    x.fillStyle = 'rgba(206,212,220,0.92)';
    x.font = '700 150px ui-monospace,Menlo,monospace';
    x.fillText('QFN48', W * 0.5, W * 0.40);
    x.font = '500 74px ui-monospace,Menlo,monospace';
    x.fillStyle = 'rgba(170,178,190,0.85)';
    x.fillText('6×6  MO-220', W * 0.5, W * 0.55);
    x.font = '500 62px ui-monospace,Menlo,monospace';
    x.fillStyle = 'rgba(150,158,170,0.75)';
    x.fillText('2601  TW', W * 0.5, W * 0.66);
    // 左上的小廠標（抽象）
    x.strokeStyle = 'rgba(150,158,170,0.55)'; x.lineWidth = 7;
    x.beginPath(); x.arc(W * 0.22, W * 0.20, 46, 0, Math.PI * 2); x.stroke();
    x.beginPath(); x.moveTo(W * 0.22 - 26, W * 0.20); x.lineTo(W * 0.22 + 26, W * 0.20); x.stroke();
    var tex = new T.CanvasTexture(c);
    tex.anisotropy = 8;
    return tex;
  }

  window.buildQFN48 = function (opt) {
    opt = opt || {};
    var S = opt.size || 6.0;        // 本體邊長 mm
    var H = opt.height || 0.85;     // 本體厚度
    var PINS = 12;                  // 每邊 12 支 → 48
    var PITCH = S / PINS;           // 0.5 mm
    var g = new T.Group();
    g.name = 'QFN48_real';

    // ── 材質 ──
    var mBody = new T.MeshStandardMaterial({
      map: markingTexture(), color: 0xffffff, roughness: 0.62, metalness: 0.05, envMapIntensity: 0.2
    });
    var mSide = new T.MeshStandardMaterial({ color: 0x07080a, roughness: 0.74, metalness: 0.03, envMapIntensity: 0.18 });
    var mGold = new T.MeshStandardMaterial({ color: 0xd8b45c, roughness: 0.26, metalness: 1.0 });
    var mGoldDull = new T.MeshStandardMaterial({ color: 0xb9994c, roughness: 0.38, metalness: 1.0 });
    var mMask = new T.MeshStandardMaterial({ color: 0x0a0b0e, roughness: 0.68, metalness: 0.04, envMapIntensity: 0.18 });

    // ── 本體（上蓋帶刻字）──
    var bodyMats = [mSide, mSide, mBody, mMask, mSide, mSide]; // +x,-x,+y(頂),-y(底),+z,-z
    var body = new T.Mesh(new T.BoxGeometry(S, H, S), bodyMats);
    body.position.y = H / 2;
    g.add(body);

    // 上蓋薄薄一層（讓刻字更清楚、邊緣有倒角感）
    var cap = new T.Mesh(new T.BoxGeometry(S * 0.985, 0.012, S * 0.985),
      new T.MeshStandardMaterial({ map: markingTexture(), roughness: 0.5, metalness: 0.05 }));
    cap.position.y = H + 0.006;
    g.add(cap);

    // ── 48 個焊墊（底面）＋ 側壁露銅 ──
    var padW = PITCH * 0.55;      // 焊墊寬
    var padD = 0.25;              // 往內延伸
    var padH = 0.016;             // 厚度（貼底但不與散熱墊重疊）
    for (var i = 0; i < PINS; i++) {
      var t = (i - (PINS - 1) / 2) * PITCH;
      // 四邊：+x / -x / +z / -z
      var sides = [
        { pos: [S / 2 - padD / 2, padH / 2, t], size: [padD, padH, padW], face: [0, t] },   // +x
        { pos: [-S / 2 + padD / 2, padH / 2, t], size: [padD, padH, padW], face: [1, t] },  // -x
        { pos: [t, padH / 2, S / 2 - padD / 2], size: [padW, padH, padD], face: [2, t] },   // +z
        { pos: [t, padH / 2, -S / 2 + padD / 2], size: [padW, padH, padD], face: [3, t] }   // -z
      ];
      sides.forEach(function (sd) {
        var pad = new T.Mesh(new T.BoxGeometry(sd.size[0], sd.size[1], sd.size[2]), mGold);
        pad.position.set(sd.pos[0], sd.pos[1] + 0.002, sd.pos[2]);
        g.add(pad);
        // 側壁露銅（無腳封裝的關鍵特徵）
        var wall = new T.Mesh(new T.BoxGeometry(
          sd.face[0] < 2 ? 0.012 : padW * 0.92,
          H * 0.34,
          sd.face[0] < 2 ? padW * 0.92 : 0.012), mGoldDull);
        var hw = S / 2 - 0.004;
        var y = H * 0.17;
        if (sd.face[0] === 0) wall.position.set(hw, y, sd.face[1]);
        if (sd.face[0] === 1) wall.position.set(-hw, y, sd.face[1]);
        if (sd.face[0] === 2) wall.position.set(sd.face[1], y, hw);
        if (sd.face[0] === 3) wall.position.set(sd.face[1], y, -hw);
        g.add(wall);
      });
    }

    // ── 外露散熱墊（4.2 × 4.2，微凹）──
    var ep = new T.Mesh(new T.BoxGeometry(4.2, 0.012, 4.2), mGold);
    ep.position.y = 0.0125;
    g.add(ep);

    // ── pin-1 凹點（左上角）──
    var dot = new T.Mesh(new T.CylinderGeometry(0.11, 0.09, 0.03, 20), mSide);
    dot.position.set(-S / 2 + 0.42, H - 0.004, -S / 2 + 0.42);
    g.add(dot);

    return g;
  };
})();
