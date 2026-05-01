<?php
// =============================================================================
// Gravity Shift - Hearing Data Save/Load API
// =============================================================================

$allowed_origins = ['https://growthfix.jp', 'http://localhost'];
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if (in_array($origin, $allowed_origins)) {
    header('Access-Control-Allow-Origin: ' . $origin);
} else {
    header('Access-Control-Allow-Origin: https://growthfix.jp');
}
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

$DATA_DIR = __DIR__ . '/../data';
$method = $_SERVER['REQUEST_METHOD'];

function respond($data, $code = 200) {
    http_response_code($code);
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    exit;
}

$project_id = $_GET['project'] ?? null;
$role = $_GET['role'] ?? null; // 'ceo', 'exec', or 'gap'
$exec_num = $_GET['exec'] ?? null; // 1, 2, 3...

if (!$project_id || !$role) {
    respond(['success' => false, 'error' => 'project and role parameters required'], 400);
}

// Validate project ID format
if (!preg_match('/^[a-f0-9\-]+$/i', $project_id)) {
    respond(['success' => false, 'error' => 'Invalid project ID format'], 400);
}

$project_dir = $DATA_DIR . '/' . basename($project_id);
if (!is_dir($project_dir)) {
    respond(['success' => false, 'error' => 'プロジェクトが見つかりません'], 404);
}

// Determine filename
if ($role === 'ceo') {
    $filename = 'ceo.json';
} elseif ($role === 'exec' && $exec_num) {
    $exec_int = intval($exec_num);
    if ($exec_int < 1 || $exec_int > 10) {
        respond(['success' => false, 'error' => 'Invalid exec number (1-10)'], 400);
    }
    $filename = 'exec_' . $exec_int . '.json';
} elseif ($role === 'gap') {
    $filename = 'gap_report.json';
} else {
    respond(['success' => false, 'error' => 'Invalid role/exec parameter'], 400);
}

$filepath = $project_dir . '/' . $filename;

// GET — load hearing data
if ($method === 'GET') {
    if (file_exists($filepath)) {
        $data = json_decode(file_get_contents($filepath), true);
        respond(['success' => true, 'data' => $data]);
    } else {
        respond(['success' => true, 'data' => null]);
    }
}

// POST — save hearing data
if ($method === 'POST') {
    $raw = file_get_contents('php://input');
    $input = json_decode($raw, true);

    if (!$input) respond(['success' => false, 'error' => 'Invalid JSON'], 400);

    // Read existing or start fresh
    $existing = [];
    if (file_exists($filepath)) {
        $existing = json_decode(file_get_contents($filepath), true) ?: [];
    }

    // Only allow hearing-related fields (prevent overwriting report_html, scores, etc.)
    $protected_fields = ['report_html', 'report_generated_at', 'scores', 'score_comments'];
    foreach ($protected_fields as $pf) {
        unset($input[$pf]);
    }

    // Merge input into existing
    $data = array_merge($existing, $input);
    $data['updated_at'] = date('Y-m-d H:i:s');

    file_put_contents($filepath, json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));

    // Update project updated_at
    $project_file = $project_dir . '/project.json';
    if (file_exists($project_file)) {
        $project = json_decode(file_get_contents($project_file), true);
        $project['updated_at'] = date('Y-m-d H:i:s');
        file_put_contents($project_file, json_encode($project, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
    }

    respond(['success' => true]);
}

respond(['success' => false, 'error' => 'Method not allowed'], 405);
