import pandas as pd
import psycopg2
from psycopg2 import sql
import sys

# Database Configuration (MUST MATCH your main.py password)
DB_CONFIG = {
    "dbname": "qonnect_geoai_db",
    "user": "postgres",
    "password": "postgres", # <--- UPDATE THIS
    "host": "localhost",
    "port": "5432"
}

def ingest_csv(file_path):
    print(f"Reading file: {file_path}")
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Connected to PostgreSQL successfully.")
    except Exception as e:
        print(f"Database connection failed: {e}")
        return

    success_count = 0
    error_count = 0

    for index, row in df.iterrows():
        try:
            # 1. Insert into field_samples (and return the generated sample_id)
            insert_sample_query = """
                INSERT INTO field_samples (project_id, sample_type, location, sample_date, field_notes)
                VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s)
                RETURNING sample_id;
            """
            # Assuming project_id = 1 (Al Madar Pilot) from our earlier setup
            cursor.execute(insert_sample_query, (
                1, 
                row['sample_type'], 
                row['longitude'], 
                row['latitude'], 
                row['sample_date'],
                f"Ingested from CSV Ref: {row['ref_id']}"
            ))
            
            new_sample_id = cursor.fetchone()[0]

            # 2. Insert into assay_results
            insert_assay_query = """
                INSERT INTO assay_results (sample_id, element_symbol, concentration, unit)
                VALUES (%s, %s, %s, %s);
            """
            cursor.execute(insert_assay_query, (
                new_sample_id, 
                row['element'], 
                row['concentration'], 
                row['unit']
            ))
            
            success_count += 1

        except Exception as e:
            print(f"Error on row {index}: {e}")
            conn.rollback()
            error_count += 1
            continue

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Ingestion Complete! Success: {success_count}, Errors: {error_count}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingest_data.py <path_to_csv>")
    else:
        ingest_csv(sys.argv[1])
