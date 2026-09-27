import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Configuration de la page optimisée pour l'écran tactile de l'iPad
st.set_page_config(
    page_title="Caisse Snack Kebab",
    page_icon="🥙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Nom du fichier pour sauvegarder l'historique sur le cloud
FICHIER_HISTORIQUE = "ventes_journee.csv"

# Initialisation du panier dans la session de la tablette
if "panier" not in st.session_state:
    st.session_state.panier = {}

# Menu du Snack Kebab
MENU = {
    "🥪 Sandwichs & Plats": {
        "Kebab Classique": 6.50,
        "Tacos L (2 viandes)": 8.00,
        "Burger Cheese": 5.50,
        "Assiette Kebab": 10.50,
    },
    "🍟 Frites & Supps": {
        "Petite Frite": 2.50,
        "Grande Frite": 3.50,
        "Supplément Fromage": 0.80,
        "Supplément Viande": 2.00,
    },
    "🥤 Boissons": {
        "Canette 33cl": 1.80,
        "Bouteille Eau 50cl": 1.20,
        "Capri-Sun": 1.50,
    },
    "📦 Menus": {
        "Menu Kebab (Frites+Boisson)": 9.50,
        "Menu Tacos (Frites+Boisson)": 11.00,
        "Menu Burger (Frites+Boisson)": 8.50,
    }
}

# --- FONCTIONS DE GESTION ---
def ajouter_au_panier(nom, prix):
    if nom in st.session_state.panier:
        st.session_state.panier[nom]["qte"] += 1
    else:
        st.session_state.panier[nom] = {"prix": prix, "qte": 1}

def vider_panier():
    st.session_state.panier = {}

def encaisser_panier(total, mode_paiement, type_commande):
    if not st.session_state.panier:
        return False
    
    nouvelle_vente = {
        "Date": datetime.now().strftime("%Y-%m-%d"),
        "Heure": datetime.now().strftime("%H:%M:%S"),
        "Type": type_commande,
        "Articles": ", ".join([f"{v['qte']}x {k}" for k, v in st.session_state.panier.items()]),
        "Total": float(total),
        "Mode": mode_paiement
    }
    
    # Sauvegarde persistante dans le fichier CSV
    df_nouvelle = pd.DataFrame([nouvelle_vente])
    if os.path.exists(FICHIER_HISTORIQUE):
        df_nouvelle.to_csv(FICHIER_HISTORIQUE, mode='a', header=False, index=False)
    else:
        df_nouvelle.to_csv(FICHIER_HISTORIQUE, mode='w', header=True, index=False)
        
    st.session_state.panier = {}
    return True

# --- INTERFACE GRAPHIQUE SAFARI / IPAD ---
st.title("🥙 Caisse Tactile iPad - Snack Kebab")

# Bouton de sécurité pour réinitialiser le fichier des ventes si besoin
if st.sidebar.button("⚠️ Effacer l'historique complet"):
    if os.path.exists(FICHIER_HISTORIQUE):
        os.remove(FICHIER_HISTORIQUE)
        st.sidebar.success("Historique supprimé.")

# Disposition en deux colonnes
col_menu, col_ticket = st.columns([3, 2])

with col_menu:
    st.subheader("Menu (Sélection Tactile)")
    categories = list(MENU.keys())
    onglets = st.tabs(categories)
    
    for i, cat in enumerate(categories):
        with onglets[i]:
            # Gros boutons faciles à presser sur tablette
            sub_cols = st.columns(2)
            index_col = 0
            for produit, prix in MENU[cat].items():
                with sub_cols[index_col]:
                    if st.button(f"{produit}\n\n{prix:.2f} €", key=f"ipad_{produit}", use_container_width=True):
                        ajouter_au_panier(produit, prix)
                        st.rerun()
                index_col = (index_col + 1) % 2

with col_ticket:
    st.subheader("📋 Ticket en cours")
    
    total_commande = 0.0
    items_affichage = []
    
    for produit, details in st.session_state.panier.items():
        sous_total = details["prix"] * details["qte"]
        total_commande += sous_total
        items_affichage.append({
            "Article": produit,
            "Qté": details["qte"],
            "Prix": f"{sous_total:.2f} €"
        })
    
    if items_affichage:
        st.dataframe(pd.DataFrame(items_affichage), use_container_width=True, hide_index=True)
    else:
        st.info("Sélectionnez des articles à gauche.")
        
    st.markdown(f"## 💰 TOTAL : {total_commande:.2f} €")
    
    # Options de règlement sur l'iPad
    type_cmd = st.radio("Type de commande", ["Sur place", "À emporter"], horizontal=True)
    mode_paie = st.selectbox("Paiement", ["Espèces", "Carte Bancaire", "Sans Contact"])
    
    col_v, col_e = st.columns(2)
    with col_v:
        if st.button("❌ Annuler", use_container_width=True):
            vider_panier()
            st.rerun()
    with col_e:
        if st.button("💶 Valider", type="primary", use_container_width=True):
            if st.session_state.panier:
                if encaisser_panier(total_commande, mode_paie, type_cmd):
                    st.success("Vente enregistrée !")
                    st.rerun()
            else:
                st.error("Le panier est vide.")

# Affichage des statistiques de la journée en temps réel
st.markdown("---")
st.subheader("📊 Rapport des ventes (Sauvegardé en continu)")
if os.path.exists(FICHIER_HISTORIQUE):
    df_ventes = pd.read_csv(FICHIER_HISTORIQUE)
    st.dataframe(df_ventes, use_container_width=True, hide_index=True)
    st.metric(label="Chiffre d'affaires total", value=f"{df_ventes['Total'].sum():.2f} €")
else:
    st.info("Aucune vente enregistrée pour le moment.")
