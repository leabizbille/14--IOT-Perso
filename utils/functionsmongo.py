import pymongo
import gridfs
import os



# Connexion à MongoDB (assurez-vous d'avoir MongoDB en marche sur votre machine ou sur un serveur)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["IOT"]  # Nom de la base de données
fs = gridfs.GridFS(db)  # Accès à GridFS

# Dossier où les PDFs sont stockés
pdf_folder = r"1-Documents\pdfs"

# Insérer chaque fichier PDF dans GridFS
for pdf_filename in os.listdir(pdf_folder):
    pdf_path = os.path.join(pdf_folder, pdf_filename)
    with open(pdf_path, "rb") as pdf_file:
        pdf_data = pdf_file.read()
        # Enregistrer le PDF dans GridFS
        fs.put(pdf_data, filename=pdf_filename)
        print(f"✅ PDF {pdf_filename} inséré dans MongoDB")

# Fermer la connexion à MongoDB
client.close()
