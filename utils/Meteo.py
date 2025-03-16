import sqlite3
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
base_bd = os.getenv("NOM_BASE")
conn = sqlite3.connect("base_bd", check_same_thread=False)

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import openmeteo_requests
import requests_cache
from retry_requests import retry
from requests.adapters import RetryError
from datetime import datetime


def get_Historical_weather_data(ville, start_date, end_date):
    """
    Récupère les données météorologiques archivées pour une ville donnée, les insère dans une base de données SQLite,
    et ajoute des informations géographiques dans une autre table avec une relation par ID ville.
    
    Parameters:
        ville (str): Nom de la ville.
        start_date (str): Date de début au format 'YYYY-MM-DD'.
        end_date (str): Date de fin au format 'YYYY-MM-DD'.
    
    Returns:
        pd.DataFrame: Un DataFrame contenant les données horaires récupérées.
    """
    try:
        # Étape 1 : Récupérer les coordonnées de la ville
        geolocalisateur = Nominatim(user_agent="weather_app")
        localisation = geolocalisateur.geocode(ville)
        if not localisation:
            print(f"Impossible de trouver la localisation pour : {ville}")
            return None

        latitude, longitude = localisation.latitude, localisation.longitude
        print(f"Coordonnées pour {ville} : Latitude {latitude}, Longitude {longitude}")

        # Étape 2 : Configuration du client Open-Meteo avec cache et gestion des erreurs
        cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)  # Utilisation du client correct

        # Étape 3 : Définition des paramètres pour l'API Open-Meteo
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "rain",
                "snowfall",
                "cloud_cover",
                "et0_fao_evapotranspiration",
                "wind_speed_10m",
                "wind_direction_10m",
                "soil_temperature_0_to_7cm"
            ]
        }

        # Étape 4 : Appel à l'API Open-Meteo
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]  # Utilisation de la première réponse

        # Étape 5 : Traitement des données horaires
        hourly = response.Hourly()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
            "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
            "rain": hourly.Variables(2).ValuesAsNumpy(),
            "snowfall": hourly.Variables(3).ValuesAsNumpy(),
            "cloud_cover": hourly.Variables(4).ValuesAsNumpy(),
            "et0_fao_evapotranspiration": hourly.Variables(5).ValuesAsNumpy(),
            "wind_speed_10m": hourly.Variables(6).ValuesAsNumpy(),
            "wind_direction_10m": hourly.Variables(7).ValuesAsNumpy(),
            "soil_temperature_0_to_7cm": hourly.Variables(8).ValuesAsNumpy()
        }

        # Création d'un DataFrame
        hourly_dataframe = pd.DataFrame(data=hourly_data)

        # Convertir la colonne 'date' en format chaîne de caractères
        hourly_dataframe['date'] = hourly_dataframe['date'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Création de la base de données SQLite et des tables
        conn = sqlite3.connect('MaBase.db')
        cursor = conn.cursor()

        # Création de la table city_info avec 'ville' comme clé primaire
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS city_info (
            ville TEXT PRIMARY KEY,
            latitude REAL,
            longitude REAL
        )''')

        # Création de la table weather, avec une colonne 'ville' comme clé étrangère référencée dans 'city_info'
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            ville TEXT,
            temperature_2m REAL,
            relative_humidity_2m REAL,
            rain REAL,
            snowfall REAL,
            cloud_cover REAL,
            et0_fao_evapotranspiration REAL,
            wind_speed_10m REAL,
            wind_direction_10m REAL,
            soil_temperature_0_to_7cm REAL,
            FOREIGN KEY (ville) REFERENCES city_info(ville)
            UNIQUE (date, ville)
        )''')

        # Insertion ou mise à jour des données géographiques dans city_info
        cursor.execute('''
        INSERT OR REPLACE INTO city_info (ville, latitude, longitude) 
        VALUES (?, ?, ?)''', 
        (ville, latitude, longitude))

        # Insertion des données météo dans la table weather, avec la ville directement
        for index, row in hourly_dataframe.iterrows():
            cursor.execute(''' 
            INSERT INTO weather (date, ville, temperature_2m, relative_humidity_2m, rain, snowfall, cloud_cover, 
                                 et0_fao_evapotranspiration, wind_speed_10m, wind_direction_10m, soil_temperature_0_to_7cm)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (row['date'], ville, row['temperature_2m'], row['relative_humidity_2m'], row['rain'], row['snowfall'], 
             row['cloud_cover'], row['et0_fao_evapotranspiration'], row['wind_speed_10m'], 
             row['wind_direction_10m'], row['soil_temperature_0_to_7cm']))

        # Commit et fermeture de la connexion
        conn.commit()
        conn.close()

        print(f"Données insérées dans la base de données pour la ville {ville}.")
        return hourly_dataframe

    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Erreur de géolocalisation : {e}")
        return None
    except Exception as e:
        print(f"Erreur lors de la récupération des données météo : {e}")
        return None

# Exemple d'utilisation
#ville = "Trogues"
#start_date = "2000-01-01"
#end_date = "2025-03-10"

#weather_data = get_Historical_weather_data(ville, start_date, end_date)

#if weather_data is not None:
    #print(weather_data.head())
