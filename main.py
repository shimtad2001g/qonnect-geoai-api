from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = FastAPI(title="Qonnect GeoAI Funder API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:your_password@localhost:5432/qonnect_geoai_db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_db():
    return psycopg2.connect(DATABASE_URL)

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    with open("templates/dashboard.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/projects")
def get_projects():
    conn = get_db(); cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT project_id, project_name FROM projects;")
    res = cur.fetchall(); cur.close(); conn.close(); return res

@app.get("/api/geochemical-samples")
def get_samples(project_id: int = 1):
    conn = get_db(); cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT fs.sample_id, fs.sample_type, ST_AsGeoJSON(fs.location) as location_geojson, ar.element_symbol, ar.concentration 
        FROM field_samples fs 
        JOIN assay_results ar ON fs.sample_id = ar.sample_id 
        WHERE fs.project_id = %s;
    """, (project_id,))
    res = cur.fetchall(); cur.close(); conn.close(); return res

@app.get("/api/impact-scorecard")
def get_impact():
    conn = get_db(); cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM vw_impact_scorecard;")
    res = cur.fetchall(); cur.close(); conn.close(); return res
