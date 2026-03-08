import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="FinManager: Intermediari Finanziari", layout="centered")

# --- CSS PERSONALIZZATO (Per renderlo più 'Game') ---
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

# --- STATO DEL GIOCO (SESSION STATE) ---
if 'turn' not in st.session_state:
    st.session_state.turn = 1
if 'capital' not in st.session_state:
    st.session_state.capital = 10000000  # 10 Milioni di Euro (Capitale iniziale)
if 'reputation' not in st.session_state:
    st.session_state.reputation = 50     # Reputazione (0-100)
if 'history_capital' not in st.session_state:
    st.session_state.history_capital = [10000000]
if 'game_over' not in st.session_state:
    st.session_state.game_over = False
if 'message' not in st.session_state:
    st.session_state.message = "Benvenuto, CEO. La tua banca è operativa. Prendi decisioni sagge basate sulla teoria del corso."

# --- DATABASE SCENARI (Logica Didattica) ---
scenarios = {
    1: {
        "title": "Modulo A: Il Credito e il Rischio",
        "question": "Una Start-up tecnologica chiede un prestito di 2 Milioni € con un tasso molto alto (12%). Il loro rating creditizio è basso (C).",
        "theory": "Concetto: Rischio di Credito vs Rendimento atteso (Credit Scoring).",
        "choices": [
            {"text": "Accetta il prestito (Alto rischio, alto rendimento)", "cap_effect": 200000, "rep_effect": -5, "risk": "high", "feedback": "Hai accettato. La startup ha pagato la prima rata, i profitti salgono, ma il tuo rischio di portafoglio (VAR) è aumentato."},
            {"text": "Rifiuta e investi in Titoli di Stato (2%)", "cap_effect": 40000, "rep_effect": 5, "risk": "low", "feedback": "Scelta prudente. Il rendimento è basso ma sicuro (Risk-free). La stabilità della banca è preservata."},
            {"text": "Chiedi garanzie reali (Collateral)", "cap_effect": 100000, "rep_effect": 0, "risk": "med", "feedback": "Ottima applicazione della teoria! Mitigare il rischio di credito tramite collateral riduce la perdita in caso di default (LGD)."}
        ]
    },
    2: {
        "title": "Modulo B: Politica Monetaria",
        "question": "La Banca Centrale Europea (BCE) ha inaspettatamente alzato i tassi di interesse di 50 punti base per combattere l'inflazione.",
        "theory": "Concetto: Rischio di Tasso d'Interesse e Repricing Gap.",
        "choices": [
            {"text": "Non fare nulla (Mantieni tassi attuali)", "cap_effect": -300000, "rep_effect": 10, "risk": "high", "feedback": "Errore! Il costo della tua raccolta aumenta (paghi di più sui depositi) ma i ricavi sui prestiti restano uguali. Il Margine di Interesse crolla."},
            {"text": "Alza subito i tassi sui prestiti alla clientela", "cap_effect": 100000, "rep_effect": -15, "risk": "med", "feedback": "Hai protetto il margine, ma i clienti sono scontenti e la domanda di prestiti scende. È un trade-off necessario."},
            {"text": "Acquista un Interest Rate Swap (IRS) di copertura", "cap_effect": -50000, "rep_effect": 5, "risk": "low", "feedback": "Mossa da esperto! Hai sostenuto un costo immediato per il derivato, ma hai immunizzato il bilancio dal rischio di rialzo tassi."}
        ]
    },
    3: {
        "title": "Modulo C: Regolamentazione (Basilea)",
        "question": "Uno 'stress test' simula una crisi immobiliare. Il valore dei tuoi asset a rischio aumenta. Devi rispettare i requisiti di capitale.",
        "theory": "Concetto: Coefficienti patrimoniali (CET1 Ratio) e Basilea III.",
        "choices": [
            {"text": "Emetti nuove azioni (Aumento di capitale)", "cap_effect": 500000, "rep_effect": -5, "risk": "low", "feedback": "Hai aumentato il Patrimonio di Vigilanza (Tier 1). Sei salvo, anche se gli azionisti sono diluiti."},
            {"text": "Vendi asset rischiosi in svendita (Fire sale)", "cap_effect": -200000, "rep_effect": -10, "risk": "high", "feedback": "Hai ridotto gli asset ponderati per il rischio (RWA), ma hai realizzato una perdita in conto capitale per vendere in fretta."},
            {"text": "Ignora e spera che la Banca d'Italia non se ne accorga", "cap_effect": -1000000, "rep_effect": -50, "risk": "fail", "feedback": "DISASTRO! La vigilanza ti ha sanzionato pesantemente. La governance della banca è compromessa."}
        ]
    },
     4: {
        "title": "Esame Finale: Crisi Sistemica",
        "question": "Corsa agli sportelli (Bank Run)! Voci infondate dicono che la banca è illiquida. I correntisti ritirano tutto.",
        "theory": "Concetto: Rischio di Liquidità e Prestatore di ultima istanza.",
        "choices": [
            {"text": "Blocca i prelievi", "cap_effect": 0, "rep_effect": -100, "risk": "fail", "feedback": "Hai scatenato il panico totale. La banca è fallita per crisi reputazionale."},
            {"text": "Chiedi liquidità alla BCE (Marginal Lending Facility)", "cap_effect": -100000, "rep_effect": -10, "risk": "med", "feedback": "Corretto. Paghi un tasso di penalizzazione alla BCE, ma ottieni la liquidità necessaria per rassicurare i mercati."},
            {"text": "Vendi i Titoli di Stato in portafoglio", "cap_effect": -50000, "rep_effect": 0, "risk": "med", "feedback": "Buona mossa. I titoli di stato sono 'Liquid Assets' (HQLA) pensati proprio per essere venduti rapidamente in caso di crisi."}
        ]
    }
}

