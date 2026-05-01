/**
 * GrowthFix 共通トラッキングスクリプト
 * GA4 + GTM + Meta Pixel を1ファイルで初期化＋イベントハブ
 *
 * 使い方:
 *   <script src="/assets/js/tracking.js" defer></script>
 *
 * イベントハブ API（260429 拡張）:
 *   window.GrowthFixEvents.seminar_register({...})
 *   window.GrowthFixEvents.form_submit('contact', {...})
 *   window.GrowthFixEvents.cta_click('seminar-bar', {...})
 *   window.GrowthFixEvents.whitepaper_download({...})
 *   window.GrowthFixEvents.diagnose_complete('CODE', {...})
 *   window.GrowthFixEvents.custom('custom_event_name', {...})
 *
 * 自動計測（data-event-cta 属性）:
 *   <a href="..." data-event-cta="seminar-bar">申込</a>
 *   → click 時に GrowthFixEvents.cta_click('seminar-bar') が自動発火
 *
 * 本番ID:
 *   - GA4: G-HZ5W5H4SYJ
 *   - GTM: GT-5D48K35Z
 *   - Meta Pixel: 3958421771147615
 *
 * 更新履歴:
 *   - 2026-04-20: GA4管理画面でのイベント名／CV名は別途手動更新要
 *   - 2026-04-29: GrowthFixEvents 名前空間とdata-event-cta 自動計測を追加
 */

(function () {
  'use strict';

  var GA4_ID = 'G-HZ5W5H4SYJ';
  var GTM_ID = 'GT-5D48K35Z';
  var META_PIXEL_ID = '3958421771147615';

  // ============================================================
  // 1. GA4 + GTM (gtag.js) 初期化
  // ============================================================
  var gtagScript = document.createElement('script');
  gtagScript.async = true;
  gtagScript.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
  document.head.appendChild(gtagScript);

  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', GA4_ID);
  window.gtag('config', GTM_ID);

  // ============================================================
  // 2. Meta Pixel 初期化
  // ============================================================
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

  // noscript 対応: Meta Pixel
  var noscriptImg = document.createElement('img');
  noscriptImg.height = 1;
  noscriptImg.width = 1;
  noscriptImg.style.display = 'none';
  noscriptImg.src = 'https://www.facebook.com/tr?id=' + META_PIXEL_ID + '&ev=PageView&noscript=1';
  noscriptImg.alt = '';
  var noscript = document.createElement('noscript');
  noscript.appendChild(noscriptImg);
  if (document.body) {
    document.body.appendChild(noscript);
  } else {
    document.addEventListener('DOMContentLoaded', function () {
      document.body && document.body.appendChild(noscript);
    });
  }

  // ============================================================
  // 3. GrowthFixEvents 名前空間（イベントハブ）
  // ============================================================
  function safeGtag(eventName, params) {
    try {
      if (typeof window.gtag === 'function') {
        window.gtag('event', eventName, params || {});
      }
    } catch (e) {}
  }

  function safeFbq(action, eventName, params) {
    try {
      if (typeof window.fbq === 'function') {
        window.fbq(action, eventName, params || {});
      }
    } catch (e) {}
  }

  function getABVariant() {
    try {
      if (window.ABTest && typeof window.ABTest.get === 'function') {
        return window.ABTest.get();
      }
    } catch (e) {}
    return 'A';
  }

  // 全イベントに ab_variant を自動付与（A/B テスト連携）
  function withVariant(meta) {
    var payload = {};
    if (meta) for (var k in meta) payload[k] = meta[k];
    payload.ab_variant = getABVariant();
    return payload;
  }

  window.GrowthFixEvents = {
    /** セミナー登録完了（GA4 conversion 候補・Meta Lead） */
    seminar_register: function (meta) {
      var payload = withVariant(meta);
      safeGtag('seminar_register', payload);
      safeFbq('track', 'Lead', payload);
    },

    /** セミナーバー click（GA4 のみ・最終申込との関連を見るため） */
    seminar_bar_click: function (meta) {
      safeGtag('seminar_bar_click', withVariant(meta));
    },

    /** フォーム送信（contact/whitepaper/sales 等） */
    form_submit: function (formType, meta) {
      var payload = withVariant(meta);
      payload.form_type = formType;
      safeGtag('form_submit', payload);
      safeFbq('track', 'SubmitApplication', payload);
    },

    /** CTA クリック（個別 CTA の比較計測） */
    cta_click: function (ctaId, meta) {
      var payload = withVariant(meta);
      payload.cta_id = ctaId;
      safeGtag('cta_click', payload);
    },

    /** WhitePaper DL（GA4 conversion 候補・Meta Lead） */
    whitepaper_download: function (meta) {
      var payload = withVariant(meta);
      payload.content_name = 'whitepaper';
      safeGtag('whitepaper_download', payload);
      safeFbq('track', 'Lead', payload);
    },

    /** 診断完了（CODE/Blueprint）*/
    diagnose_complete: function (diagnoseType, meta) {
      var payload = withVariant(meta);
      payload.diagnose_type = diagnoseType;
      safeGtag('diagnose_complete', payload);
      safeFbq('track', 'CompleteRegistration', payload);
    },

    /** 汎用カスタムイベント（拡張用）*/
    custom: function (eventName, meta) {
      safeGtag(eventName, withVariant(meta));
    }
  };

  // ============================================================
  // 4. 自動 click 計測（data-event-cta 属性）
  // ============================================================
  function bindAutoClickTracking() {
    document.addEventListener('click', function (e) {
      var el = e.target;
      // data-event-cta を持つ親要素まで遡る
      while (el && el !== document.body) {
        if (el.hasAttribute && el.hasAttribute('data-event-cta')) {
          var ctaId = el.getAttribute('data-event-cta');
          var meta = {};
          if (el.tagName === 'A' && el.href) meta.href = el.href;
          window.GrowthFixEvents.cta_click(ctaId, meta);
          return;
        }
        el = el.parentNode;
      }
    }, true);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindAutoClickTracking);
  } else {
    bindAutoClickTracking();
  }
})();
