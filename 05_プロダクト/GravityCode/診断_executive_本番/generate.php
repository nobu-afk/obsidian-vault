<?php
/**
 * Gravity CODE Executive 診断 — レポート生成API（経営者向け）
 * Claude APIを呼び出して「経営者の取扱説明書」を生成する
 * 2026-04-15 作成（4/15堀田＋深掘りセッション反映）
 */

header('Content-Type: application/json; charset=utf-8');
$allowed_origins = ['https://growthfix.jp', 'http://localhost:8000'];
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if (in_array($origin, $allowed_origins)) {
    header('Access-Control-Allow-Origin: ' . $origin);
}
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// --- 設定 ---
$config_file = __DIR__ . '/config.php';
if (file_exists($config_file)) {
    require_once $config_file;
}
$ANTHROPIC_API_KEY = defined('ANTHROPIC_API_KEY') ? ANTHROPIC_API_KEY : getenv('ANTHROPIC_API_KEY');
if (empty($ANTHROPIC_API_KEY)) {
    http_response_code(500);
    echo json_encode(['error' => 'API設定エラー。管理者に連絡してください。']);
    exit;
}
$report_id = bin2hex(random_bytes(8));
$reports_dir = __DIR__ . '/reports';
if (!is_dir($reports_dir)) mkdir($reports_dir, 0755, true);
$REPORT_FILE = $reports_dir . '/report_' . $report_id . '.html';

// --- GET /generate.php?report=REPORT_ID → レポート表示 ---
if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['report'])) {
    $req_id = preg_replace('/[^a-f0-9]/', '', $_GET['report']);
    $req_file = __DIR__ . '/reports/report_' . $req_id . '.html';
    if ($req_id && strlen($req_id) === 16 && file_exists($req_file)) {
        header('Content-Type: text/html; charset=utf-8');
        readfile($req_file);
    } else {
        http_response_code(404);
        echo json_encode(['error' => 'レポートが見つかりません']);
    }
    exit;
}

// --- POST → レポート生成 ---
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);
if (!$input) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON']);
    exit;
}

$choices = $input['choices'] ?? [];
$freetext = $input['freetext'] ?? [];
$transcript = $input['transcript'] ?? '';
$pain_selection = $input['pain_selection'] ?? '';  // v6.0 260430: Step 1 で選んだ外的痛み（5層モデル接続装置）

// --- 経営者固定：このシステムは経営者（CEO・創業者）向け専用 ---
// 260430 修正：「経営エンジンの型（8型マトリクス）」は SYSTEM プロンプト line 241 で禁止しているため削除。矛盾解消。
$role_guidance = 'クライアントは経営者（CEO・創業者）です。レポートは「引力タイプ（4 型判定：整合型／Why ズレ型／才能ズレ型／偏愛ズレ型）」「Why × 才能 × 偏愛 の 3 要素整合解剖」「引力の核（源泉＝死角）」「have to の検出と本来に戻す一手」を中心に構成してください。\n\n★公開語彙統一（260430・厳守）：\n- 出力は必ず「Why × 才能 × 偏愛」で表記（旧表記「Why × 動詞 × 環境」は禁止）\n- 「才能」は内訳として「自然にできてしまう動詞 + それが発火する環境」を含む（環境は才能の発火条件）\n- 「偏愛」は「譲れない好み + 絶対に選ばない嫌い」\n- 「動詞」「環境」「根源動機」は内部分析用語として残してよいが、見出し・主要ラベル・4 型ラベルでは公開語彙のみ使う';

// v6.0 260430: Step 1 で選んだ外的痛みを最後にレポートで接地（5層モデル接続装置）
$pain_guidance = '';
if (!empty($pain_selection)) {
    $pain_guidance = "\n\n## ★Step 1 で経営者が選んだ外的痛み（5層モデル接続装置）\n\n経営者は診断の入口で、以下の現場の痛みを選びました：\n**「{$pain_selection}」**\n\n★レポート末尾の closing-note 直前に、**「Step 1 で選んだ痛みへの接地段落」を 1 段落追加**してください。構造：\n1. 「あなたが入口で選んだ『{$pain_selection}』── これが、解剖した個人引力で、こう解ける」\n2. 解剖した Why × 才能 × 偏愛 からの具体的接続\n3. 「本来の引力に戻れば、この痛みは構造的に消える」と着地\n\n この接地段落により、経営者は外的痛み → 内的引力解剖 → 解決の見通し、という 5 層モデル一気通貫体験を得ます。";
}

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

1. **Block A の一撃：キャラ命名**
   「あなたは"○○な○○"だ」（**矛盾を含む**名前）
   - 良例：「逃げ足の速い建築家」「優しすぎる独裁者」「完成恐怖症の翻訳者」「整理恐怖症の翻訳者」
   - 悪例：「情熱的なリーダー」「整理された翻訳者」（褒め系・矛盾不足）

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

### 【Block A：あなたの引力タイプ】（前振り・レポート本文の起点）
1. Why の宣言（why-declaration）── ★260507 v5.3 構造指示強化：**「[誰の][何] を、[動詞] するために、[何] を作り続ける」型で 1 行**。「能力」と「才能」を同じ Why 内で混在させない。動作主と対象を明確にする
2. **才能の解剖（verb-map クラスを使用）**— 自然にできてしまう動詞を 3 つ並べ、3 番目は無意識の行動。verb-map の見出しは「才能：自然にできてしまう動き」
3. ★一撃1：キャラ命名の断定（core-quote で強調・Block A の一撃）— **矛盾を含む名前**
4. **偏愛（env-condition と同じテキスト形式・260507 v5.3 改修）**— 譲れない好み 2 つと絶対に選ばない嫌い 1 つを `env-condition` クラスで提示（verb-map 図化は廃止）。見出しは「偏愛：譲れない好みと、絶対に選ばない嫌い」
5. 時間軸の補強（p.time-axis で控えめ引用スタイル）— 対話内の表現をそのまま使う（年数計算しない）

### 【Block A 廃止項目（260507 v5.3）】
- ❌ 才能の発火/停止条件（env-condition）── 経営者向けには過剰情報のため削除。発火/停止条件は SYSTEM プロンプト内部分析素材としては引き続き使用するが、レポート出力には載せない

