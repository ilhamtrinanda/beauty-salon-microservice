<?php
// 1. TANGANI CORS
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
    http_response_code(200);
    exit();
}

// 2. KONEKSI DATABASE - SESUAI DOCKER-COMPOSE
// Gunakan environment variable atau default ke mysql_salon
$host = getenv('DB_HOST') ?: 'mysql_salon';
$dbname = getenv('DB_NAME') ?: 'salon_db';
$username = getenv('DB_USER') ?: 'root';
$password = getenv('DB_PASSWORD') ?: 'password';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Database connection failed: ' . $e->getMessage(),
        'host' => $host,
        'dbname' => $dbname,
        'user' => $username
    ]);
    exit;
}

// 3. PARSING URL - UNTUK DOCKER
$method = $_SERVER['REQUEST_METHOD'];
$requestUri = $_SERVER['REQUEST_URI'];

// Hapus query string
$path = parse_url($requestUri, PHP_URL_PATH);

// Hapus nama file dari path
$scriptName = $_SERVER['SCRIPT_NAME'];
$path = str_replace(dirname($scriptName), '', $path);
$path = str_replace(basename($scriptName), '', $path);

// Bersihkan path
$path = trim($path, '/');
$segments = $path ? explode('/', $path) : [];

// ID adalah segment pertama yang numerik
$id = null;
foreach ($segments as $segment) {
    if (is_numeric($segment)) {
        $id = intval($segment);
        break;
    }
}

// Debug - Bisa dilihat di Docker logs
error_log("=== DEBUG ===");
error_log("Method: $method");
error_log("Request URI: $requestUri");
error_log("Script Name: $scriptName");
error_log("Path: $path");
error_log("Segments: " . json_encode($segments));
error_log("ID: " . ($id ?? 'null'));
error_log("=============");

// 4. OPERASI CRUD
try {
    switch ($method) {
        case 'GET':
            if ($id) {
                $stmt = $pdo->prepare("SELECT * FROM salons WHERE id = ?");
                $stmt->execute([$id]);
                $salon = $stmt->fetch(PDO::FETCH_ASSOC);

                if ($salon) {
                    echo json_encode(['success' => true, 'data' => $salon]);
                } else {
                    http_response_code(404);
                    echo json_encode(['success' => false, 'message' => 'Data tidak ditemukan']);
                }
            } else {
                $stmt = $pdo->query("SELECT * FROM salons ORDER BY id DESC");
                echo json_encode(['success' => true, 'data' => $stmt->fetchAll(PDO::FETCH_ASSOC)]);
            }
            break;

        case 'POST':
            $data = json_decode(file_get_contents('php://input'), true);

            if (!$data || !isset($data['name'])) {
                http_response_code(400);
                echo json_encode(['success' => false, 'message' => 'Data tidak valid']);
                break;
            }

            $stmt = $pdo->prepare("INSERT INTO salons (name, address, phone, services, price) VALUES (?, ?, ?, ?, ?)");
            $stmt->execute([
                $data['name'] ?? '',
                $data['address'] ?? '',
                $data['phone'] ?? '',
                $data['services'] ?? '',
                $data['price'] ?? 0
            ]);

            echo json_encode(['success' => true, 'id' => $pdo->lastInsertId()]);
            break;

        case 'PUT':
            if (!$id) {
                http_response_code(400);
                echo json_encode(['success' => false, 'message' => 'ID tidak ditemukan di URL']);
                break;
            }

            $data = json_decode(file_get_contents('php://input'), true);

            if (!$data) {
                http_response_code(400);
                echo json_encode(['success' => false, 'message' => 'Data tidak valid']);
                break;
            }

            $stmt = $pdo->prepare("UPDATE salons SET name=?, address=?, phone=?, services=?, price=? WHERE id=?");
            $result = $stmt->execute([
                $data['name'] ?? '',
                $data['address'] ?? '',
                $data['phone'] ?? '',
                $data['services'] ?? '',
                $data['price'] ?? 0,
                $id
            ]);

            if ($stmt->rowCount() > 0) {
                echo json_encode(['success' => true, 'message' => 'Data berhasil diupdate']);
            } else {
                http_response_code(404);
                echo json_encode(['success' => false, 'message' => 'Data tidak ditemukan atau tidak ada perubahan']);
            }
            break;

        case 'DELETE':
            if (!$id) {
                http_response_code(400);
                echo json_encode(['success' => false, 'message' => 'ID tidak ditemukan di URL. Path: ' . $path]);
                break;
            }

            $stmt = $pdo->prepare("DELETE FROM salons WHERE id = ?");
            $stmt->execute([$id]);

            if ($stmt->rowCount() > 0) {
                echo json_encode(['success' => true, 'message' => 'Data berhasil dihapus']);
            } else {
                http_response_code(404);
                echo json_encode(['success' => false, 'message' => 'Data tidak ditemukan']);
            }
            break;

        default:
            http_response_code(405);
            echo json_encode(['success' => false, 'message' => 'Method tidak didukung']);
    }
} catch (PDOException $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Database error: ' . $e->getMessage()]);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
}
