from dotenv import load_dotenv
import os
import pymongo
import gridfs

# Chargement de l'environnement
load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME", "Documents")
pdf_folder = r"1-Documents\pdfs"
temperature_folder = r"1-Documents\Fichiers Temperature"

#pdf EDF du scraping
def import_pdfs_to_gridfs(db, pdf_folder, collection_name="EDF"):
    """
    Importe les fichiers PDF d'un dossier local dans GridFS (MongoDB),
    en évitant les doublons de nom de fichier.

    Args:
        db (pymongo.database.Database): instance de base MongoDB.
        pdf_folder (str): chemin du dossier contenant les PDFs.
        collection_name (str): nom logique de la collection GridFS.
    """
    if not os.path.exists(pdf_folder):
        raise FileNotFoundError(f"📂 Le dossier {pdf_folder} est introuvable.")

    fs = gridfs.GridFS(db, collection=collection_name)

    for pdf_filename in os.listdir(pdf_folder):
        if not pdf_filename.lower().endswith(".pdf"):
            continue  # Ignore les fichiers non-PDF

        # Éviter les doublons
        if fs.find_one({"filename": pdf_filename}):
            print(f"⏩ {pdf_filename} déjà présent, ignoré.")
            continue

        pdf_path = os.path.join(pdf_folder, pdf_filename)
        with open(pdf_path, "rb") as pdf_file:
            fs.put(pdf_file.read(), filename=pdf_filename)
            print(f"✅ {pdf_filename} inséré dans GridFS ({collection_name})")

# Fichiers csv de govee
def import_csv_to_gridfs(db, temperature_folder, collection_name="Govee"):
    """
    Importe les fichiers cvs d'un dossier local dans GridFS (MongoDB),
    en évitant les doublons de nom de fichier.

    Args:
        db (pymongo.database.Database): instance de base MongoDB.
        temperature_folder (str): chemin du dossier contenant les CSVs.
        collection_name (str): nom logique de la collection GridFS.
    """
    if not os.path.exists(temperature_folder):
        raise FileNotFoundError(f"📂 Le dossier {temperature_folder} est introuvable.")

    fs = gridfs.GridFS(db, collection=collection_name)

    for csv_filename in os.listdir(temperature_folder):
        if not csv_filename.lower().endswith(".csv"):
            continue  # Ignore les fichiers non-CSV

        # Éviter les doublons
        if fs.find_one({"filename": csv_filename}):
            print(f"⏩ {csv_filename} déjà présent, ignoré.")
            continue

        csv_path = os.path.join(temperature_folder, csv_filename)
        with open(csv_path, "rb") as csv_file:
            fs.put(csv_file.read(), filename=csv_filename)
            print(f"✅ {csv_filename} inséré dans GridFS ({collection_name})")



# Connexion MongoDB
client = pymongo.MongoClient(mongo_uri)
db = client[db_name]

# Appel de la fonction
import_pdfs_to_gridfs(db, pdf_folder, collection_name="EDF")
import_csv_to_gridfs (db,temperature_folder, collection_name ="Govee")
# Fermeture
client.close()