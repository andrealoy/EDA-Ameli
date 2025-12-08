# Graphiques plotly pour l'application Streamlit
import plotly.express as px
import numpy as np 
import pandas as pd 

def group_by_year_and_calculate_mean_prev(df_filtered):
    """Groupe le DataFrame par année et calcule la moyenne de la prévalence."""
    return df_filtered.groupby("annee")["prev"].mean().reset_index()

def plot_prevalence_over_time(df_grouped):
    """Trace un graphique de la prévalence au fil des années pour une pathologie donnée."""          
    fig = px.line(df_grouped, x="annee", y="prev", title="Évolution de la prévalence par année", markers=True)
    fig.update_layout(xaxis_title="Année", yaxis_title="Prévalence (prev)")
    return fig

def plot_real_vs_expected_prevalence(df_grouped):
    """Trace un graphique comparant la prévalence réelle et la prévalence attendue sans Covid."""
    df_obs = df_grouped.copy()
    # 2. Fit sur les années pré-Covid
    mask_pre = df_obs["annee"] < 2020
    x_pre = df_obs.loc[mask_pre, "annee"]
    y_pre = df_obs.loc[mask_pre, "prev"]

    m, b = np.polyfit(x_pre, y_pre, 1)
    df_obs["prev_attendue"] = m * df_obs["annee"] + b
    # 3. Plot avec plotly
    fig = px.line(df_obs, x="annee", y=["prev", "prev_attendue"],
                  labels={"value": "Prévalence (%)", "annee": "Année", "variable": "Type"},
                  title="Prévalence réelle vs attendue (sans Covid)")
    
    # Customize colors and line styles
    fig.data[0].update(mode="markers+lines", line=dict(color="#006FDD", width=2), marker=dict(size=6))
    fig.data[1].update(mode="lines", line=dict(color="#E74C3C", width=2, dash="dash"))
    
    # Rename traces for legend and hover with colored labels
    fig.data[0].update(
        name="Prévalence",
        legendgroup="Prévalence",
        hovertemplate='<b style="color:#006FDD">Prévalence</b><br>Année: %{x}<br>Prévalence: %{y:.2f}%<extra></extra>'
    )
    fig.data[1].update(
        name="Prévalence attendue (sans Covid)",
        legendgroup="Prévalence attendue (sans Covid)",
        hovertemplate='<b style="color:#E74C3C">Prévalence attendue (sans Covid)</b><br>Année: %{x}<br>Prévalence: %{y:.2f}%<extra></extra>'
    )
    return fig

def plot_prevalence_sex(df_filtered:pd.DataFrame, sexcode:int):
    """Trace un graphique de la prévalence pour un sexe au fil des années pour une pathologie donnée."""
    df_sex = df_filtered[df_filtered["sexe"] == sexcode]
    df_grouped_sex = df_sex.groupby("annee")["prev"].mean().reset_index()
    fig = px.line(df_grouped_sex, x="annee", y="prev", markers=True)
    if sexcode == 1:
        fig.update_layout(title="Prévalence chez les Hommes")
        fig.data[0].update(
            name="Prévalence Hommes",
            legendgroup="Prévalence Hommes",
            mode="markers+lines",
            line=dict(color="#0052CC", width=2),
            marker=dict(size=6),
            hovertemplate='<b style="color:#0052CC">Prévalence Hommes</b><br>Année: %{x}<br>Prévalence: %{y:.2f}%<extra></extra>'
        )
    else:
        fig.update_layout(title="Prévalence chez les Femmes")
        fig.data[0].update(
            name="Prévalence Femmes",
            legendgroup="Prévalence Femmes",
            mode="markers+lines",
            line=dict(color="#9700DD", width=2),
            marker=dict(size=6),
            hovertemplate='<b style="color:#9700DD">Prévalence Femmes</b><br>Année: %{x}<br>Prévalence: %{y:.2f}%<extra></extra>'
        )

    return fig

def plot_prevalence_difference_sex(df_filtered:pd.DataFrame):
    """Trace un graphique de la différence de prévalence entre les sexes au fil des années pour une pathologie donnée."""
    df_men = df_filtered[df_filtered["sexe"] == 1]
    df_women = df_filtered[df_filtered["sexe"] == 2]        
    df_grouped_men = df_men.groupby("annee")["prev"].mean().reset_index()
    df_grouped_women = df_women.groupby("annee")["prev"].mean().reset_index()      

    fig = px.line(title="Différence de prévalence entre Hommes et Femmes")
    fig.add_scatter(
        x=df_grouped_women["annee"],
        y=df_grouped_women["prev"],
        mode="lines+markers",
        name="Femmes",
        line=dict(color="#9700DD", width=2),
        marker=dict(size=6),
        hovertemplate='<b style="color:#9700DD">Femmes</b><br>Année: %{x}<br>Prévalence: %{y:.2f}%<extra></extra>'
    )
    fig.add_scatter(
        x=df_grouped_men["annee"],
        y=df_grouped_men["prev"],
        mode="lines+markers",
        name="Hommes",
        line=dict(color="#0052CC", width=2),
        marker=dict(size=6),
        hovertemplate='<b style="color:#0052CC">Hommes</b><br>Année: %{x}<br>Prévalence: %{y:.2f}%<extra></extra>'
    )
    fig.add_scatter(
        x=df_grouped_women["annee"],
        y=df_grouped_women["prev"],
        mode="lines",
        name="Écart H-F",
        fill=None,
        line=dict(color="gray", width=0),
    )
    fig.update_traces(fill='tonexty', fillcolor='rgba(128,128,128,0.2)', selector=dict(name="Écart H-F"))
    fig.update_layout(xaxis_title="Année", yaxis_title="Prévalence (%)")
    return fig   

