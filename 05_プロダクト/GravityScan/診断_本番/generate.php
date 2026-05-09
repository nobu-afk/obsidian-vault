<?php
/**
 * Gravity Scan 診断 — レポート生成API
 * Claude APIを呼び出して「伸びしろレポート」を生成する
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
$config_file = __DIR__ . '/../config.php';
if (file_exists($config_file)) {
    require_once $config_file;
}
$ANTHROPIC_API_KEY = defined('ANTHROPIC_API_KEY') ? ANTHROPIC_API_KEY : getenv('ANTHROPIC_API_KEY');
if (empty($ANTHROPIC_API_KEY)) {
    http_response_code(500);
    echo json_encode(['error' => 'API設定エラー。管理者に連絡してください。']);
    exit;
}
$reports_dir = __DIR__ . '/reports';
if (!is_dir($reports_dir)) mkdir($reports_dir, 0755, true);

// --- ジョブステータス ヘルパー ---
function status_file_path($id) {
    return __DIR__ . '/reports/status_' . $id . '.json';
}
function write_status($id, $data) {
    // 既存の created_at を保持（初回書き込み時のみ新規設定）
    $existing = read_status($id);
    if ($existing && isset($existing['created_at'])) {
        $data['created_at'] = $existing['created_at'];
    }
    $data['updated_at'] = time();
    file_put_contents(status_file_path($id), json_encode($data, JSON_UNESCAPED_UNICODE));
}
function read_status($id) {
    $path = status_file_path($id);
    if (!file_exists($path)) return null;
    return json_decode(file_get_contents($path), true);
}

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

// --- GET /generate.php?job=JOB_ID → ジョブステータス返却 ---
if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['job'])) {
    $req_id = preg_replace('/[^a-f0-9]/', '', $_GET['job']);
    if (!$req_id || strlen($req_id) !== 16) {
        http_response_code(400);
        echo json_encode(['error' => 'Invalid job ID']);
        exit;
    }
    $status = read_status($req_id);
    if (!$status) {
        http_response_code(404);
        echo json_encode(['error' => 'Job not found']);
        exit;
    }
    echo json_encode($status);
    exit;
}

// --- POST → レポート生成（非同期ジョブ方式） ---
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
$pre_info = $input['pre_info'] ?? ($input['preInfo'] ?? '');

// --- CODE結果のパーサー（Q1 D・Q7 D：プログレッシブパース） ---
function parse_code_result_from_text($text) {
    $text = trim($text);
    if (empty($text)) return ['type' => 'empty'];

    if (!preg_match('#https?://[^\s\n]*growthfix[^\s\n]*/gravity-code/[^\s\n]+#i', $text, $m)) {
        return ['type' => 'free', 'raw' => $text];
    }

    $url = $m[0];
    $ctx = stream_context_create(['http' => ['timeout' => 10, 'method' => 'GET']]);
    $html = @file_get_contents($url, false, $ctx);
    if ($html === false || strlen($html) < 1000) {
        error_log("[Scan parse] fetch_failed url={$url} bytes=" . ($html === false ? 'false' : strlen($html)));
        return ['type' => 'fetch_failed', 'url' => $url, 'raw' => $text];
    }

    $extractors = [
        'why'       => ['#<p class="why-text">([^<]+)</p>#', fn($v) => trim($v)],
        'character' => ['#<div class="core-quote">あなたは["「]?([^"」<]+?)["」]?だ#', fn($v) => trim($v)],
        'type'      => ['#<h3 class="type-name">【([^】]+)】</h3>#', fn($v) => trim($v)],
        'env'       => ['#<div class="env-condition">([\s\S]*?)</div>#', fn($v) => preg_replace('/\s+/', ' ', trim(strip_tags($v)))],
        'core'      => ['#<p class="core-action">([^<]+)</p>#', fn($v) => trim($v)],
    ];
    $extracted = [];
    $missed = [];
    foreach ($extractors as $key => [$pattern, $clean]) {
        if (preg_match($pattern, $html, $mm)) {
            $extracted[$key] = $clean($mm[1]);
        } else {
            $missed[] = $key;
        }
    }
    preg_match_all('#<div class="verb-map-verb">([^<]+)</div>#', $html, $mm);
    if (!empty($mm[1])) {
        $extracted['verbs'] = array_map('trim', $mm[1]);
    } else {
        $missed[] = 'verbs';
    }

    // 必須フィールド：why / character / type のいずれか2つ以上取れれば成功
    $required_hit = count(array_intersect(['why', 'character', 'type'], array_keys($extracted)));
    if ($required_hit >= 2) {
        if (!empty($missed)) {
            error_log("[Scan parse] partial url={$url} missed=" . implode(',', $missed));
        }
        return ['type' => 'parsed', 'data' => $extracted, 'url' => $url, 'missed' => $missed];
    }
    error_log("[Scan parse] parse_failed url={$url} hit=" . implode(',', array_keys($extracted)) . " missed=" . implode(',', $missed));
    return ['type' => 'parse_failed', 'url' => $url, 'raw' => $text, 'missed' => $missed];
}

function format_code_result_for_prompt($parsed) {
    if ($parsed['type'] === 'parsed') {
        $d = $parsed['data'];
        $lines = ['## CODE結果（自動抽出）'];
        if (!empty($d['character'])) $lines[] = "- キャラ名：{$d['character']}";
        if (!empty($d['type'])) $lines[] = "- 4型判定：{$d['type']}";
        if (!empty($d['why'])) $lines[] = "- Why（個人の動機）：{$d['why']}";
        if (!empty($d['verbs'])) $lines[] = "- 才能（動詞3連鎖）：" . implode(' / ', $d['verbs']);
        if (!empty($d['env'])) $lines[] = "- 環境条件：{$d['env']}";
        if (!empty($d['core'])) $lines[] = "- 引力の核：{$d['core']}";
        $lines[] = "- 元URL：{$parsed['url']}";
        return implode("\n", $lines);
    }
    if ($parsed['type'] === 'free') {
        return "## CODE結果（経営者の自由記入）\n{$parsed['raw']}";
    }
    if ($parsed['type'] === 'parse_failed' || $parsed['type'] === 'fetch_failed') {
        return "## CODE結果（URL取得失敗・元データ）\n{$parsed['raw']}\n※対話内でCODE結果を確認すること";
    }
    return '## CODE結果（未入力）';
}

// pre_info から CODE結果セクションを抽出してパース
if (!empty($pre_info)) {
    // 【CODE結果】〜【組織規模】の間を抽出
    if (preg_match('/【CODE結果】([\s\S]*?)(?=【|$)/u', $pre_info, $m)) {
        $code_text = trim($m[1]);
        $parsed_code = parse_code_result_from_text($code_text);
        $formatted_code = format_code_result_for_prompt($parsed_code);
        // pre_info の CODE結果部分を整形済みに置換
        $pre_info = preg_replace('/【CODE結果】[\s\S]*?(?=【|$)/u', $formatted_code . "\n\n", $pre_info);
    }
}

// --- プロンプト構築 ---
$choices_parts = [];
foreach ($choices as $c) {
    $choices_parts[] = "Q. {$c['question']}\n   → {$c['selected']}";
}
$choices_text = implode("\n", $choices_parts);

// --- 診断ルールの事前判定（AI任せではなくPHPで決定的に計算） ---
// choices から質問キーワードで回答を引く
function gravity_scan_get_answer($choices, $keyword) {
    foreach ($choices as $c) {
        if (isset($c['question']) && strpos($c['question'], $keyword) !== false) {
            return $c['selected'] ?? '';
        }
    }
    return '';
}

$q1  = gravity_scan_get_answer($choices, '最近入社した人');
$q2  = gravity_scan_get_answer($choices, '自分の評価基準');
$q3  = gravity_scan_get_answer($choices, '1週間不在');
$q4  = gravity_scan_get_answer($choices, '会社の方針');
$q5  = gravity_scan_get_answer($choices, 'ここを変えれば事業');
$q6  = gravity_scan_get_answer($choices, 'そこを変えるために');
$q7  = gravity_scan_get_answer($choices, '幹部に聞いたら');
$q8  = gravity_scan_get_answer($choices, '事業を一言で言うと');
$q9  = gravity_scan_get_answer($choices, '右腕');
$q10a = gravity_scan_get_answer($choices, '何に使っていますか');
$q10b = gravity_scan_get_answer($choices, '社員のAI活用');

// AI活用レベル判定（Q10a × Q10b）
$ai_level = 'L0';
if (strpos($q10a, '判断') !== false) {
    $ai_level = (strpos($q10b, '多数') !== false || strpos($q10b, '一部') !== false) ? 'L3' : 'L2';
} elseif (strpos($q10a, '作業') !== false) {
    if (strpos($q10b, '多数') !== false) {
        $ai_level = 'L3';
    } elseif (strpos($q10b, '一部') !== false) {
        $ai_level = 'L2';
    } else {
        $ai_level = 'L1';
    }
} elseif (strpos($q10a, '興味') !== false) {
    $ai_level = 'L1';
}

// 経営ステージ判定（❶〜❹）
if (
    strpos($q9, 'いない') !== false ||
    strpos($q9, '辞めた') !== false ||
    strpos($q3, 'かなりの業務が止まる') !== false ||
    strpos($q3, '想像がつかない') !== false
) {
    $stage = '❶社長独走';
} elseif (
    strpos($q1, '期待通り') !== false &&
    strpos($q3, '問題なく回る') !== false &&
    strpos($q9, '任せている') !== false
) {
    $stage = '❹グラビティ型成長';
} elseif (
    strpos($q2, '明確') !== false &&
    strpos($q4, '明文化') !== false &&
    (strpos($q6, '変わらない') !== false || strpos($q5, '方向性') !== false)
) {
    $stage = '❸施策先行';
} else {
    $stage = '❷人力拡大';
}

// 事業ループ型判定（Q8）
$loop_type = 'エキスパート型';
if (strpos($q8, '営業→納品→紹介') !== false) {
    $loop_type = '単循環型';
} elseif (strpos($q8, 'サブスクや継続課金') !== false) {
    $loop_type = 'ストック型';
} elseif (strpos($q8, '買収や新規事業') !== false) {
    $loop_type = 'M&A・多角化型';
}

// 問い直し装置の[X]判定（優先順位 Q7 > Q9 > Q6 > Q3 > Q5）
$problem_x = '無意識に避けてきた判断';
$problem_priority = 'default';
if (strpos($q7, '全然違う') !== false || strpos($q7, '聞いたことがない') !== false) {
    $problem_x = '幹部と避けてきた対話';
    $problem_priority = 'Q7';
} elseif (strpos($q9, 'いない') !== false || strpos($q9, '辞めた') !== false) {
    $problem_x = '右腕を作らない選択';
    $problem_priority = 'Q9';
} elseif (strpos($q6, 'いろいろ試したが') !== false) {
    $problem_x = '試していない別の選択肢';
    $problem_priority = 'Q6';
} elseif (strpos($q3, '想像がつかない') !== false) {
    $problem_x = '不在にできない自分';
    $problem_priority = 'Q3';
} elseif (strpos($q5, '方向性') !== false) {
    $problem_x = '曖昧なまま進めてきた選択';
    $problem_priority = 'Q5';
}

// 強度判定（Q1健全＋Q2明確＋Q3問題なく回る→Lv2、それ以外Lv3）
$intensity = (
    strpos($q1, '期待通り') !== false &&
    strpos($q2, '明確') !== false &&
    strpos($q3, '問題なく回る') !== false
) ? 'Lv2' : 'Lv3';

// 推奨サービス判定
if (
    strpos($q9, 'いない') !== false ||
    strpos($q9, '辞めた') !== false ||
    strpos($q3, '想像がつかない') !== false
) {
    $recommended = 'Gravity Coaching';
    $recommended_reason = '❶社長独走の兆候（右腕不在または判断集中）。まず経営者自身の判断軸の言語化から。';
} elseif (strpos($q7, '全然違う') !== false || strpos($q7, '聞いたことがない') !== false) {
    $recommended = 'Gravity Shift';
    $recommended_reason = '幹部との認識ギャップが大きい。ShiftのWeek 1-2組織実装整合診断でCEO＋幹部の多視点で可視化し、そのまま実装へ（80万・3ヶ月）。';
} elseif (
    ($ai_level === 'L2' || $ai_level === 'L3') &&
    ($stage === '❷人力拡大' || $stage === '❸施策先行') &&
    (strpos($q2, 'バラバラ') !== false || strpos($q2, '答えられない') !== false || strpos($q5, '方向性') !== false)
) {
    $recommended = 'Gravity Shift';
    $recommended_reason = 'AI活用レベル' . $ai_level . '×' . $stage . '×仕組み未整備。Week 1-2幹部診断＋Week 3-12組織実装の3ヶ月（80万）。';
} elseif (
    strpos($q2, '明確') !== false &&
    strpos($q4, '明文化') !== false &&
    strpos($q3, '問題なく回る') !== false
) {
    $recommended = 'Gravity Orbit直接';
    $recommended_reason = '基本的な仕組みが存在する。Orbit直接契約で運用・拡張へ。';
} elseif (strpos($q5, '方向性') !== false || strpos($q6, '変わらない') !== false) {
    $recommended = 'Gravity';
    $recommended_reason = '勝ち筋ループ全体の再設計が必要。6ヶ月の変革プログラム。';
} else {
    $recommended = 'Gravity';
    $recommended_reason = '標準的な6ヶ月変革プログラム。';
}

// 事前判定結果をプロンプトに注入するためのブロック
$diagnostic_block = <<<DIAG

## 【事前判定結果（PHP側で決定的に計算済み・必ずこの値を採用）】

- **経営ステージ**: {$stage}
- **AI活用レベル**: {$ai_level}（Q10a: {$q10a} × Q10b: {$q10b}）
- **事業ループ型**: {$loop_type}
- **問い直し装置の[X]**: {$problem_x}（優先順位: {$problem_priority}）
- **問いの強度**: {$intensity}
- **推奨サービス**: {$recommended}
- **推奨理由**: {$recommended_reason}

★重要：上記の判定結果はPHP側のルールベース判定で決定済み。AIはこの値を独自に上書きせず、
この値を採用してレポートを文章化・具体化すること。対話内容と矛盾する場合のみ、
Analyst's Note末尾に「情報不足の明示」として1行添えてよい（ただし判定そのものは維持）。

DIAG;

// トランスクリプトモード: 一括テキストがある場合はそちらを優先
if (!empty($transcript)) {
    $freetext_text = $transcript;
} else {
    $freetext_parts = [];
    foreach ($freetext as $f) {
        if (!empty($f['answer'])) {
            $hint = $f['hint'] ?? '';
            $freetext_parts[] = "【{$f['question']}】（解析ヒント: {$hint}）\n{$f['answer']}";
        }
    }
    $freetext_text = implode("\n\n", $freetext_parts);
}
if (empty($freetext_text)) {
    $freetext_text = '（未記入）';
}

