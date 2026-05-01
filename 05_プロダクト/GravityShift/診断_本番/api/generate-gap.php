<?php
// =============================================================================
// Gravity Shift v5 - 組織実装整合診断レポート生成（Week 1-2診断）
// 260422 SCAN統合版：BP翻訳マップ vs 組織実態の実装ギャップを整合／ズレ／漏れで可視化
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
if (!$project_id) {
    echo json_encode(['success' => false, 'error' => 'project_id required'], JSON_UNESCAPED_UNICODE);
    exit;
}

if (!preg_match('/^[a-f0-9\-]+$/i', $project_id)) {
    echo json_encode(['success' => false, 'error' => 'Invalid project ID format'], JSON_UNESCAPED_UNICODE);
    exit;
}

$project_dir = $DATA_DIR . '/' . basename($project_id);
$project_file = $project_dir . '/project.json';

if (!file_exists($project_file)) {
    echo json_encode(['success' => false, 'error' => 'プロジェクトが見つかりません'], JSON_UNESCAPED_UNICODE);
    exit;
}

$project = json_decode(file_get_contents($project_file), true);

$ceo_file = $project_dir . '/ceo.json';
if (!file_exists($ceo_file)) {
    echo json_encode(['success' => false, 'error' => 'CEOヒアリングデータが見つかりません'], JSON_UNESCAPED_UNICODE);
    exit;
}
$ceo_data = json_decode(file_get_contents($ceo_file), true);

$exec_count = $project['exec_count'] ?? 3;
$exec_data_list = [];
for ($i = 1; $i <= $exec_count; $i++) {
    $exec_file = $project_dir . '/exec_' . $i . '.json';
    if (!file_exists($exec_file)) {
        echo json_encode(['success' => false, 'error' => "幹部{$i}のヒアリングデータが見つかりません"], JSON_UNESCAPED_UNICODE);
        exit;
    }
    $exec_data_list[] = json_decode(file_get_contents($exec_file), true);
}

$today = date('Y-m-d');
$g = function($key, $data) { return $data[$key] ?? ''; };

// --- BP参照データの取得（URL優先→HTML貼付フォールバック） ---
function fetch_bp_report_content($bp_ref) {
    if (!empty($bp_ref['bp_url'])) {
        $url = $bp_ref['bp_url'];
        if (preg_match('#https?://[^\s]*growthfix[^\s]*/gravity-blueprint/[^\s]*#i', $url)) {
            $ctx = stream_context_create(['http' => ['timeout' => 10, 'method' => 'GET']]);
            $html = @file_get_contents($url, false, $ctx);
            if ($html !== false && strlen($html) > 1000) {
                return ['source' => 'url_fetch', 'url' => $url, 'html' => $html];
            }
            error_log("[Shift generate-gap] BP URL fetch failed: $url");
        }
    }
    if (!empty($bp_ref['bp_html'])) {
        return ['source' => 'html_paste', 'html' => $bp_ref['bp_html']];
    }
    return null;
}

$bp_content = !empty($project['bp_reference']) ? fetch_bp_report_content($project['bp_reference']) : null;
$code_type = $project['bp_reference']['code_type'] ?? '';

// --- Build comprehensive user message ---
$user_message = "以下のデータに基づいて、Gravity Shift Week 1-2「組織実装整合診断」レポートを生成してください。\n\n";

$user_message .= "## プロジェクト概要\n";
$user_message .= "- 会社名: " . ($project['company_name'] ?? '') . "\n";
$user_message .= "- 経営者: " . ($project['ceo_name'] ?? '') . "\n";
$user_message .= "- 社員数: " . ($project['employee_count'] ?? '') . "\n";
$user_message .= "- 業種: " . ($project['industry'] ?? '') . "\n";
$user_message .= "- 参加幹部数: " . $exec_count . "名\n";
$user_message .= "- レポート日: " . $today . "\n";
if ($code_type) {
    $user_message .= "- CODE 4型判定: **{$code_type}**（分析重点化に使用）\n";
}
$user_message .= "\n";

