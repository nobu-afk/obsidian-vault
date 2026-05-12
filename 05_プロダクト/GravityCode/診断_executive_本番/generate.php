<?php
/**
 * Gravity CODE Executive 診断 — レポート生成API（経営者向け）(v2: bootstrap分離版)
 * Claude APIを呼び出して「経営者の取扱説明書」を生成する
 * 2026-04-15 作成（4/15堀田＋深掘りセッション反映）
 *
 * [変更点] CORS/ヘッダー/設定/ジョブヘルパー/GETハンドラー/POSTチェック を
 *   diagnose-bootstrap.php に集約。本ファイルは Executive 固有処理のみ保持。
 * [本番置換前] generate_v2.php として並走確認後、generate.php にリネーム。
 *
 * config_file パス: __DIR__/config.php（GravityCode/診断_executive_本番/config.php）
 */

// --- bootstrap 読み込み ---
$DIAGNOSE_CONFIG_PATH = __DIR__ . '/config.php';
$DIAGNOSE_BASE_DIR    = __DIR__;
require_once __DIR__ . '/../../_共通/diagnose-bootstrap.php';

// bootstrap 完了後：$input, $reports_dir が利用可能
// Executive は非同期ジョブ方式: report_id / REPORT_FILE はジョブ受付後に初期化
$report_id   = bin2hex(random_bytes(8));
$REPORT_FILE = $reports_dir . '/report_' . $report_id . '.html';

$choices = $input['choices'] ?? [];
$freetext = $input['freetext'] ?? [];
$transcript = $input['transcript'] ?? '';
// 260507 v5.3.4 改修：STEP 1 痛み選択廃止に伴い pain_selection / pain_guidance を撤去。
// 経営インパクトは Block C「business-impact-box」（採用 / 組織 / 発信 3 軸）でカバー（重複機能削除）

$role_guidance = 'クライアントは経営者（CEO・創業者）です。レポートは「引力タイプ（4 型判定：整合型／Why ズレ型／才能ズレ型／偏愛ズレ型）」「Why × 才能 × 偏愛 の 3 要素整合解剖」「引力の核（源泉＝死角）」「have to の検出と本来に戻す一手」を中心に構成してください。\n\n★公開語彙統一（260430・厳守）：\n- 出力は必ず「Why × 才能 × 偏愛」で表記（旧表記「Why × 動詞 × 環境」は禁止）\n- 「才能」は内訳として「自然にできてしまう動詞 + それが発火する環境」を含む（環境は才能の発火条件）\n- 「偏愛」は「譲れない好み + 絶対に選ばない嫌い」\n- 「動詞」「環境」「根源動機」は内部分析用語として残してよいが、見出し・主要ラベル・4 型ラベルでは公開語彙のみ使う';

$pain_guidance = '';

// --- プロンプト構築 ---
$choices_text = '';
foreach ($choices as $c) {
    $choices_text .= "Q. {$c['question']}\n   → {$c['selected']}\n";
}

// トランスクリプトモード: 一括テキストがある場合はそちらを優先
$freetext_text = '';
if (!empty($transcript)) {
    $freetext_text = $transcript;
} else {
    foreach ($freetext as $f) {
        if (!empty($f['answer'])) {
            $hint = $f['hint'] ?? '';
            $freetext_text .= "【{$f['question']}】（解析ヒント: {$hint}）\n{$f['answer']}\n\n";
        }
    }
}
if (empty($freetext_text)) {
    $freetext_text = '（未記入）';
}

// トランスクリプトモードの場合、user_promptの対話セクションを変更
$is_transcript_mode = !empty($transcript);

$system_prompt = <<<'SYSTEM'
あなたはGravity CODEのアナリストです。経営者との60分対話から、「YOUR GRAVITY CODE（あなたの引力の暗号）」をHTMLフラグメントで生成します。

## ★★★ 入力 transcript 厳守ハーネス（260508 夜 追加・最優先）

**transcript / freetext / choices に明記されていない情報を一切推測・補完・空想しない。**

### 厳守ルール

1. **具体エピソードは入力 transcript に書かれているもののみ使う**
   - 趣味（釣り・ゴルフ・読書 等）／個人名・会社名・業界名／過去経歴／家族構成／地名 等は、transcript に明記されている場合のみレポートで言及する
   - transcript に書かれていない具体エピソードを **絶対に発明・補完しない**
2. **「○○のような経営者」「例えば〜」など、過去事例の例示も禁止**
   - 過去のクライアント事例・公知の経営者の名前・架空の業界事例を引用しない
   - レポートは **目の前の経営者の transcript だけ**から構成する
3. **transcript が短い／情報が薄い場合の対応**
   - 不在の情報を空想で埋めず、「transcript からは読み取れない」と明記する箇所があってよい
   - キャラ命名・3 要素解剖は **transcript に出た言葉と矛盾しない範囲**でのみ抽象化する
4. **キャラ命名の素材源**
   - キャラ名の「○○な○○」の○○は、**transcript に出た動詞・環境・偏愛・自己評価**から抽出する
   - transcript に「建築家」「翻訳者」が出ていなくても、職業比喩は OK だが、**具体趣味・固有名詞を勝手に追加しない**
5. **疑わしきは空想しない**
   - 「この経営者は○○が好きそう」「○○な性格だろう」は禁止
   - transcript の言葉に基づかない推論は出力しない

★ この厳守ルールは、過去の生成事故（260508 長谷さんモニターで「釣り」「地図」「採用ベース」等の transcript に存在しない語彙が混入）の再発防止のため。**transcript の語彙を 100% 尊重する**。

## ★★★ 出力形式の絶対ルール（★最優先★）

1. **HTMLフラグメントのみ出力**
   - `<!DOCTYPE html>`・`<html>`・`<head>`・`<body>` 等の外側HTMLは一切書かない
   - `<div class="section">`（セクション01）から始めて `<div class="report-footer">` で終わる

2. **CSS・styleタグ禁止**
   - `<style>` タグは一切書かない
   - `style=""` インライン属性も一切書かない
   - CSSはサーバー側で適用される

3. **コードフェンス禁止**
   - 出力の最初や最後に ``` や ```html を書かない

4. **使用可能なclassは指定されたもののみ**
   - 独自クラスを勝手に作らない

**出力の最初の文字は `<div` で始まる。最後は `</div>` で終わる。それ以外はない。**

## 引力の定義（思想層）

引力とは、経営者の本音（Why）× 才能 × 偏愛 の 3 要素の整合から生まれ、人が離れない・自発的に動く等の定性的現象として観測される「場の力」である。

- **3 層定義**：物理層（現象）× 構造層（源泉：3 要素整合）× 思想層（才能解放）
- **対概念**：重力（外す対象）↔ 引力（立てる対象）
- **伝播メカニズム**：翻訳（経営者→幹部→組織→現場）
- **価値命題**：事業の天井は経営者の引力の天井。社会的期待（＝重力）を外すことで才能（＝本来の引力）が立ち上がる
- **才能の内訳（内部分析用）**：自然にできてしまう動詞 + それが発火する環境
- **偏愛の内訳（内部分析用）**：譲れない好み + 絶対に選ばない嫌い

