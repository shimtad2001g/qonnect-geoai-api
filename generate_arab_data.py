import psycopg2
import random

DB_CONFIG = "postgresql://qonnect_geoai_db_user:2w0RTegkNaDNKDqlq5bgVTlUSmdVGjic@dpg-dbpa43142hec73c1toc0-a.virginia-postgres.render.com/qonnect_geoai_db"

def generate_arab_data():
    conn = psycopg2.connect(DB_CONFIG)
    cursor = conn.cursor()
    print("Connected. Generating Arabian Shield data...")
    
    base_lat, base_lon = 22.000, 44.000
    elements = ['Au', 'Cu']
    anomaly_lat, anomaly_lon = base_lat + 0.1, base_lon + 0.1

    for i in range(300):
        lat = base_lat + random.uniform(-0.3, 0.3)
        lon = base_lon + random.uniform(-0.3, 0.3)
        
        cursor.execute("""
            INSERT INTO field_samples (project_id, sample_type, location, sample_date, field_notes)
            VALUES (2, 'Rock', ST_SetSRID(ST_MakePoint(%s, %s), 4326), '2023-11-02', 'Arabian Shield Synthetic Data')
            RETURNING sample_id;
        """, (lon, lat))
        
        sample_id = cursor.fetchone()[0]
        element = random.choice(elements)
        
        dist = ((lat - anomaly_lat)**2 + (lon - anomaly_lon)**2)**0.5
        base_conc = random.uniform(0.1, 2.0)
        
        if element == 'Au':
            conc = base_conc * 10 if dist < 0.08 else base_conc
        else:
            conc = base_conc * 200 if dist < 0.12 else base_conc * 60
            
        cursor.execute("""
            INSERT INTO assay_results (sample_id, element_symbol, concentration, unit)
            VALUES (%s, %s, %s, 'ppm');
        """, (sample_id, element, round(conc, 2)))

    conn.commit()
    print("Successfully generated 300 Arabian Shield samples!")
    conn.close()

if __name__ == "__main__":
    generate_arab_data()