// BP参照データ
if ($bp_content) {
    $user_message .= "---\n\n## CEO側：BP v6.0 翻訳マップ（参照データ）\n\n";
    $user_message .= "以下はBlueprintセッションで経営者自身が描いた「個人引力（Why × 才能 × 偏愛）→ 採用 4 軸（採用基準・面接プロセス・採用後評価軸・幹部役割分担）」の翻訳設計図と面接ブループリント 5 要素です。翻訳マップ・ボトルネック・面接ブループリントを読み取り、Week 1-2診断の整合／ズレ／漏れ分析の基軸としてください。\n\n";
    $user_message .= "**取得方法:** " . $bp_content['source'] . "\n";
    if (!empty($bp_content['url'])) {
        $user_message .= "**URL:** " . $bp_content['url'] . "\n";
    }
    $user_message .= "\n**BPレポート全文（HTML）:**\n```\n" . substr($bp_content['html'], 0, 30000) . "\n```\n\n";
} else {
    $user_message .= "---\n\n## CEO側：BP v6.0 翻訳マップ（参照データ）\n\n";
    $user_message .= "**BP結果未取得。** 翻訳マップが参照できないため、CEO側の基軸データは下記CEOセッションの「bp_organizational_context」回答のみとなります。実装整合診断の精度が低下することを明記してください。Blueprint 受講後の再診断を強く推奨。\n\n";
}

// CEO ヒアリング
$user_message .= "---\n\n## CEOヒアリング（" . ($project['ceo_name'] ?? '') . "）\n\n";

$user_message .= "### CEOスコア\n";
$score_labels = ['hiring' => '採用', 'evaluation' => '評価・報酬', 'management' => 'マネジメント・権限移譲', 'culture' => '組織設計・カルチャー'];
$ceo_scores = $ceo_data['scores'] ?? [];
foreach ($score_labels as $key => $label) {
    $s = $ceo_scores[$key] ?? '—';
    $c = ($ceo_data['score_comments'][$key] ?? '');
    $user_message .= "- {$label}: {$s}/5" . ($c ? " ({$c})" : "") . "\n";
}
$user_message .= "\n";

$ceo_questions = [
    'opening' => '一番の困りごと',
    'q1' => '良かった採用とミスマッチの違い',
    'q2' => '採用最終判断者と基準言語化',
    'q3' => '今一番採用したい人材像',
    'q4' => '評価と報酬の決め方・制度・基準',
    'q5' => 'もっと評価されるべき人',
    'q6' => 'CEOにしかできない判断',
    'q7' => '任せられない領域とマネージャー層への要求',
    'q8' => '意思決定フローと会社らしさ',
    'q9' => '詰まっている部分と半年後の理想',
    'bp_organizational_context' => 'BP翻訳マップの組織文脈化（翻訳マップが組織でどう現れているか／実装されているか）',
    'closing' => '気づき',
];
$user_message .= "### CEO回答要旨\n";
foreach ($ceo_questions as $key => $label) {
    $answer = $g($key . '_answer', $ceo_data);
    if ($answer) {
        $user_message .= "- **{$label}**: {$answer}\n";
    }
}
$user_message .= "\n";

