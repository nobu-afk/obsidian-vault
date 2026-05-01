<?php
// =============================================================================
// Gravity Shift - Project CRUD API
// =============================================================================

$allowed_origins = ['https://growthfix.jp', 'http://localhost'];
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
if (in_array($origin, $allowed_origins)) {
    header('Access-Control-Allow-Origin: ' . $origin);
} else {
    header('Access-Control-Allow-Origin: https://growthfix.jp');
}
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

$DATA_DIR = __DIR__ . '/../data';

// Ensure data directory exists
if (!is_dir($DATA_DIR)) {
    mkdir($DATA_DIR, 0755, true);
}

$method = $_SERVER['REQUEST_METHOD'];
$project_id = $_GET['id'] ?? null;

// Validate project ID format (hex-hex-hex-hex-hex)
if ($project_id && !preg_match('/^[a-f0-9\-]+$/i', $project_id)) {
    respond(['success' => false, 'error' => 'Invalid project ID format'], 400);
}

// --- Helper Functions ---
function respond($data, $code = 200) {
    http_response_code($code);
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    exit;
}

function readProjectJson($dir) {
    $file = $dir . '/project.json';
    if (!file_exists($file)) return null;
    return json_decode(file_get_contents($file), true);
}

function writeProjectJson($dir, $data) {
    file_put_contents($dir . '/project.json', json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
}

// --- Routes ---

// GET /api/project.php — list all projects
// GET /api/project.php?id={id} — get single project
if ($method === 'GET') {
    if ($project_id) {
        $project_dir = $DATA_DIR . '/' . basename($project_id);
        $project = readProjectJson($project_dir);
        if (!$project) respond(['success' => false, 'error' => 'プロジェクトが見つかりません'], 404);

        // Enrich with hearing status
        $project['hearings'] = [];

        // CEO hearing
        $ceo_file = $project_dir . '/ceo.json';
        if (file_exists($ceo_file)) {
            $ceo = json_decode(file_get_contents($ceo_file), true);
            $project['hearings']['ceo'] = [
                'status' => $ceo['status'] ?? 'not_started',
                'name' => $project['ceo_name'] ?? '',
                'has_report' => !empty($ceo['report_html']),
            ];
        } else {
            $project['hearings']['ceo'] = ['status' => 'not_started', 'name' => $project['ceo_name'] ?? '', 'has_report' => false];
        }

        // Exec hearings
        $exec_count = $project['exec_count'] ?? 3;
        for ($i = 1; $i <= $exec_count; $i++) {
            $exec_file = $project_dir . '/exec_' . $i . '.json';
            if (file_exists($exec_file)) {
                $exec = json_decode(file_get_contents($exec_file), true);
                $project['hearings']['exec_' . $i] = [
                    'status' => $exec['status'] ?? 'not_started',
                    'name' => $exec['name'] ?? '幹部' . $i,
                    'has_report' => !empty($exec['report_html']),
                ];
            } else {
                $project['hearings']['exec_' . $i] = ['status' => 'not_started', 'name' => '幹部' . $i, 'has_report' => false];
            }
        }

        // Gap report
        $gap_file = $project_dir . '/gap_report.json';
        $project['has_gap_report'] = file_exists($gap_file) && !empty(json_decode(file_get_contents($gap_file), true)['report_html'] ?? '');

        respond(['success' => true, 'project' => $project]);
    } else {
        // List all projects
        $projects = [];
        if (is_dir($DATA_DIR)) {
            $dirs = scandir($DATA_DIR);
            foreach ($dirs as $dir) {
                if ($dir === '.' || $dir === '..') continue;
                $project = readProjectJson($DATA_DIR . '/' . $dir);
                if ($project) {
                    // Count completed hearings
                    $completed = 0;
                    $total = 1 + ($project['exec_count'] ?? 3);

                    $ceo_file = $DATA_DIR . '/' . $dir . '/ceo.json';
                    if (file_exists($ceo_file)) {
                        $ceo = json_decode(file_get_contents($ceo_file), true);
                        if (($ceo['status'] ?? '') === 'completed') $completed++;
                    }

                    $exec_count = $project['exec_count'] ?? 3;
                    for ($i = 1; $i <= $exec_count; $i++) {
                        $exec_file = $DATA_DIR . '/' . $dir . '/exec_' . $i . '.json';
                        if (file_exists($exec_file)) {
                            $exec = json_decode(file_get_contents($exec_file), true);
                            if (($exec['status'] ?? '') === 'completed') $completed++;
                        }
                    }

                    $project['completed_hearings'] = $completed;
                    $project['total_hearings'] = $total;

                    $gap_file = $DATA_DIR . '/' . $dir . '/gap_report.json';
                    $project['has_gap_report'] = file_exists($gap_file) && !empty(json_decode(file_get_contents($gap_file), true)['report_html'] ?? '');

                    $projects[] = $project;
                }
            }
        }

        // Sort by created_at desc
        usort($projects, function($a, $b) {
            return strcmp($b['created_at'] ?? '', $a['created_at'] ?? '');
        });

        respond(['success' => true, 'projects' => $projects]);
    }
}

// POST /api/project.php — create new project
if ($method === 'POST') {
    $raw = file_get_contents('php://input');
    $input = json_decode($raw, true);

    if (!$input) respond(['success' => false, 'error' => 'Invalid JSON'], 400);

    $company_name = trim($input['company_name'] ?? '');
    $ceo_name = trim($input['ceo_name'] ?? '');
    $employee_count = trim($input['employee_count'] ?? '');
    $industry = trim($input['industry'] ?? '');
    $exec_count = intval($input['exec_count'] ?? 3);

    if (!$company_name) respond(['success' => false, 'error' => '会社名は必須です'], 400);
    if ($exec_count < 0 || $exec_count > 10) $exec_count = 0;

    // Generate project ID
    $id = sprintf('%s-%04x-%04x-%04x-%012x',
        bin2hex(random_bytes(4)),
        mt_rand(0, 0xffff),
        mt_rand(0, 0x0fff) | 0x4000,
        mt_rand(0, 0x3fff) | 0x8000,
        mt_rand(0, 0xffffffffffff)
    );

    $project_dir = $DATA_DIR . '/' . $id;
    mkdir($project_dir, 0755, true);

    // BP結果参照データ（260421要件定義・BP必須前提・Scanの深層引力5軸はBP結果を使う）
    $bp_reference = [];
    if (isset($input['bp_reference']) && is_array($input['bp_reference'])) {
        $bp_reference = [
            'bp_received' => !empty($input['bp_reference']['bp_received']),
            'bp_date' => trim($input['bp_reference']['bp_date'] ?? ''),
            'bp_anger' => trim($input['bp_reference']['bp_anger'] ?? ''),
            'bp_motive' => trim($input['bp_reference']['bp_motive'] ?? ''),
            'bp_vow' => trim($input['bp_reference']['bp_vow'] ?? ''),
            'bp_wound' => trim($input['bp_reference']['bp_wound'] ?? ''),
            'bp_future' => trim($input['bp_reference']['bp_future'] ?? ''),
        ];
    }

    $project = [
        'id' => $id,
        'company_name' => $company_name,
        'ceo_name' => $ceo_name,
        'employee_count' => $employee_count,
        'industry' => $industry,
        'exec_count' => $exec_count,
        'exec_names' => is_array($input['exec_names'] ?? null) ? $input['exec_names'] : [],
        'bp_reference' => $bp_reference,
        'created_at' => date('Y-m-d H:i:s'),
        'updated_at' => date('Y-m-d H:i:s'),
    ];

    writeProjectJson($project_dir, $project);

    respond(['success' => true, 'project' => $project], 201);
}

// PUT /api/project.php?id={id} — update project
if ($method === 'PUT') {
    if (!$project_id) respond(['success' => false, 'error' => 'Project ID required'], 400);

    $project_dir = $DATA_DIR . '/' . basename($project_id);
    $project = readProjectJson($project_dir);
    if (!$project) respond(['success' => false, 'error' => 'プロジェクトが見つかりません'], 404);

    $raw = file_get_contents('php://input');
    $input = json_decode($raw, true);
    if (!$input) respond(['success' => false, 'error' => 'Invalid JSON'], 400);

    // Update allowed fields
    $allowed = ['company_name', 'ceo_name', 'employee_count', 'industry', 'exec_count', 'exec_names', 'bp_reference'];
    foreach ($allowed as $field) {
        if (isset($input[$field])) {
            $project[$field] = $input[$field];
        }
    }
    $project['updated_at'] = date('Y-m-d H:i:s');

    writeProjectJson($project_dir, $project);

    respond(['success' => true, 'project' => $project]);
}

// DELETE /api/project.php?id={id} — delete project
if ($method === 'DELETE') {
    if (!$project_id) respond(['success' => false, 'error' => 'Project ID required'], 400);

    $project_dir = $DATA_DIR . '/' . basename($project_id);
    if (!is_dir($project_dir)) respond(['success' => false, 'error' => 'プロジェクトが見つかりません'], 404);

    // Remove all files in directory (including hidden files)
    $files = array_merge(glob($project_dir . '/*'), glob($project_dir . '/.*'));
    foreach ($files as $file) {
        if (is_file($file)) unlink($file);
    }
    rmdir($project_dir);

    respond(['success' => true]);
}

respond(['success' => false, 'error' => 'Method not allowed'], 405);
