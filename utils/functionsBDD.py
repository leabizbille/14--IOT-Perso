import sqlite3
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
base_bd = os.getenv("NOM_BASE")
conn = sqlite3.connect("base_bd", check_same_thread=False)


def get_connection():
    """Retourne une connexion à la base de données avec gestion des erreurs."""
    try:
        # Tentative de connexion à la base de données SQLite
        conn = sqlite3.connect("base_bd", check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        # Si une erreur SQLite survient, afficher un message d'erreur
        print(f"Erreur de connexion à la base de données : {e}")
        return None  # Retourne None si la connexion échoue
    except Exception as e:
        # Capturer toute autre exception non spécifiée
        print(f"Erreur inattendue : {e}")
        return None  # Retourne None si une autre erreur survient


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
            print("Table ConsoHeureElec créée ou déjà existante.")
    except sqlite3.Error as e:
        # Capturer les erreurs spécifiques à SQLite
        print(f"Erreur SQLite lors de la création de la table : {e}")
        return False  # Retourne False en cas d'erreur
    except Exception as e:
        # Capturer toute autre exception
        print(f"Erreur inattendue : {e}")
        return False  # Retourne False en cas d'erreur
    return True  # Retourne True si la table a été créée sans erreur

def get_existing_dates(conn, id_batiment):
    """Retourne les dates déjà existantes dans la base de données pour un bâtiment donné."""
    query = "SELECT Horodatage FROM ConsoHeureElec WHERE ID_Batiment = ?"
    return set(pd.read_sql(query, conn, params=(id_batiment,))["Horodatage"].tolist())

# Table pour les temperature des pieces
def creer_table_temperature_piece(base_bd):
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
            print("Table TemperaturePiece créée ou déjà existante.")
    except sqlite3.Error as e:
        # Capturer les erreurs spécifiques à SQLite
        print(f"Erreur SQLite lors de la création de la table : {e}")
        return False  # Retourne False en cas d'erreur
    except Exception as e:
        # Capturer toute autre exception
        print(f"Erreur inattendue : {e}")
        return False  # Retourne False en cas d'erreur
    return True  # Retourne True si la table a été créée sans erreur

