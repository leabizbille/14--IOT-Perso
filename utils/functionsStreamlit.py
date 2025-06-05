import streamlit as st
import pandas as pd
import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from io import BytesIO
from dotenv import load_dotenv
import pymongo
from datetime import date

 # --------------------------------------------------------------
from utils.functionsmongo import (import_csv_to_gridfs, 
                                  download_files_from_gridfs,
                                  temperature_folder)
 # --------------------------------------------------------------
from utils import (
    importer_csv_dans_bdd, 
    traiter_donnees_Temperature_streamlit,
    creer_table_utilisateur,
    insert_user,
    creer_table_consoheure, 
    creer_table_city_info, 
    creer_table_batiment,
    creer_table_piece,
    recuperer_conso_data,
    recuperer_conso_dataGAZ,
    afficher_graphique,
    afficher_graphiqueGaz,
    get_connection,
    get_user,
    fig_to_bytes,
    check_password,
    creer_table_consoJour_GAZ,
    importer_csv_GAZ_bdd,
    inserer_donnees_temperature_piece,
    insert_user,
    get_Historical_weather_data
)

 # --------------------------------------------------------------

# Récupérer les variables d'environnement
base_bd = os.getenv("NOM_BASE")
url_Meteo = os.getenv("URL_METEO")
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME", "Documents")

 # --------------------------------------------------------------

# Données Mongo
client = pymongo.MongoClient(mongo_uri)
db = client[db_name]

 # --------------------------------------------------------------

pdf_folder = r"1-Documents\pdfs"
temperature_folder = r"1-Documents\Fichiers Temperature"
GRDF_folder = r"1-Documents\GRDF"

 # --------------------------------------------------------------
# Vérification du nom de la base
if not base_bd:
    raise ValueError("Erreur : la variable d'environnement NOM_BASE n'est pas définie.")

# Utiliser la fonction get_connection()
conn = get_connection()
if conn is None:
    raise ValueError("Erreur : impossible d'établir la connexion à la base de données.")

# ✅ Connexion réussie, on peut maintenant utiliser `conn`
cursor = conn.cursor()
 # --------------------------------------------------------------

 # --------------------------------------------------------------
  # ----------------------PAGES STREAMLIT----------------------------------------
   # --------------------------------------------------------------
