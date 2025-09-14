import subprocess
import webbrowser
import time

# myenv\Scripts\activate 
# python run_all.py

# Lancer FastAPI
subprocess.Popen('start cmd /k "uvicorn utils.api:app --reload --port 8000"', shell=True)

# Lancer Streamlit
subprocess.Popen('start cmd /k "streamlit run app2.py"', shell=True)

# Attendre quelques secondes pour que Streamlit démarre
time.sleep(5)

# Ouvrir le navigateur sur l'URL de Streamlit
webbrowser.open("http://localhost:8501")

# Ouvrir le navigateur sur l'URL de FastAPI (docs)
webbrowser.open("http://localhost:8000/docs")

print("Les deux applications sont lancées et les navigateurs ouverts.")
