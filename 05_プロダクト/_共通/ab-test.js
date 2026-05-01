/* ============================================================
   GrowthFix A/B テストフレームワーク
   配置: https://growthfix.jp/assets/js/ab-test.js
   方式: UTM パラメータ駆動式（決定論的・ランダム配分なし）
   使い方:
     [URL]
       ?variant=A   → バリアント A
       ?variant=B   → バリアント B
       無指定        → A（デフォルト）

     [HTML 宣言式]
       <a data-ab-test="seminar-cta"
          data-ab-a="無料 ／ 申込はこちら ▶"
          data-ab-b="今すぐ申し込む →"
          data-ab-c="残席わずか・無料登録">
         無料 ／ 申込はこちら ▶
       </a>

     [JS プログラマティック]
       const text = window.ABTest.text({A:'...', B:'...', C:'...'});

   GA4 計測:
     gtag('event', 'ab_test_view', { test_name, variant })

   更新履歴:
     - 2026-04-29: 初版
   ============================================================ */
(function () {
  'use strict';

  // ============================================================
  // バリアント決定（URL 優先・sessionStorage 保持・デフォルト A）
  // ============================================================
  function getVariant() {
    try {
      var params = new URLSearchParams(window.location.search);
      var v = params.get('variant');
      if (v && /^[A-Z]$/.test(v.toUpperCase())) {
        var upper = v.toUpperCase();
        try { sessionStorage.setItem('gf_ab_variant', upper); } catch (e) {}
        return upper;
      }
      // セッションに保存されたバリアントがあればそれを使う（同セッション内で一貫性）
      try {
        var stored = sessionStorage.getItem('gf_ab_variant');
        if (stored && /^[A-Z]$/.test(stored)) return stored;
      } catch (e) {}
    } catch (e) {}
    return 'A';
  }

  var variant = getVariant();
  var trackedTests = {}; // 同一テストの重複送信を防止

  // ============================================================
  // GA4 イベント送信（gtag があれば）
  // ============================================================
  function track(testName) {
    if (trackedTests[testName]) return;
    trackedTests[testName] = true;
    try {
      if (typeof window.gtag === 'function') {
        window.gtag('event', 'ab_test_view', {
          test_name: testName,
          variant: variant
        });
      }
    } catch (e) {}
  }

  // ============================================================
  // グローバル API
  // ============================================================
  window.ABTest = {
    variant: variant,

    /**
     * バリアント別テキストを取得
     * @param {Object} config - { A: '...', B: '...', C: '...' }
     * @param {string} [testName] - GA4 計測用のテスト名（省略可）
     * @returns {string}
     */
    text: function (config, testName) {
      if (testName) track(testName);
      return config[variant] || config['A'] || '';
    },

    /**
     * GA4 イベントを明示的に送信
     */
    track: track,

    /**
     * 現在のバリアントを返す
     */
    get: function () { return variant; }
  };

  // ============================================================
  // DOM 走査：data-ab-test 属性を持つ要素のテキストを自動置換
  // ============================================================
  function applyDOMVariants() {
    var elements = document.querySelectorAll('[data-ab-test]');
    elements.forEach(function (el) {
      var testName = el.getAttribute('data-ab-test');
      if (!testName) return;

      var config = {};
      ['A', 'B', 'C', 'D', 'E'].forEach(function (v) {
        var attr = el.getAttribute('data-ab-' + v.toLowerCase());
        if (attr !== null) config[v] = attr;
      });

      var text = window.ABTest.text(config, testName);
      if (text) {
        // 子要素を持たない場合のみ textContent で安全に書き換え
        if (el.children.length === 0) {
          el.textContent = text;
        } else {
          // HTML を含む可能性があれば innerHTML（要注意）
          el.innerHTML = text;
        }
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyDOMVariants);
  } else {
    applyDOMVariants();
  }
})();
