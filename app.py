
import pandas as pd
import sqlite3
import enum
import logging
import sys
import bcrypt
from datetime import datetime, date

# --- 1. CONFIGURATION DU JOURNAL D'ENTREPRISE (LOGGER) ---
logger = logging.getLogger("DARVANNERIE_ERP")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

# --- 2. ENUMS ET STRUCTURES DE DONNÉES (VALUE OBJECTS) ---
class ClientSegment(enum.Enum):
    HOTEL = "Hospitality / Hôtels de Prestige"
    EMBASSY = "Ambassades / Corps Diplomatiques"
    RESTAURANT = "Gastr…
[4:48 AM, 13/07/2026] Tazart Mobilier: import streamlit as st
import pandas as pd
import sqlite3
import enum
import logging
import sys
import bcrypt
from datetime import datetime, date

# --- 1. CONFIGURATION DU JOURNAL D'ENTREPRISE (LOGGER) ---
logger = logging.getLogger("DARVANNERIE_ERP")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

# --- 2. ENUMS ET STRUCTURES DE DONNÉES (VALUE OBJECTS) ---
class ClientSegment(enum.Enum):
    HOTEL = "Hospitality / Hôtels de Prestige"
    EMBASSY = "Ambassades / Corps Diplomatiques"
    RESTAURANT = "Gastronomie / Restaurants"
    ARCHITECT = "Cabinets d'Architecture"
    INTERIOR_DESIGNER = "Designers d'Intérieur / Prescripteurs"
    DEVELOPER = "Promoteurs Immobiliers"
    GOVERNMENT = "Institutions Publiques / Ministères"
    CORPORATE = "Espaces Corporate / Bureaux"
    RESIDENTIAL = "Villas Privées & Résidences"

class WorkflowStage(enum.Enum):
    LEAD = "Lead Acquisition"
    MEETING = "Réunion d'Alignement Technique"
    QUOTATION = "Ingénierie du Chiffrage / Devis"
    APPROVAL = "Signature Contractuelle / Validation"
    TECHNICAL_STUDY = "Bureau d'Études / Plans CAD"
    PROJECT_CLOSED = "Archivage Dossier Permanent"