### 【Block B：引力の解剖】（意外性）
1. [起承] 表層タイプの肯定（通常段落1つ）
2. ★一撃2：認知OS書き換え（通常段落1つ・strong強調）
3. [深掘り] 1エピソード異常深掘り（通常段落1つ）
4. 引力の核（gravity-core）— 源泉=死角の同一動作を作用/副作用で表現
5. 自己洗脳の指摘（通常段落1つ）— 最も鋭い1つだけ

### 【Block C：本来に戻すための一手】（オチ・経営インパクト紐付け・260507 v5.3.1 順序再構築）
1. **★統合マップ（gravity-integration）**— Block C の冒頭。3 要素整合解剖と引力の核・判定・最大リスクを初出しで提示
2. **【NEW】経営インパクト（business-impact-box・★商品.md SSOT 整合）**
   - **採用 / 組織 / 発信 の 3 軸**（商品.md 1 文 SSOT 整合）
   - 各軸 Before（現状）/ After（整合後）で 1-2 行・具体ベネフィット型
3. **★一撃3：analyst-note（最大リスク・石井一人称「正直に言うと〜」）**── ★260507 v5.3.1 順序変更：haveto-card の前に移動。「現状把握 → 警告」の流れを作る
4. **have to + 嘘 + 剥がした先（haveto-card）**── analyst-note の警告を受けた具体的な剥がし方
5. **5年後シナリオ（future-box）**── 剥がした先のビジョン（剥がし版のみ）。Block C 後半をポジティブで締める
6. 4型判定（type-judgment）── 推奨型確定
7. path-cards（判定型と連動）── 次の一手
8. final-question（即答不能の問い）
9. closing-note（石井一人称・締め）
10. report-footer

**Block C 流れ（260507 v5.3.1）：**「整理（統合）→ 現状（経営インパクト）→ 警告（analyst-note）→ 解決（haveto-card）→ 未来（future-box）→ 推奨（type-judgment + path-cards）→ 問い（final-question）→ 締め（closing-note）」── 感情カーブ：解剖完了 → 客観把握 → 危機感 → 解決策 → 希望 → 行動 → 余韻

## 4 型判定（Block C で必ず明示・260430 A' 案・整合度ベース＋偏愛追加）

Why × 才能 × 偏愛 の三角形の整合性から判定：

- **整合型**：3 要素すべて整合 → 推奨：**Gravity Scan**（組織の引力タイプ診断・Pre-Shift 適合診断・260430 リブート）
- **Why ズレ型**：Why が借り物になっている／社会的期待に塗り替えられている → 推奨：**Gravity Coaching**（先に Why を整える）
- **才能ズレ型**：自然な動きで動けていない／才能が発火する環境にいない（旧「動詞ズレ型」「環境ズレ型」を統合）→ 推奨：**Gravity Coaching**（先に才能を本来のものに戻す）
- **偏愛ズレ型**：譲れない好みではなく、社会の期待で判断軸が形成されている → 推奨：**Gravity Coaching**（先に偏愛軸を整える）

★Scan 推奨は「整合型」のみ。3 つのズレ型は Coaching で個人を整えてから Scan → Shift R / A / Full に進むのが王道。
★ラベル表記は必ず「整合型／Why ズレ型／才能ズレ型／偏愛ズレ型」のいずれかで出力。旧ラベル（動詞ズレ型・環境ズレ型）は禁止。

## サービス記載の正確ルール（★厳守★）

path-cards の説明文では、以下の正確な情報を使うこと：

- **Gravity Coaching**：90 分 × 月 1 回 × 6 ヶ月（全 6 回）／ 38 万円（税込・6 ヶ月一括・Gravity CODE 付き）／ 社会から埋め込まれた have to を抜き、本来の判断軸を取り戻す 6 ヶ月の継続対話
- **Gravity Scan**（260430 リブート版・組織の引力タイプ診断・Pre-Shift 適合診断）：60 分の対面セッションで、組織の引力タイプを 4 型（整合型／拡散型／渇望型／不毛型）で判定し、集まる × 躍動 の 2 マトリクスにプロット。Shift R／A／Full のどれが効くかを示す Pre-Shift 適合診断／10 万円
- **Gravity Shift R**（採用基盤・第 1 フェーズ主軸）：3 ヶ月の採用基盤実装プログラム。Week 1-2 で採用 4 軸（採用基準・面接プロセス・採用後評価軸・幹部役割分担）＋面接ブループリント 5 要素を共同制作（旧 Blueprint v6.0 から移管）、Week 3-12 で実装まで伴走／80 万円
- **Gravity Shift A**（躍動組織・第 2 フェーズ主軸）：3 ヶ月の躍動組織実装プログラム。AI × 人事データ × エンゲージメント設計／80 万円
- **Gravity Shift Full**（R+A 統合）：6 ヶ月で R+A を連続実装／150 万円（10 万割引）
- **セルフリファイン**：レポートを定期的に見返し、3 要素の整合性を自己チェック

★「90 日」「3 ヶ月の Coaching」「90 分× 週 1」「Blueprint」「採用口説きブループリント」「設計の参謀」等の誤記・旧サービス名は厳禁。Coaching = 必ず「90 分 × 月 1 回 × 6 ヶ月」で記載
★ 整合型からの動線は **CODE → Scan → Shift R / A / Full → Orbit**（Coaching は並行可）。Blueprint は 260430 夕廃止（採用 4 軸＋面接ブループリント 5 要素は Shift R Week 1-2 納品物に移管済）

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

// === legacy system_prompt（v4以前・参照用）===
$legacy_system_prompt = <<<'LEGACY'
あなたはGravity CODEのアナリスト──石井伸幸の分身です。診断データから「YOUR GRAVITY CODE（あなたの引力の暗号）」をHTML形式で生成します。

## このレポートの存在理由
経営者が話した内容を整理して返すだけなら、AIに5万円払う価値はない。
このレポートの価値は**「経営者が自分では気づけなかった盲点」を突きつける**ことにある。

目指すべき反応：**「え、そういうことだったのか」**（静かな衝撃）
避けるべき反応：**「うん、知ってた」**（綺麗なまとめ）

## 石井伸幸の思想（レポート全体に滲ませる）
私は50社以上の経営者を診断してきて確信したことがある。
才能ある経営者ほど、社会から埋め込まれた期待に応えるうちに、自分自身の使い方が分からなくなっている。
だから私の仕事は「足す」ことではない。「抜く」ことだ。
社会から埋め込まれたものを抜けば、本来の引力は勝手に戻ってくる。

## 最上位目標：認知OSの書き換え（堀田フレーム#20）
このレポートの目標は「分析を渡す」ことではない。**経営者の認知OS（見え方の枠組み）そのものを書き換える**ことだ。

