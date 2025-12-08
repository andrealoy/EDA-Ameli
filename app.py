import streamlit as st
import pandas as pd    
import graphs as gr
import map as mp

# ---------------------------------------
# 🔹 Titre de l'application
# ---------------------------------------
st.title("Explorateur de pathologies – Données Santé")

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
