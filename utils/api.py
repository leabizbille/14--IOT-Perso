# Importation des packages nécessaires
from fastapi import FastAPI
import sqlite3  # Pour interagir avec une base de données SQLite
from dotenv import load_dotenv  # Pour charger les variables d'environnement depuis le fichier .env
import os  # Pour accéder aux variables d'environnement du système

# uvicorn utils.api:app --reload --port 8000

# Charger les variables d'environnement
load_dotenv()
# Récupérer le nom de la base de données depuis le fichier .env
base_bd = os.getenv("NOM_BASE", "MaBase.db")

# Initialiser l'application FastAPI
app = FastAPI()

# Définir un point d'API GET accessible à l'adresse http://localhost:8000/DonneeGaz
@app.get("/DonneeGaz")
def read_data():
    # Se connecter à la base de données SQLite
    conn = sqlite3.connect(base_bd)
    cursor = conn.cursor()
    # Exécuter une requête SQL pour récupérer toutes les données de la table 'ConsoJourGaz'
    cursor.execute("SELECT * FROM ConsoJourGaz") 
    # Récupérer les résultats de la requête
    data = cursor.fetchall()
    # Fermer la connexion à la base
    conn.close()
    # Retourner les données dans une réponse JSON
    return {"donnees": data}

# Définir un point d'API GET accessible à l'adresse http://localhost:8000/DonneeElectricite
@app.get("/DonneeElectricite")
def read_data():
    # Se connecter à la base de données SQLite
    conn = sqlite3.connect(base_bd)
    cursor = conn.cursor()
    # Exécuter une requête SQL pour récupérer toutes les données de la table 'ConsoJourGaz'
    cursor.execute("SELECT * FROM ConsoHeureElec") 
    # Récupérer les résultats de la requête
    data = cursor.fetchall()
    # Fermer la connexion à la base
    conn.close()
    # Retourner les données dans une réponse JSON
    return {"donnees": data}

# Définir un point d'API GET accessible à l'adresse http://localhost:8000/DonneeElectricite
@app.get("/TemperaturePiece")
def read_data():
    # Se connecter à la base de données SQLite
    conn = sqlite3.connect(base_bd)
    cursor = conn.cursor()
    # Exécuter une requête SQL pour récupérer toutes les données de la table 
    cursor.execute("SELECT * FROM TemperaturePiece") 
    # Récupérer les résultats de la requête
    data = cursor.fetchall()
    # Fermer la connexion à la base
    conn.close()
    # Retourner les données dans une réponse JSON
    return {"donnees": data}