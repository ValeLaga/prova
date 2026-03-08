import streamlit as st
import json
import requests
from datetime import datetime
import random

st.set_page_config(page_title="FinQuest EIF", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

# ─── FIREBASE ─────────────────────────────────────────────────────────────────
FIREBASE_PROJECT_ID = "finquest-leaderboard"

def firebase_get_all(col):
    try:
        r = requests.get(f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/{col}", timeout=5)
        return r.json().get("documents", []) if r.status_code == 200 else []
    except: return []

def firebase_set(col, doc_id, data):
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/{col}/{doc_id}"
        fields = {}
        for k, v in data.items():
            if isinstance(v, int): fields[k] = {"integerValue": str(v)}
            elif isinstance(v, float): fields[k] = {"doubleValue": v}
            elif isinstance(v, list): fields[k] = {"stringValue": json.dumps(v)}
            else: fields[k] = {"stringValue": str(v)}
        requests.patch(url, json={"fields": fields}, timeout=5)
    except: pass

def parse_fb(doc):
    if not doc or "fields" not in doc: return None
    r = {}
    for k, v in doc["fields"].items():
        if "integerValue" in v: r[k] = int(v["integerValue"])
        elif "doubleValue" in v: r[k] = float(v["doubleValue"])
        elif "stringValue" in v:
            val = v["stringValue"]
            try: r[k] = json.loads(val)
            except: r[k] = val
    return r

def get_leaderboard():
    docs = firebase_get_all("studenti")
    entries = [e for e in [parse_fb(d) for d in docs] if e]
    return sorted(entries, key=lambda x: x.get("xp", 0), reverse=True)

def save_progress():
    if not st.session_state.get("registrato"): return
    lv, titolo = get_livello(st.session_state.xp)
    doc_id = st.session_state.nome.lower().replace(" ", "_").replace(".", "")[:50]
    firebase_set("studenti", doc_id, {
        "nome": st.session_state.nome, "xp": st.session_state.xp,
        "missioni": len(st.session_state.completate), "streak": st.session_state.streak,
        "badge": len(st.session_state.badge), "livello": lv, "titolo": titolo,
        "aggiornato": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=Outfit:wght@300;400;500;600;700;800&display=swap');

:root {
  --ink:    #0C0E14;
  --paper:  #F5F0E8;
  --cream:  #EDE8DC;
  --gold:   #C9A84C;
  --gold2:  #E8C876;
  --rust:   #C4522A;
  --teal:   #2A7B7C;
  --teal2:  #3AABA3;
  --slate:  #3D4A5C;
  --mist:   #8A94A6;
  --red:    #BF3B3B;
  --green:  #2E7D52;
  --blue:   #2C5F8A;
  --purple: #5C3D8A;
}

* { font-family: 'Outfit', sans-serif; box-sizing: border-box; }
html, body { background: var(--ink) !important; }
.stApp { background: var(--ink) !important; }
#MainMenu, footer, header { visibility: hidden; }

section[data-testid="stSidebar"] {
  background: #080A10 !important;
  border-right: 1px solid rgba(201,168,76,0.15) !important;
}
section[data-testid="stSidebar"] > div { background: transparent !important; }

/* Typography */
.serif { font-family: 'DM Serif Display', serif; }
.mono  { font-family: 'DM Mono', monospace; }

/* Masthead */
.masthead {
  background: linear-gradient(135deg, #0C0E14 0%, #111520 50%, #0C0E14 100%);
  border-bottom: 2px solid var(--gold);
  padding: 28px 40px 22px;
  margin: -20px -20px 32px;
  position: relative;
  overflow: hidden;
}
.masthead::before {
  content: '';
  position: absolute; inset: 0;
  background: repeating-linear-gradient(
    0deg, transparent, transparent 39px,
    rgba(201,168,76,0.04) 39px, rgba(201,168,76,0.04) 40px
  ), repeating-linear-gradient(
    90deg, transparent, transparent 39px,
    rgba(201,168,76,0.04) 39px, rgba(201,168,76,0.04) 40px
  );
  pointer-events: none;
}
.masthead-date {
  font-family: 'DM Mono', monospace;
  font-size: 0.65rem;
  color: var(--gold);
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 6px;
  opacity: 0.7;
}
.masthead-title {
  font-family: 'DM Serif Display', serif;
  font-size: 4.5rem;
  color: var(--paper);
  letter-spacing: -3px;
  line-height: 0.9;
  margin-bottom: 6px;
}
.masthead-rule {
  display: flex; align-items: center; gap: 14px; margin: 12px 0 8px;
}
.masthead-rule::before, .masthead-rule::after {
  content: ''; flex: 1; height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
}
.masthead-subtitle {
  font-family: 'DM Mono', monospace;
  font-size: 0.62rem; letter-spacing: 4px;
  color: var(--mist); text-transform: uppercase;
}

/* Cards */
.card {
  background: #10131C;
  border: 1px solid rgba(201,168,76,0.12);
  border-radius: 4px;
  transition: all 0.2s ease;
}
.card:hover { border-color: rgba(201,168,76,0.28); }
.card-gold { border-left: 3px solid var(--gold); }
.card-teal { border-left: 3px solid var(--teal2); }
.card-rust { border-left: 3px solid var(--rust); }
.card-blue { border-left: 3px solid var(--blue); }
.card-purple { border-left: 3px solid var(--purple); }
.card-green { border-left: 3px solid var(--green); }

/* Area pills */
.area-pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 3px 10px; border-radius: 2px;
  font-family: 'DM Mono', monospace;
  font-size: 0.6rem; letter-spacing: 2px; text-transform: uppercase;
}

/* XP Bar */
.xp-track { background: rgba(201,168,76,0.1); border-radius: 1px; height: 3px; }
.xp-fill  {
  height: 100%; border-radius: 1px;
  background: linear-gradient(90deg, var(--gold), var(--gold2));
  box-shadow: 0 0 8px rgba(201,168,76,0.5);
  transition: width 1s cubic-bezier(.4,0,.2,1);
}

/* Mission tiles */
.mission-tile {
  background: #10131C;
  border: 1px solid rgba(201,168,76,0.1);
  border-radius: 4px;
  padding: 20px 18px;
  min-height: 180px;
  position: relative;
  transition: all 0.2s;
}
.mission-tile:hover { border-color: rgba(201,168,76,0.25); transform: translateY(-2px); }
.mission-tile.boss { border-color: rgba(196,82,42,0.3); background: #130C08; }
.mission-tile.done { border-color: rgba(46,125,82,0.3); background: #081310; }
.mission-tile.locked { opacity: 0.35; }
.boss-glow { box-shadow: 0 0 20px rgba(196,82,42,0.15); }

/* Buttons */
.stButton > button {
  background: transparent !important;
  color: var(--mist) !important;
  border: 1px solid rgba(201,168,76,0.2) !important;
  border-radius: 2px !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 0.72rem !important;
  letter-spacing: 1.5px !important;
  text-transform: uppercase !important;
  padding: 10px 16px !important;
  width: 100% !important;
  transition: all 0.15s !important;
}
.stButton > button:hover {
  background: rgba(201,168,76,0.08) !important;
  color: var(--gold) !important;
  border-color: var(--gold) !important;
}

/* Feedback */
.fb-correct {
  background: #081310; border: 1px solid rgba(46,125,82,0.35);
  border-left: 3px solid var(--green);
  border-radius: 4px; padding: 22px;
}
.fb-wrong {
  background: #130C08; border: 1px solid rgba(196,82,42,0.35);
  border-left: 3px solid var(--rust);
  border-radius: 4px; padding: 22px;
}

/* Text */
h1,h2,h3 { color: var(--paper) !important; font-family: 'DM Serif Display', serif !important; }
p, div, span { color: var(--mist); }
label { color: var(--mist) !important; }
.stTextInput > div > div > input {
  background: #10131C !important; color: var(--paper) !important;
  border: 1px solid rgba(201,168,76,0.2) !important;
  border-radius: 2px !important; font-family: 'Outfit' !important;
}
.stTabs [data-baseweb="tab-list"] {
  background: #10131C; border-radius: 2px; padding: 3px;
  border: 1px solid rgba(201,168,76,0.1);
}
.stTabs [data-baseweb="tab"] { color: var(--mist) !important; border-radius: 2px !important; }
.stTabs [aria-selected="true"] { background: rgba(201,168,76,0.1) !important; color: var(--gold) !important; }
hr { border-color: rgba(201,168,76,0.1) !important; }

/* Decorative quote marks */
.deco-num {
  font-family: 'DM Serif Display', serif;
  font-size: 5rem; color: rgba(201,168,76,0.08);
  line-height: 1; position: absolute; top: -8px; right: 14px;
  pointer-events: none;
}

@keyframes boss-flicker {
  0%,100% { opacity: 1; }
  50% { opacity: 0.85; }
}
.boss-flicker { animation: boss-flicker 2s ease-in-out infinite; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-up { animation: fadeUp 0.4s ease forwards; }

/* Sidebar nav */
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border-radius: 2px; cursor: pointer;
  transition: all 0.15s; border: 1px solid transparent;
  margin-bottom: 4px; color: var(--mist) !important;
  font-family: 'DM Mono', monospace; font-size: 0.72rem;
  letter-spacing: 1.5px; text-transform: uppercase;
}
.nav-item:hover { background: rgba(201,168,76,0.06); border-color: rgba(201,168,76,0.15); color: var(--gold) !important; }
.nav-active { background: rgba(201,168,76,0.08) !important; border-color: rgba(201,168,76,0.25) !important; color: var(--gold) !important; }

/* Leaderboard row */
.lb-row {
  display: flex; align-items: center; gap: 16px;
  padding: 14px 18px;
  background: #10131C; border: 1px solid rgba(201,168,76,0.08);
  border-radius: 3px; margin-bottom: 6px;
  transition: border-color 0.15s;
}
.lb-row:hover { border-color: rgba(201,168,76,0.2); }
.lb-row.me { border-color: rgba(201,168,76,0.4); background: #141008; }

/* Quiz option */
.q-option {
  background: #10131C; border: 1px solid rgba(201,168,76,0.12);
  border-radius: 3px; padding: 14px 18px;
  color: var(--mist) !important; font-size: 0.88rem;
  cursor: pointer; transition: all 0.15s;
  margin-bottom: 8px; line-height: 1.6;
}
.q-option:hover { border-color: var(--gold); color: var(--paper) !important; background: rgba(201,168,76,0.04); }
</style>
""", unsafe_allow_html=True)

# ─── MISSIONS DATABASE ────────────────────────────────────────────────────────
MISSIONS = {

  "sistema": {
    "nome": "Sistema Finanziario", "emoji": "◈",
    "colore": "gold", "accent": "#C9A84C",
    "xp_totale": 600,
    "desc": "Funzioni, saldi, strumenti, teorie dell'intermediazione",
    "livelli": [
      {
        "id": "S1", "titolo": "Fondamenti del Sistema Finanziario",
        "desc": "Ruolo, circuiti, saldi finanziari, aggregati monetari M1-M3",
        "xp": 60,
        "domande": [
          {
            "testo": "Il sistema finanziario svolge tre funzioni fondamentali. La funzione di 'regolamento degli scambi' si realizza attraverso:",
            "opzioni": ["A) L'emissione di titoli di Stato per finanziare la spesa pubblica",
                        "B) L'offerta di strumenti di pagamento (moneta, bonifici, carte) che consentono di regolare transazioni tra operatori economici eliminando il baratto",
                        "C) La supervisione bancaria esercitata dalla Banca d'Italia",
                        "D) La quotazione delle società in borsa che regola il prezzo del capitale"],
            "corretta": 1,
            "spiegazione": "Le TRE funzioni del sistema finanziario sono: (1) Trasferimento delle risorse — da unità in surplus a unità in deficit, nello spazio (tra settori) e nel tempo (intertemporal). (2) Regolamento degli scambi — strumenti di pagamento che sostituiscono il baratto: moneta legale, depositi in c/c, carte di debito/credito, bonifici SEPA, sistema TARGET2 per pagamenti interbancari. (3) Gestione dei rischi — strumenti assicurativi e derivati che consentono di trasferire e diversificare i rischi. In Italia il sistema dei pagamenti processa ogni anno ~€2.000 miliardi di transazioni. Il TIPS (TARGET Instant Payment Settlement) gestisce i pagamenti istantanei 24/7 tra le banche europee."
          },
          {
            "testo": "Il 'circuito diretto' vs il 'circuito indiretto' di intermediazione finanziaria differiscono perché:",
            "opzioni": ["A) Nel circuito diretto non ci sono costi di transazione, nel circuito indiretto sì",
                        "B) Nel circuito diretto gli investitori acquistano strumenti emessi direttamente dagli emittenti (mercati); nel circuito indiretto un intermediario si INTERPONE — raccoglie fondi da chi ha surplus ed eroga credito a chi ha deficit, trasformando rischio, scadenza e importo",
                        "C) Il circuito diretto funziona solo per le imprese, il circuito indiretto solo per le famiglie",
                        "D) Il circuito diretto è regolato dalla BCE, il circuito indiretto dalla CONSOB"],
            "corretta": 1,
            "spiegazione": "CIRCUITO DIRETTO (mercati): l'impresa emette azioni o obbligazioni → gli investitori le acquistano → l'intermediario (banca/SIM) può svolgere solo una funzione di 'advisor' o 'underwriter' senza interporre il bilancio. Vantaggi: trasparenza dei prezzi, accesso diretto al risparmio, diversificazione per gli investitori. Limiti: richiede standardizzazione, informazioni pubbliche, investitori sofisticati. CIRCUITO INDIRETTO (intermediato): la banca raccoglie depositi dalle famiglie e concede prestiti alle imprese. Trasforma: scadenze (depositi a breve → prestiti a lungo), importi (piccoli depositi → grandi prestiti), rischio (assume e diversifica il rischio di credito). Questa funzione di 'qualitative asset transformation' giustifica l'esistenza delle banche secondo Diamond (1984). Il sistema italiano è storicamente bank-based: le banche finanziano ~65-70% del credito alle imprese non finanziarie."
          },
          {
            "testo": "SF = S − ΔAR = ΔAF − ΔPF. Se le Famiglie hanno S = €80 mld e ΔAR = €30 mld, le Società non finanziarie hanno S = €40 mld e ΔAR = €70 mld, la Pubblica Amministrazione ha deficit/PIL = 3% con PIL = €2.000 mld, qual è il saldo del settore estero (segno opposto alla posizione netta dell'Italia con l'estero)?",
            "opzioni": ["A) Il settore estero ha saldo zero — la somma dei saldi settoriali è sempre zero",
                        "B) SF Famiglie = +€50 mld; SF SNF = −€30 mld; SF PA = −€60 mld; SF Estero = +€40 mld (l'Italia prende in prestito €40 mld dall'estero, il saldo CA italiano è −€40 mld)",
                        "C) Il settore estero non ha saldo finanziario — è un concetto applicabile solo ai settori residenti",
                        "D) Il settore estero ha sempre saldo positivo perché l'Italia ha surplus commerciale"],
            "corretta": 1,
            "spiegazione": "Calcolo: SF Famiglie = 80 − 30 = +€50 mld (surplus strutturale). SF SNF = 40 − 70 = −€30 mld (deficit strutturale: investono più di quanto risparmiano). SF PA = −3% × 2.000 = −€60 mld (deficit pubblico). Somma dei saldi interni = +50 − 30 − 60 = −€40 mld. Per identità contabile, la somma di TUTTI i saldi settoriali (incluso estero) = 0: SF Estero = +€40 mld. Questo significa che l'Italia si finanzia dall'estero per €40 mld (saldo delle partite correnti = −€40 mld): importa più capitali di quanti ne esporta. LA BILANCIA DEI PAGAMENTI: saldo CC + saldo finanziario = 0. Deficit CC → la nazione accumula debiti verso l'estero (NIIP negativa). L'Italia ha avuto NIIP peggiore del −25% del PIL prima della crisi del debito 2011-12; poi è migliorata grazie ai surplus di CA dal 2013."
          },
          {
            "testo": "Gli aggregati monetari M1, M2, M3 della BCE. Un fondo comune monetario (FCM) che investe in BOT e commercial paper è incluso in:",
            "opzioni": ["A) M1 — è un deposito a vista perché le quote sono rimborsabili immediatamente",
                        "B) M3 — i FCM sono liquidità M3 per la loro alta liquidità e sostitutività con i depositi, ma non sono inclusi in M1 né M2",
                        "C) Non è incluso in nessun aggregato monetario — è un prodotto di risparmio, non moneta",
                        "D) M2 — per via della scadenza media inferiore a 2 anni dei titoli in portafoglio"],
            "corretta": 1,
            "spiegazione": "CLASSIFICAZIONE AGGREGATI: M1 = Circolante + Depositi a vista (liquidità immediata, usati come mezzo di pagamento). M2 = M1 + Depositi fino a 2 anni + Depositi con preavviso ≤3 mesi (liquidità differita ma alta). M3 = M2 + Pronti Contro Termine + Obbligazioni bancarie ≤2 anni + Quote Fondi Monetari (sostituti quasi-monetari). I FCM (Fondi Comuni Monetari) rientrano in M3 perché: (1) le quote sono liquidabili con brevissimo preavviso, (2) il valore è stabile (NAV ~ €1), (3) sono percepiti dagli investitori come quasi-equivalenti ai depositi. POLITICA MONETARIA BCE: target operativo = tasso di interesse sui depositi overnight (DFR). M3 è un 'indicatore' non un target — l'esperienza degli anni 2000-2010 ha mostrato che la velocità della moneta (V nella MV=PY) è troppo instabile per usare M3 come target operativo."
          }
        ]
      },
      {
        "id": "S2", "titolo": "Teorie dell'Intermediazione",
        "desc": "Costi di transazione, asimmetrie info, Akerlof, Diamond, adverse selection",
        "xp": 100,
        "domande": [
          {
            "testo": "Il modello di Diamond (1984) 'Financial Intermediation and Delegated Monitoring' dimostra che le banche esistono come 'delegated monitors'. Qual è l'intuizione centrale?",
            "opzioni": ["A) Le banche esistono perché i mercati non riescono a prezzare correttamente il rischio di credito",
                        "B) Invece di avere N risparmiatori che monitorano ciascuno il proprio debitore (costo N×m), è più efficiente delegare il monitoraggio a un intermediario (costo m) che diversifica il proprio rischio di fallimento su molti debitori — economie di scala nel monitoraggio",
                        "C) Le banche esistono perché lo Stato impone l'intermediazione obbligatoria per ragioni fiscali",
                        "D) Le banche riducono il rischio di mercato aggregando strumenti diversi in portafogli diversificati"],
            "corretta": 1,
            "spiegazione": "Diamond (1984) — il modello fondativo della teoria bancaria moderna: Con N imprenditori e M risparmiatori: se ogni risparmiatore monitora ogni imprenditore → costo totale = N×M×m (enorme). Se i risparmiatori delegano a un intermediario (banca): banca monitora gli N imprenditori, costo = N×m. Il risparmio è (N×M×m − N×m) = N×m×(M−1). MA: la banca deve essere incentivata a monitorare onestamente. Diamond risolve con la diversificazione: se la banca presta a molti debitori indipendenti, la sua distribuzione delle perdite converge alla media (LGN) → pagherà quasi sempre i depositanti → il contratto di debito è ottimale. La banca si 'automonitorizza' attraverso la minaccia del fallimento. IMPLICAZIONE NORMATIVA: la diversificazione bancaria non è solo prudenziale, è condizione necessaria per l'esistenza stessa delle banche come delegated monitors. Concentrazione = rischio di fallimento della funzione informativa."
          },
          {
            "testo": "Lo 'hold-up problem' nel relationship banking si verifica quando:",
            "opzioni": ["A) Il cliente non vuole rivelare informazioni riservate all'analista del credito",
                        "B) La banca, avendo accumulato informazioni private sul cliente nel corso del rapporto, acquista potere monopolistico e può estrarre rendite rifinanziando a condizioni peggiori — il cliente è 'prigioniero' perché cambiare banca significa perdere il valore informatico accumulato",
                        "C) Il debitore blocca i fondi ricevuti su un conto vincolato invece di investirli",
                        "D) La banca rifiuta di concedere credito in attesa che il cliente fornisca più garanzie collaterali"],
            "corretta": 1,
            "spiegazione": "L'HOLD-UP PROBLEM è la principale critica al relationship banking: la banca costruisce soft information esclusiva (reputazione, flussi di cassa reali, prospettive del settore). Questa informazione è privata e non trasferibile a un'altra banca → il cliente diventa informativamente 'locked-in'. La banca sfrutterà questa posizione nelle rinegoziazioni: al rinnovo del prestito può imporre condizioni peggiori sapendo che il cliente non può facilmente andare altrove. EVIDENZE EMPIRICHE: le PMI italiane con banca unica (monobanca) pagano spread 20-50bps più alti delle PMI con più banche concorrenti per lo stesso merito creditizio. SOLUZIONE: multibanking (avere più banche) riduce l'hold-up ma aumenta il free-riding nel monitoraggio (nessuna banca vuole investire in informazioni che beneficerebbero anche le altre). Bilanciamento ottimale: 'main bank' + 1-2 banche secondarie (il modello Hausbank tedesco)."
          },
          {
            "testo": "La teoria della 'segnalazione' (Spence, 1973) applicata al credito: perché un debitore di qualità alta potrebbe preferire offrire una garanzia collaterale piuttosto che accettare un tasso di interesse più basso senza garanzia?",
            "opzioni": ["A) Perché la garanzia riduce il tasso di interesse e il debitore risparmia sugli interessi",
                        "B) Perché il collaterale è un segnale credibile della qualità del debitore: solo i debitori di qualità alta (con bassa probabilità di default) trovano conveniente impegnare collaterale — per i debitori rischiosi il costo atteso della perdita del collaterale (PD alta × valore garanzia) supera il beneficio del tasso più basso",
                        "C) Perché la normativa bancaria impone garanzie collaterali per tutti i prestiti superiori a €50.000",
                        "D) Perché il collaterale elimina completamente il rischio di credito — è una forma di assicurazione totale"],
            "corretta": 1,
            "spiegazione": "SEGNALAZIONE (Spence) nel credito: il collaterale risolve l'adverse selection come segnale auto-selettivo. Consideriamo due tipi di debitori: Debitore 'buono' (PD=2%): probabilità di perdere il collaterale = 2% → costo atteso = 2% × valore garanzia (basso). Debitore 'cattivo' (PD=20%): probabilità di perdere il collaterale = 20% → costo atteso = 20% × valore garanzia (alto). Il debitore buono preferisce offrire collaterale per ottenere il tasso migliore (costo basso della garanzia + tasso basso). Il debitore cattivo non trova conveniente il menu 'collaterale + tasso basso' (costo alto della garanzia). EQUILIBRIO SEPARANTE: la banca offre due contratti — (1) tasso alto, no collaterale per i cattivi; (2) tasso basso, collaterale per i buoni. I tipi si auto-selezionano. Limite: per funzionare il collaterale deve essere costoso per i debitori rischiosi e quasi gratuito per i buoni → richiede garanzie reali (immobili) non personali."
          }
        ]
      },
      {
        "id": "S3", "titolo": "◈ BOSS — Strumenti Finanziari & Pricing",
        "desc": "⚔ Equity, debt, derivati, IFRS9, rating, duration, convexity",
        "xp": 180, "boss": True,
        "domande": [
          {
            "testo": "La 'duration modificata' di un BTP decennale cedola 4%, yield 5%, è circa 7.8 anni. Se i tassi salgono di 50bps, la variazione percentuale del prezzo è approssimativamente:",
            "opzioni": ["A) −3.9% → ΔP/P ≈ −DM × Δy = −7.8 × 0.005",
                        "B) −3.9% — calcolato come Duration × Δy = 7.8 × 0.5 = 3.9%",
                        "C) +3.9% — i prezzi salgono quando i tassi aumentano",
                        "D) −7.8% — la duration stessa misura la variazione percentuale del prezzo"],
            "corretta": 0,
            "spiegazione": "Duration Modificata: DM = Duration Macaulay / (1+y). Approssimazione lineare: ΔP/P ≈ −DM × Δy = −7.8 × 0.005 = −0.039 = −3.9%. ATTENZIONE: l'approssimazione è lineare — sopravvaluta la perdita perché ignora la CONVESSITÀ. La variazione reale è: ΔP/P ≈ −DM×Δy + ½×Convexity×Δy². La convexity positiva significa che il prezzo scende MENO di quanto previsto dalla duration per rialzi di tasso e sale PIÙ per ribassi. ESEMPIO PRATICO: BTP 10Y con DM=7.8: se i tassi salgono di 100bps, stima lineare = −7.8%, stima con convexity ≈ −7.4% (la convexity 'ammortizza' la perdita). Perché importa: le banche con portafogli di titoli classificati FVOCI o FVTPL vedono impatto diretto sul patrimonio/CE per variazioni di tasso — il rischio IRRBB (Interest Rate Risk Banking Book) è monitorato dalla BCE nel processo SREP. La crisi di SVB (2023) è stata causata proprio dall'ignorare la duration risk su portafogli HtM."
          },
          {
            "testo": "Un'obbligazione 'convertibile' (convertible bond) è classificata da IAS 32 come strumento finanziario composto. Perché impatta diversamente il bilancio rispetto a un'obbligazione straight?",
            "opzioni": ["A) Perché è più rischiosa e richiede maggiori accantonamenti ECL",
                        "B) IAS 32 richiede la separazione della componente debito (VA dei flussi certi, iscritto al passivo) e della componente equity (opzione di conversione, iscritta nel patrimonio netto) — il trattamento 'split accounting' riduce il valore contabile del debito e aumenta il patrimonio netto",
                        "C) Perché le obbligazioni convertibili sono sempre classificate FVTPL secondo IFRS 9",
                        "D) Non impatta diversamente — le convertibili sono trattate come normali obbligazioni fino alla conversione effettiva"],
            "corretta": 1,
            "spiegazione": "IAS 32 SPLIT ACCOUNTING per gli strumenti composti: identificazione delle componenti — la convertible ha una componente debito (i flussi fissi di cedola e rimborso) e una componente equity (il diritto di convertire in azioni = opzione call sull'equity emittente). Valorizzazione: Valore componente debito = VA dei flussi futuri attualizzati al tasso di mercato per un bond non convertibile equivalente. Valore componente equity = Totale emissione − Valore debito (residuo). ESEMPIO: emissione convertibile €100M, cedola 2%, mercato 5%, maturità 5 anni → VA debito = ~87M → equity component = 13M. Implicazione: l'emittente iscrive €87M a passivo (debito) e €13M a patrimonio netto. Gli interessi sono calcolati sull'87M al tasso effettivo 5%, non al 2% nominale → costo finanziario effettivo più alto di quanto appare dal coupon. Questo incentiva le imprese a usare le convertibili: basso coupon in cambio di diluzione potenziale futura — tipico delle startup growth (Tesla 2020 aveva convertibili a 0% cedola)."
          },
          {
            "testo": "I Credit Default Swap (CDS) sull'Italia a 5 anni quotano 150bps. Cosa significa e come si usano per misurare il rischio?",
            "opzioni": ["A) Il tasso di rendimento dei BTP italiani a 5 anni è 1.50% sopra l'Euribor",
                        "B) Il protection buyer paga 150bps annui per essere risarcito in caso di credit event (default/ristrutturazione) sull'Italia — il CDS spread è il 'prezzo del rischio' di default percepito dal mercato",
                        "C) I CDS a 150bps indicano che l'Italia ha una probabilità di default del 15% nei prossimi 5 anni",
                        "D) Le agenzie di rating hanno assegnato un rating equivalente a 150bps di spread creditizio"],
            "corretta": 1,
            "spiegazione": "CDS (Credit Default Swap) — struttura: il protection buyer paga il CDS spread (150bps = 1.5%/anno) sul nozionale al protection seller. In caso di credit event (default, ristrutturazione, moratoria), il seller paga la perdita al buyer (par − recovery). Relazione con PD implicita: CDS spread ≈ PD × LGD. Ipotizzando LGD = 40%: PD implicita = 150bps / 40% = 3.75%/anno. PD cumulata 5 anni ≈ 1 − (1−3.75%)^5 ≈ 17.4%. STORIA: spread CDS Italia ha toccato 550bps nel novembre 2011 (crisi Berlusconi/spread BTP) → PD implicita ~14%/anno. Dopo Draghi 'whatever it takes' → crollo a <100bps. USO: (1) Copertura del rischio sovrano per le banche con grandi portafogli BTP; (2) Speculazione direzionale sul rischio paese; (3) Regolamentazione — i CDS sono diventati famigerati con i naked CDS su debito sovrano greco (vietati nell'UE dal 2012 per i naked positions)."
          }
        ]
      }
    ]
  },

  "banche": {
    "nome": "Banche & Bilancio", "emoji": "▣",
    "colore": "blue", "accent": "#2C5F8A",
    "xp_totale": 650,
    "desc": "Raccolta, impieghi, bilancio IAS/IFRS, equilibri gestionali, NPL",
    "livelli": [
      {
        "id": "B1", "titolo": "Raccolta Bancaria e Passivo",
        "desc": "Depositi, PCT, obbligazioni, MREL, raccolta wholesale vs retail",
        "xp": 80,
        "domande": [
          {
            "testo": "Il MREL (Minimum Requirement for own funds and Eligible Liabilities) è il requisito minimo di passività bail-inable introdotto dalla BRRD. Una banca con Total Assets €100 mld e RWA €60 mld deve mantenere MREL = 8% del TREA (Total Risk Exposure Amount). Quante passività eligible deve avere?",
            "opzioni": ["A) €8 mld — 8% degli attivi totali di €100 mld",
                        "B) €4.8 mld — 8% degli RWA di €60 mld",
                        "C) €8 mld include: CET1 + AT1 + T2 + Senior Non-Preferred eligible; il MREL si calcola su TREA che in questo caso è RWA = €60 mld → MREL = 8% × 60 = €4.8 mld ma in pratica il requisito è spesso più alto includendo buffer",
                        "D) Il MREL non si applica alle banche non-G-SIB"],
            "corretta": 2,
            "spiegazione": "MREL (Bank Recovery and Resolution Directive): obiettivo è garantire che la banca abbia abbastanza passività subordinate da poter assorbire perdite e ricapitalizzarsi senza fondi pubblici in caso di risoluzione. CALCOLO: MREL = % × TREA (Total Risk Exposure Amount = RWA + requisiti operativi). La struttura del passivo bail-inable (dall'alto verso il basso nella gerarchia delle perdite): CET1 capitale ordinario → AT1 (Tier 1 aggiuntivo, es. CoCo bonds) → T2 (subordinate classiche) → Senior Non-Preferred (SNP — strumento introdotto dal 2019, senior ma subordinato alle preferred) → Senior Preferred (obbligazioni ordinarie) → Depositi >100K grandi imprese. TLAC vs MREL: TLAC (Total Loss Absorbing Capacity) è il requisito FSB per le G-SIB globali (UniCredit, BNP, Deutsche) → più stringente (~18-20% RWA). MREL è il framework europeo per tutte le banche soggette a risoluzione. La distinzione Senior Preferred / Non-Preferred è italiana dal D.Lgs. 23/2018 che ha creato la nuova categoria SNP."
          },
          {
            "testo": "Un'operazione di TLTRO III (Targeted Longer-Term Refinancing Operation) ha concesso alla banca fondi a tasso negativo (−0.5% nella fase incentivata 2020-21) condizionati alla crescita dei prestiti. Quale effetto ha sul NIM bancario e perché la BCE l'ha strutturata così?",
            "opzioni": ["A) Il TLTRO aumenta il NIM perché la banca riceve fondi a tasso negativo e li presta a tassi positivi — pura carry trade",
                        "B) Il TLTRO comprime il NIM: il beneficio del tasso negativo sulla raccolta riduce il costo del funding, ma la BCE ha strutturato il meccanismo condizionato per evitare che la banca usasse i fondi per carry trade sui BTP invece di prestarli a famiglie e imprese",
                        "C) Il TLTRO non impatta il NIM — è un'operazione fuori bilancio della banca centrale",
                        "D) Il TLTRO aumenta i requisiti patrimoniali perché i fondi BCE hanno peso del rischio del 100%"],
            "corretta": 1,
            "spiegazione": "TLTRO III (2019-2021-2024): operazioni di rifinanziamento a lungo termine (4 anni) con tasso agevolato (fino a −1% nella fase COVID-incentivata per le banche che aumentavano i prestiti). MECCANISMO INCENTIVO: tasso base = DFR (−0.5%). Se la banca aumenta i prestiti netti sopra una soglia → tasso scende ulteriormente. Se non raggiunge target → tasso sale al DFR. EFFETTI CONTABILI: i TLTRO a tasso negativo generano un 'TLTRO benefit' — la BCE paga la banca per prendere in prestito. IFRS: questo beneficio è rilevato come commissione differita (a CE) lungo la vita del TLTRO. Problema 2022-2023: quando il DFR è salito sopra zero, il TLTRO è diventato costoso rispetto al mercato → le banche lo hanno rimborsato anticipatamente (prevista clausola di rimborso) per €477 miliardi nel febbraio 2023. Questo ha drenato liquidità dal sistema e amplificato la trasmissione monetaria restrittiva BCE."
          },
          {
            "testo": "Il 'core tier 1 deposit franchise' è considerato la fonte di raccolta più pregiata per una banca retail. Perché i depositi a vista retail hanno un 'beta' di deposito basso anche con tassi BCE al 4%?",
            "opzioni": ["A) Perché la normativa limita il tasso massimo sui depositi al 2%",
                        "B) Perché i depositi retail mostrano alta 'stickiness' — i clienti non cambiano banca per differenziali di tasso ridotti (costi di switching, inerzia comportamentale, relazioni di fiducia) → la banca può mantenere bassi tassi sui depositi anche con tassi di mercato alti, intascando lo spread",
                        "C) Perché il FITD garantisce i depositi fino a €100K eliminando il rischio di bank run",
                        "D) Perché i depositi a vista non producono interessi per definizione contrattuale"],
            "corretta": 1,
            "spiegazione": "DEPOSIT BETA = variazione del tasso sui depositi / variazione del tasso di policy BCE. Beta basso (es. 0.2): se BCE alza di 100bps, i depositi retail aumentano solo di 20bps. Beta alto (es. 0.8): tipico dei depositi corporate large-cap che hanno accesso diretto ai mercati monetari. STICKINESS DEI DEPOSITI RETAIL: (1) Switching costs elevati — cambio domiciliazione stipendio, addebiti automatici (utility, rata mutuo) → costo reale e psicologico del cambio. (2) Inerzia comportamentale (status quo bias — Thaler). (3) Relazione di lungo periodo e fiducia — difficile monetizzare in uno spread marginale. (4) Limiti cognitivi — molti clienti non confrontano attivamente i rendimenti. IMPLICAZIONE: nel 2022-2023 le banche italiane hanno alzato i tassi retail molto meno del tasso BCE → la franchising value dei depositi (il valore del deposit franchise) si è ampliata enormemente. Intesa stima il valore del proprio deposit franchise in decine di miliardi di euro nel calcolo del fair value del portafoglio bancario."
          }
        ]
      },
      {
        "id": "B2", "titolo": "Credito: Processo, NPL e Pricing",
        "desc": "Istruttoria, PD/LGD/EAD, forbearance, NPL lifecycle, covenant, Centrale Rischi",
        "xp": 120,
        "domande": [
          {
            "testo": "Un'impresa ottiene un finanziamento con covenant 'Debt/EBITDA ≤ 3.5×'. Al momento della concessione EBITDA = €10M, debito totale = €30M (ratio 3.0×). L'anno successivo l'EBITDA scende a €8M (debito invariato). Quali conseguenze scattano?",
            "opzioni": ["A) Il prestito viene automaticamente riclassificato a sofferenza e segnalato in Centrale dei Rischi",
                        "B) Il covenant è violato (30/8 = 3.75× > 3.5×): la banca può dichiarare 'event of default' e accelerare il rimborso, oppure concedere un 'waiver' (rinuncia temporanea) rinegoziando le condizioni — tipicamente spread più alto, nuove garanzie, piano di riduzione del debito",
                        "C) La banca deve immediatamente accantonare il 100% del prestito come perdita attesa",
                        "D) Il covenant vincola solo la distribuzione dei dividendi, non il rimborso del prestito"],
            "corretta": 1,
            "spiegazione": "COVENANT BREACH: Debt/EBITDA = 30/8 = 3.75× > threshold 3.5× → violazione tecnica. CONSEGUENZE TIPICHE nei contratti di credito: (1) Notification: l'impresa deve notificare immediatamente la banca. (2) Cross-default: se il covenant è in più linee di credito, la violazione in uno può triggerare il default anche negli altri. (3) Options della banca: a) Waiver — rinuncia formale per un periodo definito: la banca accetta la violazione in cambio di spread aumentato (+50-150bps tipicamente), nuove garanzie, piano di riduzione del debito entro 12-18 mesi; b) Acceleration — rimborso immediato del prestito; c) Rinegoziazione strutturale — modifica definitiva del covenant o del piano di ammortamento. IL WAIVER NON È FORBEARANCE automaticamente (secondo EBA): solo se l'impresa è in difficoltà finanziaria e il waiver è una concessione che non avverrebbe in condizioni normali → si applica la classificazione forbearance con tutte le implicazioni IFRS 9."
          },
          {
            "testo": "La 'Centrale dei Rischi' (CR) della Banca d'Italia è un sistema informativo cruciale per la valutazione del merito creditizio. Una PMI con segnalazioni 'a incaglio' in CR: quali conseguenze ha per l'accesso al credito?",
            "opzioni": ["A) Nessuna conseguenza — le informazioni in CR sono confidenziali e non accessibili alle banche",
                        "B) Le banche (tutte le banche segnalanti) possono consultare la CR e vedere la storia creditizia della PMI: segnalazioni di incaglio/sofferenza portano tipicamente a rifiuto automatico del credito o condizioni molto peggiorate, anche se la banca consultante non ha rapporti diretti con quella PMI",
                        "C) Solo la banca che ha segnalato l'incaglio può consultare le informazioni — le altre banche non hanno accesso",
                        "D) Le segnalazioni negative in CR vengono cancellate dopo 6 mesi se il debitore regolarizza la posizione"],
            "corretta": 1,
            "spiegazione": "CENTRALE DEI RISCHI (CR) Banca d'Italia — sistema di centralizzazione delle informazioni sui rischi di credito: obbligatoria per tutte le banche e intermediari ex art. 106 TUB per esposizioni ≥ €30.000. Dati segnalati: importi utilizzati, accordati, garanzie, classificazione (in bonis / scaduto / inadempienza probabile / sofferenza). ACCESSO: ogni intermediario segnalante può consultare la posizione globale di un soggetto → visione aggregata di tutti i debiti nel sistema. EFFETTI NEGATIVI: una segnalazione a 'sofferenza' presso anche solo una banca → tutte le banche vedono il rischio → effetto moltiplicativo sul razionamento del credito. TIMING: le segnalazioni rimangono visibili anche dopo la regolarizzazione (segnale negativo residuo). GARANZIE: il debitore ha diritto di consultare la propria posizione CR e può contestare errori. ATTENZIONE: la CR è diversa dai 'SIC' (Sistemi di Informazione Creditizia privati come CRIF) che operano su soglie più basse (anche piccoli prestiti personali)."
          },
          {
            "testo": "IFRS 9 — modello ECL a 3 stage. Una PMI finanziaria classificata in Stage 1 viene messa in Stage 2 per 'significativo aumento del rischio di credito'. Quali sono le conseguenze contabili immediate?",
            "opzioni": ["A) Il credito viene svalutato al 50% e classificato come sofferenza nel bilancio",
                        "B) L'accantonamento ECL passa da perdita attesa a 12 mesi (Stage 1) a perdita attesa lifetime (tutta la vita residua del credito) — tipicamente un salto 3-5× nell'importo dell'accantonamento; il cambio impatta direttamente il conto economico (rettifica di valore)",
                        "C) Il credito deve essere ceduto al mercato NPL entro 90 giorni",
                        "D) Stage 2 non ha effetti contabili — è solo un segnale di allerta interno"],
            "corretta": 1,
            "spiegazione": "IFRS 9 — Stage migration: Stage 1 → Stage 2 è la transizione più impattante. STAGE 1: ECL = PD(12m) × LGD × EAD. Esempio: PD 12m = 1%, LGD = 40%, EAD = €1M → ECL = €4.000. STAGE 2: ECL = PD(lifetime) × LGD × EAD. Se PD lifetime (5 anni) = 8% → ECL = 8% × 40% × 1M = €32.000. L'accantonamento aumenta di 8× in questo esempio → impatto significativo a CE (rettifica netta). TRIGGER per Stage 2: rating interno deteriora di 2+ notch, scaduto >30 giorni (ma reversibile), inclusione in watch-list, covenant in breach, settore in stress (forward-looking). CLIFF EFFECT: il 'salto' da Stage 1 a Stage 2 crea discontinuità — piccoli deterioramenti del merito creditizio hanno impatti contabili sproporzionati. Questo ha generato critiche: le banche hanno incentivo a mantenere artificialmente i debitori in Stage 1 per evitare l'impatto a CE (regulatory capital optimization vs accounting accuracy). Le autorità hanno rafforzato i trigger automatici."
          },
          {
            "testo": "Una banca vuole cedere un portafoglio NPL lordi per €500M con coverage ratio 45% (accantonamenti €225M) a un servicer specializzato (es. doValue, Prelios) al prezzo di €140M. Come impatta il bilancio?",
            "opzioni": ["A) Plusvalenza di €140M meno il valore lordo €500M = perdita €360M",
                        "B) Al momento della cessione: valore netto contabile = €500M − €225M (fondo rettifiche) = €275M netti. Prezzo cessione = €140M. Perdita da cessione = €275M − €140M = −€135M rilevata a CE; contemporaneamente vengono liberati gli accantonamenti €225M che erano già a rettifica del valore lordo",
                        "C) La cessione NPL non ha impatto a CE — è un'operazione di bilancio che sposta solo attivi",
                        "D) Plusvalenza di €140M poiché il portafoglio era già completamente svalutato"],
            "corretta": 1,
            "spiegazione": "CESSIONE NPL — CONTABILITÀ: Situazione pre-cessione: Crediti lordi: €500M (attivo, valore nominale). Fondo rettifiche: −€225M (contra-asset). Valore netto: €275M. All'atto della cessione: si incassano €140M (cassa). Si derecognize il credito lordo €500M. Si libera il fondo €225M. Risultato: entrata cassa €140M + liberazione fondo €225M = €365M ricevuto vs uscita netta credito €275M → PERDITA NETTA = €140 − €275 = −€135M a CE. La perdita da cessione NPL misura il gap tra il coverage ratio bancario e il prezzo di mercato NPL (recovery rate dei servicer). Nel 2015-2016 le banche italiane cedevano NPL a 20-25 centesimi su €1 di valore lordo → perdite enormi. Post-GACS e riforma: i prezzi NPL italiani sono saliti a 30-40 centesimi grazie al mercato più maturo e agli SRT (Significant Risk Transfer) garantiti dallo Stato."
          }
        ]
      },
      {
        "id": "B3", "titolo": "◈ BOSS — Bilancio Bancario IAS/IFRS",
        "desc": "⚔ SP e CE completi, NIM, ROE decomposition, CET1, Texas Ratio, EVA bancario",
        "xp": 200, "boss": True,
        "domande": [
          {
            "testo": "Decomposizione ROE bancaria (DuPont estesa): ROE = ROA × Equity Multiplier. Banca A: ROA = 0.8%, Equity Multiplier = 14× → ROE = 11.2%. Banca B: ROA = 1.2%, Equity Multiplier = 9× → ROE = 10.8%. Quale banca ha la struttura più efficiente risk-adjusted?",
            "opzioni": ["A) Banca A — ROE più alto di 0.4pp",
                        "B) Banca B ha ROA più alto (più profittevole per unità di attivo) con leva finanziaria più bassa (meno rischio) — un ROE simile con meno leva è superiore risk-adjusted: RAROC di B è migliore, CET1 ratio di B è più alto (EM più basso = più capitale / attivo)",
                        "C) Non è possibile confrontarle senza conoscere i RWA di entrambe",
                        "D) Banca A è più efficiente perché usa meglio la leva finanziaria disponibile"],
            "corretta": 1,
            "spiegazione": "DECOMPOSIZIONE ROE BANCARIO (DuPont): ROE = Net Income/Equity = (NI/TA) × (TA/Equity) = ROA × EM. EM (Equity Multiplier) = 1/CET1 Ratio approssimativamente. Banca A: EM=14× → CET1 ≈ 7.1% (basso). Banca B: EM=9× → CET1 ≈ 11.1% (più alto). RISK-ADJUSTED ANALYSIS: Banca A ha ROA basso (0.8%) e ALTA leva → più vulnerabile alle perdite inattese. Se ROA scende a 0.4% (shock), ROE A = 5.6% vs ROE B = 3.6% — ma B ha molto più buffer di assorbimento delle perdite. RAROC = RAROE: Return on Risk-Adjusted Capital. Banca B con CET1 più alto può assorbire più perdite prima di cadere sotto il requisito minimo. PRASSI REGOLAMENTARE: la BCE nel SREP valuta non solo il ROE ma il P&L sostenibile: banche con EM alto e ROA basso sono giudicate più vulnerabili e ricevono requisiti SREP aggiuntivi. L'obiettivo ottimale: massimizzare ROA (efficienza operativa) non EM (leva)."
          },
          {
            "testo": "Il Conto Economico bancario IFRS ha una struttura 'a scaletta' specifica. Partendo da Margine di Interesse (NIM netto = €800M), Commissioni nette = €400M, Risultato trading = −€50M, Spese operative = −€700M (cost-income = ?), Rettifiche ECL = −€150M, Imposte = −€80M. Qual è l'utile netto e il cost-income ratio?",
            "opzioni": ["A) Utile netto = €220M; Cost-Income = 58.3%",
                        "B) Utile netto = €220M; Cost-Income = 70% calcolato su proventi operativi totali (€1.000M) escluso trading",
                        "C) Utile netto = €220M; Cost-Income = 58.3% (700/(800+400−50))",
                        "D) Utile netto = €300M (escludendo le rettifiche che sono poste straordinarie)"],
            "corretta": 2,
            "spiegazione": "CONTO ECONOMICO BANCARIO — scaletta completa: Margine di Interesse (NIM): €800M. + Commissioni nette: +€400M. +/− Trading e fair value: −€50M. = PROVENTI OPERATIVI TOTALI (PBT pre-rettifiche): €1.150M. − Spese operative (personale + ammortamenti + amministrative): −€700M. = RISULTATO OPERATIVO (PPOP — Pre-Provision Operating Profit): €450M. − Rettifiche ECL e svalutazioni: −€150M. = UTILE ANTE IMPOSTE: €300M. − Imposte (aliquota ~26.7%): −€80M. = UTILE NETTO: €220M. COST-INCOME RATIO = Spese operative / Proventi totali = 700 / 1.150 = 60.9% (risposta C calcola diversamente). Nota: nel calcolo standard il trading viene incluso al denominatore → CIR = 700/1.150 = 60.9%. L'industria mira a CIR < 50-55% per essere competitiva. Il KPI PPOP (450M) misura la capacità di generare utile prima delle perdite su crediti — indicatore di resilienza. PPOP / RWA = indicatore di buffer contro le perdite ECL future."
          },
          {
            "testo": "Basilea III Pillar 1 richiede CET1 ≥ 4.5% + Capital Conservation Buffer 2.5% = 7% di CET1. UniCredit ha CET1 = 15.9%. Perché mantiene un buffer così elevato rispetto al minimo?",
            "opzioni": ["A) La regolamentazione impone CET1 = 15.9% per le banche G-SIB — il minimo di 7% è solo per le piccole banche locali",
                        "B) Il CET1 effettivo richiesto è 7% (P1) + P2R ≈ 2% + G-SIB buffer 1-2% + CCyB + management buffer → requisito totale ~12-13%; il buffer di 15.9% è strategico: segnalazione ai mercati di solidità, spazio per crescita degli RWA, capacità di pagare dividendi senza scendere sotto il MDA, assorbimento di perdite inattese",
                        "C) UniCredit ha un accordo specifico con la BCE che impone CET1 ≥ 15% come condizione per operare in 25 paesi",
                        "D) Il CET1 alto è obbligatorio per legge italiana — il TUB impone coefficienti più alti dello standard europeo"],
            "corretta": 1,
            "spiegazione": "STRUTTURA REQUISITI CET1 — stack completo per UniCredit: P1 Pillar 1: 4.5% (minimo assoluto). + Capital Conservation Buffer (CCB): 2.5%. = P1+CCB: 7%. + Pillar 2 Requirement (P2R — SREP): ~2-2.5% (confidenziale, ma disclosed in forma aggregata). + G-SIB surcharge (UniCredit è G-SIB bucket 1): 1%. + Countercyclical Buffer (CCyB): ~0.5% (varia per paese di esposizione). = REQUISITO TOTALE (MDA trigger): ~11-12%. Buffer gestionale sopra MDA: ~3-4% (management buffer). = CET1 target 14-16%. Il MDA (Maximum Distributable Amount) si attiva se CET1 scende sotto il requisito totale: limiti automatici a dividendi, buy-back, bonus variabili. L'eccesso di CET1 (buffer strategico) ha valore: (1) Segnale di solidità → funding cost più basso; (2) Flessibilità per M&A e crescita RWA; (3) Stabilità del dividendo; (4) Buffer per stress scenarios (SREP/EBA stress test)."
          }
        ]
      }
    ]
  },

  "mercati": {
    "nome": "Mercati Mobiliari", "emoji": "◉",
    "colore": "teal", "accent": "#2A7B7C",
    "xp_totale": 650,
    "desc": "Azioni, obbligazioni, derivati, microstructura, efficienza, valutazione",
    "livelli": [
      {
        "id": "M1", "titolo": "Obbligazioni: Struttura e Pricing Avanzato",
        "desc": "YTM, duration, convexity, spread, titoli di Stato, OAT, Bund, BTP",
        "xp": 90,
        "domande": [
          {
            "testo": "Il 'doom loop' sovrano-bancario descrive un meccanismo di amplificazione delle crisi. Come funziona?",
            "opzioni": ["A) Le banche comprano troppi BTP → quando i BTP scendono, le banche perdono capitale → le banche riducono il credito → l'economia rallenta → le entrate fiscali calano → deficit aumenta → spread sale → BTP scendono ancora (loop)",
                        "B) Le banche centrali comprano troppi titoli di Stato creando inflazione",
                        "C) I fondi pensione vendono BTP per comprare azioni causando crollo dei prezzi sovrani",
                        "D) I governi nazionalizzano le banche in difficoltà peggiorando il debito pubblico"],
            "corretta": 0,
            "spiegazione": "IL DOOM LOOP (Brunnermeier, 2012): il circolo vizioso tra rischio bancario e rischio sovrano europeo: (1) Le banche europee detengono grandi quantità di titoli sovrani del proprio paese (home bias: banche italiane ~€350-400 mld di BTP). (2) Quando il rischio sovrano aumenta → prezzi BTP scendono → le banche subiscono perdite FVOCI/FVTPL e write-down → CET1 erode → le banche riducono il credito e/o vendono attivi. (3) La contrazione del credito rallenta l'economia → entrate fiscali scendono, spesa sociale sale → deficit aumenta → investitori chiedono premio di rischio più alto → spread allargato → BTP giù ancora. (4) Le banche in difficoltà potrebbero richiedere bail-out pubblico → aumenta il debito sovrano → peggiorano ancora le prospettive fiscali. EPISODI: Italia/Spagna/Portogallo 2011-12, Grecia 2010-15. SOLUZIONE STRUTTURALE: l'Unione Bancaria (SSM + SRM + EDIS) e il completamento dell'Unione dei Mercati di Capitali mirano a rompere questo legame. Il principale strumento rimanente è il limite normativo alle esposizioni concentrate su singolo emittente (Large Exposure Rules — escludono però le esposizioni sovrane in valuta domestica, problema ancora irrisolto nel dibattito europeo)."
          },
          {
            "testo": "L'inflazione inattesa impatta diversamente su BTP cedola fissa vs BTPi (BTP Italia indicizzato all'inflazione). Con inflazione effettiva al 8% contro il 2% atteso al momento dell'emissione:",
            "opzioni": ["A) Il BTP fisso e il BTPi subiscono lo stesso impatto perché entrambi sono obbligazioni sovrane italiane",
                        "B) Il BTP fisso perde in termini reali: il rendimento reale = nominale − inflazione reale = 3% − 8% = −5%. Il BTPi mantiene il rendimento reale: il capitale si rivaluta dell'8% e la cedola è calcolata sul capitale rivalutato → l'investitore è protetto dall'inflazione inattesa",
                        "C) Il BTPi perde valore perché i mercati scontano l'inflazione futura riducendo i prezzi",
                        "D) Entrambi guadagnano con alta inflazione perché il governo emette meno nuovi titoli"],
            "corretta": 1,
            "spiegazione": "BTP FISSO vs BTPi: BTP fisso (nominale): cedola = % fisso × valore nominale costante. Con inflazione 8%: rendimento REALE = 3% (nominale) − 8% (inflazione) = −5%/anno. Il potere d'acquisto dell'investitore scende. BTPi (indicizzato all'HICP italiano): capitale rivalutato = Nominale × (Indice finale / Indice emissione) = 1.000 × (108/100) = 1.080. Cedola = % reale × capitale rivalutato = 1% × 1.080 = €10.80 vs €10 del BTP fisso. Rendimento reale = circa +1% (il tasso cedolare reale è quello stabilito all'emissione). SPREAD BEI (Break-Even Inflation): la differenza di yield tra BTP fisso e BTPi della stessa scadenza misura l'INFLAZIONE ATTESA dal mercato (Break-Even Inflation Rate). Se BEI = 2% ma inflazione realizzata = 8% → gli investitori in BTPi hanno guadagnato enormemente rispetto ai detentori di BTP fissi. STRUMENTO DI POLICY: le banche centrali usano i BEI per misurare le aspettative di inflazione di mercato — uno degli input chiave per le decisioni di tasso BCE."
          },
          {
            "testo": "Il 'mercato dei repo' (PCT) europeo (€10+ trilioni di outstanding) è cruciale per la liquidità interbancaria. Cosa causa un 'repo market freeze' e quali conseguenze ha?",
            "opzioni": ["A) Un freeze del repo avviene quando la BCE alza i tassi di interesse — le banche preferiscono il mercato obbligazionario",
                        "B) Un repo freeze avviene quando il collaterale perde credibilità (downgrade sovrano, haircut increase) → le banche non si prestano più fondi → illiquidità improvvisa anche per banche solvibili → credit crunch nell'economia reale",
                        "C) I repo freeze sono eventi tecnici causati da guasti ai sistemi di clearing (LCH, Eurex Clearing)",
                        "D) I freeze avvengono a fine trimestre per ragioni di window dressing dei bilanci bancari"],
            "corretta": 1,
            "spiegazione": "REPO MARKET FREEZE — meccanismo di contagio finanziario: (1) COLLATERAL QUALITY: i repo sono garantiti da titoli di alta qualità (govies, covered bonds). Se il collaterale si svaluta o viene downgradato → la controparte richiede haircut più alti o rifiuta il collaterale → la banca non può più finanziare le proprie posizioni. (2) MECHANICS: Lehman (settembre 2008): il crollo del valore degli MBS come collaterale → le controparti smettono di accettarli → Lehman non riesce a rollare i propri repo overnight → illiquidità → insolvenza in 48 ore. (3) CONTAGIO: anche banche solvibili con buoni asset non riescono a finanziare le proprie posizioni → vendita forzata → crollo dei prezzi → amplificazione. (4) 2011 EUROREPO CRISIS: i govies periferici (BTP, Bonos) smettono di essere accettati come collaterale da molte controparti → segmentazione del mercato → spread interbancari italiani/spagnoli alle stelle. SOLUZIONI: la BCE ha aperto lo sportello di emergency liquidity (ELA) e ampliato gli asset eligible come collaterale nelle MRO/LTRO per sopperire al blocco del mercato privato."
          }
        ]
      },
      {
        "id": "M2", "titolo": "Azioni: Valutazione e Anomalie",
        "desc": "DDM, Gordon, multipli, CAPM, anomalie di mercato, behavioral finance",
        "xp": 120,
        "domande": [
          {
            "testo": "Il CAPM (Capital Asset Pricing Model) afferma: E(R) = Rf + β × (Rm − Rf). Eni ha β = 1.2, Rf = 3%, premio di mercato (Rm−Rf) = 5%. Il costo dell'equity di ENI per il DDM è:",
            "opzioni": ["A) 6% — calcolato come Rf + β = 3% + 1.2 = ... (errore concettuale)",
                        "B) 9% — calcolato come Rf + β×MRP = 3% + 1.2×5% = 3% + 6% = 9%",
                        "C) 5% — il premio di mercato aggiustato per il beta",
                        "D) 8% — calcolato come β × Rm = 1.2 × 8% (ipotizzando Rm = 8%)"],
            "corretta": 1,
            "spiegazione": "CAPM: E(R_ENI) = 3% + 1.2 × 5% = 3% + 6% = 9%. β > 1 → ENI è più volatile del mercato (settore energy ciclico): quando il mercato sale del 10%, ENI tende a salire del 12% e viceversa. Questo tasso del 9% è il 'costo dell'equity' da usare nel DDM: P = D1 / (r − g) = D1 / (9% − g). LIMITAZIONI DEL CAPM: (1) β instabile nel tempo — il β di Eni varia con il prezzo del petrolio. (2) Un solo fattore di rischio — il Fama-French 3-factor model aggiunge size (SMB) e value (HML); il modello a 5 fattori aggiunge profitability e investment. (3) Beta backward-looking — il β storico non prevede necessariamente quello futuro. (4) Market portfolio non osservabile (Roll's Critique, 1977). IN PRATICA: le banche d'investimento usano β adjusted (0.67 × β storico + 0.33 × 1.0) per convergere verso 1.0 nel lungo periodo. Il costo dell'equity viene spesso validato con il 'dividend yield + growth rate' approach come cross-check."
          },
          {
            "testo": "L'anomalia del 'momentum' sui mercati azionari (Jegadeesh & Titman, 1993) contraddice l'EMH nella forma semi-forte. Come funziona e perché persiste?",
            "opzioni": ["A) Il momentum è semplicemente il beta: le azioni ad alto beta salgono di più in mercati toro",
                        "B) Le azioni che hanno performato meglio negli ultimi 3-12 mesi tendono a continuare a farlo nei successivi 3-6 mesi (winner stocks) — persiste perché i prezzi recepiscono l'informazione lentamente (under-reaction) e/o per effetto herding degli investitori istituzionali",
                        "C) Il momentum spiega perché le azioni value (basso P/B) sovraperformano le growth — è un proxy del rischio fondamentale",
                        "D) Il momentum è solo un artefatto statistico che scompare nei periodi di alta volatilità di mercato"],
            "corretta": 1,
            "spiegazione": "MOMENTUM ANOMALY — una delle anomalie più robuste nella finanza empirica: SCOPERTA: Jegadeesh & Titman (1993) su dati NYSE/AMEX 1963-1989: strategia long top decile/short bottom decile performance 6-12 mesi passati → rendimento anomalo ~1%/mese per i 6 mesi successivi. SPIEGAZIONI COMPORTAMENTALI: (1) Under-reaction iniziale (Barberis, Shleifer, Vishny, 1998): gli investitori aggiornano troppo lentamente le aspettative all'arrivo di buone notizie → i prezzi salgono gradualmente invece di saltare. (2) Herding istituzionale: i fondi comprano i winner perché sono valutati sulla performance relativa → momentum self-fulfilling. (3) Disposition effect (Shefrin & Statman): gli investitori vendono troppo presto i winner (per cristallizzare il guadagno) e mantengono i loser troppo a lungo → ritardano l'aggiornamento dei prezzi. CRASH RISK: il momentum 'crasha' nei momentum reversals (es. marzo 2020, agosto 2022): quando il mercato si ribalta bruscamente, la strategia short subisce perdite enormi. L'AQR Capital Management gestisce miliardi su strategie momentum — dimostrazione che l'anomalia persiste nonostante sia nota."
          },
          {
            "testo": "Un'IPO (Initial Public Offering) di una PMI tecnologica italiana su Euronext Milan: il bookbuilding fissa il prezzo a €10/azione. Statisticamente, entro 3-6 mesi dall'IPO, cosa si osserva tipicamente ('long-run underperformance' di Ritter, 1991)?",
            "opzioni": ["A) Le IPO sovraperformano il mercato del 15-20% nei primi 6 mesi grazie all'effetto novità",
                        "B) In media le IPO mostrano underperformance rispetto al mercato nel lungo periodo (3-5 anni): le imprese tendono a quotarsi quando le valutazioni di mercato sono elevate (market timing), e i promotori/banche tendono a fissare prezzi che massimizzano i proventi dell'emissione a scapito degli investitori",
                        "C) Le IPO non mostrano pattern sistematici — ogni caso è indipendente",
                        "D) Le IPO sovraperformano perché solo le migliori imprese si quotano — effetto selezione positiva"],
            "corretta": 1,
            "spiegazione": "IPO ANOMALIES (Ritter 1991, Loughran & Ritter 1995): due anomalie documentate: (1) UNDERPRICING di breve periodo: il prezzo di chiusura del 1° giorno è in media 10-20% sopra il prezzo IPO (l'emittente lascia 'money on the table'). PERCHÉ: information asymmetry tra emittente e investitori — il prezzo IPO basso serve ad attrarre investitori informati che poi 'certificano' il valore con i loro acquisti. (2) LONG-RUN UNDERPERFORMANCE: nei 3-5 anni post-IPO, le imprese neo-quotate underperformano il benchmark del 20-30% cumulativamente (dato USA). SPIEGAZIONI: Market timing theory (Baker & Wurgler): le imprese si quotano quando le valutazioni sono alte → gli investitori pagano multipli elevati destinati a comprimersi. Grandstanding: venture capital e promotori 'scaricano' sul mercato le imprese al picco di valutazione. Finestre di mercato: le IPO si concentrano nei bull market → selection bias. IMPLICAZIONE PRATICA: i retail investor che comprano IPO in borsa al primo giorno di trading storicamente ottengono rendimenti peggiori del mercato su 3 anni. Le IPO da comprare sono quelle del bookbuilding — riservate agli istituzionali."
          }
        ]
      },
      {
        "id": "M3", "titolo": "◈ BOSS — Derivati, Strutture e Microstructura",
        "desc": "⚔ Options, Greeks, IRS, VaR, mercato order/quote-driven, HFT",
        "xp": 200, "boss": True,
        "domande": [
          {
            "testo": "Il 'Greek' Delta di un'opzione call vale 0.65. Cosa significa e come varia con il tempo (theta) e la volatilità (vega)?",
            "opzioni": ["A) Il premio dell'opzione aumenta di €0.65 per ogni €1 di aumento del sottostante — Delta è sempre costante durante la vita dell'opzione",
                        "B) Δ = 0.65: per ogni €1 di aumento dell'azione, il valore della call aumenta di €0.65. Δ converge a 1 per call deep-in-the-money e a 0 per deep-out-of-money; vega misura la sensibilità al cambiamento della volatilità implicita (vega positivo per opzioni lunghe); theta è il 'time decay' — ogni giorno che passa riduce il valore dell'opzione (theta negativo per le posizioni long options)",
                        "C) Delta misura la probabilità risk-neutral che l'opzione scada in-the-money alla scadenza",
                        "D) Delta è sempre 0.5 per le opzioni at-the-money indipendentemente dalla scadenza e dalla volatilità"],
            "corretta": 1,
            "spiegazione": "GREEKS — delta hedging e sensibilità: Δ (Delta): variazione del prezzo dell'opzione per €1 di variazione del sottostante. Call Δ ∈ [0,1]; Put Δ ∈ [−1,0]. Δ = 0.65 → la call è leggermente in-the-money. Un delta-hedger neutrale vende 0.65 azioni per ogni opzione call acquistata. Γ (Gamma): tasso di variazione del delta → misura la convexity dell'opzione. Gamma massimo per opzioni ATM. Θ (Theta): time decay — ogni giorno trascorso riduce il valore dell'opzione (le opzioni sono 'deperibili'). Long options: Θ < 0 (perdi tempo-valore ogni giorno). Short options: Θ > 0 (guadagni dal time decay). ν (Vega): sensibilità alla volatilità implicita. Long options: Vega > 0 (beneficiano di più volatilità). Short options: Vega < 0. Ρ (Rho): sensibilità ai tassi di interesse (rilevante per opzioni con lunga scadenza). PUT-CALL PARITY: C − P = S − K×e^(−rT). Relazione fondamentale che lega prezzi call e put — violazioni (rare) sono opportunità di arbitraggio."
          },
          {
            "testo": "Un hedge fund usa un 'variance swap' per posizionarsi sulla volatilità realizzata di Intesa SanPaolo. Paga volatilità fissa del 20% e riceve volatilità realizzata. Se la volatilità realizzata nel periodo è 28%, il payoff del fondo è:",
            "opzioni": ["A) 28% − 20% = 8% del nozionale",
                        "B) (28²− 20²) × (Nozionale/Vega notional) = (784 − 400) × vega = 384 × vega. Il payoff si basa su VARIANZA (σ²), non sulla volatilità — il nozionale è in 'variance points'",
                        "C) (28 − 20)% × nozionale = 8% × nozionale (payoff lineare sulla volatilità)",
                        "D) Il payoff è zero — la volatilità fissa e quella realizzata si annullano in un variance swap"],
            "corretta": 1,
            "spiegazione": "VARIANCE SWAP — uno degli strumenti più sofisticati del mercato dei derivati: PAYOFF = (σ²_realizzata − K²_var) × Vega_nozionale × (1/2). Il payoff è sulla VARIANZA (σ²), non sulla volatilità (σ). Con σ_realizzata = 28%, K = 20%: σ²_r = 784 (variance points), K² = 400. Payoff = (784 − 400) × Vega = 384 × Vega. VANTAGGI vs Straddle/opzioni: payoff puro sulla volatilità realizzata, senza dover gestire il delta-hedging continuo. Il vega del variance swap è costante (a differenza delle opzioni dove il vega dipende dal moneyness). VOLATILITY vs VARIANCE: il mercato degli strumenti sulla volatilità (VIX, variance swap, vol swap) è cresciuto enormemente: investitori usano la volatilità come asset class. Il VIX (CBOE Volatility Index per S&P500) misura la volatilità implicita ATM a 30 giorni — il 'fear gauge' del mercato. Nel 2008 il VIX ha toccato 80+ (vs media storica ~18-20). Il VVIX (volatilità della volatilità) misura quanto è incerta la volatilità stessa — secondo livello di complessità."
          },
          {
            "testo": "Il trading ad alta frequenza (High-Frequency Trading, HFT) rappresenta ~50-60% del volume azionario nei mercati USA. Qual è il principale beneficio e il principale rischio sistemico?",
            "opzioni": ["A) Beneficio: profitti per gli HFT trader; Rischio: nessuno — il mercato si auto-regola",
                        "B) Beneficio: liquidità immediata e spread bid-ask ridotti → minori costi di transazione per gli investitori tradizionali. Rischio: 'flash crash' — cascate di ordini automatici amplificano i movimenti di prezzo con velocità inumana (es. Flash Crash maggio 2010: Dow Jones -1.000 punti in 36 minuti)",
                        "C) Beneficio: riduzione della volatilità del mercato; Rischio: aumento dei costi di intermediazione per le piccole banche",
                        "D) Beneficio: prezzi più informativi; Rischio: monopolio del mercato da parte di poche imprese tecnologiche"],
            "corretta": 1,
            "spiegazione": "HFT — dibattito accademico e regolamentare: PRO (benefici): Riduzione degli spread bid-ask: studi mostrano che l'HFT ha ridotto gli spread del 50-80% negli ultimi 20 anni. Maggiore liquidità immediata: ordini enormi vengono assorbiti più velocemente. Price discovery più efficiente: l'arbitraggio di latenza tra mercati diversi mantiene i prezzi allineati. CONTRO (rischi): Flash Crash (6 maggio 2010): un ordine enorme di E-mini S&P500 futures di Waddell & Reed ha innescato una cascata di HFT sell orders → mercato -9% in minuti → rimbalzo completo in 90 minuti. Cause: liquidity withdrawal — gli HFT si ritirano dal mercato nei momenti di stress, quando la liquidità è più necessaria. Front-running: alcuni HFT vedono gli ordini istituzionali in arrivo e si posizionano davanti (tecnicamente legale ma eticamente contestato). REGOLAZIONE: MiFID II ha introdotto obblighi di market making continuativo, circuit breaker automatici, tassa sulle transazioni finanziarie (in discussione UE). La SEC ha introdotto il Consolidated Audit Trail (CAT) per tracciare tutti gli ordini HFT."
          }
        ]
      }
    ]
  },

  "intermediari": {
    "nome": "Intermediari Specializzati", "emoji": "◆",
    "colore": "rust", "accent": "#C4522A",
    "xp_totale": 550,
    "desc": "Assicurazioni, SGR/SICAV, SIM, leasing, factoring, private equity",
    "livelli": [
      {
        "id": "I1", "titolo": "Assicurazioni & Asset Liability Management",
        "desc": "Ramo vita, ramo danni, riserve tecniche, Solvency II, bancassurance",
        "xp": 80,
        "domande": [
          {
            "testo": "Solvency II (entrata in vigore 2016) ha rivoluzionato la regolamentazione assicurativa europea con un approccio a 3 Pilastri analogo a Basilea. Il Pillar 1 (requisiti quantitativi) introduce il SCR (Solvency Capital Requirement). Come si calcola e cosa copre?",
            "opzioni": ["A) SCR = 8% delle riserve tecniche — analogo al CET1 bancario",
                        "B) SCR = capitale necessario per sopravvivere a uno shock 'Value at Risk 99.5% a 1 anno' — copre i rischi di sottoscrizione, di mercato, di credito e operativo; è calcolato con formula standard o modello interno approvato dall'IVASS",
                        "C) SCR = somma dei premi raccolti nell'anno × coefficiente di rischiosità del ramo",
                        "D) SCR è un requisito puramente qualitativo — non ha formula quantitativa, è determinato caso per caso dall'IVASS"],
            "corretta": 1,
            "spiegazione": "SOLVENCY II — architettura: PILLAR 1: Quantitative requirements. SCR (Solvency Capital Requirement): VaR 99.5% a 1 anno su tutti i rischi combinati (mercato, sottoscrizione vita/danni, credito, operativo). Se il VaR 99.5% = €500M → la compagnia deve avere €500M di fondi propri eligible. MCR (Minimum Capital Requirement) = VaR 85% → soglia di triggering intervention. PILLAR 2: Governance, risk management, ORSA (Own Risk and Solvency Assessment) = analogo dell'ICAAP bancario. PILLAR 3: Reporting e trasparenza (SFCR — Solvency and Financial Condition Report pubblico). NOVITÀ CHIAVE vs. Solvency I: approccio mark-to-market per le riserve tecniche (Best Estimate + Risk Margin) vs. approccio prudenziale statico di Solvency I. Gli attivi sono valorizzati al fair value → le compagnie assicurative sono diventate molto più sensibili ai movimenti dei tassi (l'ALM è diventato centrale). Il rialzo dei tassi BCE 2022-2023 ha MIGLIORATO la solvency ratio delle compagnie vita perché ha ridotto il valore delle riserve tecniche (passivo) più di quanto non riducesse gli attivi obbligazionari — effetto duration mismatch favorevole per le assicurazioni con passivo a lunga duration."
          },
          {
            "testo": "Un fondo pensione a prestazione definita (Defined Benefit, DB) ha obbligazioni future verso i pensionati con duration 20 anni e un portafoglio obbligazionario con duration 8 anni. Quale rischio di tasso affronta e come si copre?",
            "opzioni": ["A) Il fondo rischia di guadagnare troppo se i tassi scendono — le obbligazioni in portafoglio si apprezzano",
                        "B) Il fondo ha un duration gap negativo: duration attivi (8) < duration passivi (20). Se i tassi scendono: il valore delle obbligazioni pensionistiche (passivo) sale molto più degli attivi → funding ratio si deteriora. Si copre allungando la duration degli attivi (LDI — Liability Driven Investment) tramite IRS receiver-fixed o zero coupon bonds a lunghissima scadenza",
                        "C) Il fondo non è esposto al rischio di tasso perché i rendimenti obbligazionari e le obbligazioni pensionistiche variano nella stessa direzione",
                        "D) Il rischio è solo inflazionistico — le pensioni sono indicizzate all'inflazione, quindi occorre coprirsi con BTPi"],
            "corretta": 1,
            "spiegazione": "LDI (Liability Driven Investment) — strategia dei fondi pensione DB: il problema classico: passivi (future pensioni) hanno duration 15-25 anni; un tipico portafoglio obbligazionario ha duration 5-8 anni → DURATION GAP = D_attivi − D_passivi < 0. Quando i tassi scendono di 1%: Passivi aumentano di ~20% (duration 20 × 1%). Attivi aumentano di ~8% (duration 8 × 1%). Funding ratio = Attivi/Passivi scende. CRISI UK OTT 2022: la Bank of England ha alzato i tassi velocemente → i fondi pensione DB con LDI estrategies che usavano IRS e gilt come collaterale hanno ricevuto margin calls devastanti (i gilt si erano svalutati rapidamente) → vendita forzata di gilt → spiral → BoE ha dovuto intervenire comprando gilt di emergenza. SOLUZIONE LDI: aggiungere receiver IRS lunghi (ricevono il tasso fisso: quando i tassi scendono, l'IRS si apprezza compensando la perdita dei passivi), o comprare zero coupon bond 30 anni. Il compromesso: allocare parte del portafoglio al 'performance portfolio' (azioni, credito) per generare rendimento e parte al 'liability matching portfolio'."
          }
        ]
      },
      {
        "id": "I2", "titolo": "Fondi, SGR, Private Equity e ETF",
        "desc": "Gestione attiva vs passiva, performance, smart beta, private equity lifecycle",
        "xp": 110,
        "domande": [
          {
            "testo": "La 'persistenza della performance' dei fondi attivi è il principale argomento a favore della gestione attiva. I dati storici (Carhart 1997, S&P SPIVA) mostrano invece che:",
            "opzioni": ["A) Il 70-80% dei fondi attivi batte il benchmark nel lungo periodo (10 anni) — la selezione del gestore è cruciale",
                        "B) La maggioranza dei fondi attivi non batte il benchmark al netto delle commissioni nel lungo periodo (10 anni: ~80-90% dei fondi USA azionari sottoperforma l'S&P500 al netto dei costi); la performance passata non è un buon predittore di quella futura",
                        "C) I fondi attivi battono sistematicamente in mercati volatili e sottoperformano in mercati stabili",
                        "D) I fondi attivi battono il benchmark nei mercati emergenti ma non nei mercati sviluppati — è coerente con l'EMH"],
            "corretta": 1,
            "spiegazione": "GESTIONE ATTIVA vs PASSIVA — il grande dibattito della finanza: DATI SPIVA (S&P Indices vs Active): su 10 anni, ~85-90% dei fondi azionari USA large cap attivi sottoperforma l'S&P500 al netto delle commissioni. MATEMATICA DEL ZERO-SUM GAME (Sharpe 1991): prima dei costi, il rendimento medio di tutti i gestori attivi DEVE essere uguale al rendimento del mercato (i gestori attivi sono il mercato). Dopo i costi (commissioni 0.8-1.5%/anno per i fondi attivi vs 0.05-0.1% per ETF), la media dei gestori attivi DEVE sottoperformare il mercato per via della commissione. ECCEZIONI: alcuni segmenti dove i gestori attivi aggiungono valore: small cap, mercati emergenti, credito illiquido (meno efficienti). PRIVATE EQUITY: non è un fondo pubblico — investe in aziende private con lockup 7-10 anni, usa leva, ottiene controllo gestionale → può veramente aggiungere valore operativo. I migliori PE (KKR, Blackstone) hanno generato alpha persistente, ma l'accesso è riservato agli istituzionali. ETF rivoluzione: dal 1993 (primo SPDR S&P500) → oggi >$10 trilioni di AUM in ETF globali. In Italia la quota dei fondi passivi è ~20% dell'industria (vs ~50% USA), ma cresce rapidamente."
          },
          {
            "testo": "Un fondo di Private Equity (PE) acquista un'azienda manifatturiera (target) con LBO (Leveraged Buyout): acquisto €200M, equity del PE = €60M, debito bancario = €140M. EBITDA target = €20M, multiplo di acquisto = 10× EV/EBITDA. Dopo 5 anni vuole uscire con EV = €280M e debito residuo = €80M. Qual è il MOIC (Multiple on Invested Capital)?",
            "opzioni": ["A) MOIC = 1.4× — calcolato come EV finale / EV iniziale = 280/200",
                        "B) MOIC = EV finale − Debito residuo / Equity iniziale = (280 − 80) / 60 = 200 / 60 = 3.3× — il PE riceve il valore dell'equity (EV meno debito) dividendo per l'equity investito inizialmente",
                        "C) MOIC = 5× — il PE ha quintuplicato l'EBITDA da 20M a 100M",
                        "D) MOIC = 2× — calcolato come (EV finale / EV iniziale) × (debito iniziale / debito residuo)"],
            "corretta": 1,
            "spiegazione": "LBO RETURNS — tre driver di valore nel PE: MOIC = (EV_exit − Debt_residuo) / Equity_investito = (280 − 80) / 60 = 3.3×. Per convertire in IRR: 60 → 200 in 5 anni: IRR = (200/60)^(1/5) − 1 = 3.33^0.2 − 1 ≈ 27% annuo. LE TRE FONTI DI VALORE IN UN LBO: (1) LEVERAGE: il debito amplifica il rendimento dell'equity (effet levier). Con EV da 200 a 280 = +40%; ma equity da 60 a 200 = +233%. La leva finanziaria moltiplica il rendimento dell'equity. (2) MULTIPLO EXPANSION: se EV/EBITDA all'uscita > all'entrata (es. acquisizione a 10×, uscita a 14×) → pura 'financial engineering'. (3) CRESCITA OPERATIVA: miglioramento dell'EBITDA tramite ottimizzazione costi, crescita ricavi, M&A bolt-on. Un buon PE genera alpha attraverso (3), non solo (1) e (2). DPI (Distributions to Paid-In) e TVPI (Total Value to Paid-In) sono le metriche standard del PE; il MOIC è un proxy semplificato. Commissioni PE: management fee 2% del committed capital + carried interest 20% sul profitto sopra l'hurdle rate (tipicamente 8%)."
          }
        ]
      },
      {
        "id": "I3", "titolo": "◈ BOSS — Business Model Avanzati",
        "desc": "⚔ BCE business model classification, banca universale, neobank, fintech disruption",
        "xp": 200, "boss": True,
        "domande": [
          {
            "testo": "I neobank (Revolut, N26, Bunq) hanno un costo di acquisizione cliente (CAC) molto più basso delle banche tradizionali grazie al modello digitale. Qual è il loro principale tallone d'Achille strutturale?",
            "opzioni": ["A) Non possono concedere prestiti — la normativa vieta ai neobank di fare attività creditizia",
                        "B) Il 'deposit stickiness' è molto più bassa rispetto alle banche tradizionali: i clienti dei neobank cambiano app con facilità (switching cost quasi zero) → funding instabile. Inoltre il LTV (Lifetime Value) del cliente è basso perché non c'è la 'relazione di filiale' che genera cross-selling → difficoltà a monetizzare oltre i pagamenti",
                        "C) I neobank non hanno accesso al sistema di pagamenti europeo (SEPA) — devono appoggiarsi alle banche tradizionali",
                        "D) I neobank pagano tassi di interesse sui depositi molto più alti delle banche tradizionali riducendo il NIM"],
            "corretta": 1,
            "spiegazione": "NEOBANK ECONOMICS — modello di business e vulnerabilità: VANTAGGI: CAC 10-50€ vs 200-400€ delle banche tradizionali (nessuna filiale, acquisizione via app/social). Costo operativo per transazione bassissimo (full automation). UX superiore, funzionalità innovative (multi-currency, crypto, round-up savings). PROBLEMI STRUTTURALI: (1) Revenue per customer basso: un cliente Revolut genera ~€15-20/anno vs €300-500/anno per un cliente bancario tradizionale con mutuo, assicurazioni, investimenti. (2) Profittabilità lontana: Revolut ha raggiunto la profittabilità solo nel 2021 dopo 6 anni — molti neobank continuano a bruciare cassa. (3) Credito: i neobank entrano nel credito (Revolut Pay Later, N26 Credit) ma soffrono dell'assenza di soft information → rischi di adverse selection. (4) Regolamentazione: ottenere una licenza bancaria completa (Revolut UK la ha ottenuta solo nel 2024 dopo anni di attesa) è costoso e limita la scalabilità. (5) Concentrazione di clienti: il cliente 'young urban digital' diventa più esigente e multi-banking con l'età → il valore del cliente cresce ma il neobank potrebbe non catturarlo."
          },
          {
            "testo": "Il 'modello di banca universale' (UniCredit, BNP Paribas, Deutsche Bank) integra retail, corporate e investment banking. Qual è il principale beneficio regolamentare del subholding/subsidiaries model vs il branch model?",
            "opzioni": ["A) Le subsidiary hanno capitale separato e possono fallire in modo ordinato (resolution) senza contagiare l'intera holding — la 'ring-fencing' protegge la banca commerciale dall'investment banking più rischioso",
                        "B) Le subsidiary pagano meno tasse rispetto ai branch perché sono entità legali indipendenti",
                        "C) Le subsidiary possono applicare standard contabili diversi (GAAP invece di IFRS) riducendo il capitale richiesto",
                        "D) Le subsidiary non sono soggette alla vigilanza BCE — solo la holding è supervisionata dal MVU"],
            "corretta": 0,
            "spiegazione": "STRUTTURA ORGANIZZATIVA BANCARIA — holding vs branch: BRANCH model: un'unica entità legale che opera in tutti i mercati tramite filiali. Vantaggi: efficienza del capitale (un unico pool), semplicità operativa. Svantaggio: un problema in una divisione si propaga a tutto il gruppo (no ring-fencing). SUBSIDIARY model: ogni divisione/paese è un'entità legale separata con proprio capitale. Vantaggio chiave: RESOLUTION PLANNING — la BRRD richiede piani di risoluzione credibili. Con le subsidiary, il Resolution Authority può chiudere/cedere singole entità senza abbattere il gruppo intero. Il ring-fencing delle attività retail (proposto in UK dalla Vickers Report → implementato dal 2019) separa obbligatoriamente la banca commerciale (depositi retail, prestiti PMI) dall'investment banking → protegge i depositanti retail dal rischio delle attività di trading. In Italia il D.Lgs. 16/2015 ha implementato la BRRD. UniCredit ha adottato il 'One UniCredit' model (2022): semplificazione della struttura sub-holding per ridurre complessità e costo di funding. Il trade-off rimane: efficienza del capitale (branch) vs resolution readiness (subsidiary)."
          }
        ]
      }
    ]
  },

  "rischio": {
    "nome": "Rischio & Regolamentazione", "emoji": "◐",
    "colore": "rust", "accent": "#C4522A",
    "xp_totale": 650,
    "desc": "Rischi bancari, Basilea IV, vigilanza SSM, stress test EBA, governance",
    "livelli": [
      {
        "id": "R1", "titolo": "Tassonomia e Misurazione dei Rischi",
        "desc": "VaR, ES, gap analysis, rischio operativo, ESG risk, rischio sistemico",
        "xp": 90,
        "domande": [
          {
            "testo": "L'Expected Shortfall (ES, o CVaR) al 97.5% è preferito al VaR 99% da Basilea IV per il trading book. Perché è considerato superiore?",
            "opzioni": ["A) L'ES è più facile da calcolare — richiede meno dati storici del VaR",
                        "B) L'ES misura la PERDITA MEDIA nella coda della distribuzione (il 2.5% peggiore dei casi), mentre il VaR indica solo la soglia superata in quel 2.5% dei casi — l'ES è 'coerente' (soddisfa la sub-additività) e cattura meglio il fat tail risk tipico dei mercati finanziari",
                        "C) L'ES al 97.5% è matematicamente equivalente al VaR 99% — usano la stessa soglia di confidenza",
                        "D) L'ES è preferito perché può essere calcolato in tempo reale senza modelli statistici complessi"],
            "corretta": 1,
            "spiegazione": "VaR vs EXPECTED SHORTFALL — il dibattito tecnico: VaR al 99%: 'qual è la perdita massima che non supero nel 99% dei casi?' → indica la SOGLIA ma non dice QUANTO si perde oltre quella soglia. ES (Expected Shortfall) al 97.5%: 'qual è la perdita MEDIA nel 2.5% dei casi peggiori?' → cattura l'intera distribuzione della coda. ESEMPIO: due portafogli con lo stesso VaR 99% = €10M: Portfolio A: nel 1% dei casi peggiori, perde sempre €11M (coda corta). Portfolio B: nel 1% dei casi peggiori, perde tra €10.5M e €500M (coda pesante). Il VaR non distingue tra A e B. L'ES sì: ES(A) ≈ €11M, ES(B) >> €50M. SUB-ADDITIVITÀ: l'ES soddisfa ES(A+B) ≤ ES(A)+ES(B) (la diversificazione riduce il rischio) — il VaR viola questa proprietà in alcuni casi. FRTB (Fundamental Review of Trading Book — Basilea IV): sostituisce il VaR 99% con ES 97.5% su scenari di stress (250 giorni storici nel periodo di stress più severo nell'ultimo decennio). Cambiamento significativo per le banche con grandi trading book."
          },
          {
            "testo": "I rischi ESG (Environmental, Social, Governance) nel banking sono diventati materia di vigilanza prudenziale dalla BCE (Guide on Climate-Related Risks, 2020). Come si manifestano come rischio di CREDITO per una banca?",
            "opzioni": ["A) Le banche che finanziano imprese inquinanti ricevono direttamente multa dalla BCE proporzionale alle emissioni",
                        "B) Rischio fisico: i debitori in zone ad alto rischio climatico (inondazioni, siccità) subiscono danni agli asset che riducono la capacità di rimborso → NPL aumentano. Rischio di transizione: i debitori in settori ad alte emissioni (oil & gas, cemento, automotive ICE) subiscono svalutazione degli asset stranded → perdita di valore del collaterale. Entrambi aumentano PD e LGD",
                        "C) I rischi ESG sono solo reputazionali — non impattano le perdite effettive su crediti",
                        "D) I rischi ESG si materializzano solo per le banche che non hanno una policy ESG — le banche con rating ESG alto sono immuni"],
            "corretta": 1,
            "spiegazione": "RISCHI CLIMATICI NEL BANKING — due categorie: (1) RISCHIO FISICO: Acuto — eventi estremi (uragani, alluvioni, siccità). Cronico — cambiamenti permanenti (innalzamento mari, desertificazione). Come impatta il credito: un'impresa agricola colpita da siccità → perdita di fatturato → incapacità di rimborsare → NPL. Un immobile in zona costiera a rischio allagamento → svalutazione del collaterale → LGD più alta se il debitore defaulta. (2) RISCHIO DI TRANSIZIONE: la decarbonizzazione (tasse carbonio, normative, cambiamento consumi) svaluta gli 'stranded assets' (impianti fossili che perdono valore prima del previsto). Le banche con grandi portafogli verso settori 'brown' (oil & gas, coal, automotive ICE) hanno esposizioni che potrebbero deteriorarsi. STRESS TEST CLIMA BCE: nel 2022 la BCE ha condotto il primo climate stress test: ~60% delle 100+ banche supervisionate avevano esposizione significativa a rischi climatici, con perdite stimate nell'ordine di €70-80 mld in scenari avversi. Implicazioni: le banche stanno sviluppando metodologie di 'green-washing due diligence' e portafogli allineati agli obiettivi di Parigi."
          }
        ]
      },
      {
        "id": "R2", "titolo": "Governance e Vigilanza Europea",
        "desc": "SSM, SREP, Banking Union, BRRD, bail-in, stress test EBA, Basilea IV",
        "xp": 130,
        "domande": [
          {
            "testo": "L'Unione Bancaria Europea si fonda su tre pilastri. Il Terzo Pilastro — EDIS (European Deposit Insurance Scheme) — non è ancora completamente operativo. Quale è il principale ostacolo politico?",
            "opzioni": ["A) La BCE si è opposta all'EDIS perché ridurrebbe la sua autonomia nella gestione delle crisi bancarie",
                        "B) I paesi con sistemi bancari 'virtuosi' (es. Germania, Paesi Bassi) temono di dover sussidiare paesi con banche più deboli e molti NPL (es. Italia del 2015-16) — mancanza di condivisione del rischio prima della condivisione dell'assicurazione (risk-reduction before risk-sharing)",
                        "C) L'EDIS è già pienamente operativo dal 2022 — protegge i depositi fino a €200.000",
                        "D) La Corte di Giustizia UE ha dichiarato l'EDIS incompatibile con i trattati europei nel 2019"],
            "corretta": 1,
            "spiegazione": "UNIONE BANCARIA — I TRE PILASTRI: (1) SSM (Single Supervisory Mechanism) — OPERATIVO dal 2014: BCE vigila sulle ~120 banche significative (>€30 mld di attivi o >20% PIL nazionale); le banche meno significative sono vigilate dalle autorità nazionali (Banca d'Italia) in coordinamento con BCE. (2) SRM (Single Resolution Mechanism) — OPERATIVO dal 2016: Single Resolution Board (SRB) gestisce le crisi delle banche significant. Fondo di Risoluzione Unico (SRF) con ~€80 mld di target. (3) EDIS — IN STALLO politico: proposto nel 2015, ancora non approvato. Il PROBLEMA: se l'EDIS mutualizza il rischio di default dei depositi, i sistemi bancari solidi (Deutsche banche, ING) potrebbero dover contribuire a salvare depositanti italiani/greci. La precondizione posta da Germania e NL: ridurre prima il rischio (NPL ratio < threshold, limiti alle esposizioni sovrane concentrate) → poi condivisione del rischio EDIS. Progressi: la proposta 2023 della Commissione introduce un approccio ibrido (garanzia liquidity first, poi graduale mutualizzazione). Un EDIS completo sarebbe il completamento dell'architettura finanziaria europea — senza di esso il doom loop bank-sovereign è parzialmente irrisolto."
          },
          {
            "testo": "Lo Stress Test EBA biennale valuta la resilienza delle banche europee in uno scenario avverso. L'EBA stress test 2023 ha testato l'impatto di: recessione -6% PIL, tassi +200bps, mercati -55%. Quale variabile impatta di più le banche con portafogli grandi di titoli di Stato classificati FVOCI?",
            "opzioni": ["A) La variabile tassi (+200bps) — l'aumento dei tassi riduce il valore di mercato dei BTP in FVOCI impattando l'OCI (Other Comprehensive Income) e quindi il CET1 attraverso il filtro prudenziale",
                        "B) La recessione (-6% PIL) — l'impatto sugli NPL è sempre predominante rispetto al rischio di tasso",
                        "C) Il crollo dei mercati (-55%) — tutte le banche hanno large equity portfolios",
                        "D) Lo stress test non considera l'impatto dei tassi sui portafogli FVOCI — usa solo scenari di credito"],
            "corretta": 0,
            "spiegazione": "STRESS TEST E PORTAFOGLI SOVRANI FVOCI: La meccanica contabile: i BTP classificati FVOCI sono iscritti al fair value. Le variazioni di fair value vanno in OCI (riserva di patrimonio netto), non a CE. Con rialzo tassi +200bps: duration BTP 10Y ≈ 8 anni → perdita ≈ −8% × 2% = −16% del valore. Se la banca ha €50 mld di BTP FVOCI → OCI negativo di −€8 mld → CET1 si riduce di €8 mld (netto tax). FILTRO PRUDENZIALE: dal 2020 il Regolamento CRR2 ha introdotto un 'Danish Compromise' (filtro prudenziale transitorio): le banche possono escludere parte della perdita su sovrani FVOCI dal CET1 (neutralizzando l'effetto). La scelta è opzionale ma una volta adottata è permanente per quella coorte di titoli. STRESS TEST 2022-2023: il principale impatto sulle banche italiane è stato proprio il portafoglio BTP: €300-400 mld di BTP → anche +100bps di spread/tasso → impatto CET1 di centinaia di pb. Le banche italiane hanno adottato massicciamente il filtro prudenziale per proteggersi. Questo crea una discrepanza tra CET1 'regolamentare' (con filtro) e 'economico' (mark-to-market)."
          },
          {
            "testo": "Il processo SREP BCE per il 2024: una banca riceve un P2R (Pillar 2 Requirement) del 2.5% e un P2G (Pillar 2 Guidance) del 1%. Il CET1 requisito totale è: P1 4.5% + CCB 2.5% + P2R 2.5% + G-SIB buffer 1% + P2G 1% = 11.5%. La banca ha CET1 = 12%. Può pagare dividendi?",
            "opzioni": ["A) No — il CET1 è sopra il requisito totale, non può distribuire capitale agli azionisti",
                        "B) Il MDA (Maximum Distributable Amount) si calcola sul buffer sopra P1+CCB+P2R+G-SIB (non incluso il P2G che è solo guidance): CET1 = 12% vs MDA trigger = 4.5+2.5+2.5+1 = 10.5%. Buffer = 1.5pp → può distribuire parte dell'utile; il P2G non è vincolante (non limita i dividendi) ma BCE si aspetta che la banca lavori per rispettarlo",
                        "C) Può pagare il 100% dei dividendi — il CET1 supera il requisito totale incluso il P2G",
                        "D) Non può pagare dividendi — il P2G è vincolante e richiede CET1 ≥ 11.5% vs il 12% attuale (buffer troppo sottile)"],
            "corretta": 1,
            "spiegazione": "MDA (Maximum Distributable Amount) — la meccanica: Il MDA si attiva automaticamente quando il CET1 scende sotto la somma dei REQUISITI VINCOLANTI: P1 (4.5%) + CCB (2.5%) + P2R (2.5%) + G-SIB (1%) = 10.5%. Al di sotto del MDA trigger → limitazioni automatiche: dividendi, buyback e bonus variabili (AT1 coupon continuano). Il P2G (Guidance) NON è vincolante legalmente → non entra nel calcolo MDA trigger. BUFFER DISPONIBILE = 12% − 10.5% = 1.5% (vincolante) → la banca PUÒ pagare dividendi pari a una frazione dell'utile (la tabella MDA BCE determina la % massima distribuibile in base alla distanza dal buffer). COMUNICAZIONE BCE: la BCE si aspetta però che la banca rispetti il P2G (12% > 11.5% ✓ in questo caso), e lo utilizza nelle valutazioni SREP successive. Se la banca scendesse sotto il P2G, la BCE avvierebbe misure supervisory (moral suasion, restrizioni operative) anche se non scattano le limitazioni automatiche del MDA."
          }
        ]
      },
      {
        "id": "R3", "titolo": "◈ BOSS — Crisi, Risoluzione e Basilea IV",
        "desc": "⚔ BRRD bail-in, resolution tools, TLAC, Basilea IV output floor, SVB case study",
        "xp": 200, "boss": True,
        "domande": [
          {
            "testo": "Il caso Silicon Valley Bank (SVB, marzo 2023): la banca aveva $200 miliardi di attivi, quasi tutti in MBS e Treasuries a lunga scadenza (duration ~6 anni), finanziati da depositi non assicurati di startup tech. Quando i tassi salirono al 5%: quale è la sequenza esatta del fallimento?",
            "opzioni": ["A) SVB è fallita per il rischio di credito — i prestiti alle startup tech sono andati in default massicciamente",
                        "B) Sequenza: rialzo tassi → svalutazione portafoglio HtM (non rilevata a CE ma nota al mercato) → voci su perdite latenti → bank run digitale (i depositi non assicurati >$250K tech startups si trasferiscono in 48 ore via app) → SVB vende i titoli per far fronte ai rimborsi → le perdite latenti diventano realized → CET1 crolla → fallimento",
                        "C) SVB è fallita perché la Fed ha revocato la licenza bancaria a causa di violazioni di compliance",
                        "D) SVB è stata colpita da una cyberattack che ha bloccato il sistema informatico causando la perdita della fiducia"],
            "corretta": 1,
            "spiegazione": "SVB CASE STUDY — il bank run dell'era digitale: LA VULNERABILITÀ STRUTTURALE: SVB aveva un duration mismatch estremo: Attivi: MBS e Treasuries con duration ~6 anni (classificati HtM — held-to-maturity — le perdite latenti NON impattano il CET1 regolamentare). Passivi: depositi a vista non assicurati di startup tech (~95% sopra $250K, quindi non garantiti FDIC). LA SEQUENZA: Fed alza i tassi da 0% a 5% → portafoglio HtM ha perdite latenti di ~$17 miliardi (non rilevate). Moody's minaccia downgrade → SVB annuncia vendita di titoli a perdita per ricapitalizzarsi → panico. 8-9 marzo 2023: i VC (Sequoia, Founders Fund) consigliano ai portfolio company di ritirare i depositi → $42 miliardi di deflussi IN UN GIORNO via mobile app → impossibile da gestire. FDIC interviene il 10 marzo → FDIC Receivership. LEZIONI: (1) Il 'HtM accounting' nasconde il rischio di tasso reale. (2) I depositi non assicurati sono più volatili di quelli retail. (3) Un bank run digitale è 10× più veloce di uno fisico → la regolamentazione della liquidità (LCR) non aveva previsto questa velocità. (4) La Fed ha garantito tutti i depositi (anche sopra $250K) per evitare contagio sistemico — de facto un bail-out depositi non protetti."
          },
          {
            "testo": "Basilea IV introduce l'Output Floor al 72.5% degli RWA standardizzati. Come cambia la struttura competitiva del mercato bancario europeo tra banche IRB-advanced e banche standardizzate?",
            "opzioni": ["A) Le banche standardizzate (piccole) sono le più penalizzate — il floor aumenta i loro RWA",
                        "B) Le grandi banche IRB-advanced (che computavano RWA molto bassi con modelli interni) perdono vantaggio competitivo: il floor limita il risparmio di capitale derivante dall'IRB. Le banche standardizzate (che già calcolano RWA alti) non sono toccate dal floor — il livello playing field si appiattisce",
                        "C) Il floor impatta egualmente tutte le banche — è una misura di standardizzazione globale",
                        "D) L'output floor si applica solo alle G-SIB, non alle banche di medie dimensioni"],
            "corretta": 1,
            "spiegazione": "BASILEA IV — OUTPUT FLOOR: il contesto storico: negli anni 2000-2015, le grandi banche europee (Deutsche, BNP, UniCredit) hanno sviluppato modelli IRB avanzati (A-IRB) sempre più sofisticati → RWA del 30-50% inferiori rispetto all'approccio standardizzato → enorme vantaggio competitivo in termini di capitale libero per dividendi, crescita, M&A. Il floor al 72.5%: se RWA_modello = 50, RWA_standardizzato = 100, floor = 72.5 → si usano 72.5 (non 50). Il risparmio IRB scende da 50% a 27.5%. IMPATTO STIMATO (EBA 2021): le banche IRB-advanced europee subiranno un aumento medio degli RWA del 15-25% → richiesta di capitale aggiuntivo di €100-150 miliardi a livello europeo. Le banche più colpite: quelle con modelli interni più 'ottimistici' (banche francesi, tedesche, nordiche con portafogli mutui e corporate a basso PD). EFFETTI COMPETITIVI: (1) Le banche standardizzate (tipicamente medie e piccole) recuperano competitività. (2) Incentivo a cedere portafogli a basso margine (dove il floor è più stringente). (3) Possibile consolidamento bancario europeo per raggiungere la scala necessaria a sopportare il costo del capitale più alto. Timeline: implementazione graduale 2025-2030 in Europa (CRR3)."
          }
        ]
      }
    ]
  },

  "macro": {
    "nome": "Politica Monetaria BCE", "emoji": "◎",
    "colore": "purple", "accent": "#5C3D8A",
    "xp_totale": 600,
    "desc": "BCE, SEBC, strumenti convenzionali e non, inflazione, meccanismi di trasmissione",
    "livelli": [
      {
        "id": "P1", "titolo": "Architettura del SEBC e Mandato BCE",
        "desc": "Trattati, Maastricht, governance BCE, obiettivi e strumenti",
        "xp": 80,
        "domande": [
          {
            "testo": "Il mandato PRIMARIO della BCE è la stabilità dei prezzi (inflazione ~2%). Il mandato SECONDARIO è supportare le politiche economiche dell'UE (crescita, occupazione). La GERARCHIA è chiara: la stabilità dei prezzi ha priorità. Quando questo trade-off si è manifestato concretamente nel 2022-2023?",
            "opzioni": ["A) La BCE ha scelto di non alzare i tassi per proteggere la crescita — ha privilegiato il mandato secondario",
                        "B) La BCE ha alzato i tassi al 4% nonostante la recessione tecnica in Germania e il forte rallentamento dell'economia — il mandato primario di stabilità dei prezzi (inflazione al 10.6% nel picco ottobre 2022) ha prevalso anche a costo di crescita più bassa e maggior sofferenza per debitori a tasso variabile",
                        "C) La BCE e la Fed hanno coordinato le decisioni di politica monetaria per evitare effetti di spill-over",
                        "D) Il Trattato di Lisbona ha modificato la gerarchia nel 2009 — ora occupazione e crescita hanno uguale peso rispetto all'inflazione"],
            "corretta": 1,
            "spiegazione": "IL CICLO MONETARIO 2022-2023 — il più aggressivo della storia BCE: CONTESTO: inflazione HICP area euro passa da 2.6% (giugno 2021) a 10.6% (ottobre 2022) — massimo storico. CAUSE: supply-side (energia +41% YoY dopo invasione Russia-Ucraina, agosto 2022) + demand-side (riapertura post-COVID) + seconda rotonda effetti (salari rincorrono i prezzi). RISPOSTA BCE: luglio 2022 — primo rialzo dal 2011, +50bps (inizio del ciclo). 10 rialzi consecutivi fino a settembre 2023 → DFR = 4%. Velocità senza precedenti: da −0.5% a +4% in 14 mesi (+450bps). IMPATTO MANDATO SECONDARIO: crescita dell'area euro quasi piatta nel 2023; Germania in recessione tecnica nel 2022-23. I mutui a tasso variabile (Euribor + spread) sono passati da ~1-2% a ~5-6% → forte aumento degli oneri finanziari delle famiglie italiane. IL DIBATTITO: alcuni membri del Consiglio (Italia, Francia) avrebbero preferito rialzi più graduali. I falchi (Germania, Olanda, Austria) hanno prevalso per via dell'inflazione alta — coerente con la gerarchia del mandato. Prima taglio tassi: giugno 2024 (−25bps) quando l'inflazione era tornata al ~2.6%."
          },
          {
            "testo": "Il Trilemma di Mundell-Fleming (Impossibile Trinity) afferma che non si possono avere simultaneamente: libera circolazione dei capitali + tasso di cambio fisso + politica monetaria autonoma. Come si applica all'Eurozona?",
            "opzioni": ["A) L'Eurozona viola il trilemma — ha tutti e tre contemporaneamente grazie all'unione politica",
                        "B) I paesi dell'Eurozona hanno rinunciato alla politica monetaria autonoma (è della BCE) per mantenere la libera circolazione dei capitali e il tasso di cambio fisso (l'euro — cambio fisso tra i paesi membri). È la scelta ottimale per mercati integrati, ma priva i governi nazionali dello strumento monetario per rispondere a shock asimmetrici",
                        "C) L'Eurozona ha rinunciato alla libera circolazione dei capitali — i movimenti di capitale cross-border sono regolamentati dalla BCE",
                        "D) Il trilemma di Mundell-Fleming si applica solo ai paesi con regime di currency board, non all'Eurozona"],
            "corretta": 1,
            "spiegazione": "TRILEMMA E AREA EURO: I tre obiettivi incompatibili: Libera circolazione dei capitali — i capitali si muovono liberamente tra Germania e Italia, senza controlli. Tasso di cambio fisso — l'euro elimina il rischio di cambio intra-area. Politica monetaria autonoma — un unico tasso BCE per tutti i 20 paesi. La SCELTA dell'Eurozona: mantenere (1) e (2), rinunciare a (3). PERCHÉ È IMPORTANTE: prima dell'euro, l'Italia usava la lira per aggiustare gli squilibri di competitività → svalutazione → export più competitivi. Con l'euro, la valvola di aggiustamento della svalutazione è scomparsa → l'aggiustamento deve avvenire tramite deflazione dei prezzi/salari (aggiustamento doloroso e lento) o mobilità del lavoro (scarsa in Europa). SHOCK ASIMMETRICO: se la Germania cresce al 3% e l'Italia è in recessione, la politica BCE deve scegliere un tasso che è troppo alto per l'Italia e troppo basso per la Germania → il tasso 'one size fits all' non è ottimale per tutti. L'OCA theory (Optimal Currency Area — Mundell) definisce le condizioni per cui una valuta comune è ottimale: alta mobilità del lavoro, mercati integrati, meccanismi di trasferimento fiscale. L'Eurozona soddisfa solo parzialmente questi criteri."
          }
        ]
      },
      {
        "id": "P2", "titolo": "Strumenti e Trasmissione Monetaria",
        "desc": "MRO, LTRO/TLTRO, QE/APP/PEPP, canali di trasmissione, inflazione 2021-23",
        "xp": 130,
        "domande": [
          {
            "testo": "Il QE (Quantitative Easing) della BCE attraverso il programma APP ha acquistato €3.3 trilioni di titoli dal 2015 al 2022. Attraverso quale canale principale ha impattato l'economia reale?",
            "opzioni": ["A) Canale diretto: la BCE ha trasferito direttamente la moneta creata alle famiglie italiane",
                        "B) Canale 'portfolio rebalancing': comprando BTP e obbligazioni corporate, la BCE spinge gli investitori verso attività più rischiose (azioni, credito corporate, real estate) riducendo i rendimenti ovunque → condizioni finanziarie più accomodanti → investimenti e consumi aumentano. Anche canale del tasso di cambio (euro più debole → export).",
                        "C) Canale bancario diretto: i fondi QE vengono girati automaticamente alle banche che li prestano alle imprese",
                        "D) Il QE non ha canali di trasmissione all'economia reale — è puramente un effetto contabile sulle riserve bancarie"],
            "corretta": 1,
            "spiegazione": "MECCANISMI DI TRASMISSIONE DEL QE: (1) PORTFOLIO REBALANCING (canale principale): la BCE compra BTP → prezzi BTP salgono, rendimenti scendono → i detentori (banche, fondi) vendono BTP alla BCE e reinvestono in asset più rischiosi (corporate bond, azioni, immobili) → prezzi di tutti gli asset salgono, rendimenti scendono → wealth effect per le famiglie → riduzione del costo del capitale per le imprese. (2) TASSO DI CAMBIO: maggiore offerta di euro sul mercato → euro si svaluta → export più competitivi → crescita. (3) ASPETTATIVE: il commitment al QE segnala che i tassi rimarranno bassi a lungo → le imprese e le famiglie investono e consumano di più ora. (4) CREDIT CHANNEL: minori rendimenti sui govies spingono le banche a fare più credito alle imprese per ottenere rendimenti accettabili. CRITICHE AL QE: (5) Distribuzione dei benefici: chi possiede più asset (i ricchi) beneficia di più dell'aumento dei prezzi → il QE aumenta la disuguaglianza patrimoniale. (6) Bolle degli asset: i prezzi immobiliari e azionari raggiunti livelli record nel periodo 2015-2021. (7) 'Zombification': tassi bassi artificialmente permettono sopravvivenza di aziende non competitive (zombie firms) che usano risorse improduttivamente."
          },
          {
            "testo": "La 'forward guidance' della BCE è uno strumento di politica monetaria non convenzionale basato sulla comunicazione. Come funziona e quando è più efficace?",
            "opzioni": ["A) La forward guidance funziona come annuncio legalmente vincolante del tasso BCE futuro — le banche sono obbligate ad adeguarsi",
                        "B) La forward guidance comunica le intenzioni future di politica monetaria ('i tassi rimarranno bassi per un lungo periodo') influenzando le aspettative di mercato oggi — più credibile è la banca centrale, più i mercati scontano i tassi futuri abbassando i rendimenti a lungo termine già oggi senza che la BCE debba agire ulteriormente",
                        "C) La forward guidance sostituisce completamente le decisioni di tasso — la BCE non decide più il tasso ma solo comunica la direzione",
                        "D) La forward guidance è efficace solo nei periodi di alta inflazione quando i mercati non si fidano delle proiezioni BCE"],
            "corretta": 1,
            "spiegazione": "FORWARD GUIDANCE — la comunicazione come strumento di policy: Bernanke (2013): 'Monetary policy is 98% talk and only 2% action.' Perché funziona: se la BCE dice 'i tassi rimarranno bassi almeno fino al 2025', le banche possono fare prestiti a lungo termine oggi a tassi bassi sapendo che il costo del funding rimarrà basso. I mercati scontano i tassi futuri → la yield curve lunga scende → condizioni finanziarie si allentano anche senza toccare il tasso overnight. TIPI DI FORWARD GUIDANCE: Open-ended: 'i tassi rimarranno bassi per un lungo periodo' (vaga, meno credibile). Calendar-based: 'fino a giugno 2024' (più credibile, ma se le condizioni cambiano la BCE è in difficoltà). State-contingent: 'fino a quando l'inflazione non sarà stabilmente al 2%' (più flessibile, BCE post-review 2021 usa questa). CREDIBILITY IS KEY: la forward guidance funziona solo se la banca centrale è credibile. Se i mercati non credono che la BCE manterrà i tassi bassi → scontano già rialzi → la guidance fallisce. Nel 2021, la BCE ha comunicato che l'inflazione era 'transitoria' e i tassi sarebbero rimasti bassi → poi ha dovuto ritrattare bruscamente nel 2022 → danno alla credibilità della guidance futura."
          },
          {
            "testo": "L'inflazione italiana 2021-2023: l'inflazione HICP è passata da 0.7% (2020) a 8.9% (2022). Quali componenti hanno contribuito e perché l'inflazione dei SERVIZI è stata più persistente dell'inflazione ENERGETICA?",
            "opzioni": ["A) L'inflazione dei servizi è scesa prima di quella energetica — i servizi hanno catene di fornitura più corte",
                        "B) L'inflazione energetica (gas, elettricità) è salita e scesa rapidamente (volatile, supply-driven); l'inflazione dei servizi (ristorazione, trasporti, turismo) è più inerziale perché trainata dai salari che si adeguano con ritardo — una volta aumentati i salari, i prezzi dei servizi rimangono alti ('second-round effects')",
                        "C) Non c'è differenza di persistenza — sia energia che servizi hanno seguito lo stesso pattern temporale",
                        "D) L'inflazione dei servizi è scesa prima grazie agli effetti delle policy fiscali italiane (bonus vari, calmierazioni)"],
            "corretta": 1,
            "spiegazione": "ANATOMY OF EURO AREA INFLATION 2021-2023: FASE 1 (2021-22) — ENERGY-DRIVEN: gas naturale +300% in Europa. Componente energy HICP: +44.3% (ottobre 2022). Causa: invasione Russia-Ucraina (febbraio 2022) + riduzione forniture Gazprom. Questo è inflazione di offerta (supply shock) — la banca centrale non può combattere facilmente la scarsità di gas alzando i tassi. FASE 2 (2022-23) — CORE INFLATION persistente: core HICP (ex energia e food) ha raggiunto il picco di 5.7% nel marzo 2023, scendendo lentamente. SERVIZI: la ristorazione, l'ospitalità, i trasporti hanno alzato i prezzi per recuperare i margini erosi dall'energia. I SALARI hanno iniziato a salire (nel 2022-23) per inseguire l'inflazione → second-round effects. I contratti collettivi italiani (CCNL) vengono rinegoziati con ritardo (ogni 3 anni) → i salari salgono dopo l'inflazione, mantenendola alta più a lungo. IMPLICAZIONE: la BCE ha dovuto mantenere i tassi alti più a lungo del previsto perché l'inflazione core (servizi + alimentari) è rimasta ben sopra il 2% anche quando l'energia era tornata a livelli normali. Dicembre 2023: core inflazione ~3.4%, energy in deflazione — un mix complesso per il Consiglio Direttivo."
          }
        ]
      },
      {
        "id": "P3", "titolo": "◈ BOSS — Politica Non Convenzionale e Futuro",
        "desc": "⚔ PEPP, OMT, TPI, CBDC, tassi negativi, review strategia BCE",
        "xp": 200, "boss": True,
        "domande": [
          {
            "testo": "Il TPI (Transmission Protection Instrument, luglio 2022) è lo strumento più recente della BCE per combattere la frammentazione dei mercati. Come funziona e in cosa differisce dall'OMT (2012)?",
            "opzioni": ["A) TPI e OMT sono identici — solo il nome è cambiato",
                        "B) TPI: acquisti illimitati e non sterilizzati di titoli sovrani di un paese specifico per prevenire la frammentazione 'ingiustificata' — attivabile UNILATERALMENTE dalla BCE (no condizionalità ESM richiesta). OMT: condizionato a un programma ESM/MES. Il TPI rimuove la condizionalità politica e può essere attivato più rapidamente",
                        "C) Il TPI acquista solo corporate bond, l'OMT solo titoli di Stato",
                        "D) Il TPI è attivato automaticamente quando lo spread BTP-Bund supera 200bps — è un meccanismo automatico"],
            "corretta": 1,
            "spiegazione": "TPI vs OMT — evoluzione degli strumenti anti-frammentazione: OMT (settembre 2012 — Draghi): Acquisti ILLIMITATI ma STERILIZZATI (la liquidità viene ritirata per evitare espansione M3). CONDIZIONATO: il paese deve fare richiesta al MES (ESM) e accettare il programma di aggiustamento. MAI UTILIZZATO: il solo annuncio fu sufficiente. TPI (luglio 2022 — Lagarde): Acquisti ILLIMITATI e NON STERILIZZATI (espansione del bilancio BCE). CONDIZIONALITÀ SEMPLIFICATA: il paese deve rispettare il Patto di Stabilità, non avere 'squilibri macroeconomici gravi', non essere in programma ESM. Attivabile UNILATERALMENTE dalla BCE — nessun paese può bloccare l'attivazione. SCOPE: può comprare titoli sovrani con scadenza 1-10 anni, anche corporate bonds in alcuni casi. RATIO: nato per proteggere la trasmissione del rialzo dei tassi (estate 2022 lo spread BTP era esploso a 250bps) senza che fosse necessaria la condizionalità ESM (politicamente insostenibile per un governo italiano in carica). ANCORA MAI UTILIZZATO: l'annuncio dell'OMT nel 2012 e del TPI nel 2022 sono stati entrambi sufficienti. Il 'Powell Put' europeo — la BCE come backstop dei mercati sovrani."
          },
          {
            "testo": "Le CBDC (Central Bank Digital Currency) — la BCE sta sviluppando l'euro digitale. Quale impatto strutturale potrebbe avere sul sistema bancario europeo?",
            "opzioni": ["A) Le CBDC non hanno impatto sul sistema bancario — sono solo una versione digitale delle banconote",
                        "B) Se i cittadini detengono direttamente euro digitali presso la BCE, potrebbero bypassare le banche commerciali per conservare i propri risparmi → disintermediazione bancaria: le banche perderebbero una parte del deposito funding, riducendo la propria capacità di fare credito. La BCE sta considerando limiti massimi di detenzione (€3.000 per individuo) proprio per evitare questo rischio",
                        "C) Le CBDC rafforzerebbero il sistema bancario perché sarebbero distribuite attraverso le banche commerciali",
                        "D) Le CBDC sostituirebbero completamente la moneta fisica entro il 2030 secondo il piano BCE"],
            "corretta": 1,
            "spiegazione": "EURO DIGITALE (e-euro) — BCE project lancio: da ottobre 2023 in fase preparatoria, emissione stimata non prima del 2026-2028. COSA È: passività diretta della BCE (come le banconote) in forma digitale, detenibile da individui e imprese. COSA NON È: non è una criptovaluta (è centralizzata), non è anonima (traceabile per antiriciclaggio), non è un investimento (nessun interesse). RISCHIO DISINTERMEDIAZIONE: se tutti convertissero i propri depositi bancari in e-euro → le banche perderebbero il funding → dovrebbero raccogliere più fondi sul mercato wholesale a costi più alti → meno credito o credito più costoso → credit crunch. MITIGAZIONE BCE: limite di detenzione individuale proposto: €3.000 (come per il portafoglio fisico) — abbastanza per i pagamenti quotidiani, troppo poco per i risparmi → minimizza la concorrenza con i depositi bancari. SCENARIO DI BANK RUN DIGITALE: in una crisi, i cittadini potrebbero trasferire in secondi i propri depositi in e-euro (safe asset garantito dallo Stato) → amplificatore delle crisi bancarie → serve una 'circuit breaker'. Il design dell'euro digitale è la questione architetturale più rilevante dell'industria finanziaria europea per il prossimo decennio."
          }
        ]
      }
    ]
  }
}

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def get_livello(xp):
    thresholds = [(0,"Matricola 📖"),(150,"Analista Trainee 📊"),(400,"Junior Analyst 📈"),
                  (800,"Associate 💼"),(1400,"Vice President 🏛"),(2200,"Director ◈"),(3200,"Managing Director 🎩"),(4500,"Partner & Legend 🏆")]
    for thresh, title in reversed(thresholds):
        if xp >= thresh: return thresholds.index((thresh,title))+1, title
    return 1, "Matricola 📖"

def xp_next_thresh(xp):
    thresholds = [0,150,400,800,1400,2200,3200,4500,99999]
    for t in thresholds:
        if xp < t: return t
    return 99999

def mid(area, idx): return f"{area}_{idx}"
def is_done(area, idx): return mid(area, idx) in st.session_state.completate

def check_badges():
    xp = st.session_state.xp; mc = st.session_state.completate; b = st.session_state.badge; new = []
    def add(bid, em, nm, ds):
        if bid not in b: new.append((em, nm, ds)); b.append(bid)
    if xp >= 150: add("lv2","📊","Analista Trainee","150 XP raggiunta!")
    if xp >= 400: add("lv3","📈","Junior Analyst","400 XP raggiunta!")
    if xp >= 800: add("lv4","💼","Associate","800 XP raggiunta!")
    if xp >= 1400:add("lv5","🏛","Vice President","1400 XP!")
    if xp >= 2200:add("lv6","◈","Director","2200 XP — Élite!")
    if xp >= 3200:add("lv7","🎩","Managing Director","3200 XP — Leggendario!")
    for ak, av in MISSIONS.items():
        n = len(av["livelli"])
        if sum(1 for m in mc if ak in m) >= n:
            add(f"{ak}_m", av["emoji"], f"Master: {av['nome']}", "Area completata!")
    if len(mc) >= sum(len(v["livelli"]) for v in MISSIONS.values()):
        add("champ","🏆","Grand Champion","Tutto il corso completato!")
    if st.session_state.streak >= 5: add("fire","🔥","On Fire","5 consecutive!")
    if st.session_state.streak >= 10: add("inferno","⚡","Inferno","10 consecutive!")
    return new

# ─── SESSION ──────────────────────────────────────────────────────────────────
def init():
    d = dict(nome="", registrato=False, xp=0, completate=[], area=None, liv=None,
             qidx=0, risposta=None, score=0, fase="home", streak=0, badge=[])
    for k,v in d.items():
        if k not in st.session_state: st.session_state[k] = v
init()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:24px 16px 16px;">
      <div style="font-family:'DM Serif Display',serif;font-size:2rem;color:#F5F0E8;line-height:1;margin-bottom:2px;">FinQuest</div>
      <div style="font-family:'DM Mono',monospace;font-size:0.58rem;color:#5C3D8A;letter-spacing:3px;text-transform:uppercase;">EIF 2026 — Accademia</div>
      <div style="margin-top:12px;height:1px;background:linear-gradient(90deg,rgba(201,168,76,0.4),transparent);"></div>
    </div>""", unsafe_allow_html=True)

    if st.session_state.registrato:
        lv, titolo = get_livello(st.session_state.xp)
        xn = xp_next_thresh(st.session_state.xp)
        xp2 = [0,150,400,800,1400,2200,3200,4500][min(lv-1,7)]
        prog = min((st.session_state.xp - xp2) / max(xn - xp2, 1), 1.0)
        tm = sum(len(v["livelli"]) for v in MISSIONS.values())
        tc = len(st.session_state.completate)

        st.markdown(f"""
        <div style="padding:4px 16px 16px;">
          <div style="color:#8A94A6;font-family:'DM Mono',monospace;font-size:0.6rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:2px;">Studente</div>
          <div style="color:#F5F0E8;font-weight:700;font-size:1rem;margin-bottom:1px;">{st.session_state.nome}</div>
          <div style="color:#C9A84C;font-family:'DM Mono',monospace;font-size:0.68rem;margin-bottom:14px;">{titolo}</div>

          <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
            <span style="color:#5C6878;font-family:'DM Mono',monospace;font-size:0.58rem;letter-spacing:1.5px;text-transform:uppercase;">Progressione</span>
            <span style="color:#C9A84C;font-family:'DM Mono',monospace;font-size:0.68rem;">{st.session_state.xp} xp</span>
          </div>
          <div class="xp-track"><div class="xp-fill" style="width:{prog*100:.0f}%;"></div></div>
          <div style="color:#3D4A5C;font-family:'DM Mono',monospace;font-size:0.58rem;margin-top:4px;">{xn - st.session_state.xp} xp al prossimo livello</div>

          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-top:14px;">
            {''.join([f'<div style="background:#0D101A;border:1px solid rgba(201,168,76,0.1);border-radius:3px;padding:8px 4px;text-align:center;"><div style="font-family:DM Serif Display,serif;font-size:1.2rem;color:{c};">{v}</div><div style="font-family:DM Mono,monospace;font-size:0.55rem;color:#3D4A5C;text-transform:uppercase;letter-spacing:1px;margin-top:1px;">{l}</div></div>' for v,l,c in [(f"Lv.{lv}","Livello","#C9A84C"),(f"{tc}/{tm}","Quest","#2A7B7C"),(f"{st.session_state.streak}🔥","Streak","#C4522A")]])}
          </div>
        </div>
        <div style="margin:4px 16px;height:1px;background:rgba(201,168,76,0.08);"></div>""", unsafe_allow_html=True)

        for ico, lbl, fase in [("◈","Mappa Missioni","home"),("▲","Classifica","leaderboard"),("◉","Profilo","profilo")]:
            if st.button(f"{ico}  {lbl}", key=f"nav_{fase}", use_container_width=True):
                st.session_state.fase = fase; st.rerun()

        if st.session_state.badge:
            bmap = {"lv2":"📊","lv3":"📈","lv4":"💼","lv5":"🏛","lv6":"◈","lv7":"🎩","champ":"🏆","fire":"🔥","inferno":"⚡",
                    **{f"{ak}_m":av["emoji"] for ak,av in MISSIONS.items()}}
            icons = " ".join([f'<span style="font-size:1rem;">{bmap.get(b,"🎖")}</span>' for b in st.session_state.badge])
            st.markdown(f'<div style="padding:8px 16px;"><div style="font-family:DM Mono,monospace;font-size:0.55rem;color:#3D4A5C;text-transform:uppercase;letter-spacing:2px;margin-bottom:5px;">Badge</div><div style="display:flex;flex-wrap:wrap;gap:3px;">{icons}</div></div>', unsafe_allow_html=True)

# ─── REGISTRAZIONE ────────────────────────────────────────────────────────────
if not st.session_state.registrato:
    now = datetime.now()
    tm = sum(len(v["livelli"]) for v in MISSIONS.values())
    tq = sum(len(q["domande"]) for v in MISSIONS.values() for q in v["livelli"])
    tx = sum(v["xp_totale"] for v in MISSIONS.values())

    st.markdown(f"""
    <div class="masthead">
      <div class="masthead-date">{now.strftime("%A, %d %B %Y")} — Anno Accademico 2025/2026</div>
      <div class="masthead-title">FinQuest</div>
      <div class="masthead-rule"><span style="font-family:'DM Mono',monospace;font-size:0.6rem;color:#C9A84C;letter-spacing:4px;">ECONOMIA DEGLI INTERMEDIARI FINANZIARI</span></div>
      <div class="masthead-subtitle">Il gioco di apprendimento del corso EIF — Università La Sapienza</div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(f"""
        <div style="background:#0D101A;border:1px solid rgba(201,168,76,0.15);border-radius:4px;padding:40px 36px;margin-bottom:20px;">
          <div style="font-family:'DM Serif Display',serif;font-size:1.6rem;color:#F5F0E8;margin-bottom:8px;line-height:1.2;">
            L'Accademia della Finanza
          </div>
          <div style="font-family:'DM Mono',monospace;font-size:0.72rem;color:#8A94A6;line-height:1.9;margin-bottom:28px;">
            Affronta missioni su tutto il programma EIF: dal sistema finanziario<br>
            alla politica monetaria, dal bilancio bancario ai mercati mobiliari.<br>
            Scala i livelli, conquista badge, scala la classifica.
          </div>
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:28px;">
            {''.join([f'<div style="border:1px solid rgba(201,168,76,0.12);border-top:2px solid {c};border-radius:3px;padding:14px 10px;text-align:center;"><div style="font-family:DM Serif Display,serif;font-size:1.8rem;color:{c};">{v}</div><div style="font-family:DM Mono,monospace;font-size:0.58rem;color:#3D4A5C;text-transform:uppercase;letter-spacing:1.5px;margin-top:3px;">{l}</div></div>' for v,l,c in [(len(MISSIONS),"Aree","#C9A84C"),(tm,"Missioni","#2A7B7C"),(tq,"Domande","#C4522A"),(tx,"XP Max","#5C3D8A")]])}
          </div>
          <div style="height:1px;background:rgba(201,168,76,0.08);margin-bottom:20px;"></div>
        </div>""", unsafe_allow_html=True)

        nome = st.text_input("", placeholder="Il tuo nome e cognome...", label_visibility="collapsed")
        if st.button("◈  Accedi all'Accademia", use_container_width=True):
            if nome.strip():
                st.session_state.nome = nome.strip(); st.session_state.registrato = True
                save_progress(); st.rerun()
            else: st.warning("Inserisci il tuo nome per continuare.")

# ─── HOME ─────────────────────────────────────────────────────────────────────
elif st.session_state.fase == "home":
    lv, titolo = get_livello(st.session_state.xp)
    tm = sum(len(v["livelli"]) for v in MISSIONS.values())
    tc = len(st.session_state.completate)

    st.markdown(f"""
    <div class="masthead" style="margin-bottom:28px;">
      <div class="masthead-date">Mappa delle Missioni — {datetime.now().strftime("%d %B %Y")}</div>
      <div style="display:flex;align-items:baseline;gap:20px;flex-wrap:wrap;">
        <div class="masthead-title" style="font-size:3rem;">{st.session_state.nome}</div>
        <div>
          <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#C9A84C;letter-spacing:2px;">{titolo}</div>
          <div style="font-family:'DM Mono',monospace;font-size:0.6rem;color:#3D4A5C;">{tc}/{tm} missioni · {st.session_state.xp} XP</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    COLORS = {"gold":"#C9A84C","blue":"#2C5F8A","teal":"#2A7B7C","rust":"#C4522A","purple":"#5C3D8A"}

    for ak, av in MISSIONS.items():
        done_c = sum(1 for m in st.session_state.completate if ak in m)
        tot_c = len(av["livelli"])
        acc = COLORS.get(av["colore"], "#C9A84C")
        pct = done_c / tot_c

        st.markdown(f"""
        <div style="margin:32px 0 14px;">
          <div style="display:flex;align-items:center;gap:14px;">
            <div style="font-family:'DM Serif Display',serif;font-size:1.6rem;color:{acc};">{av['emoji']}</div>
            <div style="flex:1;">
              <div style="font-family:'DM Serif Display',serif;font-size:1.2rem;color:#F5F0E8;">{av['nome']}</div>
              <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#5C6878;margin-top:1px;">{av['desc']}</div>
            </div>
            <div style="text-align:right;">
              <div style="font-family:'DM Mono',monospace;font-size:0.75rem;color:{acc};">{done_c}/{tot_c}</div>
              <div style="width:80px;margin-top:4px;"><div class="xp-track" style="height:2px;"><div style="height:100%;width:{pct*100:.0f}%;background:{acc};border-radius:1px;"></div></div></div>
            </div>
          </div>
          <div style="height:1px;background:linear-gradient(90deg,{acc}30,transparent);margin-top:10px;"></div>
        </div>""", unsafe_allow_html=True)

        cols = st.columns(len(av["livelli"]))
        for i, ld in enumerate(av["livelli"]):
            with cols[i]:
                comp = is_done(ak, i)
                boss = ld.get("boss", False)
                lock = i > 0 and not is_done(ak, i-1)
                border_c = "#2E7D52" if comp else ("#C4522A55" if boss else f"{acc}25")
                bg_c = "#060E09" if comp else ("#130A06" if boss else "#0D101A")
                ico = "✓" if comp else ("⚔" if boss else ("◌" if lock else "▶"))
                ico_c = "#2E7D52" if comp else ("#C4522A" if boss else ("#3D4A5C" if lock else acc))
                num = ld.get("id","?")
                boss_anim = "boss-flicker" if boss and not lock and not comp else ""

                st.markdown(f"""
                <div class="mission-tile {boss_anim}" style="background:{bg_c};border:1px solid {border_c};opacity:{'0.32' if lock else '1'};">
                  <div class="deco-num">{num}</div>
                  <div style="font-family:'DM Mono',monospace;font-size:1rem;color:{ico_c};margin-bottom:8px;">{ico}</div>
                  <div style="font-family:'DM Serif Display',serif;font-size:0.85rem;color:#C8C0B0;line-height:1.4;margin-bottom:6px;">{ld['titolo']}</div>
                  <div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#3D4A5C;line-height:1.5;margin-bottom:10px;">{ld['desc'][:55]}{'…' if len(ld['desc'])>55 else ''}</div>
                  <div style="font-family:'DM Mono',monospace;font-size:0.68rem;color:{acc};">+{ld['xp']} xp</div>
                </div>""", unsafe_allow_html=True)

                if not lock and not comp:
                    lbl = "⚔  Boss Fight" if boss else "▶  Inizia"
                    if st.button(lbl, key=f"p_{ak}_{i}", use_container_width=True):
                        st.session_state.area=ak; st.session_state.liv=i
                        st.session_state.qidx=0; st.session_state.risposta=None
                        st.session_state.score=0; st.session_state.fase="quiz"; st.rerun()
                elif comp:
                    if st.button("◌  Rigioca", key=f"r_{ak}_{i}", use_container_width=True):
                        st.session_state.area=ak; st.session_state.liv=i
                        st.session_state.qidx=0; st.session_state.risposta=None
                        st.session_state.score=0; st.session_state.fase="quiz"; st.rerun()
                else:
                    st.button("◌  Bloccato", key=f"l_{ak}_{i}", use_container_width=True, disabled=True)

# ─── QUIZ ────────────────────────────────────────────────────────────────────
elif st.session_state.fase == "quiz":
    ak=st.session_state.area; li=st.session_state.liv
    av=MISSIONS[ak]; ld=av["livelli"][li]
    qs=ld["domande"]; qi=st.session_state.qidx
    boss=ld.get("boss",False); acc=COLORS.get(av["colore"],"#C9A84C") if "COLORS" in dir() else "#C9A84C"
    COLORS2 = {"gold":"#C9A84C","blue":"#2C5F8A","teal":"#2A7B7C","rust":"#C4522A","purple":"#5C3D8A"}
    acc = COLORS2.get(av["colore"],"#C9A84C")

    c_back, _ = st.columns([1,5])
    with c_back:
        if st.button("← Mappa", key="bk"):
            st.session_state.fase = "home"; st.rerun()

    st.markdown(f"""
    <div style="margin:12px 0 20px;">
      <div style="font-family:'DM Mono',monospace;font-size:0.6rem;color:{acc};letter-spacing:2px;text-transform:uppercase;margin-bottom:3px;">
        {av['emoji']} {av['nome']} › {ld['titolo']}
      </div>
      <div style="font-family:'DM Serif Display',serif;font-size:1.75rem;color:#F5F0E8;">
        {'⚔ Boss Fight' if boss else f'Domanda {qi+1} di {len(qs)}'}
      </div>
    </div>
    <div class="xp-track" style="margin-bottom:24px;height:2px;">
      <div style="height:100%;width:{qi/len(qs)*100:.0f}%;background:{'linear-gradient(90deg,#C4522A,#E8C876)' if boss else f'linear-gradient(90deg,{acc},{acc}88)'};border-radius:1px;transition:width .5s;"></div>
    </div>""", unsafe_allow_html=True)

    if qi < len(qs):
        q = qs[qi]
        cq, ci = st.columns([3, 1])
        with cq:
            bc = "rgba(196,82,42,0.2)" if boss else f"rgba(201,168,76,0.08)"
            bl = "#C4522A" if boss else acc
            st.markdown(f"""
            <div style="background:#0D101A;border:1px solid {bc};border-left:3px solid {bl};border-radius:3px;padding:28px;margin-bottom:20px;">
              <div style="font-family:'Outfit',sans-serif;font-size:0.95rem;color:#C8C0B0;line-height:1.85;">{q['testo']}</div>
            </div>""", unsafe_allow_html=True)

            if st.session_state.risposta is None:
                for j, opt in enumerate(q["opzioni"]):
                    if st.button(opt, key=f"o{j}", use_container_width=True):
                        st.session_state.risposta = j
                        if j == q["corretta"]: st.session_state.score += 1
                        st.rerun()
            else:
                sc2 = st.session_state.risposta; co = q["corretta"]
                if sc2 == co:
                    st.markdown(f'<div class="fb-correct fade-up"><div style="font-family:DM Mono,monospace;font-size:0.72rem;letter-spacing:2px;color:#2E7D52;text-transform:uppercase;margin-bottom:10px;">✓ Risposta corretta</div><div style="color:#A7C4A0;font-size:0.88rem;line-height:1.8;">{q["spiegazione"]}</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="fb-wrong fade-up"><div style="font-family:DM Mono,monospace;font-size:0.72rem;letter-spacing:2px;color:#C4522A;text-transform:uppercase;margin-bottom:8px;">✗ Non corretto</div><div style="color:#C4522A;font-size:0.82rem;margin-bottom:10px;">Risposta esatta: <strong style="color:#E8C876;">{q["opzioni"][co]}</strong></div><div style="color:#A09080;font-size:0.84rem;line-height:1.8;">{q["spiegazione"]}</div></div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                nl = "Prossima  →" if qi < len(qs)-1 else "Risultato  ◈"
                if st.button(nl, key="nx", use_container_width=True):
                    st.session_state.qidx += 1; st.session_state.risposta = None
                    if st.session_state.qidx >= len(qs): st.session_state.fase = "risultato"
                    st.rerun()

        with ci:
            for val,lbl,c in [(f"+{ld['xp']}","XP in palio","#C9A84C"),(f"{st.session_state.score}/{qi}","Corrette","#2A7B7C"),(st.session_state.xp,"XP Totali","#5C3D8A")]:
                st.markdown(f'<div style="background:#0D101A;border:1px solid rgba(201,168,76,0.1);border-radius:3px;padding:16px;text-align:center;margin-bottom:8px;"><div style="font-family:DM Serif Display,serif;font-size:1.6rem;color:{c};">{val}</div><div style="font-family:DM Mono,monospace;font-size:0.58rem;color:#3D4A5C;text-transform:uppercase;letter-spacing:1.5px;margin-top:3px;">{lbl}</div></div>', unsafe_allow_html=True)

# ─── RISULTATO ────────────────────────────────────────────────────────────────
elif st.session_state.fase == "risultato":
    ak=st.session_state.area; li=st.session_state.liv
    ld=MISSIONS[ak]["livelli"][li]; sc=st.session_state.score; tot=len(ld["domande"])
    pct=sc/tot; boss=ld.get("boss",False); xpb=ld["xp"]
    if pct==1.0: xpg=xpb; ri="◈"; rt="Prestazione Perfetta"; c="#C9A84C"; st2="★★★"
    elif pct>=.67: xpg=int(xpb*.7); ri="▶"; rt="Missione Superata"; c="#2A7B7C"; st2="★★"
    else: xpg=int(xpb*.3); ri="◌"; rt="Risultato Insufficiente"; c="#C4522A"; st2="★"
    m=mid(ak,li); done=m in st.session_state.completate
    if pct>=.67 and not done:
        st.session_state.completate.append(m); st.session_state.xp+=xpg; st.session_state.streak+=1
    elif pct<.67:
        st.session_state.streak=0; st.session_state.xp+=xpg
    nb=check_badges(); save_progress()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        st.markdown(f"""
        <div style="background:#0D101A;border:1px solid {c}25;border-top:3px solid {c};border-radius:3px;padding:44px;text-align:center;margin-bottom:16px;" class="fade-up">
          <div style="font-family:'DM Mono',monospace;font-size:1.8rem;color:{c};margin-bottom:10px;">{st2}</div>
          <div style="font-family:'DM Serif Display',serif;font-size:2rem;color:#F5F0E8;margin-bottom:5px;">{rt}</div>
          <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:#3D4A5C;letter-spacing:2px;margin-bottom:30px;">{'⚔ BOSS SCONFITTO' if boss and pct>=.67 else ld['titolo'].upper()}</div>
          <div style="display:flex;justify-content:center;gap:48px;">
            {''.join([f'<div><div style="font-family:DM Serif Display,serif;font-size:2.8rem;color:{col};line-height:1;">{v}</div><div style="font-family:DM Mono,monospace;font-size:0.6rem;color:#3D4A5C;text-transform:uppercase;letter-spacing:2px;margin-top:3px;">{l}</div></div>' for v,l,col in [(f"{sc}/{tot}","Corrette",c),(f"+{xpg}","XP","#C9A84C"),(st.session_state.xp,"Totale","#5C3D8A")]])}
          </div>
        </div>""", unsafe_allow_html=True)
        for em,nm,ds in nb:
            st.markdown(f'<div style="background:#100D00;border:1px solid rgba(201,168,76,0.3);border-top:2px solid #C9A84C;border-radius:3px;padding:18px;text-align:center;margin-bottom:10px;" class="fade-up"><div style="font-size:1.8rem;margin-bottom:5px;">{em}</div><div style="font-family:DM Serif Display,serif;color:#C9A84C;font-size:1rem;">Badge: {nm}</div><div style="font-family:DM Mono,monospace;font-size:0.65rem;color:#5C4A20;margin-top:3px;">{ds}</div></div>', unsafe_allow_html=True)
        cc1,cc2,cc3=st.columns(3)
        with cc1:
            if st.button("◌  Riprova", use_container_width=True):
                st.session_state.qidx=0; st.session_state.risposta=None; st.session_state.score=0; st.session_state.fase="quiz"; st.rerun()
        with cc2:
            if st.button("◈  Mappa", use_container_width=True): st.session_state.fase="home"; st.rerun()
        with cc3:
            if st.button("▲  Classifica", use_container_width=True): st.session_state.fase="leaderboard"; st.rerun()

# ─── LEADERBOARD ─────────────────────────────────────────────────────────────
elif st.session_state.fase == "leaderboard":
    st.markdown(f"""
    <div class="masthead" style="margin-bottom:28px;">
      <div class="masthead-date">Classifica Generale — {datetime.now().strftime("%d %B %Y")}</div>
      <div class="masthead-title" style="font-size:2.5rem;">Leaderboard</div>
    </div>""", unsafe_allow_html=True)
    c1,c2=st.columns([1,3])
    with c1:
        if st.button("◌  Aggiorna", use_container_width=True): st.rerun()
    with c2:
        st.markdown('<div style="background:#0D101A;border:1px solid rgba(201,168,76,0.1);border-radius:3px;padding:10px 14px;color:#3D4A5C;font-family:DM Mono,monospace;font-size:0.7rem;">Configura Firebase per la classifica condivisa. Senza configurazione mostra solo il giocatore corrente.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    entries = get_leaderboard()
    if not entries and st.session_state.xp > 0:
        lv,tit=get_livello(st.session_state.xp)
        entries=[{"nome":st.session_state.nome,"xp":st.session_state.xp,"missioni":len(st.session_state.completate),"streak":st.session_state.streak,"badge":len(st.session_state.badge),"livello":lv,"titolo":tit}]
    medals=["◈","▲","◉"]; mcol=["#C9A84C","#8A94A6","#C4522A"]
    for i,e in enumerate(entries[:25]):
        me=e.get("nome","")==st.session_state.nome
        ri=medals[i] if i<3 else f"#{i+1}"; rc=mcol[i] if i<3 else "#3D4A5C"
        br="rgba(201,168,76,0.35)" if me else "rgba(201,168,76,0.06)"
        bg="#100D00" if me else "#0D101A"
        st.markdown(f"""
        <div class="lb-row {'me' if me else ''}" style="background:{bg};border-color:{br};">
          <div style="font-family:DM Serif Display,serif;font-size:1.4rem;color:{rc};min-width:36px;">{ri}</div>
          <div style="flex:1;">
            <div style="color:#C8C0B0;font-weight:600;font-size:0.9rem;">{e.get('nome','?')} {'<span style="font-family:DM Mono,monospace;font-size:0.6rem;color:#C9A84C;">(tu)</span>' if me else ''}</div>
            <div style="font-family:DM Mono,monospace;font-size:0.63rem;color:#3D4A5C;margin-top:1px;">{e.get('titolo','')}</div>
          </div>
          {''.join([f'<div style="text-align:center;min-width:50px;"><div style="font-family:DM Serif Display,serif;font-size:1.15rem;color:{c};">{v}</div><div style="font-family:DM Mono,monospace;font-size:0.55rem;color:#3D4A5C;text-transform:uppercase;letter-spacing:1px;">{l}</div></div>' for v,l,c in [(e.get("xp",0),"XP","#C9A84C"),(e.get("missioni",0),"Quest","#2A7B7C"),(f'{e.get("streak",0)}🔥',"Streak","#C4522A"),(e.get("badge",0),"Badge","#5C3D8A")]])}
        </div>""", unsafe_allow_html=True)

# ─── PROFILO ─────────────────────────────────────────────────────────────────
elif st.session_state.fase == "profilo":
    lv,titolo=get_livello(st.session_state.xp)
    xn=xp_next_thresh(st.session_state.xp)
    xp2=[0,150,400,800,1400,2200,3200,4500][min(lv-1,7)]
    prog=min((st.session_state.xp-xp2)/max(xn-xp2,1),1.0)
    tm=sum(len(v["livelli"]) for v in MISSIONS.values())
    COLORS2={"gold":"#C9A84C","blue":"#2C5F8A","teal":"#2A7B7C","rust":"#C4522A","purple":"#5C3D8A"}

    st.markdown(f"""
    <div class="masthead" style="margin-bottom:28px;">
      <div class="masthead-date">Profilo Studente — {datetime.now().strftime("%d %B %Y")}</div>
      <div class="masthead-title" style="font-size:2.5rem;">{st.session_state.nome}</div>
      <div style="font-family:DM Mono,monospace;font-size:0.7rem;color:#C9A84C;margin-top:4px;">{titolo} · Livello {lv} · {st.session_state.xp} XP</div>
    </div>""", unsafe_allow_html=True)

    cs=st.columns(5)
    for col,(ico,lbl,val,c) in zip(cs,[("◈","XP",st.session_state.xp,"#C9A84C"),("▶","Missioni",f"{len(st.session_state.completate)}/{tm}","#2A7B7C"),("◉","Livello",lv,"#5C3D8A"),("🔥","Streak",st.session_state.streak,"#C4522A"),("★","Badge",len(st.session_state.badge),"#2C5F8A")]):
        with col:
            st.markdown(f'<div style="background:#0D101A;border:1px solid rgba(201,168,76,0.1);border-top:2px solid {c};border-radius:3px;padding:18px;text-align:center;"><div style="font-family:DM Serif Display,serif;font-size:1.8rem;color:{c};margin-bottom:3px;">{val}</div><div style="font-family:DM Mono,monospace;font-size:0.6rem;color:#3D4A5C;text-transform:uppercase;letter-spacing:1.5px;">{lbl}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div style="background:#0D101A;border:1px solid rgba(201,168,76,0.1);border-radius:3px;padding:22px;margin-bottom:20px;"><div style="display:flex;justify-content:space-between;margin-bottom:8px;"><span style="font-family:DM Mono,monospace;font-size:0.65rem;color:#5C6878;text-transform:uppercase;letter-spacing:2px;">Prossimo Livello</span><span style="font-family:DM Mono,monospace;font-size:0.68rem;color:#C9A84C;">{st.session_state.xp} / {xn} XP</span></div><div class="xp-track" style="height:5px;"><div class="xp-fill" style="width:{prog*100:.0f}%;"></div></div><div style="font-family:DM Mono,monospace;font-size:0.6rem;color:#3D4A5C;margin-top:6px;">Ancora {xn-st.session_state.xp} XP al Livello {lv+1}</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="font-family:DM Serif Display,serif;font-size:1.1rem;color:#F5F0E8;margin-bottom:12px;">Progressione per Area</div>', unsafe_allow_html=True)
    ac=st.columns(len(MISSIONS))
    for col,(ak,av) in zip(ac,MISSIONS.items()):
        done=sum(1 for m in st.session_state.completate if ak in m); tot=len(av["livelli"]); pg=done/tot; acc=COLORS2.get(av["colore"],"#C9A84C")
        with col:
            st.markdown(f'<div style="background:#0D101A;border:1px solid rgba(201,168,76,0.08);border-radius:3px;padding:14px;text-align:center;"><div style="font-family:DM Serif Display,serif;font-size:1.3rem;color:{acc};margin-bottom:5px;">{av["emoji"]}</div><div style="font-family:DM Mono,monospace;font-size:0.68rem;color:{acc};margin-bottom:6px;">{done}/{tot}</div><div class="xp-track" style="height:3px;"><div style="height:100%;width:{pg*100:.0f}%;background:{acc};border-radius:1px;"></div></div></div>', unsafe_allow_html=True)

    st.markdown('<br><div style="font-family:DM Serif Display,serif;font-size:1.1rem;color:#F5F0E8;margin-bottom:12px;">Badge Collection</div>', unsafe_allow_html=True)
    bdef={"lv2":("📊","Analista Trainee"),"lv3":("📈","Junior Analyst"),"lv4":("💼","Associate"),"lv5":("🏛","Vice President"),"lv6":("◈","Director"),"lv7":("🎩","MD"),
          **{f"{ak}_m":(av["emoji"],f"Master {av['nome']}") for ak,av in MISSIONS.items()},
          "champ":("🏆","Champion"),"fire":("🔥","On Fire"),"inferno":("⚡","Inferno")}
    bc2=st.columns(6)
    for i,(bid,(em,nm)) in enumerate(bdef.items()):
        with bc2[i%6]:
            got=bid in st.session_state.badge; op="1" if got else "0.15"
            bc3="rgba(201,168,76,0.25)" if got else "rgba(201,168,76,0.05)"
            st.markdown(f'<div style="background:#0D101A;border:1px solid {bc3};border-radius:3px;padding:12px;text-align:center;opacity:{op};margin-bottom:8px;"><div style="font-size:1.5rem;margin-bottom:4px;">{em}</div><div style="font-family:DM Mono,monospace;font-size:0.58rem;color:{"#C9A84C" if got else "#3D4A5C"};">{nm}</div></div>', unsafe_allow_html=True)
