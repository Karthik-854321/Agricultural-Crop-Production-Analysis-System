CREATE DATABASE IF NOT EXISTS crop_analysis
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE crop_analysis;

CREATE TABLE IF NOT EXISTS regions (
  region_id INT AUTO_INCREMENT PRIMARY KEY,
  region_name VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS crops (
  crop_id INT AUTO_INCREMENT PRIMARY KEY,
  crop_name VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS crop_records (
  record_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  crop_id INT NOT NULL,
  region_id INT NOT NULL,
  year SMALLINT NOT NULL,
  cultivated_area DECIMAL(18,4) NULL,
  area_unit VARCHAR(40) NOT NULL,
  production DECIMAL(18,4) NULL,
  production_unit VARCHAR(40) NOT NULL,
  rainfall DECIMAL(12,4) NULL,
  rainfall_unit VARCHAR(40) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (crop_id) REFERENCES crops(crop_id),
  FOREIGN KEY (region_id) REFERENCES regions(region_id),
  INDEX idx_crop_year (crop_id, year),
  INDEX idx_region_year (region_id, year)
);