# --- 3. MOTEUR DE BASE DE DONNÉES (PERSISTENCE) ---
DB_NAME = "darvannerie_management.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS crm_prospects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            segment TEXT NOT NULL,
            contact_person TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            address TEXT,
            website TEXT,
            lead_source TEXT,
            potential_value REAL,
            probability REAL,
            next_follow_up TEXT,
            notes TEXT
        )
    """)
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone() == 0:
        salt = bcrypt.gensalt(rounds=12)
        pwd_hash = bcrypt.hashpw("DarvannerieLux2026!".encode('utf-8'), salt).decode('utf-8')
        c.execute("INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                  ("ceo_admin", pwd_hash, "Director General", "Admin"))
    c.execute("SELECT COUNT(*) FROM crm_prospects")
    if c.fetchone() == 0:
        c.execute("""
            INSERT INTO crm_prospects (company_name, segment, contact_person, phone, email, potential_value, probability, next_follow_up, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Hôtel Royal Mansour - Extension", "Hospitality / Hôtels de Prestige", "Directeur Achats FF&E", "+212 524 38 88 88", "procurement@royalmansour.ma", 1650000.0, 0.75, "2026-07-20", "Projet sur-mesure bois de Noyer et rotin."))
    conn.commit()
    conn.close()

# --- 4. COUCHE SERVICES ET LOGIQUE CRM ---
class CRMRepositoryAndService:
    def _init_(self, db_path):
        self.db_path = db_path

    def get_all_prospects_df(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT id as ID, company_name as [Établissement / Compte], segment as [Secteur d'Activité], contact_person as [Contact Principal], phone as [Téléphone], email as [E-mail], potential_value as [Valeur Potentielle (DH)], probability as [Probabilité], next_follow_up as [Prochain Suivi chantiers], notes as [Notes de Brief] FROM crm_prospects ORDER BY company_name", conn)
        conn.close()
        return df

    def register_prospect(self, name, segment_str, contact, phone, email, address, website, source, value, prob_percent, follow_date, notes):
        if not name or not email or not contact:
            raise ValueError("Les champs Nom, E-mail et Contact Principal sont obligatoires.")
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        prob_decimal = float(prob_percent / 100.0)
        c.execute("""
            INSERT INTO crm_prospects (company_name, segment, contact_person, phone, email, address, website, lead_source, potential_value, probability, next_follow_up, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, segment_str, contact, phone, email, address, website, source, value, prob_decimal, str(follow_date), notes))
        conn.commit()
        conn.close()

    def delete_prospect(self, p_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM crm_prospects WHERE id = ?", (p_id,))
        conn.commit()
        conn.close()

# --- 5. INTERFACE UTILISATEUR VISUELLE ---
init_db()
crm_system = CRMRepositoryAndService(DB_NAME)

st.sidebar.title("⚜️ DARVANNERIE")
st.sidebar.caption("Système Industriel Intégré v1.0")

if 'authenticated_user' not in st.session_state:
    st.session_state['authenticated_user'] = {"username": "ceo_admin", "role": "Admin", "name": "Directeur Général"}
user = st.session_state['authenticated_user']
st.sidebar.write(f"Session : *{user['name']}*")
st.sidebar.write("---")

navigation_selector = st.sidebar.radio("Navigation Directions", ["01 Architecture du Système", "02 Direction Commerciale (CRM)"])

st.markdown("""
    <style>
        .metric-card {
            background: white; padding: 1.5rem; border-radius: 8px; border: 1px solid #EAE6DF;
            box-shadow: 0 4px 12px rgba(26, 26, 26, 0.02); margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

if navigation_selector == "01 Architecture du Système":
    st.title("Moteur Central DARVANNERIE ERP")
    st.success("Toutes les connexions aux pools relationnels SQL sont synchronisées.")
    st.info("Passez à l'onglet '02 Direction Commerciale' dans le menu de gauche pour manipuler les clients.")

elif navigation_selector == "02 Direction Commerciale (CRM)":
    st.subheader("⚜️ Portefeuille Comptes & Grands Comptes B2B")
    st.write("Gestion des relations stratégiques avec les architectes, les groupes hôteliers et les institutions.")
    
    tab_pipeline, tab_creation = st.tabs(["📊 Entonnoir des Affaires", "➕ Inscrire un Compte d'Architecture / Client"])
    
    with tab_pipeline:
        df_crm = crm_system.get_all_prospects_df()
        if not df_crm.empty:
            df_crm["Valeur Pondérée (DH)"] = df_crm["Valeur Potentielle (DH)"] * df_crm["Probabilité"]
            total_val = df_crm["Valeur Potentielle (DH)"].sum()
            total_weighted = df_crm["Valeur Pondérée (DH)"].sum()
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"<div class='metric-card'><h5>Volume Brut en Négociation</h5><h2>{total_val:,.2f} DH</h2></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='metric-card'><h5>Pipeline Pondéré de Confiance</h5><h2>{total_weighted:,.2f} DH</h2></div>", unsafe_allow_html=True)
            
            st.write("---")
            df_display = df_crm.copy()
            df_display["Probabilité de Succès"] = (df_display["Probabilité"] * 100).astype(int).astype(str) + "%"
            st.dataframe(df_display.drop(columns=["Probabilité", "Valeur Pondérée (DH)"]), use_container_width=True, hide_index=True)
            
            st.write("---")
            st.caption("Zone de Nettoyage de Sécurité")
            id_to_delete = st.number_input("ID du compte à supprimer", min_value=1, step=1)
            if st.button("Archiver / Supprimer définitivement le compte"):
                crm_system.delete_prospect(int(id_to_delete))
                st.success(f"Compte ID {id_to_delete} retiré.")
                st.rerun()
        else:
            st.info("Aucun prospect enregistré pour le moment.")
            
    with tab_creation:
        with st.form("crm_luxury_form"):
            st.markdown("### Fiche d'Identification Institutionnelle")
            col1, col2 = st.columns(2)
            with col1:
                company_name = st.text_input("Raison Sociale / Entité Corporate")
                segment_selection = st.selectbox("Secteur Spécifique", [seg.value for seg in ClientSegment])
                contact_person = st.text_input("Interlocuteur Principal (Ex: Directeur FF&E)")
                phone = st.text_input("Ligne Directe de Contact")
                email = st.text_input("Adresse E-mail Professionnelle")
            with col2:
                address = st.text_area("Adresse Physique / Bureau de Prescription")
                website = st.text_input("Site Web / Portfolio en ligne du Designer")
                source = st.selectbox("Source de l'Opportunité", ["Recommandation / Réseau", "Appel d'Offre Institutionnel", "Prospection Directe", "Inbound Digital"])
                potential_value = st.number_input("Estimation Budget Ameublement Global (DH)", min_value=0.0, step=10000.0, format="%.2f")
                probability_percent = st.slider("Indice de Probabilité de Signature (%)", min_value=10, max_value=100, value=30, step=5)
                next_follow_up = st.date_input("Date planifiée du prochain Brief Technique", value=date.today())
            
            notes = st.text_area("Spécificités du projet / Matières demandées (Ex: Bois de Noyer, finitions Laiton)")
            if st.form_submit_button("Valider et Ouvrir le Dossier Client"):
                try:
                    crm_system.register_prospect(company_name, segment_selection, contact_person, phone, email, address, website, source, potential_value, probability_percent, next_follow_up, notes)
