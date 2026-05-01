# 共通ヘッダー/フッター雛形（260416固定）

Gravityシリーズ7LPのheader/footer統一の雛形です。
タグライン・サービスリンク・著作権表記に変更が入る際は、**必ず本フォルダの雛形を先に更新し、その後7LPへ展開**してください。

## 2系統の雛形

1. **`site-header_template.html` / `site-footer_template.html`**
   個別LP（CODE / Scan / Scan DEEP / Coaching / Shift / Orbit）用。6LP共通。

2. **`b-header_template.html` / `b-footer_template.html`**
   シリーズハブLP（Gravity）専用。命名系統が個別LPと異なるため別雛形。

## プレースホルダ規約

テンプレート内の `{{...}}` は各LPで置換する変数です。

| 変数 | 例 | 備考 |
|---|---|---|
| `{{PRODUCT_NAME}}` | `Gravity Code` / `Gravity Scan` / `Gravity Scan DEEP` 等 | ロゴテキスト |
| `{{LOGO_HREF}}` | `#` or `https://growthfix.jp/` | CODEは`#main`等、LPにより差 |
| `{{NAV_ITEMS}}` | `<a href="#deliverable">成果物</a>...` | 3-4個 |
| `{{MOBILE_NAV_ITEMS}}` | 同上 + CTA | `<a class="btn btn-primary">申し込む</a>`込み |
| `{{CTA_LABEL}}` | `申し込む` / `体験する` / `診断する` | ハブは`診断する` |
| `{{CTA_ANCHOR}}` | `#apply` / `#trial` | |
| `{{PRODUCT_SLUG}}` | `gravity-code` 等 | footer-current 判定用 |

## 運用ルール

- **3ファイル以上触る規模のタグライン・footer構造変更は雛形から着手**
- **1LPだけの暫定修正は雛形に反映しない**（差分リスト欄に記録）
- 差分リストは `260416_差分リスト.md` を参照
