<?php
// =============================================================================
// Gravity Shift - Individual Report Generator (Claude API)
// =============================================================================

require_once __DIR__ . '/../../config.php';
$api_key = defined('ANTHROPIC_API_KEY') ? ANTHROPIC_API_KEY : '';

$allowed_origins = ['https://growthfix.jp', 'http://localhost'];
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if (in_array($origin, $allowed_origins)) {
    header('Access-Control-Allow-Origin: ' . $origin);
} else {
    header('Access-Control-Allow-Origin: https://growthfix.jp');
}
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'error' => 'Method not allowed'], JSON_UNESCAPED_UNICODE);
    exit;
}

if (empty($api_key)) {
    echo json_encode(['success' => false, 'error' => 'APIキーが設定されていません'], JSON_UNESCAPED_UNICODE);
    exit;
}

$DATA_DIR = __DIR__ . '/../data';

$raw_body = file_get_contents('php://input');
$request = json_decode($raw_body, true);

if (!$request) {
    echo json_encode(['success' => false, 'error' => 'Invalid JSON'], JSON_UNESCAPED_UNICODE);
    exit;
}

$project_id = $request['project_id'] ?? null;
$role = $request['role'] ?? null; // 'ceo' or 'exec'
$exec_num = $request['exec_num'] ?? null;
$scores = $request['scores'] ?? [];
$score_comments = $request['score_comments'] ?? [];

if (!$project_id || !$role) {
    echo json_encode(['success' => false, 'error' => 'project_id and role required'], JSON_UNESCAPED_UNICODE);
    exit;
}
if (!in_array($role, ['ceo', 'exec'])) {
    echo json_encode(['success' => false, 'error' => 'Invalid role. Must be ceo or exec'], JSON_UNESCAPED_UNICODE);
    exit;
}

// Validate project ID format
if (!preg_match('/^[a-f0-9\-]+$/i', $project_id)) {
    echo json_encode(['success' => false, 'error' => 'Invalid project ID format'], JSON_UNESCAPED_UNICODE);
    exit;
}

// Load project info
$project_dir = $DATA_DIR . '/' . basename($project_id);
$project_file = $project_dir . '/project.json';
if (!file_exists($project_file)) {
    echo json_encode(['success' => false, 'error' => 'プロジェクトが見つかりません'], JSON_UNESCAPED_UNICODE);
    exit;
}
$project = json_decode(file_get_contents($project_file), true);

// Load hearing data
if ($role === 'ceo') {
    $hearing_file = $project_dir . '/ceo.json';
} else {
    $exec_int = intval($exec_num);
    if ($exec_int < 1 || $exec_int > 10) {
        echo json_encode(['success' => false, 'error' => 'Invalid exec number'], JSON_UNESCAPED_UNICODE);
        exit;
    }
    $hearing_file = $project_dir . '/exec_' . $exec_int . '.json';
}

if (!file_exists($hearing_file)) {
    echo json_encode(['success' => false, 'error' => 'ヒアリングデータが見つかりません'], JSON_UNESCAPED_UNICODE);
    exit;
}

$d = json_decode(file_get_contents($hearing_file), true);
$g = function($key) use ($d) { return $d[$key] ?? ''; };

$today = date('Y-m-d');
$respondent_name = $role === 'ceo' ? $project['ceo_name'] : ($d['name'] ?? '幹部' . $exec_num);
$role_label = $role === 'ceo' ? '経営者' : '経営幹部';

// Build user message
$user_message = "以下のヒアリングデータに基づいて組織の盲点レポートを生成してください。\n\n";
$user_message .= "## 基本情報\n";
$user_message .= "- 会社名: " . ($project['company_name'] ?? '') . "\n";
$user_message .= "- 回答者: " . $respondent_name . "（{$role_label}）\n";
$user_message .= "- 社員数: " . ($project['employee_count'] ?? '') . "\n";
$user_message .= "- 業種: " . ($project['industry'] ?? '') . "\n";
$user_message .= "- ヒアリング日: " . ($g('hearing_date') ?: $today) . "\n";
$user_message .= "- レポート納品日: " . $today . "\n\n";

