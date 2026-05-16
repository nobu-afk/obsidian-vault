/*!
 * GrowthFix Site Chrome (header / overlay / footer)
 * 全 HTML の共通 chrome を一箇所に集約。各ページの <body> 末尾に
 *   <script src="https://growthfix.jp/gravity/site-chrome.js" defer></script>
 * を置くだけで、header・overlay・footer が自動挿入される。
 * 共通CSSは site-chrome.css に分離（IDE/キャッシュ最適化・260425）
 * 更新時は js / css の対応するファイルを差し替えれば全ページに反映。
 */
(function () {
  'use strict';

  var STYLE_HREF = 'https://growthfix.jp/gravity/site-chrome.css?v=20260515f';
  var FOOTER_STYLE_HREF = 'https://growthfix.jp/gravity/site-chrome-footer.css?v=20260515e';

  var MAIL_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="12" viewBox="0 0 16 12" fill="none"><g clip-path="url(#clip0_0_116)"><path d="M15.5176 0H0.482376C0.35438 0.00018278 0.231688 0.0524685 0.141244 0.145374C0.0508 0.23828 -1.24026e-07 0.36421 0 0.495507L0 1.46974L8 6.96883L16 1.46905V0.495507C16 0.36421 15.9492 0.23828 15.8588 0.145374C15.7683 0.0524685 15.6456 0.00018278 15.5176 0Z" fill="white"/><path d="M5.21272e-08 3.50028V10.02C-5.88738e-05 10.2801 0.0498413 10.5376 0.146849 10.7779C0.243857 11.0182 0.38607 11.2365 0.565363 11.4204C0.744655 11.6043 0.957513 11.7501 1.19177 11.8495C1.42603 11.949 1.6771 12.0001 1.93062 12H14.0694C14.3229 12.0001 14.574 11.949 14.8082 11.8495C15.0425 11.7501 15.2553 11.6043 15.4346 11.4204C15.6139 11.2365 15.7561 11.0182 15.8532 10.7779C15.9502 10.5376 16.0001 10.2801 16 10.02V3.49959L8 8.99937L5.21272e-08 3.50028Z" fill="white"/></g><defs><clipPath id="clip0_0_116"><rect width="16" height="12" fill="white"/></clipPath></defs></svg>';

  var MAIL_SPAN = '<span class="d-flex">' + MAIL_SVG + '</span>';

  var OVERLAY =
    '<div class="menu-overlay">' +
      '<div class="overlay-links">' +
        '<div class="overlay-links__group">' +
          '<a href="https://growthfix.jp/profile" class="overlay-links__lead d-flex flex-center">代表者プロフィール</a>' +
          '<a target="_blank" rel="noopener noreferrer" href="https://growthfix.jp/gravity/" class="overlay-links__lead d-flex flex-center">サービス</a>' +
          '<a href="https://growthfix.jp/achievement" class="overlay-links__lead d-flex flex-center">事例・実績</a>' +
          '<a href="https://growthfix.jp/knowledge" class="overlay-links__lead d-flex flex-center">ナレッジ</a>' +
          '<a href="https://growthfix.jp/news" class="overlay-links__lead d-flex flex-center">お知らせ</a>' +
        '</div>' +
        '<div class="overlay-links__contact">' +
          '<a href="https://growthfix.jp/contact" class="l-header__contact">' +
            '<span>お問い合わせ</span>' + MAIL_SPAN +
          '</a>' +
        '</div>' +
      '</div>' +
    '</div>';

  var HEADER =
    '<div class="header d-flex flex-row align-center flex-between">' +
      '<a href="https://growthfix.jp/" class="header-logo"><span class="header-logo__text">GrowthFix</span></a>' +
      '<ul class="link d-flex flex-row align-center">' +
        '<li><a href="https://growthfix.jp/profile" class="link_btn"><span>代表者プロフィール</span></a></li>' +
        '<li><a target="_blank" rel="noopener noreferrer" href="https://growthfix.jp/gravity/" class="link_btn"><span>サービス</span></a></li>' +
        '<li><a href="https://growthfix.jp/achievement" class="link_btn"><span>事例・実績</span></a></li>' +
        '<li><a href="https://growthfix.jp/knowledge" class="link_btn"><span>ナレッジ</span></a></li>' +
        '<li><a href="https://growthfix.jp/news" class="link_btn"><span>お知らせ</span></a></li>' +
        '<li>' +
          '<a href="https://growthfix.jp/contact" class="link_contact d-flex flex-row">' +
            '<span>お問い合わせ</span>' + MAIL_SPAN +
          '</a>' +
        '</li>' +
      '</ul>' +
    '</div>';

  // SP用ハンバーガー（body直下に独立配置：ancestor干渉を完全回避）
  var SP_MENU =
    '<div class="sp-menu" style="position:fixed;top:14px;right:14px;z-index:99999;cursor:pointer;padding:10px;background:rgba(255,255,255,0.92);border-radius:4px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">' +
      '<div class="sp-menu-item">' +
        '<span style="display:block;width:24px;height:2px;background:#0f172a;margin:0 0 5px;border-bottom:none;"></span>' +
        '<span style="display:block;width:24px;height:2px;background:#0f172a;margin:0 0 5px;border-bottom:none;"></span>' +
        '<span style="display:block;width:24px;height:2px;background:#0f172a;margin:0;border-bottom:none;"></span>' +
      '</div>' +
    '</div>';

  var FOOTER =
    '<footer class="b-footer">' +
      '<div class="container b-footer-inner">' +
        '<div class="b-brand">GrowthFix<br>' +
          '<span class="b-footer-tagline">優秀人材が集まり、躍動する会社をつくる。</span><br>' +
          '<span class="b-footer-tagline-sub">組織に、引力を。</span>' +
        '</div>' +
        '<div class="b-footer-profile">' +
          '<p class="b-footer-profile-name"><strong>石井伸幸</strong> ── 組織の引力設計者 ／ 引力の参謀</p>' +
          '<p class="b-footer-profile-desc">人事16年（DMM50事業／MOON-X 30→120人）× プロコーチ（MCA 2期）× Claude Code開発実装（AIで、チーム8人分の仕事を1人で回している・2026年4月実績）</p>' +
          '<p class="b-footer-profile-link"><a href="https://growthfix.jp/profile/">プロフィール詳細 →</a></p>' +
        '</div>' +
        '<div class="b-footer-links">' +
          '<div class="b-footer-col">' +
            '<p class="b-footer-col-label">個人軸</p>' +
            '<a href="https://growthfix.jp/gravity/code/">Gravity CODE</a>' +
            '<a href="https://growthfix.jp/gravity/coaching/">Gravity Coaching</a>' +
          '</div>' +
          '<div class="b-footer-col">' +
            '<p class="b-footer-col-label">組織軸</p>' +
            '<a href="https://growthfix.jp/gravity/">組織の引力設計プログラム</a>' +
            '<a href="https://growthfix.jp/gravity/diagnose/">無料 Web 診断（18 問 3 分）</a>' +
          '</div>' +
          '<div class="b-footer-col">' +
            '<p class="b-footer-col-label">会社・サイト</p>' +
            '<a href="https://growthfix.jp/">運営会社</a>' +
            '<a href="https://growthfix.jp/profile/">プロフィール</a>' +
            '<a href="https://growthfix.jp/contact/">お問い合わせ</a>' +
          '</div>' +
          '<div class="b-footer-col">' +
            '<p class="b-footer-col-label">リソース・規約</p>' +
            '<a href="https://growthfix.jp/whitepaper/">WhitePaper</a>' +
            '<a href="https://growthfix.jp/citations/">学術ベース（主要参考文献）</a>' +
            '<a href="https://growthfix.jp/privacy-policy/">プライバシーポリシー</a>' +
          '</div>' +
        '</div>' +
        '<div class="b-footer-copy">&copy; 2026 GrowthFix. All rights reserved.</div>' +
      '</div>' +
    '</footer>';

  // 260503 footer-only モード追加：data-mode="footer" 属性で footer のみ注入
  // - コーポレート系（top/service/profile/news/achievement/whitepaper-optin/knowledge/privacy/contact）：full chrome（header + overlay + sp-menu + footer）
  // - LP 系（Gravity hub + 各 Gravity LP）：footer-only（独自 header 維持）
  function getMode() {
    var script = document.currentScript || document.querySelector('script[src*="site-chrome.js"]');
    return script && script.getAttribute('data-mode') === 'footer' ? 'footer' : 'full';
  }

  function loadStylesheet(href) {
    if (document.querySelector('link[href="' + href + '"]')) return;
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = href;
    document.head.appendChild(link);
  }

  function mount() {
    var mode = getMode();
    // footer-only モード（LP 系）：site-chrome-footer.css のみ読み込み（LP 既存 CSS 非干渉）
    if (mode === 'footer') {
      loadStylesheet(FOOTER_STYLE_HREF);
      document.body.insertAdjacentHTML('beforeend', FOOTER);
      return;
    }
    // full モード（コーポレート系）：site-chrome.css 読み込み + header / overlay / sp-menu / footer 全注入
    // 260515 追加：footer は LP 系と完全同期させるため site-chrome-footer.css も読み込む（後勝ち優先）
    loadStylesheet(STYLE_HREF);
    loadStylesheet(FOOTER_STYLE_HREF);
    document.body.insertAdjacentHTML('afterbegin', OVERLAY + HEADER);
    document.body.insertAdjacentHTML('beforeend', FOOTER + SP_MENU);

    // ハンバーガーメニュートグル（WPテーマの.changeクラスでスライドイン）
    var hamburger = document.querySelector('.sp-menu-item');
    var overlay = document.querySelector('.menu-overlay');
    if (hamburger && overlay) {
      var setOpen = function (open) {
        // 同状態なら no-op（無駄なclassList書き換え＋body styleタッチを防ぐ）
        if (overlay.classList.contains('change') === open) return;
        overlay.classList.toggle('change', open);
        hamburger.classList.toggle('change', open);
        document.body.style.overflow = open ? 'hidden' : '';
      };
      hamburger.addEventListener('click', function (e) {
        e.stopPropagation();
        setOpen(!overlay.classList.contains('change'));
      });
      overlay.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', function () { setOpen(false); });
      });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') setOpen(false);
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount);
  } else {
    mount();
  }
})();
