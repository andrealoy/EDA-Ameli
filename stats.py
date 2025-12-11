import pandas as pd
import streamlit as st

# ============================================================
# 1. STATISTIQUES 
# ============================================================

# --- Démographie ---
def demographic_stats(df):
    return {
        "nb_classes_age": df["libelle_classe_age"].nunique(),
        "nb_sexes": df["sexe"].nunique(),
    }


# --- Géographie ---
def geographic_stats(df):
    return {
        "nb_regions": df["region"].nunique(),
        "nb_departements": df["dept"].nunique(),
    }


# --- Pathologies ---
def pathology_stats(df):
    return {
        "nb_patho_niv1": df["patho_niv1"].nunique(),
        "nb_patho_niv2": df["patho_niv2_simplifie"].nunique(),
        "nb_patho_niv3": df["patho_niv3"].nunique(),
        "pct_nan_niv2": df["patho_niv2_simplifie"].isna().mean().round(3),
        "pct_nan_niv3": df["patho_niv3"].isna().mean().round(3),
    }


# --- Statistiques numériques ---
def numeric_stats(df):
    return {
        # prev
        "prev_mean": df["prev"].mean(),
        "prev_median": df["prev"].median(),
        "pct_nan_prev": df["prev"].isna().mean().round(3),

        # Ntop
        "Ntop_mean": df["Ntop"].mean(),
        "pct_nan_Ntop": df["Ntop"].isna().mean().round(3),

        # Npop
        "Npop_mean": df["Npop"].mean(),
    }


# ============================================================
# 2. AFFICHAGE STREAMLIT
# ============================================================

# --- Démographie ---
def display_demographic_metrics(df):
    stats = demographic_stats(df)
    st.subheader("👥 Démographie")

    col1, col2 = st.columns(2)
    col1.metric("Classes d'âge", stats["nb_classes_age"])
    col2.metric("Catégories de sexe", stats["nb_sexes"])


# --- Géographie ---
def display_geographic_metrics(df):
    stats = geographic_stats(df)
    st.subheader("🗺️ Géographie")

    col1, col2 = st.columns(2)
    col1.metric("Régions couvertes", stats["nb_regions"])
    col2.metric("Départements couverts", stats["nb_departements"])


# --- Pathologies ---
def display_pathology_metrics(df):
    stats = pathology_stats(df)
    st.subheader("🧬 Pathologies")

    col1, col2, col3 = st.columns(3)
    col1.metric("Niveau 1", stats["nb_patho_niv1"])
    col2.metric("Niveau 2", stats["nb_patho_niv2"])
    col3.metric("Niveau 3", stats["nb_patho_niv3"])

    col4, col5 = st.columns(2)
    col4.metric("% NaN niv2", f"{stats['pct_nan_niv2']*100:.1f}%")
    col5.metric("% NaN niv3", f"{stats['pct_nan_niv3']*100:.1f}%")


# --- Statistiques numériques ---
def display_numeric_metrics(df):
    stats = numeric_stats(df)
    st.subheader("🔢 Variables numériques")

    col1, col2, col3 = st.columns(3)
    col1.metric("Prévalence moyenne", f"{stats['prev_mean']:.4f}")
    col2.metric("Prévalence médiane", f"{stats['prev_median']:.4f}")
    col3.metric("% NaN prévalence", f"{stats['pct_nan_prev']*100:.1f}%")

    col4, col5, col6 = st.columns(3)
    col4.metric("Ntop moyen", f"{stats['Ntop_mean']:.0f}")
    col5.metric("Npop moyen", f"{stats['Npop_mean']:.0f}")
    col6.metric("% NaN Ntop", f"{stats['pct_nan_Ntop']*100:.1f}%")