// Scoring
$user_message .= "## コンサルタントのスコアリング\n";
$score_labels = ['hiring' => '採用', 'evaluation' => '評価・報酬', 'management' => 'マネジメント・権限移譲', 'culture' => '組織設計・カルチャー'];
foreach ($score_labels as $key => $label) {
    $s = $scores[$key] ?? '—';
    $c = $score_comments[$key] ?? '';
    $user_message .= "- {$label}: {$s}/5" . ($c ? " - {$c}" : "") . "\n";
}
$user_message .= "\n";

// Hearing content
$user_message .= "## ヒアリング内容\n\n";

// Opening
$user_message .= "### 冒頭：一番の困りごと\n";
$user_message .= "Q: " . ($role === 'ceo'
    ? "今、人と組織の問題で一番時間を取られていることは何ですか？"
    : "今、組織の中で一番課題だと感じていることは何ですか？") . "\n";
$user_message .= "A: " . $g('opening_answer') . "\n";
if ($g('opening_memo')) $user_message .= "コンサルタントメモ: " . $g('opening_memo') . "\n";
$user_message .= "\n";

// Questions - build from the data (questions are stored with q1_answer, q2_answer, etc.)
$domain_configs = [
    ['label' => '領域1：採用', 'questions' => [], 'memo_key' => 'domain_hiring_memo'],
    ['label' => '領域2：評価・報酬', 'questions' => [], 'memo_key' => 'domain_evaluation_memo'],
    ['label' => '領域3：マネジメント・権限移譲', 'questions' => [], 'memo_key' => 'domain_management_memo'],
    ['label' => '領域4：組織設計・カルチャー', 'questions' => [], 'memo_key' => 'domain_culture_memo'],
];

if ($role === 'ceo') {
    $domain_configs[0]['questions'] = [
        ['q1', '直近の採用で「良かった人」と「ミスマッチだった人」、何が違いましたか？'],
        ['q2', '採用最終判断は誰が、どんな基準で行っていますか？基準は言語化されていますか？'],
        ['q3', 'いま一番採用したい人材像は？'],
    ];
    $domain_configs[1]['questions'] = [
        ['q4', '評価と報酬はどう決めていますか？制度・基準はありますか？'],
        ['q5', '「この人はもっと評価されるべき」と感じる人はいますか？何が足りていないと思いますか？'],
    ];
    $domain_configs[2]['questions'] = [
        ['q6', 'いまCEOにしかできない判断は？'],
        ['q7', 'いま任せられない領域と、マネージャー層に本当に求めていることは？'],
    ];
    $domain_configs[3]['questions'] = [
        ['q8', '意思決定フローはどうなっていますか？「会社らしさ」を一言で言うと？'],
        ['q9', 'いま組織で「詰まっている部分」はどこですか？半年後、組織がどうなっていたら理想ですか？'],
    ];
} else {
    $domain_configs[0]['questions'] = [
        ['q1', '直近入社したメンバーは期待通りに機能していますか？採用時の現場要望は反映されていますか？'],
        ['q2', '採用最終判断は誰が、どんな基準でしていると見えますか？基準は言語化されていますか？'],
        ['q3', '今のチームに一番足りていないのはどんなスキル・役割の人ですか？'],
    ];
    $domain_configs[1]['questions'] = [
        ['q4', '評価と報酬はどう決まっていますか？制度・基準はありますか？納得感は？'],
        ['q5', '「もっと評価されるべき人」「評価が実態と合っていない人」はいますか？'],
    ];
    $domain_configs[2]['questions'] = [
        ['q6', '社長にしかできない判断は何だと思いますか？逆に任せるべき領域は？'],
        ['q7', '社長から求められていることと、自分（幹部）側から社長に求めていることは？'],
    ];
    $domain_configs[3]['questions'] = [
        ['q8', '会社の意思決定プロセスは現場から見て機能していますか？「会社らしさ」を一言で言うと？'],
        ['q9', 'いま組織で「ここが詰まっている／変えたい」と感じる部分は？半年後、組織がどうなっていたら理想ですか？'],
    ];
}

