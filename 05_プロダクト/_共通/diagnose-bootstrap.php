<?php
/**
 * Gravity 診断 generate.php 共通ブートストラップ
 *
 * 読み込み方：各 generate.php の冒頭（<?php の直後）に
 *   $DIAGNOSE_CONFIG_PATH = __DIR__ . '/config.php';   // またはパス調整
 *   require_once __DIR__ . '/../../_共通/diagnose-bootstrap.php';
 * を追加する。$DIAGNOSE_CONFIG_PATH が未定義の場合は __DIR__/config.php にフォールバック。
 *
 * 提供するもの：
 *   - CORS ヘッダー（growthfix.jp / localhost:8000 許可）
 *   - OPTIONS 早期 return
 *   - ANTHROPIC_API_KEY 読み込みとエラー返却
 *   - $reports_dir の作成
 *   - ジョブステータスヘルパー関数（status_file_path / write_status / read_status）
 *   - GET ?report= ハンドラー
 *   - GET ?job= ハンドラー
 *   - POST メソッドチェック
 *   - $input = json_decode(...) とバリデーション
 *
 * 以降の処理（$choices 取り出し・プロンプト構築・Claude API 呼び出し）は
 * 各 generate.php 側で実装する。
 *
 * 共通化対象外（差分が存在するため各ファイルで管理）：
 *   - $config_file パス（Scan: /../config.php、CODE/Exec: /config.php）
 *   - $report_id / $REPORT_FILE の宣言位置（非同期 vs 同期で初期化タイミング差異）
 */

// ============================================================
// 1. レスポンスヘッダー / CORS
// ============================================================
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

// ============================================================
// 2. 設定（config.php 読み込み + ANTHROPIC_API_KEY）
// ============================================================
// 呼び出し元が $DIAGNOSE_CONFIG_PATH を定義していない場合は __DIR__ の config.php を使う。
// ※ __DIR__ はこのファイル自身のディレクトリになるため、呼び出し元で明示的に指定すること。
if (!isset($DIAGNOSE_CONFIG_PATH)) {
    $DIAGNOSE_CONFIG_PATH = __DIR__ . '/config.php';
}
if (file_exists($DIAGNOSE_CONFIG_PATH)) {
    require_once $DIAGNOSE_CONFIG_PATH;
}
$ANTHROPIC_API_KEY = defined('ANTHROPIC_API_KEY') ? ANTHROPIC_API_KEY : getenv('ANTHROPIC_API_KEY');
if (empty($ANTHROPIC_API_KEY)) {
    http_response_code(500);
    echo json_encode(['error' => 'API設定エラー。管理者に連絡してください。']);
    exit;
}

// ============================================================
// 3. reports ディレクトリ確保
// ============================================================
// 呼び出し元の __DIR__ を使って reports/ を作るため、
// 呼び出し元が $DIAGNOSE_BASE_DIR を定義することを推奨。
// 未定義の場合はこのファイルのディレクトリを使う（誤動作の可能性があるため明示を推奨）。
if (!isset($DIAGNOSE_BASE_DIR)) {
    $DIAGNOSE_BASE_DIR = __DIR__;
}
$reports_dir = $DIAGNOSE_BASE_DIR . '/reports';
@mkdir($reports_dir, 0755, true);

// ============================================================
// 4. ジョブステータスヘルパー関数
// ============================================================
if (!function_exists('status_file_path')) {
    function status_file_path($id, $dir) {
        return $dir . '/status_' . $id . '.json';
    }
}

if (!function_exists('read_status')) {
    function read_status($id, $dir) {
        $path = status_file_path($id, $dir);
        $raw = @file_get_contents($path);
        return $raw === false ? null : json_decode($raw, true);
    }
}

if (!function_exists('write_status')) {
    function write_status($id, $data, $dir) {
        if (!isset($data['created_at'])) {
            $existing = read_status($id, $dir);
            $data['created_at'] = $existing['created_at'] ?? time();
        }
        $data['updated_at'] = time();
        file_put_contents(status_file_path($id, $dir), json_encode($data, JSON_UNESCAPED_UNICODE));
    }
}

// ============================================================
// 5. GET ?report=REPORT_ID → レポート HTML 返却
// ============================================================
if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['report'])) {
    $req_id = preg_replace('/[^a-f0-9]/', '', $_GET['report']);
    $req_file = $reports_dir . '/report_' . $req_id . '.html';
    if ($req_id && strlen($req_id) === 16 && file_exists($req_file)) {
        header('Content-Type: text/html; charset=utf-8');
        readfile($req_file);
    } else {
        http_response_code(404);
        echo json_encode(['error' => 'レポートが見つかりません']);
    }
    exit;
}

// ============================================================
// 6. GET ?job=JOB_ID → ジョブステータス返却
// ============================================================
if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['job'])) {
    $req_id = preg_replace('/[^a-f0-9]/', '', $_GET['job']);
    if (!$req_id || strlen($req_id) !== 16) {
        http_response_code(400);
        echo json_encode(['error' => 'Invalid job ID']);
        exit;
    }
    $status = read_status($req_id, $reports_dir);
    if (!$status) {
        http_response_code(404);
        echo json_encode(['error' => 'Job not found']);
        exit;
    }
    echo json_encode($status);
    exit;
}

// ============================================================
// 7. POST メソッドチェック
// ============================================================
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

// ============================================================
// 8. リクエストボディ JSON デコード
// ============================================================
$input = json_decode(file_get_contents('php://input'), true);
if (!$input) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON']);
    exit;
}

// ここまで bootstrap 完了。
// 以降の処理（$choices 取り出し・プロンプト構築・Claude API 呼び出し）は
// 各 generate.php 側で実装する。
