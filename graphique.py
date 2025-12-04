import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import linregress

# ---------------------------------------------------------
# Fonction : Régression linéaire + significativité
# ---------------------------------------------------------
def analyse_tendance(df, year_col="annee", value_col="prev"):
    """
    Retourne la pente, p-value, % variation et si la tendance est significative.
    Ne trace rien (full backend).
    """
    if df.empty:
        return {"slope": np.nan, "p_value": np.nan, "significant": False, "variation_pct": np.nan}

    df_year = df.groupby(year_col)[value_col].sum().reset_index().sort_values(year_col)

    years = df_year[year_col].astype(float).values
    values = df_year[value_col].astype(float).values

    if len(years) < 2:
        return {"slope": np.nan, "p_value": np.nan, "significant": False, "variation_pct": np.nan}

    res = linregress(years, values)
    slope, p_value = res.slope, res.pvalue
    variation_pct = (values[-1] - values[0]) / values[0] * 100 if values[0] != 0 else np.nan

    significant = (p_value < 0.05) and (slope > 0)

    return {
        "slope": slope,
        "p_value": p_value,
        "significant": significant,
        "variation_pct": variation_pct
    }


# ---------------------------------------------------------
# Graphique 1 : évolution de la prévalence
# ---------------------------------------------------------
def graphique1(df, patho1, age=["tous âges"], dept=["999"], region=[99]):
    """
    Graphique Plotly : Évolution de la prévalence par sexe
    - 3 courbes (Total, Hommes, Femmes)
    - Intègre analyse_tendance pour détecter augmentation significative
    """

    # Filtre
    df_graph = df[
        (df["patho_niv1"] == patho1) &
        (df["top"].str.endswith(("_CAT_CAT", "_CAT_EXC", "_CAT_INC"), na=False)) &
        (df["libelle_classe_age"].isin(age)) &
        (df["dept"].isin(dept)) &
        (df["region"].isin(region))
    ]

    if df_graph.empty:
        return px.scatter(title=f"Aucune donnée disponible pour {patho1}")

    # ---- Séries par sexe ----------------------------------------------------
    def somme_par_annee(df_sex):
        return df_sex.groupby("annee")["prev"].sum()

    serie_total  = somme_par_annee(df_graph[df_graph["sexe"] == 9])
    serie_hommes = somme_par_annee(df_graph[df_graph["sexe"] == 1])
    serie_femmes = somme_par_annee(df_graph[df_graph["sexe"] == 2])

    # ---- Préparer df long pour plotly ---------------------------------------
    df_plot = pd.concat([
        pd.DataFrame({"annee": serie_total.index,  "prev": serie_total.values,  "Sexe": "Total"}),
        pd.DataFrame({"annee": serie_hommes.index, "prev": serie_hommes.values, "Sexe": "Hommes"}),
        pd.DataFrame({"annee": serie_femmes.index, "prev": serie_femmes.values, "Sexe": "Femmes"})
    ])

    # ---- Analyse des tendances ----------------------------------------------
    stats_total  = analyse_tendance(df_plot[df_plot["Sexe"] == "Total"])
    stats_hommes = analyse_tendance(df_plot[df_plot["Sexe"] == "Hommes"])
    stats_femmes = analyse_tendance(df_plot[df_plot["Sexe"] == "Femmes"])

    # Construire annotation du titre
    annotation = []
    if stats_total["significant"]:  annotation.append("Total ↑")
    if stats_hommes["significant"]: annotation.append("Hommes ↑")
    if stats_femmes["significant"]: annotation.append("Femmes ↑")

    annotation_txt = (
        " | Augmentation significative : " + ", ".join(annotation)
        if annotation
        else ""
    )

    # ---- Graphique final -----------------------------------------------------
    fig = px.line(
        df_plot,
        x="annee",
        y="prev",
        color="Sexe",
        markers=True,
        title=f"Évolution de la prévalence : {patho1}",
        labels={"prev": "Prévalence", "annee": "Année"}
    )

    fig.update_layout(
        template="plotly_white",
        legend_title_text="Sexe",
        yaxis=dict(range=[0, df_plot["prev"].max() * 1.05])
    )
    fig.update_layout(
        template="plotly_white",
        legend_title_text="Sexe",
        yaxis=dict(range=[0, df_plot["prev"].max() * 1.05])
 
    )# ---- Annotation sous l’axe des X ----
    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0.5,
        y=-0.3,   # Ajuste plus bas ou plus haut si besoin
        showarrow=False,
         text=(
        "Augmentation significative : " + ", ".join(annotation)
        if annotation else "Pas d’augmentation significative détectée"
    ),
    font=dict(size=12),
    )
    
    return fig

