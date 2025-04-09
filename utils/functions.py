import pandas as pd
import streamlit as st
from .functionsBDD import get_connection, get_existing_dates, get_existing_datesGAZ


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

# importer fichier GAZ dans bdd.
def importer_csv_GAZ_bdd(uploaded_file, id_batiment):
    """Importe les données du fichier gaz dans la table ConsoJourGaz en évitant les doublons."""

    if uploaded_file is not None:
        try:
            # Détection encodage + lecture brute pour affichage
            #uploaded_file.seek(0)
            #content = uploaded_file.read().decode("latin1")
            #st.text("\n".join(content.splitlines()[:10]))

            # Rewind du fichier pour relecture
            #uploaded_file.seek(0)

            # Lecture du fichier CSV sans skiprows
            df = pd.read_csv(uploaded_file, sep=";", encoding="latin1", skiprows=2)

            # Vérification des colonnes
            expected_cols = ["Date de consommation", "Consommation (m3)", "Coefficient de conversion"]
            if not all(col in df.columns for col in expected_cols):
                st.error(f"Colonnes manquantes. Colonnes attendues : {expected_cols}")
                st.write("Colonnes trouvées :", df.columns.tolist())
                return None

            # Remplacement des virgules par des points pour les nombres
            df["Consommation (m3)"] = df["Consommation (m3)"].astype(str).str.replace(",", ".")
            df["Coefficient de conversion"] = df["Coefficient de conversion"].astype(str).str.replace(",", ".")

            # Conversion des colonnes
            df["Valeur_m3"] = pd.to_numeric(df["Consommation (m3)"], errors="coerce")
            df["Conversion"] = pd.to_numeric(df["Coefficient de conversion"], errors="coerce")

            # Conversion des dates
            df["Horodatage"] = pd.to_datetime(df["Date de consommation"], dayfirst=True, errors="coerce")
            df["Horodatage"] = df["Horodatage"].dt.normalize()  # Supprimer les heures

            # Ajout de l’ID bâtiment
            df["ID_Batiment"] = id_batiment

            # Nettoyage des colonnes finales
            df = df[["Horodatage", "Valeur_m3", "Conversion", "ID_Batiment"]]

            # Connexion BDD
            conn = get_connection()

            # Récupération des dates existantes
            existing_dates = get_existing_datesGAZ(conn, id_batiment)

            # Suppression des doublons
            df_new = df[~df["Horodatage"].isin(existing_dates)]

            if df_new.empty:
                st.warning("Toutes les données de ce fichier existent déjà en base. Rien à insérer.")
            else:
                df_new.to_sql("ConsoJourGaz", conn, if_exists="append", index=False)
                st.success(f"{len(df_new)} nouvelles lignes insérées pour l'ID_Batiment {id_batiment}.")
                st.write("Aperçu des nouvelles données importées :")
                st.dataframe(df_new.head())

        except Exception as e:
            st.error(f"Erreur lors du traitement du fichier : {e}")