$qnum = 1;
foreach ($domain_configs as $dc) {
    $user_message .= "### {$dc['label']}\n\n";
    foreach ($dc['questions'] as $qa) {
        $user_message .= "Q{$qnum}: {$qa[1]}\n";
        $user_message .= "A: " . $g($qa[0] . '_answer') . "\n";
        if ($g($qa[0] . '_memo')) $user_message .= "メモ: " . $g($qa[0] . '_memo') . "\n";
        $user_message .= "\n";
        $qnum++;
    }
    if ($g($dc['memo_key'])) {
        $user_message .= "**{$dc['label']}の構造的所感（コンサルタント）:**\n" . $g($dc['memo_key']) . "\n\n";
    }
}

// CEO-only: BP organizational context（260421要件定義）
if ($role === 'ceo' && $g('bp_organizational_context_answer')) {
    $user_message .= "### BP結果の組織文脈化（深層引力が組織でどう現れているか）\n";
    $user_message .= "A: " . $g('bp_organizational_context_answer') . "\n";
    if ($g('bp_organizational_memo')) $user_message .= "メモ: " . $g('bp_organizational_memo') . "\n\n";
}

// Exec-only: Deep Gravity 5問（幹部視点）＋ BP feedback
if ($role === 'exec') {
    $gravity_questions = [
        ['q10_gravity_anger', '【怒り】社長の事業の根っこにある"許せなさ"は何だと思いますか？'],
        ['q11_gravity_motive', '【動機】社長がもし売上や評価を全て手放したら、何に向き合い続けると思いますか？'],
        ['q12_gravity_vow', '【宣言】社長は自分自身に何を誓って経営をしていると思いますか？'],
        ['q13_gravity_wound', '【傷】社長が今の事業を始めた動機の奥にある、個人的な傷は何だと思いますか？'],
        ['q14_gravity_future', '【未来】社長が15年後に今を振り返って後悔するとしたら、何を悔やむと思いますか？'],
    ];
    $has_gravity = false;
    foreach ($gravity_questions as $gq) { if ($g($gq[0])) { $has_gravity = true; break; } }
    if ($has_gravity) {
        $user_message .= "### 深層引力（幹部から見た社長の5問）\n\n";
        foreach ($gravity_questions as $gq) {
            if ($g($gq[0])) {
                $user_message .= "{$gq[1]}\n";
                $user_message .= "A: " . $g($gq[0]) . "\n\n";
            }
        }
    }
    if ($g('bp_feedback')) {
        $user_message .= "### BP結果への幹部意見（任意）\n";
        $user_message .= "A: " . $g('bp_feedback') . "\n\n";
    }
}

// Closing
$user_message .= "### 締め\n";
$user_message .= "Q: 今日話してみて、自分でも気づいていなかったことはありましたか？\n";
$user_message .= "A: " . $g('closing_answer') . "\n";
if ($g('closing_memo')) $user_message .= "メモ: " . $g('closing_memo') . "\n";

// System prompt (same as existing but with role context)
$role_context = $role === 'ceo'
    ? "これは経営者（CEO）へのヒアリングです。経営者視点での課題認識を分析してください。"
    : "これは経営幹部（{$respondent_name}）へのヒアリングです。経営者ではなく現場に近い立場からの課題認識を分析してください。経営者との認識ギャップが示唆される箇所は特に注目してください。";

$system_prompt = <<<SYSPROMPT
あなたはGrowthFixの組織コンサルタントとして、Gravity Scanの「組織の盲点レポート」を作成します。

{$role_context}

## 絶対ルール
- レポートに記載するエピソード・発言はヒアリングデータに実際に含まれるもの**のみ**使用。このプロンプト内の説明用の例をクライアントのデータとして使うことは**禁止**
- ヒアリングで語られていないことを推測で補わない
- 煽り表現（「こそが」「最大の」「実は」「意外にも」）はレポート全体で2回以内
- 課題を過大に描かない。一致点・強みもきちんと評価する
- divタグは必ず開閉一致させること

## 意外性の出し方
レポートの価値は「経営者が良かれと思ってやっていることが構造的に停滞を強化している」メカニズムの可視化にある。
**目指すべき：** 「あ、そういう構造だったのか」（静かな気づき）
**避けるべき：** 「あなたの経営は根本的に間違っています」（過大な否定・断定）

