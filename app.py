import streamlit as st
import pandas as pd
from graphique import graphique1, graphique2, graphique3, graphique4, graphique_grand
import plotly.express as px

# ---------------------------
# Charger DataFrame
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_pickle("df_nettoye.pkl")
    df["patho_niv1"] = df["patho_niv1"].astype(str).str.strip()
    df["patho_niv2"] = df["patho_niv2"].astype(str).str.strip()
    return df

df = load_data()

st.set_page_config(layout="wide")

# ---------------------------
# Sélection patho1
# ---------------------------
toutes_les_pathos = sorted(df["patho_niv1"].dropna().unique())
patho1 = st.selectbox("Choisir une pathologie (niv1)", toutes_les_pathos)

# Filtrer df pour patho1
df_patho1 = df[df["patho_niv1"] == patho1]

# ---------------------------
# Sélection patho2
# ---------------------------
sous_pathos_disponibles = sorted(df_patho1["patho_niv2"].dropna().unique())
patho2 = st.multiselect("Choisir une ou plusieurs sous-pathologies (niv2)", sous_pathos_disponibles)

# Filtrer selon patho2
df_graph = df_patho1
if patho2:
    df_graph = df_graph[df_graph["patho_niv2"].isin(patho2)]

# ---------------------------
# Vérification des données
# ---------------------------
if df_graph.empty:
    st.warning("Aucune donnée disponible pour ces sélections.")
else:
    st.success(f"Données prêtes pour {patho1} et {len(patho2)} sous-pathologies sélectionnées.")

# ---------------------------
# Affichage des graphiques
# ---------------------------
st.header("Visualisation prévalence par sexe et année")

# Grille 2x2 élargie
col1, col2 = st.columns([3, 3], gap="medium")
with col1:
    st.plotly_chart(graphique1(df_graph, patho1), use_container_width=True)
with col2:
    st.plotly_chart(graphique2(df_graph, patho1), use_container_width=True)

col3, col4 = st.columns([3, 3], gap="medium")
with col3:
    st.plotly_chart(graphique3(df_graph, patho1), use_container_width=True)
with col4:
    st.plotly_chart(graphique4(df_graph, patho1), use_container_width=True)

# Grand graphique plein écran
st.subheader("Grand graphique de synthèse")
st.plotly_chart(graphique_grand(df_graph, patho1), use_container_width=True)
