import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from prometheus_client import start_http_server, Counter
import threading
import time

from utils import (
    page_Enedis, 
    page_Gaz,
    page_connexion,
    base_bd,
    page_GoveeH5179, 
    page_installation, 
    page_Meteo,
    page_parametres,
    get_connection, 
    traiter_donnees_Temperature_streamlit # a faire
)

# Connexion à la base de données
conn = get_connection()

if conn is None:
    raise ValueError("La connexion à la base de données a échoué. Impossible de continuer.")

# Si la connexion est réussie, tu peux maintenant créer le curseur
cursor = conn.cursor()

# --- Prometheus Metrics Setup ---
# Start Prometheus metrics server in a separate thread
# Check if the server is already running to avoid issues with Streamlit's hot-reloading
if '_prometheus_server_started' not in st.session_state:
    try:
        start_http_server(8001)
        st.session_state._prometheus_server_started = True
        print("Prometheus metrics server started on port 8001")
    except OSError as e:
        # Handle cases where the port might already be in use (e.g., during dev reloads)
        print(f"Prometheus server already running or port 8001 busy? Error: {e}")
        # Optionally, decide if this is critical or can be ignored in dev
        pass # Or raise an error if needed

    # Define metrics only if not already defined in the session state
    if 'PAGE_SELECTIONS' not in st.session_state:
        st.session_state.PAGE_SELECTIONS = Counter('page_selections_total', 'Total selections for each main menu page', ['page_name'])
        print("Prometheus Counter 'page_selections_total' defined.")

# Use the metric from session state
PAGE_SELECTIONS = st.session_state.PAGE_SELECTIONS


st.sidebar.title("Navigation")

# --- Étape 1 : Sélection du menu principal ---
menu_options = ["🏠 Paramétrages du Batiment", "🌍 Météo", "📊 Insertion de données externes", "🌡️ Températures"]
menu_principal = st.sidebar.radio("Sélectionnez :", menu_options)

# Increment Prometheus counter based on selection
if menu_principal:
    PAGE_SELECTIONS.labels(page_name=menu_principal).inc()

# --- Étape 2 : Sélection des sous-menus selon la catégorie choisie ---
if menu_principal == "🏠 Paramétrages du Batiment":
    menu_batiment = st.sidebar.selectbox("Gestion du bâtiment", 
                                         ["Paramètres du Bâtiment", "Paramètres des Pièces"])

    if menu_batiment == "Paramètres du Bâtiment":
        page_parametres()
    elif menu_batiment == "Paramètres des Pièces":
        page_installation()

elif menu_principal == "🌍 Météo":
    menu_meteo = st.sidebar.selectbox("☁️ Données météo", ["Données Météo"])
    
    if menu_meteo == "Données Météo":
        page_Meteo()

elif menu_principal == "📊 Insertion de données externes":
    menu_donnees = st.sidebar.selectbox("🔌 Données externes", 
                                        ["Page Enedis", "Page GDF"])

    if menu_donnees == "Page Enedis":
        page_Enedis()
    elif menu_donnees == "Page GDF":
        page_Gaz()

elif menu_principal == "🌡️ Températures":
    menu_temperatures = st.sidebar.selectbox("📈 Températures des pièces" ,
                                             ["GoveeWifi Temperature", "GoveeBluetooth Temperature"])
    if menu_temperatures =="GoveeWifi Temperature":
        page_GoveeH5179()
    elif menu_temperatures == "GoveeBluetooth Temperature":
        page_GoveeH5179()
        #page_GoveeBT() à faire et enlever l autre


# --- Fermeture propre de la connexion ---
if 'conn' in globals() and conn:
    conn.close()