**3つの手法：**
1. **意図と結果の乖離** — 施策の意図は正しいが、構造が意図と逆の結果を生んでいる可能性を示す
2. **発言間の接続** — 別の質問への回答が同じ構造の表と裏であることを示す。これが「話のまとめ」を超えるレポートの鍵
3. **見えている問題の裏の構造** — 表面の症状の裏にある構造的原因をヒアリング内容に基づいて記述する

## レポート構造

### 1. エグゼクティブサマリー
- **この組織を一言で言うと**（core-quoteブロック）— 読んだ経営者が「え、うちってそういう会社なの？」と感じる、この組織の盲点を一言で表すキャッチコピー。挑発的だが事実に基づく一言。ヒアリング内容から導出すること
- **盲点の核**: 組織全体の盲点を要約（2-3文）
- **全体像**: 回答者の主訴と構造的な実態のギャップを説明（2-3段落）。1段落目で経営者が認識している課題を要約し、2段落目で「しかしヒアリングを構造的に分析すると〜」と、経営者が見えていない構造を示す
- **停滞の影響度**: 4領域のスコアと一言コメントをテーブルで表示

### 2. 盲点マップ
- **4領域マトリクス**: 各領域の「見えている問題（表面の症状）」と「見えていない構造的原因」を対比するテーブル
- **因果ループ図**: ASCII図で停滞の連鎖構造を表現。矢印（│▼├──→└──→）を使い自己強化ループを特定

### 3. 構造的課題
- 3-4個の構造的課題を特定
- 各課題に: 表面の症状、構造的原因、影響範囲、深刻度、詳細分析
- ヒアリングの具体的なエピソードや発言を引用して分析
- ★少なくとも1つの課題は「経営者が正しいと思ってやっていることが、構造的には停滞を強化している」パターンにする（ヒアリング内容に根拠がある場合のみ）

### 4. 優先順位
- 構造的依存関係に基づく推奨着手順序

### 5. AI時代の組織構造への示唆
以下の3つの観点でヒアリング内容を分析する。ヒアリングに根拠がない観点は省略してよい。

**a) ボス力 vs 部下力の分布**
- 組織内で「ボス力（自分で判断・設計・決定する力）」を持つ人と「部下力（報告・確認・対応する力）」で動いている人の比率を、ヒアリング内容から推察する
- 「社長に確認します」が多い組織＝部下力偏重。AI時代にはこの層が代替リスクを抱える

**b) 付加価値労働生産性の観点**
- ヒアリングで語られた評価基準が「物的生産性（たくさん作る・プロセスを回す）」に寄っていないかを確認する
- 「付加価値（高く売れるもの・事業成果への貢献）」を評価する仕組みがあるかを示唆する

**c) 経路依存性の検出**
- 「過去に正しかった仕組みが、環境が変わっても残り続けている」構造がヒアリングから検出されたら指摘する
- 経営者の意図は正しかったが、仕組みが固化して現在の環境に合わなくなっている可能性を控えめに示唆

### 6. 組織構造の3指標診断（260420 Q27追加・RECODE由来）

以下の3指標でヒアリング内容を構造化する。ヒアリングから該当する発言・エピソードが抽出できない指標は「該当データ不足」と明記。推測で補わない。

**a) 硬直化4要因**
組織が硬直化する4つの構造的要因のうち、この組織に該当するものを1-4個特定：
1. **前例踏襲**：過去の成功パターンを疑わず繰り返している兆候
2. **役割固定**：「この仕事はこの人」が長期固定・ジョブローテなし・結果としての属人化
3. **意思決定の階層化**：判断が上に集中し、現場が自律判断できない状態（社長に確認します症候群）
4. **評価の形骸化**：評価制度はあるが、実態として昇給・昇格に連動せず機能不全

各要因について：
- ヒアリングからの該当発言引用（または「該当発言なし」）
- この要因が存在する構造的理由（2-3行）
- 一致度スコア（薄い／中程度／強い）

