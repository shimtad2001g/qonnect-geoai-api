import psycopg2
import random
from psycopg2.extras import execute_values

DB_CONFIG = {
    "dbname": "qonnect_geoai_db",
    "user": "postgres",
    "password": "postgres", # <--- UPDATE THIS
    "host": "localhost",
    "port": "5432"
}

def generate_data():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Connected to database. Generating 500 samples...")
        
        # Center of Gamo Gofa
        base_lat, base_lon = 6.456, 37.123
        elements = ['Au', 'Cu', 'As', 'Zn', 'Pb']
        sample_types = ['Soil', 'Rock', 'Sediment']
        
        # Generate anomalies (hotspots)
        anomaly_lat, anomaly_lon = base_lat + 0.1, base_lon - 0.1

        for i in range(500):
            # Randomize location slightly
            lat = base_lat + random.uniform(-0.4, 0.4)
            lon = base_lon + random.uniform(-0.4, 0.4)
            
            sample_type = random.choice(sample_types)
            
            # Insert into field_samples
            cursor.execute("""
                INSERT INTO field_samples (project_id, sample_type, location, sample_date, field_notes)
                VALUES (1, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), '2023-11-01', 'Synthetic AI Test Data')
                RETURNING sample_id;
            """, (sample_type, lon, lat))
            
            sample_id = cursor.fetchone()[0]
            
            # Determine element and concentration
            element = random.choice(elements)
            
            # Create a "hotspot" effect around the anomaly coordinates
            dist_to_anomaly = ((lat - anomaly_lat)**2 + (lon - anomaly_lon)**2)**0.5
            base_conc = random.uniform(0.01, 2.0)
            
            if element == 'Au':
                conc = base_conc * 5 if dist_to_anomaly < 0.1 else base_conc
            elif element == 'Cu':
                conc = base_conc * 150 if dist_to_anomaly < 0.15 else base_conc * 50
            else:
                conc = base_conc * 10
                
            cursor.execute("""
                INSERT INTO assay_results (sample_id, element_symbol, concentration, unit)
                VALUES (%s, %s, %s, 'ppm');
            """, (sample_id, element, round(conc, 2)))

        conn.commit()
        print("Successfully generated and ingested 500 samples!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    generate_data()
