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
    df["patho_niv2_simplifie"] = df["patho_niv2_simplifie"].astype(str).str.strip()
    return df

df = load_data()
st.set_page_config(layout="wide")

# ---------------------------
# Tire et zone de texte
# ---------------------------
st.header("Analyse des pathologies")


st.write("""
L’application permet de sélectionner une **pathologie principale (niv1)** ainsi que ses **sous-pathologies simplifiées (niv2)**, 
puis affiche les données sous forme de **graphiques interactifs** par sexe et par année. Elle permet un suivi clair des tendances et prévalences en France **entre 2015 et 2023**.""")


### 📊 Informations générales sur le jeu de données
with st.expander("Informations générales sur le jeu de données", expanded=False):
    st.markdown("""
**📌 Source et origine :**  
  *Data.gouv — Dataset Pathologies : effectif de patients par pathologie, sexe, classe d'âge et territoire*  
  Produit par la **Caisse nationale de l'Assurance Maladie (Cnam)**.

- **🔢 Nombre d’observations :** **5 216 400**

- **🧱 Nombre de variables :** **16**

- **🔠 Types de variables :**  
  - `float64` : 3  
  - `int64` : 4  
  - `object` : 9

- **❗ Nombre de valeurs manquantes par variable :** *(voir tableau ci-dessous)*

---
""")


# ---------------------------
# Selectbox unique pour patho1
# ---------------------------
toutes_les_pathos = sorted(df["patho_niv1"].dropna().unique())
patho1 = st.selectbox("Choisir une pathologie (niv1)", toutes_les_pathos)

# ---------------------------
# Variable figée pour graphique1
# ---------------------------
if "patho1_graph1" not in st.session_state:
    st.session_state["patho1_graph1"] = patho1

if st.session_state["patho1_graph1"] != patho1:
    st.session_state["patho1_graph1"] = patho1

patho1_a_afficher_graph1 = st.session_state["patho1_graph1"]

# df_graph pour graphique1 (ne dépend que de patho1)
df_graph1 = df[df["patho_niv1"] == patho1_a_afficher_graph1]

# ---------------------------
# Variable figée pour graphique4
# ---------------------------
if "patho1_graph4" not in st.session_state:
    st.session_state["patho1_graph4"] = patho1

if st.session_state["patho1_graph4"] != patho1:
    st.session_state["patho1_graph4"] = patho1

patho1_a_afficher_graph4 = st.session_state["patho1_graph4"]

# df_graph pour graphique4 (ne dépend que de patho1)
df_graph4 = df[df["patho_niv1"] == patho1_a_afficher_graph4]

# ---------------------------
# df_graph pour les autres graphiques (dépend de patho1 et patho2 simplifié)
# ---------------------------
df_graph2 = df[df["patho_niv1"] == patho1]

# Sélection patho2 simplifié
sous_pathos_disponibles = sorted(df_graph2["patho_niv2_simplifie"].dropna().unique())
patho2 = st.multiselect("Choisir une ou plusieurs sous-pathologies (niv2)", sous_pathos_disponibles)

if patho2:
    df_graph2 = df_graph2[df_graph2["patho_niv2_simplifie"].isin(patho2)]

# ---------------------------
# Vérification des données
# ---------------------------
if df_graph2.empty:
    st.warning("Aucune donnée disponible pour ces sélections.")
else:
    st.success(f"Données prêtes pour {patho1} et {len(patho2)} sous-pathologies sélectionnées.")

# ---------------------------
# Affichage des graphiques
# ---------------------------

col1, col2 = st.columns([3, 3], gap="medium")
with col1:
    st.plotly_chart(graphique1(df_graph1, patho1_a_afficher_graph1), use_container_width=True)  # figée patho2
with col2:
    st.plotly_chart(graphique2(df_graph2, patho1), use_container_width=True)

col3, col4 = st.columns([3, 3], gap="medium")
with col3:
    st.plotly_chart(graphique3(df_graph2, patho1), use_container_width=True)
with col4:
    st.plotly_chart(graphique4(df_graph4, patho1_a_afficher_graph4), use_container_width=True)  # figée patho2

# Grand graphique plein écran
st.subheader("Grand graphique de synthèse")
st.plotly_chart(graphique_grand(df_graph2, patho1), use_container_width=True)
