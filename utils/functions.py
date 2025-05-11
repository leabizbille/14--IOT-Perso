import pandas as pd
import streamlit as st
from .functionsBDD import get_connection, get_existing_dates, get_existing_datesGAZ
import bcrypt

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webdriver import WebDriver
from datetime import datetime

import time
import os
import re
from dotenv import load_dotenv

# Fonction pour extraire le premier mot avant le premier underscore du nom du fichier
def extraire_piece(nom_fichier):
    try:
        # Vérifier que le nom du fichier contient le caractère de séparation '_'
        if '_' not in nom_fichier:
            raise ValueError(f"Le nom du fichier '{nom_fichier}' ne contient pas de caractère de séparation '_'.")

        # Extraire la partie avant le premier '_'
        piece = nom_fichier.split('_')[0]
        return piece
    except Exception as e:
        # Si une erreur survient, afficher un message d'erreur avec Streamlit
        st.error(f"❌ Erreur dans l'extraction de la pièce du fichier '{nom_fichier}': {e}")
        return None

# Fonction pour nettoyer la colonne "Piece" 
def nettoyer_Piece(data):
    try:
        # Vérifier si data est une chaîne de caractères
        if not isinstance(data, str):
            raise TypeError(f"Erreur : la donnée '{data}' n'est pas une chaîne de caractères.")

        # Supprimer les espaces au début et à la fin
        data = data.strip()

        # Appliquer les transformations de données
        if data.startswith('Emma'):
            return 'ChambreE'
        elif data == 'Salle à manger':
            return 'Salle_manger'
        elif data == 'Chambre':
            return 'ChambreP'
        elif data == 'Couloir Porte':
            return 'Entree'
        elif data == 'couloir':
            return 'CouloirRDC'
        else:
            return data  # Conserve les autres modalités intactes

    except Exception as e:
        # Afficher un message d'erreur via Streamlit si une exception est levée
        st.error(f"❌ Erreur dans le nettoyage de la donnée '{data}': {e}")
        return None

# importer fichier ENEDIS dans bdd.
def importer_csv_dans_bdd(uploaded_file, id_batiment):
    """Importe les données du CSV dans la table ConsoHeureElec en évitant les doublons."""
    if uploaded_file is not None:
        try:
            # Lire le fichier CSV en ignorant les 2 premières lignes
            df = pd.read_csv(uploaded_file, sep=";", skiprows=2)

            # Vérifier que les colonnes existent
            if "Horodate" in df.columns and "Valeur" in df.columns:
                # Sélectionner et renommer les colonnes
                df = df[["Horodate", "Valeur"]]
                df.columns = ["Horodatage", "ValeurW"]

                # Conversion de la colonne Horodatage au format datetime
                df['Horodatage'] = pd.to_datetime(df['Horodatage'], errors='coerce', utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")

                # Ajouter la colonne ID_Batiment
                df["ID_Batiment"] = id_batiment

                # Connexion à la base de données
                conn = get_connection()

                # Récupérer les dates déjà présentes en base
                existing_dates = get_existing_dates(conn, id_batiment)

                # Filtrer pour ne garder que les nouvelles données
                df_new = df[~df["Horodatage"].isin(existing_dates)]

                if df_new.empty:
                    st.warning("Toutes les données de ce fichier existent déjà en base. Rien à insérer.")
                else:
                    # Insérer uniquement les nouvelles données
                    df_new.to_sql("ConsoHeureElec", conn, if_exists="append", index=False)
                    st.success(f"{len(df_new)} nouvelles lignes insérées pour l'ID_Batiment {id_batiment}.")
                    st.write("Aperçu des nouvelles données importées :")
                    st.dataframe(df_new.head())

            else:
                st.error("Les colonnes 'Horodate' et 'Valeur' sont introuvables dans le fichier CSV.")

        except Exception as e:
            st.error(f"Erreur lors du traitement du fichier : {e}")

# importer fichier GAZ dans bdd.
def importer_csv_GAZ_bdd(uploaded_file, id_batiment):
    """Importe les données du fichier gaz dans la table ConsoJourGaz en évitant les doublons."""

    if uploaded_file is not None:
        try:
            # Lecture du fichier CSV sans skiprows
            df = pd.read_csv(uploaded_file,  parse_dates=["Date de consommation"], dayfirst=True,sep=";", encoding="latin1", skiprows=2)
            # Vérification des colonnes
            expected_cols = ["Date de consommation", "Consommation (m3)", "Coefficient de conversion"]
            if not all(col in df.columns for col in expected_cols):
                st.error(f"Colonnes manquantes. Colonnes attendues : {expected_cols}")
                st.write("Colonnes trouvées :", df.columns.tolist())
                return None

            # Remplacement des virgules par des points pour les nombres
            df["Consommation (m3)"] = df["Consommation (m3)"].astype(str).str.replace(",", ".")
            df["Coefficient de conversion"] = df["Coefficient de conversion"].astype(str).str.replace(",", ".")

            # Conversion des colonnes
            df["Valeur_m3"] = pd.to_numeric(df["Consommation (m3)"], errors="coerce")
            df["Conversion"] = pd.to_numeric(df["Coefficient de conversion"], errors="coerce")

            # Conversion des dates
            df["Horodatage"] = pd.to_datetime(df["Date de consommation"], errors="coerce")
            df["Horodatage"] = df["Horodatage"].dt.normalize()  # Supprimer les heures

            # Ajout de l’ID bâtiment
            df["ID_Batiment"] = id_batiment

            # Nettoyage des colonnes finales
            df = df[["Horodatage", "Valeur_m3", "Conversion", "ID_Batiment"]]

            # Connexion BDD
            conn = get_connection()

            # Récupération des dates existantes
            existing_dates = get_existing_datesGAZ(conn, id_batiment)

            # Suppression des doublons
            df_new = df[~df["Horodatage"].isin(existing_dates)]

            if df_new.empty:
                st.warning("Toutes les données de ce fichier existent déjà en base. Rien à insérer.")
            else:
                df_new.to_sql("ConsoJourGaz", conn, if_exists="append", index=False)
                st.success(f"{len(df_new)} nouvelles lignes insérées pour l'ID_Batiment {id_batiment}.")
                st.write("Aperçu des nouvelles données importées :")
                st.dataframe(df_new.head())

        except Exception as e:
            st.error(f"Erreur lors du traitement du fichier : {e}")

# Vérification mot de passe
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)


