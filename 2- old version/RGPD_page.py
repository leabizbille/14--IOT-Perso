import streamlit as st
from datetime import date

def afficher_page_rgpd():
    st.set_page_config(page_title="Protection des données Candidats", layout="wide")

    st.title("🔒 Données personnelles")

    col1, col2 = st.columns([2, 1])  # Texte explicatif à gauche, formulaire à droite

    with col1:
        st.markdown("""
        <div style='text-align: justify'>
        En créant un compte sur notre plateforme IoT, certaines données personnelles seront collectées.  
        Nous respectons scrupuleusement le <strong>Règlement Général sur la Protection des Données (RGPD)</strong> et la <strong>loi Informatique et Libertés</strong>.
        Ces données incluent vos consommations énergétiques (électricité, gaz, température), ainsi que les informations issues des formulaires sur les bâtiments et pièces.  
        Elles permettent de créer des outils intelligents pour mieux comprendre vos usages et améliorer nos services.
        Nous utilisons une intelligence artificielle pour analyser ces données. Aucune décision n'est prise sans votre consentement.
        Vos informations ne sont partagées qu’avec nos administrateurs et sont conservées au maximum 1 an.
        Vous disposez à tout moment de droits d'accès, de rectification, de suppression ou d'opposition. Pour toute question, contactez <strong>Mme X</strong>  
        👉 <a href='mailto:madame_x@gmail.com'>madame_x@gmail.com</a>

        🔗 Plus d’infos : <a href='https://www.cnil.fr' target='_blank'>www.cnil.fr</a>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        st.markdown("""
        **Base légale :**  Votre consentement explicite (article 6.1.a du RGPD). En cas de traitement automatisé, l’article 22 s’applique.
        **Finalité :**  Développer un modèle d’IA permettant d’optimiser les consommations et de comprendre les variations environnementales entre intérieur et extérieur.
        """)
        st.divider()

    with col2:
        st.header("📝 Formulaire de consentement")
        with st.form("consent_form"):
            name = st.text_input("Nom et prénom")
            today = st.date_input("Date", value=date.today())
            agree_1 = st.checkbox("J’accepte que mes données soient utilisées.")
            agree_2 = st.checkbox("Je consens au traitement automatisé de mes données.")
            submitted = st.form_submit_button("Soumettre")

        if submitted:
            if agree_1 and agree_2:
                st.success("✅ Merci, votre consentement a bien été enregistré.")
                st.write("**Nom :**", name)
                st.write("**Date :**", today)
                st.write("**Consentement :** ✔️ donné (y compris IA)")
            else:
                st.error("⚠️ Vous devez accepter les deux conditions pour valider votre consentement.")

# Pour test local
if __name__ == "__main__":
    afficher_page_rgpd()
