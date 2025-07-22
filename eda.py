import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


def main():
    # Charger les données localement
    @st.cache_data
    def load_data_dr():
        df_dr = pd.read_excel("proba_bayesienne_DR.xlsx")
        return df_dr

    @st.cache_data
    def load_data_br():
        excel_file = "base_creance_branche_finale.xlsx"
        df_br = pd.read_excel(excel_file)
        return df_br

    df_dr = load_data_dr()
    df_br = load_data_br()

    st.title("Exploration des données")
    st.markdown(" Cette section permet d'explorer les données relatives aux créances significatives par Direction Régionale (DR) et par Branche. Vous pouvez visualiser les probabilités bayésiennes, les proportions de créances significatives, le nombre total de contrats par année, ainsi que la répartition des branches par nombre de créances significatives et par DR.")


    # Section 3: Nombre total de contrats par année
    st.markdown("### Relation entre l'évolution du nombre de contrats d'assurance et de créances signif par année")

    # Regrouper par année et calculer le total des contrats
    contrats_per_year = df_dr.groupby("annee")["total_contrats"].sum().reset_index()
    contrats_per_year.rename(columns={"total_contrats": "nombre_total_contrats"}, inplace=True)

    # Ajouter une colonne pour les créances significatives
    contrats_per_year["nb_contrats_gt1000"] = df_dr.groupby("annee")["nb_contrats_gt1000"].sum().reset_index()["nb_contrats_gt1000"]

    # Créer une figure avec deux axes Y
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Ajouter le bar chart pour le nombre total de contrats
    fig.add_trace(
        go.Bar(
            x=contrats_per_year["annee"],
            y=contrats_per_year["nombre_total_contrats"],
            name="Nombre total de contrats",
            text=contrats_per_year["nombre_total_contrats"],
            textposition="outside",
            marker=dict(color="blue"),
            hovertemplate='Année: %{x}<br>Nombre de contrats: %{y}<extra></extra>'
        ),
        secondary_y=False  # Utiliser l'axe Y principal
    )

    # Ajouter le line chart pour le nombre de créances significatives
    fig.add_trace(
        go.Scatter(
            x=contrats_per_year["annee"],
            y=contrats_per_year["nb_contrats_gt1000"],
            mode="lines+markers",
            name="Nombre de créances significatives",
            line=dict(color="red", width=2),
            marker=dict(size=8),
            hovertemplate='Année: %{x}<br>Nombre de créances significatives: %{y}<extra></extra>'
        ),
        secondary_y=True  # Utiliser l'axe Y secondaire
    )

    # Mettre à jour la mise en page
    fig.update_layout(
        title="Evolution du nombre de contrats et de créances signif par année",
        xaxis=dict(title="Année"),
        yaxis=dict(title="Nombre total de contrats"),
        legend=dict(
            yanchor="top",
            y=-0.08,
            xanchor="left",
            x=0.7
        ),
        template="plotly_white"
    )

    # Mettre à jour les axes Y
    fig.update_yaxes(title_text="Nombre de contrats", secondary_y=False)
    fig.update_yaxes(
        title_text="Nombre de créances significatives",
        secondary_y=True,
        range=[0, contrats_per_year["nb_contrats_gt1000"].max() * 1.5]  # Augmenter l'échelle pour rendre le line chart plus bas
    )

    # Afficher le graphique dans Streamlit
    st.plotly_chart(fig, use_container_width=True)


    # Obtenir les années et les branches uniques
    annees = sorted(df_br['annee'].unique())
    branches = sorted(df_br['BRANCHE'].unique())

    # Section 4: Répartition des branches par nombre de créances significatives par année
    st.header("Répartition du nombre de créances significatives en fonction des branches")

    # Préparer les données pour le diagramme
    totaux_par_annee = df_br.groupby(['annee', 'BRANCHE'])['creance_signif'].sum().unstack(fill_value=0)

    # Largeur des barres
    bar_width = 0.8 / len(branches)

    # Créer le graphique avec Plotly
    fig1 = go.Figure()

    # Tracer les barres pour chaque branche
    for i, branche in enumerate(branches):
        # Calculer les positions des barres pour chaque branche
        x_positions = [x + i * bar_width for x in range(len(annees))]
        # Valeurs pour la branche actuelle
        y_values = totaux_par_annee[branche].reindex(annees, fill_value=0)
        # Ajouter une trace pour chaque branche
        fig1.add_trace(
            go.Bar(
                x=x_positions,
                y=y_values,
                name=branche,
                width=bar_width,  # Définir la largeur des barres
            )
        )

    # Configurer les axes et le titre
    fig1.update_layout(
        title="Répartition du nombre de créances significatives en fonction des branches",
        xaxis=dict(
            title="Année",
            tickmode="array",
            tickvals=[x + bar_width * (len(branches) - 1) / 2 for x in range(len(annees))],
            ticktext=annees
        ),
        yaxis=dict(title="Nombre de créances significatives"),
        legend=dict(title="Branches", orientation="h", x=0.5, xanchor="center", y=-0.2),
        template="plotly_white"
    )

    # Afficher le graphique dans Streamlit
    st.plotly_chart(fig1, use_container_width=True)

    # Section 4: Répartition des branches par moyenne des montants des créances significatives par année
    st.header("Répartition des montants moyens des créances significatives en fonction des branches")

    # Calculer la moyenne des montants des créances significatives pour chaque branche et chaque année
    moyennes_par_annee = df_br.groupby(['annee', 'BRANCHE'])['moyenne_montant_creances_sinif'].mean().unstack(fill_value=0)

    # Largeur des barres
    bar_width = 0.8 / len(branches)

    # Créer le graphique avec Plotly
    fig2 = go.Figure()

    # Tracer les barres pour chaque branche
    for i, branche in enumerate(branches):
        # Calculer les positions des barres pour chaque branche
        x_positions = [x + i * bar_width for x in range(len(annees))]
        # Valeurs pour la branche actuelle
        y_values = moyennes_par_annee[branche].reindex(annees, fill_value=0)
        # Ajouter une trace pour chaque branche
        fig2.add_trace(
            go.Bar(
                x=x_positions,
                y=y_values,
                name=branche,
                width=bar_width,  # Définir la largeur des barres
            )
        )

    # Configurer les axes et le titre
    fig2.update_layout(
        title="Répartition des montants moyens des créances significatives en fonction des branches",
        xaxis=dict(
            title="Année",
            tickmode="array",
            tickvals=[x + bar_width * (len(branches) - 1) / 2 for x in range(len(annees))],
            ticktext=annees
        ),
        yaxis=dict(title="montants moyens des créances significatives"),
        legend=dict(title="Branches", orientation="h", x=0.5, xanchor="center", y=-0.2),
        template="plotly_white"
    )

    # Afficher le graphique dans Streamlit
    st.plotly_chart(fig2, use_container_width=True)
            
    # Section 5: Répartition des branches par créances significatives et DR
    st.header("Répartition des créances significatives par branches et par DR")

    # Créer une heatmap avec Plotly
    fig_heatmap = px.imshow(
        df_br.pivot_table(index="BRANCHE", columns="NOM_DR", values="creance_signif", aggfunc="sum"),
        labels=dict(x="Direction Régionale (DR)", y="Branche", color="creance_signif"),
        title="Répartition des créances significatives par branches et par DR",
        color_continuous_scale="Blues"
    )

    # Afficher le graphique
    st.plotly_chart(fig_heatmap)

if __name__ == "__main__":
    main()
