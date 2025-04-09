import sqlite3
from dotenv import load_dotenv
import os
import pandas as pd


# Charger les variables d'environnement une seule fois au début du script
load_dotenv()
# Récupérer la base de données depuis .env
base_bd = os.getenv("NOM_BASE", "MaBase.db")

# Vérifier que la variable est bien récupérée
if not base_bd:
    raise ValueError("⚠️ La variable NOM_BASE n'est pas définie dans .env !")

def get_connection():
    """Retourne une connexion à la base de données avec gestion des erreurs."""
    try:
        # Vérifie si le fichier de base existe
        if not os.path.exists(base_bd):
            raise ValueError(f"⚠️ Le fichier de base de données n'existe pas : {base_bd}")

        # Connexion à SQLite
        conn = sqlite3.connect(base_bd, check_same_thread=False)
        print(f"✅ Connexion réussie à la base de données : {base_bd}")
        return conn
    except sqlite3.Error as e:
        print(f"❌ Erreur de connexion à la base de données : {e}")
        return None
    except ValueError as ve:
        print(ve)
        return None


# BDD Table pour ENEDIS
def creer_table_consoheure(conn):
    """Crée la table ConsoHeureElec si elle n'existe pas, avec gestion des erreurs."""
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ConsoHeureElec (
                    Horodatage TEXT,
                    ValeurW INTEGER,
                    ID_Batiment INTEGER,
                    PRIMARY KEY (Horodatage, ID_Batiment),
                    FOREIGN KEY (ID_Batiment) REFERENCES Batiment(ID_Batiment)
                )
            ''')
            conn.commit()
            #print("Table ConsoHeureElec créée ou déjà existante.")
    except sqlite3.Error as e:
        # Capturer les erreurs spécifiques à SQLite
        print(f"Erreur SQLite lors de la création de la table : {e}")
        return False  # Retourne False en cas d'erreur
    except Exception as e:
        # Capturer toute autre exception
        print(f"Erreur inattendue : {e}")
        return False  # Retourne False en cas d'erreur
    return True  # Retourne True si la table a été créée sans erreur

# Fonction pour récupérer les données de consommation
def recuperer_conso_data(conn):
    """
    Récupère les données de consommation électrique depuis la table ConsoHeureElec.

    Parameters:
        conn (sqlite3.Connection): Connexion à la base de données SQLite.

    Returns:
        pd.DataFrame: Un DataFrame contenant les données de consommation avec les colonnes Horodatage, ValeurW, et ID_Batiment.
    """
    try:
        cursor = conn.cursor()

        # Exécution de la requête SQL pour récupérer les données
        cursor.execute("SELECT Horodatage, ValeurW, ID_Batiment FROM ConsoHeureElec")
        
        # Récupérer les résultats et les convertir en DataFrame
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["Horodatage", "ValeurW", "ID_Batiment"])

        # Convertir la colonne 'Horodatage' en format datetime
        df['Horodatage'] = pd.to_datetime(df['Horodatage'])

        return df
    except sqlite3.Error as e:
        print(f"Erreur SQLite lors de la récupération des données : {e}")
        return None  # Retourner None en cas d'erreur
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        return None  # Retourner None en cas d'erreur

def get_existing_dates(conn, id_batiment):
    """Retourne les dates déjà existantes dans la base de données pour un bâtiment donné."""
    query = "SELECT Horodatage FROM ConsoHeureElec WHERE ID_Batiment = ?"
    return set(pd.read_sql(query, conn, params=(id_batiment,))["Horodatage"].tolist())


def get_existing_datesGAZ(conn, id_batiment):
    """Retourne les dates déjà existantes dans la base de données pour un bâtiment donné."""
    query = "SELECT Horodatage FROM ConsoJourGaz WHERE ID_Batiment = ?"
    return set(pd.read_sql(query, conn, params=(id_batiment,))["Horodatage"].tolist())
# Table pour les temperature des pieces
def creer_table_temperature_piece(conn):
    try:
        with conn:
            cursor = conn.cursor()
            # Création de la table TemperaturePiece
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS TemperaturePiece (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Horodatage TEXT NOT NULL,
                    Température_Celsius INTEGER NOT NULL,
                    Humidité_Relative INTEGER NOT NULL,
                    Piece TEXT(20) NOT NULL,
                    ID_Batiment TEXT(20) NOT NULL,
                    CONSTRAINT TemperaturePiece_Piece_FK 
                        FOREIGN KEY (ID_Batiment, Piece) 
                        REFERENCES Piece(ID_Batiment, Piece)
                )
            ''')
            conn.commit()
            #print("Table TemperaturePiece créée ou déjà existante.")
    except sqlite3.Error as e:
        # Capturer les erreurs spécifiques à SQLite
        print(f"Erreur SQLite lors de la création de la table : {e}")
        return False  # Retourne False en cas d'erreur
    except Exception as e:
        # Capturer toute autre exception
        print(f"Erreur inattendue : {e}")
        return False  # Retourne False en cas d'erreur
    return True  # Retourne True si la table a été créée sans erreur