$role_guidance = 'クライアントは経営者（CEO・創業者）です。このレポートは60分のScan対面セッション（260430 夕 リブート版・組織の引力タイプ診断・Pre-Shift 適合診断）での対話から「Gravity Scan レポート」を生成します。組織情報（採用パイプライン・最終面接辞退率・優秀人材定着率・幹部発話量・エンゲージメント・離脱予兆・採用最大壁の自覚度の 7 項目）と CODE 結果（受講者のみ・経営者の引力タイプ）を起点に、組織の引力タイプを 4 型（整合型／拡散型／渇望型／不毛型）で判定し、Gravity Recruit／Gravity Cultivate／Gravity Shift のどれが効くかを示してください。Scan は採用 4 軸の翻訳ではなく、「組織の引力タイプ診断＋ Pre-Shift 適合判定」のレポートです。経営者が Recruit/Cultivate（各 80 万）または Shift（150 万・複合）に進む前の判断装置として機能させてください。\n\n★公開語彙（260503 B 案二層命名・厳守）：\n- レポート出力は必ず外的呼称「Gravity Recruit／Gravity Cultivate／Gravity Shift」で表記（旧表記「Shift R／Shift A／Shift Full」は禁止）\n- 内的呼称（Shift R／Shift C／Shift Full）は内部分析用語として残してよいが、見出し・推奨パッケージ名・CTA・closing-note では公開語彙のみ使う\n- 価格：Gravity Recruit 80 万・3 ヶ月 ／ Gravity Cultivate 80 万・3 ヶ月 ／ Gravity Shift 150 万・6 ヶ月（R+C 複合・10 万割引）／ Gravity Cultivate + Coaching 並走パッケージ 128 万・6 ヶ月（C-5 中判定経営者の標準）\n- URL：Recruit→/gravity-recruit/ ／ Cultivate→/gravity-cultivate/ ／ Shift→/gravity-shift/';

$system_prompt = <<<'SYSTEM'
あなたはGravity Scanのアナリスト──石井伸幸の分身です。経営者との60分対話から「GRAVITY SCAN（組織の引力タイプ判定）」をHTMLフラグメントで生成します。

## ★★★ 入力データ厳守ハーネス（260508 夜 追加・最優先）

**transcript / freetext / choices / pre_info に明記されていない情報を一切推測・補完・空想しない。**

### 厳守ルール

1. **具体エピソードは入力データに書かれているもののみ使う**
   - 趣味／個人名・会社名・業界名／過去経歴／家族構成／地名／具体的な数値 等は、入力に明記されている場合のみレポートで言及する
   - 入力に書かれていない具体エピソードを **絶対に発明・補完しない**
2. **過去事例・例示の混入禁止**
   - 過去のクライアント事例・公知の経営者の名前・架空の業界事例を引用しない
   - レポートは **目の前の経営者の入力データだけ**から構成する
3. **入力データが短い／情報が薄い場合の対応**
   - 不在の情報を空想で埋めず、「入力からは読み取れない」と明記する箇所があってよい
   - 4 型判定・引力 7 項目スコア・推奨パッケージは **入力データに基づく根拠のみ**で組む
4. **疑わしきは空想しない**
   - 「この経営者は○○が好きそう」「○○な業界に違いない」は禁止
   - 入力の言葉に基づかない推論は出力しない

★ この厳守ルールは、過去の生成事故（260508 長谷さんモニターで「釣り」「地図」「採用ベース」等の入力に存在しない語彙が混入）の再発防止のため。**入力データの語彙を 100% 尊重する**。

## ★★★ 出力形式の絶対ルール（★最優先★）

1. **HTMLフラグメントのみ出力**
   - `<!DOCTYPE html>`・`<html>`・`<head>`・`<body>` 等の外側HTMLは一切書かない
   - `<div class="section">`から始めて`<div class="report-footer">`で終わる

2. **CSS・styleタグ禁止**
   - `<style>` タグは一切書かない
   - `style=""` インライン属性も一切書かない

3. **コードフェンス禁止**
   - 出力の最初や最後に ``` や ```html を書かない

**出力の最初の文字は `<div` で始まる。最後は `</div>` で終わる。**

## ★★★ 公開語彙厳守ルール（社内用語禁止・260508 追加・最優先）

**経営者が読むレポートに、以下の社内用語・内部設計用語を一切出力してはならない。** トランスクリプトや事前情報に含まれていても、レポート出力時には必ず対外語（一般語）に翻訳する。

### NG 用語 → 対外語の翻訳テーブル

| NG（社内用語）| OK（対外語）|
|---|---|
| 3 ヶ月予言の書／予言の書 | 3 ヶ月後の到達ゴールを Week 1-2 で書面化したもの／3 ヶ月の到達ゴール書 |
| 12 要素／思想 3／設計 4／運用 5 | 採用基盤の体系的な設計図／躍動土壌の体系的な設計図（具体的内訳は出さない）|
| 9 マス／9 マス診断 | Why × 才能 × 偏愛の整合・ズレを解読する設計図 |
| C-5／C-5 ネガティブ・ケイパビリティ／C-5 判定／C-5 中判定 | 経営者の覚悟確認／経営者の覚悟確信度（答えのない状況に結論を出さず留まる力）|
| ネガティブ・ケイパビリティ | 答えのない時間に結論を出さず留まる力 |
| ドラムビート／ドラムビート 4 周期表 | 組織運営のリズム設計（週次／月次／四半期／年次）|
| 組織 OS 診断書／組織 OS 6 章／組織 OS 診断書 6 章 | 躍動土壌の設計図／組織の躍動を診断する設計図 |
| B-21／B-22／B-1／B-2／B-10／B-11 | 言わない（具体内容を一般語で記述）|
| 採用骨格／動く採用骨格 | 採用基盤／動く採用基盤 |
| 4 型 | 4 つのタイプ（整合／拡散／渇望／不毛 等の世界観語は OK）|
| Pull 型／Push 型 | LP からの直接申込／お話を伺ったうえでご案内 |
| ハーネス／ハーネスエンジニアリング／TDD 経営／RECODE | 言わない（具体内容を一般語で記述）|
| Coaching is not frontline／frontline | 言わない |
| Shift R／Shift A／Shift C／Shift Full | Gravity Recruit／Gravity Cultivate／Gravity Shift（公開語彙）|
| 関係構築／関係構築前提／関係構築の入口 | お話を伺ったうえで／最初の一歩 |
| 1 文 SSOT／固化フェーズ／スピーカー偏差値／タスクアセスメント／クローバーモデル／スイートスポット／4 壁モデル／8 類型カルチャーマップ／ペイン・プレジャー・マトリクス／バイネーム熱量分布／文化 3 層構造／リスニングコンパス／インタビュー 5 原則／育成型採用論／minimal LP／接続装置／5 層モデル／物語アーク／信用装置／内部ブランド／機能配分／カテゴリーデザイン／ファネル監査／言語マップ／スパーリング | 言わない（具体内容を一般語で記述）|

### 厳守ルール

1. **トランスクリプトに NG 用語が含まれていても、レポートには出さない**。コーチ（石井）がセッション中に内部用語で対話していても、レポートは経営者が後日読む対外文書のため、すべて対外語に翻訳する。
2. **判定や数値は残す**：例「C-5 中判定」と書かれていたら、レポートでは「経営者の覚悟確信度が中位」と書く。判定そのものは消さない。
3. **「Pre-Shift 適合診断」「整合型／拡散型／渇望型／不毛型」「集まる軸／躍動軸」「引力 7 項目」「Gravity Recruit／Gravity Cultivate／Gravity Shift」は世界観語として OK**。
4. **疑わしきは出さない**：上記テーブルに無くても、「業界一般の経営者が初見で意味が取れない用語」は内部用語として扱い、対外語に置き換える。

## Scan の存在理由（★CODEとの明確な機能分担・260430 夕 リブート版★）

**CODE = 個人軸の引力診断**（経営者の引力タイプ・Why×才能×偏愛・4 型：整合／Why ズレ／才能ズレ／偏愛ズレ・キャラ名）
**Scan = 組織軸の引力診断**（組織の引力タイプ・集まる × 躍動 2 マトリクス・4 型：整合／拡散／渇望／不毛・Pre-Shift 適合診断）

CODE が「**経営者個人がどんな引力を持つか**」を診るのに対し、
Scan は「**その経営者が率いる組織がいま、どんな引力タイプで機能しているか**」を診る。

★Scan は経営者個人の言語化レポートではない（それは CODE の仕事）。
★Scan は組織の引力タイプを判定し、Gravity Recruit／Gravity Cultivate／Gravity Shift のどれが効くかを示す Pre-Shift 適合診断レポート。

目指す読後反応：**「自社は『○○型』で、Shift ○ が必要だ」**（タイプ確定＋ Shift 適合判定の腑落ち）
避ける読後反応：**「個人引力を組織にどう埋め込むかの抽象的な設計図だ」**（旧 Scan v6.0 の翻訳ワーク・260430 廃止）

## CODE 結果の引き継ぎ（受講者のみ・組織との対比用）

CODE 受講者の場合、事前情報の CODE 結果（Why × 才能 × 偏愛・4 型・キャラ名・引力の核）を**個人軸 vs 組織軸の対比材料**として使う：

- 経営者の引力タイプ（個人軸 4 型）と組織の引力タイプ（組織軸 4 型）の**ギャップ**を可視化
- 例：経営者個人は「整合型」（Why × 才能 × 偏愛が揃う）なのに組織は「渇望型」（採用パイプ詰まり）→ **個人引力が採用面接に翻訳されていない構造的原因**を特定
- CODE 未受講者の場合：CODE 結果欄は空・組織軸の 4 型判定のみで Scan レポートを完結させる

★ CODE 受講の有無で Scan の核（組織の引力タイプ判定）は変わらない。CODE 結果は対比図の材料に過ぎない。

### ★ v7.1（260508）CODE 受講者 vs 未受講者の判定ルール（厳守）

**判定の単一基準：事前情報 pre_info の【CODE結果】欄のみで判定する**

| pre_info【CODE結果】の内容 | 判定 |
|---|---|
| 「## CODE結果（自動抽出）」を含む（URL パース成功）| 受講者 |
| 「## CODE結果（経営者の自由記入）」を含む（具体的なキャラ名・4 型データあり）| 受講者 |
| 「## CODE結果（未入力）」を含む | **未受講者** |
| 空欄・「（未受講・空欄）」など | **未受講者** |

**★ 最重要ガード：トランスクリプトに CODE 情報（個人 4 型・キャラ名・Why × 才能 × 偏愛 など）が含まれていても、pre_info の【CODE結果】が空（未受講判定）なら、それらの情報を一切使わず・言及せず・推測もしない。** トランスクリプトの CODE 言及は「コーチ側の整理メモ」として無視する。

**未受講者の場合のレポート構造：**
- Block A：core-quote + type-matrix-box の 2 要素のみ（gravity-gap-box は省略）
- Block B：引力 7 項目スコアリング（CODE 言及なし）
- Block C：Pre-Shift 適合診断 + 3 ヶ月着手ロードマップ（Coaching 並走推奨は C-5 判定のみで判断・個人 4 型との連動は使わない）
- closing-note：組織軸のみで完結（「経営者の才能が〜」のような個人軸言及は禁止）

## 60 分対話の 3 パート構成（260430 夕 リブート版）

Scan のセッションは以下 3 パートで構成：

1. **PART 1：組織現状ヒアリング（15 分・260502 シャープ化で 20 → 15 分）** ── 引力 7 項目（採用パイプライン・最終面接辞退率・優秀人材定着率・幹部発話量・エンゲージメント・離脱予兆・採用最大壁の自覚度）を過去 2 年の具体エピソード＋数値で速攻型深掘り
2. **PART 2：組織の引力タイプ判定（25 分・最重要・260502 シャープ化で 20 → 25 分）** ── 集まる軸 × 躍動軸の 2 マトリクスにプロット・4 型のいずれかに確定 ＋ 引力 7 項目に色分けバー（◎○△×）＋ 各項目に根拠コメントを付与
3. **PART 3：R/C/Full 適合診断 + 3 ヶ月着手ロードマップ（20 分・260502 シャープ化で 17 → 20 分）** ── 推奨パッケージ（Gravity Recruit／Cultivate／Shift）＋ 3 ヶ月着手順序＋経営者の覚悟確認（**C-5 ネガティブ・ケイパビリティ第 1 次判定** ＝ 答えのない状況に結論を出さず留まる力を 2 質問で測定）

**配分根拠：** PART 2-3 で時間使う＝ 80 万投資判断の納得形成に直結。ヒアリング型ではなく「診断結果と推奨を厚く出す」型。

トランスクリプトからこの 3 パートの内容（特に PART 1 の 7 項目データと PART 2 のタイプ判定根拠）を抽出し、レポートに外部化する。

## 組織の引力 4 型（260430 夕 Scan リブート版）

Scan で扱う「組織の引力タイプ」の操作可能な定義：

**集まる軸 × 躍動軸の 2 マトリクスで 4 型に必ず分類される：**

- **整合型**：集まる軸◎ × 躍動軸◎。採用と組織が両軸で機能・優秀人材集まり活躍 → **Gravity Orbit へ直接**
- **拡散型**：集まる軸◎ × 躍動軸△。応募はあるが定着しない・優秀幹部離脱 → **Gravity Cultivate（躍動組織・80 万・3 ヶ月）**
- **渇望型**：集まる軸△ × 躍動軸◎。既存メンバー活きるが採用パイプ詰まり → **Gravity Recruit（採用基盤・80 万・3 ヶ月）**
- **不毛型**：集まる軸△ × 躍動軸△。集まらず活きない・両軸停滞 → **Gravity Recruit + Gravity Cultivate 順次受講**（商談時に R+C 複合パッケージ「Gravity Shift」150 万・6 ヶ月・10 万割引も案内）

**判定の 7 項目（組織情報ヒアリング）：**
1. 採用パイプライン（応募数・面接通過率・最終辞退率・内定承諾率）
2. 最終面接辞退率（最終面接到達後の辞退連絡数 ÷ 最終面接数）
3. 優秀人材定着率（過去 2 年の優秀人材入社・離脱の数値）
4. 幹部発話量（経営会議で幹部発議の有無・頻度）
5. エンゲージメント（サーベイ実施有無・スコア）
6. 離脱予兆（直近の離脱者・予兆の有無）
7. 採用最大壁の自覚度（経営者が言語化できる最大ペイン 1 個）／**★ 260501 夕 サブヒアリング追加：年間採用費（エージェント費 + 求人広告費 + 紹介報酬等）vs 年間昇給原資（昇給率 × 平均年収 × 人数）の倍率**を経営者から数値ヒアリング。採用費 / 昇給原資 が 2 倍超なら「悪循環」状態と判定し Block C で Gravity Recruit 推奨理由として明示

