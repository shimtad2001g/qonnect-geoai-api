from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Qonnect GeoAI Funder API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB_CONFIG = {"dbname": "qonnect_geoai_db", "user": "postgres", "password": "postgres", "host": "localhost", "port": "5432"}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    with open("templates/dashboard.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/geochemical-samples")
def get_samples():
    conn = get_db(); cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT sample_id, sample_type, ST_AsGeoJSON(location) as location_geojson, element_symbol, concentration FROM vw_geochemical_samples;")
    res = cur.fetchall(); cur.close(); conn.close(); return res

@app.get("/api/impact-scorecard")
def get_impact():
    conn = get_db(); cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM vw_impact_scorecard;")
    res = cur.fetchall(); cur.close(); conn.close(); return res
