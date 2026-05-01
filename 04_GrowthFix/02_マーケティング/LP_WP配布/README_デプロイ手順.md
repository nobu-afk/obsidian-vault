# WP配布LP デプロイ手順（2026-04-14）

> **目的：** WP「事業の勝ち筋ループの作り方」を無料配布するLP
> **本番URL：** `https://growthfix.jp/whitepaper/`
> **ファイル：** `LP_WP配布/index.html`（single-file・CSS inline）

---

## デプロイ前の設定（2つ）

### 1. Utage申込フォーム連携

現状、form action の URL がプレースホルダーです：

```html
<form action="https://utage-system.com/r/YOUR_UTAGE_ID_HERE/store" method="post" target="utage-iframe" id="wp-form">
```

**手順：**
1. Utageにログイン
2. 新規商品作成：「事業の勝ち筋ループの作り方（WP無料配布）」
3. メール登録後の自動送信：PDF（whitepaper-v7.pdf）を添付
4. Utageの商品URLを取得
5. `YOUR_UTAGE_ID_HERE` を実際のURLに差し替え

**Utage商品の設定例：**
- 商品名：事業の勝ち筋ループの作り方（無料WP）
- 価格：0円
- 自動メール：登録後即時送信
- メール件名：「【GrowthFix】ホワイトペーパーのダウンロードリンクです」
- メール本文：PDFダウンロードリンク＋体験セッション案内

### 2. OGP画像の準備

```html
<meta property="og:image" content="https://growthfix.jp/whitepaper/ogp.png">
```

- サイズ：1200x630px
- 内容：WP表紙風のデザイン（タイトル＋サブタイトル＋GrowthFix）
- 黒背景・白文字でブランド統一
- ファイル名：`ogp.png`
- 配置先：`/whitepaper/ogp.png`

---

## FTPデプロイコマンド

### LP本体のアップロード

```bash
curl -T "/Users/ishiinobuyuki/Documents/Obsidian Vault/04_GrowthFix/02_マーケティング/LP_WP配布/index.html" \
  "ftp://sv16489.xserver.jp/growthfix.jp/public_html/whitepaper/index.html" \
  --user "xs992119:${FTP_PASS}" -s -w "index.html: %{http_code}\n"
```

※ `/whitepaper/` ディレクトリが存在しない場合、FTPが自動作成する or エラーになる。
自動作成されない場合は、FTPクライアントで事前にディレクトリ作成が必要。

### OGP画像のアップロード

```bash
curl -T "path/to/ogp.png" \
  "ftp://sv16489.xserver.jp/growthfix.jp/public_html/whitepaper/ogp.png" \
  --user "xs992119:${FTP_PASS}"
```

### WP PDFのアップロード

Utageのダウンロードリンク経由にするか、直接配置するか選べる：

**オプションA：Utage経由（推奨）**
- メール登録者のみPDFダウンロード可能
- リード獲得が確実

**オプションB：直接配置**
```bash
curl -T "/Users/ishiinobuyuki/Desktop/gravity-whitepaper-v7.pdf" \
  "ftp://sv16489.xserver.jp/growthfix.jp/public_html/whitepaper/gravity-whitepaper.pdf" \
  --user "xs992119:${FTP_PASS}"
```

---

## デプロイ後の確認

### 動作確認チェックリスト

- [ ] `https://growthfix.jp/whitepaper/` が表示される
- [ ] モバイル（iPhone/Android）で崩れなく表示される
- [ ] メールアドレス入力→送信が成功する
- [ ] 送信後に自動メールが届く
- [ ] メール内のPDFリンクがダウンロード可能
- [ ] OGP画像がFacebook/X でシェア時に表示される（https://developers.facebook.com/tools/debug/ で確認）
- [ ] Google Analytics でページビューが計測される
- [ ] Meta Pixel の PageView イベントが発火している

### URL設定

- メインLP：`https://growthfix.jp/whitepaper/`
- 短縮URL（X投稿用）：要取得（bit.ly等）

---

## デザイン仕様

### カラーパレット（モノクロ基調）

- 濃：#0f172a（Hero背景・CTA）
- 濃グレー：#1e293b（本文）
- 中グレー：#475569（補足テキスト）
- 薄グレー：#64748b（小さい補足）
- 薄背景：#f8fafc（セクション背景）
- 罫線：#e2e8f0
- 白：#ffffff

### レイアウト構造

```
[Hero]              黒背景・WPのカバー風デザイン
  ↓
[Value]             4つの価値提案（01〜04の数字）
  ↓
[Author]            石井プロフィール＋引用
  ↓
[Form]              メール登録フォーム（名前・会社・メール）
  ↓
[FAQ]               5つのよくある質問
  ↓
[Footer]            黒背景・各サービスへのリンク
```

### レスポンシブ対応

- デスクトップ：最大幅640px（読みやすさ重視）
- モバイル：92%幅・パディング調整
- ブレークポイント：600px

---

## Meta広告との連携

### 推定コンバージョンフロー

```
Meta広告（CTR 0.8-1.0%）
  ↓
LP到達（月500-1,000クリック想定）
  ↓
メール登録（CVR 20-30%）
  ↓
WP DL 月100-200件（真の変数の先行指標）
  ↓
育成メール5通（Day 0〜10）
  ↓
体験セッション申込（リスト5-10%）
  ↓
月4件の体験セッション達成（真の変数）
```

### Meta広告設定

- 目的：**リード獲得**（Lead）
- コンバージョン地点：LPのForm送信イベント
- Pixel設定：「Lead」イベントをForm送信時に発火
  - ページに追加：`fbq('track', 'Lead');` をForm成功時に発火

---

## 今後の改修候補

### Phase 1（初期配布）
- 現状のシンプルLP
- メールアドレス収集のみ

### Phase 2（検証後・転換率改善）
- A/Bテスト（Hero コピー変更）
- テスティモニアル追加
- 体験セッション直接予約フォームの追加

### Phase 3（規模拡大）
- セミナー告知の統合
- Note記事への誘導
- 複数言語対応（英語版等）

---

## デプロイ前タスク（今週中）

- [ ] Utage商品「事業の勝ち筋ループの作り方（無料WP）」作成
- [ ] Utage商品URLを`index.html`のform actionに反映
- [ ] OGP画像（1200x630px）制作
- [ ] WP v7 完成版（whitepaper-v7.pdf）の準備
- [ ] `/whitepaper/` ディレクトリの作成（FTP）
- [ ] 上記3ファイルのデプロイ
- [ ] 動作確認
- [ ] Meta広告設定
- [ ] X固定投稿の更新（WP配布告知）
