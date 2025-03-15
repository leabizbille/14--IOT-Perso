
Launch the application :
fastapi dev main.py

# Pour le serveur : 
uvicorn main:app --reload --host=0.0.0.0

# effacer les connexions sur le port 8000 :
netstat -ano | findstr :8000

Mon Adresse IPv4 192.168.0.105

where python    # Version python et localisation sur ordi.
# 1 Environnement  -----------------------------------------------------------------
python -m venv myenv
myenv\Scripts\activate       # Environnement

# 2 Git Ignore ---------------------------------------------------------------------

pip install -r requirements.txt
pip install bleak --force-reinstall
pip install visions[type_image_path]==0.7.4
pip install --upgrade pip


#------------------------------------------------------------------
python govee-h5075.py -m      # récuperation des data températures et modules
python govee-h5075.py -s

#------------------------------------------------------------------
# Pour mettre en fonction streamlit 
streamlit run Streamlit_BaseBatiment.py

#------------------------------------------------------------------
Mettre le fichier .known_govees dans le fichier C:\Users\Lau
