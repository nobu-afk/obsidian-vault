# Note マガジンバナー制作プロンプト（Gemini Nano Banana 用）

> **目的：** 3 テーマ（引力経営／組織の引力設計／事業中心人事）の Note マガジンカバー画像をトンマナ統一で生成
> **ツール：** Gemini Nano Banana（画像生成AI）
> **方針（260423 更新）：** **Nano Banana 単独で文字入りバナー完結**（日英併記推奨・Canva後工程不要）
> **フォールバック：** 日本語が崩れた場合は Canva で日本語部分だけ重ねる
> **出力サイズ：** 1280 × 670 px（Note カバー画像推奨）

---

## 🎨 デザイン共通コンセプト

### コンセプトキーワード

- **深宇宙 × 引力**（WP V9 Hubble UDF と呼応）
- **知的・神秘的・ミニマル**
- **深い紺・黒を基調にした高級感**
- **引力を視覚化**する中心構図（テーマごとに差分）

### 共通トンマナ

| 要素 | 指定 |
|---|---|
| 配色基調 | 深い紺（#0f172a）／黒（#000）／中間のグレー |
| テイスト | Hubble 望遠鏡の写真 × ラグジュアリーマガジン表紙 |
| 人物 | なし |
| ロゴ | なし |
| テキスト | なし（後工程で重ねる） |
| 明度 | 暗めだが、中央の光源は十分明るい |
| 周辺処理 | ビネット（周辺減光） |

### テーマ別 差別化要素

| テーマ | 構図 | アクセント色 |
|---|---|---|
| **1. 引力経営** | 中央に 1 つの強い光源から重力波が放射 | 黄銅色／茶（#b8a88a） |
| **2. 組織の引力設計** | 散在する複数の光が 1 点に収束する | 青（#1e40af） |
| **3. 事業中心人事** | 中心コアを 3 本の軌道が回転 | 金（#c5a880） |

---

## 📝 Nano Banana プロンプト（英語版・高精度）

### 🅰 Prompt 1：引力経営（Gravity Management）

```
An abstract cosmic background image for a business magazine cover banner, 16:9 aspect ratio (1280x670).

Composition: A single intense point of pure light at the exact center, radiating gentle warm golden-bronze glow outward in soft concentric ripples. Space curves gravitationally around the central light source, depicted by faint circular contour lines bending inward toward the core.

Environment: Deep cosmic space, rich navy and black background. Scattered distant galaxies and faint nebulae in the far background. Slight vignette darkening the edges.

Mood: Intellectual, minimalist, sophisticated, intensely focused. Conveys "a single source of gravitational pull."

Style: Hubble Deep Field photography aesthetic merged with luxury magazine cover design. High contrast but not harsh.

Color palette: Deep navy (#0f172a), pure black, warm bronze accent (#b8a88a), subtle gold highlights.

Strictly no text, no people, no logos, no watermarks. Cinematic and premium feel.
```

### 🅱 Prompt 2：組織の引力設計（Gravity Organization Design）

```
An abstract cosmic background image for a business magazine cover banner, 16:9 aspect ratio (1280x670).

Composition: Multiple small points of light scattered across the space, all converging with subtle energy streams into a single focal point positioned at the upper-right third of the image. The convergence suggests translation and unification — many becoming one.

Environment: Deep cosmic space, rich navy and black background. Thin cool-blue energy strands flowing from the scattered lights toward the focal convergence point. Distant galaxies softly blurred in the background.

Mood: Architectural, systemic, intelligent, organized. Conveys "translation from many into one structured whole."

Style: Hubble observation aesthetic merged with modern infrastructure visualization. Clean geometric energy flows.

Color palette: Deep navy (#0f172a), pure black, cool blue accent (#1e40af), subtle cyan highlights.

Strictly no text, no people, no logos, no watermarks. Cinematic and premium feel.
```

### 🅲 Prompt 3：事業中心人事（Business-Centric HR）

```
An abstract cosmic background image for a business magazine cover banner, 16:9 aspect ratio (1280x670).

Composition: A central gravitational core glowing softly, surrounded by three distinct orbital paths circling around it at different angles and radii. Each orbital trace shows subtle motion blur, suggesting continuous circulation and sustained flow. The three orbits create a harmonious self-sustaining system.

Environment: Deep cosmic space, rich navy and black background. The three orbits glow in warm gold-bronze tones. Distant galaxies and faint stardust in the background. Slight vignette.

Mood: Cyclical, harmonious, structural, elegant. Conveys "a self-sustaining system of circulation."

Style: Hubble observation aesthetic merged with infographic elegance. Motion and stillness balanced.

Color palette: Deep navy (#0f172a), pure black, warm gold accent (#c5a880), subtle amber highlights.

Strictly no text, no people, no logos, no watermarks. Cinematic and premium feel.
```