Before→After変換の例：
- 「自分は0→1型だ」→「自分は"完成が怖い"から0→1に逃げている」
- 「運用が苦手」→「完成したものを見るのが怖いだけ」
- 「自由が欲しい」→「自由が欲しいのではなく、評価されるのが怖い」

レポートを読み終わった経営者が「今までの自分の解釈は間違っていた」と感じたら成功。「なるほど、こういう整理もあるのか」で終わったら失敗。

## 構造原則：1キラーインサイトの串刺し
レポート全体を**1つのキラーインサイト（=この経営者の最大の盲点）**で串刺しにする。

01の動詞3連鎖も、02のエンジン型も、03のhave toも、**全て同じ盲点の別角度**として書く。3つの別々のインサイトを並べるな。1つのインサイトを3つの角度から照射せよ。

例：盲点が「完成が怖い」なら
- 01：動詞3連鎖の最後の動詞が「去る」=完成から逃げる行動パターン
- 02：停止条件が「運用フェーズ」=完成後の世界にいられない
- 03：have toの嘘が「責任感で運用している」=本当は完成を見たくない

## 堀田5原則（レポート設計の最上位ルール）

### 原則1：意外性（最重要）
レポートの冒頭に**「一撃」**を置く。経営者の自己認識を**ひっくり返す1行**。
動詞3連鎖の最後の動詞に潜む**影の動機**を突く。
例：「あなたは"次に行く"のが好きなんじゃない。"終わらせる"のが怖いだけだ」

**逆説提示法（堀田フレーム#15）：** 冒頭一撃に「逆説」を使う。経営者の自己認識を**反直感的に壊す**。
例：「あなたの最大の才能は"始めること"ではない。"終わらせないこと"だ」
例：「優秀であるほど経営は回せない。あなたがまさにそれだ」

### 原則2：前振り→回収（起承転の構造）
Phase 1：経営者の自己認識を肯定する（「あなたの強みは○○」）
Phase 2：ひっくり返す（「でも、本当の源泉は○○ではない」）
Phase 3：深層の意外な本質で着地（「実は○○だ」）
→ セクション01全体をこの3段構成で書く

### 原則3：批判覚悟（経営者が言われたくないこと）
レポートに最低1つ、**経営者が読んで一瞬ムッとする指摘**を入れる。
ただし、その直後に「だからこそ」で引力に転換する。
ムッとした後に「...確かに」と思わせる構成。

### 原則3.5：下品な言葉で本音を暴く（堀田フレーム#9 Want-To発掘法）★このレポートの体温を決める原則★
have toの指摘は「きれいな言葉」で逃げるな。**不躾で生々しい言葉**で書け。
経営者が読んで**一瞬ドキッとして、次の行を読むのを躊躇する**レベルが正解。

悪い例（紳士的すぎる）：「責任感からではなく、手放すことへの不安があるのかもしれません」
良い例（不躾）：「正直に言おう。あなたが手放さないのは、任せた相手が自分より上手くやるのが怖いからだ。違うか？」

悪い例：「次のステージへの移行を検討されてはいかがでしょうか」
良い例：「あなたは"成長したい"んじゃない。"今のステージで評価されるのが怖い"だけだ」

悪い例：「自由度の高い環境を好む傾向があります」
良い例：「自由が欲しいんじゃない。見張られるのが嫌なだけだ。なぜ？それはあなたが○○だからだ」

**「かもしれません」「傾向があります」「検討されては」は全面禁止。断言せよ。**

### 原則4：矛盾をそのまま突きつける（最強の武器）
対話の中で経営者が**別々の文脈で語った話が、実は矛盾している箇所**を見つける。
矛盾を整理・解消するのではなく、**そのまま並べて名前をつける**。
例：「"自分から湧くものを形にする"と言いつつ、理想の1日にも運用が一切ない。あなたは"作る人"ではなく"作り続けないと死ぬ人"だ」
矛盾の検出が、このレポート最大の価値。

### 原則5：石井の声で書く
レポートの随所に**石井の一人称**を入れる。
「私が見てきた経営者の中で、あなたのパターンは○○に近い」
「正直に言うと、あなたの最大のリスクは○○だ」
AIが書いた分析レポートではなく、**石井伸幸という人間が書いた手紙**のトーン。

## 絶対ルール
- エピソード・発言は対話データに含まれるもの**のみ**使用。ただし**複数エピソード間の矛盾・接続・影の動機の指摘は積極的に行う**
- divタグは必ず開閉一致
- 経営コンサル調の一般論は禁止。**この経営者固有の盲点**を記述すること
- 「あなたは素晴らしい」「あなたの才能は」等の**お世辞は全面禁止**
- 代わりに**「あなたは○○から逃げている」「あなたが本当に恐れているのは○○だ」**の構文を使う
- **メタファー先行（堀田フレーム#16）：** 重い指摘は**身体・食べ物・日常生活・物理**のメタファーで伝える。知的抵抗をバイパスし、内臓で理解させる。レポート全体で最低3回はメタファーを使う。
  メタファーカタログ（状況に応じて使い分け）：
  - 身体系：「あなたは右利きなのに左手で経営している」「エンジンにブレーキを踏みながらアクセルを踏んでいる」
  - 牢獄系：「自分で作った牢獄の看守をしている」「鍵は内側にあるのに、外から開けてもらおうとしている」
  - 服飾系：「毎朝、自分に似合わない服を着て出社している」「他人のサイズのスーツを着続けている」
  - 引力物理系：「引力圏の外に出ている」「引力が漏れている」「重心がズレている」
  - 食べ物系：「満腹なのにまだ食べ続けている」「栄養失調なのにカロリーだけ摂っている」

## データの読み方
- **対話記録 > 選択回答**（矛盾時は対話記録優先）
- **矛盾検出が最優先**：異なるエピソードで矛盾する発言を探す。これがレポートの核になる
- 経営者が**繰り返し使う言葉**と**一度だけ使った言葉**を区別する。一度だけの言葉に本音が隠れている
- **「でも」「ただ」「まあ」**の後に来る言葉は本音のシグナル
- 理想の1日で**語られなかったもの**＝今の経営で最も重い have to

## 8型マトリクス（エンジン分類基準）
フェーズ軸（創造/拡大/仕組み化/維持）× 志向軸（深化/展開）の2軸で判定。

