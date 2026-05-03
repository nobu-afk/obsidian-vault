/* ============================================================
   GrowthFix LIVE WEBINAR バー（共通注入スクリプト）
   配置: https://growthfix.jp/assets/js/seminar-bar.js
   役割: 全LP上部にセミナー告知バーを動的に挿入
   特徴:
     - 日付ベースの自動撤去（締切後は表示されない）
     - 設定変更は本ファイル1箇所のみ（旧来は19LP編集が必要だった）
     - defer 読込で render-blocking なし
   更新履歴:
     - 2026-04-29: 初版（19LPのインライン版から JS 化）
   ============================================================ */
(function () {
  'use strict';

  // ============================================================
  // セミナー設定（次回開催情報・ここを変えるだけで全LPに反映）
  // ============================================================
  // 260503 取り下げ：5/15 セミナーをリスケ（5/8 長谷さんモニター + 各 LP ブラッシュアップ集中のため）
  //                 設定値は次回開催時の編集起点として保持・enabled: true に戻すだけで再表示
  var SEMINAR = {
    enabled: false,                                   // 260503 取り下げ（次回開催時 true に戻す）
    deadline: '2026-05-15T13:00:00+09:00',            // この時刻を過ぎたら自動非表示（12-13時開催・260430修正）
    badge: 'LIVE WEBINAR',                            // 赤バッジ文字
    date: '5/15 金 12:00-13:00',                      // 黄色日時表記
    titlePrefix: 'AI 時代こそ、',                     // タイトル前半
    titleHighlight: '採用に強い会社',                 // 黄色強調
    titleSuffix: 'だけが生き残る。',                  // タイトル後半
    cta: '無料 ／ 申込はこちら ▶',                   // CTA バッジ文言（A 案・デフォルト）
    url: 'https://growthfix.jp/seminar/acting/'       // 申込先 URL
  };

  // ============================================================
  // A/B テスト：CTA 文言バリアント（?variant=A|B|C で切替）
  // window.ABTest が読み込まれていれば自動適用、なければデフォルト（A）
  // ============================================================
  var CTA_VARIANTS = {
    A: SEMINAR.cta,                            // デフォルト：無料 ／ 申込はこちら ▶
    B: '今すぐ無料登録 →',                     // B 案：行動誘導型
    C: '残席わずか ／ 無料申込 ▶'              // C 案：希少性訴求
  };

  function getCTA() {
    if (window.ABTest && typeof window.ABTest.text === 'function') {
      return window.ABTest.text(CTA_VARIANTS, 'seminar-bar-cta');
    }
    return SEMINAR.cta;
  }

  // ============================================================
  // 表示判定（無効化 or 締切超過なら何もしない）
  // ============================================================
  if (!SEMINAR.enabled) return;
  try {
    if (new Date() > new Date(SEMINAR.deadline)) return;
  } catch (e) {
    // 日付パース失敗時は安全側に倒して非表示
    return;
  }

  // ============================================================
  // HTML 構築（インラインスタイルで CSS 依存ゼロ・mobile.css で SP 最適化）
  // ============================================================
  var ctaText = getCTA();

  // ============================================================
  // 自前 CSS を <head> に注入（DOM API で確実に動作・全ルール !important）
  // .next-seminar-bar 既存ルール（mobile.css）と整合・最優先
  // ============================================================
  var cssText =
    /* PC・基本スタイル */
    '.gf-sbar{background:#0a0f1e!important;color:#fff!important;padding:14px 16px!important;text-align:center!important;border-bottom:1px solid #1e293b!important;}' +
    '.gf-sbar__link{color:#fff!important;text-decoration:none!important;display:inline-block!important;max-width:980px!important;font-size:13px!important;letter-spacing:0.04em!important;line-height:1.7!important;}' +
    '.gf-sbar__badge{display:inline-block!important;padding:3px 10px!important;background:#ef4444!important;color:#fff!important;font-size:11px!important;font-weight:700!important;letter-spacing:0.12em!important;border-radius:3px!important;margin-right:10px!important;vertical-align:middle!important;}' +
    '.gf-sbar__date{color:#fbbf24!important;font-weight:800!important;}' +
    '.gf-sbar__sep{margin:0 8px!important;color:#475569!important;}' +
    '.gf-sbar__title em{color:#fbbf24!important;font-style:normal!important;}' +
    '.gf-sbar__cta{display:inline-block!important;margin-left:10px!important;padding:4px 12px!important;background:#fbbf24!important;color:#0f172a!important;font-size:12px!important;font-weight:800!important;border-radius:3px!important;}' +
    /* モバイル最適化（768px 以下）*/
    '@media(max-width:768px){' +
      '.gf-sbar{padding:10px 12px!important;}' +
      '.gf-sbar__link{font-size:11.5px!important;line-height:1.55!important;letter-spacing:0.01em!important;}' +
      '.gf-sbar__badge{font-size:9.5px!important;padding:2px 6px!important;margin-right:5px!important;letter-spacing:0.08em!important;}' +
      '.gf-sbar__date{font-size:12px!important;}' +
      '.gf-sbar__sep{display:none!important;}' +
      '.gf-sbar__title{display:block!important;margin-top:4px!important;font-size:11.5px!important;}' +
      '.gf-sbar__cta{display:inline-block!important;margin-top:6px!important;margin-left:0!important;font-size:11px!important;padding:4px 10px!important;}' +
    '}' +
    /* 極小画面（375px 以下）*/
    '@media(max-width:375px){' +
      '.gf-sbar{padding:8px 10px!important;}' +
      '.gf-sbar__link{font-size:11px!important;}' +
      '.gf-sbar__date{font-size:11.5px!important;}' +
      '.gf-sbar__title{font-size:11px!important;}' +
      '.gf-sbar__cta{font-size:10.5px!important;padding:3px 9px!important;}' +
    '}';

  // <head> に <style> を確実に注入（既存があれば上書き）
  function injectStyle() {
    var existing = document.getElementById('next-seminar-bar-style');
    if (existing) existing.parentNode.removeChild(existing);
    var styleEl = document.createElement('style');
    styleEl.id = 'next-seminar-bar-style';
    styleEl.textContent = cssText;
    (document.head || document.documentElement).appendChild(styleEl);
  }

  var html =
    '<section class="next-seminar-bar gf-sbar">' +
      '<a class="gf-sbar__link" href="' + SEMINAR.url + '" data-event-cta="seminar-bar">' +
        '<span class="gf-sbar__badge">' + SEMINAR.badge + '</span>' +
        '<strong class="gf-sbar__date">' + SEMINAR.date + '</strong>' +
        '<span class="gf-sbar__sep">／</span>' +
        '<span class="gf-sbar__title">' + SEMINAR.titlePrefix + '<em>' + SEMINAR.titleHighlight + '</em>' + SEMINAR.titleSuffix + '</span>' +
        '<span class="gf-sbar__cta">' + ctaText + '</span>' +
      '</a>' +
    '</section>';

  // ============================================================
  // body 先頭に挿入（既に存在していたら何もしない＝多重挿入防止）
  // ============================================================
  function insert() {
    if (!document.body) return;
    if (document.querySelector('.next-seminar-bar')) return;
    injectStyle();  // <head> に <style> を先に注入
    document.body.insertAdjacentHTML('afterbegin', html);
  }

  if (document.body) {
    insert();
  } else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', insert);
  } else {
    insert();
  }
})();
