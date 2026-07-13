import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Line

# --- INITIALISATION DE LA BASE DE DONNÉES ---
DB_NAME = "darvannerie_management.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            project_type TEXT,
            total_ht REAL,
            amount_paid REAL,
            delivery_date TEXT,
            status TEXT,
            items_json TEXT
        )
    """)
    c.execute("SELECT COUNT(*) FROM orders")
    if c.fetchone() == 0:
        # Données initiales exemplaires pour la manufacture
        c.execute("""
            INSERT INTO orders (client_name, project_type, total_ht, amount_paid, delivery_date, status, items_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "Hôtel Royal Mansour", "Hospitality", 450000.0, 135000.0, 
            "2026-09-15", "En production (Atelier Bois)", 
            "Lot 1: 40 Lits de jour Outdoor en Iroko\nLot 2: 15 Tables basses en placage Noyer"
        ))
        conn.commit()
    conn.close()

def get_orders():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT id as ID, client_name as Client, project_type as [Secteur], total_ht as [Total HT (DH)], amount_paid as [Acompte Versé (DH)], delivery_date as [Date Livraison], status as Statut, items_json as [Détail Articles] FROM orders", conn)
    conn.close()
    return df

def save_order(client, p_type, tht, paid, d_date, status, items):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders (client_name, project_type, total_ht, amount_paid, delivery_date, status, items_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (client, p_type, tht, paid, str(d_date), status, items))
    conn.commit()
    conn.close()

def remove_order(order_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()

# --- DESIGN DU LOGO VECTORIEL EXAMPLAIRE ---
def draw_pdf_logo(width=480, height=50):
    d = Drawing(width, height)
    # Rectangle de fond beige/lin très subtil
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#F9F8F6"), strokeColor=None))
    # Ligne géométrique noire représentant la précision
    d.add(Line(20, height/2, 100, height/2, strokeColor=colors.HexColor("#1A1A1A"), strokeWidth=1))
    # Monogramme textuel
    d.add(String(120, height/2 - 5, "D A R V A N N E R I E", fontName="Helvetica-Bold", fontSize=14, fillColor=colors.HexColor("#1A1A1A")))
    d.add(Line(280, height/2, 460, height/2, strokeColor=colors.HexColor("#1A1A1A"), strokeWidth=1))
    return d

# --- CONSTRUCTEUR DE DOCUMENTS FACTURES & DEVIS ---
def build_document_pdf(row, doc_type="DEVIS"):
    filename = f"{doc_type}_{str(row['Client']).replace(' ', '_')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    
    body_s = ParagraphStyle('DocBody', fontName='Helvetica', fontSize=10, leading=15, textColor=colors.HexColor("#333333"))
    bold_s = ParagraphStyle('DocBodyBold', parent=body_s, fontName='Helvetica-Bold', textColor=colors.HexColor("#1A1A1A"))
    
    story = []
    
    # 1. En-tête graphique (Logo)
    story.append(draw_pdf_logo())
    story.append(Spacer(1, 20))
    
    # 2. Informations Institutionnelles
    meta_data = [
        [Paragraph("<b>MANUFACTURE DARVANNERIE</b><br/>Zone Industrielle Haut de Gamme<br/>Maroc<br/>contact@darvannerie.com", body_s),
         Paragraph(f"<b>DOCUMENT :</b> {doc_type} OFFICIEL<br/><b>RÉF :</b> DV-2026-{row['ID']}<br/><b>DATE :</b> {date.today().strftime('%d/%m/%Y')}", body_s)]
    ]
    t_meta = Table(meta_data, colWidths=)
    t_meta.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_meta)
    story.append(Spacer(1, 30))
    
    # 3. Informations Destinataire
    story.append(Paragraph(f"<b>DESTINATAIRE / PROJET :</b>", bold_s))
    story.append(Paragraph(f"Nom du compte : {row['Client']}<br/>Division sectorielle : {row['Secteur']}<br/>Échéance d'installation ciblée : {row['Date Livraison']}", body_s))
    story.append(Spacer(1, 25))
    
    # 4. Spécifications techniques des ouvrages
    story.append(Paragraph("<b>DÉSIGNATION ET SPÉCIFICATIONS DES OUVRAGES (SUR-MESURE) :</b>", bold_s))
    story.append(Paragraph(str(row['Détail Articles']).replace('\n', '<br/>'), body_s))
    story.append(Spacer(1, 30))
    
    # 5. Décompte Financier B2B complet (HT, TVA, TTC, Acompte)
    total_ht = float(row['Total HT (DH)'])
    tva = total_ht * 0.20
    total_ttc = total_ht + tva
    acompte = float(row['Acompte Versé (DH)'])
    reste_a_payer = total_ttc - acompte
    
    fin_data = [
        [Paragraph("<b>SOUS-TOTAL TOTAL HT :</b>", body_s), Paragraph(f"{total_ht:,.2f} DH", body_s)],
        [Paragraph("<b>TVA RÉGLEMENTAIRE (20%) :</b>", body_s), Paragraph(f"{tva:,.2f} DH", body_s)],
        [Paragraph("<b>MONTANT TOTAL TTC :</b>", bold_s), Paragraph(f"<b>{total_ttc:,.2f} DH</b>", bold_s)],
        [Paragraph("<b>ACOMPTE DÉJÀ PERÇU :</b>", body_s), Paragraph(f"{acompte:,.2f} DH", body_s)],
        [Paragraph("<b>SOLDE RESTANT À PERCEVOIR :</b>", bold_s), Paragraph(f"<font color='#7D6752'><b>{reste_a_payer:,.2f} DH</b></font>", bold_s)]
    ]
    t_fin = Table(fin_data, colWidths=)
    t_fin.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F9F8F6")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E5E5")),
    ]))
    story.append(t_fin)
    
    story.append(Spacer(1, 40))
    story.append(Paragraph("<font size=7 color=#888888>CONDITIONS DE FABRICATION : Lancement en ébénisterie et tapisserie conditionné à la validation opérationnelle du prototype d'étude technique. Les délais de livraison courent à réception de l'acompte de couverture.</font>", body_s))
    
    doc.build(story)
    return filename

