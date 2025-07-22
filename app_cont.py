import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

def main():
    # Configurer la page pour utiliser toute la largeur
    st.set_page_config(layout="wide")

    # Charger les données localement
    @st.cache_data
    def load_data_cont():
        df_cont = pd.read_excel(r"C:\Users\pc\Desktop\New folder\Python folder\risque_credit\streamlit_app\base_contentieux_finale_v2.xlsx")
        return df_cont

    df_cont = load_data_cont()

    st.title("Analyse des Créances contentieuses par Direction Régionale (DR)")
    st.markdown("Cette section permet de visualiser les créances contentieuses par Direction Régionale (DR) et d'analyser les risques associés en nombre et en montant moyen.")

    # Calculer le nombre total de créances significatives et le nombre de créances contentieuses par année
    creances_par_annee = df_cont.groupby('annee').agg({
        'sum_creance_signif': 'sum',
        'creance_signif_cont': 'sum'
    }).reset_index()

    # Calculer le pourcentage de créances contentieuses parmi les créances significatives
    creances_par_annee['pourcentage_contentieuses'] = (creances_par_annee['creance_signif_cont'] / creances_par_annee['sum_creance_signif']) * 100

    # Formater les valeurs en pourcentage avec le symbole %
    creances_par_annee['pourcentage_contentieuses'] = creances_par_annee['pourcentage_contentieuses'].apply(lambda x: f"{x:.2f}%")
    creances_par_annee= creances_par_annee.rename(columns={'annee': 'Année',
                                                        "sum_creance_signif":"Nombre de créances significatives",
                                                        "creance_signif_cont":"Nombre créances contentieuses",
                                                        'pourcentage_contentieuses': "Créances contentieuses/Créances significatives (%)"})
    # Afficher le tableau des pourcentages
    st.markdown("### Pourcentage de créances contentieuses parmi les créances significatives par année")
    st.write(creances_par_annee)

    # Créer un graphique en ligne pour montrer l'évolution du pourcentage au fil des années
    fig_line = px.line(
        creances_par_annee,
        x='Année',
        y="Créances contentieuses/Créances significatives (%)",
        title="Évolution du pourcentage de créances contentieuses parmi les créances significatives",
        
    )

    # Mettre à jour la mise en page du graphique en ligne
    fig_line.update_layout(
        xaxis_title="Année",
        yaxis_title="créances contentieuses/créances significatives (%)",
        yaxis=dict(ticksuffix="%")
    )

    # Afficher le graphique en ligne
    st.plotly_chart(fig_line)

    # Dictionnaire des abréviations pour les DR
    abbreviations = {
        "ALGER1": "ALG1",
        "ALGER2": "ALG2",
        "ALGER3": "ALG3",
        "ANNABA": "ANN",
        "BATNA": "BAT",
        "BECHAR": "BECH",
        "BLIDA": "BLI",
        "CONSTANTINE": "CON",
        "CORPORATE": "COR",
        "ORAN": "ORA",
        "OUARGLA": "OUAR",
        "RELIZANE": "REL",
        "SBA": "SBA",
        "SETIF": "SET",
        "TIZIOUZOU": "TIZI",
        "TLEMCEN": "TLE"
    }

    # Fonction pour générer le scatter plot des créances contentieuses
    def generate_cont_scatter_plot(year):
        df_filtered = df_cont[df_cont['annee'] == year].copy()
        df_filtered['montant_moyen_creances'] = df_filtered['somme_montant_creance'] / df_filtered['creance_signif_cont']
        df_filtered['NOM_DR'] = df_filtered['NOM_DR'].map(abbreviations)

        mean_creances_signif = df_filtered['creance_signif_cont'].mean()
        mean_montant_moyen_creances = df_filtered['montant_moyen_creances'].mean()
        # Créer une grille pour le dégradé de couleur
        x = np.linspace(df_filtered['creance_signif_cont'].min(), df_filtered['creance_signif_cont'].max(), 100)
        y = np.linspace(df_filtered['montant_moyen_creances'].min(), df_filtered['montant_moyen_creances'].max(), 100)
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
                          x=1.3,
                          xanchor="right",
                          y=0.5,
                          yanchor="bottom"
                          ),    # afficher la barre de couleur
            opacity=0.4       # Rendre le dégradé semi-transparent
        ))


        fig.add_trace(go.Scatter(
            x=df_filtered['creance_signif_cont'],
            y=df_filtered['montant_moyen_creances'],
            mode='markers+text',
            text=df_filtered['NOM_DR'],
            textposition='top center',
            name=f"Année {year}",
            marker=dict(size=10, color='blue'),
            textfont=dict(size=12)
        ))

        fig.add_trace(go.Scatter(
            x=[mean_creances_signif, mean_creances_signif],
            y=[df_filtered['montant_moyen_creances'].min(), df_filtered['montant_moyen_creances'].max()],
            mode='lines',
            line=dict(color='red', dash='dot'),
            name=f"nombre moyen de créances contentieuses (Année {year})"
        ))

        fig.add_trace(go.Scatter(
            x=[df_filtered['creance_signif_cont'].min(), df_filtered['creance_signif_cont'].max()],
            y=[mean_montant_moyen_creances, mean_montant_moyen_creances],
            mode='lines',
            line=dict(color='blue', dash='dot'),
            name=f"moyenne des montants moyens des créances significatives (Année {year})"
        ))

        
        fig.update_layout(
            title=dict(
                #x=0.5,
                y=0.95,    
                text=f"Cartographie du risque de créances contentieuses par DR pour l'année {year}"),
            xaxis_title="Nombre de créances contentieuses",
            yaxis_title="Montant moyen des créances contentieuses",
            template="plotly_white",
            width=900,
            height=600,
            legend=dict(
                yanchor="top",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            font=dict(color="black", size=10),
            title_font=dict(color="black", size=12),
            xaxis=dict(
                tickfont=dict(color="black", size=10),
                showgrid=False,
                title=dict(font=dict(color="black", size=12))
            ),
            yaxis=dict(
                tickfont=dict(color="black", size=10),
                showgrid=False,
                title=dict(font=dict(color="black", size=10))
            )
        )

        return fig

    # Fonction pour générer le radar chart des créances contentieuses
    def generate_cont_radar_chart(year):
        data = df_cont[df_cont['annee'] == year]
        data_sorted = data.sort_values(by='proba_bayesienne', ascending=False)

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=data_sorted['proba_bayesienne'],
            theta=data_sorted['NOM_DR'],
            name=str(year),
            fill='toself'
        ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            title=dict(
                    text=f"Diagramme en Radar du risque de créances contentieuses par DR - {year}",
                    font=dict(color="black", size=12),
                    #x=0.5,
                    y=0.95),
            height=400,
            width=700
        )

        return fig

    # Obtenir la liste unique des années
    years = df_cont['annee'].unique()

    # Afficher les graphiques pour chaque année
    for year in years:
        st.header(f"Année {year}")

        col1, col2 = st.columns(2)

        with col1:
            #st.write("### Diagramme en Radar")
            container = st.container()
            with container:
                radar_chart = generate_cont_radar_chart(year)
                st.plotly_chart(radar_chart)

        with col2:
            #st.write("### Cartographie du risque de créances contentieuses")
            container = st.container()
            with container:
                scatter_plot = generate_cont_scatter_plot(year)
                st.plotly_chart(scatter_plot)

if __name__ == "__main__":
    main()