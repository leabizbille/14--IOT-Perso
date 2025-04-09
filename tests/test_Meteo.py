import pytest
from unittest import mock
import pandas as pd
from openmeteo_requests import Client
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from utils import (
    get_Historical_weather_data
)

# Test avec un mock de la fonction geolocalisation
def test_get_Historical_weather_data_geolocation(mocker):
    # Mock de la fonction geolocalisation (Nominatim)
    mock_geocode = mocker.patch('geopy.geocoders.Nominatim.geocode')
    mock_geocode.return_value = mock.Mock(latitude=48.8566, longitude=2.3522)  # Coordonnées de Paris

    # Mock de la réponse de l'API météo
    mock_weather_api = mocker.patch('openmeteo_requests.Client.weather_api')
    mock_weather_api.return_value = [
        mock.Mock(
            Hourly=lambda: mock.Mock(
                Time=lambda: ['2025-04-08T00:00:00Z'],
                TimeEnd=lambda: ['2025-04-08T01:00:00Z'],
                Interval=lambda: [3600],
                Variables=lambda x: mock.Mock(ValuesAsNumpy=lambda: [20.5] if x == 0 else [50.0])
            )
        )
    ]

    # Appel de la fonction avec des valeurs de test
    result = get_Historical_weather_data("Paris", "2025-04-08", "2025-04-08")

    # Assertions sur le résultat
    assert result is not None  # On vérifie que l'on reçoit bien un DataFrame
    assert isinstance(result, pd.DataFrame)  # Le résultat doit être un DataFrame
    assert result.shape == (1, 10)  # On vérifie le nombre de lignes et de colonnes dans le DataFrame
    assert result['temperature_2m'][0] == 20.5  # Test de la température

    # Vérification que la fonction `geocode` a été appelée avec le bon paramètre
    mock_geocode.assert_called_once_with("Paris")

    # Vérification que l'API météo a bien été appelée
    mock_weather_api.assert_called_once()

# Test en cas d'erreur de géolocalisation
def test_get_Historical_weather_data_geolocation_error(mocker):
    # Simuler une erreur de géolocalisation
    mocker.patch('geopy.geocoders.Nominatim.geocode', side_effect=GeocoderTimedOut)

    result = get_Historical_weather_data("VilleInexistante", "2025-04-08", "2025-04-08")

    assert result is None  # Si une erreur survient, la fonction doit retourner None

# Test pour l'API Open-Meteo (simulation d'une erreur)
def test_get_Historical_weather_data_api_error(mocker):
    # Simuler une erreur lors de l'appel à l'API météo
    mocker.patch('openmeteo_requests.Client.weather_api', side_effect=Exception("API non disponible"))

    result = get_Historical_weather_data("Paris", "2025-04-08", "2025-04-08")

    assert result is None  # Si une erreur survient, la fonction doit retourner None