# --- INTERFACE DE GESTION CONTEMPORAINE (STREAMLIT) ---
init_db()
st.set_page_config(page_title="ERP DARVANNERIE", layout="wide")

st.title("DARVANNERIE — Direction Industrielle & Comptabilité B2B")
st.write("Plateforme interne sécurisée d'ordonnancement des ateliers, de comptabilité des acomptes et d'édition documentaire.")

tabs = st.tabs(["📊 Tableau de Bord Global", "💸 Comptabilité & Échéances", "📝 Saisie Nouvelle Commande"])
df_orders = get_orders()

# ONGLET 1 : PRODUCTION ET CALENDRIER
with tabs[0]:
    st.subheader("Planification des chantiers et fabrication")
    if not df_orders.empty:
        # Calcul dynamique des jours restants avant livraison
        def compute_days(date_str):
            try:
                target = datetime.strptime(date_str, "%Y-%m-%d").date()
                days = (target - date.today()).days
                return f"{days} jours restants" if days >= 0 else "Échéance dépassée"
            except:
                return "Date non définie"
        
        df_dash = df_orders.copy()
        df_dash["Compte à rebours"] = df_dash["Date Livraison"].apply(compute_days)
        
        st.dataframe(df_dash[["ID", "Client", "Secteur", "Date Livraison", "Compte à rebours", "Statut"]], use_container_width=True, hide_index=True)
    else:
        st.info("Aucun carnet de commande actif.")

# ONGLET 2 : COMPTABILITÉ ET PDF
with tabs[1]:
    st.subheader("Suivi financier des acomptes et facturation")
    if not df_orders.empty:
        col_select, col_actions = st.columns([1, 2])
        
        with col_select:
            order_id = st.selectbox("Sélectionner l'ID de la commande cible", df_orders["ID"].unique())
            row_selected = df_orders[df_orders["ID"] == order_id].iloc[0]
            
            # Calcul des indicateurs financiers instantanés
            tht = float(row_selected["Total HT (DH)"])
            ttc = tht * 1.20
            paid = float(row_selected["Acompte Versé (DH)"])
            pourcentage_acompte = (paid / ttc * 100) if ttc > 0 else 0
            reste = ttc - paid
            
            st.metric("Total TTC à percevoir", f"{ttc:,.2f} DH")
            st.metric("Acompte perçu", f"{paid:,.2f} DH", f"{pourcentage_acompte:.1f}% du TTC")
            st.metric("Reste à recouvrer", f"{reste:,.2f} DH")
            
        with col_actions:
            st.markdown("### 🖨️ Édition Documentaire Réglementaire")
            col_b1, col_b2 = st.columns(2)
            
            with col_b1:
                if st.button("Générer le Devis Client"):
                    pdf_name = build_document_pdf(row_selected, "DEVIS")
                    with open(pdf_name, "rb") as f:
                        st.download_button(label="📥 Télécharger le Devis PDF", data=f, file_name=pdf_name, mime="application/pdf")
            
            with col_b2:
                if st.button("Générer la Facture d'Acompte"):
                    pdf_name = build_document_pdf(row_selected, "FACTURE_ACOMPTE")
                    with open(pdf_name, "rb") as f:
                        st.download_button(label="📥 Télécharger la Facture PDF", data=f, file_name=pdf_name, mime="application/pdf")
            
            st.write("---")
            st.markdown("### ⚙️ Administration")
            if st.button("❌ Clôturer et Archiver cette commande définitivement"):