# ---------------------------
# Graphique 2 : pyramide des âges
# ---------------------------
def graphique2(df, patho1, dept=["999"], region=[99], annee_sel=2022):
    """
    Pyramide des âges interactive pour des pathologies données par année.
    """

    # Sélection des colonnes utiles et conversion
    df_reduit = df[["annee", "patho_niv1", "dept", "region", "libelle_classe_age", "sexe", "Ntop"]].copy()
    df_reduit["Ntop"] = pd.to_numeric(df_reduit["Ntop"], errors="coerce")

    # Filtrer les données selon les critères
    df_filtered = df_reduit[
        (df_reduit["patho_niv1"] == patho1) &
        (df_reduit["dept"].isin(dept)) &
        (df_reduit["region"].isin(region)) &
        (df_reduit["Ntop"].notna()) &
        (df_reduit["Ntop"] != "PSY_CAT_CAT") &
        (df_reduit["libelle_classe_age"] != "tous âges") &
        (df_reduit["annee"] == annee_sel)
    ]

    if df_filtered.empty:
        return go.Figure().add_annotation(text=f"Aucune donnée pour {', '.join(patho1)} en {annee_sel}")

    # Grouper par tranche d'âge et sexe
    pivot = df_filtered.groupby(["libelle_classe_age", "sexe"])["Ntop"].sum().unstack(fill_value=0)
    pivot = pivot.reindex(sorted(df_filtered["libelle_classe_age"].unique()), fill_value=0)

    # Préparer les valeurs pour la pyramide
    hommes_neg = -pivot.get(1, pd.Series(np.zeros(len(pivot))))
    femmes = pivot.get(2, pd.Series(np.zeros(len(pivot))))

    xlim = max(femmes.max(), -hommes_neg.min()) * 1.1  # axe X symétrique

    # Créer figure Plotly
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=pivot.index,
        x=hommes_neg,
        name='Hommes',
        orientation='h',
        marker_color='blue',
        hovertemplate='Age: %{y}<br>Hommes: %{text}<extra></extra>',
        text=abs(hommes_neg)
    ))
    fig.add_trace(go.Bar(
        y=pivot.index,
        x=femmes,
        name='Femmes',
        orientation='h',
        marker_color='red',
        hovertemplate='Age: %{y}<br>Femmes: %{x}<extra></extra>'
    ))

    fig.update_layout(
        title=f"Pyramide des âges pour {''.join(patho1)} en {annee_sel}",
        barmode='relative',
        xaxis=dict(
            tickvals=np.arange(-xlim, xlim+1, step=int(xlim/5)),
            ticktext=[str(abs(int(x))) for x in np.arange(-xlim, xlim+1, step=int(xlim/5))],
            title="Nombre de cas",
            range=[-xlim, xlim]
        ),
        yaxis=dict(title="Tranche d'âge"),
        template="plotly_white",
        legend=dict(title="Sexe")
    )

    return fig


