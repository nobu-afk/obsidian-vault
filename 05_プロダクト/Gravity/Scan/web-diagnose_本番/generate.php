<?php
/**
 * Gravity Scan 4 型 Web 無料診断 — generate.php (v0.2 12 問版・ミニマル版)
 *
 * 役割：
 *  1. POST JSON 受信（リード情報 + 12 問回答 + フロント計算済スコア）
 *  2. バリデーション（origin / 必須項目 / 12 問範囲 / メール形式）
 *  3. PHP 側でもスコア再計算（フロント改ざん対策）
 *  4. CSV ログ保存（logs/leads_YYYYMM.csv）
 *  5. メール送信：経営者お礼 + 内部通知（mb_send_mail）
 *  6. JSON 返却（success / type / scores / message）
 *
 * 設計 SSOT：
 *  - 05_プロダクト/GravityScan/診断_設計/260512_4型判定エンジン_PHP設計_v0.2_12問版.md
 *  - 05_プロダクト/GravityScan/診断_設計/260512_4型Web診断UI_仕様書_v0.2_12問版.md
 *
 * 配置先：/gravity-scan/web-diagnose/generate.php
 */

declare(strict_types=1);

mb_internal_encoding('UTF-8');
mb_language('uni');

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store, no-cache, must-revalidate');

// ========================================
// 0. メソッド + Origin / Referer 確認
// ========================================
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method Not Allowed'], JSON_UNESCAPED_UNICODE);
    exit;
}

$allowed_host = 'growthfix.jp';
$origin  = $_SERVER['HTTP_ORIGIN']  ?? '';
$referer = $_SERVER['HTTP_REFERER'] ?? '';
if (
    (strpos($origin,  $allowed_host) === false) &&
    (strpos($referer, $allowed_host) === false)
) {
    http_response_code(403);
    echo json_encode(['error' => 'Invalid origin'], JSON_UNESCAPED_UNICODE);
    exit;
}

// ========================================
// 1. JSON 受信 + パース
// ========================================
$raw = file_get_contents('php://input');
if ($raw === false || $raw === '') {
    http_response_code(400);
    echo json_encode(['error' => 'Empty body'], JSON_UNESCAPED_UNICODE);
    exit;
}
$input = json_decode($raw, true);
if (!is_array($input)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON'], JSON_UNESCAPED_UNICODE);
    exit;
}

// ========================================
// 2. 必須項目バリデーション
// ========================================
$required = ['name', 'company', 'email', 'industry', 'size', 'type', 'collect', 'vitality', 'answers'];
foreach ($required as $key) {
    if (!array_key_exists($key, $input)) {
        http_response_code(400);
        echo json_encode(['error' => "Missing field: {$key}"], JSON_UNESCAPED_UNICODE);
        exit;
    }
}

$name     = mb_substr(trim((string)$input['name']),     0, 100);
$company  = mb_substr(trim((string)$input['company']),  0, 200);
$email    = trim((string)$input['email']);
$industry = mb_substr(trim((string)$input['industry']), 0, 50);
$size     = mb_substr(trim((string)$input['size']),     0, 20);
$type_in  = mb_substr(trim((string)$input['type']),     0, 10);

if ($name === '' || $company === '') {
    http_response_code(400);
    echo json_encode(['error' => '氏名と会社名は必須です'], JSON_UNESCAPED_UNICODE);
    exit;
}
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo json_encode(['error' => 'メールアドレスの形式が正しくありません'], JSON_UNESCAPED_UNICODE);
    exit;
}

$valid_types = ['整合', '拡散', '渇望', '不毛'];
if (!in_array($type_in, $valid_types, true)) {
    http_response_code(400);
    echo json_encode(['error' => '型 ID が不正です'], JSON_UNESCAPED_UNICODE);
    exit;
}

$answers = $input['answers'];
if (!is_array($answers) || count($answers) !== 12) {
    http_response_code(400);
    echo json_encode(['error' => '回答は 12 問必要です'], JSON_UNESCAPED_UNICODE);
    exit;
}
$ans_int = [];
foreach ($answers as $v) {
    if (!is_numeric($v)) {
        http_response_code(400);
        echo json_encode(['error' => '回答は整数で入力してください'], JSON_UNESCAPED_UNICODE);
        exit;
    }
    $iv = (int)$v;
    if ($iv < 1 || $iv > 5) {
        http_response_code(400);
        echo json_encode(['error' => '回答は 1-5 の範囲で入力してください'], JSON_UNESCAPED_UNICODE);
        exit;
    }
    $ans_int[] = $iv;
}

// ========================================
// 3. PHP 側スコア再計算（フロント改ざん対策・SSOT 準拠）
//    集まる軸：answers[0..5]、躍動軸：answers[6..11]
//    正規化：(sum - 6) / 24 × 100
// ========================================
function calc_axis_score(array $a, int $start, int $end): int {
    $sum = 0;
    for ($i = $start; $i <= $end; $i++) {
        $sum += $a[$i];
    }
    return (int)round(($sum - 6) / 24 * 100);
}
function judge_type(int $g, int $t): string {
    $hg = $g >= 50;
    $ht = $t >= 50;
    if ($hg && $ht)  return '整合';
    if ($hg && !$ht) return '拡散';
    if (!$hg && $ht) return '渇望';
    return '不毛';
}

$gather_score = calc_axis_score($ans_int, 0, 5);
$thrive_score = calc_axis_score($ans_int, 6, 11);
$type_php     = judge_type($gather_score, $thrive_score);
$type_match   = ($type_php === $type_in) ? 'OK' : 'MISMATCH';

