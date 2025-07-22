import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp

def main():
    # Configurer la page pour utiliser toute la largeur
    st.set_page_config(layout="wide")

    st.title("Analyse des Créances significatives par Branche")
    st.markdown("Cette section permet de visualiser les créances significatives par Branche et d'analyser les risques associés en constatant l'évolution de la criticité au fil du temps.")
    # Charger les données localement
    @st.cache_data
    def load_data_br():
        excel_file = r"C:\Users\pc\Desktop\New folder\Python folder\risque_credit\streamlit_app\base_creance_branche_finale.xlsx"
        df_br = pd.read_excel(excel_file)
        return df_br

    df_br = load_data_br()


    # Calculer la criticité
    df_br["criticite"] = df_br["proba_bayesienne"] * df_br["moyenne_montant_creances_sinif"]

    # Obtenir les années et les DR uniques
    years = sorted(df_br['annee'].unique())
    drs = sorted(df_br['NOM_DR'].unique())
    branches = sorted(df_br['BRANCHE'].unique())

    # Sélection de la DR
    selected_dr = st.selectbox("Sélectionnez une Direction Régionale (DR)", drs)


    # Fonction pour générer les graphiques radar
    # Fonction pour générer les graphiques radar
    def generate_radar_charts(dr):
        # Créer une figure pour une seule DR
        fig = sp.make_subplots(
            rows=1, cols=len(years),
            specs=[[{'type': 'polar'}] * len(years)],
            subplot_titles=[f"{year}" for year in years]
        )

        # Calculer le maximum des probabilités bayésiennes pour cette DR sur toutes les années
        max_proba = df_br[df_br['NOM_DR'] == dr]['proba_bayesienne'].max()

        for i, year in enumerate(years):
            # Filtrer les données pour la DR et l'année actuelles
            df_filtered = df_br[(df_br['NOM_DR'] == dr) & (df_br['annee'] == year)]

            if not df_filtered.empty:
                # Ajouter une trace radar pour cette DR et cette année
                fig.add_trace(
                    go.Scatterpolar(
                        r=df_filtered['proba_bayesienne'],
                        theta=df_filtered['BRANCHE'],
                        fill='toself',
                        name=f"{dr} - {year}"
                    ),
                    row=1, col=i + 1
                )

                # Mettre à jour l'échelle de l'axe radial pour le sous-plot
                fig.update_polars(
                    row=1, col=i + 1,
                    angularaxis=dict(
                        tickfont=dict(color="black", size=10),  # Réduire la taille des écritures des branches
                        rotation=90,  # Rapprocher les années du cercle
                        direction="clockwise"  # Ajuster la direction des labels
                    ),
                    radialaxis=dict(
                        tickfont=dict(color="black", size=10),  # Réduire la taille des écritures radiales
                        range=[0, max_proba]  # Ajuster la plage des valeurs radiales
                    )
                )

        # Mettre à jour la mise en page globale
        fig.update_layout(
            title=f"Évolution des probabilités bayésiennes pour {dr}",
            height=330,
            width=800,  # Réduire la largeur totale pour rapprocher les radar charts
            showlegend=False,
            font=dict(color="black"),
            title_font=dict(color="black"),
            margin=dict(l=20, r=20, t=100, b=1)  # Réduire les marges gauche, droite, haut et bas
        )

        return fig
    # Fonction pour générer les graphiques de criticité
    def generate_criticite_chart(dr):
        df_dr = df_br[df_br['NOM_DR'] == dr]

        fig = go.Figure()

        for branch in branches:
            df_line = df_dr[df_dr['BRANCHE'] == branch]
            fig.add_trace(go.Scatter(
                x=df_line['annee'],
                y=df_line['criticite'],
                mode='lines+markers',
                name=branch
            ))

        # Mettre à jour la mise en page
        fig.update_layout(
            title=f"Évolution de la criticité par branche pour {dr}",
            xaxis_title="Année",
            yaxis_title="Criticité (Proba × Montant moyen)",
            legend_title="Branche",
            height=400,
            width=900
        )

        return fig

    # Afficher les graphiques dans des conteneurs
    with st.container():
        st.header(f"Analyse des créances pour {selected_dr}")
        
        radar_charts = generate_radar_charts(selected_dr)
        st.plotly_chart(radar_charts, use_container_width=True)

    with st.container():
        
        criticite_chart = generate_criticite_chart(selected_dr)
        st.plotly_chart(criticite_chart, use_container_width=True)
        
if __name__ == "__main__":
    main()