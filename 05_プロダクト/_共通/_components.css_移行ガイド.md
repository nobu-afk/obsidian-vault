# components.css 移行ガイド（260429 確定）

> **目的：** 12 LP に散在する Hero/CTA/Card の重複 CSS を `_共通/components.css` に集約する移行手順
> **作成：** 2026-04-29
> **配布先：** `https://growthfix.jp/assets/css/components.css`
> **基本方針：** 既存 LP は壊さない・新規要素から段階的に移行

---

## 段階的移行戦略

**新規 LP を作る時：** components.css をベースに `gf-` prefix のクラスで構築
**既存 LP：** 大型改修時のみ移行・小さな変更で書き換えはしない（破壊リスク）

---

## 新規 LP 用テンプレート

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{LP タイトル}</title>
  <meta name="description" content="{説明}">
  <meta property="og:title" content="{LP タイトル}">
  <meta property="og:description" content="{説明}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://growthfix.jp/{path}/">
  <meta property="og:image" content="https://growthfix.jp/gravity/ogp.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://growthfix.jp/gravity/ogp.png">

  <!-- 共通基盤 -->
  <link rel="stylesheet" href="https://growthfix.jp/assets/css/components.css?v=20260429a">
  <link rel="stylesheet" href="https://growthfix.jp/assets/css/mobile.css?v=20260428c">

  <!-- 計測・テスト・告知 -->
  <script src="https://growthfix.jp/assets/js/tracking.js" defer></script>
  <script src="https://growthfix.jp/assets/js/ab-test.js?v=20260429a" defer></script>
  <script src="https://growthfix.jp/assets/js/seminar-bar.js?v=20260429a" defer></script>
</head>
<body>
  <!-- HERO -->
  <section class="gf-hero">
    <div class="gf-hero-inner">
      <p class="gf-hero-eyebrow">サブタイトル</p>
      <h1 class="gf-hero-title">タイトル</h1>
      <p class="gf-hero-sub">説明文</p>
      <div class="gf-hero-meta">
        <span class="gf-hero-badge">価格</span>
        <span class="gf-hero-badge">期間</span>
      </div>
      <a class="gf-btn gf-btn-primary gf-btn-lg" href="#apply" data-event-cta="hero-cta">申し込む</a>
    </div>
  </section>

  <!-- セクション -->
  <section class="gf-section">
    <div class="gf-section-inner">
      <span class="gf-section-label">SECTION LABEL</span>
      <h2 class="gf-section-title">セクションタイトル</h2>
      <p class="gf-section-lead">リード文</p>

      <!-- カードグリッド -->
      <div class="gf-grid gf-grid-3">
        <div class="gf-card">
          <span class="gf-card-eyebrow">EYEBROW</span>
          <h3 class="gf-card-title">カードタイトル</h3>
          <p class="gf-card-desc">説明文</p>
        </div>
        <!-- ... -->
      </div>
    </div>
  </section>
</body>
</html>
```

---

## 既存 LP の段階移行（オプショナル・大型改修時のみ）

### Phase 1：新規追加要素のみ gf- クラス利用

例：既存 LP に新セクションを追加する時、その部分だけ `gf-` クラスで実装。古いセクションには触らない。

### Phase 2：HERO セクションの段階置換

各 LP の HERO は典型的に：
```html
<!-- 旧 -->
<section class="bp-v2-hero">
  <div class="container-narrow">
    <p class="hero-eyebrow" style="...">設計の参謀</p>
    <h1>...</h1>
    ...
  </div>
</section>
```

を以下に置換可能：
```html
<!-- 新 -->
<section class="gf-hero">
  <div class="gf-hero-inner">
    <p class="gf-hero-eyebrow">設計の参謀</p>
    <h1 class="gf-hero-title">...</h1>
    ...
  </div>
</section>
```

**注意：** 既存 LP の固有 CSS（`bp-v2-hero` の独自スタイル）が衝突する可能性あり。ローカルで確認後に置換。

### Phase 3：CTA ボタンの統一

```html
<!-- 旧 -->
<a class="btn btn-primary btn-lg" href="...">

<!-- 新 -->
<a class="gf-btn gf-btn-primary gf-btn-lg" href="..." data-event-cta="hero-cta">
```

---

## クラス命名規則

| Prefix | 意図 |
|---|---|
| `gf-` | GrowthFix 共通コンポーネント（components.css）|
| `bp-v2-`, `shift-v2-`, `orbit-` | LP 固有コンポーネント（既存・触らない）|
| `next-seminar-bar` | 共通バー（seminar-bar.js が制御）|

**ルール：** `gf-` クラスは components.css の中だけで定義。LP 個別 CSS で `gf-` を override しない（衝突回避）。

---

## 計測連携

`gf-btn` を使う時は **必ず** `data-event-cta="..."` を付ける：

```html
<a class="gf-btn gf-btn-primary" href="..." data-event-cta="seminar-bar">申込</a>
```

`tracking.js` の自動 click 計測（260429 拡張）が GA4 に `cta_click` イベントを送信する。

---

## ベンチマーク（移行前後）

### 移行前（典型的な LP）
- HERO セクション CSS：30-50 行（LP ごとに独自）
- CTA ボタン：10-15 行（インラインスタイルあり）
- Card：20-30 行
- **合計：60-100 行/LP × 12 LP = 720-1200 行の重複**

### 移行後
- HERO/CTA/Card：components.css 1 ファイル（230 行）
- LP 個別 CSS：固有要素のみ（10-30 行）
- **削減：~700-900 行**

---

## 関連ファイル

- 本体 CSS：`05_プロダクト/_共通/components.css`
- 本体 mobile：`05_プロダクト/_共通/mobile.css`
- 雛形運用 memory：`feedback_lp_header_footer_template.md`
- LP 変更時チェックリスト：`05_プロダクト/_共通/_LP変更時_モバイル確認チェックリスト.md`

---

*作成: 2026-04-29 / 新規 LP は components.css ベース・既存 LP は大型改修時のみ移行*
