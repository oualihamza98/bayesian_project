import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

def main():
    # Configurer la page pour utiliser toute la largeur
    st.set_page_config(layout="wide")
    st.title("Analyse des Créances significatives par Direction Régionale (DR)")
    st.markdown("Cette section permet de visualiser les créances significatives par Direction Régionale (DR) et d'analyser les risques associés en nombre et en montant moyen.")
    # Charger les données localement
    @st.cache_data
    def load_data_dr():
        df_dr = pd.read_excel(r"C:\Users\pc\Desktop\New folder\Python folder\risque_credit\streamlit_app\proba_bayesienne_DR.xlsx")
        return df_dr

    @st.cache_data
    def load_data_br():
        excel_file = r"C:\Users\pc\Desktop\New folder\Python folder\risque_credit\streamlit_app\base_creance_branche_finale.xlsx"
        df_br = pd.read_excel(excel_file)
        return df_br

    @st.cache_data
    def load_data_creance_info():
        df = pd.read_excel(r"C:\Users\pc\Desktop\Etude_risque_crédit\bases_aggregated\base_creance_info_v3.xlsx")
        df = df[["annee", "NOM_DR", "CODE_DR", "BRANCHE", "proba_a_priori", "nb_contrats_gt1000", "total_contrats", "moyenne_creances_gt1000"]]
        return df

    df_dr = load_data_dr()
    df_br = load_data_br()
    df_creance_info = load_data_creance_info()

    # Créer le graphique
    fig_line = px.line(
        df_dr,
        x="annee",  # Axe X : Année
        y="proba_bayesienne",  # Axe Y : Probabilité bayésienne
        color="NOM_DR",  # Couleur par Direction Régionale (DR)
        title="Évolution de la probabilité bayésienne par DR au fil du temps",
        labels={"annee": "Année", "proba_bayesienne": "Probabilité Bayésienne", "NOM_DR": "Direction Régionale"}
    )

    # Afficher le graphique dans Streamlit
    st.plotly_chart(fig_line, use_container_width=True)

    # Top 3 DR par année
    st.markdown("### Classement des 3 premieres DR par année en terme de risque de créance significative")
    df_sorted=df_dr[["annee", "NOM_DR", "proba_bayesienne"]].copy()
    df_sorted = df_dr.sort_values(by=["annee", "proba_bayesienne"], ascending=[True, False])
    df_sorted.rename(columns={"proba_bayesienne": "risque creance significative"}, inplace=True)
    top_3_per_year = df_sorted.groupby("annee").head(3)
    st.write(top_3_per_year[["annee", "NOM_DR", "risque creance significative"]])

    # Définir les colonnes et les opérations d'agrégation
    aggregation_rules = {
        'CODE_DR': 'mean',
        'nb_contrats_gt1000': 'sum',
        'total_contrats': 'sum',
        'moyenne_creances_gt1000': 'mean',
        'proba_a_priori': 'mean'
    }

    # Agréger le DataFrame
    df_aggregated = df_creance_info.groupby(['annee', 'NOM_DR']).agg(aggregation_rules).reset_index()

    # Dictionnaire des abréviations pour les DR
    abbreviations = {
        "ALGER 1": "ALG1",
        "ALGER 2": "ALG2",
        "ALGER 3": "ALG3",
        "ANNABA": "ANN",
        "BATNA": "BAT",
        "BECHAR": "BEC",
        "BLIDA": "BLI",
        "CONSTANTINE": "CON",
        "CORPORATE": "COR",
        "ORAN": "ORA",
        "OUARGLA": "OUA",
        "RELIZANE": "REL",
        "SBA": "SBA",
        "SETIF": "SET",
        "TIZI OUZOU": "TIZ",
        "TLEMCEN": "TLE"
    }

    # Fonction pour générer les images
    def generate_radar_chart(year):
        data = df_dr[df_dr['annee'] == year]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=data['proba_bayesienne'],
            theta=data['NOM_DR'],
            name=str(year),
            fill='toself'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            title=dict(
                text=f"Diagramme en radar des probabilités bayésiennes par DR - {year}",
                x=0.5,  # Centrer le titre
                y=0.95,  # Position verticale (proche du haut)
                xanchor="center",  # Ancrage horizontal
                yanchor="top",  # Ancrage vertical
                font=dict(color="black")  # Couleur et style du texte
            ),
            height=400,
            width=700,
        )
        return fig

    def generate_scatter_plot(year):
        df_filtered = df_aggregated[df_aggregated['annee'] == year].copy()

        if (year == 2021):
            df_filtered['moyenne_creances_gt1000'] = np.log(df_filtered['moyenne_creances_gt1000'])
            yaxis_title = "Logarithme du montant moyen des créances significatives"
        else:
            yaxis_title = "Montant moyen des créances significatives"

        df_filtered['NOM_DR'] = df_filtered['NOM_DR'].map(abbreviations)

        mean_nb_contrats = df_filtered['nb_contrats_gt1000'].mean()
        mean_moyenne_creances = df_filtered['moyenne_creances_gt1000'].mean()

        # Créer une grille pour le dégradé de couleur
        x = np.linspace(df_filtered['nb_contrats_gt1000'].min(), df_filtered['nb_contrats_gt1000'].max(), 100)
        y = np.linspace(df_filtered['moyenne_creances_gt1000'].min(), df_filtered['moyenne_creances_gt1000'].max(), 100)
        X, Y = np.meshgrid(x, y)

        # Calculer la probabilité bayésienne comme une fonction de X et Y (exemple simplifié)
        Z = (X - X.min()) / (X.max() - X.min()) * (Y - Y.min()) / (Y.max() - Y.min())  # Normalisation dynamique  # Normalisation pour créer un dégradé

        # Créer la figure
        fig = go.Figure()

        # Ajouter le dégradé de couleur en arrière-plan
        fig.add_trace(go.Contour(
            x=x,
            y=y,
            z=Z,
            colorscale=[
            [0, "#baf5bd"],  # Vert clair
            [0.02, "#c8f5b3"],  # Vert-jaune clair
            [0.08, "#eff595"],  # Jaune
            [0.35, "#f5e88b"],  # Jaune-orange clair
            [0.42, "#f5d97f"],  # Orange clair
            [0.49, "#f5ca73"],  # Orange
            # [0.56, "#f5bb67"],  # Orange-rouge clair
            # [0.63, "#f5ac5b"],  # Orange-rouge
            # [0.7, "#f57c42"],  # Rouge-orange
            [0.77, "#f55c36"],  # Rouge clair
            [0.84, "#f53c2a"],  # Rouge moyen
            [0.91, "#f51c1e"],  # Rouge foncé
            [1, "#f50012"]  # Rouge intense
            ],  # Dégradé de vert à rouge
            ncontours=50,
            showscale=True,
            colorbar=dict(title="barre du risque",
                          tickfont=dict(size=10),
                          len=0.4,
                          x=1.05,
                          xanchor="right",
                          y=-0.5,
                          yanchor="bottom"
                          ),    # afficher la barre de couleur
            opacity=0.4       # Rendre le dégradé semi-transparent
        ))

        # Ajouter les points représentant les DR
        fig.add_trace(go.Scatter(
            x=df_filtered['nb_contrats_gt1000'],
            y=df_filtered['moyenne_creances_gt1000'],
            mode='markers+text',
            text=df_filtered['NOM_DR'],
            textposition='top center',
            name="DR",
            marker=dict(size=8, color='blue')
        ))

        # Ajouter une ligne verticale (moyenne nb_contrats_gt1000)
        fig.add_trace(go.Scatter(
            x=[mean_nb_contrats, mean_nb_contrats],
            y=[df_filtered['moyenne_creances_gt1000'].min(), df_filtered['moyenne_creances_gt1000'].max()],
            mode='lines',
            line=dict(color='red', dash='dot'),
            name="Moyenne des nombre de créances significatives"
        ))

        # Ajouter une ligne horizontale (moyenne moyenne_creances_gt1000)
        fig.add_trace(go.Scatter(
            x=[df_filtered['nb_contrats_gt1000'].min(), df_filtered['nb_contrats_gt1000'].max()],
            y=[mean_moyenne_creances, mean_moyenne_creances],
            mode='lines',
            line=dict(color='blue', dash='dot'),
            name="Montant moyen des créances"
        ))

        # Mettre à jour la mise en page
        fig.update_layout(
            title=dict(
                text=f"Répartition du risque de créance signif des DR pour l'année\n {year}",
                x=0.5,  # Position horizontale (centré)
                y=0.95,  # Position verticale (proche du haut)
                xanchor="center",  # Ancrage horizontal
            yanchor="top",  # Ancrage vertical
            font=dict(color="black")  # Couleur et style du texte
            ),
            xaxis_title="Nombre de créances significatives",
            yaxis_title=yaxis_title,
            template="plotly_white",
            font=dict(color="black"),
            title_font=dict(color="black"),
            legend=dict(
                yanchor="top",
                y=-0.3,
                xanchor="center",
                x=0.5
            ),
            xaxis=dict(
                tickfont=dict(color="black"),
                title=dict(font=dict(color="black")),
                showgrid=False  # Supprimer la grille de l'axe X
            ),
            yaxis=dict(
                tickfont=dict(color="black"),
                title=dict(font=dict(color="black")),
                showgrid=False  # Supprimer la grille de l'axe Y
            )
        )

        return fig    

    # Obtenir la liste unique des années
    years = df_dr['annee'].unique()

    # Afficher les graphiques pour chaque année
    for year in years:
        st.header(f"Année {year}")

        col1, col2 = st.columns(2)

        with col1:
            #st.write("### Diagramme en radar")
            container = st.container()
            with container:
                radar_chart = generate_radar_chart(year)
                st.plotly_chart(radar_chart)

        with col2:
            #st.write("### Cartographie du risque de créance significative")
            container = st.container()
            with container:
                scatter_plot = generate_scatter_plot(year)
                st.plotly_chart(scatter_plot)

if __name__ == "__main__":
    main()