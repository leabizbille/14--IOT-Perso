import sqlite3
from dotenv import load_dotenv
import os
import pandas as pd
from utils.functionsBDD import creer_table_city_info,creer_table_weather,insert_or_update_city_info, insert_weather_data
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import openmeteo_requests
import requests_cache
from retry_requests import retry
from requests.adapters import RetryError
from datetime import datetime
from dotenv import load_dotenv

#______________________________________________________________

# Charger les variables d'environnement - Aller chercher le fichier .env dans le dossier parent (racine du projet)
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
#load_dotenv(dotenv_path=os.path.abspath(dotenv_path))
load_dotenv(dotenv_path=dotenv_path, override=True)

base_bd = os.getenv("NOM_BASE")
#print(f"Chemin absolu du fichier .env : {dotenv_path}")
#print(f"Valeur de NOM_BASE : {base_bd}")
#print(f"Existe-t-il ? {os.path.exists(base_bd)}")

# Récupérer le nom de la base de données correctement
base_bd = os.getenv("NOM_BASE")
conn = sqlite3.connect(base_bd, check_same_thread=False)
url_Meteo = os.getenv("URL_METEO")

# Vérifier si la variable est bien chargée
#print(f"Nom de la base récupérée : {base_bd}")  # Debug
#print(f"Chemin du fichier .env : {dotenv_path}")  # Debug
#print(f"Contenu de NOM_BASE : {os.getenv('NOM_BASE')}")  # Debug

if base_bd is None:
    raise ValueError("Erreur : la variable d'environnement NOM_BASE n'est pas définie.")
#______________________________________________________________

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
        #print(f"Coordonnées pour {ville} : Latitude {latitude}, Longitude {longitude}")

        # Étape 2 : Configuration du client Open-Meteo avec cache et gestion des erreurs
        cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)  # Utilisation du client correct

        # Étape 3 : Définition des paramètres pour l'API Open-Meteo
        url = url_Meteo
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

        creer_table_city_info(conn)
        creer_table_weather(conn)
        insert_or_update_city_info(conn, ville, latitude, longitude)
        insert_weather_data(conn, ville, hourly_dataframe)
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
#end_date = "2025-03-16"

#weather_data = get_Historical_weather_data(ville, start_date, end_date)

#if weather_data is not None:
    #print(weather_data.head())
