from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import sqlite3
import os
from datetime import date

# --- Chargement des variables d’environnement ---
load_dotenv()
DB = os.getenv("NOM_BASE", "MaBase.db")
API_KEY = os.getenv("API_KEY")
#print(API_KEY)

# --- Initialisation de l’app ---
app = FastAPI(
    title="API IDOCS",
    description="Accès aux données de l'application : Infrastructure de Données pour l’Optimisation et la Centralisation d’un Système IoT.",
    version="1.0.2",
    openapi_tags=[
        {"name": "Gaz", "description": "Endpoints relatifs à la consommation de gaz"},
        {"name": "Électricité", "description": "Endpoints relatifs à la consommation d’électricité"},
        {"name": "Température", "description": "Endpoints relatifs à la température intérieure"},
    ],
)

# --- Système d'authentification Bearer ---
auth_scheme = HTTPBearer(auto_error=True)

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if credentials.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide"
        )
    return credentials.credentials

# --- Modèle de réponse standard ---
class DonneesReponse(BaseModel):
    donnees: List[Dict[str, Any]]

# --- Exemple route test ---
@app.get("/test", tags=["Test"])
def test_endpoint(token: str = Depends(verify_api_key)):
    return {"message": "Authentification réussie", "token_utilisé": token}

# --- Fonctions DB  ---
def fetch_data_from_db(table: str, where_clause: Optional[str] = None, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    query = f"SELECT * FROM {table}"
    if where_clause:
        query += f" WHERE {where_clause}"
    cur.execute(query, params or [])
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def fetch_filtered_temperature(
    start_date: Optional[str],
    end_date: Optional[str],
    piece: Optional[str],
    limit: int = 200,
    offset: int = 0,
    order_by: str = "Horodatage",
    order_dir: str = "asc"
) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    allowed_order_by = {"Horodatage", "piece", "valeur"}
    allowed_order_dir = {"asc", "desc"}

    if order_by not in allowed_order_by:
        raise ValueError(f"Colonne de tri non autorisée : {order_by}")
    if order_dir.lower() not in allowed_order_dir:
        raise ValueError(f"Direction de tri non autorisée : {order_dir}")

    query = "SELECT * FROM TemperaturePiece WHERE 1=1"
    params = []

    if start_date:
        query += " AND Horodatage >= ?"
        params.append(start_date)
    if end_date:
        query += " AND Horodatage <= ?"
        params.append(end_date)
    if piece:
        query += " AND piece = ?"
        params.append(piece)

    query += f" ORDER BY {order_by} {order_dir.upper()} LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def fetch_filtered_electricite(
    start_date: Optional[str],
    end_date: Optional[str],
    limit: int = 100,
    offset: int = 0,
    order_by: str = "Horodatage",
    order_dir: str = "asc"
) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Colonnes autorisées pour le tri, à adapter selon ta table ConsoHeureElec
    allowed_order_by = {"Horodatage", "valeur", "ID_Batiment"}
    allowed_order_dir = {"asc", "desc"}

    if order_by not in allowed_order_by:
        raise ValueError(f"Colonne de tri non autorisée : {order_by}")
    if order_dir.lower() not in allowed_order_dir:
        raise ValueError(f"Direction de tri non autorisée : {order_dir}")

    query = "SELECT * FROM ConsoHeureElec WHERE 1=1"
    params = []

    if start_date:
        query += " AND Horodatage >= ?"
        params.append(start_date)
    if end_date:
        query += " AND Horodatage <= ?"
        params.append(end_date)

    query += f" ORDER BY {order_by} {order_dir.upper()} LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --- Routes endpoints protégés par token ---
