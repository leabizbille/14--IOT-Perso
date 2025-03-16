import os
import pandas as pd
import streamlit as st
from datetime import datetime
from .functions import nettoyer_Piece, extraire_piece
from dotenv import load_dotenv
import os

load_dotenv()
chemin_sortie = os.getenv("CHEMIN_SORTIE_FICHIER_TEMPERATURE")


def traiter_donnees_Temperature_streamlit(uploaded_files, chemin_sortie):
    if not uploaded_files:
        st.error("❌ Aucun fichier CSV chargé.")
        return None  

    if not os.path.exists(chemin_sortie):
        os.makedirs(chemin_sortie)
        st.write(f"📁 Dossier '{chemin_sortie}' créé pour stocker les fichiers triés.")

    list_dfs = []  
    nb_fichiers = 0

    for uploaded_file in uploaded_files:
        try:
            # Lire le fichier CSV
            df = pd.read_csv(uploaded_file, sep=",", header=0, skip_blank_lines=True)
            nb_fichiers += 1
            st.write(f"📄 Fichier {uploaded_file.name} chargé avec {df.shape[0]} lignes et {df.shape[1]} colonnes.")

            if df.empty:
                st.warning(f"⚠️ Le fichier {uploaded_file.name} est vide. Ignoré.")
                continue  

            # Vérifier que les colonnes nécessaires existent
            if df.shape[1] < 3:
                st.warning(f"⚠️ Le fichier {uploaded_file.name} ne contient pas les colonnes nécessaires. Ignoré.")
                continue

            # Renommer les colonnes et convertir la date
            df.rename(columns={df.columns[0]: "Date", df.columns[1]: "Temperature", df.columns[2]: "Humidite"}, inplace=True)
            df["Date"] = pd.to_datetime(df["Date"], format='%Y-%m-%d %H:%M:%S', errors='coerce')

            # Extraire la "Piece" du nom du fichier 
            df["Piece"] = extraire_piece(uploaded_file.name)

            # Nettoyer la colonne "Piece"
            df["Piece"] = df["Piece"].apply(nettoyer_Piece)

            list_dfs.append(df)
        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture du fichier {uploaded_file.name} : {e}")

    st.write(f"📂 Nombre total de fichiers CSV traités : {nb_fichiers}")

    if not list_dfs:
        st.warning("❌ Aucune donnée valide à traiter.")
        return None  

    # Combiner les fichiers
    df_combine = pd.concat(list_dfs, ignore_index=True)

    # Supprimer les doublons
    df_combine.drop_duplicates(subset=["Date", "Piece"], keep='first', inplace=True)

    # Vérifier si le fichier de sortie existe déjà et ajuster le nom si nécessaire
    date_du_jour = datetime.now().strftime("%Y-%m-%d")
    nom_fichier_sortie = f"donnees_combinees_Temperature_{date_du_jour}.csv"
    chemin_sortie_fichier = os.path.join(chemin_sortie, nom_fichier_sortie)

    # Si le fichier existe déjà, ajouter un suffixe numérique
    counter = 1
    while os.path.exists(chemin_sortie_fichier):
        chemin_sortie_fichier = os.path.join(chemin_sortie, f"donnees_combinees_Temperature_{date_du_jour}_{counter}.csv")
        counter += 1

    # Sauvegarde du fichier final
    try:
        df_combine.to_csv(chemin_sortie_fichier, index=False)
        st.success(f"✅ Fichier enregistré : {nom_fichier_sortie} ({df_combine.shape[0]} lignes)")
    except Exception as e:
        st.error(f"❌ Erreur lors de la sauvegarde du fichier : {e}")
        return None

    return df_combine
