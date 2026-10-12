CREATE DATABASE shopping
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_hungarian_ci;

USE shopping;

CREATE TABLE bevasarlas (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    mit VARCHAR(255) NOT NULL,
    mennyit DECIMAL(10,2) NULL,
    mertekegyseg VARCHAR(50) NULL,
    honnan VARCHAR(100) NULL,
    teljesult BOOLEAN NOT NULL DEFAULT FALSE,

    PRIMARY KEY (id)
);