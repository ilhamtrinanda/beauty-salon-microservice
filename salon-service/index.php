<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE');
header('Access-Control-Allow-Headers: Content-Type');

$host = getenv('DB_HOST') ?: 'localhost';
$dbname = getenv('DB_NAME') ?: 'salon_db';
$username = getenv('DB_USER') ?: 'root';
$password = getenv('DB_PASSWORD') ?: 'password';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Create table if not exists
    $pdo->exec("CREATE TABLE IF NOT EXISTS salons (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        address TEXT,
        phone VARCHAR(50),
        services TEXT,
        price DECIMAL(10,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )");
} catch (PDOException $e) {
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
    exit;
}

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$segments = explode('/', trim($path, '/'));

// Health check
if ($path === '/health') {
    echo json_encode(['status' => 'Salon Service is running']);
    exit;
}

// Get ID from URL if exists
$id = isset($segments[2]) ? intval($segments[2]) : null;

switch ($method) {
    case 'GET':
        if ($id) {
            // Get single salon
            $stmt = $pdo->prepare("SELECT * FROM salons WHERE id = ?");
            $stmt->execute([$id]);
            $salon = $stmt->fetch(PDO::FETCH_ASSOC);

            if ($salon) {
                echo json_encode(['success' => true, 'data' => $salon]);
            } else {
                http_response_code(404);
                echo json_encode(['success' => false, 'message' => 'Salon not found']);
            }
        } else {
            // Get all salons
            $stmt = $pdo->query("SELECT * FROM salons");
            $salons = $stmt->fetchAll(PDO::FETCH_ASSOC);
            echo json_encode(['success' => true, 'data' => $salons]);
        }
        break;

    case 'POST':
        $data = json_decode(file_get_contents('php://input'), true);

        $stmt = $pdo->prepare("INSERT INTO salons (name, address, phone, services, price) VALUES (?, ?, ?, ?, ?)");
        $stmt->execute([
            $data['name'],
            $data['address'] ?? '',
            $data['phone'] ?? '',
            $data['services'] ?? '',
            $data['price'] ?? 0
        ]);

        $newId = $pdo->lastInsertId();
        $stmt = $pdo->prepare("SELECT * FROM salons WHERE id = ?");
        $stmt->execute([$newId]);
        $salon = $stmt->fetch(PDO::FETCH_ASSOC);

        http_response_code(201);
        echo json_encode(['success' => true, 'data' => $salon]);
        break;

    case 'PUT':
        if (!$id) {
            http_response_code(400);
            echo json_encode(['success' => false, 'message' => 'ID required']);
            break;
        }

        $data = json_decode(file_get_contents('php://input'), true);

        $stmt = $pdo->prepare("UPDATE salons SET name=?, address=?, phone=?, services=?, price=? WHERE id=?");
        $stmt->execute([
            $data['name'],
            $data['address'] ?? '',
            $data['phone'] ?? '',
            $data['services'] ?? '',
            $data['price'] ?? 0,
            $id
        ]);

        $stmt = $pdo->prepare("SELECT * FROM salons WHERE id = ?");
        $stmt->execute([$id]);
        $salon = $stmt->fetch(PDO::FETCH_ASSOC);

        echo json_encode(['success' => true, 'data' => $salon]);
        break;

    case 'DELETE':
        if (!$id) {
            http_response_code(400);
            echo json_encode(['success' => false, 'message' => 'ID required']);
            break;
        }

        $stmt = $pdo->prepare("DELETE FROM salons WHERE id = ?");
        $stmt->execute([$id]);

        echo json_encode(['success' => true, 'message' => 'Salon deleted']);
        break;

    default:
        http_response_code(405);
        echo json_encode(['success' => false, 'message' => 'Method not allowed']);
}