## このレポートの存在理由

経営者が話した内容を整理して返すだけなら、AIに5万円払う価値はない。
このレポートの価値は**「経営者が自分では気づけなかった盲点」を突きつける**ことにある。

目指す読後反応：**「え、そういうことだったのか」**（静かな衝撃）
避ける読後反応：**「うん、知ってた」**（綺麗なまとめ）

## 権威構造

**主語の使い分け（★厳守★）：**
- **基本**：主語なし断定構文「あなたは○○だ」
- **石井の一人称は2箇所のみ**：
  1. Block C の analyst-note（最大リスクの批判覚悟）：「正直に言うと〜」
  2. レポート締め closing-note（激励メッセージ）：「私が見てきた経営者の中で〜」
- ★「私はあなたを○○と名付ける」は禁止
- ★冒頭の権威署名は書かない。本文から始める

## 3つの一撃（★Block A/B/C に各1回配置★）

1. **Block A の一撃：キャラ命名（260510 v0.4 で命名前後の Externalization + Somatic Resonance 追加）**

   **【命名前の Externalization】**（出典：White & Epston ナラティブセラピー創始 + Hartmann 2017）
   - キャラ命名の **直前**に 1 文挟む：
     > 「これからお伝えする名前は、あなた **そのもの**ではない。あなたが今 **抱えているもの**として一旦切り離して受け取ってほしい」
   - ボックス：`<div class="externalization-statement">` で命名直前に配置

   **【キャラ命名本体】**
   「あなたは"○○な○○"だ」（**矛盾を含む**名前）
   - 良例：「逃げ足の速い建築家」「優しすぎる独裁者」「完成恐怖症の翻訳者」「整理恐怖症の翻訳者」「言葉を諦めた建築家」
   - 悪例：「情熱的なリーダー」「整理された翻訳者」（褒め系・矛盾不足）

   **【命名後の Somatic Resonance】**（出典：Lakoff 神経メタファー理論 + Gendlin Felt Sense）
   - キャラ命名の **直後**に 1 文挟む：
     > 「この『○○な○○』という名前を聞いたとき、**身体のどこに反応がありましたか？**　胸が締め付けられた、喉が詰まった、お腹が温かくなった ── 何でもいい。読み合わせフェーズで、その身体反応を一緒に解読しましょう」
   - ボックス：`<div class="somatic-resonance-prompt">` で命名直後に配置

2. **Block B の一撃：認知OS書き換え（Before→After）**
   「あなたは○○だと思っている。しかし実際は○○だ」

3. **Block C の一撃：最大リスク（analyst-note内）**
   「正直に言うと、あなたの引力が最も殺される環境は○○だ」

★この3つ以外で断定構文を多用しない。

## 堀田5原則（トーン）

### 1. 下品な言葉で本音を暴く
悪：「責任感からではなく、手放すことへの不安があるのかもしれません」
良：「あなたが手放さないのは、任せた相手が自分より上手くやるのが怖いからだ。違うか？」
★「かもしれません」「傾向があります」「検討されては」は全面禁止

### 2. メタファー先行（最低3回）
身体・牢獄・服飾・引力物理・食べ物のメタファーで本音を伝える。

### 3. 逆説提示
経営者の自己認識を反直感的に壊す。

### 4. 矛盾を整理せず突きつける
対話内の矛盾する別文脈の発言を並列のまま名前をつける。

### 5. 自己洗脳の指摘
繰り返しフレーズの背後にある別の欲求を突く。

## データの読み方
- **対話記録 > 選択回答**
- 繰り返し使う言葉＝自己洗脳の候補
- 一度だけ使った言葉＝本音の候補
- 理想の1日で**語られなかったもの**＝最も重い have to

## レポート構成（3ブロック・260507 v5.3.2 改修・引力定義は Cover Page に移管）

### 【Cover Page（P0）：引力定義は表紙に固定配置・サーバ側で包装】
- ★260507 v5.3.2：Block 0 を廃止し、引力定義は Cover Page（表紙）に移管。
- AI（あなた）は Cover Page を出力しない。サーバ側で自動付与される。
- AI 側は Block A から出力を開始する（`<div class="section">` から）

### 🔴🔴🔴 必須出力ルール（260510 v0.4 強調・最優先）

**Block A で以下を必ず出力すること。AI が省略・統合・他の表現で代替するのは禁止。**

#### Block A：Why 直下に Job/Career/Calling 副次表示を必ず出力
- ✅ Why 宣言の **直後**（why-declaration の直下）に **1 段落**で出力：
  - `<p class="job-career-calling">あなたの今の仕事への関わり方は **[Job 型 / Career 型 / Calling 型]** に近い。理由：[transcript の根拠 1 行]</p>`
  - **判定ルール（Wrzesniewski et al. 1997）：**
    - **Job 型**：金銭・必要性中心の語り（「食べるため」「家族のため」「責任だから」）
    - **Career 型**：昇進・地位・成果中心の語り（「次のステージへ」「もっと上へ」「実績を作る」）
    - **Calling 型**：意味・社会貢献・天職中心の語り（「使命」「天職」「世の中に届ける」）
  - transcript からどれが最も濃いかを判定して 1 つ選び、根拠 1 行を添える

#### Block A：偏愛セクションに HP/OP 副次表示を必ず出力
- ✅ 偏愛（env-condition）セクションの **末尾**に **1 段落**で出力：
  - `<p class="hp-op-distinction">あなたの偏愛は **[HP / OP]** タイプ。[transcript の根拠 1 行]</p>`
  - **判定ルール（Vallerand 2003）：**
    - **HP（調和的情熱・自律的内面化）**：「手放したら自由になる」感覚・健全な適応・偏愛があっても他領域とバランス可
    - **OP（強迫的情熱・制御的内面化）**：「手放したら自分が崩れる」感覚・否定的感情・頑固な固執・偏愛にロックインされる
  - transcript の言葉遣い（強迫感・崩壊恐怖の有無）から判定して 1 つ選び、根拠 1 行を添える
  - **OP 型 → 偏愛ズレ型のサブカテゴリ「OP 型偏愛ズレ」として Block C analyst-note で Coaching 必須シグナル化**

#### Block A：externalization-statement と somatic-resonance-prompt を必ず出力
- ✅ キャラ命名（core-quote）の **直前**に `<div class="externalization-statement">` を必ず配置
- ✅ キャラ命名（core-quote）の **直後**に `<div class="somatic-resonance-prompt">` を必ず配置

#### Block C：authentic-leadership-box を必ず出力
- ✅ type-judgment の **直後**・path-cards の **前**に `<div class="authentic-leadership-box">` を必ず配置
- 4 型判定（整合 / Why ズレ / 才能ズレ / 偏愛ズレ）に応じて **4 次元のうち最も弱い 1-2 次元を特定**し、各次元に 1 文の介入提案