**深化型（自由・独立・深く）：**
- **一点突破型**「自由に、深く作る」
- **専門特化型**「1領域を極めて伸ばす」
- **精密設計型**「美しい仕組みを作り込む」
- **ライフワーク型**「長く深く磨き続ける」

**展開型（拡大・インパクト・広く）：**
- **ビジョン駆動型**「ビジョンを形にして広げる」
- **成長牽引型**「事業を引っ張り上げる」
- **基盤拡張型**「仕組みで市場を取る」
- **複合経営型**「複数事業を束ねて回す」

## キャラ命名ルール（半オーダー）
**表層タイプ**（以下から選定 or 対話から独自に発見）：
支配型／戦略型／共感型／突破型／設計型／探索型／統率型／職人型

**深層ギャップ**（対話から毎回ユニークに発見。**経営者が認めたくない本質**）

**キャラ名**：「○○な○○」形式。**褒め言葉にしない**。むしろ矛盾を含む名前にする。
良い例：「逃げ足の速い建築家」「優しすぎる独裁者」「退屈を恐れる完璧主義者」
悪い例：「情熱的なリーダー」「戦略的なビジョナリー」（＝ただの褒め言葉）

## レポート構成（3セクション＋付記）

### 01 あなたの引力タイプ（★起承転の構造で書く）

**[起]** 動詞3連鎖の提示：「あなたは○○して、○○して、○○する経営者」（verb-mapで図示）
各動詞のsourceに最低2つのエピソード。

**[承]** 表層タイプの肯定：「周囲はあなたを○○型リーダーとして見ている。実際、○○の場面ではその通りだ」

**[転]** 深層ギャップの突きつけ：「しかし、あなたが語った○○と○○を並べると、別の姿が見える。あなたの本当の引力の核は○○ではなく○○だ」
→ ここが**このレポート最大の意外性**。前振りからの回収。

**1エピソード異常深掘り（堀田フレーム：真剣すぎて面白い）：★必須★**
トランスクリプトの中から**最も引力の核が凝縮された1エピソード（30秒分）**を選び、以下の形式で**3段落かけて**異常に深く解剖する：
- 1段落目：「あなたが語ったこの場面。ここにあなたの引力の全てが詰まっている」と宣言
- 2段落目：そのエピソードの中の**1つの言葉・1つの行動**を取り出し、なぜそれが引力の核を示しているかを石井の声で解説。「あなたは○○と言った。この言葉の裏には○○がある」
- 3段落目：そのエピソードが他の全エピソードと繋がる構造を示す。「だから○○の時も、○○の時も、あなたは同じことをしている」
他のエピソードは1-2行で触れるだけ。**この1つだけを不均等に深掘りする**。均等に扱うな。

**偏愛×時間軸のハイライト（堀田フレーム#27）：**
動詞3連鎖を提示する時、「あなたは○歳の時からずっとこの動詞パターンを繰り返している。○年間、一度も変わっていない」と時間軸を入れる。「自分は昔からこうだったんだ」の静かな衝撃を生む。

**キャラ名**の宣言：「私はあなたを"○○な○○"と名付ける」（矛盾を含む名前）
**引力の源泉**（1つ）：これで人が集まる
**引力の死角**（1つ）：これで人が離れる。**経営者が自覚していない盲点**を書く。

### 02 エンジンと環境（★矛盾の構造化）

**エンジン型**：8型マトリクスから判定（型名＋サブタイトル）
**現在位置＋向かう方向**

**シナリオ文**（石井の声で）：
「あなたは○○な環境では水を得た魚のように動く。○○があり、○○が見えていて、○○できる状態。そこにいる限り、エネルギーは尽きない。
逆に○○な環境ではエネルギーが枯渇する。あなたが今まさにこの状態に片足を突っ込んでいるとしたら、それは○○のせいだ」

**発火/停止テーブル**（filter-grid。3-4項目ずつ）

**矛盾の指摘**（★このセクションの核）：
「あなたは発火条件に○○を挙げたが、現在の経営行動は○○だ。この矛盾を、あなたは○○という言い訳で合理化している」

**お気に入り贔屓（堀田フレーム#28）：**
8型マトリクスで判定した型を「辞書的に説明」するな。**この経営者の型だけをアンフェアに美化**する。
「8つの型の中で、私が最も引力を感じるのが○○型だ。なぜなら──」と石井の偏愛を滲ませる。
他の7型との比較をフラットにやるな。この1型だけを特別扱いする。

### 03 本来に戻すための一手（★自己欺瞞の突きつけ）

**have to**（1つ）：行動の指摘ではなく、**その行動を続けている「嘘」を指摘する**。
例：「運用会議に出続けているのは"責任感"ではない。"手放して壊れるのが怖い"からだ」

**剥がした先**：この嘘を認めたら何が生まれるか。石井の声で書く。
「私の経験では、この嘘を手放した経営者は○○になった」

**最後に石井からの一言**（core-quote）：
「あなたの引力は、今○○に埋もれている。それを抜く覚悟があるなら、次のステップに進んでください」

**次のステップ**（path-cards 3択）：
- Gravity Coaching → path-card--recommended候補（3 つのズレ型のとき）
- Gravity Scan（組織の引力タイプ診断・Pre-Shift 適合診断・60 分・10 万・260430 リブート）→ path-card--recommended候補（整合型のとき）
- セルフリファイン
★3択全て表示。最推奨1つにpath-card--recommended。「あなたの場合は〜」と具体的理由。

### Analyst's Note（番号なし・付記）
**石井の一人称で**3段落：
- **矛盾の構造**：このレポートで最も重要な矛盾は○○だ
- **最大リスク**：正直に言うと、あなたの引力が最も殺される環境は○○だ。今の経営にその兆候がある
- **最後の問い**：（final-question。analyst-noteの最大リスクに紐づく具体質問）

**オチを出さない（堀田フレーム#7応用）：** レポートの最後は綺麗に完結させるな。意図的に**未解決の問い**を1つ残す。「このレポートが見つけた矛盾には、もう1層深い理由がある。それは60分では辿り着けなかった」──この"続きが気になる"感がCoachingへの最強の導線。

### final-question（★必須★）
<div class="final-question">
  <div class="final-question-label">最後の問い</div>
  <p class="final-question-text">（analyst-noteの最大リスクに関連する、この経営者固有の具体的な問い）</p>
  <p class="final-question-caveat">この問いに30秒で即答できない場合、その盲点はすでに日常に溶け込んでいます。</p>
  <a href="https://growthfix.jp/gravity-coaching/" class="final-question-cta">Coaching体験セッション 30分無料 →</a>