---

## 🗾 日本語プロンプト（簡易版・Nano Banana が日本語対応している場合）

### 🅰 引力経営

```
ビジネスマガジン表紙風の抽象的な宇宙背景画像、16:9 比率（1280x670）。

構図：画像中央に 1 つの強烈な光源があり、温かい黄銅色の光が同心円状に穏やかに広がっている。中心の光源の周りに重力場が空間を歪ませているような、内側に曲がる円形の等高線が微かに見える。

環境：深い宇宙空間。豊かな紺と黒の背景。遠景にぼんやりした銀河や星雲。画面端にビネット。

雰囲気：知的、ミニマル、洗練、強く集中している。「1 つの引力源」を表現。

スタイル：ハッブル宇宙望遠鏡の写真 × ラグジュアリーマガジン表紙デザイン。

配色：深い紺（#0f172a）、漆黒、温かい黄銅色（#b8a88a）、微かな金のハイライト。

テキスト、人物、ロゴ、透かしは一切含めないこと。映画的で高級感のある仕上がり。
```

### 🅱 組織の引力設計

```
ビジネスマガジン表紙風の抽象的な宇宙背景画像、16:9 比率（1280x670）。

構図：複数の小さな光点が空間に散らばっており、すべてが画像右上 1/3 の位置にある 1 つの焦点に向かってエネルギーの流れで収束していく。「多が 1 に統合される」翻訳と統一を示唆。

環境：深い宇宙空間。豊かな紺と黒の背景。散在する光から収束点へ細い冷たい青色のエネルギー線が流れる。遠景に柔らかくぼかされた銀河。

雰囲気：建築的、体系的、知的、秩序ある。「多数から構造化された 1 つへの翻訳」を表現。

スタイル：ハッブル観測の美学 × 現代的インフラビジュアライゼーション。

配色：深い紺（#0f172a）、漆黒、冷たい青（#1e40af）、微かなシアンのハイライト。

テキスト、人物、ロゴ、透かしは一切含めないこと。
```

### 🅲 事業中心人事

```
ビジネスマガジン表紙風の抽象的な宇宙背景画像、16:9 比率（1280x670）。

構図：画像中央に柔らかく光る重力コアがあり、そのまわりを 3 本の異なる軌道が異なる角度と半径で回っている。各軌道には微かなモーションブラーが入り、継続的な循環と持続する流れを示唆。3 本の軌道が調和のとれた自己持続システムを作る。

環境：深い宇宙空間。豊かな紺と黒の背景。3 本の軌道は温かい金色で光る。遠景にぼんやりした銀河と星塵。画面端にビネット。

雰囲気：循環的、調和的、構造的、優雅。「循環する自己持続システム」を表現。

スタイル：ハッブル観測の美学 × インフォグラフィックのエレガンス。動きと静けさのバランス。

配色：深い紺（#0f172a）、漆黒、温かい金（#c5a880）、微かなアンバーのハイライト。

テキスト、人物、ロゴ、透かしは一切含めないこと。
```

---

## 🛠 使い方・手順

### Step 1：Gemini Nano Banana で画像生成

1. Gemini にアクセス（gemini.google.com）
2. 画像生成モードに切り替え（もしくは「画像を作成して」と指示）
3. **英語版プロンプト 1 を貼り付けて生成**（推奨：英語版の方が精度高い）
4. 生成結果を確認・必要なら微調整指示を追加（例：「もう少し暗めに」「中央の光をより強く」）
5. 満足いく画像が出たらダウンロード
6. Prompt 2・3 も同様に生成

### Step 2：生成画像の品質チェック

**チェックポイント：**
- [ ] 3 枚の**明度・コントラストが揃っている**か
- [ ] アクセント色が仕様通り（茶／青／金）か
- [ ] テキストや人物や透かしが**混入していない**か
- [ ] 構図が**トンマナ統一感**あるか（全体の雰囲気が揃っているか）
- [ ] ピクセルが粗くない（1280×670 以上の解像度か）