# Tables pour les villes ----------------------------------------------------------------
def creer_table_city_info(conn):
    try:
        with conn:
            cursor = conn.cursor()
            # Création de la table city_info avec 'ville' comme clé primaire
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS city_info (
                ville TEXT PRIMARY KEY,
                latitude REAL,
                longitude REAL
            )''')
            conn.commit()
            #print("Table city_info créée ou déjà existante.")
    except sqlite3.Error as e:
        # Capturer les erreurs spécifiques à SQLite
        print(f"Erreur SQLite lors de la création de la table : {e}")
        return False  # Retourne False en cas d'erreur
    except Exception as e:
        # Capturer toute autre exception
        print(f"Erreur inattendue : {e}")
        return False  # Retourne False en cas d'erreur
    return True  # Retourne True si la table a été créée sans erreur

def insert_or_update_city_info(conn, ville, latitude, longitude):
    """
    Insère ou met à jour les informations géographiques d'une ville dans la table city_info.

    Parameters:
        conn (sqlite3.Connection): Connexion à la base de données SQLite.
        ville (str): Nom de la ville.
        latitude (float): Latitude de la ville.
        longitude (float): Longitude de la ville.
    """
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO city_info (ville, latitude, longitude) 
        VALUES (?, ?, ?)''', 
        (ville, latitude, longitude))
    conn.commit()


# Table pour les informations météorologiques --------------------------------
def creer_table_weather(conn):
    try:
        with conn:
            cursor = conn.cursor()
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
            conn.commit()
            print("Table weather créée ou déjà existante.")
    except sqlite3.Error as e:
        # Capturer les erreurs spécifiques à SQLite
        print(f"Erreur SQLite lors de la création de la table : {e}")
        return False  # Retourne False en cas d'erreur
    except Exception as e:
        # Capturer toute autre exception
        print(f"Erreur inattendue : {e}")
        return False  # Retourne False en cas d'erreur
    return True  # Retourne True si la table a été créée sans erreur