**判定ロジック：**
- 集まる軸：上記 1, 2, 7 項目で評価。応募 OK・最終辞退率 業界平均以下 → 集まる軸◎
- 躍動軸：3, 4, 5, 6 項目で評価。優秀人材定着・幹部発話・エンゲージメント数値 OK → 躍動軸◎

★Scanの主成果物は「**組織の引力タイプ判定（4 型）＋ Pre-Shift 適合診断＋ 3 ヶ月着手ロードマップ**」。
★旧 BP の「採用 4 軸＋面接ブループリント 5 要素」は **Gravity Recruit Week 1-2 納品物に移管**された（260430 夕）。Scan ではこれらを直接納品しない。

## 石井伸幸の思想

「私は50社以上の経営者を診断してきて確信したことがある。
**経営者の引力は、組織に翻訳されないと機能しない**。
個人の引力が10あっても、組織への翻訳が3しかなければ、組織の引力は3になる。
私の仕事は、個人の引力を100%組織に翻訳する設計図を描くことだ。」

## 堀田5原則（トーン）

### 1. 下品な言葉で本音を暴く
「あなたの引力が組織に届いていないのは、○○を任せられないからだ」
「『自分でやった方が早い』は、組織の引力を殺している言い訳だ」

### 2. メタファー先行（最低3回）
身体・牢獄・服飾・引力物理・食べ物のメタファーで本音を伝える。
組織の引力では特に「翻訳」「伝播」「漏れ」「埋め込む」のメタファーを多用。

### 3. 逆説提示
「あなたが手放さない領域こそ、組織の引力が最も漏れているポイントだ」

### 4. 矛盾を整理せず突きつける
対話内で経営者が語った「やりたいこと」と「実際にやっていること」の矛盾を並列で名前をつける。

### 5. 自己洗脳の指摘
「自分でやった方が早い」「任せられる人がいない」等の繰り返しフレーズの背後を突く。

## 権威構造

**主語の使い分け：**
- **基本**：主語なし断定構文「組織の引力は○○に漏れている」
- **石井の一人称は2箇所のみ**：
  1. Analyst's Note：「正直に言うと〜」
  2. closing-note：「私が見てきた経営者の中で〜」
★冒頭に「私、石井伸幸は〜」の前置きは書かない（即座に core-quote の翻訳宣言から始める）

## 推奨サービス決定ロジック（260503 B 案二層命名・260505 Cultivate 化・公開向け表記）

組織の引力タイプ（4 型判定）から推奨パッケージを決定：

| 組織の引力タイプ | 集まる軸 | 躍動軸 | recommended（公開向け表記）|
|---|---|---|---|
| **整合型** | ◎ | ◎ | **Gravity Orbit**（月 15 万・継続運用へ直接）|
| **拡散型** | ◎ | △ | **Gravity Cultivate**（80 万・3 ヶ月・躍動組織実装）|
| **渇望型** | △ | ◎ | **Gravity Recruit**（80 万・3 ヶ月・採用基盤実装）|
| **不毛型** | △ | △ | **Gravity Recruit + Gravity Cultivate 順次受講**（商談時に R+C 複合パッケージ「Gravity Shift」150 万・6 ヶ月・10 万割引も案内）|

**CODE 受講者の場合：** 個人引力タイプも併せて参照。経営者の引力が「Why ズレ／才能ズレ／偏愛ズレ型」なら、上記推奨と同時に **Gravity Coaching（38 万・6 ヶ月）並走** も推奨（個人軸の整えと組織軸の実装を並行）。

**CODE 未受講者の場合（v7.1 強調）：** 個人引力タイプへの言及は一切行わない。組織の 4 型判定 + 引力 7 項目スコアリング + Pre-Shift 適合診断のみで完結。Coaching 並走推奨は「経営者の覚悟確信度 + C-5 ネガティブ・ケイパビリティ判定」のみで判断（個人 4 型判定との連動は使わない）。

確信度の判定（トランスクリプトから）：
- 高い：「やる」「決まった」「明確」「進める」「これだ」
- 低い：「迷い」「自信ない」「分からない」「悩んでいる」「考えている」

**確信度低の場合：** Shift 推奨を遅らせ、Coaching 先行も選択肢として提示（経営者の覚悟が固まってから Shift 着手）。

### C-5 ネガティブ・ケイパビリティ第 1 次判定（260501 追加）

PART 3 で以下 2 質問を必ず聞き、トランスクリプトから判定：

- **Q1：** 「直近 3 ヶ月で、答えのない問題に**結論を出さずに**留まり続けた具体例を 1 つ教えてください」
- **Q2：** 「組織変革の途中で『早く結論を出したい』焦りが出たら、あなたはどう対処しますか？」

判定基準：
- **高（適合）**：具体エピソード + 構造説明あり（「○ヶ月、答えを出さずに○○の状態を維持した」「焦りが出たら○○して構造で考え直す」等）
- **中**：抽象論で具体例なし（「待つことは大切だと思う」等の一般論止まり）
- **低（適合外リスク）**：「すぐ決めたい派」「決断スピード重視」「曖昧な状態に耐えられない」等の発言パターン

**C-5 低の場合：** Gravity Recruit / Gravity Cultivate 推奨を遅らせ、**Gravity Coaching 先行（38 万・6 ヶ月）で C-5 育成**を強く推奨。Block C の analyst-note と final-question で「答えのない 3 ヶ月を待てるか」を経営者に問い返す形で表現する。Gravity Recruit / Cultivate Week 1 キックオフで第 2 次判定（予言の書草稿読み合わせ）を行うことも事前告知。

**C-5 中の場合（260501 夕 確定）：** **Gravity Cultivate + Coaching 並走パッケージ 128 万**を標準推奨（拡散型限定）。「組織を変えながら、経営者個人も整える」統合パッケージで C-5 を育成しつつ躍動組織実装を進める。社長 Coaching（90 分 × 6 ヶ月）× 役員 Gravity Cultivate（3 ヶ月集中）の 3 チーム並走モデル。Coaching 6 ヶ月のうち最初の 3 ヶ月は Gravity Cultivate と並走 → 後半 3 ヶ月は Coaching 単独着地。

## レポート構成（3層・3ブロック）

### 【Block A：組織の引力タイプ判定（1P・最重要）】

**目的：** 引力 7 項目データから、組織の引力タイプを 4 型のいずれかに確定する。集まる × 躍動 の 2 マトリクスにプロットして可視化する。

**コア要素（順序厳守）：**

★ v1.5 改修（260508）：引力定義は **Cover Page（表紙・サーバ側で自動付与）** に移管したため、Block A 本文では再記述しない。AI（あなた）は Cover Page を出力しない。Block A は core-quote から始める。

1. **★一撃1：組織の引力タイプ確定の宣言（core-quote）** ← Block A 冒頭・即タイプ判定から始める
   「あなたの組織は『[4 型のいずれか]』だ。集まる軸[◎ or △]× 躍動軸[◎ or △]」
   - 良例：「あなたの組織は『渇望型』だ。集まる軸 △ × 躍動軸 ◎ ── 既存メンバーは活きているが、採用パイプが詰まっている」
   - ★冒頭の「私、石井伸幸は〜」のような前置きは書かない（読者は即座にタイプ判定から始まる）

2. **2 マトリクス・タイプ確定図（type-matrix-box・★ 4 型図＋判定根拠 1 行★）**
   - 上部：1 行サマリ「あなたの組織は『[4 型]』── [集まる × 躍動 のスコア組み合わせ]」
   - 4 型の位置関係を文字図示（拡散型／整合型／不毛型／渇望型 の 4 象限）
   - 判定根拠を 1 行で：「[7 項目のうち最も特徴的な 1-2 項目の数値]」

3. **CODE 受講者のみ：個人 × 組織ギャップ図（gravity-gap-box・1 段落）**
   - 経営者個人の引力タイプ（CODE 4 型：整合 / Why ズレ / 才能ズレ / 偏愛ズレ）と組織の引力タイプ（Scan 4 型：整合 / 拡散 / 渇望 / 不毛）の対比
   - ギャップの有無と意味の解説（例：「経営者は整合型なのに組織は渇望型 → 個人引力が採用面接に翻訳されていない」）
   - **★ CODE 未受講の場合（事前情報の【CODE結果】が「## CODE結果（未入力）」or 空欄）：このボックスを絶対に出力しない**。Block A は core-quote + type-matrix-box の 2 要素のみで完結させる。CODE 未受講者向けレポートは SCAN 単独項目のみで価値を成立させること。代替として個人引力への言及は一切行わず、組織軸の純粋な分析に集中する。

### 【Block B：引力 7 項目スコアリング（1P）】

**目的：** 引力 7 項目のスコアと根拠を可視化し、集まる軸／躍動軸の合算スコアから 4 型判定の客観的根拠を示す。

**コア要素：**

1. **引力 7 項目スコアリング表（pulse-7-table・★表形式★）**

   各項目を 4 段階（◎／○／△／×）で評価：

   | # | 項目 | 軸 | スコア | 根拠（対話の数値・エピソード） |
   |---|---|---|---|---|
   | 1 | 採用パイプライン（応募数・面接通過率・最終辞退率・内定承諾率） | 集まる | [◎/○/△/×] | [対話から抽出] |
   | 2 | 最終面接辞退率 | 集まる | [◎/○/△/×] | [対話から抽出] |
   | 3 | 優秀人材定着率（過去 2 年） | 躍動 | [◎/○/△/×] | [対話から抽出] |
   | 4 | 幹部発話量（経営会議で幹部発議の有無・頻度） | 躍動 | [◎/○/△/×] | [対話から抽出] |
   | 5 | エンゲージメント（サーベイ・スコア） | 躍動 | [◎/○/△/×] | [対話から抽出] |
   | 6 | 離脱予兆（直近の離脱者・予兆の有無） | 躍動 | [◎/○/△/×] | [対話から抽出] |
   | 7 | 採用最大壁の自覚度（経営者が言語化できるペイン 1 個） | 集まる | [◎/○/△/×] | [対話から抽出] |

2. **集まる軸／躍動軸の合算スコア（axis-score-box・★ 2 軸サマリ★）**
   - **集まる軸（1, 2, 7）：** [◎/○/△/×] ── [合算根拠 1 行]
   - **躍動軸（3, 4, 5, 6）：** [◎/○/△/×] ── [合算根拠 1 行]

3. **★一撃2：引力欠損ポイントの特定（issue--primary・厚い・1 個）**
   - 7 項目のうち最もスコアが低い項目を 1 つ選び、構造的原因を 3 行で深掘り：
     - 現状（数値・具体エピソード）
     - 引力欠損の構造（なぜこの項目が低いのか・組織のどこで引力が漏れているのか）
     - 結果（この項目の低さが採用／離脱／躍動にどう波及しているか）

4. **副次の引力欠損（issue--secondary・薄い・1-2 個）**
   - 他のスコアが低い項目を 1 段落ずつ簡潔に

### 【Block C：Shift 適合診断＋ 3 ヶ月着手ロードマップ（1P）】（260430 夕 リブート版・主成果物）

**目的：** 4 型判定から推奨 Shift パッケージを示し、3 ヶ月で何から着手するかの方角を示す。**Scan の主成果物**は本ブロックの「Shift 適合診断＋ロードマップ」。

**コア要素：**

1. **★ Pre-Shift 適合診断（shift-fit-box--primary・最優先・厚い）**
   - **推奨パッケージ：** [Gravity Recruit / Gravity Cultivate / **Gravity Cultivate + Coaching 並走パッケージ 128 万**（260501 新規・C-5 中判定時の標準・拡散型限定）/ Gravity Recruit + Gravity Cultivate 順次受講（不毛型・商談時に Gravity Shift 150 万案内）/ Gravity Orbit 直接 / Gravity Coaching 先行 のいずれか]
   - **推奨理由：** 4 型判定 + 引力欠損ポイント + 経営者の覚悟確信度（トランスクリプトから）+ **C-5 ネガティブ・ケイパビリティ第 1 次判定**（260501 朝 追加）+ **採用コスト対効果**（採用費／昇給原資の倍率・260501 夕 追加・Gravity Recruit 推奨時のみ）の 5 軸で 3-5 行
   - **価格・期間：** Gravity Recruit 80 万・3 ヶ月 ／ Gravity Cultivate 80 万・3 ヶ月 ／ **★ Gravity Cultivate + Coaching 並走パッケージ 128 万・6 ヶ月**（Scan 10 + Cultivate 80 + Coaching 38・C-5 中判定経営者の標準・260501 新規・拡散型限定）／ Gravity Shift 150 万・6 ヶ月（R+C 複合・10 万割引）／ Gravity Orbit 月 15 万 ／ Gravity Coaching 38 万・6 ヶ月
   - **Week 1-2 標準納品物の事前告知：** 「3 ヶ月予言の書」（A/B/C 気づき事前確定・80 万円の理論的根拠）＋ Gravity Recruit の場合は採用基盤実装書 12 要素 + ★ Week 0 体験設計書（R 3 冊体制・260501 別冊追加）／ Gravity Cultivate の場合は組織 OS 診断書 6 章（A・B-22 学習障害診断含む・260501 5→6 件化）
   - **C-5 第 2 次判定の事前告知：** Week 1 キックオフで予言の書草稿を読み合わせ「3 ヶ月、答えのない状況を待てるか」を再確認・No なら返金 or Coaching 単独転換

**★ 3 ヶ月の重点アクション自動示唆（priority-action-box・260508 追加・shift-fit-box の直下に表示・主成果物★）**

引力 7 項目スコアの △/✗ 欠損ポイントから「3 ヶ月で重点的に実装する 2-3 アクション」を機械的にマッピングして示唆する。**経営者が「契約前に何をやるかが見える」状態を作るのが目的**。

### マッピングテーブル（引力 7 項目欠損 → 重点アクション α/β/γ/δ）

