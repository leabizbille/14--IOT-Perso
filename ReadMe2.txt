# 🌡️ Application IoT & Data – Données Govee, Énergie & Météo

🎯 Résumé du projet & objectifs

Ce projet a pour objectif de construire un pipeline complet de collecte, traitement, analyse et visualisation 
de données environnementales, en particulier des données de température issues de capteurs connectés 
(Govee H5075 / H5179), mais aussi d’autres sources comme EDF (PDF) et GRDF (PNG).

Il repose sur une stack orientée Data Science et Data Engineering, combinant des scripts Python, une application 
Streamlit pour l’interface utilisateur, MongoDB (via GridFS) pour le stockage flexible des fichiers, ainsi qu’un 
backend FastAPI pour exposer des points d’accès asynchrones.



### 🔧 Serveur FastAPI

```bash
uvicorn utils.api:app --reload --port 8000
```
🌐 Doc auto	http://localhost:8000/docs

### Développement local avec FastAPI
```bash
fastapi utils.api.py

# ⚙️ Mon token Bearer API ( depuis un .env )
$API_KEY = "   "

# ⚙️ URL de base de ton API FastAPI
$BASE_URL = "http://localhost:8000"

# ⚙️ En-têtes communs pour toutes les requêtes
$headers = @{
    Authorization = "Bearer $API_KEY"
}

# -------------------------------
# TEST : Endpoint protégé `/test`
# -------------------------------

Write-Host "`n=== Test Endpoint Protégé `/test` ==="
$response = Invoke-RestMethod -Uri "$BASE_URL/test" -Headers $headers -Method GET
$response

# -------------------------------
# TEST : Endpoint filtré `/gaz/`
# -------------------------------

Write-Host "`n=== Test Endpoint `/gaz/` ==="
$params = @{
    date_debut = "2025-01-01"
    date_fin   = "2025-01-31"
}
$response = Invoke-RestMethod -Uri "$BASE_URL/gaz/" -Headers $headers -Method GET -Body $params
$response

# -------------------------------
# TEST : Endpoint filtré `/electricite`
# -------------------------------

Write-Host "`n=== Test Endpoint `/electricite` ==="
$params = @{
    start_date = "2025-01-01"
    end_date   = "2025-01-31"
    limit      = 10
    offset     = 0
    order_by   = "Horodatage"
    order_dir  = "asc"
}
# Construire la query string dynamiquement
$query = ($params.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "&"
$response = Invoke-RestMethod -Uri "$BASE_URL/electricite?$query" -Headers $headers -Method GET
$response

```
### Libérer le port 8000 sous Windows, si besoin.

```bash
netstat -ano | findstr :8000
```

---

## 1️⃣ Environnement Python

```bash
python -m venv myenv           # Création de l’environnement virtuel
myenv\Scripts\activate         # Activation sous Windows
```

---

## 2️⃣ Git & Gestion de versions

### 🔒 Fichiers à ignorer

Fichier `.gitignore` pour éviter de versionner les fichiers sensibles ou inutiles (par ex. : `.env`, `__pycache__/`, `*.db`, `*.csv`, etc.).

### 🔁 Workflow Git

```bash
git checkout -b feature/ajout-page-meteo       # Nouvelle branche
git add .
git commit -m "Ajout de la page météo"
git checkout main                              # Retour à main
git merge feature/ajout-page-meteo             # Fusion
git push origin main                           # Push vers dépôt distant
```

---

## 3️⃣ Installation des dépendances

### 🔎 Identifier la version Python

```bash
where python
```

### 📦 Installer les packages

```bash
pip install -r requirements.txt
pip install --upgrade pip
pip install bleak --force-reinstall                 # Pour le Bluetooth Govee
pip install visions[type_image_path]==0.7.4
```

---

## 4️⃣ Librairies utilisées (extrait)

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


---

## 5️⃣ Suivi des packages

### 📋 Liste des packages installés

```bash
pip list
```

### 📂 Sauvegarde des packages installés

```bash
pip freeze > 1-Documents/requirements_Sauvegarde.txt
```

---

## 6️⃣ Fichier `.env` & Variables d’environnement

```bash
pip install python-dotenv
```

> Le fichier `.env` est à la racine du projet avec les clés sensibles comme `MONGO_URI`, `API_KEY`, etc.

---

## 7️⃣ Scripts à exécuter

### 📅 Récupération de données

```bash
python govee-h5075.py -m         # Récupère les données température par modules
python govee-h5075.py -s         # Synchronisation
python Meteo.py                  # Appelle l'API météo Open-Meteo
python -m utils.ScrapingGRDF     # Récupère les données GRDF (graphiques PNG)
```

---

## 8️⃣ 🚀 Lancement de l'application web (Streamlit)
## 

```bash
streamlit run app2.py
```

### 🔪 Autres

```bash
python -m utils.api              # API interne
streamlit cache clear            # Nettoyage du cache Streamlit
```

---

## 📁 Dossiers spéciaux

* Mettre le fichier `.known_govees` dans le dossier suivant (Windows) :

  ```
  C:\Users\Lau
  ```