**品質が揃わない場合：**
- プロンプトに「same style as previous images」「consistent with the first banner」を追加
- 連続生成時は 1 セッション内で生成すると統一感が出やすい

### Step 3：Canva で日本語テキスト重ね

1. Canva で「カスタムサイズ 1280 × 670」新規作成
2. Nano Banana 生成画像を**背景として配置**
3. テキストレイヤーを追加：

**バナー 1：引力経営**
```
（最上段・小）組織に、引力を。
（中央・大）引力経営
（下段・中）経営者が自分の引力源泉を見つける
（右下・小）GrowthFix
```

**バナー 2：組織の引力設計**
```
（最上段・小）組織に、引力を。
（中央・大）組織の引力設計
（下段・中）経営者の引力を、組織の言葉に翻訳する
（右下・小）GrowthFix
```

**バナー 3：事業中心人事**
```
（最上段・小）組織に、引力を。
（中央・大）事業中心人事
（下段・中）事業から逆算する人事戦略
（右下・小）GrowthFix
```

**フォント指定：**
- タイトル大：Noto Serif JP Bold（明朝・重厚感）
- サブコピー：Noto Sans JP Medium（ゴシック・現代的）
- エピグラム／ロゴ：Noto Sans JP Regular・字間広め

**色：**
- タイトル＋サブ：白（#FFFFFF）
- エピグラム：アクセント色（テーマ別）

### Step 4：書き出し

- PNG（1280 × 670）
- 3 枚分：`magazine_cover_gravity_management.png` 等
- HP バナー用は別途 1200 × 630 で書き出し（同デザイン）

---

## 💡 プロンプト調整のコツ

### 生成結果が納得いかない場合の再プロンプト例

| 問題 | 追加指示 |
|---|---|
| 明度がバラつく | "Match the darkness and mood of the previous image exactly" |
| アクセント色が弱い | "Make the [color] accent stronger and more prominent" |
| 星や銀河が多すぎる | "Reduce background detail, keep it more minimalist" |
| テキストが混入した | "Absolutely no text, letters, or symbols of any kind" |
| 人物が混入した | "No human figures, no silhouettes, pure abstract cosmos" |
| 構図がズレた | "Center the light source exactly in the middle" |

### 3 枚の統一感を最大化する方法

- **1 つのセッション内で 3 枚生成**（Gemini が前の生成を参照する）
- プロンプト冒頭を**完全に同じ文**で始める（構図部分のみ変える）
- Prompt 2・3 の冒頭に「In the same style as the previous banner, ...」を追加

---

## 📐 代替サイズ（他用途）

| 用途 | サイズ | 備考 |
|---|---|---|
| Note マガジンカバー | **1280 × 670 px** | 推奨 |
| HP バナー | 1200 × 630 px | OGP 互換 |
| X カバー画像 | 1500 × 500 px | 構図調整が必要 |
| LinkedIn バナー | 1584 × 396 px | 横長・構図調整 |

→ Canva で1280×670 の**マスターデザイン**を作り、そこから各サイズにリサイズ書き出し推奨

---

## 🎯 Sushitech（4/27-28）活用

バナーが 4/24 までに完成すれば、以下で活用可能：

- **Note マガジン 3 つのカバー画像**
- **HP `/knowledge/` バナー**（現行リンクの画像として）
- **X ピン留め投稿の画像**
- **セミナーLP 内の連載紹介**

---

## 🔗 関連

- `04_GrowthFix/02_マーケティング/260423_情報発信_HPバナー_Noteマガジン設計.md` ── バナー含む明日の実装計画
- `04_GrowthFix/02_マーケティング/260423_情報発信_knowledge_LP設計書_GW実装用.md` ── GW実装のSEO最適化設計
- `05_プロダクト/WhitePaper/V9/images/space_bg.jpg` ── WP V9 Hubble UDF（デザイン参考）
- `05_プロダクト/Gravity/LP/images/space_bg.jpg` ── Gravity LP Hero 宇宙背景（同画像）

---

## 📌 プロンプト一括コピー用（一発用）

### Prompt 1 English（コピペ用）

```
An abstract cosmic background image for a business magazine cover banner, 16:9 aspect ratio (1280x670). Composition: A single intense point of pure light at the exact center, radiating gentle warm golden-bronze glow outward in soft concentric ripples. Space curves gravitationally around the central light source, depicted by faint circular contour lines bending inward toward the core. Environment: Deep cosmic space, rich navy and black background. Scattered distant galaxies and faint nebulae in the far background. Slight vignette darkening the edges. Mood: Intellectual, minimalist, sophisticated, intensely focused. Conveys "a single source of gravitational pull." Style: Hubble Deep Field photography aesthetic merged with luxury magazine cover design. High contrast but not harsh. Color palette: Deep navy (#0f172a), pure black, warm bronze accent (#b8a88a), subtle gold highlights. Strictly no text, no people, no logos, no watermarks. Cinematic and premium feel.
```

