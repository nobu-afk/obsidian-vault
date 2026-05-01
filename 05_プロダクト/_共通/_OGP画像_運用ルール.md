# OGP 画像 運用ルール（260429 確定）

> **目的：** 19 LP の OGP 画像参照を一元管理。SNS シェア時のサムネイル品質を保つ
> **作成：** 2026-04-29
> **発火条件：** 新規 LP 追加・既存 LP の OGP 画像差し替え時

---

## 現行運用（260429 時点）

### 既存 OGP 画像（実在・全て HTTP 200）

| URL | 用途 |
|---|---|
| `https://growthfix.jp/gravity/ogp.png` | **デフォルト・汎用フォールバック**（Gravity ブランド共通）|
| `https://growthfix.jp/gravity-code/ogp.png` | CODE LP・CODE Executive 診断 |
| `https://growthfix.jp/gravity-coaching/ogp.png` | Coaching LP |
| `https://growthfix.jp/gravity-orbit/ogp.png` | Orbit LP |

### 廃止・存在しない画像（参照禁止）

| URL | 状態 |
|---|---|
| `/gravity-blueprint/ogp.png` | ❌ 404（→ `/gravity/ogp.png` 利用）|
| `/gravity-shift/og-image.jpg` | ❌ 404（→ `/gravity/ogp.png` 利用）|
| `/ogp.png`（ルート）| ❌ 404 |

---

## 新規 LP 追加時のルール

1. **専用 OGP 画像を作る場合：** `/{service-path}/ogp.png` として配置
2. **作らない場合（推奨）：** `/gravity/ogp.png` を fallback として参照

```html
<meta property="og:image" content="https://growthfix.jp/gravity/ogp.png" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:image" content="https://growthfix.jp/gravity/ogp.png" />
```

---

## OGP 画像差し替え時の手順

### 1. ローカルで新画像を作成

- 推奨サイズ：1200 × 630（OG 標準）
- フォーマット：PNG
- ファイルサイズ：5MB 以下

### 2. FTP デプロイ

```bash
curl -T <local-image-path> \
  "ftp://sv16489.xserver.jp/growthfix.jp/public_html/{service-path}/ogp.png" \
  --user "xs992119:${FTP_PASS}"
```

### 3. キャッシュ更新

OGP 画像は外部キャッシュ（Facebook/X）が長く効く。差し替え時は以下：
- Facebook Sharing Debugger でキャッシュ更新：https://developers.facebook.com/tools/debug/
- Twitter Card Validator でキャッシュ更新：https://cards-dev.twitter.com/validator

---

## 19 LP の OGP 状態（260429 時点・全 HTTP 200）

| LP | og:image |
|---|---|
| top （/） | gravity/ogp.png（要確認）|
| /gravity/ | /gravity/ogp.png ✓ |
| /gravity-code/ | /gravity-code/ogp.png ✓ |
| /gravity-code/executive/ | /gravity-code/ogp.png（260429 追加）|
| /gravity-blueprint/ | /gravity/ogp.png（260429 修正）|
| /gravity-blueprint/diagnose/ | /gravity/ogp.png（260429 追加）|
| /gravity-coaching/ | /gravity-coaching/ogp.png ✓ |
| /gravity-shift/ | /gravity/ogp.png（260429 修正・既存は 404 だった）|
| /gravity-orbit/ | /gravity-orbit/ogp.png ✓ |
| /service/ | （要確認）|
| /profile/ | （要確認）|
| /achievement/ | （要確認）|
| /contact/ | /gravity/ogp.png（260429 追加）|
| /privacy-policy/ | /gravity/ogp.png（260429 追加）|
| /news/ | /gravity/ogp.png（260429 追加）|
| /news/site-renewal/ | （要確認）|
| /news/gravity-release/ | （要確認）|
| /knowledge/ | （要確認）|
| /whitepaper/ | （要確認）|

---

## 関連ファイル

- 新規 LP テンプレート（雛形運用）：memory `feedback_lp_header_footer_template.md`
- LP 変更時チェックリスト：`05_プロダクト/_共通/_LP変更時_モバイル確認チェックリスト.md`
- mobile.css 戦略：memory `reference_mobile_css_strategy.md`

---

*作成: 2026-04-29 / OGP 画像の単一情報源・新規 LP 追加時の必須参照*
