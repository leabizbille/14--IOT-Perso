from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

import time
import os
from dotenv import load_dotenv

#______________________________________________________________

load_dotenv()
edf_email = os.getenv("EMAIL_EDF")
edf_password = os.getenv("EDF_PASSWORD")
url_edf = os.getenv("URL_EDF")
url_edf_facture = os.getenv("URL_EDF_FACTURE")

#______________________________________________________________

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-http2")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--incognito")
    # Uncomment the next line if you want headless mode:
    # options.add_argument("--headless")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def wait_element(driver, by, identifier, timeout=30, clickable=False):
    try:
        wait = WebDriverWait(driver, timeout)
        if clickable:
            return wait.until(EC.element_to_be_clickable((by, identifier)))
        return wait.until(EC.presence_of_element_located((by, identifier)))
    except TimeoutException:
        print(f"❌ Élément non trouvé : {identifier}")
        save_debug_html(driver)
        driver.quit()
        exit()

def save_debug_html(driver):
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("🛠️ Page sauvegardée pour debug : debug_page.html")

#______________________________________________________________

driver = setup_driver()
driver.delete_all_cookies()
driver.get_log('browser')

try:
    print("🌐 Accès au site EDF...")
    driver.get(url_edf)

    # Cookies
    try:
        accepter_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accepter') or contains(text(), 'Tout accepter')]"))
        )
        accepter_btn.click()
        print("✅ Cookies acceptés")
    except TimeoutException:
        print("⚠️ Aucun bandeau cookies détecté")

    driver.refresh()

    # Email
    email_input = wait_element(driver, By.ID, "email")
    email_input.send_keys(edf_email)
    print("✅ Email saisi")

    suivant_btn1 = wait_element(driver, By.ID, "username-next-button", clickable=True)
    suivant_btn1.click()
    print("✅ Bouton 'Suivant' cliqué après email")

    # Mot de passe
    print("⏳ Attente du champ mot de passe...")
    password_input = wait_element(driver, By.ID, "password2-password-field", timeout=60)
    if password_input:
        password_input.send_keys(edf_password)
        print("✅ Mot de passe saisi")
    else:
        print("⚠️ Le champ mot de passe n'a pas été trouvé.")

    suivant_btn2 = wait_element(driver, By.ID, "password2-next-button", clickable=True)
    suivant_btn2.click()
    print("✅ Bouton 'Suivant' cliqué après mot de passe")

    # Sélection téléphone ( à partir d'ici, le bouton radio est bien sélectionné, mais il ne se passe rien)
    radio_button = wait_element(driver, By.ID, "callback_0_0", clickable=True)
    driver.execute_script("arguments[0].click();", radio_button)

    print("✅ Option téléphone sélectionnée")

    time.sleep(2)  # Pause pour éviter d’aller trop vite

    suivant_btn3 = wait_element(driver, By.ID, "hotpcust3-next-button")
    WebDriverWait(driver, 30).until(lambda d: suivant_btn3.get_attribute("aria-disabled") == "false")
    suivant_btn3.click()
    print("✅ Bouton 'Suivant' cliqué après sélection")

    # Code reçu par SMS
    code_input = WebDriverWait(driver, 90).until(
        EC.visibility_of_element_located((By.ID, "code-seizure__field"))
    )

    code = input("📲 Entrez le code reçu par SMS : ")
    code_input.send_keys(code)
    print("✅ Code saisi")

    suivant_btn5 = wait_element(driver, By.ID, "hotpcust4-next-button", clickable=True)
    suivant_btn5.click()
    print("✅ Connexion validée avec le code")

    # Espace client chargé
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Bienvenue') or contains(text(), 'Votre espace client')]"))
    )
    print("✅ Connexion réussie : ", driver.title)

    # Accès à la page des factures
    driver.get(url_edf_facture)
    print("📥 Ouverture de la page des factures...")
    time.sleep(10)

    factures = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
    print(f"\n📄 {len(factures)} facture(s) trouvée(s) :")
    for facture in factures:
        print(f"- {facture.text.strip()} → {facture.get_attribute('href')}")

    # Logs JS (optionnel)
    for log in driver.get_log('browser'):
        print(log)

finally:
    input("\n🛑 Appuie sur [Entrée] pour fermer le navigateur...")
    driver.quit()
