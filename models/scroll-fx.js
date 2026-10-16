/* scroll-fx.js — 3D 模型庫網站共用「滾動特效」層
   ・頂部滾動進度條
   ・[data-reveal] 元素進入畫面時淡入上移（可用 data-reveal-delay 微調）
   ・[data-parallax="0.2"] 元素隨滾動位移（正=往下慢、負=往上快）
   ・首頁若有 #hero3d 會回報進度給 window.__heroProgress
   設計原則：純 DOM/CSS、不碰各頁的 three.js，任何頁面都可安全載入（無效果時自動略過）。 */
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
    function measure() {
      maxScroll = Math.max(1, document.documentElement.scrollHeight - innerHeight);
    }

    // ② 淡入
    var items = [].slice.call(document.querySelectorAll('[data-reveal]'));
    items.forEach(function (el) {
      el.style.opacity = 0;
      el.style.transform = 'translateY(28px)';
      el.style.transition = 'opacity .75s cubic-bezier(.2,.7,.3,1), transform .75s cubic-bezier(.2,.7,.3,1)';
    });
    var io = ('IntersectionObserver' in window) ? new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var d = parseInt(e.target.getAttribute('data-reveal-delay') || '0', 10);
        setTimeout(function () {
          e.target.style.opacity = 1;
          e.target.style.transform = 'translateY(0)';
        }, d);
        io.unobserve(e.target);
      });
    }, { threshold: 0.16, rootMargin: '0px 0px -8% 0px' }) : null;
    if (io) items.forEach(function (el) { io.observe(el); });
    else items.forEach(function (el) { el.style.opacity = 1; el.style.transform = 'none'; });

    // ③ 視差
    var px = [].slice.call(document.querySelectorAll('[data-parallax]')).map(function (el) {
      return { el: el, k: parseFloat(el.getAttribute('data-parallax')) || 0.15 };
    });

    var ticking = false, progress = 0;
    function onScroll() {
      progress = Math.max(0, Math.min(1, scrollY / maxScroll));
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(render);
      }
    }
    function render() {
      ticking = false;
      bar.style.width = (progress * 100).toFixed(2) + '%';
      window.__heroProgress = progress;
      if (px.length && !reduce) {
        for (var i = 0; i < px.length; i++) {
          var p = px[i];
          var r = p.el.getBoundingClientRect();
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
