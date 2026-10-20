/* scroll-fx.js — 3D 模型庫網站共用「滾動特效」層（v2：安全版）
   ・頂部滾動進度條
   ・[data-reveal] 元素進入畫面時淡入（data-reveal-delay 可錯開）
   ・[data-parallax="0.2"] 元素隨滾動位移
   ・首頁若有 3D 場景，會把滾動進度寫到 window.__heroProgress
   安全原則（重要）：內容一律預設可見。只有「這支 JS 真的執行到」才會加上 .sfx-ready
   去隱藏待淡入元素；JS 載入失敗、被擋、有例外 → 內容完全不受影響。
   另外 1.5s／3s 兩道保險，確保動畫沒觸發時內容一定會出現。 */
(function () {
  if (window.__scrollFx) return; window.__scrollFx = true;
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    // ① 進度條
    var bar = document.createElement('div');
    bar.id = 'sfxBar';
    bar.style.cssText = 'position:fixed;top:0;left:0;height:3px;width:0;z-index:99999;' +
      'background:linear-gradient(90deg,#e8734a,#ffb27a);box-shadow:0 0 10px rgba(232,115,74,.6);' +
      'transition:width .08s linear;pointer-events:none';
    document.body.appendChild(bar);

    var maxScroll = 1;
    function measure() { maxScroll = Math.max(1, document.documentElement.scrollHeight - innerHeight); }

    // ② 淡入（CSS 由這支 JS 注入；沒跑到這裡就完全不會隱藏內容）
    var items = [].slice.call(document.querySelectorAll('[data-reveal]'));
    if (items.length) {
      var st = document.createElement('style');
      st.textContent =
        '.sfx-ready [data-reveal]{opacity:0;transform:translateY(28px)}' +
        '.sfx-ready [data-reveal].sfx-in{opacity:1;transform:none;' +
        'transition:opacity .75s cubic-bezier(.2,.7,.3,1),transform .75s cubic-bezier(.2,.7,.3,1)}';
      document.head.appendChild(st);
      document.documentElement.classList.add('sfx-ready');

      var show = function (el) { el.classList.add('sfx-in'); };
      var showAll = function (inViewOnly) {
        var vh = innerHeight;
        items.forEach(function (el) {
          if (!inViewOnly) { show(el); return; }
          var r = el.getBoundingClientRect();
          if (r.top < vh * 0.95 && r.bottom > 0) show(el);
        });
      };

      if ('IntersectionObserver' in window && !reduce) {
        var io = new IntersectionObserver(function (es) {
          es.forEach(function (e) {
            if (!e.isIntersecting) return;
            var d = parseInt(e.target.getAttribute('data-reveal-delay') || '0', 10);
            setTimeout(function () { show(e.target); }, d);
            io.unobserve(e.target);
          });
        }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
        items.forEach(function (el) { io.observe(el); });
      } else {
        items.forEach(show);
      }
      setTimeout(function () { showAll(true); }, 1500);   // 保險一：畫面內的一定顯示
      setTimeout(function () { showAll(false); }, 3000);  // 保險二：全部顯示
    }

    // ③ 視差
    var px = [].slice.call(document.querySelectorAll('[data-parallax]')).map(function (el) {
      return { el: el, k: parseFloat(el.getAttribute('data-parallax')) || 0.15 };
    });

    var ticking = false, progress = 0;
    function onScroll() {
      progress = Math.max(0, Math.min(1, scrollY / maxScroll));
      if (!ticking) { ticking = true; requestAnimationFrame(render); }
    }
    function render() {
      ticking = false;
      bar.style.width = (progress * 100).toFixed(2) + '%';
      window.__heroProgress = progress;
      if (px.length && !reduce) {
        for (var i = 0; i < px.length; i++) {
          var p = px[i], r = p.el.getBoundingClientRect();
          var center = r.top + r.height / 2 - innerHeight / 2;
          p.el.style.transform = 'translate3d(0,' + (-center * p.k).toFixed(1) + 'px,0)';
        }
      }
    }
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', function () { measure(); onScroll(); });
    measure(); onScroll();
  });
})();
