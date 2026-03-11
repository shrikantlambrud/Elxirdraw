-- =====================================
-- RENTAL SYSTEM DATABASE
-- =====================================

CREATE DATABASE IF NOT EXISTS rental_system;
USE rental_system;

-- =====================================
-- USERS TABLE
-- =====================================

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('owner','renter','admin') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================
-- PROPERTIES TABLE
-- =====================================

CREATE TABLE properties (
    id INT PRIMARY KEY AUTO_INCREMENT,
    owner_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    price INT NOT NULL,
    city VARCHAR(100) NOT NULL,
    area VARCHAR(150),
    
    status ENUM('pending','active','rejected') DEFAULT 'pending',
    
    utr_number VARCHAR(100),
    payment_status ENUM('pending','submitted','approved','rejected') 
        DEFAULT 'pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (owner_id) REFERENCES users(id)
        ON DELETE CASCADE
);

-- =====================================
-- INDEXES (for faster search)
-- =====================================

CREATE INDEX idx_city ON properties(city);
CREATE INDEX idx_status ON properties(status);
CREATE INDEX idx_payment_status ON properties(payment_status);

-- =====================================
-- DEFAULT ADMIN USER
-- Email: admin@gmail.com
-- Password: admin123
-- =====================================

INSERT INTO users (name, email, password, role)
VALUES (
    'Admin',
    'admin@gmail.com',
    '$pbkdf2-sha256$29000$5v0bW8XxPq0gk0Pz$yYF8D7T9lRzL3HqJx2kRj6JYvJfYwzWJz4mX9X6sY2U',
    'admin'
);

-- NOTE:
-- If password does not work, register admin manually
-- because hash may differ based on your Werkzeug version.