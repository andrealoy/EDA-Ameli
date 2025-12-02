import streamlit as st
import pandas as pd
import json

@st.cache_data
def load_data():
    return pd.read_parquet("datasets/cleaned.parquet")

def load_json():
    with open("datasets/regions_names.json", "r", encoding="utf-8") as f:
        region_names = json.load(f)
    with open("datasets/dept_names.json", "r", encoding="utf-8") as f:
        dept_names = json.load(f)
    with open("datasets/possible_values.json", "r", encoding="utf-8") as f:
        possible_values = json.load(f)
    return region_names, dept_names, possible_values

df = load_data()
region_names, dept_names, possible_values = load_json()

ages = possible_values["age"]
depts = possible_values["dept"]
regions = possible_values["region"]
dept_to_region = possible_values["dept_to_region"]

with st.sidebar:
    st.title("Sélection des filtres")

    age_selected = st.select_slider(
        "Tranche d'âge",
        options=sorted(ages)
    )

    # Sélecteur de département (avec noms humains)
    dept_selected = st.selectbox(
        "Département",
        options= sorted(depts, key=lambda x: dept_names.get(x)),
        format_func=lambda x: dept_names.get(x, f"Département {x}")
    )

    # Région associée automatiquement grâce à ton mapping dept -> région
    region_auto = dept_to_region.get(dept_selected)

    # Affichage formaté du nom de la région
    region_label = region_names.get(str(region_auto), f"Région {region_auto}")




st.write("### Résumé des filtres")
st.write("Âge :", age_selected)
st.write("Département :", dept_selected)
st.write("Région :", region_label)

