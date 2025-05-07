from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

import time
import os
import re
from dotenv import load_dotenv

#______________________________________________________________

load_dotenv()
grdf_email = os.getenv("EMAIL_GRDF")
grdf_password = os.getenv("GRDF_PASSWORD")
url_grdf = os.getenv("URL_GRDF")

#______________________________________________________________

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
    driver.implicitly_wait(5)  # Ajout d’un temps d’attente implicite
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
        print("🌐 Navigation vers GRDF")

        # Email
        email_input = wait_element(driver, By.ID, "input27")
        if not email_input:
            raise Exception("Champ email introuvable")
        email_input.send_keys(grdf_email)
        print("✅ Email saisi")

        suivant_btn1 = wait_element(driver, By.ID, "grdfButton", clickable=True)
        if not suivant_btn1:
            raise Exception("Bouton 'Suivant' après email introuvable")
        suivant_btn1.click()
        print("✅ Bouton 'Suivant' cliqué après email")

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
        print("✅ Bouton 'Se connecter' cliqué après mot de passe")

        time.sleep(5)

        accept_cookies(driver)
        analyze_page(driver)

        print("🎉 Connexion réussie")
        return True

    except Exception as e:
        print("❌ Erreur lors de la connexion :", str(e))
        save_debug_html(driver)
        return False

#______________________________________________________________

driver = setup_driver()
driver.delete_all_cookies()

try:
    success = connexion(driver, url_grdf, grdf_email, grdf_password)

    if success:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Tableau de bord')]"))
        )
        print("✅ Connexion confirmée sur le tableau de bord :", driver.title)

        # 🔍 Nom du compteur
        try:
            alias_element = driver.find_element(By.CSS_SELECTOR, "span.pceAlias")
            alias_text = alias_element.text.strip()
            print("🏠 Nom du compteur :", alias_text)
        except Exception as e:
            print("❌ Erreur nom compteur :", str(e))
            print("🔎 Affichage de tous les spans disponibles pour debug :")
            for s in driver.find_elements(By.TAG_NAME, "span")[:10]:
                print("➡️", s.get_attribute("class"), ":", s.text.strip())

        # 🔍 Numéro PCE
        try:
            pce_element = None
            candidates = [
                "p.pce-id-content-pce-number",
                "div.pce-id-content-pce-number",
                "span.pce-id-content-pce-number"
            ]
            for selector in candidates:
                try:
                    pce_element = driver.find_element(By.CSS_SELECTOR, selector)
                    if pce_element.text.strip():
                        break
                except:
                    continue

            if not pce_element:
                raise Exception("Aucun élément avec les sélecteurs PCE attendus")

            pce_text = pce_element.text.strip()
            print("🔢 Numéro PCE brut :", pce_text)

            match = re.search(r"(?:N°\s*PCE)?\s*([\d\s]{10,})", pce_text)
            if match:
                numero_pce = match.group(1).replace(" ", "")
                print("✅ Numéro PCE nettoyé :", numero_pce)
            else:
                print("⚠️ Numéro PCE non trouvé dans le texte :", pce_text)

        except Exception as e:
            print("❌ Erreur numéro PCE :", str(e))
            print("🔎 Tous les paragraphes disponibles pour debug :")
            for p in driver.find_elements(By.TAG_NAME, "p")[:10]:
                print("➡️", p.get_attribute("class"), ":", p.text.strip())

        driver.save_screenshot("screenshot.png")
        print("🖼️ Capture d'écran enregistrée : screenshot.png")

finally:
    input("\n🛑 Appuie sur [Entrée] pour fermer le navigateur...")
    driver.quit()