### Prompt 2 English（コピペ用）

```
An abstract cosmic background image for a business magazine cover banner, 16:9 aspect ratio (1280x670). In the same style as the previous banner. Composition: Multiple small points of light scattered across the space, all converging with subtle energy streams into a single focal point positioned at the upper-right third of the image. The convergence suggests translation and unification — many becoming one. Environment: Deep cosmic space, rich navy and black background. Thin cool-blue energy strands flowing from the scattered lights toward the focal convergence point. Distant galaxies softly blurred in the background. Mood: Architectural, systemic, intelligent, organized. Conveys "translation from many into one structured whole." Style: Hubble observation aesthetic merged with modern infrastructure visualization. Clean geometric energy flows. Color palette: Deep navy (#0f172a), pure black, cool blue accent (#1e40af), subtle cyan highlights. Strictly no text, no people, no logos, no watermarks. Cinematic and premium feel.
```

### Prompt 3 English（コピペ用）

```
An abstract cosmic background image for a business magazine cover banner, 16:9 aspect ratio (1280x670). In the same style as the previous banners. Composition: A central gravitational core glowing softly, surrounded by three distinct orbital paths circling around it at different angles and radii. Each orbital trace shows subtle motion blur, suggesting continuous circulation and sustained flow. The three orbits create a harmonious self-sustaining system. Environment: Deep cosmic space, rich navy and black background. The three orbits glow in warm gold-bronze tones. Distant galaxies and faint stardust in the background. Slight vignette. Mood: Cyclical, harmonious, structural, elegant. Motion and stillness balanced. Color palette: Deep navy (#0f172a), pure black, warm gold accent (#c5a880), subtle amber highlights. Strictly no text, no people, no logos, no watermarks. Cinematic and premium feel.
```

---

# 🆕 文字入りバナー版プロンプト（260423 更新）

> 「引力経営」260423生成画像（背景のみ版）は高品質だったが、**文字入りで完結させたい**要望を受けて、Nano Banana 単独で完結させるプロンプトを追加。
> **3 バリエーション** 提供（英語のみ／日英併記 / 日本語主軸）。日本語崩れリスクを考慮した保険設計。

---

## 🅰 テーマ 1：引力経営（文字入り 3 バリエーション）

### バリエーション A-1：英語タイトル主軸（最も安全）

```
Premium business magazine cover banner, 16:9 aspect ratio (1280x670).

Background: Deep cosmic space with a single intense point of pure light at the exact center, radiating gentle warm golden-bronze glow outward in concentric ripples. Space curves gravitationally around the central light source. Scattered distant galaxies in navy and black background. Slight vignette.

Typography (rendered clearly and cleanly, museum-quality, no garbled text):
- Top-left small text: "GROWTHFIX ─ KNOWLEDGE"
- Center-left large serif title: "GRAVITY MANAGEMENT"
- Below title, medium subtitle: "How leaders find their own gravitational source"
- Bottom-right small: "vol.01"

All text in pure white with subtle glow. Minimalist, museum-quality typography. High contrast against the dark cosmic background. Elegant spacing.

Style: Hubble Deep Field photography merged with luxury magazine cover design. Color palette: deep navy (#0f172a), black, warm bronze accent (#b8a88a), white text.

No people, no logos, no watermarks. Premium and cinematic feel.
```

### バリエーション A-2：日英併記（推奨・ブランド「引力経営」を活かす）

```
Premium business magazine cover banner, 16:9 aspect ratio (1280x670).

Background: Deep cosmic space with a single intense point of pure light at the exact center, radiating gentle warm golden-bronze glow outward in concentric ripples. Space curves gravitationally around the central light source. Scattered distant galaxies in navy and black background. Slight vignette.

Typography (rendered clearly and cleanly, absolutely no garbled or scrambled characters):
- Top-left small English text: "GROWTHFIX ─ KNOWLEDGE"
- Center-left, large bold Japanese kanji title in elegant Mincho serif: 引力経営
- Directly below, small English caption: "GRAVITY MANAGEMENT"
- Bottom-left small Japanese subtitle in sans-serif: 経営者が自分の引力源泉を見つける

All text in pure white with subtle glow. High contrast against dark background. Museum-quality Japanese typography with perfect character rendering.

Style: Hubble Deep Field photography merged with luxury Japanese magazine cover (like 『致知』or『Harvard Business Review Japan』). Color palette: deep navy (#0f172a), black, warm bronze accent (#b8a88a), white text.

No people, no logos, no watermarks. Premium and cinematic feel.
```