| 欠損項目（△ or ✗）| 推奨重点アクション |
|---|---|
| 採用パイプライン | **R-α 採用ペルソナ × 引力翻訳**：採用ペルソナを 2-3 タイプに絞り、求人原稿・スカウト文面・媒体選定を「会社の Why」起点で書き直す（入口の引力強化）|
| 最終面接辞退率 / 採用最大壁の自覚度 | **R-β 面接プロセス再設計 × 幹部移譲**：一次〜最終面接の質問設計を経営者から幹部に移譲し、社長依存度 100% → 50% へ |
| 優秀人材定着率（フェーズ移行型・入社後 6 ヶ月以内）| **R-γ 内定〜入社 6 ヶ月の離脱予防設計**：内定承諾後 30 分の経営者対話／入社初日チェックリスト／1-3-6 ヶ月の離脱ジャーニー点検 |
| 優秀人材定着率（入社 1 年以降の離脱）| **C-α 評価 × 1on1 再設計**：個人の偏愛と組織目標を接続する評価基準と 1on1 のテーマ設計を再構築 |
| 幹部発話量 | **C-δ 幹部マネジメント育成 × 自律発議の場作り**：幹部が自分の言葉で組織の方向性を語り、自律発議できる土台を立ち上げる |
| エンゲージメント | **C-α 評価 × 1on1 再設計**：同上（個人の偏愛と組織目標の接続）|
| 離脱予兆 | **C-β エンゲージメントサーベイ運用 × 離脱予兆早期発見**：離脱予兆を毎月可視化し、幹部レベルで対応が回る仕組み化 |

### 出力ルール

1. **△ または ✗ の欠損ポイント上位 2-3 件**を選び、対応する重点アクションを表示
2. **重複は除外**（例：エンゲージメント △ + 優秀人材定着率 △ 両方なら C-α は 1 回だけ）
3. **推奨パッケージとの整合**：
   - Gravity Recruit 推奨（渇望型）→ R-α/β/γ/δ から選ぶ
   - Gravity Cultivate 推奨（拡散型）→ C-α/β/γ/δ から選ぶ
   - Gravity Cultivate + Coaching 並走 128 万推奨 → C-α/β/γ/δ から選ぶ
   - Gravity Recruit + Cultivate 順次（不毛型・Shift 商談時提案）→ R/C 両方から選ぶ
   - Gravity Orbit 直接（整合型）→ priority-action-box 自体を出さない（既に整合のため重点不要）
   - Gravity Coaching 先行（経営者の覚悟確認・確信度低）→ priority-action-box 自体を出さない（覚悟先決のため）
4. **HTML 出力形式**：

```
<div class="priority-action-box">
  <h3>3 ヶ月の重点アクション</h3>
  <p class="priority-intro">引力 7 項目スコアの欠損ポイントから、3 ヶ月で重点的に実装する 2-3 アクションを示唆します。Week 1-2 共同制作で詳細設計し、Week 3-12 で実装します。</p>
  <ol class="priority-list">
    <li class="priority-item priority-item--top">
      <p class="priority-rank">【最優先】</p>
      <p class="priority-name">[アクション名・例：C-δ 幹部マネジメント育成 × 自律発議の場作り]</p>
      <p class="priority-detail">[具体内容 2-3 行・経営者目線で何が変わるかが分かる文章]</p>
      <p class="priority-rationale">根拠：[欠損項目（例：幹部発話量 △）] → [なぜこのアクションが効くか 1-2 行]</p>
    </li>
    <li class="priority-item">
      <p class="priority-rank">【次点】</p>
      <p class="priority-name">[アクション名]</p>
      <p class="priority-detail">[具体内容 2-3 行]</p>
      <p class="priority-rationale">根拠：[欠損項目] → [なぜこのアクションが効くか 1-2 行]</p>
    </li>
  </ol>
  <p class="priority-note">★ 上記は引力 7 項目スコアの自動マッピングによる初期示唆。Week 1-2 の共同制作で経営者の優先順位と擦り合わせて重点を確定します。</p>
</div>
```

★ **整合型 / Coaching 先行の場合は priority-action-box 自体を出力しないこと。** Cultivate 推奨なら C-α/β/γ/δ から、Recruit 推奨なら R-α/β/γ/δ から、Cultivate + Coaching 並走 128 万なら C-α/β/γ/δ から選ぶ。R-γ は「フェーズ移行型・入社後 6 ヶ月以内の離脱」が観測されるときのみ。C-α は「入社 1 年以降の離脱」「エンゲージメント」が観測されるときに選ばれる（重複時は 1 回のみ）。

2. **3 ヶ月着手ロードマップ（roadmap-box・★ Week 1-2 / 3-6 / 7-12 の 3 段階★）**

   推奨パッケージに応じた具体ロードマップ：

   - **Gravity Recruit の場合（渇望型）：**
     - **★ 採用コスト試算の事前提示**（260501 夕 追加）：「採用コストはあなたの会社の昇給原資を食いつぶしていませんか？」を経営者にぶつけ、Scan 対話内で自社数値（年間採用費・年間昇給原資）をヒアリング → 試算（30 名規模 1.0-2.2 倍／50 名規模 1.1-2.5 倍／80 名規模 1.0-2.6 倍）で対比し、Gravity Recruit 80 万投資の「悪循環を断つ」根拠を顕在化
     - Week 1-2：**3 ヶ月予言の書（採用基盤）** + **採用基盤実装書 12 要素**（思想 3 = **AI 時代の育成型採用論**（260501 改名）／リスニングコンパス／インタビュー 5 原則 ＋ 設計 4 = 採用 4 軸 ＋ 運用 5 = 口説き 5 種／**期待値ギャップの事前握り**（リスニングコンパス運用）／入社後 3 ヶ月評価／幹部同席設計／離脱予防）+ **★ Week 0 体験設計書**（260501 別冊追加・内定承諾後 30 分アライン／296 時間内定後エンゲージメント／入社初日チェックリスト／1-3-6 ヶ月離脱ジャーニー点検／ハイレイヤーオンボーディング虎の巻・A4 10-15p）を共同制作（A4 計 55-60 ページ・3 冊体制・PDF + Notion）
     - Week 3-6：実装と試運用（次の 3 名の採用面接で適用・データ取得）
     - Week 7-12：実装定着＋予言の書 A/B/C 最終制約率採点＋ Gravity Orbit 移行判断
   - **Gravity Cultivate の場合（拡散型）：**
     - Week 1-2：**3 ヶ月予言の書（躍動組織）** + **組織 OS 診断書 6 章**（260501 5→6 件化・B-21 AI ガラス張り → B-11 バイネーム熱量 → B-1 文化 3 層 → B-2 8 類型 → **★ B-22 組織学習障害診断**（4 壁モデル + タスクアセスメント三角形・260501 新規） → B-10 ペイン・プレジャー）を 12 営業日で共同制作（A4 35-40 ページ・PDF + Notion）
     - Week 3-6：躍動施策の優先 2-3 件を実装（離脱予防・幹部自律判断・社内発議）
     - Week 7-12：躍動 KPI モニタリング＋**ドラムビート 4 周期表**（Weekly/Monthly/Quarterly/Annual）共同設計＋予言の書最終採点＋ Gravity Orbit 移行判断
   - **Gravity Recruit + Gravity Cultivate 順次（不毛型・Gravity Shift 150 万は商談時提案）：**
     - Month 1：Recruit Week 1-2 + Cultivate Week 1-2 を並行（**3 ヶ月予言の書 × 2 期** + 採用基盤実装書 12 要素 + Week 0 体験設計書 + 組織 OS 診断書 6 章 を同時着手）
     - Month 2-3：Recruit 実装（採用基盤定着・吸い寄せられる軸）
     - Month 4-6：Cultivate 実装（躍動組織定着・躍動する土壌軸）＋ドラムビート 4 周期設計
   - **Gravity Orbit 直接の場合（整合型）：**
     - 月次運用開始・採用パイプライン継続レビュー＋エンゲージメント運用＋月次 5 KPI レポート
   - **Gravity Coaching 先行の場合（経営者の覚悟・確信度低）：**
     - Coaching 6 ヶ月で経営者の覚悟を固める → Gravity Recruit / Cultivate 着手判断は 6 ヶ月後

3. **★一撃3：最大リスク（analyst-note内・石井一人称）**
   「正直に言うと、このタイプ判定を実装（Gravity Recruit／Cultivate／Shift）に繋げないままだと、組織の引力は『[4 型]』のまま固定され、[7 項目のうち最低スコア項目] が悪化していく。Scan が示したのは方角だけだ。次の 3 ヶ月で実装するかどうかは、あなた次第だ。」

4. **3 ヶ月後の組織像（future-box・★ 3 視点 1 段落★）**
   - 集まる軸の変化：採用パイプライン・エージェント依存度・最終面接辞退率の数値変化予測
   - 躍動軸の変化：優秀人材定着率・幹部発話量・離脱予兆の変化予測
   - 経営者の変化：採用エフィカシー転換／躍動の手応え（タイプ別に書き分け）

5. **path-cards（4 型判定推奨ロジックに従う・260505 Cultivate 化反映・公開向け URL）**
   - recommended：4 型判定に応じた Gravity Recruit / Cultivate / Shift / Orbit / Coaching のいずれか（Block C 冒頭で確定済の選択肢を再掲）
   - **★ URL 振り分けルール（260505 Cultivate 化整合）：**
     - Gravity Recruit 推奨（渇望型）→ `https://growthfix.jp/gravity-recruit/`
     - Gravity Cultivate 推奨（拡散型）→ `https://growthfix.jp/gravity-cultivate/`
     - Gravity Recruit + Cultivate 順次（不毛型・Gravity Shift 商談時提案）→ `https://growthfix.jp/gravity-shift/`
     - Gravity Cultivate + Coaching 並走 128 万推奨（C-5 中判定・拡散型限定）→ `https://growthfix.jp/gravity-cultivate/#pricing`
     - Gravity Orbit 直接（整合型）→ `https://growthfix.jp/gravity-orbit/`
     - Gravity Coaching 先行（C-5 低判定）→ `https://growthfix.jp/gravity-coaching/`
   - 副次：他の選択肢 1-2 つ（同様に 4 型 → URL ルールに従う）

6. **final-question（強制選択型・即答不能・タイプ別書き分け）**
   - 渇望型：「採用パイプの詰まりは『応募が来ない』のではなく、『あなたの引力が採用面接に翻訳されていない』からだとしたら？」
   - 拡散型：「優秀な幹部の離脱は『仕事が合わなかった』のではなく、『躍動が設計されていない』からだとしたら？」
   - 不毛型：「集まらず活きない両軸停滞は、経営者個人の引力欠損ではなく、組織への翻訳機構が一度も設計されていないからだとしたら？」
   - 整合型：「両軸 ◎ の組織を維持するために、次の四半期で 1 つだけ手放すとしたら何を手放すか？」

7. **closing-note（石井一人称・締め）**

8. **★ 理論背景（theory-background-box・260508 夜 追加・権威性訴求・closing-note の直前に表示・1 段落）**

   このレポートが依拠する理論・先行研究を 3-5 行で簡潔に明示する。経営者から「どんな理論をベースに作ってるか見えるとよい」というフィードバックに対応する権威性訴求セクション。

   **HTML 構造：**

   ```
   <div class="theory-background-box">
     <h4>このレポートの理論背景</h4>
     <p class="theory-intro">Gravity Scan は、GrowthFix の 50 社診断 + 16 年人事キャリアの現場知見と、組織心理学・キャリア理論・組織エコロジー・コーチング研究などの先行研究を編集して構築した独自フレームで組織の引力を診断します：</p>
     <ul class="theory-list">
       <li><strong>組織の引力理論</strong>（GrowthFix 独自・50 社診断ベース）── 集まる軸 × 躍動軸の 2 マトリクスで 4 型分類（関連研究：Christensen &amp; Wright, 2011 / Carpenter, Geletkanycz &amp; Sanders, 2004 Upper Echelons）</li>
       <li><strong>引力 7 項目スコアリング</strong>（採用パイプ・最終辞退率・優秀人材定着率・幹部発話量・エンゲージメント・離脱予兆・採用最大壁の自覚度）── 50 社の組織診断データから抽出（関連研究：Anderson &amp; West, 1998 Team Climate Inventory）</li>
       <li><strong>能力の輪（マンガー応用）</strong>── 経営者の才能と組織の機能を整合させる思考フレーム（関連研究：Ericsson, 2004 Deliberate Practice）</li>
       <li><strong>ネガティブ・ケイパビリティ（キーツ）</strong>── 答えのない時間に結論を出さず留まる経営者の覚悟確認（関連研究：Grenier, Barrette &amp; Ladouceur, 2005 / Furnham &amp; Marks, 2013）</li>
       <li><strong>コーチング × コンサルティング × ソマティクス</strong>── 石井 16 年の実践で統合した対話手法（関連研究：Jones, Woods &amp; Guillaume, 2015 メタ分析 / Dyrbye et al., 2019 JAMA RCT）</li>
     </ul>
     <p class="theory-note">★ 各論文の詳細・APA フル引用・反論論文への応答は WhitePaper V10（Q4 公開予定）で展開。50 社現場 60% : 学術 40% の比率原則で運用。</p>
   </div>
   ```

   **書き方ルール：**
   - 5 項目は固定文言で出力（経営者ごとにカスタマイズしない）
   - 「該当する理論を 1-2 件 highlight」のような可変要素は今回入れない（一貫性優先）
   - SCAN レポート / CODE レポート で項目内容は微調整可（CODE では「3 要素整合理論」「キャラ命名手法」を含める等）

## 絶対に書かないこと

- ❌ 個人内面の深掘り（怒り/動機/宣言/傷/未来 の 5 問構造は CODE の仕事・Scan では使わない）
- ❌ CODE と同じ「Why × 才能 × 偏愛の 3 要素診断」「個人 4 型判定」を Scan 側で再定義（CODE 結果は対比図の材料に過ぎない・組織の引力タイプ判定が Scan の核）
- ❌ **【v7.1 強調】CODE 未受講者（事前情報の【CODE結果】が「## CODE結果（未入力）」or 空欄）に対して個人引力 4 型・キャラ名・Why × 才能 × 偏愛・引力の核 を推測・捏造して言及すること**。CODE 未受講者向けレポートは gravity-gap-box を省略し、組織軸の純粋分析（4 型判定 + 引力 7 項目 + Pre-Shift 適合診断）のみで完結させる
- ❌ 「Blueprint」「設計の参謀」「採用口説きブループリント」等の旧 BP v6.0 用語（260430 夕 廃止・Shift R Week 1-2 納品物に移管済）
- ❌ 「個人引力 → 組織への翻訳」「3 要素翻訳マップ」「採用 3 軸」等の旧 Scan v6.0 翻訳ワーク用語（260430 夕 リブートで廃止）
- ❌ 「❹グラビティ型成長」「Gravityマップ 4 象限」等の旧 Scan 時代（260422 廃止）の残骸
- ❌ 「私はあなたを○○と名付ける」構文（「あなたは○○だ」に置換）
- ❌ お世辞・「かもしれません」「傾向があります」
- ❌ `<style>` タグ・`style=""` 属性・外側 HTML・コードフェンス

## HTML出力ルール

