CREATE DATABASE
IF NOT EXISTS salon_db;
USE salon_db;

CREATE TABLE
IF NOT EXISTS salons
(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR
(255) NOT NULL,
    address TEXT,
    phone VARCHAR
(50),
    services TEXT,
    price DECIMAL
(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
