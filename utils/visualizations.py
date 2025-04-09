import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
import pandas as pd


# Fonction pour afficher les graphiques d'Enedis
def afficher_graphiqueGaz(df, period='jour'):
    if df is None:
        st.error("Les données de gaz n'ont pas pu être chargées.")
        return

    df['Horodatage'] = pd.to_datetime(df['Horodatage'], errors='coerce')

    if period == 'année':
        df_grouped = df.groupby(df['Horodatage'].dt.year)['Valeur_m3'].sum()
    elif period == 'mois':
        df_grouped = df.groupby(df['Horodatage'].dt.to_period('M'))['Valeur_m3'].sum()
    elif period == 'jour':
        df_grouped = df.groupby(df['Horodatage'].dt.date)['Valeur_m3'].sum()
    else:
        st.warning("Période non reconnue.")
        return

    plt.figure(figsize=(10, 6))
    df_grouped.plot(kind='bar', color='skyblue')
    plt.title(f"Consommation de gaz en m3 par {period}", fontsize=16)
    plt.xlabel(f"Date ({period})", fontsize=12)
    plt.ylabel("Consommation en m3", fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt)

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