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
GRDF_folder = r"1-Documents\GRDF"

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
# Fichiers csv de govee
def import_png_to_gridfs(db, GRDF_folder, collection_name="GRDF"):
    """
    Importe les fichiers png d'un dossier local dans GridFS (MongoDB),
    en évitant les doublons de nom de fichier.
    Args:
        db (pymongo.database.Database): instance de base MongoDB.
        GRDF_folder (str): chemin du dossier contenant les CSVs.
        collection_name (str): nom logique de la collection GridFS.
    """
    if not os.path.exists(GRDF_folder):
        raise FileNotFoundError(f"📂 Le dossier {GRDF_folder} est introuvable.")

    fs = gridfs.GridFS(db, collection=collection_name)

    for png_filename in os.listdir(GRDF_folder):
        if not png_filename.lower().endswith(".png"):
            continue  # Ignore les fichiers non-png

        # Éviter les doublons
        if fs.find_one({"filename": png_filename}):
            print(f"⏩ {png_filename} déjà présent, ignoré.")
            continue

        png_path = os.path.join(GRDF_folder , png_filename)
        with open(png_path, "rb") as png_file:
            fs.put(png_file.read(), filename=png_filename)
            print(f"✅ {png_filename} inséré dans GridFS ({collection_name})")

# Connexion MongoDB
client = pymongo.MongoClient(mongo_uri)
db = client[db_name]

# Appel de la fonction
import_pdfs_to_gridfs(db, pdf_folder, collection_name="EDF")
import_csv_to_gridfs (db,temperature_folder, collection_name ="Govee")
import_png_to_gridfs (db,GRDF_folder, collection_name ="GRDF")

# Fermeture
client.close()

def download_files_from_gridfs(db, destination_folder, collection_name="Govee"):
    import gridfs

    fs = gridfs.GridFS(db, collection=collection_name)

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for file in fs.find():
        file_path = os.path.join(destination_folder, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.read())
        print(f"📥 {file.filename} téléchargé dans {destination_folder}")
