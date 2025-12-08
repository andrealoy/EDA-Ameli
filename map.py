import pydeck as pdk
import pandas as pd
import json

def plot_heatmap_by_department(df_filtered: pd.DataFrame, selected_patho: str = None, year: int = None):
    """Trace une heatmap par département du nombre de cas pour une pathologie donnée avec PyDeck."""
    
    if selected_patho is None:
        selected_patho = df_filtered["patho_niv1"].iloc[0] if len(df_filtered) > 0 and "patho_niv1" in df_filtered.columns else "Pathologie"
    if year is None:
        year = int(df_filtered["annee"].iloc[0]) if len(df_filtered) > 0 else "N/A"
    
    # Load GeoJSON
    with open("datasets/france-departements.geojson", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    
    # Group by department and count cases
    df_dept = df_filtered.groupby("dept").size().reset_index(name="count")
    df_dept["dept"] = df_dept["dept"].astype(str).str.zfill(2)
    
    # Create a dictionary for quick lookup
    count_dict = dict(zip(df_dept["dept"], df_dept["count"]))
    max_count = df_dept["count"].max() if len(df_dept) > 0 else 1
    
    # Add count to each feature in GeoJSON
    for feature in geojson_data["features"]:
        dept_code = feature["properties"]["code"]
        count = count_dict.get(dept_code, 0)
        feature["properties"]["count"] = count
        feature["properties"]["dept_name"] = feature["properties"]["nom"]
        
        # Gradient from black to red based on count
        if count == 0:
            # Black for no cases
            red, green, blue = 0, 0, 0
        elif max_count > 0:
            # Gradient: black (0,0,0) to red (255,0,0)
            ratio = count / max_count
            red = int(ratio * 255)
            green = 0
            blue = 0
        else:
            red, green, blue = 0, 0, 0
        
        feature["properties"]["fill_color"] = [red, green, blue, 200]
    
    # Create PyDeck GeoJsonLayer
    layer = pdk.Layer(
        "GeoJsonLayer",
        geojson_data,
        opacity=0.8,
        stroked=True,
        filled=True,
        extruded=False,
        get_fill_color="properties.fill_color",
        get_line_color=[255, 255, 255],
        get_line_width=200,
        pickable=True,
        auto_highlight=True,
    )
    
    # Set the viewport location
    view_state = pdk.ViewState(
        latitude=46.8,
        longitude=2.5,
        zoom=5,
        pitch=0,
    )
    
    # Render
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>{dept_name}</b><br/>Département: {code}<br/>Nombre de cas: {count}",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        },
    )
    
    return deck