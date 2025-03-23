import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st


# Fonction pour afficher les graphiques d'Enedis
def afficher_graphique(df, period='jour'):
    # Grouper les données en fonction de la période choisie
    if period == 'année':
        df_grouped = df.groupby(df['Horodatage'].dt.year)['ValeurW'].sum()
    elif period == 'mois':
        df_grouped = df.groupby(df['Horodatage'].dt.to_period('M'))['ValeurW'].sum()
    elif period == 'jour':
        df_grouped = df.groupby(df['Horodatage'].dt.date)['ValeurW'].sum()
    elif period == 'heure':
        df_grouped = df.groupby(df['Horodatage'].dt.hour)['ValeurW'].sum()

    # Affichage du graphique
    plt.figure(figsize=(10, 6))
    df_grouped.plot(kind='bar', color='skyblue')
    plt.title(f"Consommation électrique par {period}", fontsize=16)
    plt.xlabel(f"Date ({period})", fontsize=12)
    plt.ylabel("Consommation en W", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)