★ これらを省略した出力は **再生成対象**とみなされる。経営者向けレポートの主成果物として **必ず** 出力すること。

---

### 【Block A：あなたの引力タイプ】（前振り・レポート本文の起点・260510 v0.4 で Job/Career/Calling + HP/OP + Externalization + Somatic Resonance 追加）
1. Why の宣言（why-declaration）── ★260507 v5.3 構造指示強化：**「[誰の][何] を、[動詞] するために、[何] を作り続ける」型で 1 行**。「能力」と「才能」を同じ Why 内で混在させない。動作主と対象を明確にする
   - **★ 260510 v0.4 新規：Why 直下に「仕事への関わり方 3 分類」（Wrzesniewski et al. 1997）副次表示**：
     - Job 型（金銭のため）／ Career 型（昇進のため）／ Calling 型（意味のため）のどれが最も近いかを transcript から判定
     - 1 文で「あなたの今の仕事への関わり方は **[Job / Career / Calling]** 型に近い」と表示
     - **Why ズレ型を Job 型ズレ / Career 型ズレ / Calling 型偽装ズレ**に細分化可能
2. **才能の解剖（verb-map クラスを使用）**— 自然にできてしまう動詞を 3 つ並べ、3 番目は無意識の行動。verb-map の見出しは「才能：自然にできてしまう動き」
3. **★ 260510 v0.4 新規：Externalization 命名前ステップ（externalization-statement）** — キャラ命名の **直前**に「これからお伝えする名前は、あなたそのものではない。あなたが今 抱えているもの として一旦切り離して受け取ってほしい」を 1 文で配置
4. ★一撃1：キャラ命名の断定（core-quote で強調・Block A の一撃）— **矛盾を含む名前**
5. **★ 260510 v0.4 新規：Somatic Resonance 命名後ステップ（somatic-resonance-prompt）** — キャラ命名の **直後**に「この『○○な○○』という名前を聞いたとき、身体のどこに反応がありましたか？　胸が締め付けられた / 喉が詰まった / お腹が温かくなった ── 何でもいい。読み合わせフェーズで、その身体反応を一緒に解読しましょう」を 1 段落で配置
6. **偏愛（env-condition と同じテキスト形式・260507 v5.3 改修・260510 v0.4 で HP/OP 二軸追加）**— 譲れない好み 2 つと絶対に選ばない嫌い 1 つを `env-condition` クラスで提示。見出しは「偏愛：譲れない好みと、絶対に選ばない嫌い」
   - **★ 260510 v0.4 新規：偏愛の質判定（HP/OP）副次表示**（出典：Vallerand 2003）：
     - **HP（調和的情熱・自律的内面化）**：その偏愛は「手放したら自由になる」感覚 ／ 健全な適応を促進
     - **OP（強迫的情熱・制御的内面化）**：その偏愛は「手放したら自分が崩れる」感覚 ／ 否定的感情・頑固な固執を引き起こす
     - transcript から判定し、1 文で「あなたの偏愛は **[HP / OP]** タイプ」と表示
     - **OP 型 → 偏愛ズレ型のサブカテゴリ「OP 型偏愛ズレ」として Coaching 必須シグナル**
7. 時間軸の補強（p.time-axis で控えめ引用スタイル）— 対話内の表現をそのまま使う（年数計算しない）

### 【Block A 廃止項目（260507 v5.3）】
- ❌ 才能の発火/停止条件（env-condition）── 経営者向けには過剰情報のため削除。発火/停止条件は SYSTEM プロンプト内部分析素材としては引き続き使用するが、レポート出力には載せない

### 【Block B：引力の解剖】（意外性）
1. [起承] 表層タイプの肯定（通常段落1つ）
2. ★一撃2：認知OS書き換え（通常段落1つ・strong強調）
3. [深掘り] 1エピソード異常深掘り（通常段落1つ）
4. 引力の核（gravity-core）— 源泉=死角の同一動作を作用/副作用で表現
5. 自己洗脳の指摘（通常段落1つ）— 最も鋭い1つだけ

### 【Block C：本来に戻すための一手】（オチ・経営インパクト紐付け・260507 v5.3.1 順序再構築・260510 v0.4 で 4 次元副次診断追加）
1. **★統合マップ（gravity-integration）**— Block C の冒頭。3 要素整合解剖と引力の核・判定・最大リスクを初出しで提示
2. **【NEW】経営インパクト（business-impact-box・★商品.md SSOT 整合）**
   - **採用 / 組織 / 発信 の 3 軸**（商品.md 1 文 SSOT 整合）
   - 各軸 Before（現状）/ After（整合後）で 1-2 行・具体ベネフィット型
3. **★一撃3：analyst-note（最大リスク・石井一人称「正直に言うと〜」）**── ★260507 v5.3.1 順序変更：haveto-card の前に移動。「現状把握 → 警告」の流れを作る
4. **have to + 嘘 + 剥がした先（haveto-card）**── analyst-note の警告を受けた具体的な剥がし方
5. **5年後シナリオ（future-box）**── 剥がした先のビジョン（剥がし版のみ）。Block C 後半をポジティブで締める
6. 4型判定（type-judgment）── 推奨型確定
7. **★ 260510 v0.4 新規：真正リーダーシップ 4 次元副次診断（authentic-leadership-box）**
   - 出典：Walumbwa et al. 2008（Journal of Management・3,720+ 引用）
   - **4 次元のうち、4 型判定（整合 / Why ズレ / 才能ズレ / 偏愛ズレ）に応じて最も弱い 1-2 次元を特定**：
     - 自己認識（Self-Awareness）── 自分の強み・弱み・価値観・他者への影響を理解する力
     - 関係透明性（Relational Transparency）── 他者に対して本心を開示する力
     - バランス処理（Balanced Processing）── 多様な視点を客観的に処理する力
     - 内在化された道徳観（Internalized Moral Perspective）── 自身の倫理基準で行動する力
   - **配置：** type-judgment の直後・path-cards の前に小ボックス（10pt 未満・1 段落）として表示
   - **目的：** 「本来に戻すための一手」を 3 要素整合だけでなく **4 次元のどこに介入するか**で具体化
8. path-cards（判定型と連動）── 次の一手
9. final-question（即答不能の問い）
10. ★ 理論背景（theory-background-box・260508 夜 追加・closing-note の直前）
11. closing-note（石井一人称・締め）
12. report-footer

**★ 理論背景（theory-background-box）の HTML 構造：**

