import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from utils.functionsBDD import base_bd, conn

from utils import (
    page_Enedis, 
    page_GoveeH5179, 
    page_installation, 
    page_Meteo,
    page_parametres,
    traiter_donnees_Temperature_streamlit # a faire
)
# Vérifier que la variable est bien récupérée
if not base_bd:
    raise ValueError("⚠️ La variable NOM_BASE n'est pas définie dans .env !")

# Connexion SQLite
try:
    conn = sqlite3.connect(base_bd, check_same_thread=False)
    print(f"✅ Connexion réussie à la base de données : {base_bd}")
except sqlite3.Error as e:
    print(f"❌ Erreur lors de la connexion à la base de données : {e}")
    conn = None  # Assure que `conn` ne soit pas utilisée si la connexion échoue
cursor = conn.cursor()

st.sidebar.title("Navigation")

# --- Étape 1 : Sélection du menu principal ---
menu_principal = st.sidebar.radio("Sélectionnez :", 
                                  ["🏠 Paramétrages du Batiment", "🌍 Météo", "📊 Insertion de données externes", "🌡️ Températures"])

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
        page_GoveeH5179()
        #page_GDF() à faire et enlever l autre

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

