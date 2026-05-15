# 営業資料マスター 限定公開（260515 8 ページピボット §7）

> **位置づけ**：260515 8 ページピボット仕様書 §7 の「営業資料 HTML 限定公開」実装。商談時に提案書として利用する内部参考値（料金・WBS・提供物リスト）含む完全版資料を、URL ハッシュ秘匿 + noindex で限定公開する装置。
>
> **作成日**：2026-05-15（260515）
> **編集権限**：石井のみ（業務委託は閲覧のみ）

---

## 📁 ディレクトリ構造

```
sales_本番/
├── _README.md                    ← 本ファイル
├── master/                       ← 編集場所（SSOT）
│   ├── index.html                ← 営業資料マスター v0.1（10 セクション）
│   ├── styles.css                ← A4 印刷想定 + モバイル対応
│   ├── .htaccess                 ← Options -Indexes + X-Robots-Tag noindex
│   └── assets/                   ← 画像・追加 CSS（v1.0 以降）
└── pdf/                          ← ビルド成果物
    └── YYMMDD_営業資料_v{VER}.pdf  ← 商談配布用 PDF
```

---

## 🔐 限定公開メカニズム

### URL ハッシュ秘匿
- 本番 URL：`https://growthfix.jp/sales/master-{HASH}/`
- 現行ハッシュ：`a896fc2ead339724`（16 hex chars = 2^64 ≈ 1.8×10^19 通り）
- 推測攻撃には実用上不可能な空間
- ハッシュ生成：`python3 -c "import secrets; print(secrets.token_hex(8))"`

### 三重防御
1. **URL ハッシュ秘匿**：直接 URL を知らない限りアクセス不可
2. **HTML `<meta name="robots" content="noindex,nofollow,noarchive,nosnippet">`**：検索エンジン拒否
3. **HTTP `X-Robots-Tag` ヘッダー**（.htaccess 経由）：HTTP レベルで強制
4. **`Options -Indexes`**（.htaccess）：ディレクトリリスト禁止
5. **`Cache-Control: private, no-cache`**：プロキシキャッシュ禁止
6. **sitemap.xml に含めない**：自動クロール拒否

### deploy.sh Layer 4 ガード（260515 追加）
- **ガード 5**：sales_本番/ 配下を `sales/master-{HASH}/` 以外に送る試行を BLOCK
- **ガード 6**：sales_本番/ 配下以外のファイルを `sales/master-{HASH}/` に送る試行を BLOCK

---

## 🚀 運用フロー

### 編集 → ビルド → デプロイ

```bash
cd "/Users/ishiinobuyuki/Documents/Obsidian Vault"

# 1. 編集（石井のみ）
# master/index.html を直接編集 → 個社事例・実証数値を追加

# 2. PDF ビルド（商談配布用）
bash 06_開発/scripts/sales/build_sales_pdf.sh 1.0
# → pdf/260515_営業資料_v1.0.pdf 生成

# 3. オンライン限定公開（URL 共有用）
bash 06_開発/scripts/deploy/deploy.sh sales
# → https://growthfix.jp/sales/master-a896fc2ead339724/
```

### PDF ビルドツール（優先順位）
1. **Google Chrome ヘッドレス**（推奨・既定で利用可）
2. wkhtmltopdf（`brew install wkhtmltopdf`）
3. weasyprint（`pip3 install weasyprint`）

### ハッシュ rotation 運用（推奨：半年 1 回）
1. 新ハッシュ生成：`python3 -c "import secrets; print(secrets.token_hex(8))"`
2. `06_開発/scripts/deploy/deploy.sh` の `SALES_HASH` 変数を更新
3. デプロイ実行：`bash deploy.sh sales`
4. 旧 URL の本番ファイルを FTP で物理削除（手動・要慎重判断）
5. 既存商談相手には新 URL を再共有

---

## 📋 マスター構造（v0.1 → v1.0 への充実化指針）

### v0.1 骨格（260515 完成）
| ページ | 内容 | v0.1 ステータス |
|---|---|---|
| 1 表紙 | 「組織の引力設計プログラム」+ 提案日 | 骨格・提案先プレースホルダ |
| 2 課題提起 | SME 経営者の人事ペイン 5 つ | 5 ペイン定義済 |
| 3 GrowthFix のポジション | PeopleX/識学/マルゴト人事 vs GrowthFix 4 軸 | 比較マトリクス |
| 4 3 軸 | 集まる × 躍動 × 留まる + 学術武装 | 軸 + 学術 cite |
| 5 WBS（3 ヶ月）| Week 1-12 ガントチャート | Phase + 主要マイルストーン |
| 6 提供物リスト | 12 要素 + 3 設計 + 月次レポート + AI Bot 3 体 | 全リスト |
| 7 投資レンジ | 最小/標準/フル 3 プラン | 月額参考値 |
| 8 継続フェーズ | 月 5 万 Orbit の中身 | 5 提供物 |
| 9 石井経歴 | 組織人事 16 年 + MCA 16 年 | 経歴 5 件 |
| 10 ご相談の流れ | 初回相談 → 診断 → 提案 → 契約 | 4 ステップ |

### v1.0 完成版への追加事項（石井編集）
- **§2 課題提起**：実際のクライアント事例（匿名）追加
- **§3 ポジション**：4 競合分析の最新数値（260511 競合分析 v1.0 由来）
- **§5 WBS**：実装事例の Week 別アウトプット写真・図表
- **§6 提供物**：HACHI / 操電フィールド検証で確証された装置の具体例
- **§7 投資レンジ**：個社事例の実 ROI 数値（守秘範囲で）
- **§9 石井経歴**：DMM HRBP 統括 / MOON-X 30→120 名 等の数値実績

---

## 🔗 関連ドキュメント

- 仕様書：`04_GrowthFix/02_マーケティング/260515_8pages_pivot_v1.0_仕様書.md` §7
- 引き継ぎ書：`04_GrowthFix/02_マーケティング/260515_8pages_pivot_引き継ぎ書_v1.0.md`
- SSOT 反映完走記録：`memory/project_8pages_pivot_ssot_reflection_260515.md`
- 競合分析 v1.0：`04_GrowthFix/02_マーケティング/260511_競合分析_v1.0.md`
- 営業プレイブック v1.0：`04_GrowthFix/00_営業/_営業プレイブック/260512_営業プレイブック_v1.0.md`
- フィールド検証：HACHI（`memory/project_hachi_field_validation_260511.md`）/ 操電（`memory/project_soden_field_validation_260512.md`）

---

## ⚠️ 編集時の注意事項

1. **本ファイル自体は本番に上げない**：sales_本番/ 直下の `_README.md` はローカルのみ・FTP デプロイ対象外
2. **master/ 配下のみ編集**：pdf/ はビルド成果物（編集不可）
3. **個人情報・詳細クライアント情報は注意**：限定公開とはいえ URL 流出リスクゼロではない。守秘範囲は明確に
4. **料金は内部参考値**：本資料の料金は商談時の参考値として扱い、個社最適化提案で柔軟に変更可
5. **ハッシュ流出時は即 rotation**：URL が想定外の場所（SNS / 漏洩メール等）で発見された場合、即座に新ハッシュへ移行