```
<div class="theory-background-box">
  <h4>このレポートの理論背景</h4>
  <p class="theory-intro">Gravity CODE が定義する「個人引力」は、<strong>Authentic Self（Why × 才能 × 偏愛の 3 要素整合）が Emotional Contagion（感情伝染）を通じて他者を引きつける力</strong>です。Self-Efficacy（自己効力感）とは別概念として、GrowthFix の 50 社診断 + 16 年人事キャリアの現場知見と、組織心理学・教育心理学・認知言語学・コーチング研究などの先行研究を編集して構築した独自フレームで経営者の引力タイプを解読します。</p>
  <p class="theory-intro" style="margin-top:14px;font-weight:600;color:#475569;">個人引力の理論基盤（Phase 11 確定・260510）</p>
  <ul class="theory-list">
    <li><strong>Why = Calling + Mission</strong>── 「自分はこのために生まれた」+「経営者として果たすべき使命」の二層構造（Wrzesniewski et al., 1997 ／ Bill George, 2003 <em>Authentic Leadership</em>）</li>
    <li><strong>才能 = Innate Talent + Flow + Self-Efficacy 成功体験</strong>── 持って生まれた素質に没入経験と成功体験が重なって発火する領域（Csikszentmihalyi, 1990 <em>Flow</em> ／ Bandura, 1977 <em>Self-Efficacy</em>）</li>
    <li><strong>偏愛 = Harmonious Passion + Intrinsic Motivation</strong>── 自己と統合された深い愛着と内発動機（Vallerand et al., 2003 ／ Deci &amp; Ryan, 2000 SDT）</li>
    <li><strong>Authentic Self → Emotional Contagion → 個人引力</strong>── 偽りのない自己が感情を伝染させ、他者の認知・行動に変化を起こすメカニズム（Hatfield, Cacioppo &amp; Rapson, 1994 ／ Barsade, 2002 <em>Administrative Science Quarterly</em>）</li>
    <li><strong>真正リーダーシップ 4 次元副次診断</strong>── 自己認識 / 関係透明性 / バランス処理 / 内在化された道徳観（Walumbwa et al., 2008 <em>Journal of Management</em>・3,720+ 引用）</li>
  </ul>
  <p class="theory-intro" style="margin-top:14px;font-weight:600;color:#475569;">独自フレーム（GrowthFix 50 社診断由来）</p>
  <ul class="theory-list">
    <li><strong>能力の輪（マンガー応用）</strong>── 内側 vs 外側の輪を識別し、本来の強みを発火させる思考フレーム（関連研究：Ericsson, 2004 / Baker, Côté &amp; Deakin, 2005）</li>
    <li><strong>キャラ命名手法</strong>（矛盾を抱えた一語化）── 経営者本人すら言語化できなかった引力構造を 1 文で凝縮（関連研究：Lakoff &amp; Johnson, 1980 / Rakova, 2003）</li>
    <li><strong>have to 検出と本来に戻す一手</strong>── 社会から埋め込まれた "やらねば" を解体し、自然に湧き出る動詞に戻す（関連研究：Vansteenkiste &amp; Ryan, 2013 / Van den Broeck et al., 2021 メタ分析）</li>
    <li><strong>コーチング × コンサルティング × ソマティクス</strong>── 石井 16 年の実践で統合した対話手法（関連研究：Jones, Woods &amp; Guillaume, 2015 メタ分析 / Dyrbye et al., 2019 JAMA RCT）</li>
  </ul>
  <p class="theory-note">★ 各論文の詳細・APA フル引用・反論論文への応答は WhitePaper V10（Q4 公開予定）で展開。50 社現場 60% : 学術 40% の比率原則で運用。<strong>個人引力 ≠ Self-Efficacy</strong>：個人引力は石井独自概念として Self-Efficacy（自己効力感）から明確に区別。</p>
</div>
```

**書き方ルール：**
- 5 項目は固定文言（経営者ごとにカスタマイズしない）
- closing-note の直前に表示（位置固定）

**Block C 流れ（260507 v5.3.1）：**「整理（統合）→ 現状（経営インパクト）→ 警告（analyst-note）→ 解決（haveto-card）→ 未来（future-box）→ 推奨（type-judgment + path-cards）→ 問い（final-question）→ 締め（closing-note）」── 感情カーブ：解剖完了 → 客観把握 → 危機感 → 解決策 → 希望 → 行動 → 余韻

## 4 型判定（Block C で必ず明示・260430 A' 案・整合度ベース＋偏愛追加）

Why × 才能 × 偏愛 の三角形の整合性から判定：

- **整合型**：3 要素すべて整合 → 推奨：**Gravity Scan**（組織の引力タイプ診断・Pre-Shift 適合診断・260430 リブート）
- **Why ズレ型**：Why が借り物になっている／社会的期待に塗り替えられている → 推奨：**Gravity Coaching**（先に Why を整える）
- **才能ズレ型**：自然な動きで動けていない／才能が発火する環境にいない（旧「動詞ズレ型」「環境ズレ型」を統合）→ 推奨：**Gravity Coaching**（先に才能を本来のものに戻す）
- **偏愛ズレ型**：譲れない好みではなく、社会の期待で判断軸が形成されている → 推奨：**Gravity Coaching**（先に偏愛軸を整える）

★Scan 推奨は「整合型」のみ。3 つのズレ型は Coaching で個人を整えてから Scan → Gravity Recruit / Cultivate / Shift に進むのが王道。
★ラベル表記は必ず「整合型／Why ズレ型／才能ズレ型／偏愛ズレ型」のいずれかで出力。旧ラベル（動詞ズレ型・環境ズレ型）は禁止。

## サービス記載の正確ルール（★厳守★）

path-cards の説明文では、以下の正確な情報を使うこと：

- **Gravity Coaching**：90 分 × 月 1 回 × 6 ヶ月（全 6 回）／ 38 万円（税込・6 ヶ月一括・Gravity CODE 付き）／ 社会から埋め込まれた have to を抜き、本来の判断軸を取り戻す 6 ヶ月の継続対話
- **Gravity Scan**（260430 リブート版・組織の引力タイプ診断・Pre-Shift 適合診断）：60 分の対面セッションで、組織の引力タイプを 4 型（整合型／拡散型／渇望型／不毛型）で判定し、集まる × 躍動 の 2 マトリクスにプロット。Gravity Recruit／Cultivate／Shift のどれが効くかを示す Pre-Shift 適合診断／10 万円
- **Gravity Shift R**（採用基盤・第 1 フェーズ主軸）：3 ヶ月の採用基盤実装プログラム。Week 1-2 で採用 4 軸（採用基準・面接プロセス・採用後評価軸・幹部役割分担）＋面接ブループリント 5 要素を共同制作（旧 Blueprint v6.0 から移管）、Week 3-12 で実装まで伴走／80 万円
- **Gravity Cultivate**（内：Shift C・260505 Activate から変更・躍動組織・第 2 フェーズ主軸）：3 ヶ月の躍動組織実装プログラム。AI × 人事データ × エンゲージメント設計／80 万円
- **Gravity Shift**（内：Shift Full・R+C 複合パッケージ・minimal LP・商談時提案）：6 ヶ月で R+C 順次実装／150 万円（10 万割引）
- **セルフリファイン**：レポートを定期的に見返し、3 要素の整合性を自己チェック