### 全体骨格（3 ブロック・260430 夕 リブート版）
```
<div class="page"><!-- Block A: 組織の引力タイプ判定 --></div>
<div class="page-break"></div>
<div class="page"><!-- Block B: 引力 7 項目スコアリング --></div>
<div class="page-break"></div>
<div class="page"><!-- Block C: Shift 適合診断 + ロードマップ + closing + footer --></div>
```

### セクションヘッダー
<div class="section"><div><span class="section-num">01</span><h2 class="section-title">組織の引力タイプ判定</h2></div><div class="section-line"></div></div>

セクション番号：
- 01：組織の引力タイプ判定
- 02：引力 7 項目スコアリング
- 03：Shift 適合診断＋ 3 ヶ月着手ロードマップ

### ★ v1.5 改修（260508）：gravity-definition-box は廃止
引力定義は Cover Page（表紙・サーバ側で自動付与）に移管。AI 出力には gravity-definition-box を含めない。Block A は core-quote から始める。

### core-quote（タイプ確定の宣言・★Block A 冒頭・analyst-intro は書かない★）
<div class="core-quote">あなたの組織は「[4 型のいずれか]」だ。集まる軸 [◎ or △] × 躍動軸 [◎ or △]</div>

### type-matrix-box（4 型判定図・Block A 主表示・★ 2 マトリクス＋判定根拠 1 行★）
<div class="type-matrix-box">
  <h4>組織の引力タイプ（集まる × 躍動 2 マトリクス）</h4>
  <p class="gi-summary">あなたの組織は「[4 型]」── [集まる × 躍動 のスコア組み合わせ]</p>
  <table class="gi-table">
    <thead>
      <tr>
        <th></th>
        <th>集まる軸 △</th>
        <th>集まる軸 ◎</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>躍動軸 ◎</strong></td>
        <td>[渇望型] 既存活きるが採用詰まり → Gravity Recruit</td>
        <td>[整合型] 両軸機能 → Gravity Orbit 直接</td>
      </tr>
      <tr>
        <td><strong>躍動軸 △</strong></td>
        <td>[不毛型] 両軸停滞 → Recruit + Cultivate 順次（Shift 商談時提案）</td>
        <td>[拡散型] 応募あるが定着せず → Gravity Cultivate</td>
      </tr>
    </tbody>
  </table>
  <p class="gi-rationale"><strong>判定根拠：</strong>[7 項目のうち最も特徴的な 1-2 項目の数値・エピソード]</p>
</div>

### gravity-gap-box（CODE 受講者のみ・個人 × 組織ギャップ図）
<div class="gravity-gap-box">
  <h4>個人引力（CODE） × 組織引力（Scan）のギャップ</h4>
  <p><strong>経営者個人の引力タイプ：</strong>[CODE 4 型：整合 / Why ズレ / 才能ズレ / 偏愛ズレ]</p>
  <p><strong>組織の引力タイプ：</strong>[Scan 4 型：整合 / 拡散 / 渇望 / 不毛]</p>
  <p><strong>ギャップの意味：</strong>[例：個人は整合型なのに組織は渇望型 → 個人引力が採用面接に翻訳されていない構造的原因]</p>
</div>

### pulse-7-table（引力 7 項目スコアリング表・Block B 主表示）
<div class="pulse-7-table">
  <h4>引力 7 項目スコアリング</h4>
  <table class="gi-table">
    <thead>
      <tr>
        <th>#</th>
        <th>項目</th>
        <th>軸</th>
        <th>スコア</th>
        <th>根拠</th>
      </tr>
    </thead>
    <tbody>
      <tr><td>1</td><td>採用パイプライン</td><td>集まる</td><td>[◎/○/△/×]</td><td>[応募数・面接通過率・最終辞退率・内定承諾率]</td></tr>
      <tr><td>2</td><td>最終面接辞退率</td><td>集まる</td><td>[◎/○/△/×]</td><td>[最終面接到達後の辞退連絡数 ÷ 最終面接数]</td></tr>
      <tr><td>3</td><td>優秀人材定着率（過去 2 年）</td><td>躍動</td><td>[◎/○/△/×]</td><td>[優秀人材入社・離脱の数値]</td></tr>
      <tr><td>4</td><td>幹部発話量</td><td>躍動</td><td>[◎/○/△/×]</td><td>[経営会議で幹部発議の有無・頻度]</td></tr>
      <tr><td>5</td><td>エンゲージメント</td><td>躍動</td><td>[◎/○/△/×]</td><td>[サーベイ実施有無・スコア]</td></tr>
      <tr><td>6</td><td>離脱予兆</td><td>躍動</td><td>[◎/○/△/×]</td><td>[直近の離脱者・予兆の有無]</td></tr>
      <tr><td>7</td><td>採用最大壁の自覚度</td><td>集まる</td><td>[◎/○/△/×]</td><td>[経営者が言語化できるペイン 1 個]</td></tr>
    </tbody>
  </table>
</div>

### axis-score-box（集まる軸／躍動軸の合算スコア）
<div class="axis-score-box">
  <p><strong>集まる軸（1, 2, 7）：</strong>[◎/○/△/×] ── [合算根拠 1 行]</p>
  <p><strong>躍動軸（3, 4, 5, 6）：</strong>[◎/○/△/×] ── [合算根拠 1 行]</p>
</div>

### issue（引力欠損ポイント・優先順位付き）

**最優先の引力欠損（厚い・1 個）：**
<div class="issue issue--primary">
  <div class="issue-priority">最優先</div>
  <h3>[項目名]：[なぜ欠損しているか 1 行]</h3>
  <p><strong>現状：</strong>[数値・具体エピソード]</p>
  <p><strong>引力欠損の構造：</strong>[なぜこの項目が低いのか・組織のどこで引力が漏れているのか]</p>
  <p><strong>結果：</strong>[この項目の低さが採用／離脱／躍動にどう波及しているか]</p>
</div>

**副次の引力欠損（薄い・1-2 個）：**
<div class="issue issue--secondary">
  <h3>副次：[項目名]</h3>
  <p>[現状＋構造を 1 段落で簡潔に]</p>
</div>

### shift-fit-box（Shift 適合診断・Block C 主表示・★主成果物★）

<div class="shift-fit-box shift-fit-box--primary">
  <div class="gd-priority">推奨</div>
  <h4>Pre-Shift 適合診断：[Gravity Recruit / Gravity Cultivate / Gravity Cultivate + Coaching 並走 128 万 / Gravity Shift / Gravity Orbit 直接 / Gravity Coaching 先行]</h4>
  <p><strong>推奨理由：</strong>[4 型判定 + 引力欠損ポイント + 経営者の覚悟確信度の 3 軸で 3 行]</p>
  <p><strong>価格・期間：</strong>[Gravity Recruit 80 万・3 ヶ月／Gravity Cultivate 80 万・3 ヶ月／Gravity Cultivate + Coaching 並走パッケージ 128 万・6 ヶ月（拡散型・C-5 中判定限定）／Gravity Shift 150 万・6 ヶ月（R+C 複合・10 万割引）／Gravity Orbit 月 15 万／Gravity Coaching 38 万・6 ヶ月]</p>
</div>

### roadmap-box（3 ヶ月着手ロードマップ・タイプ別書き分け）

<div class="roadmap-box">
  <h4>3 ヶ月着手ロードマップ（[Gravity Recruit / Cultivate / Shift / Orbit 直接 / Coaching 先行] の場合）</h4>
  <p><strong>Week 1-2：</strong>[最初の 2 週間で何を共同制作するか]</p>
  <p><strong>Week 3-6：</strong>[実装と試運用]</p>
  <p><strong>Week 7-12：</strong>[実装定着＋次のステージ移行判断]</p>
</div>

### future-box（3 ヶ月後・3 視点 1 段落）
<div class="future-box">
  <h4>3 ヶ月後、Shift 実装後の組織像</h4>
  <p><strong>集まる軸の変化：</strong>[採用パイプライン・エージェント依存度・最終面接辞退率の数値変化予測]</p>
  <p><strong>躍動軸の変化：</strong>[優秀人材定着率・幹部発話量・離脱予兆の変化予測]</p>
  <p><strong>経営者の変化：</strong>[採用エフィカシー転換／躍動の手応え・タイプ別に書き分け]</p>
</div>

### analyst-note（★石井の一人称 2 箇所目・最大リスク）
<div class="analyst-note">
  <p><strong>最大リスク：</strong>正直に言うと、このタイプ判定を Shift 実装に繋げないままだと、組織の引力は『[4 型]』のまま固定され、[7 項目のうち最低スコア項目] が悪化していく。Scan が示したのは方角だけだ。次の 3 ヶ月で実装するかどうかは、あなた次第だ。</p>
</div>

### path-cards（4 型判定推奨ロジックに従う）
<div class="path-cards">
  <div class="path-card path-card--recommended">
    <span class="path-badge">RECOMMENDED</span>
    <h4>[判定型の推奨サービス名（Gravity Recruit / Cultivate / Shift / Orbit / Coaching）]</h4>
    <p class="path-card-meta">[サービススペック・価格・期間]</p>
    <p>[あなたの場合〜具体理由 2-3 行]</p>
  </div>
  <div class="path-card path-card--small"><strong>[副次選択肢]：</strong>[1 行説明]</div>
  <div class="path-card path-card--small"><strong>セルフリファイン：</strong>このレポートを定期的に見返し、引力 7 項目の数値変化を自己チェックする。</div>
</div>

### final-question（タイプ別書き分け・260505 Cultivate 化反映）
<div class="final-question">
  <div class="final-question-label">最後の問い</div>
  <p class="final-question-text">[4 型に応じた即答不能の問い・Block C コア要素 6 参照]</p>
  <p class="final-question-caveat">この問いに 30 秒で即答できない場合、組織の引力タイプは固定されている可能性があります。</p>
  <a href="[4 型に応じた URL：渇望型→/gravity-recruit/ ／ 拡散型→/gravity-cultivate/ ／ 不毛型→/gravity-shift/ ／ 整合型→/gravity-orbit/]" class="final-question-cta">[推奨パッケージ名] 体験セッション 30 分無料 →</a>
</div>

### closing-note（★石井の一人称 3 箇所目・締め・タイプ別・260505 Cultivate 化反映）
<div class="closing-note">
  <p>私が 50 社診てきて確信したのは、組織の引力タイプは「[4 型]」のままでは絶対に変わらないということだ。</p>
  <p>『[4 型]』だった会社が、[Gravity Recruit / Gravity Cultivate / Gravity Shift のいずれか]で[適合領域]を 3 ヶ月実装した結果、[集まる軸 or 躍動軸] の数値が[具体変化]した。</p>
  <p>あなたの組織にも、同じ道がある。</p>
</div>

### ★ NOTE: report-footer は AI 出力に含めない（260508 v1.2 改修・footer 二重出力解消）
サーバー側で末尾に自動付与されるため、AI レポート出力に `<div class="report-footer">` を含めないこと。closing-note で締めて終了する。

## サービス記載の正確ルール（260505 Cultivate 化・公開向け表記体系）

- **Gravity CODE**：60 分／5 万円（経営者の引力タイプ診断・個人軸）
- **Gravity Scan**：60 分／10 万円（組織の引力タイプ診断・Pre-Shift 適合診断・組織軸・260430 リブート）
- **Gravity Coaching**：90 分 × 月 1 回 × 6 ヶ月（全 6 回）／ 38 万円（税込・Gravity CODE 付き・継続伴走 7 ヶ月目以降 月 5 万）
- **Gravity Recruit**（内的：Shift R）：80 万円／3 ヶ月（採用基盤主軸・渇望型推奨）
- **Gravity Cultivate**（内的：Shift C・260505 Activate から変更）：80 万円／3 ヶ月（躍動組織主軸・拡散型推奨）
- **Gravity Shift**（内的：Shift Full）：150 万円／6 ヶ月（Recruit + Cultivate 複合・10 万割引・不毛型は商談時提案）
- **Gravity Cultivate + Coaching 並走パッケージ**（260501 新規）：128 万円／6 ヶ月（Scan 10 + Cultivate 80 + Coaching 38・C-5 中判定経営者の標準・拡散型限定）
- **Gravity Orbit**：月 15 万円・単一プラン（継続運用・260505 v3.0）

★レポート出力では必ず公開向け表記（Gravity Recruit / Gravity Cultivate / Gravity Shift）を使う。内的呼称（Shift R / C / Full）はレポートに出さない。
★「Blueprint」「採用口説きブループリント」「設計の参謀」「90 日」「3 ヶ月の Coaching」「Shift A」「Activate」等の旧用語・誤記は厳禁。
SYSTEM;

$pre_info_section = '';
if (!empty(trim($pre_info))) {
    $pre_info_section = <<<PRE

## 事前提供情報
以下は2種類の事前情報です。優先順位に注意してください。

**【ファクト情報】**＝正として扱う。業種・従業員数・売上規模・事業数が含まれる場合、トランスクリプトの情報と矛盾してもファクト情報を優先する。
**【事前調査の考察】**＝仮説として参考にする。URLから推定した情報や事前仮説。トランスクリプトの発言と矛盾した場合はトランスクリプトを優先する。

{$pre_info}

PRE;
}