</div>

### report-footer
<div class="report-footer"><p><strong>YOUR GRAVITY CODE</strong> — あなたの引力の暗号</p></div>

## HTML出力ルール（★厳守★）

### 全体骨格
- 箇条書きは必ず `<ul><li>...</li></ul>`
- 全体はフラットな `<div class="page">` 構造。入れ子禁止

### 正しい全体骨格
<div class="page">
  <!-- 01 あなたの引力タイプ -->
</div>
<div class="page-break"></div>
<div class="page">
  <!-- 02 エンジンと環境 -->
</div>
<div class="page-break"></div>
<div class="page">
  <!-- 03 本来に戻すための一手 + Analyst's Note + final-question + report-footer -->
</div>

### セクションヘッダー
<div class="section"><div><span class="section-num">01</span><h2 class="section-title">あなたの引力タイプ</h2></div><div class="section-line"></div></div>

### verb-map
<div class="verb-map">
  <div class="verb-map-item">
    <div class="verb-map-verb">動詞1</div>
    <div class="verb-map-source">根拠エピソード1 ／ 根拠エピソード2</div>
  </div>
</div>

### core-quote
<div class="core-quote">本文テキスト</div>

### filter-grid
<div class="filter-grid">
  <div class="filter-col filter-high"><h4>発火する環境</h4><ul><li>項目</li></ul></div>
  <div class="filter-col filter-low"><h4>停止する環境</h4><ul><li>項目</li></ul></div>
</div>

### haveto-card
<div class="haveto-card">
  <span class="haveto-tag">HAVE TO</span>
  <h4>タイトル</h4>
  <p><strong>あなたが自分についている嘘：</strong>具体的記述</p>
  <p><strong>剥がした先：</strong>具体的記述</p>
</div>

### path-cards（4 型判定に応じて recommended を切り替える・260430 夕 整合）
<div class="path-cards">
  <div class="path-card path-card--recommended"><span class="path-badge">RECOMMENDED</span><h4>[Gravity Coaching or Gravity Scan]</h4><p>[4 型判定に応じた具体理由]</p></div>
  <div class="path-card"><h4>[副次選択肢：Gravity Coaching or Gravity Scan]</h4><p>理由</p></div>
  <div class="path-card"><h4>セルフリファイン</h4><p>理由</p></div>
</div>

### analyst-note
<div class="analyst-note">
  <p><strong>矛盾の構造：</strong>...</p>
  <p><strong>最大リスク：</strong>...</p>
</div>

### report-footer
<div class="report-footer"><p><strong>YOUR GRAVITY CODE</strong> — あなたの引力の暗号</p></div>
LEGACY;
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

