import time
import os
import re
from dotenv import load_dotenv

from utils import (setup_driver,
    wait_element,
    save_debug_html,
    accept_cookies,
    analyze_page,
    connexion,
    save_screenshot_with_date
)

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
________________________

load_dotenv()
grdf_email = os.getenv("EMAIL_GRDF")
grdf_password = os.getenv("GRDF_PASSWORD")
url_grdf = os.getenv("URL_GRDF")

#______________________________________________________________

driver = setup_driver()
driver.delete_all_cookies()

try:
    success = connexion(driver, url_grdf, grdf_email, grdf_password)

    if success:
        numero_pce = "inconnu"  # Définition par défaut

        try:
            # Nom du compteur
            alias_element = driver.find_element(By.CSS_SELECTOR, "span.pceAlias")
            alias_text = alias_element.text.strip()
            print("🏠 Nom du compteur :", alias_text)

            # Tentative de récupération du numéro PCE
            pce_element = None
            selectors = [
                "p.pce-id-content-pce-number",
                "div.pce-id-content-pce-number",
                "span.pce-id-content-pce-number"
            ]
            for sel in selectors:
                try:
                    el = driver.find_element(By.CSS_SELECTOR, sel)
                    if el.text.strip():
                        pce_element = el
                        break
                except:
                    continue

            if pce_element:
                raw_text = pce_element.text.strip()
                match = re.search(r"(?:N°\s*PCE)?\s*([\d\s]{10,})", raw_text)
                if match:
                    numero_pce = match.group(1).replace(" ", "")
                    print("✅ Numéro PCE nettoyé :", numero_pce)
                else:
                    print("⚠️ Numéro PCE non trouvé dans :", raw_text)
            else:
                print("⚠️ Aucun élément correspondant aux sélecteurs PCE")

        except Exception as e:
            print("❌ Erreur récupération PCE :", e)

        # Captures ciblées: 
        save_screenshot_with_date(driver, target="full", numero_pce=numero_pce, label="TableauBord")

        save_screenshot_with_date(
            driver, target="div.conso-transmises-resume-body", 
            numero_pce=numero_pce, label="Maitrise_Energie"
        )

        save_screenshot_with_date(
            driver, target="ecg-meg-comparaison-foyer-similaire-dashboard-graph",
            numero_pce=numero_pce, label="Donnee_Transmise"
        )

        time.sleep(3)

        # Capture finale de l’étiquette énergétique 
        save_screenshot_with_date(
            driver,
            target="div.etiquette-container",  
            numero_pce=numero_pce,
            label="Etiquette_Energie"
        )

        # Attente explicite de la section consommation
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ecg-conso-details"))
        )

    else:
        print("❌ Connexion échouée, aucune capture réalisée.")

except Exception as e:
    print("❌ Erreur générale :", str(e))

finally:
    input("\n🛑 Appuie sur [Entrée] pour fermer le navigateur...")
    driver.quit()
