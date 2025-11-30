import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------
# Graphique 1 : évolution de la prévalence
# ---------------------------
def graphique1(df, patho1, age=["tous âges"], dept=["999"], region=[99]):
    """
    Graphique interactif avec Plotly : Évolution de la prévalence par sexe pour patho1
    - Axe X : année
    - Axe Y : prévalence
    - Trois courbes : Total (9), Hommes (1), Femmes (2)
    """
    # Filtrer df pour patho1 et top se terminant par _CAT_CAT
    df_graph = df[
        (df["patho_niv1"] == patho1) &
        (df["top"].str.endswith("_CAT_CAT", na=False)) &
        (df["libelle_classe_age"].isin(age)) &
        (df["dept"].isin(dept)) &
        (df["region"].isin(region))
    ]

    # Sécurité si df vide
    if df_graph.empty:
        return px.scatter(title=f"Aucune donnée disponible pour {patho1}")

    # Calcul des séries par sexe
    def somme_ntop_par_annee(df_sex):
        return df_sex.groupby("annee")["prev"].sum()

    serie_sexe9 = somme_ntop_par_annee(df_graph[df_graph["sexe"] == 9])
    serie_hommes = somme_ntop_par_annee(df_graph[df_graph["sexe"] == 1])
    serie_femmes = somme_ntop_par_annee(df_graph[df_graph["sexe"] == 2])

    # Reconstituer un DataFrame long pour Plotly
    df_plot = pd.concat([
        pd.DataFrame({"annee": serie_sexe9.index, "prev": serie_sexe9.values, "Sexe": "Total"}),
        pd.DataFrame({"annee": serie_hommes.index, "prev": serie_hommes.values, "Sexe": "Hommes"}),
        pd.DataFrame({"annee": serie_femmes.index, "prev": serie_femmes.values, "Sexe": "Femmes"})
    ])

    # Créer graphique interactif avec Plotly
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
        yaxis=dict(range=[0, df_plot["prev"].max() * 1.05 if not df_plot["prev"].empty else 1])
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
        title=f"Pyramide des âges pour {"".join(patho1)} en {annee_sel}",
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
def graphique4(df):
    if df.empty:
        return px.scatter(title="Aucune donnée disponible pour Graphique 4")
    fig = px.line(
        df.groupby("annee")["prev"].median().reset_index(),
        x="annee",
        y="prev",
        markers=True,
        title="Graphique 4",
        labels={"prev": "Prévalence médiane", "annee": "Année"}
    )
    fig.update_layout(template="plotly_white")
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