# ---------------------------
# Graphique 3
# ---------------------------
def graphique3(df, patho1, dept=["999"], region=[99],annee_sel=2022):
    """
    Camembert H/F pour une pathologie et une année.
    """
    # Filtrer les données et convertir Ntop
    df_reduit = df[["annee", "patho_niv1", "dept", "region", "libelle_classe_age", "sexe", "Ntop"]].copy()
    df_reduit["Ntop"] = pd.to_numeric(df_reduit["Ntop"], errors="coerce")
    
    df_filtered = df_reduit[
        (df_reduit["patho_niv1"] == patho1) &
        (df_reduit["dept"].isin(dept)) &
        (df_reduit["region"].isin(region)) &
        (df_reduit["Ntop"].notna()) &
        (df_reduit["Ntop"] != "PSY_CAT_CAT") &
        (df_reduit["libelle_classe_age"] != "tous âges") &
        (df_reduit["annee"] == annee_sel)
    ]

    # Totaux par sexe
    hommes = df_filtered[df_filtered["sexe"] == 1]["Ntop"].sum()
    femmes = df_filtered[df_filtered["sexe"] == 2]["Ntop"].sum()

    # Camembert
    fig = px.pie(
        names=["Hommes", "Femmes"],
        values=[hommes, femmes],
        title=f"Répartition H/F pour {patho1} ({annee_sel})",
        hole=0  # si tu veux un donut, mettre >0
    )

    fig.update_traces(textinfo='percent+label')
    return fig
# ---------------------------
# Graphique 4
# ---------------------------
def graphique4(df, patho1, dept=["999"], region=[99], annee_sel=2022):
    """
    Histogramme des patho_niv2_simplifie (en abscisse) avec somme de Ntop (en ordonnée)
    pour une pathologie de niveau 1, une année et des filtres géographiques.
    """

    # --- Correction du slice de colonnes ---
    colonnes = ["annee",  "patho_niv1", "patho_niv2_simplifie", "dept", "region", "libelle_classe_age",  "sexe", "Ntop"
    ]
    df_reduit = df[colonnes].copy()

    # --- Conversion Ntop en numérique ---
    df_reduit["Ntop"] = pd.to_numeric(df_reduit["Ntop"], errors="coerce")

    # --- Filtres ---
    df_filtered = df_reduit[
        (df_reduit["patho_niv1"] == patho1) &
        (df_reduit["dept"].isin(dept)) &
        (df_reduit["region"].isin(region)) &
        (df_reduit["Ntop"].notna()) &
        (df_reduit["patho_niv2_simplifie"].notna()) & 
        (df_reduit["patho_niv2_simplifie"] != "") & 
        (df_reduit["patho_niv2_simplifie"].str.lower() != "nan") & 
        (df_reduit["libelle_classe_age"] != "tous âges") &
        (df_reduit["annee"] == annee_sel)
      
    ].copy()

    # --- Regroupement par patho_niv2 ---
    df_grouped = (
        
        df_filtered.groupby("patho_niv2_simplifie", as_index=False)
        .agg({"Ntop": "sum"})
        .sort_values(by="Ntop", ascending=False)
    )

    # --- Histogramme Plotly ---
    fig = px.bar(
        df_grouped,
        x="patho_niv2_simplifie",
        y="Ntop",
        labels={"patho_niv2_simplifie": " ", "Ntop": "Nombre de cas"},
        title=f"{patho1} ({annee_sel}) Répartition du nombre de cas en fonction du type de sous pathologie "
    )

    fig.update_layout(xaxis_tickangle=45)

    return fig

# ---------------------------
# Grand graphique
# ---------------------------
def graphique_grand(df, patho1):
    df_graph = df[df["patho_niv1"] == patho1]
    if df_graph.empty:
        return px.scatter(title=f"Aucune donnée pour le grand graphique : {patho1}")

    fig = px.line(
        df_graph.groupby("annee")["prev"].sum().reset_index(),
        x="annee",
        y="prev",
        markers=True,
        title=f"Grand graphique synthèse : {patho1}",
        labels={"prev": "Prévalence", "annee": "Année"}
    )
    fig.update_layout(template="plotly_white")
    return fig