// 幹部ヒアリング
foreach ($exec_data_list as $idx => $exec_data) {
    $exec_num = $idx + 1;
    $exec_name = $exec_data['name'] ?? '幹部' . $exec_num;
    $exec_role = $exec_data['role_title'] ?? '';

    $user_message .= "---\n\n## 幹部{$exec_num}ヒアリング（{$exec_name}" . ($exec_role ? "・{$exec_role}" : "") . "）\n\n";

    $user_message .= "### 幹部{$exec_num}スコア\n";
    $exec_scores = $exec_data['scores'] ?? [];
    foreach ($score_labels as $key => $label) {
        $s = $exec_scores[$key] ?? '—';
        $c = ($exec_data['score_comments'][$key] ?? '');
        $user_message .= "- {$label}: {$s}/5" . ($c ? " ({$c})" : "") . "\n";
    }
    $user_message .= "\n";

    $exec_questions = [
        'opening' => '一番の課題',
        'q1' => '新入社員の機能度・採用要望反映',
        'q2' => '採用最終判断と基準（幹部視点）',
        'q3' => '不足スキル・役割',
        'q4' => '評価と報酬の決まり方・納得感',
        'q5' => 'もっと評価されるべき人',
        'q6' => '社長にしかできない判断（幹部視点）',
        'q7' => '社長から求められていること/社長への要望',
        'q8' => '意思決定プロセスと会社らしさ',
        'q9' => '詰まっている部分と半年後の理想',
        'closing' => '気づき',
    ];
    $user_message .= "### 幹部{$exec_num}回答要旨\n";
    foreach ($exec_questions as $key => $label) {
        $answer = $g($key . '_answer', $exec_data);
        if ($answer) {
            $user_message .= "- **{$label}**: {$answer}\n";
        }
    }
    $user_message .= "\n";

    // 翻訳マップ実装確認3問（幹部Q10-Q12）
    $impl_keys = [
        'q10_why_to_mission' => 'Why→採用基準/採用後評価軸 の実装確認',
        'q11_verb_to_function' => '才能→面接プロセス/幹部役割分担 の実装確認',
        'q12_env_to_structure' => '偏愛→採用判断軸/組織カルチャー の実装確認',
    ];
    $has_impl = false;
    foreach ($impl_keys as $key => $label) {
        if (!empty($exec_data[$key])) { $has_impl = true; break; }
    }
    if ($has_impl) {
        $user_message .= "### 幹部{$exec_num}の翻訳マップ実装確認\n";
        foreach ($impl_keys as $key => $label) {
            $answer = $exec_data[$key] ?? '';
            if ($answer) {
                $user_message .= "- **{$label}**: {$answer}\n";
            }
        }
        $user_message .= "\n";
    }

    // 幹部のBP意見聴取（任意）
    if (!empty($exec_data['bp_feedback'])) {
        $user_message .= "### 幹部{$exec_num}のBP翻訳マップへの意見\n";
        $user_message .= "- {$exec_data['bp_feedback']}\n\n";
    }
}

// --- System prompt（v5版・引力の実装整合診断） ---
$exec_names_list = [];
foreach ($exec_data_list as $idx => $ed) {
    $exec_names_list[] = ($ed['name'] ?? '幹部' . ($idx + 1));
}
$exec_names_str = implode('、', $exec_names_list);

// 4型別の分析重点
$type_focus = '';
if ($code_type) {
    $type_focus_map = [
        '整合型' => "経営者の翻訳マップは安定している前提。ボトルネックは組織リソース（人員・予算・時間）不足か、Implementation speedの問題。採用・育成の量的拡大と、役割分担の明示化を重点分析。",
        '才能ズレ型' => "経営者の才能（自然な動きと発火環境・CODE特定）が組織に組み込まれていない実装ギャップが最頻発。「才能→面接プロセス/幹部役割分担」の翻訳の実装状況を特に厚く分析。役割分担・業務プロセス・幹部育成・会議体の再設計が優先アクション候補。",
        'Whyズレ型' => "経営者個人のWhyが揺らいでいる兆候。組織実装を進めても土台が不安定。BP再診断またはCoaching並行を推奨。実装整合診断は一旦保留し、Why確立後の再実施が望ましい旨をレポートに明記。",
        '偏愛ズレ型' => "経営者の偏愛（譲れない好み・絶対に選ばない嫌い）が判断軸として機能しておらず、社会の期待で評価軸・役割分担が設計されている実装齟齬が出やすい。判断基準・評価制度・役割分担を経営者の偏愛軸で再定義することが核心。偏愛実装ギャップを特に厚く分析。",
    ];
    $type_focus = "\n\n## ★4型別分析重点（CEO判定：{$code_type}）\n" . ($type_focus_map[$code_type] ?? '');
}

