import streamlit as st
import pandas as pd
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Line

# --- SYSTÈME DE STOCKAGE PERSISTANT COMPATIBLE CLOUD ---
if 'orders' not in st.session_state:
    st.session_state.orders = [
        {
            "ID": 1,
            "Client": "Hôtel Royal Mansour",
            "Secteur": "Hospitality",
            "Total HT (DH)": 450000.0,
            "Acompte Versé (DH)": 135000.0,
            "Date Livraison": "2026-09-15",
            "Statut": "En production (Atelier Bois)",
            "Détail Articles": "Lot 1: 40 Lits de jour Outdoor en Iroko\nLot 2: 15 Tables basses en placage Noyer"
        }
    ]

if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        "Bois Massif & Placages (Noyer/Chêne/Iroko)": {"quantity": 45.0, "unit": "m³", "min": 10.0},
        "Métallurgie d'Art (Acier/Laiton/Profilés)": {"quantity": 350.0, "unit": "kg", "min": 80.0},
        "Fibres Premium (Rotin Naturel & Synthétique)": {"quantity": 120.0, "unit": "Bobines", "min": 30.0},
        "Haute Tapisserie (Textiles Certifiés & Cuirs)": {"quantity": 500.0, "unit": "Mètres", "min": 100.0}
    }

# --- DESIGN DU LOGO VECTORIEL ---
def draw_pdf_logo(width=480, height=50):
    d = Drawing(width, height)
    d.add(Rect(0, 0, width, height, fillColor=colors.HexColor("#F9F8F6"), strokeColor=None))
    d.add(Line(20, height/2, 100, height/2, strokeColor=colors.HexColor("#1A1A1A"), strokeWidth=1))
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
    story.append(draw_pdf_logo())
    story.append(Spacer(1, 20))
    
    meta_data = [
        [Paragraph("<b>MANUFACTURE DARVANNERIE</b><br/>Zone Industrielle Haut de Gamme<br/>Maroc<br/>contact@darvannerie.com", body_s),
         Paragraph(f"<b>DOCUMENT :</b> {doc_type} OFFICIEL<br/><b>RÉF :</b> DV-2026-{row['ID']}<br/><b>DATE :</b> {date.today().strftime('%d/%m/%Y')}", body_s)]
    ]
    t_meta = Table(meta_data, colWidths=[240, 240])
    t_meta.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(t_meta)
    story.append(Spacer(1, 30))
    
    story.append(Paragraph(f"<b>DESTINATAIRE / PROJET :</b>", bold_s))
    story.append(Paragraph(f"Nom du compte : {row['Client']}<br/>Division sectorielle : {row['Secteur']}<br/>Échéance d'installation ciblée : {row['Date Livraison']}", body_s))
    story.append(Spacer(1, 25))
    
    story.append(Paragraph("<b>DÉSIGNATION ET SPÉCIFICATIONS DES OUVRAGES (SUR-MESURE) :</b>", bold_s))
    story.append(Paragraph(str(row['Détail Articles']).replace('\n', '<br/>'), body_s))
    story.append(Spacer(1, 30))
    
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
    t_fin = Table(fin_data, colWidths=[240, 240])
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

# --- INTERFACE DE GESTION CONTEMPORAINE ---
st.set_page_config(page_title="ERP DARVANNERIE", layout="wide")
st.title("DARVANNERIE — Direction Industrielle & Comptabilité B2B")
st.write("Plateforme interne sécurisée d'ordonnancement des ateliers, de comptabilité des acomptes et d'édition documentaire.")

tabs = st.tabs(["📊 Tableau de Bord Global", "💸 Comptabilité & Échéances", "📝 Saisie Nouvelle Commande", "📦 Gestion des Stocks Ateliers"])
df_orders = pd.DataFrame(st.session_state.orders)

# ONGLET 1 : PRODUCTION ET CALENDRIER
with tabs[0]:
    st.subheader("Planification des chantiers et fabrication")
    if not df_orders.empty:
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
        col_select, col_actions = st.columns(2)
        
        with col_select:
            order_id = st.selectbox("Sélectionner l'ID de la commande cible", df_orders["ID"].unique())
            row_selected = df_orders[df_orders["ID"] == order_id].iloc[0]
            
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
            if st.button("❌ Clôturer et Archiver cette commande"):
                st.session_state.orders = [o for o in st.session_state.orders if o["ID"] != order_id]
                st.success("Commande archivée.")
                st.rerun()
    else:
        st.info("Aucune donnée financière disponible.")

# ONGLET 3 : NOUVELLE COMMANDE
with tabs[2]:
    st.subheader("Enregistrement d'un nouvel ordre de fabrication FF&E")
    with st.form("new_order_form"):
        c_name = st.text_input("Raison sociale du donneur d'ordre")
        p_type = st.selectbox("Secteur d'activité", ["Hospitality", "Villa & Résidentiel", "Institutionnel", "Corporate / Bureaux"])
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            total_ht = st.number_input("Montant Marché HT (DH)", min_value=0.0, step=5000.0)
        with col_f2:
            acompte_paid = st.number_input("Acompte versé à la signature (DH)", min_value=0.0, step=5000.0)
            
        deliv_date = st.date_input("Date contractuelle de livraison", value=date.today())
        p_status = st.selectbox("Ordonnancement initial / Phase d'atelier", [
            "Étude technique & Plans d'exécution", "Lancement Prototypage Témoin", "En production (Atelier Ébénisterie/Bois)", 
            "En production (Atelier Métallurgie/Art)", "En production (Atelier Tressage/Rotin)", "En production (Atelier Haute Tapisserie)",
            "Contrôle Qualité & Emballage", "Livraison & Pose sur site"
        ])
        
