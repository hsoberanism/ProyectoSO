CREATE DATABASE IF NOT EXISTS banco_db;

USE banco_db;

CREATE TABLE IF NOT EXISTS banco (
    id INT AUTO_INCREMENT PRIMARY KEY,

    cuenta VARCHAR(20) NOT NULL,

    tipo ENUM('MONETARIA', 'AHORRO') NOT NULL,

    monto DECIMAL(12,2) NOT NULL,

    moneda CHAR(3) NOT NULL DEFAULT 'GTQ',

    estado ENUM('PENDIENTE', 'PROCESADO')
        NOT NULL DEFAULT 'PENDIENTE',

    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    procesado_en TIMESTAMP NULL,

    procesado_por VARCHAR(10) NULL,

    INDEX idx_estado_fecha (estado, creado_en, id)
) ENGINE=InnoDB;