# Page de connexion
def page_connexion(conn):
    # Initialisation session
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""

    if not st.session_state.logged_in:
        st.title("🔐 Connexion")

        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")

            if submit:
                user = get_user(conn, username)
                if user and check_password(password, user[1]):
                    st.session_state.logged_in = True
                    st.session_state.username = user[0]
                    st.session_state.role = user[2]
                    st.success("Connexion réussie 🎉")
                    st.rerun()

                else:
                    st.error("Identifiants invalides.")
    if st.button("Créer un compte"):
        st.session_state.page = "register"
        st.rerun()
    else:
        st.sidebar.success(f"Connecté en tant que : {st.session_state.username}")

        # Affichage conditionnel en fonction du rôle
        if st.session_state.role == "admin":
            st.title("👑 Tableau de bord")
            st.write(f"Bienvenue, {st.session_state.username} !")
        elif st.session_state.role == "user":
            st.title("👤 Mon Espace utilisateur")
            st.write(f"Bienvenue, {st.session_state.username} !")
        else:
            st.warning("")

        if st.sidebar.button("Se déconnecter"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.rerun()
def page_creation_compte(conn):
    st.title("🆕 Créer un compte")

    with st.form("register_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        confirm = st.text_input("Confirmer le mot de passe", type="password")
        role = st.selectbox("Rôle", ["user", "admin"])
        submit = st.form_submit_button("Continuer")

        if submit:
            if not username or not password:
                st.error("Tous les champs sont requis.")
            elif password != confirm:
                st.error("Les mots de passe ne correspondent pas.")
            else:
                # Stocke les données temporairement
                st.session_state.temp_user = {
                    "username": username,
                    "password": password,
                    "role": role
                }
                st.session_state.page = "rgpd"
                st.rerun()

    if st.button("⬅️ Retour à la connexion"):
        st.session_state.page = "login"
        st.rerun()


# --- Fonction : Page de gestion des bâtiments ---
def page_parametres():
    st.title("Configuration des bâtiments")

    username = st.session_state.username

    # Récupérer l'id de l'utilisateur à partir de son nom
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM utilisateur WHERE username = ?", (username,))
    user_row = cursor.fetchone()
    
    if user_row is None:
        st.error("Utilisateur introuvable.")
        return
    
    id_utilisateur = user_row[0]

    with st.form("chauffage_form"):
        ID_Batiment = st.text_input("Choisissez un nom pour votre bâtiment")
        ville = st.selectbox("Sélectionner la ville", options=['Tours', 'Trogues', 'Monts', 'Luz-Saint-Sauveur', 'Paris', 'Lyon', 'Marseille', 'Bordeaux', 'Toulouse', 'Nantes'])
        consigne_ete_jour = st.number_input("Consigne jour en été (°C)", min_value=0, max_value=50, value=23)
        consigne_ete_nuit = st.number_input("Consigne nuit en été (°C)", min_value=0, max_value=50, value=26)
        consigne_hiver_jour = st.number_input("Consigne jour en hiver (°C)", min_value=15, max_value=30, value=20)
        consigne_hiver_nuit = st.number_input("Consigne nuit en hiver (°C)", min_value=10, max_value=30, value=16)
        consigne_absence = st.number_input("Consigne absence plus de 2 jours (°C)", min_value=5, max_value=20, value=12)
        date_allumage = st.date_input("Date d'allumage du chauffage", value=datetime.today())
        date_arret = st.date_input("Date d'arrêt du chauffage", value=datetime.today())
        zone_academique = st.selectbox("Zone académique", options=["A", "B", "C"])
        type_batiment = st.selectbox("Type de bâtiment", options=["Maison", "Entreprise", "École", "Autre"])

        submit_button = st.form_submit_button("Soumettre")

        if submit_button:
            if ID_Batiment:
                # Insertion ou mise à jour du bâtiment
                cursor.execute("""
                    INSERT INTO Batiment (ID_Batiment, Ville, Consigne_Ete_Jour, Consigne_Ete_Nuit, 
                                        Consigne_Hiver_Jour, Consigne_Hiver_Nuit, Consigne_Absence, 
                                        Date_Allumage, Date_Arret, Zone_Academique, Type_Batiment, id_utilisateur)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(ID_Batiment) DO UPDATE SET 
                        Ville=excluded.Ville,
                        Consigne_Ete_Jour=excluded.Consigne_Ete_Jour,
                        Consigne_Ete_Nuit=excluded.Consigne_Ete_Nuit,
                        Consigne_Hiver_Jour=excluded.Consigne_Hiver_Jour,
                        Consigne_Hiver_Nuit=excluded.Consigne_Hiver_Nuit,
                        Consigne_Absence=excluded.Consigne_Absence,
                        Date_Allumage=excluded.Date_Allumage,
                        Date_Arret=excluded.Date_Arret,
                        Zone_Academique=excluded.Zone_Academique,
                        Type_Batiment=excluded.Type_Batiment,
                        id_utilisateur=excluded.id_utilisateur;
                """, (
                    ID_Batiment, ville, consigne_ete_jour, consigne_ete_nuit,
                    consigne_hiver_jour, consigne_hiver_nuit, consigne_absence,
                    date_allumage, date_arret, zone_academique, type_batiment, id_utilisateur
                ))

                # Ajouter l'entrée dans la table de liaison (utilisateur_batiment)
                cursor.execute("""
                    INSERT OR IGNORE INTO utilisateur_batiment (id_utilisateur, id_batiment)
                    VALUES (?, ?);
                """, (id_utilisateur, ID_Batiment))

                conn.commit()
                st.success(f"Bâtiment '{ID_Batiment}' ajouté/mis à jour et lié à l'utilisateur !")
            else:
                st.error("Veuillez entrer un nom pour le bâtiment.")

    # --- Affichage des bâtiments liés à l'utilisateur ---
    df_batiment = pd.read_sql_query("""
        SELECT b.* FROM Batiment b
        JOIN utilisateur_batiment ub ON b.ID_Batiment = ub.id_batiment
        WHERE ub.id_utilisateur = ?
    """, conn, params=(id_utilisateur,))
    
    st.subheader("Vos bâtiments enregistrés")
    st.dataframe(df_batiment)
def page_installation():
    st.title("Configuration des pièces")
    creer_table_piece(conn)
    # Récupérer la liste des bâtiments existants
    batiments = pd.read_sql("SELECT ID_Batiment FROM Batiment", conn)
    if batiments.empty:
        st.warning("Aucun bâtiment enregistré. Ajoutez-en un dans la section 'Paramètres de gestion'.")
        return

    selected_batiment = st.selectbox("Sélectionnez un bâtiment", batiments["ID_Batiment"].tolist())

    # Récupérer la liste des pièces associées au bâtiment sélectionné
    pieces = pd.read_sql("SELECT Piece FROM Piece WHERE ID_Batiment = ?", conn, params=(selected_batiment,))
    piece_names = ["Ajouter une nouvelle pièce"] + pieces["Piece"].tolist()
    selected_piece_name = st.selectbox("Sélectionnez une pièce à modifier ou ajoutez-en une nouvelle", piece_names)

    # Pré-remplissage des champs si une pièce existante est sélectionnée
    if selected_piece_name != "Ajouter une nouvelle pièce":
        piece_data = pd.read_sql("SELECT * FROM Piece WHERE Piece = ? AND ID_Batiment = ?", conn, params=(selected_piece_name, selected_batiment))
        piece_id = piece_data["Piece"].iloc[0]
        piece = piece_data["Piece"].iloc[0]
        surface = piece_data["Surface"].iloc[0]
        orientation = piece_data["Orientation"].iloc[0]
        chauffage_principal = piece_data["Chauffage_Principal"].iloc[0]
        chauffage_secondaire = piece_data["Chauffage_Secondaire"].iloc[0]
        etage = piece_data["Etage"].iloc[0]
        nbr_fenetre = piece_data["Nbr_Fenetre"].iloc[0]
        nbr_porte = piece_data["Nbr_Porte"].iloc[0]
        nbr_mur_facade = piece_data["Nbr_Mur_Facade"].iloc[0]
        is_new_piece = False
    else:
        piece_id = None
        piece = ""
        surface = 1
        orientation = "Nord"
        chauffage_principal = "Aucun"
        chauffage_secondaire = "Aucun"
        etage = 0
        nbr_fenetre = 0
        nbr_porte = 0
        nbr_mur_facade = 1
        is_new_piece = True

    # Formulaire d'ajout/modification
    with st.form("piece_form"):
        piece = st.text_input("Nom de la pièce", value=piece)
        surface = st.number_input("Surface (m²)", min_value=1, step=1, value=surface)
        orientation = st.selectbox("Orientation", ["Nord", "Sud", "Est", "Ouest", "Nord-Est", "Sud-Est", "Nord-Ouest", "Sud-Ouest"], index=["Nord", "Sud", "Est", "Ouest", "Nord-Est", "Sud-Est", "Nord-Ouest", "Sud-Ouest"].index(orientation))
        chauffage_principal = st.selectbox("Chauffage Principal", ["Gaz", "Electrique", "Cheminée", "Chauffage au sol", "Aucun"], index=["Gaz", "Electrique", "Cheminée", "Chauffage au sol", "Aucun"].index(chauffage_principal))
        chauffage_secondaire = st.selectbox("Chauffage Secondaire", ["Gaz", "Electrique", "Cheminée", "Chauffage au sol", "Aucun"], index=["Gaz", "Electrique", "Cheminée", "Chauffage au sol", "Aucun"].index(chauffage_secondaire))
        etage = st.number_input("Étage", min_value=0, step=1, value=etage)
        nbr_fenetre = st.number_input("Nombre de fenêtres", min_value=0, step=1, value=nbr_fenetre)
        nbr_porte = st.number_input("Nombre de porte exterieur", min_value=0, step=1, value=nbr_porte)
        nbr_mur_facade = st.number_input("Nombre de murs en façade", min_value=1, step=1, value=nbr_mur_facade)

        submitted = st.form_submit_button("Sauvegarder")

        if submitted:
            if piece:
                try:
                    if is_new_piece:
                        # Ajout d'une nouvelle pièce
                        cursor.execute("""
                            INSERT INTO Piece (Piece, Surface, Orientation, Chauffage_Principal, Chauffage_Secondaire, 
                                               Nbr_Fenetre, Nbr_Porte, Nbr_Mur_Facade, Etage, ID_Batiment)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (piece, surface, orientation, chauffage_principal, chauffage_secondaire, 
                              nbr_fenetre, nbr_porte, nbr_mur_facade, etage, selected_batiment))
                        conn.commit()
                        st.success(f"✅ Pièce '{piece}' ajoutée au bâtiment '{selected_batiment}' avec succès !")
                    else:
                        # Mise à jour d'une pièce existante
                        cursor.execute("""
                            UPDATE Piece
                            SET Piece = ?, Surface = ?, Orientation = ?, Chauffage_Principal = ?, Chauffage_Secondaire = ?, 
                                Nbr_Fenetre = ?, Nbr_Porte = ?, Nbr_Mur_Facade = ?, Etage = ?
                            WHERE Piece = ?
                        """, (piece, surface, orientation, chauffage_principal, chauffage_secondaire, 
                              nbr_fenetre, nbr_porte, nbr_mur_facade, etage, piece_id))
                        conn.commit()
                        st.success(f"✅ Pièce '{piece}' mise à jour avec succès !")

                except sqlite3.IntegrityError:
                    st.error("❌ Erreur : Cette pièce existe déjà !")
            else:
                st.error("Le nom de la pièce est obligatoire.")

    # --- Affichage des pièces enregistrées ---
    df_pieces = pd.read_sql("SELECT * FROM Piece", conn)
    st.subheader("📊 Pièces enregistrées")
    st.dataframe(df_pieces)

# --- Fonction : Page Météo ---
def page_Meteo():
    st.title("Téléchargement de la météo")
    creer_table_city_info(conn)
    
    # Récupérer la liste des villes existantes
    villes_df = pd.read_sql("SELECT DISTINCT ville FROM Batiment", conn)

    # Récupérer la liste des bâtiments existants
    selected_ville = st.selectbox("Sélectionnez une ville", villes_df["Ville"].tolist())
    if villes_df.empty:
        st.warning("Aucune ville enregistrée. Ajoutez-en une dans la section 'Paramètres de gestion'.")
        return
    
    # Récupérer le nombre de données météo déjà téléchargées pour la ville sélectionnée
    if selected_ville:
        count_query = """
        SELECT COUNT(*) 
        FROM weather
        WHERE ville = ?
        """
        count_df = pd.read_sql(count_query, conn, params=(selected_ville,))
        count = count_df.iloc[0, 0]  # Extraire la première valeur du DataFrame
        st.write(f"✅ Nombre de données météo déjà téléchargées pour '{selected_ville}': {count}")

    with st.form("meteo_form"):
        start_date = st.date_input("Date de début de l'historique de la météo :", value=datetime.today())
        end_date = st.date_input("Date de fin :", value=datetime.today())
        submitted = st.form_submit_button("Télécharger")
        
        if submitted:
            if selected_ville:
                try:
                    get_Historical_weather_data(selected_ville, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
                    st.success(f"✅ La météo pour '{selected_ville}' a été téléchargée avec succès !")
                except sqlite3.IntegrityError:
                    st.error("❌ Erreur : La météo de cette ville est déjà enregistrée pour cette période !")
                except Exception as e:
                    st.error(f"❌ Une erreur s'est produite : {e}")
            else:
                st.error("Le nom de la ville est obligatoire.")
    
    # --- Affichage des données météo enregistrées ---
    df_ville = pd.read_sql("SELECT * FROM city_info", conn)
    st.subheader(" Villes avec données météo enregistrées")
    st.dataframe(df_ville)

# --- Fonction : Page Insertion fichier Enedis
def page_Enedis():
    st.title("Sélection du bâtiment :")

    # Récupérer la liste des bâtiments existants
    batiments = pd.read_sql("SELECT ID_Batiment FROM Batiment", conn)
    if batiments.empty:
        st.warning("Aucun bâtiment enregistré. Ajoutez-en un dans la section 'Paramètres de gestion'.")
        return

    selected_batiment = st.selectbox("Sélectionnez un bâtiment", batiments["ID_Batiment"].tolist())

    st.subheader("Téléchargement des données par HEURE d'Enedis")
    
    # --- Image illustrative ---
    st.image("1-Documents/EnedisHeure.png", caption="Exemple de fichier attendu", use_container_width=True)

    # Vérifier si la table existe, sinon la créer
    creer_table_consoheure(conn)

    # Dépôt du fichier CSV
    uploaded_file = st.file_uploader("Déposez un fichier CSV", type=["csv"])

    if uploaded_file is not None:
        try:
            importer_csv_dans_bdd(uploaded_file, selected_batiment)
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")

        st.title("Graphique de Consommation Électrique")

    # Récupérer les données de consommation
    df = recuperer_conso_data(conn)

    st.subheader("Visualisation :")
    # Sélecteur de période
    period = st.selectbox("Choisissez la période", ["année", "mois", "jour", "heure"])
    
    # Affichage du graphique
    afficher_graphique(df, period)

# --- Fonction : Page Goovee
def page_GoveeH5179():
    st.title("Analyse des données Govee H5179")

    # Connexion à la base de données
    #conn = sqlite3.connect("MaBase.db")  # Chemin vers ta base de données

    st.subheader("Sélection du bâtiment")
    # Récupérer la liste des bâtiments existants
    try:
        batiments = pd.read_sql("SELECT ID_Batiment FROM Batiment", conn)
    except Exception as e:
        st.error(f"Erreur lors de la récupération des bâtiments : {e}")
        return

    if batiments.empty:
        st.warning("Aucun bâtiment enregistré. Ajoutez-en un dans la section 'Paramètres de gestion'.")
        return

    Id_Batiment = st.selectbox("Sélectionnez un bâtiment", batiments["ID_Batiment"].tolist())

    uploaded_files = st.file_uploader("Déposez un ou plusieurs fichiers CSV", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        chemin_sortie = "donnees_temperature"  # Dossier de stockage local
        df_resultat = traiter_donnees_Temperature_streamlit(uploaded_files, chemin_sortie)

        if df_resultat is not None:
            st.write("Aperçu des données combinées :", df_resultat.head())

            if inserer_donnees_temperature_piece(conn, df_resultat, Id_Batiment):
                st.success("✅ Données insérées avec succès dans la base de données.")
            else:
                st.error("❌ Une erreur est survenue lors de l'insertion des données.")

                        # Bouton de téléchargement
            csv = df_resultat.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger le fichier combiné",
                data=csv,
                file_name=f"donnees_combinees_Temperature_{datetime.now().strftime('%Y-%m-%d')}.csv",
                mime="text/csv"
            )  

            # 📤 Bouton – Upload vers MongoDB
            if st.button("📤 Envoyer les CSV dans MongoDB"):
                import_csv_to_gridfs(db, temperature_folder, collection_name="Govee")
                st.success("✅ CSV importés avec succès dans MongoDB !")

            # 📥 Bouton – Télécharger depuis MongoDB
            if st.button("📥 Récupérer les fichiers depuis MongoDB"):
                download_files_from_gridfs(db, temperature_folder, collection_name="Govee")
                st.success(f"✅ Fichiers récupérés dans le dossier : {chemin_sortie}")
# --- Fonction : Page GZ
def page_Gaz():
    st.title("Sélection du bâtiment :")

    # Récupérer la liste des bâtiments existants
    batiments = pd.read_sql("SELECT ID_Batiment FROM Batiment", conn)
    if batiments.empty:
        st.warning("Aucun bâtiment enregistré. Ajoutez-en un dans la section 'Paramètres de gestion'.")
        return

    selected_batiment = st.selectbox("Sélectionnez un bâtiment", batiments["ID_Batiment"].tolist())

    st.subheader("Téléchargement des données journalière de consommation de Gaz")
    
    # --- Image illustrative --- A changer
    st.image("1-Documents/GAZJour.png", caption="Exemple de fichier attendu", use_container_width=True) 

    # Vérifier si la table existe, sinon la créer
    creer_table_consoJour_GAZ(conn)

    # Dépôt du fichier CSV
    uploaded_file = st.file_uploader("Déposez un fichier CSV", type=["csv"])
    # Appeler la fonction pour afficher les 4 premières lignes

    if uploaded_file is not None:
        try:
            importer_csv_GAZ_bdd(uploaded_file, selected_batiment)
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")

        st.title("Graphique de Consommation de Gaz")

    # Récupérer les données de consommation
    df = recuperer_conso_dataGAZ(conn)
    
    st.subheader("Visualisation :")
    # Sélecteur de période
    period = st.selectbox("Choisissez la période", ["année", "mois", "jour"])
    
    # Affichage du graphique
    afficher_graphiqueGaz(df, period)

# PAGE APIimport streamlit as st
def page_API():
    st.title("API")
    st.info("Doc Swagger de l'API : http://127.0.0.1:8000/docs")

    BASE_URL = "http://127.0.0.1:8000"

    # Fonction pour interroger l’API FastAPI
    def get_data(endpoint):
        try:
            response = requests.get(f"{BASE_URL}/{endpoint}")
            response.raise_for_status()
            return response.json().get("donnees", [])
        except requests.exceptions.RequestException as e:
            st.error(f"Erreur lors de la récupération des données depuis '{endpoint}': {e}")
            return []

    try:
        # Interface avec onglets
        onglets = st.tabs(["🔥 Gaz", "⚡ Électricité", "🌡️ Température"])

        with onglets[0]:
            st.subheader("Consommation de gaz (jour)")
            data_gaz = get_data("DonneeGaz")
            if data_gaz:
                st.dataframe(data_gaz)
            else:
                st.info("Pas de données disponibles pour le gaz.")

        with onglets[1]:
            st.subheader("Consommation d'électricité (heure)")
            data_elec = get_data("DonneeElectricite")
            if data_elec:
                st.dataframe(data_elec)
            else:
                st.info("Pas de données disponibles pour l'électricité.")

        with onglets[2]:
            st.subheader("Températures intérieures")
            data_temp = get_data("TemperaturePiece")
            if data_temp:
                st.dataframe(data_temp)
            else:
                st.info("Pas de données disponibles pour la température.")

    except Exception as e:
        st.error(f"Une erreur est survenue dans l'affichage de la page API : {e}")

def page_rgpd(conn):
    st.title("🔒 Consentement RGPD")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div style='text-align: justify'>
        En créant un compte sur notre plateforme IoT, certaines données personnelles seront collectées.<br><br>
        Nous respectons le <strong>RGPD</strong> et la <strong>loi Informatique et Libertés</strong>.<br><br>
        Vos données (conso, température, formulaires bâtiments) servent uniquement à créer un modèle d’IA pour mieux gérer les consommations.  
        Elles ne sont partagées qu’avec les administrateurs, pour une durée de 1 an max.<br><br>
        Pour toute question : <a href='mailto:madame_x@gmail.com'>madame_x@gmail.com</a><br>
        🔗 <a href='https://www.cnil.fr' target='_blank'>Plus d'infos</a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        with st.form("rgpd_form"):
            today = st.date_input("Date", value=date.today())
            agree_1 = st.checkbox("✅ J’accepte l'utilisation de mes données.")
            agree_2 = st.checkbox("✅ Je consens au traitement automatisé.")
            submit = st.form_submit_button("Valider le consentement")

        if submit:
            if agree_1 and agree_2:
                # Récupère les infos temporaires
                user = st.session_state.get("temp_user", {})
                if user:
                    #from insert_logic import insert_user  # remplace selon ton architecture
                    success = insert_user(conn, user["username"], user["password"], user["role"])
                    if success:
                        st.success("🎉 Compte créé avec succès.")
                        st.session_state.page = "login"
                        st.rerun()
                    else:
                        st.error("Erreur lors de la création du compte.")
                        st.session_state.page = "creation"
                        st.rerun()
                else:
                    st.error("Erreur : informations utilisateur manquantes.")
            else:
                st.error("Vous devez accepter les deux conditions pour créer un compte.")












def fig_to_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf.getvalue()

def page_visualisation_Govee():
    st.title("Visualisation des Données H5179")

    # Connexion à la base de données
    conn = sqlite3.connect("MaBase.db")

    try:
        requete = """
            SELECT DISTINCT 
                strftime('%Y', Horodatage) AS annee,
                strftime('%m', Horodatage) AS mois,
                strftime('%d', Horodatage) AS jour
            FROM TemperaturePiece
        """
        date_info = pd.read_sql(requete, conn)
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return

    # Filtres temporels
    st.subheader("Filtrage temporel")
    annees = st.multiselect("Années", sorted(date_info["annee"].unique(), reverse=True))
    mois = st.multiselect("Mois", sorted(date_info["mois"].unique()))

    jours_disponibles = date_info
    if annees:
        jours_disponibles = jours_disponibles[jours_disponibles["annee"].isin(annees)]
    if mois:
        jours_disponibles = jours_disponibles[jours_disponibles["mois"].isin(mois)]

    jours = st.multiselect("Jours", sorted(jours_disponibles["jour"].unique()))

    # Filtre pièce
    st.subheader("Sélectionnez la pièce")
    try:
        pieces = pd.read_sql("SELECT DISTINCT Piece FROM TemperaturePiece", conn)
    except Exception as e:
        st.error(f"Erreur lors de la récupération des pièces : {e}")
        return

    selected_pieces = st.multiselect("Choisir la pièce", sorted(pieces["Piece"].unique()))

    # Type de données (1 seule pour affichage)
    type_donnee = st.selectbox("Type de donnée à afficher", ("Température_Celsius", "Humidité_Relative"))

    if st.button("Afficher les données"):
        filtres = []
        if annees:
            filtres.append(f"strftime('%Y', Horodatage) IN ({','.join(f'\"{a}\"' for a in annees)})")
        if mois:
            filtres.append(f"strftime('%m', Horodatage) IN ({','.join(f'\"{m}\"' for m in mois)})")
        if jours:
            filtres.append(f"strftime('%d', Horodatage) IN ({','.join(f'\"{j}\"' for j in jours)})")
        if selected_pieces:
            filtres.append(f"Piece IN ({','.join(f'\"{p}\"' for p in selected_pieces)})")

        requete_donnees = f"""
            SELECT * 
            FROM TemperaturePiece
            WHERE {' AND '.join(filtres)}
        """

        try:
            df = pd.read_sql(requete_donnees, conn)
        except Exception as e:
            st.error(f"Erreur lors de la récupération des données : {e}")
            return

        if df.empty:
            st.warning("Aucune donnée trouvée pour les critères sélectionnés.")
        else:
            st.write("Aperçu des données filtrées :")
            st.dataframe(df)

            # Visualisation
            st.subheader("Graphique de la donnée choisie")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.lineplot(data=df, x="Horodatage", y=type_donnee, hue="Piece", ax=ax)
            ax.set_title(f"{type_donnee} - Données agrégées")
            ax.set_xlabel("Horodatage")
            ax.set_ylabel("Valeur")
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # Télécharger le graphique
            st.download_button(
                label="Télécharger le graphique",
                data=fig_to_bytes(fig),
                file_name=f"{type_donnee}_graph.png",
                mime="image/png"
            )

def fig_to_bytes(fig):
    """Convertit un graphique Matplotlib en bytes pour le téléchargement."""
    from io import BytesIO
    img_bytes = BytesIO()
    fig.savefig(img_bytes, format="png")
    img_bytes.seek(0)
    return img_bytes.read()