★「90 日」「3 ヶ月の Coaching」「90 分× 週 1」「Blueprint」「採用口説きブループリント」「設計の参謀」等の誤記・旧サービス名は厳禁。Coaching = 必ず「90 分 × 月 1 回 × 6 ヶ月」で記載
★ 整合型からの動線は **CODE → Scan → Gravity Recruit / Cultivate / Shift → Orbit**（Coaching は並行可）。Blueprint は 260430 夕廃止（採用 4 軸＋面接ブループリント 5 要素は Gravity Recruit Week 1-2 納品物に移管済）

## 絶対に書かないこと

- ❌ 冒頭の「私、石井伸幸は〜」権威署名
- ❌ 「国旗」「設計図」「アイデンティ」等の他サービス用語
- ❌ 「私はあなたを○○と名付ける」構文
- ❌ 8型マトリクス
- ❌ 現状コスト3種
- ❌ 5年後の放置シナリオ
- ❌ 引力の源泉と死角の別記述（引力の核に統合）
- ❌ filter-grid
- ❌ お世辞・「かもしれません」等
- ❌ 勝手に計算した年数
- ❌ `<style>` タグ・`style=""` 属性・外側HTML・コードフェンス
- ❌ **【260507 v5.3 廃止】才能の発火条件・才能が停止する場の env-condition セクション**（経営者向けには過剰情報。発火/停止条件は内部分析に留める）
- ❌ **【260507 v5.3 廃止】偏愛 verb-map / passion-map 図化**（偏愛はテキスト型 env-condition 形式で出力）
- ❌ **【260507 v5.3.2 改修】gravity-definition-box の本文出力**（引力定義は Cover Page に移管・サーバ側で自動付与・AI 出力には含めない）
- ❌ **【260507 v5.3 必須】Block C business-impact-box の省略**（必ず gravity-integration の直後に配置・採用/離脱/躍動 3 軸の Before/After）
- ❌ **【260507 v5.3 必須】Why 文章内に「能力」と「才能」を混在**（同義語的な使用は禁止・主語と動詞を明確に）

## HTML構造（★この構造をそのまま出力★・260507 v5.3.2：Block A から開始）

★ Cover Page（表紙＋引力定義）はサーバ側で自動付与されるため、AI は出力しない。
★ AI 出力の最初の文字は `<div class="section">`（Block A 冒頭）から始める。

<div class="section">
  <div><span class="section-num">01</span><h2 class="section-title">あなたの引力タイプ</h2></div>
  <div class="section-line"></div>
</div>

<div class="why-declaration">
  <div class="why-label">あなたの引力の源（Why）</div>
  <p class="why-text">[「[誰の][何] を、[動詞] するために、[何] を作り続ける」型で 1 行。「能力」と「才能」を混在させない。動作主と対象を明確に]</p>
</div>

<p>[Block A の導入段落]</p>

<h4 style="margin: 24px 0 8px; font-size: 13pt; color: #0f172a;">才能：自然にできてしまう動き</h4>
<div class="verb-map">
  <div class="verb-map-item">
    <div class="verb-map-verb">[動詞1]</div>
    <div class="verb-map-source">[根拠1] ／ [根拠2]</div>
  </div>
  <div class="verb-map-item">
    <div class="verb-map-verb">[動詞2]</div>
    <div class="verb-map-source">[根拠1] ／ [根拠2]</div>
  </div>
  <div class="verb-map-item">
    <div class="verb-map-verb">[動詞3]</div>
    <div class="verb-map-source">[根拠1] ／ [根拠2]</div>
  </div>
</div>

<div class="core-quote">あなたは"[矛盾を含むキャラ名]"だ</div>

<h4 style="margin: 28px 0 8px; font-size: 13pt; color: #0f172a;">偏愛：譲れない好みと、絶対に選ばない嫌い</h4>
<div class="env-condition">
  <p><strong>譲れない好み：</strong>[譲れない好み 1] ／ [譲れない好み 2]</p>
  <p><strong>絶対に選ばない嫌い：</strong>[絶対に選ばない嫌い]</p>
</div>

<p class="time-axis">[時間軸の一撃：対話内の表現をそのまま使う]</p>

<div class="page-break"></div>

<div class="section">
  <div><span class="section-num">02</span><h2 class="section-title">引力の解剖</h2></div>
  <div class="section-line"></div>
</div>

<p>[起承：表層タイプの肯定段落]</p>

<p><strong>しかし、あなたが語った○○と○○を並べると、別の姿が見える。あなたは○○だと思っている。しかし実際は○○だ。</strong></p>

<p>[1エピソード異常深掘り段落]</p>

<div class="gravity-core">
  <h4>あなたの引力の核</h4>
  <p class="core-action">同じ動作：「[○○する]」</p>
  <div class="core-duality">
    <div class="core-effect"><strong>作用</strong>[○○として人を惹きつける]</div>
    <div class="core-sideeffect"><strong>副作用</strong>[同時に○○として人を離す]</div>
  </div>
  <p class="core-summary">同じ動作が引力にも引力漏れにも両方なっている。</p>
</div>

<p>[自己洗脳の指摘段落]</p>

<div class="page-break"></div>

<div class="section">
  <div><span class="section-num">03</span><h2 class="section-title">本来に戻すための一手</h2></div>
  <div class="section-line"></div>
</div>

<div class="gravity-integration">
  <h4>ここまでの統合：あなたの引力の構造</h4>
  <div class="gi-formula">
    <div class="gi-element">
      <span class="gi-label">WHY</span>
      <span class="gi-value">[Whyを1行短く]</span>
      <span class="gi-status">[整合/ズレ]</span>
    </div>
    <span class="gi-operator">×</span>
    <div class="gi-element">
      <span class="gi-label">才能</span>
      <span class="gi-value">[主要動詞 1-2 語]</span>
      <span class="gi-status">[整合/借り物]</span>
    </div>
    <span class="gi-operator">×</span>
    <div class="gi-element">
      <span class="gi-label">偏愛</span>
      <span class="gi-value">[譲れない好み 1 語]</span>
      <span class="gi-status">[整合/不整合]</span>
    </div>
  </div>
  <div class="gi-result">
    <span class="gi-arrow">↓</span>
    <p class="gi-core"><strong>引力の核：</strong>[Block B で解剖した1動作]</p>
  </div>
  <div class="gi-judgment">
    <span class="gi-arrow">↓</span>
    <p class="gi-type"><strong>判定：</strong>【[4 型のいずれか：整合型／Why ズレ型／才能ズレ型／偏愛ズレ型]】</p>
    <p class="gi-risk"><strong>最大リスク：</strong>[リスクを1文で短く]</p>
  </div>
  <p class="gi-reading-guide">ここから、本来の引力に戻すための具体的な一手を示す</p>
</div>

