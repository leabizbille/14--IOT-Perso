import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from prometheus_client import start_http_server, Counter, REGISTRY


from utils import (
    page_Enedis, 
    page_Gaz,
    page_creation_compte,
    page_connexion,
    base_bd,
    page_GoveeH5179, 
    page_installation, 
    page_Meteo,
    page_parametres,
    get_connection, 
    creer_table_utilisateur,
    page_visualisation_Govee,
    traiter_donnees_Temperature_streamlit
)

# --- Connexion à la base de données ---
conn = get_connection()
if conn is None:
    st.error("❌ Connexion à la base de données échouée.")
    st.stop()
# Création de la table utilisateur si elle n'existe pas
creer_table_utilisateur(conn)
# --- Prometheus metrics ---
if '_prometheus_server_started' not in st.session_state:
    try:
        start_http_server(8001)
        st.session_state._prometheus_server_started = True
        print("Prometheus server started on port 8001.")
    except OSError as e:
        print(f"⚠️ Port 8001 occupé ? Détail : {e}")
if 'PAGE_SELECTIONS' not in st.session_state:
    try:
        # Vérifie si le compteur existe déjà dans le registre global
        REGISTRY.get_sample_value('page_selections_total')  # Renvoie None si inexistant
        st.session_state.PAGE_SELECTIONS = REGISTRY._names_to_collectors['page_selections_total']
    except KeyError:
        # Crée le compteur seulement s'il n'existe pas déjà
        st.session_state.PAGE_SELECTIONS = Counter(
            'page_selections_total', 
            'Total selections for each main menu page', 
            ['page_name']
        )

PAGE_SELECTIONS = st.session_state.PAGE_SELECTIONS

# --- Initialisation session utilisateur ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

# --- Connexion utilisateur ---
# Déterminer la page d'authentification à afficher
if not st.session_state.logged_in:
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.page == "login":
        page_connexion(conn)
    elif st.session_state.page == "register":
        page_creation_compte(conn)

    st.stop()  # Ne va pas plus loin tant qu'on n'est pas connecté

# --- Barre latérale après connexion ---
st.sidebar.title("Navigation")
st.sidebar.success(f"Connecté : {st.session_state.username} ({st.session_state.role})")

# --- Menu principal ---
menu_options = [
    "🏠 Paramétrages du Batiment", 
    "🌍 Météo", 
    "📊 Insertion de données externes", 
    "🌡️ Températures"
]
menu_principal = st.sidebar.radio("Sélectionnez :", menu_options)

# Compteur Prometheus
PAGE_SELECTIONS.labels(page_name=menu_principal).inc()

# --- Sous-menus selon sélection ---
if menu_principal == "🏠 Paramétrages du Batiment":
    menu_batiment = st.sidebar.selectbox("Gestion du bâtiment", 
                                         ["Paramètres du Bâtiment", "Paramètres des Pièces"])
    if menu_batiment == "Paramètres du Bâtiment":
        page_parametres()
    elif menu_batiment == "Paramètres des Pièces":
        page_installation()

elif menu_principal == "🌍 Météo":
    if st.sidebar.selectbox("☁️ Données météo", ["Données Météo"]) == "Données Météo":
        page_Meteo()

elif menu_principal == "📊 Insertion de données externes":
    menu_donnees = st.sidebar.selectbox("🔌 Données externes", ["Page Enedis", "Page GRDF"])
    if menu_donnees == "Page Enedis":
        page_Enedis()
    elif menu_donnees == "Page GRDF":
        page_Gaz()

elif menu_principal == "🌡️ Températures":
    menu_temperatures = st.sidebar.selectbox("📈 Températures des pièces", 
                                             ["GoveeWifi Temperature", "Visualisation des Temperatures"])
    if menu_temperatures == "GoveeWifi Temperature":
        page_GoveeH5179()
    elif menu_temperatures == "Visualisation des Temperatures":
        page_visualisation_Govee()

# --- Déconnexion ---
if st.sidebar.button("Se déconnecter"):
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

# --- Fermeture propre de la connexion ---
if conn:
    conn.close()