def plot_repartition_by_sex(df_year:pd.DataFrame):
    """Trace un pie chart de la répartition de la prévalence par sexe pour une pathologie donnée et une année donnée."""
    df_grouped = df_year.groupby("sexe")["prev"].mean().reset_index()
    year = int(df_year["annee"].iloc[0]) if len(df_year) > 0 else "N/A"
    
    # Map sex codes to labels
    df_grouped["sexe_label"] = df_grouped["sexe"].map({1: "Homme", 2: "Femme"})
    
    fig = px.pie(
        df_grouped,
        names="sexe_label",
        values="prev",
        title=f"Répartition de la prévalence par sexe en {year}",
        color="sexe_label",
        color_discrete_map={"Homme": "#0052CC", "Femme": "#9700DD"}
    )
    fig.update_traces(
        hovertemplate='<b>Sexe: %{label}</b><br>Prévalence: %{value:.2f}%<br>Pourcentage: %{percent}<extra></extra>'
    )
    return fig
    

def plot_age_pyramid(df_year:pd.DataFrame):     
    """Trace une pyramide des âges de la prévalence par sexe pour une pathologie donnée."""
    year = int(df_year["annee"].iloc[0]) if len(df_year) > 0 else "N/A"
    patho = df_year["patho_niv1"].iloc[0] if len(df_year) > 0 and "patho_niv1" in df_year.columns else "Pathologie"
    
    # Group by age and sex
    df_grouped = df_year.groupby(["libelle_classe_age", "sexe"])["prev"].mean().reset_index()
    df_grouped["prev_signed"] = df_grouped.apply(lambda row: -row["prev"] if row["sexe"] == 1 else row["prev"], axis=1)
    df_grouped["sexe_label"] = df_grouped["sexe"].map({1: "Hommes", 2: "Femmes"})
    
    fig = px.bar(
        df_grouped,
        x="prev_signed",
        y="libelle_classe_age",
        color="sexe_label",
        orientation="h",
        title=f"Pyramide des âges – {patho} ({year})",
        color_discrete_map={"Hommes": "#0052CC", "Femmes": "#9700DD"},
        labels={"sexe_label": "Sexe"}
    )
    
    # Update hover templates with colored labels
    fig.update_traces(
        hovertemplate='<b style="color:#0052CC">Hommes</b><br>Âge: %{y}<br>Prévalence: %{customdata:.2f}%<extra></extra>',
        selector=dict(name="Hommes"),
        customdata=df_grouped[df_grouped["sexe"] == 1]["prev"]
    )
    fig.update_traces(
        hovertemplate='<b style="color:#9700DD">Femmes</b><br>Âge: %{y}<br>Prévalence: %{customdata:.2f}%<extra></extra>',
        selector=dict(name="Femmes"),
        customdata=df_grouped[df_grouped["sexe"] == 2]["prev"]
    )
    
    fig.update_layout(
        barmode="relative",
        xaxis_title="Prévalence (%)",
        yaxis_title="Âge",
        bargap=0.1
    )
    
    return fig

def repartition_by_subpathology(df_filtered:pd.DataFrame, selected_patho1:str=None, year:int=None):
    """Trace un bar chart de la répartition des sous-pathologies (niv2 ou niv3) pour une pathologie donnée et une année donnée."""
    if selected_patho1 is None:
        selected_patho1 = df_filtered["patho_niv1"].iloc[0] if len(df_filtered) > 0 and "patho_niv1" in df_filtered.columns else "Pathologie"
    if year is None:
        year = int(df_filtered["annee"].iloc[0]) if len(df_filtered) > 0 else "N/A"
    
    # Check how many unique niv2 we have
    unique_niv2 = df_filtered["patho_niv2_simplifie"].nunique()
    
    if unique_niv2 <= 1:
        # Only one niv2, check if we can show niv3
        unique_niv3 = df_filtered["patho_niv3"].nunique()
        niv2_name = df_filtered["patho_niv2_simplifie"].iloc[0] if len(df_filtered) > 0 else "Sous-pathologie unique"
        
        if unique_niv3 <= 1:
            # Only one niv3 too, can't show distribution
            fig = px.bar(title=f"Répartition des sous-pathologies pour {selected_patho1}")
            fig.add_annotation(
                text=f"Une seule sous-pathologie : <b>{niv2_name}</b><br><br>Impossible d'afficher une répartition",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16),
                align="center"
            )
            return fig
        else:
            # Multiple niv3, show niv3 distribution
            counts = df_filtered["patho_niv3"].value_counts().sort_values(ascending=False)
            counts = counts.reset_index()
            counts.columns = ["pathology", "count"]
            title = f"Répartition des sous-pathologies (niv3) pour {niv2_name}"
            xlabel = "Sous-pathologie (niv3)"
    else:
        # Multiple niv2, show niv2
        counts = df_filtered["patho_niv2_simplifie"].value_counts().sort_values(ascending=False)
        counts = counts.reset_index()
        counts.columns = ["pathology", "count"]
        title = f"Répartition des sous-pathologies (niv2) pour {selected_patho1}"
        xlabel = "Sous-pathologie (niv2)"
    
    fig = px.bar(
        counts,
        x="pathology",
        y="count",
        title=title,
        labels={"pathology": xlabel, "count": "Nombre de cas"},
        color="count",
        color_continuous_scale="Blues"
    )
    
    fig.update_traces(
        hovertemplate='<b>Sous-pathologie: %{x}</b><br>Nombre de cas: %{y}<extra></extra>'
    )
    fig.update_layout(xaxis_tickangle=-45)    
    return fig
   
    
