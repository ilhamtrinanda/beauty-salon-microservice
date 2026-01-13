CREATE DATABASE booking_db;

\c booking_db;

CREATE TABLE
IF NOT EXISTS bookings
(
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR
(255) NOT NULL,
    salon_id INT NOT NULL,
    booking_date TIMESTAMP NOT NULL,
    status VARCHAR
(50) DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