def insert_weather_data(conn, ville, hourly_dataframe):
    """
    Insère les données météorologiques dans la table weather.

    Parameters:
        conn (sqlite3.Connection): Connexion à la base de données SQLite.
        ville (str): Nom de la ville.
        hourly_dataframe (pd.DataFrame): DataFrame contenant les données météorologiques horaires.
    """
    cursor = conn.cursor()
    
    for _, row in hourly_dataframe.iterrows():
        cursor.execute(''' 
            INSERT INTO weather (date, ville, temperature_2m, relative_humidity_2m, rain, snowfall, cloud_cover, 
                                 et0_fao_evapotranspiration, wind_speed_10m, wind_direction_10m, soil_temperature_0_to_7cm)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (row['date'], ville, row['temperature_2m'], row['relative_humidity_2m'], row['rain'], row['snowfall'], 
             row['cloud_cover'], row['et0_fao_evapotranspiration'], row['wind_speed_10m'], 
             row['wind_direction_10m'], row['soil_temperature_0_to_7cm']))
    
    conn.commit()

def creer_table_batiment(conn):
    try:
        with conn:
            # Création de la table Piece si elle n'existe pas déjà
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Batiment (
                ID_Batiment TEXT PRIMARY KEY,
                Ville TEXT,
                Consigne_Ete_Jour INTEGER,
                Consigne_Ete_Nuit INTEGER,
                Consigne_Hiver_Jour INTEGER,
                Consigne_Hiver_Nuit INTEGER,
                Consigne_Absence INTEGER,
                Date_Allumage DATE,
                Date_Arret DATE,
                Zone_Academique TEXT,
                Type_Batiment TEXT
            );
            """)
        # Commit pour enregistrer les changements dans la base de données
            conn.commit()
            print("Table Batiment créée ou déjà existante.")
    except sqlite3.Error as e:
        # Capturer les erreurs spécifiques à SQLite
        print(f"Erreur SQLite lors de la création de la table : {e}")
        return False  # Retourne False en cas d'erreur
    except Exception as e:
        # Capturer toute autre exception
        print(f"Erreur inattendue : {e}")
        return False  # Retourne False en cas d'erreur
    return True  # Retourne True si la table a été créée sans erreur


def creer_table_piece(conn):
    try:
        with conn:
            # Création de la table Piece si elle n'existe pas déjà
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Piece (
                ID_Batiment TEXT NOT NULL,
                Piece TEXT NOT NULL,
                Surface INTEGER NOT NULL,
                Orientation TEXT NOT NULL,
                Chauffage_Principal TEXT,
                Chauffage_Secondaire TEXT,
                Nbr_Fenetre INTEGER NOT NULL,
                Nbr_Porte INTEGER NOT NULL,
                Nbr_Mur_Facade INTEGER NOT NULL,
                Etage INTEGER,
                PRIMARY KEY (ID_Batiment, Piece),
                FOREIGN KEY (ID_Batiment) REFERENCES Batiment(ID_Batiment)
            );
            """)
        # Commit pour enregistrer les changements dans la base de données
            conn.commit()
            #print("Table 'Piece' créée avec succès.")
    except sqlite3.Error as e:
        # Capturer les erreurs spécifiques à SQLite
        print(f"Erreur SQLite lors de la création de la table : {e}")
        return False  # Retourne False en cas d'erreur
    except Exception as e:
        # Capturer toute autre exception
        print(f"Erreur inattendue : {e}")
        return False  # Retourne False en cas d'erreur
    return True  # Retourne True si la table a été créée sans erreur


# BDD Table pour le GAZ
def creer_table_consoJour_GAZ(conn):
    """Créer la table Conso Gaz  si elle n'existe pas, avec gestion des erreurs."""
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ConsoJourGaz (
                    Horodatage TEXT,
                    Valeur_m3 INTEGER,
                    Conversion INTEGER,
                    ID_Batiment INTEGER,
                    PRIMARY KEY (Horodatage, ID_Batiment),
                    FOREIGN KEY (ID_Batiment) REFERENCES Batiment(ID_Batiment)
                )
            ''')
            conn.commit()
            #print("Table Conso GAZ créée ou déjà existante.")
    except sqlite3.Error as e:
        # Capturer les erreurs spécifiques à SQLite
        print(f"Erreur SQLite lors de la création de la table : {e}")
        return False  # Retourne False en cas d'erreur
    except Exception as e:
        # Capturer toute autre exception
        print(f"Erreur inattendue : {e}")
        return False  # Retourne False en cas d'erreur
    return True  # Retourne True si la table a été créée sans erreur

# Fonction pour récupérer les données de consommation
def recuperer_conso_dataGAZ(conn):
    """
    Récupère les données de consommation gaz depuis la table ConsoJourGaz.

    Parameters:
        conn (sqlite3.Connection): Connexion à la base de données SQLite.

    Returns:
        pd.DataFrame: Un DataFrame contenant les données de consommation avec les colonnes Horodatage, Valeur_m3, Conversion et ID_Batiment.
    """
    try:
        cursor = conn.cursor()

        # Exécution de la requête SQL pour récupérer les données
        cursor.execute("SELECT Horodatage, Valeur_m3,Conversion , ID_Batiment FROM ConsoJourGaz")
        
        # Récupérer les résultats et les convertir en DataFrame
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["Horodatage", "Valeur_m3", "Conversion","ID_Batiment"])

        # Convertir la colonne 'Horodatage' en format datetime
        df['Horodatage'] = pd.to_datetime(df['Horodatage'])

        return df
    except sqlite3.Error as e:
        print(f"Erreur SQLite lors de la récupération des données : {e}")
        return None  # Retourner None en cas d'erreur
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        return None  # Retourner None en cas d'erreur