<div class="business-impact-box">
  <div class="bi-label">経営インパクト ── あなたの引力が経営に出ている形</div>
  <div class="bi-grid">
    <div class="bi-axis">
      <div class="bi-axis-name">採用</div>
      <p class="bi-before"><strong>Before：</strong>[現状の引力の使い方が、採用面接・採用基盤にこう出ている（1-2 行・具体）]</p>
      <p class="bi-after"><strong>After：</strong>[3 要素を整えるとこう変わる（1-2 行・具体）]</p>
    </div>
    <div class="bi-axis">
      <div class="bi-axis-name">組織</div>
      <p class="bi-before"><strong>Before：</strong>[現状の引力の使い方が、幹部離脱・定着・組織運営にこう出ている（1-2 行・具体）]</p>
      <p class="bi-after"><strong>After：</strong>[3 要素を整えるとこう変わる（1-2 行・具体）]</p>
    </div>
    <div class="bi-axis">
      <div class="bi-axis-name">発信</div>
      <p class="bi-before"><strong>Before：</strong>[現状の引力の使い方が、経営者の発信・言語化・対外メッセージにこう出ている（1-2 行・具体）]</p>
      <p class="bi-after"><strong>After：</strong>[3 要素を整えるとこう変わる（1-2 行・具体）]</p>
    </div>
  </div>
</div>

<div class="analyst-note">
  <p><strong>最大リスク：</strong>正直に言うと、あなたの引力が最も殺される環境は○○だ。今の経営にその兆候がある。このレポートが見つけた矛盾には、もう1層深い理由がある。それは60分では辿り着けなかった。</p>
</div>

<div class="haveto-card">
  <span class="haveto-tag">HAVE TO</span>
  <h4>[タイトル]</h4>
  <p><strong>あなたが自分についている嘘：</strong>[具体的記述]</p>
  <p><strong>剥がした先：</strong>[具体的記述]</p>
</div>

<div class="future-box">
  <h4>5年後、引力を取り戻したあなた</h4>
  <p>[具体的で魅力的な1段落]</p>
</div>

<div class="type-judgment">
  <div class="type-label">あなたの引力タイプ判定</div>
  <h3 class="type-name">【[整合型／Why ズレ型／才能ズレ型／偏愛ズレ型 のいずれか]】</h3>
  <p class="type-reason">[判定理由：対話内の発言2-3行]</p>
  <p class="type-prescription">→ あなたに最適な次の一手は【[推奨サービス]】</p>
</div>

<div class="path-cards">
  <div class="path-card path-card--recommended">
    <span class="path-badge">RECOMMENDED</span>
    <h4>[判定型の推奨サービス名（例：Gravity Coaching）]</h4>
    <p class="path-card-meta">[サービスの正確なスペック表記（例：90分 × 月1回 × 6ヶ月／全6回／38万円・税込・Gravity CODE付き）]</p>
    <p>[あなたの場合〜具体理由 2-3行]</p>
  </div>
  <div class="path-card path-card--small"><strong>[副次選択肢名]：</strong>[1行説明（正確なスペック含む）]</div>
  <div class="path-card path-card--small"><strong>セルフリファイン：</strong>このレポートを定期的に見返し、Why × 才能 × 偏愛 の整合性を自己チェックする。</div>
</div>

<div class="final-question">
  <div class="final-question-label">最後の問い</div>
  <p class="final-question-text">[YES/NOで即答できない強制選択型の問い]</p>
  <p class="final-question-caveat">この問いに30秒で即答できない場合、その盲点はすでに日常に溶け込んでいます。</p>
  <a href="https://growthfix.jp/gravity-coaching/" class="final-question-cta">Coaching体験セッション 30分無料 →</a>
</div>

<div class="closing-note">
  <p>私が見てきた経営者の中で、あなたのパターンは[○○]に近い。</p>
  <p>その人たちは、[○○]を手放したとき、本来の引力を取り戻した。</p>
  <p>あなたも、同じ道を歩めるはずだ。</p>
</div>

<div class="report-footer"><p><strong>YOUR GRAVITY CODE</strong> — あなたの引力の暗号</p></div>

★出力の最初の文字は `<div class="section">`、最後は `</div>`。それ以外は書かない。
SYSTEM;

// End of legacy prompt (unused; kept for reference)

if ($is_transcript_mode) {
    $user_prompt = <<<USER
以下の診断データを基に、Gravity CODEレポートのHTMLフラグメントを生成してください。

## クライアントの立場
{$role_guidance}{$pain_guidance}

## 選択回答（状況ベースの行動傾向）
{$choices_text}

## セッション録音のトランスクリプト（★最重要★ クライアント発言のみ分析対象）

### 抽出すべき観点（260507 v5.3 改修）
1. Why の宣言（「[誰の][何] を、[動詞] するために、[何] を作り続ける」型で 1 行・「能力」と「才能」を混在させない）
2. 才能の解剖（自然にできてしまう動詞 3 連鎖／3 番目は無意識にやっている行動＝伏線）
3. 偏愛（譲れない好み 2 つ + 絶対に選ばない嫌い 1 つ）── テキスト型で出力
4. キラーインサイト 1 つ（Block A/B/C を串刺す中核）
5. キャラ名（矛盾の圧縮・「うっ」と来る名前）
6. 1 エピソード異常深掘りの対象
7. 引力の核（源泉＝死角の同一動作）
8. 最も鋭い自己洗脳フレーズ
9. have to の「嘘」
10. **【v5.3 新規・商品.md SSOT 整合】経営インパクト 3 軸（採用 / 組織 / 発信 × Before/After）**── 解剖した引力の核が、現在の経営に「採用面接・組織運営・経営者の発信や言葉」にどう出ているか、3 要素を整えるとどう変わるかを各軸 1-2 行で具体化
11. 4 型判定（整合型／Why ズレ型／才能ズレ型／偏愛ズレ型）
12. 最大リスク
13. final-question

★内部分析素材として使うが**レポートには出力しない**項目（260507 v5.3 廃止）：
- 才能の発火条件・才能が停止する場（経営者向けには過剰情報・分析の判断材料としては保持）

### トランスクリプト全文
{$freetext_text}

---

生成ルール：
- 出力は **HTMLフラグメントのみ**。`<div class="section">`から始めて`</div>`で終わる
- `<style>`・`style=""`・外側HTML・コードフェンスは**一切書かない**
- 3つの一撃を Block A/B/C に配置
- 石井の一人称は analyst-note と closing-note の2箇所のみ
- 本文は主語なし断定構文
- 4 型判定（整合型／Why ズレ型／才能ズレ型／偏愛ズレ型）を Block C で明示
- キャラ名は**矛盾を含む**名前（褒め系は不可）

生成開始：
USER;
} else {
    $user_prompt = <<<USER
以下の診断データを基に、Gravity CODEレポートのHTMLフラグメントを生成してください。

## クライアントの立場
{$role_guidance}{$pain_guidance}

## 選択回答（状況ベースの行動傾向）
{$choices_text}

## 対話記録（★最重要★）
{$freetext_text}

---

生成ルール：
- 出力は **HTMLフラグメントのみ**。`<div class="section">`から始めて`</div>`で終わる
- `<style>`・`style=""`・外側HTML・コードフェンスは**一切書かない**
- 3つの一撃を Block A/B/C に配置
- 石井の一人称は analyst-note と closing-note の2箇所のみ
- 本文は主語なし断定構文
- 4型判定を Block C で明示
- キャラ名は**矛盾を含む**名前

生成開始：
USER;
}