# --- FUNZIONE PER GESTIRE IL TURNO ---
def next_turn(choice):
    # Calcolo casualità o modificatori
    result_cap = choice['cap_effect']
    result_rep = choice['rep_effect']
    
    # Aggiorna Stato
    st.session_state.capital += result_cap
    st.session_state.reputation += result_rep
    st.session_state.history_capital.append(st.session_state.capital)
    st.session_state.message = choice['feedback']
    
    # Check Game Over
    if st.session_state.capital <= 0:
        st.session_state.game_over = True
        st.session_state.message = "BANCAROTTA! La tua banca è insolvente. Il bail-in ha azzerato il capitale."
    elif st.session_state.reputation <= 0:
        st.session_state.game_over = True
        st.session_state.message = "GAME OVER! Nessuno si fida più della tua banca. I clienti sono fuggiti."
    else:
        st.session_state.turn += 1

# --- INTERFACCIA UTENTE ---

# Header
st.title("🏛 FinManager: The Intermediary")
st.markdown("**Corso di Economia degli Intermediari Finanziari**")

# Dashboard Metriche
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Capitale (Tier 1)", value=f"€ {st.session_state.capital:,.0f}")
with col2:
    st.metric(label="Reputazione", value=f"{st.session_state.reputation}/100", delta=st.session_state.reputation - 50)
with col3:
    st.metric(label="Turno / Modulo", value=f"{st.session_state.turn}/4")

st.divider()

# Area di Gioco
if not st.session_state.game_over and st.session_state.turn <= 4:
    current_scenario = scenarios[st.session_state.turn]
    
    st.subheader(f"Scenario {st.session_state.turn}: {current_scenario['title']}")
    st.info(current_scenario['theory'])
    
    st.markdown(f"### 📢 {current_scenario['question']}")
    
    # Visualizzazione Feedback turno precedente
    if st.session_state.turn > 1:
        with st.expander("Esito turno precedente", expanded=True):
            st.warning(st.session_state.message)

    # Pulsanti Scelte
    cols = st.columns(3)
    for idx, option in enumerate(current_scenario['choices']):
        with cols[idx]:
            if st.button(option['text'], key=f"btn_{st.session_state.turn}_{idx}"):
                next_turn(option)
                st.rerun()

