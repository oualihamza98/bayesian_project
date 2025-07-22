import streamlit as st
import eda
import app_dr
import app_branche
import app_cont

# Configurer la page pour utiliser toute la largeur
st.set_page_config(layout="wide")


# Menu latéral pour naviguer entre les compartiments
menu = st.sidebar.selectbox(
    "Navigation",
    ["Exploratory Data Analysis", "Analyse par DR", "Analyse par branche", "Analyse des créances contentieuses"]
)

if menu == "Exploratory Data Analysis":
    
    eda.main()
elif menu == "Analyse par DR":
    
    app_dr.main()
elif menu == "Analyse par branche":
    
    app_branche.main()
elif menu == "Analyse des créances contentieuses":
    
    app_cont.main()
