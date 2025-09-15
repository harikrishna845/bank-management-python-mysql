-- schema.sql
-- Database schema and sample data for Bank Management System

CREATE TABLE admin (
    admin_id VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50) NOT NULL
);

CREATE TABLE users (
    account_no BIGINT PRIMARY KEY,
    name VARCHAR(100),
    account_type ENUM('savings','current'),
    pin INT,
    balance DECIMAL(10,2)
);

CREATE TABLE transactions (
    txn_id INT AUTO_INCREMENT PRIMARY KEY,
    account_no BIGINT,
    action ENUM('credit','debit'),
    amount DECIMAL(10,2),
    txn_date DATETIME,
    closing_balance DECIMAL(10,2)
);

-- Sample data
INSERT INTO admin VALUES ('hari', 'hari123');

INSERT INTO users VALUES
(978654321, 'harikrishna', 'savings', 3087, 801.00),
(978654322, 'sai', 'current', 7777, 500.00),
(978654323, 'mani', 'savings', 9999, 300.00),
(978654324, 'nandini', 'savings', 9999, 0.00);
