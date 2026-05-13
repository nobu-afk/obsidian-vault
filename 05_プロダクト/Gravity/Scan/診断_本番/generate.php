<?php
/**
 * Gravity Scan 診断 — レポート生成API (v2: bootstrap分離版)
 * Claude APIを呼び出して「伸びしろレポート」を生成する
 *
 * [変更点] CORS/ヘッダー/設定/ジョブヘルパー/GETハンドラー/POSTチェック を
 *   diagnose-bootstrap.php に集約。本ファイルは Scan 固有処理のみ保持。
 * [本番置換前] generate_v2.php として並走確認後、generate.php にリネーム。
 *
 * config_file パス: __DIR__/../../config.php（Scan は GravityScan/config.php）
 */

// --- bootstrap 読み込み ---
$DIAGNOSE_CONFIG_PATH = __DIR__ . '/../config.php';
$DIAGNOSE_BASE_DIR    = __DIR__;
require_once __DIR__ . '/../../_共通/diagnose-bootstrap.php';

// bootstrap 完了後：$input, $reports_dir が利用可能
// Scan は非同期ジョブ方式: report_id / REPORT_FILE は POST 受付後に初期化
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

$role_guidance = 'クライアントは経営者（CEO・創業者）です。このレポートは60分のScan対面セッション（組織の引力タイプ診断＋ Pre-Shift 適合診断）での対話から「Gravity Scan レポート」を生成します。組織情報（採用パイプライン・最終面接辞退率・優秀人材定着率・幹部発話量・エンゲージメント・離脱予兆・採用最大壁の自覚度＋ PO Fit 認識・心理的安全性 4 行動＋採用コスト対効果の 8 項目）と CODE 結果（受講者のみ・経営者の引力タイプ）を起点に、組織の引力タイプを 4 型（整合型／拡散型／渇望型／不毛型）で判定し、Gravity Recruit／Gravity Cultivate／Gravity Shift のどれが効くかを示してください。Scan は採用 4 軸の翻訳ではなく、「組織の引力タイプ診断＋ Pre-Shift 適合判定」のレポートです。経営者が Recruit/Cultivate（各 80 万）または Shift（150 万・複合）に進む前の判断装置として機能させてください。\n\n★公開語彙（B 案二層命名・厳守）：\n- レポート出力は必ず外的呼称「Gravity Recruit／Gravity Cultivate／Gravity Shift」で表記（旧表記「Shift R／Shift A／Shift Full」は禁止）\n- 内的呼称（Shift R／Shift C／Shift Full）は内部分析用語として残してよいが、見出し・推奨パッケージ名・CTA・closing-note では公開語彙のみ使う\n- 価格：Gravity Recruit 80 万・3 ヶ月 ／ Gravity Cultivate 150 万・6 ヶ月 ／ Gravity Shift 220 万・9 ヶ月（R+C 複合・10 万割引）／ Gravity Coaching 38 万・6 ヶ月（覚悟未形成の経営者向け先行プラン）\n- URL：Recruit→/gravity-recruit/ ／ Cultivate→/gravity-cultivate/ ／ Shift→/gravity-shift/';

// --- SYSTEM プロンプト読み込み（外部ファイル・P1-C 260512 分離）---
$system_prompt = file_get_contents(__DIR__ . '/system_prompt.txt');
if ($system_prompt === false) {
    error_log('[Scan generate] system_prompt.txt 読み込み失敗');
    http_response_code(500);
    echo json_encode(['error' => 'レポート生成の初期化に失敗しました']);
    exit;
}


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

### 事前情報の活用

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
- **引力定義は Cover Page（表紙・サーバ側で自動付与）に移管**。AI（あなた）は Cover Page を出力しない。Block A は core-quote から始める。gravity-definition-box は本文に含めない
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
- 引力定義は Cover Page に移管・AI は Cover Page を出力しない・Block A は core-quote から始める
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
], $reports_dir);

// --- 即時レスポンス: ジョブIDを返してから接続を閉じ、バックグラウンド処理へ ---
echo json_encode(['job_id' => $job_id, 'report_url' => $report_url]);

if (function_exists('fastcgi_finish_request')) {
    fastcgi_finish_request();
}
ignore_user_abort(true);
set_time_limit(300);

write_status($job_id, [
    'status' => 'running',
    'created_at' => time(),
], $reports_dir);

// --- Claude API 呼び出し（バックグラウンド実行・SYSTEM プロンプト prompt caching 有効） ---
$api_body = json_encode([
    'model' => 'claude-sonnet-4-5',
    'max_tokens' => 12000,
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
    ], $reports_dir);
    exit;
}

if ($http_code !== 200) {
    error_log('Claude API error (HTTP ' . $http_code . '): ' . $response);
    write_status($job_id, [
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
    write_status($job_id, [
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
// 長い文字列から先に置換する（短い文字列が部分的に先にマッチしないように）。
// jargon_map は外部 JSON ファイルから読み込む（P1-C 260512 分離）
$jargon_map_raw = file_get_contents(__DIR__ . '/jargon_map.json');
if ($jargon_map_raw === false) {
    error_log('[Scan generate] jargon_map.json 読み込み失敗');
    $jargon_map = [];
} else {
    $jargon_map = json_decode($jargon_map_raw, true) ?? [];
}

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
<link rel="stylesheet" href="/assets/css/diagnose-report.css?v=20260512">
<link rel="stylesheet" href="/assets/css/diagnose-report-scan.css?v=20260512">
<style>
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
], $reports_dir);