$system_prompt = <<<SYSPROMPT
あなたはGrowthFixの組織コンサルタントとして、Gravity Shift Week 1-2「組織実装整合診断」レポートを作成します。

## Shiftの核心価値（260422 SCAN統合版）

「**BPで設計した個人引力が組織の現場でどう実装されているか（整合／ズレ／漏れ）を、幹部の証言で立体検証する診断**」

CEO（{$project['ceo_name']}）のBP翻訳マップ（仮説）と、経営幹部（{$exec_names_str}）が感じている組織実態を対比し、3パターン（整合／ズレ／漏れ）で実装ギャップを可視化します。
{$type_focus}

## 絶対ルール

- レポートに記載するエピソード・発言はヒアリングデータに実際に含まれるもの**のみ**使用。このプロンプト内の例をクライアントのデータとして使うことは**禁止**
- ヒアリングで語られていないことを推測で補わない
- 煽り表現（「こそが」「最大の」「実は」「意外にも」）はレポート全体で2回以内
- ギャップを過大に描かない。スコア差1以内は「一致」として強みに評価
- divタグは必ず開閉一致させること
- 旧SCAN時代の「深層引力5軸ギャップ」「怒り／動機／宣言／傷／未来」の5問構造は使わない（260422廃止）
- 代わりに「翻訳マップ（個人引力 Why × 才能 × 偏愛 → 採用 4 軸：採用基準・面接プロセス・採用後評価軸・幹部役割分担）の実装整合」を軸にする

## 意外性の出し方

レポートの価値は「経営者が見えていない構造」を幹部の発言との対比で浮かび上がらせること。
- **目指すべき：** 「あ、幹部はそう見えていたのか」（静かな気づき）
- **避けるべき：** 「あなたの認識は間違っています」（過大な否定・断定・パーセント数値での断定）

**3つの手法：**
1. **盲点の構造的原因** — CEOに見えないのは「見ようとしていない」からではなく「構造的に見えにくい位置にいる」から
2. **逆盲点** — CEOが課題視しているのに幹部が問題視していない場合、「なぜ危機感が伝わっていないか」を分析
3. **認識反転** — CEOが強みと思っていることを幹部が課題と感じている場合。これがあればレポートの核心

## レポート構造（3層・Shift v2仕様）

### 1. エグゼクティブサマリー
- プロジェクト概要（会社名、参加者、実施日、4型）
- **実装整合の総合判定**: 「整合強／部分的整合／ズレ大／漏れ大」で評価
- **Week 3-12 実装方針**: 最優先ボトルネック1点＋実装順序3点
- **最重要1文**: 実装ギャップの核心を1文で core-quote ブロック表示
- 3要素（Why・才能・偏愛）の整合度をテーブルで簡潔に表示

### 2. 翻訳マップ実装整合診断（★メイン）

本セクションがレポートの核心。BP翻訳マップ（CEO仮説）vs 組織実態（幹部証言）を対比し、整合／ズレ／漏れの3パターンで分析。

**3要素×3パターン分析：**

#### 要素A：Why → 採用基準/採用後評価軸
- BP翻訳マップ（CEO仮説）：BPレポートから該当箇所を引用
- 幹部認識（組織実態）：幹部Q10回答＋戦略Q1-Q5から該当発言を引用
- **判定：** 整合（gap-match）／ズレ（gap-diverge）／漏れ（gap-critical）
  - 整合：CEO仮説が採用基準・採用後評価軸に実装されている
  - ズレ：CEO仮説と現場実態が食い違っている
  - 漏れ：CEO仮説は理解されているが、まだ組織に実装されていない
- 構造的意味：なぜその状態なのか

