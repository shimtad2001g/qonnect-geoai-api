from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import secrets

app = FastAPI(title="Qonnect GeoAI Secure API")

# Security Setup
security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "almadar")
    correct_password = secrets.compare_digest(credentials.password, "geoai2024")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:your_password@localhost:5432/qonnect_geoai_db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

def get_db():
    return psycopg2.connect(DATABASE_URL)

# Add the dependency to require login for ALL routes
@app.get("/", response_class=HTMLResponse, dependencies=[Depends(verify_credentials)])
def serve_dashboard():
    with open("templates/dashboard.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/projects", dependencies=[Depends(verify_credentials)])
def get_projects():
    conn = get_db(); cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT project_id, project_name FROM projects;")
    res = cur.fetchall(); cur.close(); conn.close(); return res

@app.get("/api/geochemical-samples", dependencies=[Depends(verify_credentials)])
def get_samples(project_id: int = 1):
    conn = get_db(); cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT fs.sample_id, fs.sample_type, ST_AsGeoJSON(fs.location) as location_geojson, ar.element_symbol, ar.concentration 
        FROM field_samples fs 
        JOIN assay_results ar ON fs.sample_id = ar.sample_id 
        WHERE fs.project_id = %s;
    """, (project_id,))
    res = cur.fetchall(); cur.close(); conn.close(); return res

@app.get("/api/impact-scorecard", dependencies=[Depends(verify_credentials)])
def get_impact():
    conn = get_db(); cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM vw_impact_scorecard;")
    res = cur.fetchall(); cur.close(); conn.close(); return res
