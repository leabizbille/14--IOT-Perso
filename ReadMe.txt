
Launch the application :
fastapi dev main.py

# Pour le serveur : 
uvicorn main:app --reload --host=0.0.0.0

# effacer les connexions sur le port 8000 :
netstat -ano | findstr :8000

Mon Adresse IPv4 192.168.0.105




# 1 Environnement  -----------------------------------------------------------------
python -m venv myenv
myenv\Scripts\activate       # Environnement

# 2 Git Ignore ---------------------------------------------------------------------

# 3. Git ---------------------------------------------------------------------------
# Créez une nouvelle branche pour une fonctionnalité
git checkout -b feature/ajout-page-meteo

# Faites vos changements, puis ajoutez et commettez les modifications
git add .
git commit -m "Ajout de la page météo"

# Une fois votre travail terminé, revenez à la branche principale
git checkout main

# Fusionnez votre branche dans la branche principale
git merge feature/ajout-page-meteo

# Poussez les modifications vers le dépôt distant
git push origin main

# 4. requirements--------------------------------------------------------------------
Connaitre la version de python : where python    
# Ici, la version python et localisation sur ordi.

pip install -r requirements.txt
pip install bleak --force-reinstall # si probleme avec bleak pour le téléchargement des données en bluetooth
pip install visions[type_image_path]==0.7.4
pip install --upgrade pip

🚀 Bibliothèques pour la gestion asynchrone et les requêtes API :

* asyncio – Permet d'exécuter du code de manière asynchrone (exécution concurrente). Utile pour interagir avec des API ou gérer des tâches parallèles sans bloquer l'application.
* requests – Utilisé pour envoyer des requêtes HTTP à des API ou récupérer des pages web.
* openmeteo-requests – Wrapper spécifique pour interagir avec l'API météo Open-Meteo.
* requests-cache – Ajoute un cache aux requêtes requests pour éviter de refaire les mêmes appels API inutiles.
* retry-requests – Permet de réessayer automatiquement une requête HTTP en cas d'échec (ex: problème réseau temporaire).
* openmeteo_py – Client Python pour récupérer des données météorologiques via Open-Meteo.
* geopy – Utilisé pour la géolocalisation et le calcul de distances entre lieux.
* holidays – Permet de récupérer les jours fériés d’un pays donné, utile pour ajuster des prévisions.

📅 Gestion du temps et des tâches planifiées : 

* datetime – Module intégré pour manipuler les dates et heures.
* schedule – Permet d’exécuter des tâches à des intervalles réguliers (ex: exécuter un script toutes les heures).

📝 Gestion des entrées utilisateur et manipulation de fichiers:

* argparse – Module intégré permettant de gérer les arguments passés en ligne de commande (utile pour créer des scripts CLI).
* uuid – Permet de générer des identifiants uniques (UUID), souvent utilisé pour identifier des objets de manière unique.
* PyPDF2 – Permet de lire et manipuler des fichiers PDF (extraction de texte, fusion, séparation de pages).

📊 Analyse et traitement des données :

* pandas – Bibliothèque essentielle pour manipuler et analyser des données sous forme de tableaux (DataFrame).
* numpy – Fournit des structures et fonctions mathématiques avancées pour manipuler des tableaux numériques efficacement.
* statsmodels – Fournit des outils pour les statistiques et la modélisation des séries temporelles.
* scikit-learn – Outil clé pour l’apprentissage automatique et le traitement des données (classification, régression, clustering, etc.).
* nltk – Bibliothèque spécialisée en traitement du langage naturel (NLP), utilisée pour l’analyse de texte.

📈 Visualisation des données et reporting

* pygwalker – Interface graphique permettant d'explorer les données de façon interactive en utilisant pandas et plotly.
* sweetviz – Génère automatiquement des rapports d’analyse de données pour une exploration rapide.
* missingno – Visualise les valeurs manquantes dans un dataset pour mieux comprendre les données et leur qualité.
* summarytools – Fournit des résumés statistiques et exploratoires des datasets.
* plotly – Bibliothèque de visualisation interactive pour générer des graphiques dynamiques.
* streamlit – Framework permettant de créer facilement des applications web interactives pour la visualisation de données et l’IA.


pip list # Pour connaitre l'ensemble des packages dans le requirements.
pip freeze > requirements_Sauvegarde.txt # Pour connaitre exactements les packages sans modifier le requiements utilisé actuellement.

#------------------------------------------------------------------
python govee-h5075.py -m      # récuperation des data températures et modules
python govee-h5075.py -s

#------------------------------------------------------------------
# Pour mettre en fonction streamlit 
streamlit run Streamlit_BaseBatiment.py

#------------------------------------------------------------------
Mettre le fichier .known_govees dans le fichier C:\Users\Lau
