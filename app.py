%%writefile app.py
import streamlit as st
from os import path
from core.logger import logger
from initialize_system import execute_cold_boot_provisioning
from ui.views.crm_view import render_crm_module

st.set_page_config(
    page_title="DARVANNERIE ERP v1.0",
    page_icon="⚜️",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'engine_initialized' not in st.session_state:
    execute_cold_boot_provisioning()
    st.session_state['engine_initialized'] = True

st.markdown("""
    <style>
        :root {
            --primary-charcoal: #1A1A1A;
            --luxury-gold-tone: #7D6752;
            --alabaster-background: #F9F8F6;
        }
        .reportview-container .main .block-container {
            padding-top: 2rem;
            background-color: var(--alabaster-background);
        }
        h1, h2, h3 {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
            font-weight: 700 !important;
            color: var(--primary-charcoal) !important;
            letter-spacing: -0.02em;
        }
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #EAE6DF;
            box-shadow: 0 4px 12px rgba(26, 26, 26, 0.02);
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

def render_application_entrypoint():
    st.sidebar.title("⚜️ DARVANNERIE")
    st.sidebar.caption("Système Industriel Intégré v1.0")
    
    if 'authenticated_user' not in st.session_state:
        st.session_state['authenticated_user'] = {"username": "ceo_admin", "role": "Admin", "name": "Directeur Général"}
        
    user = st.session_state['authenticated_user']
    st.sidebar.write(f"Session : **{user['name']}**")
    st.sidebar.write("---")
    
    navigation_selector = st.sidebar.radio(
        "Navigation Directions",
        ["01 Architecture du Système", "02 Direction Commerciale (CRM)"]
    )
    
    if navigation_selector == "01 Architecture du Système":
        st.title("Moteur Central DARVANNERIE ERP")
        st.success("Toutes les connexions aux pools relationnels SQL sont synchronisées.")
        st.info("Passez à l'onglet '02 Direction Commerciale' dans le menu de gauche pour manipuler les clients.")
    elif navigation_selector == "02 Direction Commerciale (CRM)":
        render_crm_module()

if __name__ == "__main__":
    render_application_entrypoint()