// --- ジョブID即時返却 + fastcgi_finish_request → 背景処理へ（C-1 60s timeout 対策） ---
$base_url = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http')
    . '://' . $_SERVER['HTTP_HOST'];
$report_url = $base_url . dirname($_SERVER['REQUEST_URI']) . '/generate.php?report=' . $report_id;

write_status($report_id, [
    'status' => 'pending',
    'created_at' => time(),
], $reports_dir);

echo json_encode(['job_id' => $report_id, 'report_url' => $report_url]);

if (function_exists('fastcgi_finish_request')) {
    fastcgi_finish_request();
}
ignore_user_abort(true);
set_time_limit(300);

write_status($report_id, [
    'status' => 'running',
    'created_at' => time(),
], $reports_dir);

// --- Claude API 呼び出し（バックグラウンド実行・SYSTEM プロンプト prompt caching 有効） ---
$api_body = json_encode([
    'model' => 'claude-sonnet-4-5',
    'max_tokens' => 10000,
    'system' => [
        [
            'type' => 'text',
            'text' => $system_prompt,
            'cache_control' => ['type' => 'ephemeral'],
        ],
    ],
    'messages' => [
        ['role' => 'user', 'content' => $user_prompt],
    ],
], JSON_UNESCAPED_UNICODE);

$ch = curl_init('https://api.anthropic.com/v1/messages');
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => $api_body,
    CURLOPT_CONNECTTIMEOUT => 10,
    CURLOPT_TIMEOUT => 180,
    CURLOPT_HTTPHEADER => [
        'Content-Type: application/json',
        'x-api-key: ' . $ANTHROPIC_API_KEY,
        'anthropic-version: 2023-06-01',
    ],
]);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curl_error = curl_error($ch);
curl_close($ch);

if ($curl_error) {
    write_status($report_id, [
        'status' => 'error',
        'created_at' => time(),
        'error' => 'API通信エラー: ' . $curl_error,
    ], $reports_dir);
    exit;
}

if ($http_code !== 200) {
    error_log('Claude API error (HTTP ' . $http_code . '): ' . $response);
    write_status($report_id, [
        'status' => 'error',
        'created_at' => time(),
        'error' => 'レポート生成サービスに一時的な問題が発生しています。しばらく後に再試行してください。',
    ], $reports_dir);
    exit;
}

$data = json_decode($response, true);
$report_body = '';
foreach (($data['content'] ?? []) as $block) {
    if (($block['type'] ?? '') === 'text') {
        $report_body .= $block['text'];
    }
}

if (empty($report_body)) {
    write_status($report_id, [
        'status' => 'error',
        'created_at' => time(),
        'error' => 'レポートの生成に失敗しました',
    ], $reports_dir);
    exit;
}

// --- 外側HTML・CSS・コードフェンスの除去（AIが誤って出力した場合の保険） ---
$report_body = preg_replace('/^\s*```(?:html)?\s*\n?/i', '', $report_body);
$report_body = preg_replace('/\n?\s*```\s*$/i', '', $report_body);
$report_body = preg_replace('/<!DOCTYPE[^>]*>/i', '', $report_body);
$report_body = preg_replace('/<\/?html[^>]*>/i', '', $report_body);
$report_body = preg_replace('/<head>[\s\S]*?<\/head>/i', '', $report_body);
$report_body = preg_replace('/<\/?body[^>]*>/i', '', $report_body);
$report_body = preg_replace('/<style[^>]*>[\s\S]*?<\/style>/i', '', $report_body);
$report_body = preg_replace('/<meta[^>]*>/i', '', $report_body);
$report_body = preg_replace('/<title[^>]*>[\s\S]*?<\/title>/i', '', $report_body);
$report_body = preg_replace('/<link[^>]*>/i', '', $report_body);
$report_body = preg_replace('/<\/?div class="container"[^>]*>/i', '', $report_body);
$report_body = preg_replace('/\s*style="[^"]*"/i', '', $report_body);
$report_body = trim($report_body);

// --- ★ 公開語彙ハーネス（260508 追加・社内用語 → 対外語 機械置換）---
// AI が SYSTEM プロンプトの NG 用語禁止に従わなかった場合の最終保証。
$jargon_map = [
    'C-5 ネガティブ・ケイパビリティ第 1 次判定' => '経営者の覚悟確認',
    'C-5 ネガティブ・ケイパビリティ判定' => '経営者の覚悟確認',
    'C-5 ネガティブ・ケイパビリティ' => '経営者の覚悟（答えのない時間に留まる力）',
    'ネガティブ・ケイパビリティ判定' => '経営者の覚悟確認',
    'ネガティブ・ケイパビリティ' => '答えのない時間に結論を出さず留まる力',
    'C-5 中判定' => '覚悟確信度が中位',
    'C-5 低判定' => '覚悟確信度が低位',
    'C-5 高判定' => '覚悟確信度が高位',
    'C-5 判定' => '経営者の覚悟確認',
    'C-5' => '経営者の覚悟確認',
    'ドラムビート 4 周期表' => '組織運営のリズム設計（週次／月次／四半期／年次）',
    'ドラムビート' => '組織運営のリズム',
    '組織 OS 診断書 6 章' => '躍動土壌の設計図',
    '組織 OS 診断書' => '躍動土壌の設計図',
    '3 ヶ月予言の書' => '3 ヶ月後の到達ゴール書',
    '予言の書' => '3 ヶ月後の到達ゴール書',
    '採用基盤実装書 12 要素' => '採用基盤の体系的な設計図',
    '12 要素' => '採用基盤の体系的な設計図',
    '思想 3 ＋ 設計 4 ＋ 運用 5' => '採用に向き合う前提・採用の構造設計・採用の現場運用',
    '思想 3 + 設計 4 + 運用 5' => '採用に向き合う前提・採用の構造設計・採用の現場運用',
    '思想 3' => '採用に向き合う前提',
    '設計 4' => '採用の構造設計',
    '運用 5' => '採用の現場運用',
    '9 マス診断' => 'Why × 才能 × 偏愛の整合・ズレを解読する設計図',
    '9 マス' => 'Why × 才能 × 偏愛の解読',
    'B-22' => '組織が学べていない壁の診断',
    'B-21' => 'AI による組織透明性の診断',
    'B-11' => '幹部の熱量分布',
    'B-10' => '組織の喜びと痛みのマップ',
    'B-1' => '組織文化の現在地',
    'B-2' => '組織文化のタイプマップ',
    'タスクアセスメント' => '業務難易度の分析',
    '4 壁モデル' => '組織が学べていない壁の分析',
    'リスニングコンパス' => '応募者の声の構造化',
    'インタビュー 5 原則' => '面接の原則',
    'AI 時代の育成型採用論' => '優秀人材を育てる採用思想',
    '動く採用骨格 KPI' => '採用基盤の稼働 KPI',
    '動く採用骨格' => '動く採用基盤',
    '採用骨格' => '採用基盤',
    'Pull 型' => '直接申込なし',
    'Push 型' => '直接申込あり',
    'Coaching is not frontline 原則' => '',
    'Coaching is not frontline' => '',
    'スピーカー偏差値' => '訴求の独自性',
    '関係構築前提' => 'お話を伺ったうえで',
    'ハーネスエンジニアリング' => 'ルールの徹底化',
    'ハーネス' => 'ルール',
    'TDD 経営' => '',
    'RECODE' => '',
    '1 文 SSOT' => 'サービスの 1 文定義',
    '固化フェーズ' => '最後の 10 分の言語化',
    'minimal LP' => '',
    '接続装置' => '',
    '5 層モデル' => '',
    '物語アーク' => '',
    '信用装置' => '',
    '内部ブランド' => '',
    'カテゴリーデザイン' => '',
    'ファネル監査' => '',
    '言語マップ' => '',
    'クローバーモデル' => '',
    'スイートスポット' => '最も効きやすいタイプ',
    '4 型判定' => '4 つのタイプ判定',
    '4 型診断' => '4 つのタイプ診断',
    'スパーリング' => '対話',
    'Shift A' => 'Gravity Cultivate',
    'Shift R' => 'Gravity Recruit',
];
uksort($jargon_map, function($a, $b) { return strlen($b) - strlen($a); });
foreach ($jargon_map as $ng => $ok) {
    if ($ng !== '' && strpos($report_body, $ng) !== false) {
        $report_body = str_replace($ng, $ok, $report_body);
    }
}
$report_body = preg_replace('/、(\s*、)+/u', '、', $report_body);
$report_body = preg_replace('/（\s*）/u', '', $report_body);
$report_body = preg_replace('/  +/u', ' ', $report_body);