@app.get("/gaz/", response_model=DonneesReponse, tags=["Gaz"], summary="Consommation journalière de gaz")
def get_gaz(
    date_debut: Optional[date] = Query(None, description="Date de début (inclus)", example="2025-01-01"),
    date_fin: Optional[date] = Query(None, description="Date de fin (inclus)", example="2025-01-31"),
    token: str = Depends(verify_api_key)
):
    if date_debut and date_fin and date_debut > date_fin:
        raise HTTPException(status_code=400, detail="`date_debut` doit être antérieure à `date_fin`")
    conditions, params = [], []
    if date_debut:
        conditions.append("Horodatage >= ?")
        params.append(str(date_debut))
    if date_fin:
        conditions.append("Horodatage <= ?")
        params.append(str(date_fin))
    where_clause = " AND ".join(conditions) if conditions else None
    data = fetch_data_from_db("ConsoJourGaz", where_clause, params)
    return {"donnees": data}

@app.get("/temperature",response_model=DonneesReponse, tags=["Température"], summary="Température des pièces (filtrable)"
)
def get_temperature_simple(
    date_debut: Optional[date] = Query(None, description="Date de début (inclus)", example="2025-01-01"),
    date_fin: Optional[date] = Query(None, description="Date de fin (inclus)", example="2025-01-31"),
    piece: Optional[str] = Query(None, description="Nom de la pièce (ex: Salon, Chambre)", example="Salon"),
    token: str = Depends(verify_api_key)
):
    conditions = []
    params = []

    if date_debut:
        conditions.append("Horodatage >= ?")
        params.append(str(date_debut))
    if date_fin:
        conditions.append("Horodatage <= ?")
        params.append(str(date_fin))
    if piece:
        conditions.append("piece = ?")
        params.append(piece)

    where_clause = " AND ".join(conditions) if conditions else None
    data = fetch_data_from_db("TemperaturePiece", where_clause, params)
    return {"donnees": data}

@app.get("/TemperaturePiece", response_model=DonneesReponse, tags=["Température"], summary="Température des pièces (filtrable, triable, paginable)"
)
def get_temperature_piece(
    start_date: Optional[date] = Query(None, description="Date de début (inclus) au format YYYY-MM-DD"),
    end_date: Optional[date] = Query(None, description="Date de fin (inclus) au format YYYY-MM-DD"),
    piece: Optional[str] = Query(None, description="Nom de la pièce (ex: Salon, Chambre)"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre max de résultats"),
    offset: int = Query(0, ge=0, description="Décalage pour la pagination"),
    order_by: str = Query("Horodatage", description="Colonne de tri (Horodatage, piece, valeur)"),
    order_dir: str = Query("asc", description="Ordre de tri : asc ou desc"),
    token: str = Depends(verify_api_key)
):
    try:
        # Convertir date en str isoformat pour sqlite
        s_date = start_date.isoformat() if start_date else None
        e_date = end_date.isoformat() if end_date else None

        data = fetch_filtered_temperature(
            s_date, e_date, piece, limit, offset, order_by, order_dir
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"donnees": data}

@app.get(
    "/electricite",
    response_model=DonneesReponse,
    tags=["Électricité"],
    summary="Consommation horaire d’électricité (filtrable, triable, paginable)"
)
def get_electricite(
    start_date: Optional[str] = Query(None, description="Date de début au format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Date de fin au format YYYY-MM-DD"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre max de résultats"),
    offset: int = Query(0, ge=0, description="Décalage pour la pagination"),
    order_by: str = Query("Horodatage", description="Colonne de tri (Horodatage, valeur, ID_Batiment)"),
    order_dir: str = Query("asc", description="Ordre de tri : asc ou desc"),
    token: str = Depends(verify_api_key)
):
    """
    Récupère les données de consommation d’électricité avec filtres, tri et pagination.

    🔹 Colonnes triables : `Horodatage`, `valeur`, `ID_Batiment`  
    🔹 Ordre : `asc` (croissant) ou `desc` (décroissant)
    """
    try:
        data = fetch_filtered_electricite(start_date, end_date, limit, offset, order_by, order_dir)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"donnees": data}
