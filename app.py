import streamlit as st
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
    LEAD = "01. Lead Acquisition"
    MEETING = "02. Réunion Technique & Alignement"
    QUOTATION = "03. Chiffrage & Devis"
    APPROVAL = "04. Validation Contractuelle"
    DEPOSIT = "05. Encaissement Acompte"
    TECHNICAL_STUDY = "06. Bureau d'Études / Plans CAD"
    MATERIAL_PURCHASE = "07. Achats Approvisionnements"
    WOOD_WORKSHOP = "08. Atelier Ébénisterie / Bois"
    METAL_WORKSHOP = "09. Atelier Métallurgie d'Art"
    PAINTING = "10. Peinture, Vernis & Laquage"
    RATTAN = "11. Tressage Rotin Main"
    UPHOLSTERY = "12. Haute Tapisserie"
    ASSEMBLY = "13. Assemblage Final"
    QUALITY_CONTROL = "14. Contrôle Qualité Strict"
    PACKAGING = "15. Mise en Caisse Logistique"
    DELIVERY = "16. Transport & Livraison"
    INSTALLATION = "17. Pose sur Site"
    PROJECT_CLOSED = "18. Facturation Finale & Clôture"

# --- 3. MOTEUR DE BASE DE DONNÉES (PERSISTENCE) ---
DB_NAME = "darvannerie_management.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Table Utilisateurs
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    # Table Prospects CRM
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
    # Table Commandes & Projets de Production
    c.execute("""
        CREATE TABLE IF NOT EXISTS production_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prospect_id INTEGER NOT NULL,
            project_title TEXT NOT NULL,
            current_stage TEXT NOT NULL,
            progress_percent REAL DEFAULT 0.0,
            assigned_artisan TEXT,
            start_date TEXT,
            end_date TEXT,
            estimated_days INTEGER,
            internal_comments TEXT,
            total_ht REAL DEFAULT 0.0,
            amount_paid REAL DEFAULT 0.0,
            FOREIGN KEY (prospect_id) REFERENCES crm_prospects(id)
        )
    """)
    
    # Seeding initial si vide
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone() == 0:
        salt = bcrypt.gensalt(rounds=12)
        pwd_hash = bcrypt.hashpw("DarvannerieLux2026!".encode('utf-8'), salt).decode('utf-8')
        c.execute("INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                  ("ceo_admin", pwd_hash, "Director General", "Admin"))
        
    c.execute("SELECT COUNT(*) FROM crm_prospects")
    if c.fetchone() == 0:
        c.execute("""
            INSERT INTO crm_prospects (id, company_name, segment, contact_person, phone, email, potential_value, probability, next_follow_up, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, "Hôtel Royal Mansour - Extension", "Hospitality / Hôtels de Prestige", "Directeur Achats FF&E", "+212 524 38 88 88", "procurement@royalmansour.ma", 1650000.0, 0.75, "2026-07-20", "Projet sur-mesure bois de Noyer et rotin."))
        
    c.execute("SELECT COUNT(*) FROM production_projects")
    if c.fetchone() == 0:
        c.execute("""
            INSERT INTO production_projects (prospect_id, project_title, current_stage, progress_percent, assigned_artisan, start_date, end_date, estimated_days, internal_comments, total_ht, amount_paid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (1, "Lot 40 Lits de Jour d'Extérieur en Iroko Massif", "08. Atelier Ébénisterie / Bois", 45.0, "Youssef (Chef Ébéniste)", "2026-07-01", "2026-08-15", 45, "Séchage du bois validé. Débitage des structures de lits en cours.", 1375000.0, 495000.0))
        
    conn.commit()
    conn.close()

# --- 4. SERVICES ET LOGIQUE CRM, PROD & FINANCE ---
class BusinessEngine:
    def __init__(self, db_path):
        self.db_path = db_path

    # CRM Mappings
    def get_all_prospects_df(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT id as ID, company_name as [Établissement], segment as [Secteur d'Activité], contact_person as [Contact Principal], phone as [Téléphone], email as [E-mail], potential_value as [Valeur Potentielle (DH)], probability as [Probabilité], next_follow_up as [Prochain Suivi], notes as [Notes] FROM crm_prospects ORDER BY company_name", conn)
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

    # Production Mappings
    def get_production_projects_df(self):
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT p.id as [ID Projet], c.company_name as [Client / Compte], p.project_title as [Intitulé Ouvrage sur-mesure], 
                   p.current_stage as [Étape Actuelle], p.progress_percent as [Avancement], p.assigned_artisan as [Responsable], 
                   p.start_date as [Début], p.end_date as [Échéance Livraison], p.estimated_days as [Durée Est. (Jours)], 
                   p.internal_comments as [Notes Atelier], p.total_ht as [Total HT (DH)], p.amount_paid as [Acompte Reçu (DH)]
            FROM production_projects p
            JOIN crm_prospects c ON p.prospect_id = c.id
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def register_production_project(self, prospect_id, title, stage, progress, artisan, start, end, days, comments, total_ht, amount_paid):
        if not title:
            raise ValueError("L'intitulé du projet de fabrication est obligatoire.")
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO production_projects (prospect_id, project_title, current_stage, progress_percent, assigned_artisan, start_date, end_date, estimated_days, internal_comments, total_ht, amount_paid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (prospect_id, title, stage, progress, artisan, str(start), str(end), days, comments, total_ht, amount_paid))
        conn.commit()
        conn.close()

    def update_production_stage(self, project_id, next_stage, next_progress, comments):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            UPDATE production_projects 
            SET current_stage = ?, progress_percent = ?, internal_comments = ?
            WHERE id = ?
        """, (next_stage, next_progress, comments, project_id))
        conn.commit()
        conn.close()

    # Finance Mappings
    def update_financial_ledger(self, project_id, total_ht, amount_paid):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            UPDATE production_projects 
            SET total_ht = ?, amount_paid = ?
            WHERE id = ?
        """, (total_ht, amount_paid, project_id))
        conn.commit()
        conn.close()

# --- 5. INTERFACE UTILISATEUR GLOBALE (UI) ---
init_db()
system_engine = BusinessEngine(DB_NAME)

st.sidebar.title("⚜️ DARVANNERIE")
st.sidebar.caption("Système Industriel Intégré v1.0")

if 'authenticated_user' not in st.session_state:
    st.session_state['authenticated_user'] = {"username": "ceo_admin", "role": "Admin", "name": "Director General"}
user = st.session_state['authenticated_user']
st.sidebar.write(f"Session : **{user['name']}**")
st.sidebar.write("---")

navigation_selector = st.sidebar.radio("Directions Modules", [