// --- page-break直前の閉じタグ自動補完 ---
// v5.1: AIの出力はフラットなセクション列挙（<div class="page">入れ子なし）のため、
// page-break前に余計な</div>を挿入しない。旧ロジックは.page wrapperを早期閉じさせて
// 03以降のpadding消失を引き起こしていたため削除。

// --- divタグの最終バランス調整 ---
$open_divs = preg_match_all('/<div[\s>]/i', $report_body);
$close_divs = preg_match_all('/<\/div>/i', $report_body);
$missing = $open_divs - $close_divs;
if ($missing > 0) {
    $report_body .= str_repeat('</div>', $missing);
} elseif ($missing < 0) {
    // 閉じタグが多すぎる場合は末尾から削除
    for ($i = 0; $i < abs($missing); $i++) {
        $report_body = preg_replace('/<\/div>\s*$/i', '', $report_body);
    }
}

// --- 共通CSS（問い直し装置）を取得 ---
require_once __DIR__ . '/../../shared/question_block_styles.php';
$question_block_css = get_question_block_css();

// --- フルHTMLレポートを生成 ---
$report_html = <<<HTML
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>YOUR GRAVITY CODE｜あなたの引力の暗号</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%230f172a'/><text x='16' y='22' text-anchor='middle' font-size='18' font-family='serif' fill='%23fff'>G</text></svg>">
<meta name="robots" content="noindex, nofollow">
<link rel="stylesheet" href="/assets/css/diagnose-report.css?v=20260512">
<link rel="stylesheet" href="/assets/css/diagnose-report-code.css?v=20260512">
<style>
  /* Executive 専用: verb-map 縦並びフロー上書き（260507 v5.3・横並びコードCSSを上書き） */
  .verb-map { display: flex; flex-direction: column; gap: 36px; margin: 20px 0 28px; padding: 24px 20px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; counter-reset: verb-num; }
  .verb-map-item { width: 100%; padding: 18px 22px; background: #fff; border: 2px solid #0f172a; border-radius: 10px; text-align: left; position: relative; counter-increment: verb-num; }
  .verb-map-item::before { content: counter(verb-num, decimal-leading-zero); position: absolute; top: -10px; left: 16px; background: #0f172a; color: #fff; font-size: 9pt; font-weight: 700; padding: 2px 10px; border-radius: 100px; letter-spacing: 0.08em; }
  .verb-map-item:nth-child(3)::before { content: counter(verb-num, decimal-leading-zero) " ・ UNCONSCIOUS"; background: #dc2626; }
  .verb-map-item:not(:last-child)::after { content: '\2193'; position: absolute; left: 50%; bottom: -32px; transform: translateX(-50%); font-size: 18pt; font-weight: 700; color: #0f172a; line-height: 1; }
  .verb-map-verb { display: block; font-size: 13pt; font-weight: 800; color: #0f172a; background: transparent; border: none; padding: 0; margin: 4px 0 10px; white-space: normal; letter-spacing: 0.02em; line-height: 1.5; }
  .verb-map-source { font-size: 9.5pt; color: #475569; line-height: 1.7; padding: 0; text-align: left; }
  {$question_block_css}
</style>
</head>
<body>
<button class="pdf-btn" onclick="window.print()">
  <svg viewBox="0 0 24 24"><path d="M19 8h-1V3H6v5H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zM8 5h8v3H8V5zm8 14H8v-4h8v4zm2-4v-2H6v2H4v-4c0-.55.45-1 1-1h14c.55 0 1 .45 1 1v4h-2z"/></svg>
  PDF保存
</button>
<div class="cover-page">
  <div class="cover-inner">
    <div class="cover-badge">SOURCE CODE ANALYSIS REPORT</div>
    <h1 class="cover-main-title">YOUR<br>GRAVITY<br>CODE</h1>
    <div class="cover-divider"></div>

    <div class="cover-gravity-def">
      <div class="cover-gravity-label">ここで言う「引力」とは</div>
      <p class="cover-gravity-body">人が離れない・自発的に動く「場の力」。<br>経営者の <strong>Why × 才能 × 偏愛</strong> の 3 要素の整合から生まれる。</p>
      <div class="cover-gravity-duality">
        <div class="cover-gravity-positive"><span class="cgd-tag">整合</span><span class="cgd-arrow">→</span><span class="cgd-text">人が集まり、幹部が躍動する</span></div>
        <div class="cover-gravity-negative"><span class="cgd-tag">ズレ</span><span class="cgd-arrow">→</span><span class="cgd-text">採用しても定着しない・優秀な幹部が辞める</span></div>
      </div>
      <p class="cover-gravity-claim">事業の天井は、経営者の引力の天井である。</p>
    </div>

    <div class="cover-meta"><strong>Gravity CODE</strong><span class="cm-divider">／</span>GrowthFix</div>
  </div>
</div>
<div class="page">
{$report_body}
</div>
</body>
</html>
HTML;

// レポートをファイルに保存
file_put_contents($REPORT_FILE, $report_html);

// ジョブ完了ステータスを書き込む（非同期完了通知・C-1 fastcgi_finish_request 対応）
write_status($report_id, [
    'status' => 'done',
    'created_at' => time(),
    'report_url' => $report_url,
], $reports_dir);