#### 要素B：才能 → 面接プロセス/幹部役割分担
- BP翻訳マップ：経営者の才能（自然な動きと発火環境）が面接プロセス・幹部役割分担にどう翻訳されるか
- 幹部認識：幹部Q11回答＋戦略Q6-Q7から該当発言
- 判定：整合／ズレ／漏れ
- 構造的意味

#### 要素C：偏愛 → 採用判断軸/組織カルチャー
- BP翻訳マップ：経営者の偏愛（譲れない好み・絶対に選ばない嫌い）が採用判断軸・組織カルチャーにどう翻訳されるか
- 幹部認識：幹部Q12回答＋戦略Q8-Q9から該当発言
- 判定：整合／ズレ／漏れ
- 構造的意味

**総合判定：**
- 3要素すべてで漏れ大 → **実装の基盤不足。Shift Week 3-12で役割分担から着手**
- 2要素でズレ大 → **実装仮説と実態の齟齬。Shift Week 3-12で認識擦り合わせから**
- 1要素のみ問題 → **部分的実装ギャップ。該当軸に集中した実装伴走**
- すべて整合 → **実装済み。Orbit移行で継続運用支援に切り替え可**

**データ不足時：** BP結果未取得の場合「BP翻訳マップが未入力のため3要素の仮説軸が欠落。BP受講後に再診断を推奨」と明記してセクション縮退。

### 3. 実装ギャップが戦術面に現れている症状（4ドメイン）

翻訳マップの実装ギャップを「原因」、戦術面の課題を「症状」として位置付け。

**4ドメイン：**
- **採用**：翻訳マップのWhy軸（採用基準）・偏愛軸（採用判断軸）の実装ギャップ
- **評価**：翻訳マップのWhy軸（採用後評価軸）・才能軸（評価基準）への実装ギャップ
- **マネジメント**：翻訳マップの才能軸（幹部役割分担）の権限移譲への実装ギャップ
- **カルチャー**：翻訳マップの偏愛軸（組織カルチャー）への実装ギャップ

**各ドメインの出力構造：**
- CEO認識（戦略Q1-Q9の該当回答）
- 幹部認識（戦略Q1-Q9の該当回答・複数幹部の傾向）
- **翻訳マップ実装ギャップとの接続**: 要素A-Cのどれがこの戦術症状の原因として機能しているか
- ギャップの構造と具体的発言の対比

### 4. 組織構造の3指標診断（補助データ）

以下の3指標を「CEO認識 vs 幹部認識」の対比で可視化する。ヒアリングから該当する発言・エピソードが抽出できない指標は「該当データ不足」と明記。推測で補わない。

**a) 硬直化4要因 認識ギャップ分析**
1. 前例踏襲 2. 役割固定 3. 意思決定の階層化 4. 評価の形骸化
各要因ごとに CEO認識／幹部認識／判定／構造的理由

**b) 熱量分布4象限 認識ギャップ分析**
熱源／戦力／浮遊／停滞 の各象限に「誰がいるか」のCEO認識 vs 幹部認識

**c) 人材4象限 認識ギャップ分析**
宝／人材／罪／無 の4象限。特に「罪」はCEO盲点・幹部視点で発見されやすい

### 5. 優先アクション提案（Week 3-12 実装ロードマップ）

- 実装ギャップ3要素のうち優先対応要素を特定
- 戦術症状への対処より**翻訳マップの実装そのものへの働きかけ**を先に
- **Month 1-3の実装順序**：
  - Month 1（Week 3-6）：最優先ボトルネック（通常は役割分担の再設計）
  - Month 2（Week 7-10）：構造面への波及（制度・会議体の更新）
  - Month 3（Week 11-12）：評価軸・採用基準の確定運用
- 各アクションに「なぜこれが先か」のロジック（翻訳マップの原因層から症状層への因果）

### 6. 次のステップ

