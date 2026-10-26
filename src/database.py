import mysql.connector
import pandas as pd
from mysql.connector import Error
from src.config import DB_CONFIG


def get_connection(with_database=True):
    config = DB_CONFIG.copy()
    if not with_database:
        config.pop("database", None)
    return mysql.connector.connect(**config)


def init_db():
    conn = get_connection(with_database=False)
    try:
        cur = conn.cursor()
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cur.close()
    finally:
        conn.close()

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS regions (
                region_id INT AUTO_INCREMENT PRIMARY KEY,
                region_name VARCHAR(150) NOT NULL UNIQUE
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS crops (
                crop_id INT AUTO_INCREMENT PRIMARY KEY,
                crop_name VARCHAR(150) NOT NULL UNIQUE
            )
        """)
        cur.execute("""
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
                CONSTRAINT fk_record_crop FOREIGN KEY (crop_id) REFERENCES crops(crop_id),
                CONSTRAINT fk_record_region FOREIGN KEY (region_id) REFERENCES regions(region_id),
                INDEX idx_crop_year (crop_id, year),
                INDEX idx_region_year (region_id, year)
            )
        """)
        conn.commit()
        cur.close()
    finally:
        conn.close()


def _get_or_create_id(cursor, table, key_column, name):
    cursor.execute(f"SELECT {key_column} FROM {table} WHERE {table[:-1] + '_name'} = %s", (name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute(f"INSERT INTO {table} ({table[:-1] + '_name'}) VALUES (%s)", (name,))
    return cursor.lastrowid


def save_records(df):
    conn = get_connection()
    inserted = 0
    try:
        cur = conn.cursor()
        for _, row in df.iterrows():
            crop_id = _get_or_create_id(cur, "crops", "crop_id", str(row["crop"]).strip())
            region_id = _get_or_create_id(cur, "regions", "region_id", str(row["region"]).strip())
            def value_or_none(value):
                return None if pd.isna(value) else value
            cur.execute("""
                INSERT INTO crop_records
                (crop_id, region_id, year, cultivated_area, area_unit, production,
                 production_unit, rainfall, rainfall_unit)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                crop_id, region_id, int(row["year"]),
                value_or_none(row.get("cultivated_area")), str(row.get("area_unit", "unspecified")),
                value_or_none(row.get("production")), str(row.get("production_unit", "unspecified")),
                value_or_none(row.get("rainfall")), value_or_none(row.get("rainfall_unit", None))
            ))
            inserted += 1
        conn.commit()
        cur.close()
        return inserted
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def load_records():
    conn = get_connection()
    try:
        query = """
            SELECT cr.record_id, c.crop_name AS crop, r.region_name AS region, cr.year,
                   cr.cultivated_area, cr.area_unit, cr.production, cr.production_unit,
                   cr.rainfall, cr.rainfall_unit
            FROM crop_records cr
            JOIN crops c ON cr.crop_id = c.crop_id
            JOIN regions r ON cr.region_id = r.region_id
            ORDER BY cr.year, c.crop_name, r.region_name
        """
        return pd.read_sql(query, conn)
    finally:
        conn.close()