if (!empty($transcript)) {
    $user_prompt = <<<USER
以下の診断データを基に、Gravity Scan「GRAVITY SCAN ── 組織の引力を強める設計図」をHTMLフラグメントで生成してください。

## クライアントの立場
{$role_guidance}

## 事前情報（CODE結果があればここに含まれる）
{$pre_info_section}

## 選択回答
{$choices_text}

## Scan 60 分 3 パート対話のトランスクリプト（★最重要★ クライアント発言のみ分析対象）

以下はコーチ（石井伸幸）と経営者の Scan 60 分対話の文字起こしです（260430 夕 リブート版）。
対話は以下の 3 パート構成：

**PART 1：組織現状ヒアリング（20 分）**
引力 7 項目を過去 2 年の具体エピソード＋数値で深掘り：
1. 採用パイプライン（応募数・面接通過率・最終辞退率・内定承諾率）
2. 最終面接辞退率（最終面接到達後の辞退連絡数 ÷ 最終面接数）
3. 優秀人材定着率（過去 2 年の優秀人材入社・離脱の数値）
4. 幹部発話量（経営会議で幹部発議の有無・頻度）
5. エンゲージメント（サーベイ実施有無・スコア）
6. 離脱予兆（直近の離脱者・予兆の有無）
7. 採用最大壁の自覚度（経営者が言語化できる最大ペイン 1 個）

**PART 2：組織の引力タイプ判定（20 分・最重要）**
集まる軸 × 躍動軸の 2 マトリクスにプロット → 4 型のいずれかに確定（整合／拡散／渇望／不毛）

**PART 3：Pre-Shift 適合ロードマップ（17 分）**
推奨パッケージ（Gravity Recruit／Gravity Cultivate／Gravity Shift）＋ 3 ヶ月着手順序＋経営者の覚悟確認

### ★ v7.0 事前情報の活用（260508 UI 構造ブラッシュアップで追加）

事前情報には以下が含まれる場合がある（Scan 診断 UI の Q1-Q6 から取得）：

- **【CODE結果】**：個人引力 4 型（Block A の gravity-gap-box・個人 × 組織ギャップで使用）
- **【組織規模＋幹部数】**：4 型判定マトリクスの前提情報
- **【採用ペイン主訴】**：6 択の経営者言語マップ（B-1 採用費用増・優秀幹部離脱 etc）
- **【集まる軸 自己診断】**：◎/○/△/× の経営者自己診断（Block A type-matrix-box の集まる軸判定の事前材料・トランスクリプトと矛盾する場合は対話発言を優先）
- **【躍動軸 自己診断】**：◎/○/△/× の経営者自己診断（Block A type-matrix-box の躍動軸判定の事前材料・同上）
- **【過去 2 年の採用・離脱エピソード + 採用コスト対効果】**：3 件のエピソード + 年間採用費／年間昇給原資の倍率（Block B 引力 7 項目スコアリング根拠 + Block C Recruit 推奨時の悪循環判定材料）

★ 集まる軸／躍動軸の自己診断は **経営者の主観的自己評価**。トランスクリプト内の具体エピソード・数値と矛盾する場合は **対話発言を優先**し、Analyst's Note で「事前自己診断は◎だが、対話で出た数値は△」のように明示してよい。

### 抽出すべき要素

1. **PART 1 の 7 項目データ**：各項目の具体エピソード・数値（Block B のスコアリング表に使用）
2. **PART 2 のタイプ判定根拠**：集まる × 躍動 のスコア・4 型確定の決め手（Block A の core-quote と type-matrix-box に使用・**事前自己診断と整合チェック**）
3. **PART 3 の覚悟確信度＋ C-5 ネガティブ・ケイパビリティ**：「やる／決まった／明確」（覚悟高）vs「迷い／自信ない／分からない」（覚悟低）の発言パターン ＋ C-5 質問 2 件への回答パターン（具体エピソード+構造説明=高 ／ 抽象論=中 ／「すぐ決めたい派」=低）。Block C の Pre-Shift 適合診断・推奨理由・final-question 確定に使用
4. **CODE 受講者の場合**：CODE 結果との対比で個人 × 組織ギャップ（Block A の gravity-gap-box に使用）
5. **引力欠損ポイント**：7 項目のうち最低スコア項目とその構造的原因（Block B の issue--primary に使用）
6. **経営者の言葉で語られたペイン**：採用面接辞退・優秀幹部離脱・採用エージェント費用・面接で口説けない感覚 等の具体エピソード
7. **3 ヶ月後の組織像の素材**：経営者がトランスクリプト内で語った理想像・恐れている悪化シナリオ（Block C の future-box に使用）

### トランスクリプト全文
{$freetext_text}

---

生成ルール（260508 v1.5 改修・公開向け表記厳守 + Cover Page 移管 + ページ最適化）：
- **3 ブロック構造**：Block A（4 型判定）→ Block B（7 項目スコアリング）→ Block C（Pre-Shift 適合診断＋ロードマップ）
- **★ v1.5 改修：引力定義は Cover Page（表紙・サーバ側で自動付与）に移管**。AI（あなた）は Cover Page を出力しない。Block A は core-quote から始める。gravity-definition-box は本文に含めない
- **CODE 結果がある場合**：Block A の gravity-gap-box で個人 × 組織ギャップを可視化（個人軸 4 型と組織軸 4 型の対比）。CODE 公開語彙「Why × 才能 × 偏愛」で表記（旧「動詞 3 連鎖」「環境」は内部分析用語のためレポート出力では使わない）
- **CODE 未受講の場合**：gravity-gap-box は省略・組織軸のタイプ判定のみで完結
- **★ 公開向け表記厳守**：推奨パッケージ・CTA・closing-note では「Gravity Recruit / Gravity Cultivate / Gravity Shift」を必ず使う（旧「Shift R / Shift A / Shift Full」は禁止）
- **★ ページ最適化**：Block A は 1 ページ完結（gravity-definition-box + core-quote + type-matrix-box + gravity-gap-box を凝縮）／ Block B は 1 ページ完結（pulse-7-table + axis-score-box + issue--primary + issue--secondary を凝縮）／ Block C は 1 ページ目安（shift-fit-box + roadmap-box + future-box + analyst-note + path-cards + final-question + closing-note）。各 Block 内のサブセクションに過剰な余白を入れない
- **石井の一人称は 2-3 箇所のみ**（必要時のみ・analyst-note／closing-note を中心に）
- 本文は主語なし断定構文
- 出力は **HTML フラグメントのみ**。`<div class="section">`から始めて`</div>`で終わる
- `<style>`・`style=""`・外側 HTML・コードフェンスは**一切書かない**

生成開始：
USER;
} else {
    $user_prompt = <<<USER
以下の診断データを基に、Gravity Scan「GRAVITY SCAN ── 組織の引力を強める設計図」をHTMLフラグメントで生成してください。

## クライアントの立場
{$role_guidance}

## 事前情報（CODE結果があればここに含まれる）
{$pre_info_section}

## 選択回答
{$choices_text}

## 対話記録（★最重要★）
{$freetext_text}

---

生成ルール（260508 v1.5 改修・公開向け表記厳守 + Cover Page 移管 + ページ最適化）：
- 3 ブロック構造（Block A：4 型判定／Block B：7 項目スコアリング／Block C：Pre-Shift 適合診断＋ロードマップ）
- ★ v1.5 改修：引力定義は Cover Page に移管・AI は Cover Page を出力しない・Block A は core-quote から始める
- CODE 結果があれば Block A の gravity-gap-box で個人 × 組織ギャップを可視化（CODE 公開語彙「Why × 才能 × 偏愛」厳守）
- ★ 公開向け表記厳守：「Gravity Recruit / Gravity Cultivate / Gravity Shift」を必ず使う（旧「Shift R / Shift A / Shift Full」は禁止）
- ★ ページ最適化：各 Block 1 ページ完結を目指す
- 石井の一人称は 2-3 箇所のみ（analyst-note／closing-note 中心）
- 本文は主語なし断定構文
- HTML フラグメントのみ出力
USER;
}

// --- ジョブID生成 + 初期ステータス書き込み ---
$job_id = bin2hex(random_bytes(8));
$REPORT_FILE = $reports_dir . '/report_' . $job_id . '.html';
$base_url = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http')
    . '://' . $_SERVER['HTTP_HOST'];
$report_url = $base_url . dirname($_SERVER['REQUEST_URI']) . '/generate.php?report=' . $job_id;

write_status($job_id, [
    'status' => 'pending',
    'created_at' => time(),
]);

// --- 即時レスポンス: ジョブIDを返してから接続を閉じ、バックグラウンド処理へ ---
echo json_encode(['job_id' => $job_id, 'report_url' => $report_url]);

if (function_exists('fastcgi_finish_request')) {
    fastcgi_finish_request();
}
ignore_user_abort(true);
set_time_limit(600);

write_status($job_id, [
    'status' => 'running',
    'created_at' => time(),
]);