elif st.session_state.game_over:
    st.error(st.session_state.message)
    st.markdown("### 📉 Andamento del Capitale")
    st.line_chart(st.session_state.history_capital)
    if st.button("Ricomincia Corso"):
        st.session_state.clear()
        st.rerun()

else:
    st.success("🎉 COMPLIMENTI! Hai completato l'anno fiscale.")
    st.markdown(f"Hai terminato con un capitale di **€ {st.session_state.capital:,.0f}** e una reputazione di **{st.session_state.reputation}**.")
    st.markdown("Hai dimostrato di saper gestire i rischi di credito, di mercato e di liquidità.")
    
    st.markdown("### 📈 Performance della tua Banca")
    # Grafico Matplotlib personalizzato
    fig, ax = plt.subplots()
    ax.plot(st.session_state.history_capital, marker='o', linestyle='-', color='b')
    ax.set_title("Evoluzione del Capitale")
    ax.set_ylabel("Euro")
    ax.set_xlabel("Turni")
    ax.grid(True)
    st.pyplot(fig)
    
    if st.button("Nuova Partita"):
        st.session_state.clear()
        st.rerun()

# Footer educativo
st.markdown("---")
st.caption("App didattica sviluppata per il corso di EIF. Le simulazioni sono semplificazioni a scopo educativo.")""", unsafe_allow_html=True)\
\
# --- STATO DEL GIOCO (SESSION STATE) ---\
if 'turn' not in st.session_state:\
    st.session_state.turn = 1\
if 'capital' not in st.session_state:\
    st.session_state.capital = 10000000  # 10 Milioni di Euro (Capitale iniziale)\
if 'reputation' not in st.session_state:\
    st.session_state.reputation = 50     # Reputazione (0-100)\
if 'history_capital' not in st.session_state:\
    st.session_state.history_capital = [10000000]\
if 'game_over' not in st.session_state:\
    st.session_state.game_over = False\
if 'message' not in st.session_state:\
    st.session_state.message = "Benvenuto, CEO. La tua banca \'e8 operativa. Prendi decisioni sagge basate sulla teoria del corso."\
\
# --- DATABASE SCENARI (Logica Didattica) ---\
scenarios = \{\
    1: \{\
        "title": "Modulo A: Il Credito e il Rischio",\
        "question": "Una Start-up tecnologica chiede un prestito di 2 Milioni \'80 con un tasso molto alto (12%). Il loro rating creditizio \'e8 basso (C).",\
        "theory": "Concetto: Rischio di Credito vs Rendimento atteso (Credit Scoring).",\
        "choices": [\
            \{"text": "Accetta il prestito (Alto rischio, alto rendimento)", "cap_effect": 200000, "rep_effect": -5, "risk": "high", "feedback": "Hai accettato. La startup ha pagato la prima rata, i profitti salgono, ma il tuo rischio di portafoglio (VAR) \'e8 aumentato."\},\
            \{"text": "Rifiuta e investi in Titoli di Stato (2%)", "cap_effect": 40000, "rep_effect": 5, "risk": "low", "feedback": "Scelta prudente. Il rendimento \'e8 basso ma sicuro (Risk-free). La stabilit\'e0 della banca \'e8 preservata."\},\
            \{"text": "Chiedi garanzie reali (Collateral)", "cap_effect": 100000, "rep_effect": 0, "risk": "med", "feedback": "Ottima applicazione della teoria! Mitigare il rischio di credito tramite collateral riduce la perdita in caso di default (LGD)."\}\
        ]\
    \},\
    2: \{\
        "title": "Modulo B: Politica Monetaria",\
        "question": "La Banca Centrale Europea (BCE) ha inaspettatamente alzato i tassi di interesse di 50 punti base per combattere l'inflazione.",\
        "theory": "Concetto: Rischio di Tasso d'Interesse e Repricing Gap.",\
        "choices": [\
            \{"text": "Non fare nulla (Mantieni tassi attuali)", "cap_effect": -300000, "rep_effect": 10, "risk": "high", "feedback": "Errore! Il costo della tua raccolta aumenta (paghi di pi\'f9 sui depositi) ma i ricavi sui prestiti restano uguali. Il Margine di Interesse crolla."\},\
            \{"text": "Alza subito i tassi sui prestiti alla clientela", "cap_effect": 100000, "rep_effect": -15, "risk": "med", "feedback": "Hai protetto il margine, ma i clienti sono scontenti e la domanda di prestiti scende. \'c8 un trade-off necessario."\},\
            \{"text": "Acquista un Interest Rate Swap (IRS) di copertura", "cap_effect": -50000, "rep_effect": 5, "risk": "low", "feedback": "Mossa da esperto! Hai sostenuto un costo immediato per il derivato, ma hai immunizzato il bilancio dal rischio di rialzo tassi."\}\
        ]\
    \},\
    3: \{\
        "title": "Modulo C: Regolamentazione (Basilea)",\
        "question": "Uno 'stress test' simula una crisi immobiliare. Il valore dei tuoi asset a rischio aumenta. Devi rispettare i requisiti di capitale.",\
        "theory": "Concetto: Coefficienti patrimoniali (CET1 Ratio) e Basilea III.",\
        "choices": [\
            \{"text": "Emetti nuove azioni (Aumento di capitale)", "cap_effect": 500000, "rep_effect": -5, "risk": "low", "feedback": "Hai aumentato il Patrimonio di Vigilanza (Tier 1). Sei salvo, anche se gli azionisti sono diluiti."\},\
            \{"text": "Vendi asset rischiosi in svendita (Fire sale)", "cap_effect": -200000, "rep_effect": -10, "risk": "high", "feedback": "Hai ridotto gli asset ponderati per il rischio (RWA), ma hai realizzato una perdita in conto capitale per vendere in fretta."\},\
            \{"text": "Ignora e spera che la Banca d'Italia non se ne accorga", "cap_effect": -1000000, "rep_effect": -50, "risk": "fail", "feedback": "DISASTRO! La vigilanza ti ha sanzionato pesantemente. La governance della banca \'e8 compromessa."\}\
        ]\
    \},\
     4: \{\
        "title": "Esame Finale: Crisi Sistemica",\
        "question": "Corsa agli sportelli (Bank Run)! Voci infondate dicono che la banca \'e8 illiquida. I correntisti ritirano tutto.",\
        "theory": "Concetto: Rischio di Liquidit\'e0 e Prestatore di ultima istanza.",\
        "choices": [\
            \{"text": "Blocca i prelievi", "cap_effect": 0, "rep_effect": -100, "risk": "fail", "feedback": "Hai scatenato il panico totale. La banca \'e8 fallita per crisi reputazionale."\},\
            \{"text": "Chiedi liquidit\'e0 alla BCE (Marginal Lending Facility)", "cap_effect": -100000, "rep_effect": -10, "risk": "med", "feedback": "Corretto. Paghi un tasso di penalizzazione alla BCE, ma ottieni la liquidit\'e0 necessaria per rassicurare i mercati."\},\
            \{"text": "Vendi i Titoli di Stato in portafoglio", "cap_effect": -50000, "rep_effect": 0, "risk": "med", "feedback": "Buona mossa. I titoli di stato sono 'Liquid Assets' (HQLA) pensati proprio per essere venduti rapidamente in caso di crisi."\}\
        ]\
    \}\
\}\
\
# --- FUNZIONE PER GESTIRE IL TURNO ---\
def next_turn(choice):\
    # Calcolo casualit\'e0 o modificatori\
    result_cap = choice['cap_effect']\
    result_rep = choice['rep_effect']\
    \
    # Aggiorna Stato\
    st.session_state.capital += result_cap\
    st.session_state.reputation += result_rep\
    st.session_state.history_capital.append(st.session_state.capital)\
    st.session_state.message = choice['feedback']\
    \
    # Check Game Over\
    if st.session_state.capital <= 0:\
        st.session_state.game_over = True\
        st.session_state.message = "BANCAROTTA! La tua banca \'e8 insolvente. Il bail-in ha azzerato il capitale."\
    elif st.session_state.reputation <= 0:\
        st.session_state.game_over = True\
        st.session_state.message = "GAME OVER! Nessuno si fida pi\'f9 della tua banca. I clienti sono fuggiti."\
    else:\
        st.session_state.turn += 1\
\
# --- INTERFACCIA UTENTE ---\
\
# Header\
st.title("\uc0\u55356 \u57307  FinManager: The Intermediary")\
st.markdown("**Corso di Economia degli Intermediari Finanziari**")\
\
# Dashboard Metriche\
col1, col2, col3 = st.columns(3)\
with col1:\
    st.metric(label="Capitale (Tier 1)", value=f"\'80 \{st.session_state.capital:,.0f\}")\
with col2:\
    st.metric(label="Reputazione", value=f"\{st.session_state.reputation\}/100", delta=st.session_state.reputation - 50)\
with col3:\
    st.metric(label="Turno / Modulo", value=f"\{st.session_state.turn\}/4")\
\
st.divider()\
\
# Area di Gioco\
if not st.session_state.game_over and st.session_state.turn <= 4:\
    current_scenario = scenarios[st.session_state.turn]\
    \
    st.subheader(f"Scenario \{st.session_state.turn\}: \{current_scenario['title']\}")\
    st.info(current_scenario['theory'])\
    \
    st.markdown(f"### \uc0\u55357 \u56546  \{current_scenario['question']\}")\
    \
    # Visualizzazione Feedback turno precedente\
    if st.session_state.turn > 1:\
        with st.expander("Esito turno precedente", expanded=True):\
            st.warning(st.session_state.message)\
\
    # Pulsanti Scelte\
    cols = st.columns(3)\
    for idx, option in enumerate(current_scenario['choices']):\
        with cols[idx]:\
            if st.button(option['text'], key=f"btn_\{st.session_state.turn\}_\{idx\}"):\
                next_turn(option)\
                st.rerun()\
\
elif st.session_state.game_over:\
    st.error(st.session_state.message)\
    st.markdown("### \uc0\u55357 \u56521  Andamento del Capitale")\
    st.line_chart(st.session_state.history_capital)\
    if st.button("Ricomincia Corso"):\
        st.session_state.clear()\
        st.rerun()\
\
else:\
    st.success("\uc0\u55356 \u57225  COMPLIMENTI! Hai completato l'anno fiscale.")\
    st.markdown(f"Hai terminato con un capitale di **\'80 \{st.session_state.capital:,.0f\}** e una reputazione di **\{st.session_state.reputation\}**.")\
    st.markdown("Hai dimostrato di saper gestire i rischi di credito, di mercato e di liquidit\'e0.")\
    \
    st.markdown("### \uc0\u55357 \u56520  Performance della tua Banca")\
    # Grafico Matplotlib personalizzato\
    fig, ax = plt.subplots()\
    ax.plot(st.session_state.history_capital, marker='o', linestyle='-', color='b')\
    ax.set_title("Evoluzione del Capitale")\
    ax.set_ylabel("Euro")\
    ax.set_xlabel("Turni")\
    ax.grid(True)\
    st.pyplot(fig)\
    \
    if st.button("Nuova Partita"):\
        st.session_state.clear()\
        st.rerun()\
\
# Footer educativo\
st.markdown("---")\
st.caption("App didattica sviluppata per il corso di EIF. Le simulazioni sono semplificazioni a scopo educativo.")}
