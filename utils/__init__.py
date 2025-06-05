# __init__.py
VERSION = "1.0.0"
AUTHOR = "Laurence"

from .functions import (
    importer_csv_dans_bdd,
    extraire_piece,
    importer_csv_GAZ_bdd,
    check_password,
    nettoyer_Piece, 
    setup_driver,
    wait_element,
    save_debug_html,
    accept_cookies,
    analyze_page,
    connexion,
    fig_to_bytes,
    save_screenshot_with_date
)

from .functionsBDD import (
    creer_table_consoheure,
    creer_table_consoJour_GAZ,
    recuperer_conso_data,
    recuperer_conso_dataGAZ,
    get_existing_datesGAZ,
    creer_table_utilisateur,
    creer_table_utilisateur_batiment,
    insert_user,
    get_user,
    base_bd,
    creer_table_batiment,
    creer_table_piece,
    insert_or_update_city_info,
    insert_weather_data,
    creer_table_weather,
    get_connection,
    get_existing_dates,
    creer_table_temperature_piece,
    inserer_donnees_temperature_piece,
    creer_table_city_info
)

from .GoveeWifiInsert import traiter_donnees_Temperature_streamlit
from .govee_h5075 import GoveeThermometerHygrometer, Alias, recorded_data, device_info 
from .Meteo import get_Historical_weather_data
from .visualizations import afficher_graphique, afficher_graphiqueGaz

from .functionsStreamlit import (
    page_Enedis,
    page_Gaz,
    page_GoveeH5179,
    page_installation,
    page_creation_compte,
    page_Meteo,
    page_connexion,
    page_visualisation_Govee,
    page_API,
    page_rgpd,
    page_parametres
)

from .functionsmongo import (
    import_pdfs_to_gridfs,
    import_csv_to_gridfs,
    import_png_to_gridfs,
    download_files_from_gridfs,
    temperature_folder
)