// ========================================
// 4. CSV ログ保存（logs/leads_YYYYMM.csv）
// ========================================
$log_dir = __DIR__ . '/logs';
if (!is_dir($log_dir)) {
    @mkdir($log_dir, 0750, true);
}
$log_file = $log_dir . '/leads_' . date('Ym') . '.csv';
$is_new = !file_exists($log_file) || filesize($log_file) === 0;
$row = [
    date('Y-m-d H:i:s'),
    $name,
    $company,
    $email,
    $industry,
    $size,
    $type_php,
    (string)$gather_score,
    (string)$thrive_score,
    implode(',', $ans_int),
    $type_match,
    $_SERVER['REMOTE_ADDR'] ?? 'unknown',
];
$fp = @fopen($log_file, 'a');
if ($fp) {
    if ($is_new) {
        fputcsv($fp, [
            'timestamp', 'name', 'company', 'email', 'industry', 'size',
            'type', 'gather', 'thrive', 'answers', 'type_match', 'ip'
        ]);
    }
    fputcsv($fp, $row);
    fclose($fp);
    @chmod($log_file, 0640);
}

// ========================================
// 5. メール送信（mb_send_mail）
// ========================================
$mail_sent = false;

// 5-1. 内部通知メール
$internal_to      = 'nobuyuki08@gmail.com';
$internal_subject = '【Gravity Scan】Web 診断完了：' . $type_php . '型（' . $company . '）';
$internal_body    = "Gravity Scan Web 無料診断（12 問版）が完了しました。\n\n";
$internal_body   .= "■ 経営者情報\n";
$internal_body   .= "氏名：{$name}\n";
$internal_body   .= "会社：{$company}\n";
$internal_body   .= "メール：{$email}\n";
$internal_body   .= "業種：{$industry}\n";
$internal_body   .= "規模：{$size}\n\n";
$internal_body   .= "■ 診断結果（PHP 側再計算）\n";
$internal_body   .= "型：{$type_php}型\n";
$internal_body   .= "集まる軸：{$gather_score}/100\n";
$internal_body   .= "躍動軸：{$thrive_score}/100\n";
$internal_body   .= "回答列：" . implode(',', $ans_int) . "\n\n";
$internal_body   .= "フロント / PHP 型一致：{$type_match}\n";
$internal_body   .= "受診日時：" . date('Y-m-d H:i:s') . " (JST)\n";
$internal_body   .= "IP：" . ($_SERVER['REMOTE_ADDR'] ?? 'unknown') . "\n\n";
$internal_body   .= "次のアクション：30 分無料相談予約フォロー\n";
$internal_body   .= "https://growthfix.jp/contact/\n";

$internal_headers  = "From: Gravity Scan <no-reply@growthfix.jp>\r\n";
$internal_headers .= "Reply-To: {$email}\r\n";
$internal_headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
$internal_headers .= "X-Mailer: GravityScan-WebDiagnose/v0.2\r\n";

if (@mb_send_mail($internal_to, $internal_subject, $internal_body, $internal_headers)) {
    $mail_sent = true;
}

// 5-2. 経営者向けお礼メール
$user_subject = '【Gravity Scan】無料診断完了：' . $type_php . '型診断結果のご案内';
$user_body    = "{$name} 様\n\n";
$user_body   .= "Gravity Scan の無料 Web 診断にご回答いただきありがとうございました。\n";
$user_body   .= "{$company} 様の組織の引力タイプを診断いたしました。\n\n";
$user_body   .= "■ 診断結果\n";
$user_body   .= "組織の引力タイプ：{$type_php}型\n";
$user_body   .= "集まる軸（採用基盤）：{$gather_score}/100\n";
$user_body   .= "躍動軸（躍動組織）：{$thrive_score}/100\n\n";
$user_body   .= "結果の詳細は受診画面でご確認いただけます。\n\n";
$user_body   .= "■ 次の一手\n";
$user_body   .= "12 問の Web 簡易版では把握できる範囲が限られます。\n";
$user_body   .= "より精密な引力タイプ判定と、貴社固有の処方箋設計をご希望の場合は\n";
$user_body   .= "下記いずれかをご活用ください。\n\n";
$user_body   .= "▼ 30 分無料相談（Zoom・勧誘なし）\n";
$user_body   .= "https://growthfix.jp/contact/\n\n";
$user_body   .= "▼ Gravity Scan 本格版（60 分・10 万円）\n";
$user_body   .= "https://growthfix.jp/gravity-scan/\n\n";
$user_body   .= "──\n";
$user_body   .= "GrowthFix 株式会社\n";
$user_body   .= "代表 石井伸幸（引力の参謀）\n";
$user_body   .= "https://growthfix.jp/\n";

$user_headers  = "From: 石井伸幸 (GrowthFix) <no-reply@growthfix.jp>\r\n";
$user_headers .= "Reply-To: nobuyuki08@gmail.com\r\n";
$user_headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
$user_headers .= "X-Mailer: GravityScan-WebDiagnose/v0.2\r\n";

@mb_send_mail($email, $user_subject, $user_body, $user_headers);

// ========================================
// 6. JSON 返却
// ========================================
echo json_encode([
    'success'      => true,
    'type'         => $type_php,
    'gather_score' => $gather_score,
    'thrive_score' => $thrive_score,
    'type_match'   => $type_match,
    'mail_sent'    => $mail_sent,
    'message'      => 'ご回答ありがとうございました。診断結果をメールでお送りしました。',
], JSON_UNESCAPED_UNICODE);
