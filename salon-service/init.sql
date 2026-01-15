CREATE DATABASE IF NOT EXISTS salon_db;
USE salon_db;

CREATE TABLE IF NOT EXISTS salons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(50),
    services TEXT,
    price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO salons (name, address, phone, services, price) VALUES 
('Salon Cantik', 'Jl. Merdeka No. 123', '08123456789', 'Potong Rambut, Creambath', 150000),
('Salon Indah', 'Jl. Sudirman No. 456', '08198765432', 'Hair Spa, Manicure', 200000),
('Salon Elite', 'Jl. Asia Afrika No. 789', '08187654321', 'Full Treatment', 250000);