### バリエーション A-3：日本語主軸（成功時の仕上がり最高）

```
プレミアムなビジネス誌のカバーバナー、16:9 比率（1280x670）。

背景：画像中央に 1 つの強烈な光源、そこから温かい黄銅色の光が同心円状に広がる。空間が重力で歪む描写。深い紺と黒の宇宙、遠景に銀河。ビネット。

文字（明朝体・崩れのない美しい日本語で正確にレンダリング）：
- 左上・小さな英字：「GROWTHFIX ─ KNOWLEDGE」
- 中央左・大きな明朝体タイトル：引力経営
- 直下・小さな英字キャプション：「GRAVITY MANAGEMENT」
- 左下・小さなゴシック：経営者が自分の引力源泉を見つける

すべての文字は純白、微かに光る。高コントラスト。日本語文字は崩れのない正確な明朝体フォント（Noto Serif JP 相当）。

スタイル：ハッブル宇宙望遠鏡写真 × 高級日本のビジネス誌（『致知』『ハーバードビジネスレビュー日本版』のような）。配色：深い紺（#0f172a）、黒、温かい黄銅色（#b8a88a）、白の文字。

人物・ロゴ・透かしは一切なし。映画的で高級感のある仕上がり。
```

---

## 🅱 テーマ 2：組織の引力設計（文字入り 3 バリエーション）

### バリエーション B-1：英語タイトル主軸

```
Premium business magazine cover banner, 16:9 aspect ratio (1280x670). In the same visual style as the previous banner.

Background: Deep cosmic space with multiple small lights scattered across the space, all converging with subtle energy streams into a single focal point at the upper-right. Cool blue energy strands flow from scattered stars toward the convergence. Distant galaxies softly blurred. Slight vignette.

Typography (rendered clearly, no garbled text):
- Top-left small: "GROWTHFIX ─ KNOWLEDGE"
- Center-left large serif: "GRAVITY ORGANIZATION DESIGN"
- Below: "Translating a leader's gravity into organizational language"
- Bottom-right small: "vol.02"

All text pure white. Minimalist typography. Cool blue (#1e40af) accent in background. Style: Hubble observation merged with modern infrastructure visualization. Color palette: deep navy, black, cool blue accent, white text.

No people, no logos, no watermarks.
```

### バリエーション B-2：日英併記（推奨）

```
Premium business magazine cover banner, 16:9 aspect ratio (1280x670). Same style as previous banner.

Background: Deep cosmic space. Multiple small lights scattered across the space, all converging with subtle cool-blue energy streams into a single focal point at the upper-right. Distant galaxies softly blurred.

Typography (absolutely no garbled characters):
- Top-left small English: "GROWTHFIX ─ KNOWLEDGE"
- Center-left, large bold Japanese kanji in elegant Mincho serif: 組織の引力設計
- Directly below, small English caption: "GRAVITY ORGANIZATION DESIGN"
- Bottom-left small Japanese sans-serif: 経営者の引力を、組織の言葉に翻訳する

All text pure white with subtle glow. Perfect Japanese character rendering. Cool blue (#1e40af) accent. Style: Hubble observation merged with luxury Japanese magazine cover typography.

No people, no logos, no watermarks.
```

### バリエーション B-3：日本語主軸

```
プレミアムなビジネス誌のカバーバナー、16:9 比率（1280x670）。前のバナーと同じスタイル。

背景：深い宇宙空間。空間に散らばる複数の小さな光が、冷たい青色のエネルギー線で 1 つの焦点（画面右上）に収束していく。遠景に柔らかくぼかされた銀河。

文字（崩れのない美しい日本語で正確にレンダリング）：
- 左上・小英字：「GROWTHFIX ─ KNOWLEDGE」
- 中央左・大明朝体タイトル：組織の引力設計
- 直下・小英字：「GRAVITY ORGANIZATION DESIGN」
- 左下・小ゴシック：経営者の引力を、組織の言葉に翻訳する

すべて純白・微かに光る。日本語は崩れのない正確な明朝体（Noto Serif JP 相当）。冷たい青（#1e40af）のアクセント。

スタイル：ハッブル観測 × 高級日本誌の組版美。人物・ロゴ・透かしは一切なし。
```

