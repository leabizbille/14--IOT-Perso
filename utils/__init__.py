# __init__.py
VERSION = "1.0.0"
AUTHOR = "Laurence"

from .functions import (
    importer_csv_dans_bdd,
    extraire_piece,
    importer_csv_GAZ_bdd,
    nettoyer_Piece
)

from .functionsBDD import (
    creer_table_consoheure,
    creer_table_consoJour_GAZ,
    recuperer_conso_data,
    recuperer_conso_dataGAZ,
    get_existing_datesGAZ,
    base_bd,
    creer_table_batiment,
    creer_table_piece,
    insert_or_update_city_info,
    insert_weather_data,
    creer_table_weather,
    get_connection,
    get_existing_dates,
    creer_table_temperature_piece,
    creer_table_city_info
)

from .GoveeWifiInsert import traiter_donnees_Temperature_streamlit

from .Meteo import get_Historical_weather_data

from .visualizations import afficher_graphique, afficher_graphiqueGaz

from .functionsStreamlit import (
    page_Enedis,
    page_Gaz,
    page_GoveeH5179,
    page_installation,
    page_Meteo,
    page_parametres
)
