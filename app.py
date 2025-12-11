import streamlit as st
import pandas as pd    
import graphs as gr
import map as mp
import stats as stt

# ---------------------------------------
# 🔹 Config
# ---------------------------------------
st.set_page_config(layout="wide")

# ---------------------------------------
# 🔹 Chargement du dataset (cache pour vitesse)
# ---------------------------------------
@st.cache_data
def load_data():
    return pd.read_parquet("datasets/df_cleaned.parquet")

df = load_data()

# -----------------------------------------------------------
# 🔹 Titre de l'application et présentation du jeu de données
# -----------------------------------------------------------


st.title("Explorateur de pathologies – Données Santé")
with st.container():
    col1, col2 = st.columns([3,2])
    
    with col1:
        st.markdown("""
        ## 🩺 Analyse des pathologies en France
        Données issues de sources publiques (Ameli)
        """)

    with col2:
        st.markdown("### 📌 Aperçu du dataset")
        st.metric("Rows", f"{df.shape[0]:,}")
        st.metric("Columns", f"{df.shape[1]:,}")

st.expander("Résumé du DataFrame").markdown("""
# ## 📊 **Résumé du DataFrame**

# ### **Structure générale**
# - **16 colonnes**, ~**636.8 MB**
# - Types : **int64 (4)**, **float64 (3)**, **object (9)**
# - Dataset volumineux avec beaucoup de variables catégorielles.

# ### **Description des variables**
# - **annee (int64)** : année d’observation  
# - **patho_niv1/2/3 (object)** : hiérarchie de pathologies  
# - **top (object)** : code topographique  
# - **cla_age_5 (object)** : classe d’âge (tranches de 5 ans)  
# - **sexe (int64)** : code sexe  
# - **region (int64)** : code région  
# - **dept (object)** : département  
# - **Ntop (float64)** : nombre de cas observés  
# - **Npop (int64)** : population  
# - **prev (float64)** : prévalence  
# - **Niveau prioritaire (object)** : catégorie de priorité  
# - **libelle_classe_age / libelle_sexe (object)** : libellés descriptifs  
# - **tri (float64)** : valeur de tri / score

# ### **Valeurs manquantes**
# - **patho_niv2 : 544 320**  
# - **patho_niv3 : 1 179 360**  
# - **Ntop : 1 382 435**  
# - **prev : 1 382 435**  
# - **Niveau prioritaire : 68 040**  
# - **tri : 68 040**  
# - Colonnes sans NaN : **annee, cla_age_5, sexe, region, dept, libelle_classe_age, libelle_sexe**

# ### **Points clés**
# - Structure hiérarchique pathologique : **niv1 complet**, niv2 et niv3 partiellement définis.  
# - **Ntop** et **prev** manquent ensemble → calcul de la prévalence impossible pour ces enregistrements. 
# - Beaucoup de colonnes object → **conversion en `category`** pour réduire l’usage mémoire.  
# """)
# -----------------------------------------------------------
# 🔹 Statistiques
# -----------------------------------------------------------
colA, colB = st.columns([2, 1])  # colonne texte + colonne metrics rapides


col1, col2, col3, col4 = st.columns(4)

with col1:
    stt.display_demographic_metrics(df)

with col2:
    stt.display_geographic_metrics(df)

with col3:
    stt.display_pathology_metrics(df)

with col4:
    stt.display_numeric_metrics(df)


# ---------------------------------------
# 🔹 SIDEBAR : choix de la pathologie et de l'année
# ---------------------------------------
# Sidebar – choix de la pathologie et année (slider)
st.sidebar.header("Filtres")

patho_list = sorted(df["patho_niv1"].dropna().unique())
annee_min = int(df["annee"].min())
annee_max = int(df["annee"].max())

selected_patho = st.sidebar.selectbox("Sélectionner une pathologie (niv1)", patho_list)

all_years = st.sidebar.checkbox("Toutes les années", value=False)

if all_years:
    selected_year = "Toutes"
else:
    selected_year = st.sidebar.slider(
        "Sélectionner une année",
        min_value=annee_min,
        max_value=annee_max,
        value=annee_max,     # par défaut = dernière année
        step=1
    )


# ---------------------------------------
# 🔹 Filtrer le dataset selon les choix
# ---------------------------------------
df_filtered = df[
    (df["patho_niv1"] == selected_patho)
]

if all_years:
    df_filtered_year = df_filtered
else:
    df_filtered_year = df_filtered[pd.to_numeric(df_filtered["annee"], errors="coerce") == selected_year]

# ---------------------------------------
# 🔹 Affichage
# ---------------------------------------
st.header(f"{len(df_filtered_year):,} cas pour : {selected_patho} en France en {selected_year}")

# ---------------------------------------
# 🔹 Génération des graphiques
# ---------------------------------------

# Données agrégées pour l'analyse temporelle
df_grouped = gr.group_by_year_and_calculate_mean_prev(df_filtered)

# Graphiques de prévalence par sexe (utilise df_filtered pour toutes les années)
fig_prev_femmes = gr.plot_prevalence_sex(df_filtered, sexcode=2)
fig_prev_hommes = gr.plot_prevalence_sex(df_filtered, sexcode=1)
fig_diff_prev_sexe = gr.plot_prevalence_difference_sex(df_filtered)

# Graphiques temporels (COVID-19)
fig_prev_time = gr.plot_real_vs_expected_prevalence(df_grouped)

# Graphiques pour l'année sélectionnée (utilise df_filtered_year)
fig_repartition_sexe = gr.plot_repartition_by_sex(df_filtered_year)
fig_age_distribution = gr.plot_age_pyramid(df_filtered_year)
fig_subpatho_distribution = gr.repartition_by_subpathology(df_filtered, selected_patho, selected_year)

# Carte géographique
deck = mp.plot_heatmap_by_department(df_filtered_year, selected_patho, selected_year)

# ---------------------------------------
# 🔹 Affichage des visualisations
# ---------------------------------------

# Section 1 : Analyse par sexe
st.markdown("### Évolution de la prévalence par sexe")
col1, col2, col3 = st.columns(3)
with col1:
    st.plotly_chart(fig_prev_femmes, use_container_width=True)
with col2:
    st.plotly_chart(fig_prev_hommes, use_container_width=True)
with col3:
    st.plotly_chart(fig_repartition_sexe, use_container_width=False)

# Graphique de différence H/F
st.plotly_chart(fig_diff_prev_sexe, use_container_width=True)

# Section 2 : Analyse temporelle
st.markdown("### Évolution de la prévalence par année avec et sans COVID-19")
st.plotly_chart(fig_prev_time, use_container_width=True)

# Section 3 : Distribution par âge
st.markdown("### Distribution de la prévalence par âge")
st.plotly_chart(fig_age_distribution, use_container_width=True)

# Section 4 : Sous-pathologies
st.markdown("### Répartition des sous-pathologies")
st.plotly_chart(fig_subpatho_distribution, use_container_width=True)

# Section 5 : Carte géographique
st.markdown("### Heatmap des cas par département")
st.pydeck_chart(deck)

# ---------------------------------------
# 🔹 Fin de l'application
# ---------------------------------------
