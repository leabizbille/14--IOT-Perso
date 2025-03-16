import streamlit as st
from utils import importer_csv_dans_bdd, creer_table_consoheure, get_connection
# app.py
from utils.functions import importer_csv_dans_bdd
from utils.functionsBDD import creer_table_consoheure, get_connection

# Connexion à la base de données
conn = get_connection()

# Création de la table si elle n'existe pas
creer_table_consoheure(conn)

# Interface utilisateur Streamlit pour l'upload du fichier CSV
uploaded_file = st.file_uploader("Choisir un fichier CSV", type=["csv"])

id_batiment = st.number_input("ID du bâtiment", min_value=1)

if uploaded_file and id_batiment:
    importer_csv_dans_bdd(uploaded_file, id_batiment)


import streamlit as st
from utils.Meteo import get_Historical_weather_data

def main():
    st.title("Weather Data Extraction")
    
    # Inputs de l'utilisateur
    ville = st.text_input("Entrez le nom de la ville")
    start_date = st.date_input("Date de début")
    end_date = st.date_input("Date de fin")
    
    if st.button("Obtenir les données météo"):
        if ville and start_date and end_date:
            weather_data = get_Historical_weather_data(ville, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
            if weather_data is not None:
                st.write(weather_data)
            else:
                st.error("Une erreur est survenue lors de la récupération des données.")
        else:
            st.error("Veuillez entrer tous les champs nécessaires.")

if __name__ == "__main__":
    main()