「このレポートを受けて、Week 3-12の実装伴走で何に着手するか」を明示。
- **Shift Week 3-12 実装方針**: 本診断で特定した最優先ボトルネックから着手
- **3ヶ月後の到達目標**: 翻訳マップが組織に実装された状態の具体像（整合／ズレ／漏れのBefore/After想定）
- **Orbit移行の判断基準**: Shift完了時の再診断で何がクリアされていれば Orbit（月額継続）移行可能か
- **並行すべきサービス**: CODE未受講なら受講推奨、個人引力の揺らぎがあればCoaching並行

## 出力形式

HTMLフラグメントで出力してください（<html>や<head>は不要）。
以下のCSSクラスを使用してください:

カバーページ:
<div class="cover">
  <span class="cover-badge">GRAVITY SHIFT</span>
  <h1 class="cover-title">組織実装整合診断レポート（Week 1-2）</h1>
  <p class="cover-subtitle">BP翻訳マップの実装状況を、整合／ズレ／漏れで可視化する</p>
  <div class="cover-meta">
    <table>
      <tr><td>クライアント</td><td>{会社名}</td></tr>
      <tr><td>経営者</td><td>{CEO名} 様</td></tr>
      <tr><td>参加幹部</td><td>{幹部名リスト}</td></tr>
      <tr><td>従業員数</td><td>{社員数}名</td></tr>
      <tr><td>業種</td><td>{業種}</td></tr>
      <tr><td>4型判定</td><td>{4型}</td></tr>
      <tr><td>レポート日</td><td>{今日の日付}</td></tr>
      <tr><td>担当</td><td>石井 伸幸（GrowthFix）</td></tr>
    </table>
  </div>
  <p class="cover-footer">Confidential — For internal use only</p>
</div>

セクションヘッダー:
<div class="page"><div class="section"><div><span class="section-num">{番号}</span><h2 class="section-title">{タイトル}</h2></div><div class="section-line"></div></div>...内容...</div>

ギャップ度合いの表示:
<span class="gap-badge gap-match">整合</span>
<span class="gap-badge gap-diverge">ズレ</span>
<span class="gap-badge gap-critical">漏れ</span>

発言対比テーブル:
<table class="compare-table">
  <thead><tr><th>観点</th><th>CEO認識（BP翻訳マップ）</th><th>幹部認識（組織実態）</th></tr></thead>
  <tbody><tr><td>{観点}</td><td>「{CEO発言 or BPマップ該当箇所}」</td><td>「{幹部発言}」</td></tr></tbody>
</table>

その他は既存のレポートCSS（section, section-num, section-title, section-line, core-quote, issue-card, issue-badge, priority-row, priority-num, action-box, action-box--gravity, disclaimer, report-footer, page, page-break）を使用。

## 重要な指示

- numbered-listはCSSで自動番号が付く。リスト項目の先頭に「1.」「①」等の番号を手動で入れないこと
- 具体的な発言を必ず「」で引用。CEOと幹部の対比を常に意識
- ギャップは「誰が悪い」ではなく「この構造がギャップを生んでいる」と構造に帰責
- 一致点は組織の強みとしてポジティブに評価
- 各セクションを<div class="page">でラップし、セクション間に<div class="page-break"></div>
- 「次のステップ」は押し売りにならず、Week 3-12実装伴走の自然な接続として提示
- 旧サービス名「Scan」「Gravity Scan」は使わない。「Gravity Shift」「Week 1-2 組織実装整合診断」を使用

## 絶対に書かないこと

- ❌ 旧5問（怒り／動機／宣言／傷／未来）の軸
- ❌ 旧サービス名「Scan」「Gravity Scan」（260422廃止）
- ❌ 「90日」「3ヶ月のCoaching」等の誤記
- ❌ `<html>` `<head>` `<body>` タグ
- ❌ `<style>` タグ・外側HTML・コードフェンス
SYSPROMPT;

