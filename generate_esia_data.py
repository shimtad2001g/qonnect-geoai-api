import psycopg2
import random

DB_CONFIG = "postgresql://qonnect_geoai_db_user:2w0RTegkNaDNKDqlq5bgVTlUSmdVGjic@dpg-dbpa43142hec73c1toc0-a.virginia-postgres.render.com/qonnect_geoai_db"

def generate_esia_data():
    conn = psycopg2.connect(DB_CONFIG)
    cursor = conn.cursor()
    print("Connected. Generating ESIA Data...")
    
    # 1. Insert the new project
    cursor.execute("""
        INSERT INTO projects (project_id, project_name, use_case, client_name, objective) 
        VALUES (3, 'ESIA Pilot - Shimeles T. Zelelew', 'Environmental Monitoring', 'Global Development Partners', 'Environmental and Social Impact Assessment using GeoAI')
        ON CONFLICT (project_id) DO NOTHING;
    """)
    
    # Center of study area (Addis Ababa region)
    base_lat, base_lon = 9.030, 38.740
    # Environmental/Social indicators
    indicators = ['PM2.5', 'WaterQuality', 'NO2', 'Social_Impact']
    
    for i in range(200):
        lat = base_lat + random.uniform(-0.2, 0.2)
        lon = base_lon + random.uniform(-0.2, 0.2)
        
        cursor.execute("""
            INSERT INTO field_samples (project_id, sample_type, location, sample_date, field_notes)
            VALUES (3, 'Environmental', ST_SetSRID(ST_MakePoint(%s, %s), 4326), '2023-11-05', 'ESIA Synthetic Data')
            RETURNING sample_id;
        """, (lon, lat))
        
        sample_id = cursor.fetchone()[0]
        indicator = random.choice(indicators)
        
        # Simulate varying impact levels
        if indicator == 'PM2.5':
            val = random.uniform(10.0, 150.0)
        elif indicator == 'WaterQuality':
            val = random.uniform(5.0, 9.5) # pH scale
        elif indicator == 'NO2':
            val = random.uniform(5.0, 80.0)
        else:
            val = random.uniform(1.0, 10.0) # Social impact index
            
        cursor.execute("""
            INSERT INTO assay_results (sample_id, element_symbol, concentration, unit)
            VALUES (%s, %s, %s, 'index');
        """, (sample_id, indicator, round(val, 2)))

    conn.commit()
    print("Successfully generated 200 ESIA samples and added the project!")
    conn.close()

if __name__ == "__main__":
    generate_esia_data()
