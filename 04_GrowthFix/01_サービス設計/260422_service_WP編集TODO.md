# /service/ WordPress 編集 TODO（260422 SCAN廃止反映）

> **背景：** 260422 SCAN廃止・Shift統合・5サービス化に伴い、`/service/` ページから Gravity Scan の記載を削除する必要があります。WordPress管理画面での編集が必要（FTPでは不可）。
> **現状：** /gravity-scan/ → /gravity-shift/ への301リダイレクトは稼働中のため、リンククリック時は正しく遷移します。**テキスト表示のみ不整合**の状態。

---

## 編集手順

1. WordPress管理画面にログイン：`https://growthfix.jp/wp-admin/`
2. 固定ページ → `/service/` を編集
3. 以下の箇所を削除または修正

---

## 削除する箇所（Gravity Scan カード全体）

以下の HTML ブロックを**完全削除**：

```html
<!-- Gravity Scan（BP前提・CEO+幹部・multi-step） -->
<div class="sv2-card" id="gravity-scan">
  ...（30-40万円・View more リンク含む全体）...
</div>
```

## 編集する箇所

### 1. サービスガイドリスト（sv2-guide-item）
- **削除対象：** `<a href="https://growthfix.jp/gravity-scan/" class="sv2-guide-item">Gravity Scan</a>`

### 2. グローバルメニューボタン
- **削除対象：** `<a href="https://growthfix.jp/gravity-scan/" class="menu_btn">Gravity Scan</a>`

### 3. Gravity Shift カード（既存）
- **価格表示更新：** `60万円` → `80万円`
- **説明文更新：** 「3ヶ月の組織実装プログラム」 → 「Week 1-2 組織実装整合診断＋Week 3-12 実装伴走の3ヶ月プログラム」

### 4. Gravity Blueprint カード（既存）
- **説明文確認：** v5.3 再定義「個人引力を組織の4軸（制度・会議・評価軸・役割分担）への翻訳設計図」に更新されているか確認

---

## 編集後の5サービス構成

```
01. Gravity CODE（5万円・任意）
02. Gravity Blueprint（10万円・必須）
03. Gravity Coaching（月15万円・並行）
04. Gravity Shift（80万円・3ヶ月）  ← Scan統合後
05. Gravity Orbit（月15-25万円・継続）
```

---

## 動線（5サービス版）

```
CODE → Blueprint → Shift → Orbit
        ↓
     Coaching（並行）
```

- BP 10万 + Shift 80万 = 総額 **90万円**
- Shift 3名枠 = 90万円（Blueprint込み総額 100万円）

---

## 緊急性

**低**。/gravity-scan/ は 301リダイレクトで /gravity-shift/ に遷移するため、クリック動線は機能しています。テキスト表示のみの不整合なので、Sushitech（4/27-28）までに対応できればOK。