**b) 熱量分布4象限**
社員の熱量を「本人の熱量（高↔低）×組織貢献度（高↔低）」の4象限で推察する：
- **熱源**（高熱量×高貢献）：組織の引力を作る人たち
- **戦力**（低熱量×高貢献）：成果は出すが燃えていない・流出リスクあり
- **浮遊**（高熱量×低貢献）：熱量はあるが貢献につながっていない・配置ミスマッチ
- **停滞**（低熱量×低貢献）：離脱候補・フィット不全

ヒアリングから各象限にどのくらいの人がいるか推察。具体的な人名は出さず、傾向として記述。

**c) 人材4象限（宝／人材／罪／無）**
組織の人材を以下の4象限で分類するフレーム。CEO認識から判別：
- **宝**：意思決定の質が高く、自律的に組織引力を増幅させる人材（3-10%が目安）
- **人材**：役割を全うし、組織の安定稼働に貢献する大多数（60-80%）
- **罪**：悪意はないが構造的に組織引力を減衰させる言動・判断をとる人材（5-15%）
- **無**：期待値に対して著しく機能していない人材（5-10%）

ヒアリングからこの4象限に相当する層の存在を推察。分類の比率感と、特に「罪」層の存在がヒアリングで暗示されているかを重点的に示す。「罪」は多くの経営者が認識していない盲点であり、この指摘が最大の付加価値になりうる。

**統合分析：** 3指標をクロス集計：
- 硬直化4要因 × 熱量4象限のどこに歪みがあるか
- 人材4象限の比率から、組織の耐用力（Scalability）を推察
- これらの交点に「Shift（3ヶ月）で最優先に手を打つべき構造」が見えてくる

### 7. 次のステップ
「このレポートを読んで、もし次のような詰まりを感じたら」という導入文を書き、レポートで可視化された構造的課題から生まれる具体的な「詰まり」を2-3個挙げる。
- **A. 自走する場合**: 具体的で即実行可能な3-4個のアクション
- **B. 詰まりを一緒に解消する場合**: Gravityプログラム（6ヶ月の組織変革）で構造を書き換えるロードマップ。サービスの押し売りではなく、レポートの課題に寄り添った提案にする

## 出力形式

HTMLフラグメントで出力してください（<html>や<head>は不要）。
以下のHTML構造とCSSクラスを正確に使用してください：

カバーページ:
<div class="cover">
  <span class="cover-badge">GRAVITY SHIFT DEEP</span>
  <h1 class="cover-title">組織の盲点レポート</h1>
  <p class="cover-subtitle">組織の組織の盲点を、丸裸にする</p>
  <div class="cover-meta">
    <table>
      <tr><td>クライアント</td><td>{会社名}</td></tr>
      <tr><td>回答者</td><td>{回答者名} 様（{役割}）</td></tr>
      <tr><td>従業員数</td><td>{社員数}名</td></tr>
      <tr><td>業種</td><td>{業種}</td></tr>
      <tr><td>診断実施日</td><td>{ヒアリング日}</td></tr>
      <tr><td>レポート納品日</td><td>{今日の日付}</td></tr>
      <tr><td>担当</td><td>石井 伸幸（GrowthFix）</td></tr>
    </table>
  </div>
  <p class="cover-footer">Confidential — For internal use only</p>
</div>

セクションヘッダー:
<div class="page"><div class="section"><div><span class="section-num">{番号}</span><h2 class="section-title">{タイトル}</h2></div><div class="section-line"></div></div>...セクション内容...</div>

停滞の核: <div class="core-quote">{要約文}</div>
深刻度ドット: <span class="severity"><span class="severity-dot"></span>...<span class="severity-dot empty"></span>...</span>
因果ループ: <div class="loop-box">{ASCII diagram}</div>
課題カード: <div class="issue-card"><div class="issue-card-head"><span class="issue-badge">課題 {N}</span><span class="issue-title">{タイトル}</span></div><table><tbody>...</tbody></table><div class="issue-analysis">{分析}</div></div>
優先順位: <div class="priority-row"><span class="priority-num">{N}</span><div class="priority-content"><div class="priority-label">{課題名}</div><div class="priority-reason">{理由}</div></div></div>
アクション: <div class="action-box">...</div> / <div class="action-box action-box--gravity">...</div>
ページ区切り: <div class="page-break"></div>

