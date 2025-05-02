import streamlit as st
from datetime import date

st.set_page_config(page_title="Protection des données Candidats", layout="centered")

st.title("🔒 Protection des données personnelles des candidats")
st.markdown("""
Dans le cadre de votre candidature, certaines de vos données personnelles sont collectées. 
Conformément au **Règlement Général sur la Protection des Données (RGPD)** et à la **loi Informatique et Libertés**, 
nous vous informons ci-dessous de l'usage de vos données et de vos droits.
""")

st.header("📌 Responsable du traitement")
st.markdown("""
Adresse : [Adresse]  
Téléphone : 00 00 00 00 00 
Déléguée à la protection des données : **Mme X**  
Email : [X@gmail.com](mailto:X@gmail.com)  
Téléphone : 01 00 00 00 00
""")

st.header("📁 Données collectées")
st.markdown("""
Les informations personnelles suivantes peuvent être collectées :  
- Nom, prénom  
- Email, téléphone, adresse  
- Activité professionnelle actuelle  
- Parcours professionnel, diplômes
""")

st.header("🎯 Finalité et usage des données")
st.markdown("""
Les données sont utilisées pour :  
- La gestion des candidatures dans le cadre d’un processus de recrutement  
- L’évaluation de votre profil par les équipes RH et les recruteurs  
- L’alimentation d’un vivier de talents (avec votre consentement)
""")

st.header("🤖 Décision automatisée par IA")
st.markdown("""
Une **intelligence artificielle** sera utilisée pour **analyser automatiquement** votre CV, 
notamment en comparant votre CV aux exigences des postes à pourvoir.

> Cette prise de décision **automatisée** vise à **évaluer la correspondance avec un poste**, en aucun cas .

⚠️ **Conséquences pour vous :**  
- Cette analyse algorithmique **peut influencer les étapes suivantes** de votre candidature.  
- Vous avez le **droit de demander une intervention humaine**, d'exprimer votre point de vue ou de contester la décision.
""")

st.header("⚖️ Base légale du traitement")
st.markdown("""
Le traitement est fondé sur **votre consentement explicite** (article 6.1.a du RGPD).  
En cas d'IA, la base est **l’article 22** du RGPD sur la prise de décision automatisée.
""")

st.header("📤 Destinataires des données")
st.markdown("""
Les données collectées sont destinées uniquement à :  
- L’équipe RH / recrutement  
- Les administrateurs de la base de données  
""")

st.header("⏳ Durée de conservation")
st.markdown("""
Les données sont conservées pendant une durée maximale de **1 an** à compter de la fin du processus de recrutement.
""")

st.header("✅ Vos droits")
st.markdown("""
Vous pouvez à tout moment exercer les droits suivants sur vos données :  
- Accès, rectification, effacement  
- Limitation ou opposition au traitement  
- Portabilité  
- Retrait de votre consentement à tout moment  

📌 Pour toute demande, contactez : **Mme X** à [X@gmail.com](mailto:X@gmail.com) ou au 01 00 00 00 00.

🔗 Pour plus d'informations sur vos droits : [www.cnil.fr](https://www.cnil.fr)
""")

st.header("📝 Consentement")

with st.form("consent_form"):
    name = st.text_input("Votre nom et prénom")
    today = st.date_input("Date", value=date.today())
    agree_1 = st.checkbox("✅ J’ai pris connaissance de l’utilisation de mes données personnelles.")
    agree_2 = st.checkbox("✅ Je consens à l’utilisation de mes données dans le cadre de ce recrutement, y compris par une IA.")
    submitted = st.form_submit_button("Soumettre")

if submitted:
    if agree_1 and agree_2:
        st.success("Merci ! Vos préférences ont été enregistrées.")
        st.write("**Nom :**", name)
        st.write("**Date :**", today)
        st.write("**Consentement :** ✔️ donné (y compris traitement automatisé)")
    else:
        st.error("⚠️ Vous devez donner votre consentement pour continuer le processus de candidature.")
