import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from utils import (
    importer_csv_dans_bdd, 
    traiter_donnees_Temperature_streamlit,
    creer_table_weather, 
    insert_weather_data, 
    creer_table_consoheure, 
    get_connection, 
    creer_table_city_info, 
    creer_table_batiment,
    creer_table_piece,
    get_Historical_weather_data
)

# Connexion à la base de données
conn = get_connection()
cursor = conn.cursor()

# Création de la table si elle n'existe pas
creer_table_consoheure(conn)
creer_table_city_info(conn)
creer_table_batiment(conn)
creer_table_piece(conn)

# --- Fonction : Page de gestion des bâtiments ---
def page_parametres():
    st.title("Paramètres de gestion des bâtiments")

    with st.form("chauffage_form"):
        ID_Batiment = st.text_input("Choisissez un nom pour votre bâtiment")
        ville = st.selectbox("Sélectionner la ville", options=['Tours', 'Trogues','Monts', 'Luz-Saint-Sauveur', 'Paris', 'Lyon', 'Marseille', 'Bordeaux', 'Toulouse', 'Nantes'])
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
                cursor.execute("""
                    INSERT INTO Batiment (ID_Batiment, Ville, Consigne_Ete_Jour, Consigne_Ete_Nuit, 
                                         Consigne_Hiver_Jour, Consigne_Hiver_Nuit, Consigne_Absence, 
                                         Date_Allumage, Date_Arret, Zone_Academique, Type_Batiment)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    Type_Batiment=excluded.Type_Batiment;
                """, (ID_Batiment, ville, consigne_ete_jour, consigne_ete_nuit, consigne_hiver_jour, 
                      consigne_hiver_nuit, consigne_absence, date_allumage, date_arret, zone_academique, type_batiment))
                conn.commit()
                st.success(f"Bâtiment '{ID_Batiment}' ajouté/mis à jour avec succès !")
            else:
                st.error("Veuillez entrer un nom pour le bâtiment.")

    # --- Affichage des bâtiments enregistrés ---
    df_batiment = pd.read_sql("SELECT * FROM Batiment", conn)
    st.subheader("Bâtiments enregistrés")
    st.dataframe(df_batiment)


# --- Fonction : Page d'installation des pièces ---
def page_installation():
    st.title("Installation des pièces")

    # Récupérer la liste des bâtiments existants
    batiments = pd.read_sql("SELECT ID_Batiment FROM Batiment", conn)
    if batiments.empty:
        st.warning("Aucun bâtiment enregistré. Ajoutez-en un dans la section 'Paramètres de gestion'.")
        return

    selected_batiment = st.selectbox("Sélectionnez un bâtiment", batiments["ID_Batiment"].tolist())

    with st.form("piece_form"):
        piece = st.text_input("Nom de la pièce")
        surface = st.number_input("Surface (m²)", min_value=1, step=1)
        orientation = st.selectbox("Orientation", ["Nord", "Sud", "Est", "Ouest", "Nord-Est", "Sud-Est", "Nord-Ouest", "Sud-Ouest"])
        chauffage_principal = st.selectbox("Chauffage Principal", ["Gaz", "Electrique", "Cheminée", "Chauffage au sol", "Aucun"])
        chauffage_secondaire = st.selectbox("Chauffage Secondaire", ["Gaz", "Electrique", "Cheminée", "Chauffage au sol", "Aucun"])
        etage = st.number_input("Étage", min_value=0, step=1)
        nbr_fenetre = st.number_input("Nombre de fenêtres", min_value=0, step=1)
        nbr_porte = st.number_input("Nombre de portes", min_value=0, step=1)
        nbr_mur_facade = st.number_input("Nombre de murs en façade", min_value=1, step=1)
        submitted = st.form_submit_button("Ajouter")

        if submitted:
            if piece:
                try:
                    cursor.execute("""
                        INSERT INTO Piece (Piece, Surface, Orientation, Chauffage_Principal, Chauffage_Secondaire, 
                                           Nbr_Fenetre, Nbr_Porte, Nbr_Mur_Facade, Etage, ID_Batiment)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (piece, surface, orientation, chauffage_principal, chauffage_secondaire, 
                          nbr_fenetre, nbr_porte, nbr_mur_facade, etage, selected_batiment))
                    conn.commit()
                    st.success(f"✅ Pièce '{piece}' ajoutée au bâtiment '{selected_batiment}' avec succès !")
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

    # Récupérer la liste des villes existantes
    villes_df = pd.read_sql("SELECT DISTINCT ville FROM Batiment", conn)

    # Récupérer la liste des bâtiments existants
    selected_ville = st.selectbox("Sélectionnez une ville", villes_df["Ville"].tolist())
    if villes_df.empty:
        st.warning("Aucune ville enregistrée. Ajoutez-en une dans la section 'Paramètres de gestion'.")
        return
    
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
    st.subheader("Sélection du bâtiment :")

    # Récupérer la liste des bâtiments existants
    batiments = pd.read_sql("SELECT ID_Batiment FROM Batiment", conn)
    if batiments.empty:
        st.warning("Aucun bâtiment enregistré. Ajoutez-en un dans la section 'Paramètres de gestion'.")
        return

    selected_batiment = st.selectbox("Sélectionnez un bâtiment", batiments["ID_Batiment"].tolist())

    st.title("Téléchargement des données d'Enedis")
    st.subheader("Conso Heure")

    # Vérifier si la table existe, sinon la créer
    creer_table_consoheure()

    # Dépôt du fichier CSV
    uploaded_file = st.file_uploader("Déposez un fichier CSV", type=["csv"])

    if uploaded_file is not None:
        try:
            importer_csv_dans_bdd(uploaded_file, selected_batiment)
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")


# --- Fonction : Page Goovee
def page_GoveeH5179():
    st.title("Analyse des données Govee H5179")
    uploaded_files = st.file_uploader("Déposez un ou plusieurs fichiers CSV", type=["csv"], accept_multiple_files=True)

    if uploaded_files:
        chemin_sortie = "donnees_temperature"  # Dossier de stockage en local
        df_resultat = traiter_donnees_Temperature_streamlit(uploaded_files, chemin_sortie)

        if df_resultat is not None:
            st.write("Aperçu des données combinées :", df_resultat.head())

            # Ajouter un bouton de téléchargement
            csv = df_resultat.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger le fichier combiné",
                data=csv,
                file_name=f"donnees_combinees_Temperature_{datetime.now().strftime('%Y-%m-%d')}.csv",
                mime="text/csv"
            )






# --- Navigation dans l'application ---
st.sidebar.title("1.Navigation")
page = st.sidebar.radio("Aller à", ["Paramètres du Batiment", "Installation", "Ville avec données Météo","Page Enedis","GoveeWifi"])

if page == "Installation":
    page_installation()
if page == "Paramètres du Batiment":
    page_parametres()   
if page == "Ville avec données Météo":
    page_Meteo()
if page == "Page Enedis":
    page_Enedis()
elif page == "GoveeWifi":
    page_GoveeH5179()

st.sidebar.title("2.")
# Fermeture de la connexion
conn.close()