## 重要な指示
- numbered-listはCSSで自動番号が付く。リスト項目の先頭に「1.」「①」等の番号を手動で入れないこと
- ヒアリングの具体的な発言を必ず「」で引用。表面の症状と構造的原因を区別
- 因果ループはASCII罫線で自己強化サイクルを含め、「このループが意味すること」を説明
- 各セクションを<div class="page">でラップし、セクション間に<div class="page-break"></div>
- 「意図は正しかったが構造が逆の結果を生んでいる」視点をサマリーと構造的課題に含める
SYSPROMPT;

// Call Claude API
$payload = json_encode([
    'model' => 'claude-opus-4-20250514',
    'max_tokens' => 12000,
    'system' => $system_prompt,
    'messages' => [['role' => 'user', 'content' => $user_message]],
], JSON_UNESCAPED_UNICODE);

$context = stream_context_create([
    'http' => [
        'method' => 'POST',
        'header' => implode("\r\n", [
            'Content-Type: application/json',
            'x-api-key: ' . $api_key,
            'anthropic-version: 2023-06-01',
        ]),
        'content' => $payload,
        'timeout' => 180,
        'ignore_errors' => true,
    ],
]);

$response = file_get_contents('https://api.anthropic.com/v1/messages', false, $context);

if ($response === false) {
    error_log('[SHIFT generate-report] Claude API connection failed for project: ' . $project_id);
    echo json_encode(['success' => false, 'error' => 'Claude APIへの接続に失敗しました'], JSON_UNESCAPED_UNICODE);
    exit;
}

$result = json_decode($response, true);

if (!$result) {
    error_log('[SHIFT generate-report] Failed to parse API response for project: ' . $project_id . ' | Raw: ' . substr($response, 0, 500));
    echo json_encode(['success' => false, 'error' => 'Claude APIからの応答を解析できませんでした'], JSON_UNESCAPED_UNICODE);
    exit;
}

if (isset($result['error'])) {
    $error_msg = $result['error']['message'] ?? 'Unknown API error';
    error_log('[SHIFT generate-report] API error for project: ' . $project_id . ' | ' . $error_msg);
    echo json_encode(['success' => false, 'error' => 'レポート生成中にエラーが発生しました。再試行してください。'], JSON_UNESCAPED_UNICODE);
    exit;
}

// Extract text content
$report_html = '';
if (isset($result['content']) && is_array($result['content'])) {
    foreach ($result['content'] as $block) {
        if ($block['type'] === 'text') {
            $report_html .= $block['text'];
        }
    }
}

if (empty($report_html)) {
    echo json_encode(['success' => false, 'error' => 'レポートの生成内容が空でした'], JSON_UNESCAPED_UNICODE);
    exit;
}

// divタグの自動修復
$open_divs = preg_match_all('/<div[\s>]/i', $report_html);
$close_divs = preg_match_all('/<\/div>/i', $report_html);
$missing = $open_divs - $close_divs;
if ($missing > 0) {
    $report_html .= str_repeat('</div>', $missing);
}

// Strip markdown code fences
$report_html = preg_replace('/^```html\s*/i', '', $report_html);
$report_html = preg_replace('/^```\w*\s*/m', '', $report_html);
$report_html = preg_replace('/\s*```\s*$/', '', $report_html);
$report_html = trim($report_html);

// Save report to hearing data
$hearing_data = json_decode(file_get_contents($hearing_file), true);
$hearing_data['report_html'] = $report_html;
$hearing_data['report_generated_at'] = date('Y-m-d H:i:s');
$hearing_data['scores'] = $scores;
$hearing_data['score_comments'] = $score_comments;
$write_result = file_put_contents($hearing_file, json_encode($hearing_data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
if ($write_result === false) {
    error_log('[SHIFT generate-report] Failed to save report to: ' . $hearing_file);
}

echo json_encode(['success' => true, 'report_html' => $report_html], JSON_UNESCAPED_UNICODE);
