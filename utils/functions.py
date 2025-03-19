import pandas as pd
import streamlit as st
from .functionsBDD import get_connection, get_existing_dates
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Fonction pour extraire le premier mot avant le premier underscore du nom du fichier
def extraire_piece(nom_fichier):
    try:
        # Vérifier que le nom du fichier contient le caractère de séparation '_'
        if '_' not in nom_fichier:
            raise ValueError(f"Le nom du fichier '{nom_fichier}' ne contient pas de caractère de séparation '_'.")

        # Extraire la partie avant le premier '_'
        piece = nom_fichier.split('_')[0]
        return piece
    except Exception as e:
        # Si une erreur survient, afficher un message d'erreur avec Streamlit
        st.error(f"❌ Erreur dans l'extraction de la pièce du fichier '{nom_fichier}': {e}")
        return None

# Fonction pour nettoyer la colonne "Piece" 
def nettoyer_Piece(data):
    try:
        # Vérifier si data est une chaîne de caractères
        if not isinstance(data, str):
            raise TypeError(f"Erreur : la donnée '{data}' n'est pas une chaîne de caractères.")

        # Supprimer les espaces au début et à la fin
        data = data.strip()

        # Appliquer les transformations de données
        if data.startswith('Emma'):
            return 'ChambreE'
        elif data == 'Salle à manger':
            return 'Salle_manger'
        elif data == 'Chambre':
            return 'ChambreP'
        elif data == 'Couloir Porte':
            return 'Entree'
        elif data == 'couloir':
            return 'CouloirRDC'
        else:
            return data  # Conserve les autres modalités intactes

    except Exception as e:
        # Afficher un message d'erreur via Streamlit si une exception est levée
        st.error(f"❌ Erreur dans le nettoyage de la donnée '{data}': {e}")
        return None

# importer fichier ENEDIS dans bdd.
def importer_csv_dans_bdd(uploaded_file, id_batiment):
    """Importe les données du CSV dans la table ConsoHeureElec en évitant les doublons."""
    if uploaded_file is not None:
        try:
            # Lire le fichier CSV en ignorant les 2 premières lignes
            df = pd.read_csv(uploaded_file, sep=";", skiprows=2)

            # Vérifier que les colonnes existent
            if "Horodate" in df.columns and "Valeur" in df.columns:
                # Sélectionner et renommer les colonnes
                df = df[["Horodate", "Valeur"]]
                df.columns = ["Horodatage", "ValeurW"]

                # Conversion de la colonne Horodatage au format datetime
                df['Horodatage'] = pd.to_datetime(df['Horodatage'], errors='coerce', utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")

                # Ajouter la colonne ID_Batiment
                df["ID_Batiment"] = id_batiment

                # Connexion à la base de données
                conn = get_connection()

                # Récupérer les dates déjà présentes en base
                existing_dates = get_existing_dates(conn, id_batiment)

                # Filtrer pour ne garder que les nouvelles données
                df_new = df[~df["Horodatage"].isin(existing_dates)]

                if df_new.empty:
                    st.warning("Toutes les données de ce fichier existent déjà en base. Rien à insérer.")
                else:
                    # Insérer uniquement les nouvelles données
                    df_new.to_sql("ConsoHeureElec", conn, if_exists="append", index=False)
                    st.success(f"{len(df_new)} nouvelles lignes insérées pour l'ID_Batiment {id_batiment}.")
                    st.write("Aperçu des nouvelles données importées :")
                    st.dataframe(df_new.head())

            else:
                st.error("Les colonnes 'Horodate' et 'Valeur' sont introuvables dans le fichier CSV.")

        except Exception as e:
            st.error(f"Erreur lors du traitement du fichier : {e}")

# Fonction pour afficher les graphiques
     
def afficher_graphique(df, period='jour'):
    # Grouper les données en fonction de la période choisie
    if period == 'année':
        df_grouped = df.groupby(df['Horodatage'].dt.year)['ValeurW'].sum()
    elif period == 'mois':
        df_grouped = df.groupby(df['Horodatage'].dt.to_period('M'))['ValeurW'].sum()
    elif period == 'jour':
        df_grouped = df.groupby(df['Horodatage'].dt.date)['ValeurW'].sum()
    elif period == 'heure':
        df_grouped = df.groupby(df['Horodatage'].dt.hour)['ValeurW'].sum()

    # Affichage du graphique
    plt.figure(figsize=(10, 6))
    df_grouped.plot(kind='bar', color='skyblue')
    plt.title(f"Consommation électrique par {period}", fontsize=16)
    plt.xlabel(f"Date ({period})", fontsize=12)
    plt.ylabel("Consommation en W", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)