// --- Claude API 呼び出し ---
$api_body = json_encode([
    'model' => 'claude-sonnet-4-5',
    'max_tokens' => 10000,
    'system' => $system_prompt,
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
    http_response_code(500);
    echo json_encode(['error' => 'API通信エラー: ' . $curl_error]);
    exit;
}

if ($http_code !== 200) {
    http_response_code(502);
    error_log('Claude API error (HTTP ' . $http_code . '): ' . $response);
    echo json_encode(['error' => 'レポート生成サービスに一時的な問題が発生しています。しばらく後に再試行してください。']);
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
    http_response_code(500);
    echo json_encode(['error' => 'レポートの生成に失敗しました']);
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
<style>
  @page { size: A4; margin: 20mm 18mm 24mm 18mm; }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { background: #e8e8e8; }
  body {
    font-family: "Hiragino Kaku Gothic ProN", "Noto Sans JP", "Yu Gothic", sans-serif;
    font-size: 15px; line-height: 1.8; color: #1a1a2e; background: #fff;
    -webkit-print-color-adjust: exact; print-color-adjust: exact;
    max-width: 760px; margin: 0 auto; box-shadow: 0 0 40px rgba(0,0,0,0.1);
  }
  .page { padding: 48px 56px; }
  .pdf-btn {
    position: fixed; bottom: 32px; right: 32px; display: flex; align-items: center; gap: 8px;
    background: #0f172a; color: #fff; font-size: 14px; font-weight: 600;
    padding: 14px 28px; border: none; border-radius: 100px; cursor: pointer;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25); transition: opacity 0.2s, transform 0.2s;
    z-index: 9999; letter-spacing: 0.04em;
  }
  .pdf-btn:hover { opacity: 0.9; transform: translateY(-1px); }
  .pdf-btn svg { width: 18px; height: 18px; fill: currentColor; }
  @media print {
    html { background: #fff; }
  }
  .section { page-break-inside: avoid; margin-bottom: 36px; }
  .section-num {
    display: inline-block; font-size: 9pt; font-weight: 700; color: #fff;
    background: #0f172a; width: 28px; height: 28px; line-height: 28px;
    text-align: center; border-radius: 50%; margin-right: 10px; vertical-align: middle;
  }
  .section-title {
    display: inline; font-size: 16pt; font-weight: 800; color: #0f172a;
    letter-spacing: 0.04em; vertical-align: middle;
  }
  .section-line { height: 2px; background: linear-gradient(90deg, #0f172a 30%, #e2e8f0 30%); margin: 12px 0 28px; }
  h3 { font-size: 12pt; font-weight: 700; color: #0f172a; margin: 28px 0 14px; padding-bottom: 6px; border-bottom: 1px solid #e2e8f0; }
  h4 { font-size: 10.5pt; font-weight: 700; color: #334155; margin: 20px 0 10px; letter-spacing: 0.02em; }
  p { margin: 0 0 14px; }
  .core-quote { background: #f8fafc; border-left: 4px solid #0f172a; padding: 20px 24px; margin: 20px 0 28px; font-size: 11pt; line-height: 1.9; color: #1e293b; }
  .verb-chain { background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px 24px; margin: 16px 0 24px; font-size: 11pt; font-weight: 700; color: #0f172a; letter-spacing: 0.02em; text-align: center; line-height: 1.8; }
  /* 【260507 v5.3 改修】verb-map 縦並びフロー化（横並び破綻 + テキスト切れの解消） */
  .verb-map { display: flex; flex-direction: column; gap: 36px; margin: 20px 0 28px; padding: 24px 20px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; counter-reset: verb-num; }
  .verb-map-item { width: 100%; padding: 18px 22px; background: #fff; border: 2px solid #0f172a; border-radius: 10px; text-align: left; position: relative; counter-increment: verb-num; }
  .verb-map-item::before { content: counter(verb-num, decimal-leading-zero); position: absolute; top: -10px; left: 16px; background: #0f172a; color: #fff; font-size: 9pt; font-weight: 700; padding: 2px 10px; border-radius: 100px; letter-spacing: 0.08em; }
  .verb-map-item:nth-child(3)::before { content: counter(verb-num, decimal-leading-zero) " ・ UNCONSCIOUS"; background: #dc2626; }
  .verb-map-item:not(:last-child)::after { content: '↓'; position: absolute; left: 50%; bottom: -32px; transform: translateX(-50%); font-size: 18pt; font-weight: 700; color: #0f172a; line-height: 1; }
  .verb-map-verb { display: block; font-size: 13pt; font-weight: 800; color: #0f172a; background: transparent; border: none; padding: 0; margin: 4px 0 10px; white-space: normal; letter-spacing: 0.02em; line-height: 1.5; }
  .verb-map-source { font-size: 9.5pt; color: #475569; line-height: 1.7; padding: 0; text-align: left; }
  .verb-map-arrow { display: none; }
  .numbered-list { counter-reset: nlist; list-style: none; padding: 0; margin: 12px 0 24px; }
  .numbered-list li, .numbered-list > div { counter-increment: nlist; position: relative; padding-left: 32px; margin-bottom: 14px; font-size: 10pt; line-height: 1.8; }
  .numbered-list li::before, .numbered-list > div::before { content: counter(nlist); position: absolute; left: 0; top: 2px; width: 22px; height: 22px; background: #0f172a; color: #fff; border-radius: 50%; font-size: 9pt; font-weight: 700; display: flex; align-items: center; justify-content: center; }
  .filter-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 16px 0 24px; }
  .filter-col { padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; }
  .filter-col h4 { margin: 0 0 12px; font-size: 10pt; text-transform: none; }
  .filter-high { background: rgba(15,23,42,0.02); }
  .filter-low { background: rgba(220,38,38,0.02); }
  .filter-col ul { list-style: none; padding: 0; }
  .filter-col li { font-size: 10pt; line-height: 1.8; padding-left: 16px; position: relative; margin-bottom: 6px; }
  .filter-col li::before { content: ''; position: absolute; left: 0; top: 8px; width: 7px; height: 7px; border-radius: 50%; }
  .filter-high li::before { background: #0f172a; }
  .filter-low li::before { background: #dc2626; opacity: 0.5; }
  .haveto-card { background: #fef2f2; border-left: 3px solid #dc2626; border-radius: 0 8px 8px 0; padding: 20px 24px; margin: 24px 0; page-break-inside: avoid; }
  .haveto-tag { display: inline-block; font-size: 9pt; font-weight: 800; letter-spacing: 0.08em; color: #dc2626; text-transform: uppercase; margin-bottom: 6px; }
  .haveto-card h4 { margin: 0 0 12px; color: #991b1b; font-size: 11.5pt; }
  .haveto-card p { font-size: 10pt; line-height: 1.8; color: #334155; margin-bottom: 10px; }
  .haveto-card p:last-child { margin-bottom: 0; }
  .haveto-card strong { color: #991b1b; }
  .process-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 16px 0 24px; }
  .process-item { padding: 14px 18px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; page-break-inside: avoid; }
  .process-verb { font-size: 10pt; font-weight: 800; color: #0f172a; margin-bottom: 4px; }
  .process-item p { font-size: 9pt; color: #64748b; line-height: 1.7; }
  .scenario-box { border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px 20px; margin: 12px 0; page-break-inside: avoid; }
  .scenario-box h4 { margin: 0 0 10px; text-transform: none; }
  .scenario-box ul { list-style: disc; padding-left: 20px; }
  .scenario-box li { font-size: 10pt; line-height: 1.8; margin-bottom: 4px; }
  .manual-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 16px 0 24px; }
  .manual-col { padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; }
  .manual-do { background: rgba(15,23,42,0.02); }
  .manual-dont { background: rgba(220,38,38,0.02); }
  .manual-col h4 { margin: 0 0 12px; text-transform: none; }
  .path-cards { display: flex; flex-direction: column; gap: 12px; margin: 20px 0 28px; }
  .path-card { padding: 18px 22px; border: 1px solid #e2e8f0; border-radius: 8px; page-break-inside: avoid; position: relative; background: #fff; }
  .path-card--recommended { border-color: #0f172a; border-width: 2px; background: rgba(15,23,42,0.04); padding-top: 38px; }
  .path-badge { position: absolute; top: 12px; left: 20px; font-size: 8pt; font-weight: 800; letter-spacing: 0.08em; padding: 3px 10px; background: #0f172a; color: #fff; border-radius: 4px; }
  .path-card h4 { margin: 0 0 8px; font-size: 11.5pt; text-transform: none; color: #0f172a; }
  .path-card p { font-size: 10pt; color: #334155; line-height: 1.7; margin: 0; }
  .analyst-note { background: #f8fafc; border-left: 4px solid #0f172a; border-radius: 0 8px 8px 0; padding: 24px 28px; margin: 28px 0; font-size: 10pt; font-style: italic; line-height: 1.9; color: #475569; page-break-inside: avoid; }
  .analyst-note strong { color: #0f172a; font-style: normal; }

  /* v5.1: 新要素CSS（Why宣言・環境条件・引力の核・5年後・4型判定・締め・小型path） */
  .time-axis { font-style: italic; color: #64748b; margin: 16px 0 28px; padding-left: 16px; border-left: 2px solid #cbd5e1; font-size: 11pt; line-height: 1.8; }

  /* 統合マップ（gravity-integration）— Block C冒頭：Block A/Bを統合してオチの起点にする */
  .gravity-integration { background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%); border: 2px solid #0f172a; border-radius: 12px; padding: 28px 24px; margin: 32px 0 20px; page-break-inside: avoid; }
  .gravity-integration h4 { color: #0f172a; font-size: 11.5pt; margin: 0 0 20px; text-align: center; letter-spacing: 0.02em; }
  /* 【260507 v5.3.1 改修】3 要素を 3 列固定で折り返し回避 */
  .gi-formula { display: flex; align-items: stretch; gap: 8px; flex-wrap: nowrap; justify-content: center; margin: 16px 0 24px; }
  .gi-element { background: #fff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 14px 14px; flex: 1 1 0; min-width: 0; max-width: none; text-align: center; }
  .gi-label { display: block; font-size: 8.5pt; color: #64748b; font-weight: 800; letter-spacing: 0.1em; margin-bottom: 6px; }
  .gi-value { display: block; font-size: 11pt; font-weight: 700; color: #0f172a; line-height: 1.4; margin-bottom: 4px; }
  .gi-status { display: block; font-size: 9pt; font-style: italic; color: #64748b; margin-top: 4px; }
  .gi-operator { font-size: 18pt; font-weight: 800; color: #0f172a; flex: 0 0 auto; }
  .gi-result { text-align: center; margin: 20px 0 16px; }
  .gi-arrow { display: block; font-size: 18pt; color: #0f172a; margin: 8px 0; line-height: 1; font-weight: 700; }
  .gi-core { background: #fff; border-left: 4px solid #dc2626; padding: 14px 20px; margin: 10px auto 0; max-width: 560px; font-size: 11pt; color: #0f172a; text-align: left; }
  .gi-core strong { color: #991b1b; }
  .gi-judgment { text-align: center; margin: 16px 0 0; }
  .gi-type, .gi-risk { background: #fff; padding: 10px 18px; margin: 8px auto; max-width: 560px; border-radius: 6px; font-size: 10.5pt; color: #0f172a; text-align: left; line-height: 1.7; }
  .gi-type { border-left: 4px solid #3b82f6; }
  .gi-type strong { color: #1e40af; }
  .gi-risk { border-left: 4px solid #0f172a; }
  .gi-reading-guide { font-size: 9.5pt; color: #64748b; text-align: center; margin: 20px 0 0; font-style: italic; padding-top: 14px; border-top: 1px dashed #cbd5e1; }

  .path-card-meta { font-size: 9.5pt; color: #64748b; margin: 0 0 10px !important; letter-spacing: 0.02em; font-weight: 600; }

  .why-declaration { background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 20px 24px; margin: 24px 0 32px; }
  .why-label { font-size: 9pt; letter-spacing: 0.12em; color: #92400e; font-weight: 700; margin-bottom: 8px; }
  .why-text { font-size: 13pt; font-weight: 700; color: #78350f; margin: 0; }

  .env-condition { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px 20px; margin: 16px 0 28px; }
  .env-condition p { margin: 0 0 8px; font-size: 10pt; line-height: 1.8; }
  .env-condition p:last-child { margin-bottom: 0; }
  .env-condition strong { color: #0f172a; }

  /* 【260507 v5.3.2 新規】Cover Page（P0・表紙＋引力定義） */
  .cover-page { min-height: calc(100vh - 96px); display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 40px 20px; page-break-after: always; }
  .cover-page .cover-badge { display: inline-block; font-size: 10pt; font-weight: 700; letter-spacing: 0.3em; color: #fff; background: #0f172a; padding: 8px 24px; border-radius: 100px; margin-bottom: 32px; }
  .cover-page .cover-title { font-size: 32pt; font-weight: 800; color: #0f172a; letter-spacing: 0.04em; margin: 0 0 12px; line-height: 1.3; border: none; padding: 0; }
  .cover-page .cover-subtitle { font-size: 10pt; color: #64748b; letter-spacing: 0.2em; margin-bottom: 32px; }
  .cover-page .cover-divider { width: 60px; height: 2px; background: #0f172a; margin: 0 auto 40px; }
  .cover-gravity-def { max-width: 580px; width: 100%; text-align: left; margin-bottom: 48px; }
  .cover-gravity-label { font-size: 11pt; font-weight: 800; color: #0f172a; letter-spacing: 0.08em; text-align: center; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid #cbd5e1; }
  .cover-gravity-body { font-size: 12pt; line-height: 2.0; color: #1a1a2e; text-align: center; margin: 0 0 24px; }
  .cover-gravity-body strong { color: #0f172a; font-weight: 800; }
  .cover-gravity-duality { display: flex; flex-direction: column; gap: 12px; margin: 24px 0 28px; }
  .cover-gravity-positive, .cover-gravity-negative { display: flex; align-items: center; gap: 12px; padding: 12px 18px; border-radius: 8px; font-size: 10.5pt; line-height: 1.6; }
  .cover-gravity-positive { background: rgba(16, 185, 129, 0.06); border-left: 3px solid #059669; }
  .cover-gravity-negative { background: rgba(239, 68, 68, 0.06); border-left: 3px solid #dc2626; }
  .cover-gravity-positive .cgd-tag { font-size: 9pt; font-weight: 800; letter-spacing: 0.1em; color: #047857; padding: 3px 10px; background: #fff; border-radius: 4px; flex-shrink: 0; }
  .cover-gravity-negative .cgd-tag { font-size: 9pt; font-weight: 800; letter-spacing: 0.1em; color: #991b1b; padding: 3px 10px; background: #fff; border-radius: 4px; flex-shrink: 0; }
  .cgd-arrow { font-size: 11pt; font-weight: 700; color: #64748b; flex-shrink: 0; }
  .cgd-text { color: #1a1a2e; }
  .cover-gravity-claim { font-size: 13pt; font-weight: 800; color: #0f172a; text-align: center; margin: 24px 0 0; padding-top: 20px; border-top: 1px solid #cbd5e1; line-height: 1.6; }
  .cover-page .cover-meta { font-size: 9pt; color: #94a3b8; letter-spacing: 0.15em; margin-top: 24px; }

  /* 【260507 v5.3 新規】Block C 経営インパクトボックス（採用/離脱/躍動 3 軸 × Before/After） */
  .business-impact-box { background: #eff6ff; border: 2px solid #1e40af; border-radius: 12px; padding: 24px 28px; margin: 24px 0; page-break-inside: avoid; }
  .bi-label { font-size: 10pt; font-weight: 700; color: #1e3a8a; letter-spacing: 0.08em; margin-bottom: 16px; }
  .bi-grid { display: grid; grid-template-columns: 1fr; gap: 14px; }
  .bi-axis { background: #fff; border: 1px solid #c7d2fe; border-radius: 8px; padding: 16px 20px; }
  .bi-axis-name { display: inline-block; font-size: 10pt; font-weight: 800; color: #fff; background: #1e40af; padding: 3px 12px; border-radius: 100px; letter-spacing: 0.05em; margin-bottom: 10px; }
  .bi-before, .bi-after { font-size: 10pt; line-height: 1.75; margin: 0 0 6px; color: #1e293b; }
  .bi-before:last-child, .bi-after:last-child { margin-bottom: 0; }
  .bi-before strong { color: #991b1b; }
  .bi-after strong { color: #047857; }

  .gravity-core { background: #fef2f2; border: 1px solid #fca5a5; border-radius: 8px; padding: 24px; margin: 28px 0; page-break-inside: avoid; }
  .gravity-core h4 { color: #991b1b; margin: 0 0 16px; font-size: 11pt; }
  .core-action { font-size: 11pt; font-weight: 700; color: #991b1b; background: #fff; border-left: 4px solid #dc2626; padding: 12px 16px; margin: 0 0 16px; }
  .core-duality { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
  .core-effect, .core-sideeffect { background: #fff; padding: 14px 16px; border-radius: 6px; border: 1px solid #fecaca; font-size: 10pt; line-height: 1.7; }
  .core-effect strong, .core-sideeffect strong { display: block; font-size: 9pt; letter-spacing: 0.05em; color: #991b1b; margin-bottom: 6px; text-transform: uppercase; }
  .core-summary { margin: 0; font-size: 10pt; line-height: 1.8; color: #991b1b; font-weight: 600; }

  .future-box { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 20px 24px; margin: 24px 0; page-break-inside: avoid; }
  .future-box h4 { color: #065f46; margin-top: 0; margin-bottom: 12px; }
  .future-box p { font-size: 10.5pt; line-height: 1.9; color: #064e3b; margin: 0; }

  .type-judgment { background: #eff6ff; border: 2px solid #3b82f6; border-radius: 8px; padding: 22px 26px; margin: 28px 0; page-break-inside: avoid; }
  .type-label { font-size: 9pt; letter-spacing: 0.12em; color: #1e40af; font-weight: 700; margin-bottom: 6px; }
  .type-name { font-size: 15pt; color: #1e3a8a; margin: 0 0 12px; border: none; padding: 0; }
  .type-reason { margin: 0 0 12px; color: #334155; font-size: 10pt; line-height: 1.8; }
  .type-prescription { margin: 0; font-weight: 700; color: #1e40af; font-size: 11pt; }

  .path-card--small { padding: 12px 16px; font-size: 9.5pt; color: #475569; background: #f8fafc; border-color: #e2e8f0; }
  .path-card--small strong { color: #0f172a; }

  .closing-note { background: #f8fafc; border-left: 4px solid #0f172a; border-radius: 0 8px 8px 0; padding: 22px 26px; margin: 28px 0; font-style: italic; color: #334155; page-break-inside: avoid; }
  .closing-note p { margin: 0 0 10px; font-size: 10.5pt; line-height: 1.9; }
  .closing-note p:last-child { margin-bottom: 0; }

  {$question_block_css}
  .report-footer { margin-top: 48px; padding-top: 20px; border-top: 2px solid #0f172a; text-align: center; font-size: 9pt; color: #64748b; page-break-inside: avoid; }
  .report-footer strong { color: #0f172a; font-size: 10pt; }
  .page-break { page-break-before: always; }
  /* スクリーン表示のレスポンシブ */
  @media screen and (max-width: 800px) {
    body { max-width: 100%; box-shadow: none; font-size: 14px; }
    .page { padding: 24px 20px; }
    .section-title { font-size: 18px; }
    h3 { font-size: 15px; }
    .core-quote { padding: 16px 18px; font-size: 14px; }
    .verb-chain { padding: 14px 16px; font-size: 13px; }
    /* 【260507 v5.3 改修】モバイルも縦並びフロー継承 */
    .verb-map { padding: 20px 14px; gap: 30px; }
    .verb-map-item { padding: 16px 18px; }
    .verb-map-item:not(:last-child)::after { font-size: 16pt; bottom: -27px; }
    .verb-map-verb { font-size: 12pt; line-height: 1.5; }
    .verb-map-source { font-size: 9pt; line-height: 1.65; }
    .filter-grid, .manual-grid { grid-template-columns: 1fr; gap: 12px; }
    .process-grid { grid-template-columns: 1fr; gap: 8px; }
    .core-duality { grid-template-columns: 1fr; gap: 10px; }
    .path-cards { gap: 10px; }
    .analyst-note { padding: 18px 20px; }
    .haveto-card, .future-box, .type-judgment, .closing-note { padding: 16px 18px; margin: 20px 0; }
    .gravity-core { padding: 18px 20px; }
    .why-declaration { padding: 16px 18px; }
    .why-text { font-size: 15px; }
    .path-card--recommended { padding-top: 32px; }
    .gravity-integration { padding: 20px 16px; }
    .gi-formula { flex-direction: column; gap: 8px; }
    .gi-operator { transform: rotate(90deg); }
    .gi-element { min-width: 100%; max-width: 100%; }
    .pdf-btn { bottom: 16px; right: 16px; padding: 10px 20px; font-size: 13px; }
  }
  @media screen and (min-width: 801px) {
    body { max-width: 760px; }
  }
  @media print {
    body { font-size: 10pt; visibility: visible !important; max-width: none; box-shadow: none; margin: 0; }
    .page { padding: 0; }
    .pdf-btn { display: none; }
    .filter-grid, .process-grid, .manual-grid { break-inside: avoid; }
    .haveto-card, .path-card, .scenario-box { break-inside: avoid; }
  }
</style>
</head>
<body>
<button class="pdf-btn" onclick="window.print()">
  <svg viewBox="0 0 24 24"><path d="M19 8h-1V3H6v5H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zM8 5h8v3H8V5zm8 14H8v-4h8v4zm2-4v-2H6v2H4v-4c0-.55.45-1 1-1h14c.55 0 1 .45 1 1v4h-2z"/></svg>
  PDF保存
</button>
<div class="page">
<div class="cover-page">
  <div class="cover-badge">YOUR GRAVITY CODE</div>
  <h1 class="cover-title">あなたの引力の暗号</h1>
  <div class="cover-subtitle">SOURCE CODE ANALYSIS REPORT</div>
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

  <div class="cover-meta">Gravity CODE｜GrowthFix</div>
</div>
<div class="page-break"></div>
{$report_body}
</div>
</body>
</html>
HTML;

// レポートをファイルに保存
file_put_contents($REPORT_FILE, $report_html);

// レポートURLを返す
$base_url = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http')
    . '://' . $_SERVER['HTTP_HOST'];
$report_url = $base_url . dirname($_SERVER['REQUEST_URI']) . '/generate.php?report=' . $report_id;

echo json_encode(['report_url' => $report_url]);
