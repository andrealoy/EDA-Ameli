import streamlit as st
import pandas as pd
from graphique import graphique1, graphique2, graphique3, graphique4, graphique_grand
import plotly.express as px

# ---------------------------
# Config page 
# ---------------------------
st.set_page_config(layout="wide")

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

# ---------------------------
# Titre et zone de texte
# ---------------------------
st.header("🔬 Analyse des pathologies")

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

- **Nombre total de données :** **78 837 770**
                
- **❗ Nombre de valeurs manquantes total :** **4 624 630**

- **Interprétation mathématique :** Le profil des courbes a été déterminé en effectuant une régression linéaire afin d’obtenir la pente, la p-value et le pourcentage de variation, permettant ainsi de conclure sur l’évolution de la variable au fil du temps. 

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
# Variable figée pour graphique4 A suuprimer plus tard
# ---------------------------
# if "patho1_graph4" not in st.session_state:
#     st.session_state["patho1_graph4"] = patho1
# if st.session_state["patho1_graph4"] != patho1:
#     st.session_state["patho1_graph4"] = patho1
# patho1_a_afficher_graph4 = st.session_state["patho1_graph4"]

# # df_graph pour graphique4 (ne dépend que de patho1)
# df_graph4 = df[df["patho_niv1"] == patho1_a_afficher_graph4]

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
# bornes du slider à partir des années présentes dans le df
# (robuste si colonne année est string)
# ---------------------------
annee_series = pd.to_numeric(df["annee"], errors="coerce").dropna().astype(int)
if not annee_series.empty:
    annee_min = int(annee_series.min())
    annee_max = int(annee_series.max())
else:
    # valeurs par défaut sûres
    annee_min, annee_max = 2015, 2023

# --- SLIDER placé juste après la sélection de patho2 ---
annee_sel = st.slider(
    "Choisir l'année",
    min_value=annee_min,
    max_value=annee_max,
    value=annee_max,
    step=1,
    key="annee_sel"
)

# --- FILTRES GEO (éventuels) ---
dept = ["999"]
region = [99]

st.subheader(f"Visualisation des données {patho1} / {patho2} pour {annee_sel}")

# ---------------------------
# Helper : appeler la fonction de graphique en essayant d'envoyer annee_sel si possible
# ---------------------------
def call_with_optional_year(func, *args, year=None):
    """
    Essaie d'appeler func(..., annee_sel=year). Si la signature ne le permet pas,
    retombe sur func(...).
    """
    if year is None:
        return func(*args)
    try:
        # premier essai : appeler en passant annee_sel nommé
        return func(*args, annee_sel=year)
    except TypeError:
        # si la fonction ne prend pas annee_sel, on l'appelle sans
        return func(*args)

# ---- Grille 2x2 pour les 4 graphiques (placeholders) ----
col1, col2 = st.columns([3, 3], gap="medium")
with col1:
    placeholder_g1 = st.empty()
with col2:
    placeholder_g2 = st.empty()

col3, col4 = st.columns([3, 3], gap="medium")
with col3:
    placeholder_g3 = st.empty()
with col4:
    placeholder_g4 = st.empty()

# ---- Générer tous les graphiques (le wrapper gère si la fonction accepte annee_sel ou pas) ----
fig1 = call_with_optional_year(graphique1, df_graph1, patho1_a_afficher_graph1, year=annee_sel)
fig2 = call_with_optional_year(graphique2, df_graph2, patho1, year=annee_sel)
fig3 = call_with_optional_year(graphique3, df_graph2, patho1, year=annee_sel)
fig4 = call_with_optional_year(graphique4, df_graph4, patho1_a_afficher_graph4, year=annee_sel)

# ---- Afficher les graphiques ----
placeholder_g1.plotly_chart(fig1, use_container_width=True)
placeholder_g2.plotly_chart(fig2, use_container_width=True)
placeholder_g3.plotly_chart(fig3, use_container_width=True)
placeholder_g4.plotly_chart(fig4, use_container_width=True)

# Grand graphique plein écran (on essaye de lui passer l'année aussi)
st.subheader("Grand graphique de synthèse")
fig_grand = call_with_optional_year(graphique_grand, df_graph2, patho1, year=annee_sel)
st.plotly_chart(fig_grand, use_container_width=True)