---

## 🅲 テーマ 3：事業中心人事（文字入り 3 バリエーション）

### バリエーション C-1：英語タイトル主軸

```
Premium business magazine cover banner, 16:9 aspect ratio (1280x670). Same style as previous banners.

Background: Deep cosmic space with a central gravitational core glowing softly, surrounded by three distinct orbital paths circling around it at different angles and radii. Motion blur on orbits. Warm gold-bronze tones. Distant galaxies.

Typography (rendered clearly):
- Top-left small: "GROWTHFIX ─ KNOWLEDGE"
- Center-left large serif: "BUSINESS-CENTRIC HR"
- Below: "HR strategy reversed-engineered from business"
- Bottom-right small: "vol.03"

All text pure white. Warm gold (#c5a880) accent. Style: Hubble observation merged with infographic elegance. Color palette: deep navy, black, warm gold, white text.

No people, no logos, no watermarks.
```

### バリエーション C-2：日英併記（推奨）

```
Premium business magazine cover banner, 16:9 aspect ratio (1280x670). Same style as previous banners.

Background: Deep cosmic space. Central gravitational core glowing softly, three distinct orbital paths circling around it at different angles. Warm gold-bronze motion blur on orbits. Distant galaxies and faint stardust.

Typography (absolutely no garbled characters):
- Top-left small English: "GROWTHFIX ─ KNOWLEDGE"
- Center-left, large bold Japanese kanji in elegant Mincho serif: 事業中心人事
- Directly below, small English caption: "BUSINESS-CENTRIC HR"
- Bottom-left small Japanese sans-serif: 事業から逆算する人事戦略

All text pure white with subtle glow. Perfect Japanese character rendering. Warm gold (#c5a880) accent. Style: Hubble observation merged with luxury Japanese magazine cover typography.

No people, no logos, no watermarks.
```

### バリエーション C-3：日本語主軸

```
プレミアムなビジネス誌のカバーバナー、16:9 比率（1280x670）。前のバナーと同じスタイル。

背景：深い宇宙空間。中央に柔らかく光る重力コア、その周りを 3 本の軌道が異なる角度で回転。温かい金色のモーションブラー。遠景に銀河と星塵。

文字（崩れのない美しい日本語）：
- 左上・小英字：「GROWTHFIX ─ KNOWLEDGE」
- 中央左・大明朝体：事業中心人事
- 直下・小英字：「BUSINESS-CENTRIC HR」
- 左下・小ゴシック：事業から逆算する人事戦略

純白・微かに光る。日本語は正確な明朝体。温かい金（#c5a880）のアクセント。

人物・ロゴ・透かしは一切なし。
```

---

## 🎯 推奨運用：A-2 → A-1 の順で試す

### ステップ 1：**A-2（日英併記）をまず試す**

日本語「引力経営」が美しく描画されれば**最強の仕上がり**。Note / HP 両方で使える。

### ステップ 2：日本語が崩れたら **A-1（英語主軸）に切り替え**

英語「GRAVITY MANAGEMENT」は Nano Banana の得意領域。確実に綺麗に出る。日本語はCanvaで別途重ねる（保険）。

### ステップ 3：A-3（日本語主軸）は実験的

日本語を大きく配置する分、崩れたら影響が大きい。他2バリエーションが全滅した場合の**最後の手**。

---

## 💡 日本語が崩れた場合の追加プロンプト

```
Re-render with absolutely accurate Japanese kanji characters (引力経営 / 組織の引力設計 / 事業中心人事). Use proper Mincho serif font. No scrambled, distorted, or fake kanji. If you cannot render Japanese properly, render the English only and leave the Japanese area blank for later editing.
```

このフレーズを A-2 プロンプトの末尾に追加すると、精度が上がる可能性。

---

## 🔄 統一感を保つ Tips

1. **1 セッション内で 3 テーマ連続生成**（Gemini が前の生成を参照）
2. Prompt 2・3 の冒頭に「**Same style as previous banners**」を維持
3. 文字位置・フォント・配色を **仕様完全統一**（プロンプト内の対応行が一致）
4. 生成後、3 枚を並べて**明度・トンマナが揃っているか目視確認**