// Call Claude API（Sonnet 4.5・260422 Shift v5）
$payload = json_encode([
    'model' => 'claude-sonnet-4-5',
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
        'timeout' => 240,
        'ignore_errors' => true,
    ],
]);

$response = file_get_contents('https://api.anthropic.com/v1/messages', false, $context);

if ($response === false) {
    error_log('[SHIFT generate-gap v5] Claude API connection failed for project: ' . $project_id);
    echo json_encode(['success' => false, 'error' => 'Claude APIへの接続に失敗しました'], JSON_UNESCAPED_UNICODE);
    exit;
}

$result = json_decode($response, true);

if (!$result) {
    error_log('[SHIFT generate-gap v5] Failed to parse API response for project: ' . $project_id . ' | Raw: ' . substr($response, 0, 500));
    echo json_encode(['success' => false, 'error' => 'Claude APIからの応答を解析できませんでした'], JSON_UNESCAPED_UNICODE);
    exit;
}

if (isset($result['error'])) {
    $error_msg = $result['error']['message'] ?? 'Unknown API error';
    error_log('[SHIFT generate-gap v5] API error for project: ' . $project_id . ' | ' . $error_msg);
    echo json_encode(['success' => false, 'error' => 'レポート生成中にエラーが発生しました。再試行してください。'], JSON_UNESCAPED_UNICODE);
    exit;
}

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

// --- Post-processing（CODE/Blueprint と同等の包括的stripping）---

// 1. Markdown code fences
$report_html = preg_replace('/^```html\s*/i', '', $report_html);
$report_html = preg_replace('/^```\w*\s*/m', '', $report_html);
$report_html = preg_replace('/\s*```\s*$/', '', $report_html);

// 2. Outer HTML/DOCTYPE/head/body tags
$report_html = preg_replace('/<!DOCTYPE[^>]*>/i', '', $report_html);
$report_html = preg_replace('/<\/?html[^>]*>/i', '', $report_html);
$report_html = preg_replace('/<head[\s\S]*?<\/head>/i', '', $report_html);
$report_html = preg_replace('/<\/?body[^>]*>/i', '', $report_html);

// 3. Meta/title/link/style tags
$report_html = preg_replace('/<meta[^>]*>/i', '', $report_html);
$report_html = preg_replace('/<title[\s\S]*?<\/title>/i', '', $report_html);
$report_html = preg_replace('/<link[^>]*>/i', '', $report_html);
$report_html = preg_replace('/<style[\s\S]*?<\/style>/i', '', $report_html);

// 4. Inline style attributes（AIが勝手に付けたものを除去）
$report_html = preg_replace('/\s+style="[^"]*"/i', '', $report_html);

// 5. div balance auto-repair
$open_divs = preg_match_all('/<div[\s>]/i', $report_html);
$close_divs = preg_match_all('/<\/div>/i', $report_html);
$missing = $open_divs - $close_divs;
if ($missing > 0) {
    $report_html .= str_repeat('</div>', $missing);
} elseif ($missing < 0) {
    $report_html = preg_replace('/<\/div>/', '', $report_html, -$missing);
}

$report_html = trim($report_html);

// Save gap report
$gap_data = [
    'report_html' => $report_html,
    'generated_at' => date('Y-m-d H:i:s'),
    'version' => 'v5_shift_integrated',
    'model' => 'claude-sonnet-4-5',
    'participants' => [
        'ceo' => $project['ceo_name'] ?? '',
        'executives' => $exec_names_list,
    ],
    'bp_reference_source' => $bp_content['source'] ?? 'none',
    'code_type' => $code_type,
];
$write_result = file_put_contents($project_dir . '/gap_report.json', json_encode($gap_data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
if ($write_result === false) {
    error_log('[SHIFT generate-gap v5] Failed to save gap report to: ' . $project_dir . '/gap_report.json');
}

echo json_encode(['success' => true, 'report_html' => $report_html], JSON_UNESCAPED_UNICODE);
