# scraper.py
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

url_edf_prix = os.getenv("URL_EDF_PRIX")

#______________________________________________________________

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-http2")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--incognito")
    # options.add_argument("--headless")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_pdf_urls():
    # Accès à la page des factures
    driver = setup_driver()
    driver.get(url_edf_prix)
    print("📥 Ouverture de la page des prix")
    time.sleep(5)

    # Cookies
    try:
        accepter_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accepter') or contains(text(), 'Tout accepter')]"))
        )
        accepter_btn.click()
        print("✅ Cookies acceptés")
    except TimeoutException:
        print("⚠️ Aucun bandeau cookies détecté")

    # Recherche des fichiers PDF
    prix = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf')]")
    print(f"\n📄 {len(prix)} pdf(s) trouvée(s) :")
    pdf_urls = []
    for pdf in prix:
        pdf_urls.append(pdf.get_attribute('href'))
        print(f"- {pdf.text.strip()} → {pdf.get_attribute('href')}")
    
    # Fermer le driver après avoir récupéré les données
    driver.quit()
    
    return pdf_urls

# if __name__ == "__main__":
#     pdf_urls = get_pdf_urls()
#     print(f"URLs des PDF récupérées : {pdf_urls}")
