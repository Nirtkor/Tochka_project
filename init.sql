-- Создание таблицы roles
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Создание таблицы users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(300) NOT NULL,
    role_id INTEGER NOT NULL REFERENCES roles(id)
);

-- Создание таблицы products
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL
);

-- Создание таблицы reservations
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    date TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL,
    total FLOAT NOT NULL
);
