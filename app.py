import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="FinManager: Intermediari Finanziari", layout="centered")

# --- CSS PERSONALIZZATO ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #f0f2f6;
    }
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- STATO DEL GIOCO ---
if 'turn' not in st.session_state:
    st.session_state.turn = 1
if 'capital' not in st.session_state:
    st.session_state.capital = 10000000
if 'reputation' not in st.session_state:
    st.session_state.reputation = 50
if 'history_capital' not in st.session_state:
    st.session_state.history_capital = [10000000]
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'message' not in st.session_state:
    st.session_state.message = "Benvenuto, CEO. La tua banca è operativa. Prendi decisioni sagge."

# --- DATABASE SCENARI ---
scenarios = {
    1: {
        "title": "Modulo A: Il Credito e il Rischio",
        "question": "Una Start-up tecnologica chiede un prestito di 2 Milioni € (Tasso 12%). Rating creditizio basso (C).",
        "theory": "Concetto: Rischio di Credito vs Rendimento atteso.",
        "choices": [
            {"text": "Accetta (Alto rischio, alto rendimento)", "cap_effect": 200000, "rep_effect": -5, "risk": "high", "feedback": "Hai accettato. Profitti alti, ma il rischio di portafoglio (VAR) è aumentato."},
            {"text": "Rifiuta e compra Titoli di Stato (2%)", "cap_effect": 40000, "rep_effect": 5, "risk": "low", "feedback": "Prudente. Rendimento basso ma sicuro (Risk-free)."},
            {"text": "Chiedi garanzie reali (Collateral)", "cap_effect": 100000, "rep_effect": 0, "risk": "med", "feedback": "Ottimo! Il collateral riduce la perdita in caso di default (LGD)."}
        ]
    },
    2: {
        "title": "Modulo B: Politica Monetaria",
        "question": "La BCE alza i tassi di interesse di 50 punti base per l'inflazione.",
        "theory": "Concetto: Rischio di Tasso d'Interesse e Repricing Gap.",
        "choices": [
            {"text": "Non fare nulla", "cap_effect": -300000, "rep_effect": 10, "risk": "high", "feedback": "Errore! Il costo della raccolta aumenta, i ricavi restano fissi. Margine giù."},
            {"text": "Alza i tassi sui prestiti", "cap_effect": 100000, "rep_effect": -15, "risk": "med", "feedback": "Hai protetto il margine, ma la domanda di prestiti scende."},
            {"text": "Acquista Swap di copertura (IRS)", "cap_effect": -50000, "rep_effect": 5, "risk": "low", "feedback": "Esperto! Costo immediato, ma bilancio immunizzato dal rischio tassi."}
        ]
    },
    3: {
        "title": "Modulo C: Regolamentazione",
        "question": "Stress test: crisi immobiliare. Devi rispettare i requisiti di capitale.",
        "theory": "Concetto: Basilea III e CET1 Ratio.",
        "choices": [
            {"text": "Aumento di capitale (nuove azioni)", "cap_effect": 500000, "rep_effect": -5, "risk": "low", "feedback": "Hai aumentato il Patrimonio di Vigilanza. Sei salvo."},
            {"text": "Svendi asset rischiosi", "cap_effect": -200000, "rep_effect": -10, "risk": "high", "feedback": "Hai ridotto gli RWA, ma hai realizzato una perdita per vendere in fretta."},
            {"text": "Ignora e spera", "cap_effect": -1000000, "rep_effect": -50, "risk": "fail", "feedback": "DISASTRO! La vigilanza ti ha sanzionato. Governance compromessa."}
        ]
    },
     4: {
        "title": "Esame Finale: Crisi Sistemica",
        "question": "Corsa agli sportelli (Bank Run)! I correntisti ritirano tutto.",
        "theory": "Concetto: Rischio di Liquidità.",
        "choices": [
            {"text": "Blocca i prelievi", "cap_effect": 0, "rep_effect": -100, "risk": "fail", "feedback": "Panico totale. Banca fallita per crisi reputazionale."},
            {"text": "Chiedi liquidità alla BCE", "cap_effect": -100000, "rep_effect": -10, "risk": "med", "feedback": "Corretto. Paghi la penalità, ma ottieni liquidità immediata."},
            {"text": "Vendi Titoli di Stato", "cap_effect": -50000, "rep_effect": 0, "risk": "med", "feedback": "Bene. Hai usato i 'Liquid Assets' (HQLA) per coprire le uscite."}
        ]
    }
}

# --- LOGICA TURNO ---
def next_turn(choice):
    st.session_state.capital += choice['cap_effect']
    st.session_state.reputation += choice['rep_effect']
    st.session_state.history_capital.append(st.session_state.capital)
    st.session_state.message = choice['feedback']
    
    if st.session_state.capital <= 0:
        st.session_state.game_over = True
        st.session_state.message = "BANCAROTTA! Capitale azzerato."
    elif st.session_state.reputation <= 0:
        st.session_state.game_over = True
        st.session_state.message = "GAME OVER! Crisi reputazionale."
    else:
        st.session_state.turn += 1

# --- INTERFACCIA ---
st.title("🏛 FinManager: University Edition")

col1, col2, col3 = st.columns(3)
col1.metric("Capitale", f"€ {st.session_state.capital:,.0f}")
col2.metric("Reputazione", f"{st.session_state.reputation}/100")
col3.metric("Turno", f"{st.session_state.turn}/4")

st.divider()

if not st.session_state.game_over and st.session_state.turn <= 4:
    scen = scenarios[st.session_state.turn]
    st.subheader(scen['title'])
    st.info(scen['theory'])
    st.write(f"**{scen['question']}**")
    
    if st.session_state.turn > 1:
        st.warning(f"Esito precedente: {st.session_state.message}")

    cols = st.columns(3)
    for idx, opt in enumerate(scen['choices']):
        if cols[idx].button(opt['text'], key=idx):
            next_turn(opt)
            st.rerun()

elif st.session_state.game_over:
    st.error(st.session_state.message)
    if st.button("Ricomincia"):
        st.session_state.clear()
        st.rerun()
else:
    st.success(f"Corso completato! Capitale finale: € {st.session_state.capital:,.0f}")
    st.line_chart(st.session_state.history_capital)
    if st.button("Nuova Partita"):
        st.session_state.clear()
        st.rerun()
