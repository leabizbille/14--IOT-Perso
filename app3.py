import streamlit as st
import asyncio
import json
from datetime import datetime
from utils import  GoveeThermometerHygrometer, Alias, recorded_data, device_info  # Assurez-vous que ce code est dans un module importable

# Initialisation des objets nécessaires
alias = Alias()

# Titre de la page
st.title('Dashboard Govee H5075 - Température et Humidité')

# Affichage de l'info du dispositif
st.header('Informations sur le dispositif')

device_info_label = st.text_input("Entrez l'adresse MAC ou alias du dispositif", "")
if device_info_label:
    if st.button("Obtenir les informations du dispositif"):
        try:
            device_info = asyncio.run(device_info(device_info_label))
            st.json(device_info.to_dict() if device_info else "Aucune information trouvée.")
        except Exception as e:
            st.error(f"Erreur : {e}")

# Affichage des données enregistrées
st.header('Données enregistrées')

data_label = st.text_input("Entrez l'adresse MAC ou alias", "")
start_time = st.text_input("Temps de début (format: minutes:secondes, ex: 480:00)", "0:00")
end_time = st.text_input("Temps de fin (format: minutes:secondes, ex: 480:00)", "60:00")
if data_label:
    if st.button("Obtenir les données enregistrées"):
        # Requête pour obtenir les données enregistrées
        try:
            recorded_data = asyncio.run(recorded_data(data_label, start=start_time, end=end_time))
            st.text(recorded_data)
        except Exception as e:
            st.error(f"Erreur : {e}")

# Affichage des mesures actuelles
st.header('Mesures en temps réel')

if st.button("Démarrer la capture des mesures"):
    st.write("Capture des mesures en cours...")
    # Pour l'affichage en temps réel, on peut lancer une boucle qui récupère les données
    def measure_consumer(address, name, battery, measurement):
        timestamp = measurement.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        st.write(f"{timestamp}   {address}   {name}   {measurement.temperatureC}°C   {measurement.dewPointC}°C   {measurement.relHumidity}%   {measurement.absHumidity} g/m³   {measurement.steamPressure} mbar   {battery}%")

    # Lancer la capture avec Streamlit
    asyncio.run(GoveeThermometerHygrometer.scan(consumer=measure_consumer, unique=False))

# Exemple d'affichage des résultats sous forme de tableau
st.header("Mesures sous forme de tableau")

# Simulation de données pour affichage
if st.button("Afficher les mesures"):
    # Simuler quelques données
    data = [
        {"Timestamp": "2025-05-05 12:00", "Température (°C)": 22.1, "Dew Point (°C)": 15.3, "Humidité relative (%)": 50.2, "Humidité absolue (g/m³)": 8.1, "Pression de vapeur (mbar)": 10.5},
        {"Timestamp": "2025-05-05 12:01", "Température (°C)": 22.2, "Dew Point (°C)": 15.4, "Humidité relative (%)": 51.0, "Humidité absolue (g/m³)": 8.2, "Pression de vapeur (mbar)": 10.6},
    ]
    st.write(data)
    st.table(data)
