/**
 * GrowthFix 共通トラッキングスクリプト
 * GA4 + GTM + Meta Pixel を1ファイルで初期化
 *
 * 使い方:
 *   <script src="/assets/js/tracking.js" defer></script>
 *
 * 設置対象LP（URLは改名後も維持）:
 *   - https://growthfix.jp/gravity/            (Gravity TOP)
 *   - https://growthfix.jp/gravity-scan/       (Gravity Blueprint ※改名後もURLは gravity-scan)
 *   - https://growthfix.jp/gravity-shift/      (Gravity Shift)
 *   - https://growthfix.jp/gravity-orbit/      (Gravity Orbit)
 *   - https://growthfix.jp/gravity-coaching/   (Gravity Coaching)
 *   - https://growthfix.jp/gravity-code/       (Gravity CODE)
 *   - https://growthfix.jp/whitepaper/         (WhitePaper)
 *
 * 本番ID:
 *   - GA4: G-HZ5W5H4SYJ
 *   - GTM: GT-5D48K35Z
 *   - Meta Pixel: 3958421771147615
 *
 * 260420 メモ:
 *   - URLは改名後も維持（/gravity-scan/ → Blueprint 表示のまま）
 *   - GA4管理画面でのイベント名／CV名は別途手動更新要
 *     → `04_GrowthFix/01_サービス設計/260420_GA4_Blueprint改名チェックリスト.md` 参照
 */

(function () {
  'use strict';

  var GA4_ID = 'G-HZ5W5H4SYJ';
  var GTM_ID = 'GT-5D48K35Z';
  var META_PIXEL_ID = '3958421771147615';

  // --- GA4 + GTM (gtag.js) ---
  var gtagScript = document.createElement('script');
  gtagScript.async = true;
  gtagScript.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
  document.head.appendChild(gtagScript);

  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', GA4_ID);
  window.gtag('config', GTM_ID);

  // --- Meta Pixel ---
  !function (f, b, e, v, n, t, s) {
    if (f.fbq) return;
    n = f.fbq = function () {
      n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
    };
    if (!f._fbq) f._fbq = n;
    n.push = n;
    n.loaded = !0;
    n.version = '2.0';
    n.queue = [];
    t = b.createElement(e);
    t.async = !0;
    t.src = v;
    s = b.getElementsByTagName(e)[0];
    s.parentNode.insertBefore(t, s);
  }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');

  window.fbq('init', META_PIXEL_ID);
  window.fbq('track', 'PageView');

  // --- noscript 対応: Meta Pixel ---
  var noscriptImg = document.createElement('img');
  noscriptImg.height = 1;
  noscriptImg.width = 1;
  noscriptImg.style.display = 'none';
  noscriptImg.src = 'https://www.facebook.com/tr?id=' + META_PIXEL_ID + '&ev=PageView&noscript=1';
  noscriptImg.alt = '';
  var noscript = document.createElement('noscript');
  noscript.appendChild(noscriptImg);
  document.body && document.body.appendChild(noscript);
})();
