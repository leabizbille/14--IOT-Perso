import requests
import os

# Créer un dossier pour stocker les fichiers téléchargés (si nécessaire)
folder_path= r"C:\Users\Lau\Documents\Moi\1-Travail (sept 23)\3- IA\1- Formation Greta\3- Projets\14- IOT Perso\1-Documents\pdfs"
os.makedirs(folder_path, exist_ok=True)

def download_pdfs(pdf_urls):

    # Créer le dossier et ses parents si nécessaire
    os.makedirs(folder_path, exist_ok=True)

    print(f"Dossier '{folder_path}' est prêt à être utilisé.")

    # Télécharger chaque fichier PDF
    for url in pdf_urls:
        # Déterminer le nom du fichier à partir de l'URL
        pdf_filename = os.path.join(folder_path, url.split("/")[-1])
        
        # Effectuer la demande HTTP pour télécharger le PDF
        response = requests.get(url)
        
        # Sauvegarder le PDF dans le dossier local
        with open(pdf_filename, 'wb') as file:
            file.write(response.content)
        print(f"📥 PDF téléchargé : {pdf_filename}")

if __name__ == "__main__":
    from ScrapingPrixEDF import get_pdf_urls  # Importer la fonction pour récupérer les URLs des PDF
    pdf_urls = get_pdf_urls()  # Récupérer les URLs des PDF depuis scraper.py
    download_pdfs(pdf_urls)  # Télécharger les PDFs


