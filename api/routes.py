from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, List, Dict, Any
from datetime import date
from pydantic import BaseModel
from utils.functionsBDD import (
    fetch_data_from_db,
    fetch_filtered_temperature,
    fetch_filtered_electricite,
    get_db,
    get_user_from_db
)
from dotenv import load_dotenv
import os

# Chargement des variables d'environnement
load_dotenv()
base_bd = os.getenv("NOM_BASE", "MaBase.db")

router = APIRouter()


# Modèle de réponse commun
class DonneesReponse(BaseModel):
    donnees: List[Dict[str, Any]]


# 🔐 Authentification utilisateur
@router.post("/login", tags=["Authentification"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    conn=Depends(get_db)
):
    user = get_user_from_db(conn, form_data.username)  
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")

    # 👉 Ici : Vérifier le mot de passe hashé 

    return {"message": "Connexion réussie", "utilisateur": user["username"]}


# 🔧 Route pour les données de gaz
@router.get("/gaz", response_model=DonneesReponse, tags=["Gaz"])
def get_gaz(
    date_debut: Optional[date] = Query(None),
    date_fin: Optional[date] = Query(None),
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


# 🌡️ Température simplifiée
@router.get("/temperature", response_model=DonneesReponse, tags=["Température"])
def get_temperature_simple(
    date_debut: Optional[date] = Query(None, description="Date de début (inclus)", examples={"value": "2025-01-01"}),
    date_fin: Optional[date] = Query(None, description="Date de fin (inclus)", examples={"value": "2025-01-01"}),
    piece: Optional[str] = Query(None),
):
    conditions, params = [], []
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


# 🌡️ Température filtrée et paginée
@router.get("/TemperaturePiece", response_model=DonneesReponse, tags=["Température"])
def get_temperature_piece(
    start_date: Optional[date] = Query(None, description="Date de début (inclus)", examples={"value": "2025-01-01"}),
    end_date: Optional[date] = Query(None, description="Date de fin (inclus)", examples={"value": "2025-01-01"}),
    piece: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    order_by: str = Query("Horodatage"),
    order_dir: str = Query("asc")
):
    try:
        s_date = start_date.isoformat() if start_date else None
        e_date = end_date.isoformat() if end_date else None
        data = fetch_filtered_temperature(s_date, e_date, piece, limit, offset, order_by, order_dir)
        return {"donnees": data}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ⚡ Électricité filtrée et paginée
@router.get("/electricite", response_model=DonneesReponse, tags=["Électricité"])
def get_electricite(
    start_date: Optional[date] = Query(None, description="Date de début (inclus)", examples={"value": "2025-01-01"}),
    end_date: Optional[date] = Query(None, description="Date de fin (inclus)", examples={"value": "2025-01-01"}),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    order_by: str = Query("Horodatage"),
    order_dir: str = Query("asc")
):
    try:
        data = fetch_filtered_electricite(start_date, end_date, limit, offset, order_by, order_dir)
        return {"donnees": data}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