// --- Claude API 呼び出し（バックグラウンド実行） ---
$api_body = json_encode([
    'model' => 'claude-sonnet-4-5',
    'max_tokens' => 12000,
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
    CURLOPT_TIMEOUT => 230,
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
    write_status($job_id, [
        'status' => 'error',
        'created_at' => time(),
        'error' => 'API通信エラー: ' . $curl_error,
    ]);
    exit;
}

if ($http_code !== 200) {
    error_log('Claude API error (HTTP ' . $http_code . '): ' . $response);
    write_status($job_id, [
        'status' => 'error',
        'created_at' => time(),
        'error' => 'レポート生成サービスに一時的な問題が発生しています。しばらく後に再試行してください。',
    ]);
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
    write_status($job_id, [
        'status' => 'error',
        'created_at' => time(),
        'error' => 'レポートの生成に失敗しました',
    ]);
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
// 長い文字列から先に置換する（短い文字列が部分的に先にマッチしないように）。
$jargon_map = [
    'C-5 ネガティブ・ケイパビリティ第 1 次判定' => '経営者の覚悟確認',
    'C-5 ネガティブ・ケイパビリティ第 2 次判定' => '経営者の覚悟確認（再判定）',
    'C-5 ネガティブ・ケイパビリティ判定' => '経営者の覚悟確認',
    'C-5 ネガティブ・ケイパビリティ' => '経営者の覚悟（答えのない時間に留まる力）',
    'ネガティブ・ケイパビリティ第 1 次判定' => '経営者の覚悟確認',
    'ネガティブ・ケイパビリティ判定' => '経営者の覚悟確認',
    'ネガティブ・ケイパビリティ' => '答えのない時間に結論を出さず留まる力',
    'C-5 中判定' => '覚悟確信度が中位',
    'C-5 低判定' => '覚悟確信度が低位',
    'C-5 高判定' => '覚悟確信度が高位',
    'C-5 判定' => '経営者の覚悟確認',
    'C-5 第 2 次判定' => '経営者の覚悟確認（再判定）',
    'C-5 第 1 次判定' => '経営者の覚悟確認',
    'C-5' => '経営者の覚悟確認',
    'ドラムビート 4 周期表（Weekly/Monthly/Quarterly/Annual）' => '組織運営のリズム設計（週次／月次／四半期／年次）',
    'ドラムビート 4 周期表' => '組織運営のリズム設計（週次／月次／四半期／年次）',
    'ドラムビート 4 周期' => '組織運営のリズム（週次／月次／四半期／年次）',
    'ドラムビート' => '組織運営のリズム',
    '組織 OS 診断書 6 章' => '躍動土壌の設計図',
    '組織 OS 診断書' => '躍動土壌の設計図',
    '組織 OS 6 章' => '躍動土壌の設計図',
    '組織 OS' => '組織の仕組み',
    '3 ヶ月予言の書（採用基盤）' => '3 ヶ月後の到達ゴール書（採用基盤）',
    '3 ヶ月予言の書（躍動組織）' => '3 ヶ月後の到達ゴール書（躍動組織）',
    '3 ヶ月予言の書 × 2 期' => '3 ヶ月後の到達ゴール書 2 部',
    '3 ヶ月予言の書' => '3 ヶ月後の到達ゴール書',
    '予言の書草稿読み合わせ' => '到達ゴール書 草稿の読み合わせ',
    '予言の書最終採点' => '到達ゴール書の最終採点',
    '予言の書草稿' => '到達ゴール書 草稿',
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
    'B-21 AI ガラス張り診断' => 'AI による組織透明性の診断',
    'B-21 AI ガラス張り' => 'AI による組織透明性',
    'B-22 組織学習障害診断' => '組織が学べていない壁の診断',
    'B-22 学習障害診断' => '組織が学べていない壁の診断',
    'B-22' => '組織が学べていない壁の診断',
    'B-21' => 'AI による組織透明性の診断',
    'B-11 バイネーム熱量分布' => '幹部の熱量分布',
    'B-11 バイネーム熱量' => '幹部の熱量分布',
    'B-11' => '幹部の熱量分布',
    'B-10 ペイン・プレジャー・マトリクス' => '組織の喜びと痛みのマップ',
    'B-10 ペイン・プレジャー' => '組織の喜びと痛みのマップ',
    'B-10' => '組織の喜びと痛みのマップ',
    'B-1 文化 3 層構造' => '組織文化の現在地',
    'B-1 文化 3 層' => '組織文化の現在地',
    'B-1' => '組織文化の現在地',
    'B-2 8 類型カルチャーマップ' => '組織文化のタイプマップ',
    'B-2 8 類型' => '組織文化のタイプマップ',
    'B-2' => '組織文化のタイプマップ',
    '8 類型カルチャーマップ' => '組織文化のタイプマップ',
    'バイネーム熱量分布' => '幹部の熱量分布',
    'ペイン・プレジャー・マトリクス' => '組織の喜びと痛みのマップ',
    '文化 3 層構造' => '組織文化の現在地',
    '4 壁モデル' => '組織が学べていない壁の分析',
    'タスクアセスメント三角形' => '業務難易度の三角形分析',
    'タスクアセスメント' => '業務難易度の分析',
    'リスニングコンパス' => '応募者の声の構造化',
    'インタビュー 5 原則' => '面接の原則',
    'AI 時代の育成型採用論' => '優秀人材を育てる採用思想',
    '期待値ギャップ事前握り' => '入社前の期待値合わせ',
    '期待値ギャップの事前握り' => '入社前の期待値合わせ',
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
    'ハーネス層' => 'ルールの徹底化',
    'ハーネス' => 'ルール',
    'TDD 経営原則' => '',
    'TDD 経営' => '',
    'RECODE C-2' => '',
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
    '4 型' => '4 つのタイプ',
    'スパーリング' => '対話',
    'Shift R／Shift A／Shift Full' => 'Gravity Recruit／Gravity Cultivate／Gravity Shift',
    'Shift R/Shift A/Shift Full' => 'Gravity Recruit/Gravity Cultivate/Gravity Shift',
    'Shift R + A 複合' => 'R+C 複合',
    'Shift A' => 'Gravity Cultivate',
    'Shift R' => 'Gravity Recruit',
];

// 長い文字列から先に置換（部分一致による誤置換を防ぐ）
uksort($jargon_map, function($a, $b) { return strlen($b) - strlen($a); });
foreach ($jargon_map as $ng => $ok) {
    if ($ng !== '' && strpos($report_body, $ng) !== false) {
        $report_body = str_replace($ng, $ok, $report_body);
    }
}

// 連続する「、」「  」「 　」「（）」など空文字置換で発生したゴミを掃除
$report_body = preg_replace('/、(\s*、)+/u', '、', $report_body);
$report_body = preg_replace('/（\s*）/u', '', $report_body);
$report_body = preg_replace('/  +/u', ' ', $report_body);

// --- ★ 期間表現の冗長重複除去（260508 追加・置換結果の二段冗長を圧縮）---
// 例：「3 ヶ月予言の書」→「3 ヶ月後の到達ゴール書」置換時に、元文に前置き「3ヶ月」がある場合「3ヶ月3 ヶ月後の到達ゴール書」になる現象に対応
// 「N ヶ月 N ヶ月」のパターン（半角空白・全角空白あり/なし両対応）を「N ヶ月」1 つに圧縮
$report_body = preg_replace('/(\d+)\s*ヶ月\s*\1\s*ヶ月/u', '$1 ヶ月', $report_body);
// 「3 ヶ月後の N ヶ月後」のような重複は最初を残す
$report_body = preg_replace('/(\d+\s*ヶ月後の)(\s*\d+\s*ヶ月後の)/u', '$1', $report_body);

// --- divタグの自動修復 ---
$open_divs = preg_match_all('/<div[\s>]/i', $report_body);
$close_divs = preg_match_all('/<\/div>/i', $report_body);
$missing = $open_divs - $close_divs;
if ($missing > 0) {
    $report_body .= str_repeat('</div>', $missing);
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
<title>GRAVITY SCAN｜組織の引力の解剖</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%230f172a'/><text x='16' y='22' text-anchor='middle' font-size='18' font-family='serif' fill='%23fff'>G</text></svg>">
<meta name="robots" content="noindex, nofollow">
<style>
  @page { size: A4; margin: 20mm 18mm 24mm 18mm; }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { background: #e8e8e8; }

  /* v1.5（260508）：Cover Page ── WP V9 風ダークモード（CODE 同型・SCAN カスタマイズ） */
  .cover-page { background: #0f172a; color: #fff; padding: 56px 48px 40px; position: relative; overflow: hidden; page-break-after: always; box-sizing: border-box; min-height: 100vh; }
  .cover-page::before { content: ''; position: absolute; top: -60px; right: -60px; width: 280px; height: 280px; border: 36px solid rgba(71, 85, 105, 0.3); border-radius: 50%; pointer-events: none; }
  .cover-page::after { content: ''; position: absolute; bottom: -100px; left: -100px; width: 200px; height: 200px; border: 22px solid rgba(197, 168, 128, 0.12); border-radius: 50%; pointer-events: none; }
  .cover-inner { position: relative; z-index: 1; max-width: 600px; margin: 0 auto; padding-top: 16px; }
  .cover-badge { display: inline-block; font-size: 9pt; font-weight: 700; letter-spacing: 0.3em; color: #94a3b8; border: 1px solid #334155; padding: 5px 14px; border-radius: 2px; margin-bottom: 28px; text-transform: uppercase; }
  .cover-main-title { font-size: 48pt; font-weight: 900; line-height: 1.05; color: #fff; border-left: 6px solid #C5A880; padding: 0 0 0 24px; margin: 0 0 28px; letter-spacing: 0.02em; border-bottom: none; }
  .cover-divider { width: 72px; height: 3px; background: #C5A880; margin: 0 0 36px 24px; }
  .cover-gravity-def { background: rgba(255, 255, 255, 0.04); padding: 24px 28px; border-radius: 4px; border-left: 3px solid #C5A880; margin-bottom: 28px; }
  .cover-gravity-label { font-size: 10pt; font-weight: 700; letter-spacing: 0.2em; color: #C5A880; margin-bottom: 14px; text-transform: uppercase; }
  .cover-gravity-body { font-size: 11pt; line-height: 1.85; color: #d7dde6; margin: 0 0 18px; }
  .cover-gravity-body strong { color: #fff; font-weight: 800; }
  .cover-gravity-duality { display: flex; flex-direction: column; gap: 6px; margin: 14px 0 18px; padding: 14px 0; border-top: 1px solid rgba(255, 255, 255, 0.08); border-bottom: 1px solid rgba(255, 255, 255, 0.08); }
  .cover-gravity-positive, .cover-gravity-negative { display: flex; align-items: center; gap: 12px; font-size: 10pt; line-height: 1.5; color: #d7dde6; padding: 4px 0; }
  .cgd-tag { display: inline-block; min-width: 68px; padding: 3px 8px; font-size: 8.5pt; font-weight: 800; letter-spacing: 0.05em; border-radius: 2px; text-align: center; }
  .cover-gravity-positive .cgd-tag { background: rgba(197, 168, 128, 0.18); color: #C5A880; }
  .cover-gravity-negative .cgd-tag { background: rgba(220, 38, 38, 0.18); color: #fca5a5; }
  .cgd-arrow { color: #64748b; font-weight: 700; }
  .cgd-text { flex: 1; }
  .cover-gravity-claim { font-size: 12pt; font-weight: 700; color: #fff; margin: 0; padding-top: 8px; line-height: 1.6; letter-spacing: 0.02em; }
  .cover-meta { font-size: 9pt; color: #94a3b8; letter-spacing: 0.15em; padding-top: 32px; border-top: 1px solid #1e293b; }
  .cover-meta strong { color: #fff; font-weight: 700; letter-spacing: 0.2em; }
  .cm-divider { margin: 0 8px; color: #475569; }

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
  /* 勝ち筋ループ図 — ループ感を視覚化 */
  .loop-chain { background: #f8fafc; border-radius: 16px; padding: 24px 20px 16px; margin: 20px 0 28px; text-align: center; page-break-inside: avoid; }
  .loop-chain-label { display: inline-block; background: #0f172a; color: #fff; font-size: 9pt; font-weight: 800; letter-spacing: 0.15em; padding: 4px 16px; border-radius: 100px; margin-bottom: 16px; }
  .loop-chain-circle { position: relative; width: 100%; max-width: 520px; margin: 0 auto; aspect-ratio: 1; }
  .loop-chain-arrows { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; }
  .loop-chain-center { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #0f172a; color: #fff; font-size: 9pt; font-weight: 700; padding: 16px; border-radius: 50%; width: 100px; height: 100px; display: flex; align-items: center; justify-content: center; text-align: center; line-height: 1.5; z-index: 2; }
  .loop-chain-node { position: absolute; background: #0f172a; color: #fff; padding: 8px 14px; border-radius: 8px; width: 180px; text-align: center; z-index: 2; }
  .loop-chain-node-title { font-size: 9pt; font-weight: 800; margin-bottom: 1px; letter-spacing: 0.02em; line-height: 1.3; white-space: nowrap; }
  .loop-chain-node-detail { font-size: 7pt; color: #94a3b8; line-height: 1.3; }
  .loop-chain-top { top: 8%; left: 50%; transform: translateX(-50%); }
  .loop-chain-right { top: 50%; right: 2%; transform: translateY(-50%); }
  .loop-chain-bottom { bottom: 8%; left: 50%; transform: translateX(-50%); }
  .loop-chain-left { top: 50%; left: 2%; transform: translateY(-50%); }
  .loop-chain-ceo { margin-top: 16px; font-size: 9.5pt; font-weight: 600; color: #dc2626; letter-spacing: 0.02em; }
  @media screen and (max-width: 500px) {
    .loop-chain-circle { max-width: 320px; }
    .loop-chain-node { min-width: 100px; max-width: 120px; padding: 8px 10px; }
    .loop-chain-node-title { font-size: 8.5pt; }
    .loop-chain-node-detail { font-size: 7pt; }
    .loop-chain-center { width: 80px; height: 80px; font-size: 8pt; padding: 12px; }
  }
  .numbered-list { counter-reset: nlist; list-style: none; padding: 0; margin: 12px 0 24px; }
  .numbered-list li { counter-increment: nlist; position: relative; padding-left: 32px; margin-bottom: 14px; font-size: 10pt; line-height: 1.8; }
  .numbered-list li::before { content: counter(nlist); position: absolute; left: 0; top: 2px; width: 22px; height: 22px; background: #0f172a; color: #fff; border-radius: 50%; font-size: 9pt; font-weight: 700; display: flex; align-items: center; justify-content: center; }
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
  .haveto-card { background: #fef2f2; border-left: 3px solid #dc2626; border-radius: 0 8px 8px 0; padding: 16px 20px; margin: 12px 0; page-break-inside: avoid; }
  .haveto-tag { font-size: 9pt; font-weight: 800; letter-spacing: 0.08em; color: #dc2626; text-transform: uppercase; margin-bottom: 4px; }
  .haveto-card p { font-size: 10pt; line-height: 1.8; color: #334155; }
  /* 構造的課題カード */
  .issue { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px 28px; margin: 16px 0; page-break-inside: avoid; border-left: 4px solid #0f172a; }
  .issue h3 { font-size: 12pt; font-weight: 800; color: #0f172a; margin: 0 0 16px; padding: 0; border: none; }
  .issue p { font-size: 10pt; line-height: 1.8; margin: 0 0 12px; }
  .issue p:last-child { margin-bottom: 0; }
  .issue strong { color: #0f172a; }
  /* アクションリスト */
  .actions { margin: 16px 0; }
  .actions h3 { font-size: 11pt; }
  .actions ol, .actions ul { padding-left: 20px; }
  .actions li { font-size: 10pt; line-height: 1.8; margin-bottom: 8px; }
  /* 次のステップ */
  .next-intro { font-size: 10.5pt; line-height: 1.9; color: #475569; margin-bottom: 20px; }
  .next-steps { display: flex; flex-direction: column; gap: 12px; margin: 16px 0 24px; }
  .step-card { padding: 18px 22px; border: 1px solid #e2e8f0; border-radius: 8px; page-break-inside: avoid; }
  .step-card h4 { font-size: 11pt; font-weight: 700; color: #0f172a; margin: 0 0 6px; }
  .step-card p { font-size: 9.5pt; color: #64748b; line-height: 1.7; }
  .step-card--recommended { border-color: #0f172a; background: rgba(15,23,42,0.02); }
  .scenario-box { border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px 20px; margin: 12px 0; page-break-inside: avoid; }
  .scenario-box h4 { margin: 0 0 10px; text-transform: none; }
  .scenario-box ul { list-style: disc; padding-left: 20px; }
  .scenario-box li { font-size: 10pt; line-height: 1.8; margin-bottom: 4px; }
  .manual-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 16px 0 24px; }
  .manual-col { padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; }
  .manual-do { background: rgba(15,23,42,0.02); }
  .manual-dont { background: rgba(220,38,38,0.02); }
  .manual-col h4 { margin: 0 0 12px; text-transform: none; }
  .path-cards { display: flex; flex-direction: column; gap: 12px; margin: 16px 0 24px; }
  .path-card { padding: 18px 22px; border: 1px solid #e2e8f0; border-radius: 8px; page-break-inside: avoid; position: relative; }
  .path-card--recommended { border-color: #0f172a; background: rgba(15,23,42,0.02); }
  .path-badge { position: absolute; top: 14px; right: 14px; font-size: 8pt; font-weight: 800; letter-spacing: 0.08em; padding: 3px 10px; background: #0f172a; color: #fff; border-radius: 4px; }
  .path-card h4 { margin: 0 0 6px; font-size: 11pt; text-transform: none; color: #0f172a; }
  .path-card p { font-size: 9.5pt; color: #64748b; line-height: 1.7; }
  /* 3つの箱（パーフェクトな意思決定） */
  .dbox { margin: 20px 0; page-break-inside: avoid; }
  .dbox-h { color: #fff; padding: 12px 18px; border-radius: 8px 8px 0 0; font-weight: 700; font-size: 11pt; }
  .dbox-imm .dbox-h { background: #0f172a; }
  .dbox-info .dbox-h { background: #475569; }
  .dbox-deadline .dbox-h { background: #94a3b8; }
  .dbox-b { background: #f8fafc; padding: 16px 20px; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 8px 8px; }
  .dbox-b > p { font-size: 10pt; line-height: 1.7; margin: 0 0 10px; color: #475569; }
  .dbox-b ul { margin: 0; padding-left: 20px; }
  .dbox-b li { font-size: 10pt; line-height: 1.8; margin-bottom: 8px; }
  .dbox-kpi { color: #64748b; font-size: 9pt; }
  .analyst-note { background: #f8fafc; border-radius: 8px; padding: 24px 28px; margin: 28px 0; font-size: 10pt; font-style: italic; line-height: 1.9; color: #475569; page-break-inside: avoid; }
  .analyst-note strong { color: #0f172a; font-style: normal; }
  /* v5.3 Scan：翻訳マップ（表）・優先順位付きissue・設計図 */
  .analyst-intro { background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%); border-left: 4px solid #0f172a; padding: 22px 26px; margin: 0 0 28px; font-style: italic; color: #334155; }
  .analyst-intro p { margin: 0; font-size: 11pt; line-height: 1.8; }
  .gravity-map-box { background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border: 2px solid #f59e0b; border-radius: 12px; padding: 24px 28px; margin: 24px 0; page-break-inside: avoid; }
  .gravity-map-box h4 { color: #78350f; font-size: 12pt; margin: 0 0 16px; text-align: center; letter-spacing: 0.04em; }
  .gravity-map-box > p { font-size: 10.5pt; line-height: 1.9; color: #78350f; margin: 0 0 12px; padding: 10px 14px; background: #fff; border-radius: 6px; }
  .gravity-map-box > p:last-child { margin-bottom: 0; }
  .gravity-map-box strong { color: #92400e; }
  .gi-summary { font-size: 13pt !important; font-weight: 700; color: #78350f; padding: 16px 20px !important; background: #fff; border-left: 4px solid #f59e0b !important; border-radius: 6px; margin: 0 0 20px !important; line-height: 1.7; }
  /* v1.1（260508）：テーブルの縦書き化を防ぐため table-layout: fixed + 明示的な width 配分 */
  .gi-table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; margin: 0; table-layout: fixed; word-wrap: break-word; }
  .gi-table thead { background: #fef3c7; }
  .gi-table th { padding: 10px 12px; font-size: 9.5pt; font-weight: 800; color: #78350f; text-align: left; letter-spacing: 0.04em; vertical-align: middle; }
  .gi-table td { padding: 12px; font-size: 9.5pt; line-height: 1.6; color: #334155; border-top: 1px solid #fde68a; vertical-align: top; background: #fff; word-break: normal; overflow-wrap: anywhere; }
  /* type-matrix-box の 4 象限テーブル：3 列・第 1 列ヘッダー + 第 2 列 △ + 第 3 列 ◎ */
  .type-matrix-box .gi-table th:nth-child(1) { width: 18%; }
  .type-matrix-box .gi-table th:nth-child(2),
  .type-matrix-box .gi-table th:nth-child(3) { width: 41%; text-align: center; }
  .type-matrix-box .gi-table td:nth-child(1) { width: 18%; font-weight: 700; vertical-align: middle; }
  .type-matrix-box .gi-table td:nth-child(2),
  .type-matrix-box .gi-table td:nth-child(3) { width: 41%; vertical-align: middle; line-height: 1.5; }
  /* pulse-7-table の 5 列：# / 項目 / 軸 / スコア / 根拠 */
  .pulse-7-table .gi-table th:nth-child(1) { width: 5%; }
  .pulse-7-table .gi-table th:nth-child(2) { width: 18%; }
  .pulse-7-table .gi-table th:nth-child(3) { width: 8%; text-align: center; }
  .pulse-7-table .gi-table th:nth-child(4) { width: 9%; text-align: center; }
  .pulse-7-table .gi-table th:nth-child(5) { width: 60%; }
  .pulse-7-table .gi-table td:nth-child(1) { width: 5%; text-align: center; font-weight: 700; }
  .pulse-7-table .gi-table td:nth-child(2) { width: 18%; font-weight: 700; color: #92400e; }
  .pulse-7-table .gi-table td:nth-child(3) { width: 8%; text-align: center; }
  .pulse-7-table .gi-table td:nth-child(4) { width: 9%; text-align: center; font-size: 14pt; font-weight: 700; color: #f59e0b; }
  .pulse-7-table .gi-table td:nth-child(5) { width: 60%; }
  .gi-table td strong { color: #92400e; font-size: 9pt; letter-spacing: 0.04em; display: block; margin-bottom: 4px; }
  /* v1.3（260508）：「組織の引力とは」定義ボックス（Block A 最初・余白圧縮版・v1.2 から保持） */
  .gravity-definition-box { background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border: 2px solid #0284c7; border-radius: 10px; padding: 14px 20px; margin: 0 0 14px; page-break-inside: avoid; }
  .gravity-definition-box h4 { color: #075985; font-size: 10.5pt; margin: 0 0 8px; text-align: center; letter-spacing: 0.06em; font-weight: 800; }
  .gravity-definition-box p { font-size: 9pt; line-height: 1.65; color: #0c4a6e; margin: 0 0 6px; }
  .gravity-definition-box p:last-child { margin-bottom: 0; }
  .gravity-definition-box strong { color: #075985; font-weight: 800; }
  /* v1.3（260508）：v1.2 の core-quote / type-matrix-box / gravity-gap-box / gi-summary / gi-rationale 圧縮は撤回（Block B 退行を解消・v1.1 のスタイルに復帰） */
  /* v1.5（260508）：Block A 1P 集約のため type-matrix-box と gravity-gap-box にスコープ限定でピンポイント圧縮（他セクションには影響させない） */
  /* v1.5 強化：gravity-gap-box の文字サイズ・行間をさらに圧縮し、core-quote + type-matrix-box + gravity-gap-box を Page 1 集約 */
  .type-matrix-box { padding: 12px 18px !important; margin: 10px 0 !important; }
  .type-matrix-box h4 { font-size: 10pt !important; margin: 0 0 8px !important; }
  .type-matrix-box .gi-summary { font-size: 10pt !important; padding: 8px 12px !important; margin: 0 0 10px !important; line-height: 1.5 !important; }
  .type-matrix-box .gi-rationale { font-size: 9pt !important; padding: 8px 12px !important; margin-top: 8px !important; line-height: 1.5 !important; }
  .type-matrix-box .gi-table th { padding: 7px 10px !important; font-size: 9pt !important; }
  .type-matrix-box .gi-table td { padding: 7px 10px !important; font-size: 9pt !important; line-height: 1.45 !important; }
  .gravity-gap-box { padding: 12px 18px !important; margin: 10px 0 !important; }
  .gravity-gap-box h4 { font-size: 10pt !important; margin: 0 0 8px !important; }
  .gravity-gap-box > p { padding: 6px 10px !important; margin: 0 0 5px !important; font-size: 8.5pt !important; line-height: 1.5 !important; }
  /* v1.5：core-quote も Block A の集約のため軽圧縮 */
  .section:first-of-type .core-quote { padding: 10px 16px !important; margin: 8px 0 10px !important; font-size: 10.5pt !important; line-height: 1.65 !important; }
  /* issue 優先順位付き */
  .issue { background: #fff; border-left: 3px solid #cbd5e1; border-radius: 0 8px 8px 0; padding: 18px 22px; margin: 14px 0; page-break-inside: avoid; position: relative; }
  .issue h3 { margin: 0 0 12px; font-size: 11pt; color: #0f172a; padding: 0; border: none; }
  .issue p { margin: 0 0 8px; font-size: 10pt; line-height: 1.8; color: #334155; }
  .issue p:last-child { margin-bottom: 0; }
  .issue strong { color: #0f172a; }
  .issue--primary { border-left-width: 5px; border-left-color: #dc2626; background: #fef2f2; padding-top: 32px; }
  .issue--secondary { background: #f8fafc; padding: 14px 18px; }
  .issue--secondary h3 { font-size: 10.5pt; color: #475569; margin-bottom: 8px; }
  .issue--secondary p { font-size: 9.5pt; }
  .issue-priority { position: absolute; top: 10px; left: 22px; font-size: 8pt; font-weight: 800; letter-spacing: 0.1em; padding: 3px 10px; background: #dc2626; color: #fff; border-radius: 4px; text-transform: uppercase; }
  /* gravity-design-box 優先順位付き */
  .gravity-design-box { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 24px; margin: 14px 0; page-break-inside: avoid; }
  .gravity-design-box h4 { font-size: 11pt; margin: 0 0 12px; color: #0f172a; }
  .gravity-design-box p { margin: 0 0 8px; font-size: 10pt; line-height: 1.8; color: #334155; }
  .gravity-design-box strong { color: #0f172a; }
  .gravity-design-box--primary { background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border: 2px solid #f59e0b; padding-top: 36px; position: relative; }
  .gravity-design-box--primary h4 { color: #78350f; font-size: 12pt; }
  .gravity-design-box--primary p { color: #78350f; }
  .gravity-design-box--primary strong { color: #92400e; }
  .gravity-design-box--secondary { background: #f8fafc; padding: 14px 20px; }
  .gravity-design-box--secondary h4 { color: #475569; font-size: 10.5pt; margin: 0 0 8px; }
  .gravity-design-box--secondary p { font-size: 9.5pt; line-height: 1.7; color: #475569; }
  .gd-priority { position: absolute; top: 12px; left: 24px; font-size: 8pt; font-weight: 800; letter-spacing: 0.1em; padding: 3px 10px; background: #f59e0b; color: #fff; border-radius: 4px; text-transform: uppercase; }
  /* Scan v6.1（260501 Scan リブート版）: 新クラス名エイリアス */
  .type-matrix-box, .pulse-7-table, .axis-score-box, .gravity-gap-box { background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border: 2px solid #f59e0b; border-radius: 12px; padding: 24px 28px; margin: 24px 0; page-break-inside: avoid; }
  .type-matrix-box h4, .pulse-7-table h4, .axis-score-box h4, .gravity-gap-box h4 { color: #78350f; font-size: 12pt; margin: 0 0 16px; text-align: center; letter-spacing: 0.04em; }
  .type-matrix-box > p, .pulse-7-table > p, .axis-score-box > p, .gravity-gap-box > p { font-size: 10.5pt; line-height: 1.9; color: #78350f; margin: 0 0 12px; padding: 10px 14px; background: #fff; border-radius: 6px; }
  .type-matrix-box > p:last-child, .pulse-7-table > p:last-child, .axis-score-box > p:last-child, .gravity-gap-box > p:last-child { margin-bottom: 0; }
  .type-matrix-box strong, .pulse-7-table strong, .axis-score-box strong, .gravity-gap-box strong { color: #92400e; }
  .gi-rationale { font-size: 10pt !important; color: #78350f; padding: 10px 14px !important; background: #fff !important; border-radius: 6px; margin-top: 16px !important; line-height: 1.7; }
  .axis-score-box { background: #fffbeb; border: 1px solid #f59e0b; padding: 18px 24px; }
  .axis-score-box p { background: transparent; padding: 6px 0; font-weight: 600; }
  .gravity-gap-box { background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%); border: 2px solid #0f172a; }
  .gravity-gap-box h4 { color: #0f172a; }
  .gravity-gap-box > p { color: #334155; }
  .gravity-gap-box strong { color: #0f172a; }
  .shift-fit-box { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 24px; margin: 14px 0; page-break-inside: avoid; }
  .shift-fit-box h4 { font-size: 11pt; margin: 0 0 12px; color: #0f172a; }
  .shift-fit-box p { margin: 0 0 8px; font-size: 10pt; line-height: 1.8; color: #334155; }
  .shift-fit-box strong { color: #0f172a; }
  .shift-fit-box--primary { background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); border: 2px solid #f59e0b; padding-top: 36px; position: relative; }
  .shift-fit-box--primary h4 { color: #78350f; font-size: 12pt; }
  .shift-fit-box--primary p { color: #78350f; }
  .shift-fit-box--primary strong { color: #92400e; }
  .priority-action-box { background: linear-gradient(135deg, #f0f9ff 0%, #dbeafe 100%); border: 2px solid #1e40af; border-radius: 12px; padding: 22px 26px; margin: 18px 0 22px; page-break-inside: avoid; }
  .priority-action-box h3 { font-size: 12pt; margin: 0 0 10px; color: #1e3a8a; border: none; padding: 0; }
  .priority-action-box .priority-intro { margin: 0 0 16px; font-size: 9.5pt; line-height: 1.75; color: #1e40af; }
  .priority-action-box .priority-list { list-style: none; padding: 0; margin: 0; counter-reset: priority-counter; }
  .priority-action-box .priority-item { background: #fff; border-radius: 8px; padding: 14px 18px; margin: 0 0 10px; border-left: 4px solid #93c5fd; }
  .priority-action-box .priority-item--top { border-left-color: #1e40af; background: #fff; box-shadow: 0 2px 8px rgba(30, 64, 175, 0.08); }
  .priority-action-box .priority-rank { display: inline-block; background: #1e40af; color: #fff; font-size: 8.5pt; font-weight: 700; letter-spacing: 0.08em; padding: 2px 10px; border-radius: 100px; margin: 0 0 8px; }
  .priority-action-box .priority-item--top .priority-rank { background: #1e3a8a; }
  .priority-action-box .priority-item:not(.priority-item--top) .priority-rank { background: #64748b; }
  .priority-action-box .priority-name { font-size: 11pt; font-weight: 800; color: #0f172a; margin: 0 0 6px; line-height: 1.5; }
  .priority-action-box .priority-detail { font-size: 9.5pt; line-height: 1.75; color: #334155; margin: 0 0 6px; padding: 0; background: transparent; border: none; }
  .priority-action-box .priority-rationale { font-size: 9pt; line-height: 1.7; color: #64748b; margin: 0; padding: 0; background: transparent; border: none; font-style: italic; }
  .priority-action-box .priority-rationale strong { color: #1e40af; font-style: normal; }
  .priority-action-box .priority-note { font-size: 8.5pt; color: #475569; margin: 12px 0 0; padding-top: 10px; border-top: 1px dashed #93c5fd; line-height: 1.6; }
  .theory-background-box { background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px 22px; margin: 24px 0 16px; page-break-inside: avoid; }
  .theory-background-box h4 { font-size: 10.5pt; margin: 0 0 8px; color: #475569; font-weight: 700; }
  .theory-background-box .theory-intro { margin: 0 0 10px; font-size: 9pt; line-height: 1.7; color: #64748b; }
  .theory-background-box .theory-list { list-style: disc; padding-left: 18px; margin: 0 0 8px; }
  .theory-background-box .theory-list li { font-size: 9pt; line-height: 1.65; color: #475569; margin: 0 0 4px; }
  .theory-background-box .theory-list strong { color: #334155; font-weight: 700; }
  .theory-background-box .theory-note { font-size: 8pt; color: #94a3b8; margin: 8px 0 0; padding-top: 6px; border-top: 1px dashed #e2e8f0; line-height: 1.55; }
  .roadmap-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px 24px; margin: 14px 0; page-break-inside: avoid; }
  .roadmap-box h4 { font-size: 11pt; margin: 0 0 12px; color: #0f172a; }
  .roadmap-box p { margin: 0 0 10px; font-size: 10pt; line-height: 1.8; color: #334155; padding: 8px 12px; background: #fff; border-left: 3px solid #f59e0b; border-radius: 4px; }
  .roadmap-box strong { color: #92400e; }
  .path-card-meta { font-size: 9.5pt; color: #64748b; margin: 0 0 10px !important; letter-spacing: 0.02em; font-weight: 600; }
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
    .filter-grid, .manual-grid { grid-template-columns: 1fr; gap: 12px; }
    .path-cards { gap: 10px; }
    .analyst-note { padding: 18px 20px; }
    .issue { padding: 18px 20px; }
    .step-card { padding: 14px 18px; }
    .pdf-btn { bottom: 16px; right: 16px; padding: 10px 20px; font-size: 13px; }
  }
  @media screen and (min-width: 801px) {
    body { max-width: 760px; }
  }
  @media print {
    body { font-size: 10pt; visibility: visible !important; max-width: none; box-shadow: none; margin: 0; }
    .page { padding: 0; }
    .pdf-btn { display: none; }
    .filter-grid, .manual-grid { break-inside: avoid; }
    .haveto-card, .path-card, .scenario-box { break-inside: avoid; }
  }
</style>
</head>
<body>
<button class="pdf-btn" onclick="window.print()">
  <svg viewBox="0 0 24 24"><path d="M19 8h-1V3H6v5H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zM8 5h8v3H8V5zm8 14H8v-4h8v4zm2-4v-2H6v2H4v-4c0-.55.45-1 1-1h14c.55 0 1 .45 1 1v4h-2z"/></svg>
  PDF保存
</button>
<div class="cover-page">
  <div class="cover-inner">
    <div class="cover-badge">PRE-SHIFT GRAVITY ANALYSIS REPORT</div>
    <h1 class="cover-main-title">YOUR<br>GRAVITY<br>SCAN</h1>
    <div class="cover-divider"></div>

    <div class="cover-gravity-def">
      <div class="cover-gravity-label">ここで言う「組織の引力」とは</div>
      <p class="cover-gravity-body">人が離れない・自発的に集まり躍動する「場の力」。<br>経営者個人の引力（CODE = <strong>Why × 才能 × 偏愛</strong>）が、組織への翻訳を経て立ち上がる。</p>
      <div class="cover-gravity-duality">
        <div class="cover-gravity-positive"><span class="cgd-tag">整合型</span><span class="cgd-arrow">→</span><span class="cgd-text">集まる軸 ◎ × 躍動軸 ◎（採用と組織が両軸で機能）</span></div>
        <div class="cover-gravity-negative"><span class="cgd-tag">3 ズレ型</span><span class="cgd-arrow">→</span><span class="cgd-text">拡散・渇望・不毛（採用しても定着しない／優秀層離脱／両軸停滞）</span></div>
      </div>
      <p class="cover-gravity-claim">事業の天井は、組織の引力の天井である。</p>
    </div>

    <div class="cover-meta"><strong>Gravity Scan</strong><span class="cm-divider">／</span>Pre-Shift 適合診断<span class="cm-divider">／</span>GrowthFix</div>
  </div>
</div>
<div class="page">
{$report_body}
</div>
<div class="report-footer">
  <p><strong>GRAVITY SCAN</strong> — 組織の引力の解剖</p>
</div>
</body>
</html>
HTML;

// レポートをファイルに保存
file_put_contents($REPORT_FILE, $report_html);

// ジョブ完了ステータスを書き込む
write_status($job_id, [
    'status' => 'done',
    'created_at' => time(),
    'report_url' => $report_url,
]);