#_________Scraping _____________________________________________________

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-http2")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--incognito")
    # options.add_argument("--headless")  # Active si nécessaire
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.implicitly_wait(15)  # Ajout d’un temps d’attente implicite
    wait = WebDriverWait(driver, 15)
    return driver

def wait_element(driver, by, identifier, timeout=30, clickable=False):
    try:
        wait = WebDriverWait(driver, timeout)
        if clickable:
            return wait.until(EC.element_to_be_clickable((by, identifier)))
        return wait.until(EC.presence_of_element_located((by, identifier)))
    except TimeoutException:
        print(f"❌ Élément non trouvé : {identifier}")
        save_debug_html(driver)
        return None

def save_debug_html(driver):
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("🛠️ Page sauvegardée pour debug : debug_page.html")

def accept_cookies(driver, max_clicks=3):
    for i in range(max_clicks):
        try:
            accept_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "btn_accept_banner"))
            )
            accept_btn.click()
            print(f"🍪 Cookies acceptés (clic {i + 1})")
            time.sleep(5)  # 🔁 Augmenter la pause ici (de 3 à 5 secondes par ex.)
        except TimeoutException:
            if i == 0:
                print("⚠️ Premier clic : Bannière non trouvée ou déjà acceptée")
            else:
                print("✅ Deuxième vérification terminée : rien à cliquer")
            break

    # Attente explicite entre les deux tentatives
    time.sleep(5)  # ⏳ Pause avant de tenter un second bouton "Tout accepter"

    try:
        second_accept_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "btn_accept_banner"))
        )
        second_accept_btn.click()
        print("🍪 Deuxième clic sur 'Tout accepter' effectué.")
        time.sleep(5)  # ⏳ Pause après le clic pour laisser charger
    except TimeoutException:
        print("⚠️ Aucun deuxième bouton 'Tout accepter' trouvé.")

def analyze_page(driver):
    print("📄 Titre de la page :", driver.title)
    print("📄 URL actuelle :", driver.current_url)
    print("📄 Longueur du HTML :", len(driver.page_source))
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f" Nombre d'iframes trouvées : {len(iframes)}")
    for i, iframe in enumerate(iframes):
        print(f"Iframe {i} : {iframe.get_attribute('src')}")
    save_debug_html(driver)

def connexion(driver, url_grdf, grdf_email, grdf_password):
    try:
        driver.get(url_grdf)
        #print("🌐 Navigation vers GRDF")

        # Email
        email_input = wait_element(driver, By.ID, "input27")
        if not email_input:
            raise Exception("Champ email introuvable")
        email_input.send_keys(grdf_email)
        #print("✅ Email saisi")

        suivant_btn1 = wait_element(driver, By.ID, "grdfButton", clickable=True)
        if not suivant_btn1:
            raise Exception("Bouton 'Suivant' après email introuvable")
        suivant_btn1.click()
        #print("✅ Bouton 'Suivant' cliqué après email")

        time.sleep(3)

        # Mot de passe
        password_input = wait_element(driver, By.ID, "input54", timeout=60)
        if not password_input:
            raise Exception("Champ mot de passe introuvable")
        password_input.send_keys(grdf_password)
        print("✅ Mot de passe saisi")

        suivant_btn2 = wait_element(driver, By.ID, "grdfButton", clickable=True)
        if not suivant_btn2:
            raise Exception("Bouton 'Se connecter' introuvable")
        suivant_btn2.click()
        #print("✅ Bouton 'Se connecter' cliqué après mot de passe")

        time.sleep(5)

        accept_cookies(driver)
        analyze_page(driver)

        print("🎉 Connexion réussie")
        return True

    except Exception as e:
        print("❌ Erreur lors de la connexion :", str(e))
        save_debug_html(driver)
        return False

def save_screenshot_with_date(driver: WebDriver, target: str = "full", 
                               numero_pce: str = "unknown", 
                               label: str = "Capture"):
    """
    Enregistre une capture d'écran, soit de la page complète soit d'une section spécifique.
    :param driver: WebDriver Selenium
    :param target: "full" pour toute la page, ou XPATH/CSS pour un élément
    :param numero_pce: Identifiant pour nommer la capture (ex : numéro PCE)
    :param label: Nom logique de la section (ex : "TableauBord", "GraphConso", etc.)
    """
    try:
        # Format de la date
        date_str = datetime.now().strftime("%Y-%m-%d")
        # Nom de fichier structuré
        filename = f"{label}_{numero_pce}_{date_str}.png"

        if target == "full":
            driver.save_screenshot(filename)
        else:
            # Identifier l'élément cible
            try:
                if target.startswith("//"):
                    element = driver.find_element("xpath", target)
                else:
                    element = driver.find_element("css selector", target)
                element.screenshot(filename)
            except Exception as e:
                print(f"⚠️ Échec de la capture ciblée : {e}")
                return

        print(f" Capture enregistrée : {filename}")
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde de la capture : {e}")

#______________________________________________________________

