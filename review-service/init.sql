CREATE DATABASE
IF NOT EXISTS review_db;
USE review_db;

CREATE TABLE
IF NOT EXISTS reviews
(
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR
(255) NOT NULL,
    salon_id INT NOT NULL,
    rating INT NOT NULL CHECK
(rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
