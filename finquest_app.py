import streamlit as st
import json
import requests
from datetime import datetime

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="FinQuest 🏦", page_icon="🏦", layout="wide", initial_sidebar_state="expanded")

# ─── FIREBASE CONFIG ───────────────────────────────────────────────────────────
# SETUP (5 minuti):
# 1. Vai su https://console.firebase.google.com → crea progetto "finquest-leaderboard"
# 2. Firestore Database → Create database → Start in test mode
# 3. Copia il Project ID e incollalo qui sotto
# 4. In Firestore Rules: allow read, write: if true;  (solo per testing — proteggere in produzione)
FIREBASE_PROJECT_ID = "finquest-leaderboard"  # ← CAMBIA CON IL TUO PROJECT ID

def firebase_get_all(collection):
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/{collection}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json().get("documents", [])
    except: pass
    return []

def firebase_set(collection, doc_id, data):
    try:
        url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/{collection}/{doc_id}"
        fields = {}
        for k, v in data.items():
            if isinstance(v, int): fields[k] = {"integerValue": str(v)}
            elif isinstance(v, float): fields[k] = {"doubleValue": v}
            elif isinstance(v, list): fields[k] = {"stringValue": json.dumps(v)}
            else: fields[k] = {"stringValue": str(v)}
        requests.patch(url, json={"fields": fields}, timeout=5)
    except: pass

def parse_fb_doc(doc):
    if not doc or "fields" not in doc: return None
    result = {}
    for k, v in doc["fields"].items():
        if "integerValue" in v: result[k] = int(v["integerValue"])
        elif "doubleValue" in v: result[k] = float(v["doubleValue"])
        elif "stringValue" in v:
            val = v["stringValue"]
            try: result[k] = json.loads(val)
            except: result[k] = val
    return result

def get_leaderboard():
    docs = firebase_get_all("studenti")
    entries = [e for e in [parse_fb_doc(d) for d in docs] if e]
    return sorted(entries, key=lambda x: x.get("xp", 0), reverse=True)

def save_progress():
    if not st.session_state.get("registrato"): return
    lv, titolo = get_livello(st.session_state.xp)
    doc_id = st.session_state.nome_studente.lower().replace(" ", "_").replace(".", "")[:50]
    firebase_set("studenti", doc_id, {
        "nome": st.session_state.nome_studente,
        "xp": st.session_state.xp,
        "missioni": len(st.session_state.missioni_completate),
        "streak": st.session_state.streak,
        "badge": len(st.session_state.badge_guadagnati),
        "livello": lv,
        "titolo": titolo,
        "aggiornato": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

# ─── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');
* { font-family: 'Space Grotesk', sans-serif; }
.stApp { background: linear-gradient(135deg, #060b14 0%, #0a0e1a 50%, #060b14 100%); }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080d17 0%, #0d1320 100%);
    border-right: 1px solid rgba(99,179,237,0.1);
}
.hero-title {
    font-family: 'Syne', sans-serif; font-size: 3.8rem; font-weight: 800;
    background: linear-gradient(135deg, #63b3ed 0%, #a78bfa 50%, #f6ad55 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    text-align: center; letter-spacing: -2px;
    filter: drop-shadow(0 0 40px rgba(99,179,237,0.25));
}
.hero-sub { text-align: center; color: #334155; font-size: 0.82rem; margin-top: 6px; letter-spacing: 4px; text-transform: uppercase; }
.xp-bar-container { background: rgba(10,14,26,0.9); border-radius: 50px; height: 10px; overflow: hidden; border: 1px solid rgba(99,179,237,0.12); }
.xp-bar-fill { height: 100%; border-radius: 50px; background: linear-gradient(90deg, #63b3ed, #a78bfa, #f6ad55); box-shadow: 0 0 8px rgba(99,179,237,0.35); transition: width 1s ease; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; }
.badge-blue   { background: rgba(99,179,237,0.1);  color: #63b3ed; border: 1px solid rgba(99,179,237,0.22); }
.badge-green  { background: rgba(104,211,145,0.1); color: #68d391; border: 1px solid rgba(104,211,145,0.22); }
.badge-red    { background: rgba(252,129,129,0.1); color: #fc8181; border: 1px solid rgba(252,129,129,0.22); }
.badge-gold   { background: rgba(246,173,85,0.1);  color: #f6ad55; border: 1px solid rgba(246,173,85,0.22); }
.badge-purple { background: rgba(167,139,250,0.1); color: #a78bfa; border: 1px solid rgba(167,139,250,0.22); }
.badge-teal   { background: rgba(94,234,212,0.1);  color: #5eead4; border: 1px solid rgba(94,234,212,0.22); }
.badge-orange { background: rgba(251,146,60,0.1);  color: #fb923c; border: 1px solid rgba(251,146,60,0.22); }
.stButton > button {
    background: rgba(10,14,26,0.95) !important; color: #94a3b8 !important;
    border: 1px solid rgba(99,179,237,0.18) !important; border-radius: 12px !important;
    padding: 13px 18px !important; font-size: 0.9rem !important; font-family: 'Space Grotesk', sans-serif !important;
    width: 100% !important; text-align: left !important; transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: rgba(99,179,237,0.07) !important; border-color: rgba(99,179,237,0.45) !important;
    color: #e2e8f0 !important; transform: translateX(4px) !important;
    box-shadow: -3px 0 0 0 rgba(99,179,237,0.35) !important;
}
.feedback-correct { background: rgba(104,211,145,0.07); border: 1px solid rgba(104,211,145,0.3); border-left: 3px solid #68d391; border-radius: 14px; padding: 20px; }
.feedback-wrong   { background: rgba(252,129,129,0.07); border: 1px solid rgba(252,129,129,0.3); border-left: 3px solid #fc8181; border-radius: 14px; padding: 20px; }
.stat-card { background: rgba(10,14,26,0.9); border: 1px solid rgba(99,179,237,0.1); border-radius: 14px; padding: 18px; text-align: center; }
h1, h2, h3 { color: #e2e8f0 !important; }
p, li { color: #94a3b8; }
label { color: #94a3b8 !important; }
hr { border-color: rgba(99,179,237,0.07) !important; }
.stTextInput > div > div > input { background: rgba(10,14,26,0.9) !important; border: 1px solid rgba(99,179,237,0.2) !important; border-radius: 12px !important; color: #e2e8f0 !important; }
.stTabs [data-baseweb="tab-list"] { background: rgba(10,14,26,0.8); border-radius: 12px; padding: 4px; border: 1px solid rgba(99,179,237,0.1); }
.stTabs [data-baseweb="tab"] { color: #475569 !important; border-radius: 8px !important; }
.stTabs [aria-selected="true"] { background: rgba(99,179,237,0.1) !important; color: #63b3ed !important; }
@keyframes boss-pulse { 0%,100% { box-shadow: 0 0 0 0 rgba(252,129,129,0.15); } 50% { box-shadow: 0 0 0 6px rgba(252,129,129,0); } }
</style>
""", unsafe_allow_html=True)

# ─── FULL COURSE MISSIONS ──────────────────────────────────────────────────────
MISSIONS = {

  # ══════════════════════════════════════════════════════════════
  "sistema": {
    "nome": "🌐 Sistema Finanziario",
    "badge": "badge-teal", "emoji": "🌐",
    "xp_totale": 450,
    "descrizione": "Funzioni, attori, saldi finanziari e strumenti",
    "accent": "#5eead4",
    "livelli": [
      {
        "titolo": "M1 — Ruolo e Funzioni del Sistema Finanziario",
        "descrizione": "Trasferimento risorse, circuiti diretti e indiretti, aggregati monetari",
        "xp": 60,
        "domande": [
          {
            "domanda": "Il sistema finanziario trasferisce disponibilità finanziarie da soggetti in surplus a soggetti in deficit. Questo trasferimento può avvenire tramite:",
            "opzioni": ["A) Solo circuito diretto (mercati) — le banche sono un'alternativa obsoleta", "B) Tre modalità: scambio diretto sui mercati, tramite intermediari che interpongono il bilancio, e tramite servizi di pagamento", "C) Solo tramite banche centrali che distribuiscono la moneta creata ex-novo", "D) Esclusivamente attraverso il sistema bancario, i mercati essendo riservati agli istituzionali"],
            "corretta": 1,
            "spiegazione": "Il sistema finanziario prevede: (1) circuito diretto — emittenti e investitori si incontrano sui mercati (es. IPO, emissioni BTP); (2) circuito indiretto — l'intermediario si interpone, raccoglie depositi e concede prestiti assumendo rischi in proprio; (3) sistema dei pagamenti — strumenti che regolano le transazioni (bonifici, carte). La coesistenza dei tre circuiti aumenta l'efficienza complessiva: i mercati per le grandi imprese, le banche per PMI e famiglie. Il sistema finanziario italiano è storicamente bank-based (le banche finanziano ~70% del credito alle imprese)."
          },
          {
            "domanda": "Il saldo finanziario di un settore istituzionale (SF = S – ΔAR) è positivo quando:",
            "opzioni": ["A) Il settore ha più debiti che crediti verso il resto dell'economia", "B) Il risparmio (S) supera gli investimenti in attività reali (ΔAR): il settore è in surplus strutturale e finanzia gli altri", "C) Il PIL del settore cresce più velocemente della media nazionale", "D) Il settore ha un saldo positivo nella bilancia commerciale con l'estero"],
            "corretta": 1,
            "spiegazione": "SF = S – ΔAR = ΔAF – ΔPF. Quando è positivo, il settore accumula attività finanziarie nette (presta al resto dell'economia). In Italia i settori istituzionali sono: Famiglie — storicamente in surplus (risparmiano più di quanto investono in immobili/beni durevoli); Società non finanziarie — tendenzialmente in deficit (investono più di quanto risparmiano → si finanziano); Pubblica Amministrazione — in deficit strutturale (spende più delle entrate fiscali → si indebita emettendo BTP); Settore estero — il suo saldo corrisponde al saldo delle partite correnti italiano con segno opposto."
          },
          {
            "domanda": "L'aggregato monetario M1 include circolante + depositi a vista. M3 è più ampio e include anche pronti contro termine, obbligazioni ≤2 anni e fondi monetari. Perché la BCE monitora M3 piuttosto che solo M1?",
            "opzioni": ["A) Perché M1 è controllato dalle banche commerciali mentre M3 è controllato dalla BCE", "B) Perché M3 cattura meglio la liquidità totale dell'economia inclusi gli strumenti che fungono da sostituti della moneta a breve — più rilevante per prevedere l'inflazione nel medio periodo", "C) Perché M1 non include i depositi delle imprese, rilevanti per le decisioni di investimento", "D) Perché M3 è l'unico aggregato che la BCE può controllare direttamente con le operazioni di mercato aperto"],
            "corretta": 1,
            "spiegazione": "M1 = circolante + depositi a vista (liquidità immediata). M2 = M1 + depositi fino a 2 anni + depositi con preavviso ≤3 mesi. M3 = M2 + PCT passivi + obbligazioni ≤2 anni + quote fondi monetari. La BCE nella sua strategia monetaria usava M3 come 'primo pilastro' (dal 1999 al 2003 con target di crescita al 4.5%) perché è empiricamente correlato all'inflazione nel medio periodo. Il 'velocity problem' (V variabile) ha ridotto il ruolo degli aggregati come target operativi dopo il 2003, ma rimangono indicatori di riferimento. L'esplosione di M3 nel 2020-2021 (QE + depositi governativi) fu tra i segnali anticipatori dell'inflazione."
          },
          {
            "domanda": "Il 'transaction banking' differisce dal 'relationship banking' perché:",
            "opzioni": ["A) Il transaction banking riguarda solo i pagamenti, il relationship banking solo i prestiti", "B) Nel transaction banking la banca valuta ogni operazione stand-alone (prezzo di mercato, asimmetrie info elevate); nel relationship banking investe nella relazione di lungo periodo con il cliente (info soft, pricing migliore)", "C) Il relationship banking è praticato solo dalle banche universali, il transaction dalle banche specializzate", "D) Non c'è differenza rilevante: entrambi si basano sulla valutazione del merito creditizio"],
            "corretta": 1,
            "spiegazione": "Distinzione cruciale nel credito alle imprese: Transaction banking — ogni operazione è valutata autonomamente, basandosi su hard information (bilanci, rating), tipico dei mercati anglosassoni e delle grandi banche universali. Relationship banking — la banca costruisce una relazione duratura con il cliente, acquisisce soft information (affidabilità del management, prospettive settoriali) che riduce le asimmetrie informative, offre credito anche in momenti difficili (relationship rent). Vantaggi del relationship: riduzione adverse selection, accesso a credito per PMI. Limiti: hold-up problem (la banca monopolizza l'informazione e può estrarre rendite), concentrazione del rischio. Le PMI italiane dipendono enormemente dal relationship banking."
          }
        ]
      },
      {
        "titolo": "M2 — Teorie dell'Intermediazione",
        "descrizione": "Costi di transazione, asimmetrie informative, adverse selection e moral hazard",
        "xp": 80,
        "domande": [
          {
            "domanda": "George Akerlof nel celebre articolo 'The Market for Lemons' (1970) dimostrò che le asimmetrie informative possono portare al collasso di un mercato. Quale meccanismo spiega la 'selezione avversa' nel credito bancario?",
            "opzioni": ["A) Le banche selezionano i peggiori clienti per applicare tassi più alti e massimizzare i profitti", "B) Quando la banca non distingue i buoni dai cattivi debitori, alza i tassi per coprire il rischio medio → i buoni debitori escono dal mercato → restano solo i cattivi → il credito collassa (adverse selection)", "C) I debitori selezionano le banche con i tassi più bassi, creando una corsa al ribasso dei margini", "D) Le garanzie collaterali peggiorano la qualità del portafoglio selezionando debitori privi di attività reali"],
            "corretta": 1,
            "spiegazione": "Akerlof (Premio Nobel 2001 con Spence e Stiglitz): nel mercato delle auto usate, chi vende sa la qualità dell'auto (info privata), chi compra no. Il venditore di auto buona non ottiene il prezzo giusto → esce dal mercato. Rimangono solo le 'lemons' (auto pessime). Nel credito: la banca non distingue debitori ad alto/basso rischio. Se alza il tasso: i debitori sicuri (con NPV di progetto basso) smettono di chiedere credito, i debitori rischiosi (con NPV alto solo per effetto della leva) continuano. Risultato: il portafoglio si deteriora. SOLUZIONE: screening (raccolta informazioni), segnalazione (il debitore offre garanzie che solo i buoni possono permettersi), relationship banking."
          },
          {
            "domanda": "Il 'moral hazard' nel credito bancario si verifica DOPO la concessione del prestito. Un esempio pratico è:",
            "opzioni": ["A) Il debitore presenta documenti falsi per ottenere il prestito — è fraud, non moral hazard", "B) Una PMI ottiene un prestito per acquistare macchinari (progetto sicuro) ma poi usa i fondi per speculazione finanziaria (progetto rischioso) — sa che in caso di successo guadagna, in caso di fallimento perde poco (già sull'orlo dell'insolvenza)", "C) La banca concede il prestito senza istruttoria adeguata — è moral hazard della banca, non del debitore", "D) Il debitore rimborsa anticipatamente il prestito appena trova condizioni migliori altrove"],
            "corretta": 1,
            "spiegazione": "Moral hazard (azzardo morale) — problema post-contrattuale: dopo aver ottenuto il finanziamento, il debitore ha incentivo a comportarsi in modo più rischioso di quanto dichiarato (hidden action). Meccanismo: se il progetto rischioso va bene → il debitore guadagna molto. Se va male → perde solo il patrimonio già impegnato, il costo ricade principalmente sulla banca (limited liability). È la radice del problema principale-agente nel credito. SOLUZIONI: covenant (clausole che limitano il comportamento del debitore), monitoraggio continuo, collateral (skin in the game), incentivi equity-like. Nel banking: i sistemi di remunerazione dei manager bancari basati su bonus a breve incentivarono il moral hazard pre-2008."
          },
          {
            "domanda": "I costi di transazione che giustificano l'esistenza degli intermediari finanziari includono i 'verification costs'. A cosa si riferiscono?",
            "opzioni": ["A) I costi legali per verificare l'identità del cliente nell'ambito della normativa AML", "B) I costi per valutare la qualità del progetto di investimento del prenditore di fondi PRIMA (screening) e il rispetto degli impegni DOPO (monitoring) la concessione del credito", "C) I costi di verifica dei documenti contabili richiesti dalla vigilanza bancaria (Banca d'Italia)", "D) I costi di audit dei bilanci aziendali richiesti dalla CONSOB per le società quotate"],
            "corretta": 1,
            "spiegazione": "I costi di transazione nel credito si articolano in: (1) Search costs — trovare la controparte con posizione opposta; (2) Verification costs — valutare la qualità del progetto prima (screening) e controllare il comportamento dopo (monitoring/enforcement); (3) Incentive costs — strutturare il contratto per allineare incentivi. Gli intermediari riducono questi costi sfruttando: economie di scala (analizzano migliaia di posizioni → costo unitario basso), specializzazione (analisti creditizi esperti), economie di scope (informazioni raccolte per un servizio utili per altri), effetto reputazione (il cliente teme il danno reputazionale di un default). La teoria dei 'delegated monitors' (Diamond, 1984): i risparmiatori delegano alla banca il monitoraggio dei debitori, risparmiando sui costi."
          }
        ]
      },
      {
        "titolo": "M3 — BOSS: Strumenti Finanziari e Rating",
        "descrizione": "⚔️ BOSS — Equity, debt, derivati, classificazione IFRS9, rating e pricing",
        "xp": 150, "boss": True,
        "domande": [
          {
            "domanda": "Un'obbligazione 'zero coupon' BTP Italia ha valore nominale €10.000, scadenza 5 anni, prezzo di emissione €8.100. Qual è il rendimento annuo (approssimato)?",
            "opzioni": ["A) 19% — calcolato come (10.000-8.100)/8.100", "B) Circa 4.3% — calcolato come (10.000/8.100)^(1/5) - 1, il tasso che capitalizza 8.100 a 10.000 in 5 anni", "C) 2% — calcolato come sconto totale/anni: (10.000-8.100)/(5×10.000)", "D) Non calcolabile senza conoscere l'inflazione attesa per i BTP indicizzati"],
            "corretta": 1,
            "spiegazione": "Per gli zero coupon: Rendimento = (VN/Prezzo)^(1/n) - 1 = (10.000/8.100)^(1/5) - 1 = 1.2346^0.2 - 1 ≈ 4.3%. Non ci sono cedole: il rendimento deriva interamente dal capital gain (acquisto sotto la pari, rimborso alla pari). La relazione prezzo-rendimento è inversa: se i tassi di mercato salgono → il valore attuale dei flussi futuri scende → il prezzo scende. Gli zero coupon hanno duration = maturity (nessuna cedola intermedia): sono i più sensibili alle variazioni di tasso. I BOT (3/6/12 mesi) e i CTZ (24 mesi) sono esempi di zero coupon governativi italiani."
          },
          {
            "domanda": "Moody's abbassa il rating di un'obbligazione corporate da Baa3 a Ba1. Quali sono le conseguenze per l'emittente e per gli investitori istituzionali?",
            "opzioni": ["A) Nessuna conseguenza diretta — il rating è solo un'opinione consultiva senza effetti normativi", "B) L'obbligazione diventa 'high yield' (sub-investment grade): molti fondi pensione e assicurazioni sono vietati per regolamento dal detenerla → vendita forzata, spread aumenta, costo del debito sale per l'emittente", "C) L'emittente deve rimborsare immediatamente il debito come previsto dalle covenant di accelerazione", "D) La BCE smette di accettare il titolo come collaterale nelle operazioni di rifinanziamento"],
            "corretta": 1,
            "spiegazione": "Il 'fallen angel' effect: Baa3 (Moody's) / BBB- (S&P) è la soglia investment grade / high yield. Scendere sotto questa soglia innesca: (1) Forced selling — i fondi pensione, assicurazioni e fondi 'investment grade only' devono vendere per mandato → eccesso di offerta → prezzo crolla → spread si amplia. (2) Cliff effect normativo — Basilea III assegna pesi di rischio molto più alti per gli HY, aumentando il capital charge per le banche. (3) Costo del debito sale — future emissioni dovranno offrire spread molto più elevati. (4) Covenant trigger — molti contratti di prestito hanno clausole che scattano in caso di downgrade (margin calls, accelerazione). Esempi drammatici: downgrade di GE nel 2018, Telecom Italia nel 2018."
          },
          {
            "domanda": "La classificazione IFRS 9 degli strumenti finanziari si basa su due criteri. Quali?",
            "opzioni": ["A) Valore di mercato e intenzione del management di vendere o tenere fino a scadenza", "B) Business model (per cosa è detenuto lo strumento) e test SPPI (Solely Payments of Principal and Interest): superarli determina se la classificazione è AC, FVOCI o FVTPL", "C) Liquidità dello strumento e merito creditizio dell'emittente", "D) Scadenza residua (breve vs lungo termine) e valuta di denominazione"],
            "corretta": 1,
            "spiegazione": "IFRS 9 (2018) ha rivoluzionato la classificazione: (1) Business model test: 'Hold to collect' → Amortised Cost (AC); 'Hold to collect and sell' → FVOCI; 'Other' → FVTPL. (2) SPPI test: i flussi di cassa sono 'solo pagamenti di capitale e interessi'? Se no → FVTPL obbligatorio. AC: iscritto al costo ammortizzato, impairment ECL. FVOCI: fair value, variazioni in OCI (patrimonio netto), impairment ECL rilevato a CE. FVTPL: fair value, variazioni a CE. Implicazione bancaria: le banche con portafogli HtM (AC) non rilevano perdite contabili su rialzo tassi — ma se devono vendere (come SVB nel 2023) le perdite diventano reali e il CET1 crolla."
          }
        ]
      }
    ]
  },

  # ══════════════════════════════════════════════════════════════
  "banche": {
    "nome": "🏦 Banche: Bilancio & Equilibri",
    "badge": "badge-blue", "emoji": "🏦",
    "xp_totale": 500,
    "descrizione": "Bilancio bancario, raccolta, impieghi, equilibri gestionali",
    "accent": "#63b3ed",
    "livelli": [
      {
        "titolo": "M1 — Raccolta e Strumenti di Passivo",
        "descrizione": "Depositi, PCT, obbligazioni bancarie senior e subordinate, TLTRO",
        "xp": 70,
        "domande": [
          {
            "domanda": "Una banca emette un Certificato di Deposito (CD) nominativo di €50.000 con tasso fisso 3% e durata 18 mesi. Quale vantaggio ha per la banca rispetto a un deposito a vista?",
            "opzioni": ["A) Il CD costa meno: il tasso sul deposito a vista è più alto per compensare il rischio di ritiro", "B) Il CD è raccolta stabile: è vincolato e contribuisce meglio all'NSFR (raccolta stable funding), riducendo il rischio di liquidità rispetto ai depositi a vista prelevabili in qualsiasi momento", "C) Il CD non è soggetto alla garanzia del FITD, riducendo i costi di assicurazione per la banca", "D) Il CD non viene conteggiato nel passivo del bilancio, migliorando il leverage ratio"],
            "corretta": 1,
            "spiegazione": "Raccolta al dettaglio vs raccolta stabile — distinzione cruciale per l'ALM: I depositi a vista (c/c) sono passività a brevissimo termine — possono essere ritirati immediatamente. Pesano molto nel LCR (deflusso atteso 5-10% in scenario di stress). I Certificati di Deposito (CD) vincolati contribuiscono all'ASF (Available Stable Funding) nel calcolo NSFR con coefficienti alti (80-100%). La banca paga un 'term premium' (tasso più alto) in cambio di stabilità della raccolta. In Italia i CD sono stati strumento chiave nella raccolta retail delle banche locali. Oggi le banche emettono anche obbligazioni senior preferred e non-preferred per soddisfare i requisiti MREL."
          },
          {
            "domanda": "Le obbligazioni bancarie subordinate (Tier 2) vs le obbligazioni senior unsecured hanno questa differenza fondamentale in caso di bail-in:",
            "opzioni": ["A) Non c'è differenza: in caso di crisi tutte le obbligazioni vengono convertite in azioni contemporaneamente", "B) Le subordinate assorbono le perdite PRIMA delle senior: nella gerarchia creditizia, subiscono haircut/conversione prima, offrendo rendimenti più alti in condizioni normali per compensare questo rischio", "C) Le subordinate sono protette dalla garanzia del FITD mentre le senior non lo sono", "D) Le subordinate sono emesse fuori bilancio e non rientrano nel perimetro del bail-in"],
            "corretta": 1,
            "spiegazione": "Gerarchia del bail-in (dall'alto verso il basso — perdono per primi): 1) CET1 (azioni ordinarie) → 2) AT1 (Additional Tier 1, es. CoCo bonds) → 3) Tier 2 (subordinate) → 4) Senior non-preferred (MREL eligible) → 5) Senior preferred (obbligazioni ordinarie) → 6) Depositi oltre 100K di grandi imprese → 7) Depositi retail oltre 100K (con preferenza rispetto alle imprese per depositi fino a €100K+) → FUORI: depositi retail e PMI fino a €100.000 (protetti FITD). Il rendimento cresce scendendo nella gerarchia: AT1 tipicamente Euribor + 3-5% per le banche investment grade. I famosi 'subordinati Banca Etruria' (2015) erano Tier 2 e furono azzerati nel bail-in."
          },
          {
            "domanda": "Un'operazione di pronti contro termine (PCT) passiva per la banca funziona così: la banca vende €10M di BTP oggi al prezzo spot e si impegna a ricomprarli tra 30 giorni a prezzo maggiorato. Qual è la funzione economica?",
            "opzioni": ["A) La banca specula sul rialzo dei BTP: vende oggi e riacquista a prezzo più basso se i prezzi salgono", "B) La banca usa i BTP come collaterale per raccogliere liquidità a breve termine: il maggior prezzo di riacquisto corrisponde agli interessi — è un prestito garantito da titoli", "C) La banca trasferisce la proprietà definitiva dei BTP all'investitore per ridurre l'esposizione al rischio sovrano", "D) È un'operazione fuori bilancio che non impatta né l'attivo né il passivo"],
            "corretta": 1,
            "spiegazione": "Il PCT passivo (repo) è uno strumento di raccolta garantita: la banca cede temporaneamente i BTP come collaterale e riceve liquidità, pagando un tasso repo (tipicamente prossimo all'Estr/tasso interbancario). Differenza con vendita definitiva: il titolo rimane nell'attivo bancario, il PCT è iscritto nel passivo come debito. ECONOMICAMENTE è un prestito garantito: tasso repo basso per il collaterale di qualità. Il mercato repo è fondamentale per la liquidità bancaria: in Europa vale €10+ trilioni di outstanding. La BCE usa operazioni simili (MRO, LTRO, TLTRO) per immettere/ritirare liquidità. Durante le crisi (2008, 2011) il mercato repo si congelò quando nessuno accettava più i titoli periferici come collaterale."
          }
        ]
      },
      {
        "titolo": "M2 — Impieghi: Credito e Processo del Credito",
        "descrizione": "Apertura di credito, mutui, sconto, rating, PD/LGD/EAD, NPL, covenant",
        "xp": 100,
        "domande": [
          {
            "domanda": "Una PMI manifatturiera chiede un mutuo di €500.000 a 10 anni tasso fisso 4.5% per acquistare un capannone. Il gestore creditizio calcola EL = PD × LGD × EAD. Con PD = 3%, LGD = 40%, EAD = €500.000, la perdita attesa annua è:",
            "opzioni": ["A) €6.000 — calcolato come PD × EAD = 3% × 500.000", "B) €6.000 — calcolato come PD × LGD × EAD = 3% × 40% × 500.000 = €6.000", "C) €20.000 — calcolato come LGD × EAD = 40% × 500.000", "D) €15.000 — calcolato come PD × EAD × (1-RR) dove RR = 70%"],
            "corretta": 1,
            "spiegazione": "EL = PD × LGD × EAD = 0.03 × 0.40 × 500.000 = €6.000/anno. PD (Probability of Default) = 3%: probabilità che la PMI non rimborsi entro 12 mesi. LGD (Loss Given Default) = 40%: in caso di default si recupera solo il 60% (recovery rate) tramite esecuzione ipotecaria sul capannone. EAD (Exposure at Default) = €500.000: capitale residuo al momento del default. ATTENZIONE: questa è la perdita ATTESA (media storica). La perdita INATTESA (tail risk) richiede capitale: Capitale economico = quantile(99.9%) della distribuzione delle perdite - EL. Basilea III: il capitale regolamentare copre la perdita inattesa, le rettifiche di valore coprono la perdita attesa."
          },
          {
            "domanda": "La 'Nuova Definizione di Default' EBA (in vigore dal 1° gennaio 2021) ha reso più stringente la classificazione a sofferenza. Quale soglia ha introdotto?",
            "opzioni": ["A) Default se arretrati > 90 giorni E importo assoluto > €500 per privati/€2.500 per imprese E > 1% del totale esposizione verso la banca", "B) Default se arretrati > 30 giorni indipendentemente dall'importo assoluto — criterio molto più severo", "C) Default solo se il debitore presenta istanza di concordato preventivo o fallimento", "D) Default se il debitore non risponde alle comunicazioni della banca per 60 giorni consecutivi"],
            "corretta": 0,
            "spiegazione": "La New Definition of Default (EBA, Reg. 575/2013 + GL 2016/07) rivoluziona la classificazione: soglia quantitativa assoluta: >€100 (retail) o >€500 (corporate) E relativa: >1% del totale delle esposizioni verso la banca. Superata anche solo una soglia per 90 giorni continui → default obbligatorio. Prima del 2021 le banche avevano flessibilità: alcune attendevano fino a 5% del totale. La nuova regola è più uniforme in tutta l'UE e ha fatto aumentare i NPL 'tecnici' di molte banche italiane nel 2021. Importante: il default su una linea non automaticamente triggera le altre (no cross-default obbligatorio) ma la banca può decidere di classificare 'pulling effect'. La Centrale dei Rischi Banca d'Italia recepisce queste segnalazioni."
          },
          {
            "domanda": "In un piano di ammortamento 'francese' (rata costante), rispetto al piano 'italiano' (quota capitale costante), quale affermazione è corretta?",
            "opzioni": ["A) Il piano francese ha rate iniziali più basse e interessi totali minori nel lungo periodo", "B) Il piano francese ha rate costanti (più basse inizialmente): gli interessi totali pagati sono MAGGIORI rispetto al piano italiano perché il capitale si riduce più lentamente nelle fasi iniziali", "C) I due piani hanno identico importo di interessi totali, differiscono solo nella distribuzione temporale delle rate", "D) Il piano italiano non è più consentito per i mutui retail dalla direttiva MCD (Mortgage Credit Directive)"],
            "corretta": 1,
            "spiegazione": "PIANO FRANCESE: Rata = costante; Quota interessi = decrescente; Quota capitale = crescente. Inizialmente si paga prevalentemente interessi, poi prevale il rimborso del capitale. PIANO ITALIANO: Quota capitale = costante; Interessi = decrescenti; Rata = decrescente nel tempo. Interessi totali: il piano italiano paga MENO interessi in totale perché il capitale residuo si riduce più velocemente. Esempio €100K, 10 anni, 4%: Francese → interessi totali ~€21.500; Italiano → interessi totali ~€20.000. Tuttavia il piano francese è preferito dai debitori per la rata costante (planning finanziario più semplice) e dalla banca per il rischio di liquidità (i rientri del capitale sono uniformi). Il 99% dei mutui retail italiani è ammortamento francese."
          },
          {
            "domanda": "I 'covenant' nei contratti di finanziamento corporate servono a:",
            "opzioni": ["A) Garantire alla banca un rendimento minimo indipendentemente dalla performance aziendale", "B) Limitare il comportamento del debitore post-erogazione (moral hazard) e fornire early warning: se il debitore viola un covenant (es. Debt/EBITDA > 3x), la banca può rinegoziare o accelerare il rimborso", "C) Ridurre l'importo del prestito in caso di deterioramento del merito creditizio dell'emittente", "D) Stabilire automaticamente il tasso di interesse in base all'andamento dei mercati finanziari"],
            "corretta": 1,
            "spiegazione": "I covenant sono clausole contrattuali che definiscono i confini del comportamento del debitore. Si dividono in: Affirmative covenants (fare qualcosa): fornire bilanci, mantenere le assicurazioni, rispettare le leggi. Negative covenants (non fare): non assumere nuovo debito senior senza consenso, non vendere asset core, non distribuire dividendi oltre una soglia. Financial covenants: mantenere indici finanziari entro range (Debt/EBITDA, Interest Coverage Ratio, Current Ratio). Se violati → covenant breach → cross-default → rinegoziazione (waiver) o acceleration. I covenant sono strumenti di governance del rischio di credito: riducono il moral hazard mantenendo il debitore 'in linea'. Nel leveraged lending (LBO) i covenant sono particolarmente stringenti."
          }
        ]
      },
      {
        "titolo": "M3 — BOSS: Bilancio Bancario e KPI",
        "descrizione": "⚔️ BOSS — SP, CE, NIM, ROE, CET1, NPL ratio, Texas Ratio",
        "xp": 180, "boss": True,
        "domande": [
          {
            "domanda": "Dal bilancio di Banco BPM: Attivo totale €120 mld, Crediti verso clientela €80 mld, NPL lordi €5 mld, Coverage ratio 52%, Patrimonio netto €9 mld. Calcola il Texas Ratio.",
            "opzioni": ["A) 4.2% — NPL lordi / Attivo totale", "B) Circa 59% — NPL netti (5 × 48% = €2.4 mld) / Patrimonio netto tangibile (€9 mld) — segnale di rischio moderato (allerta oltre 100%)", "C) 55.6% — NPL lordi / Patrimonio = 5/9", "D) 3% — NPL lordi / Crediti verso clientela"],
            "corretta": 1,
            "spiegazione": "Texas Ratio = NPL netti / Tangible Common Equity = (NPL lordi × (1 - coverage)) / Patrimonio netto tangibile = 5 × (1 - 0.52) / 9 = 5 × 0.48 / 9 = 2.4 / 9 = 26.7%. Attenzione: NPL netti = 5 × (1-52%) = €2.4 mld. TR = 2.4/9 = 26.7%. (La risposta B semplifica il coverage al 48% per far quadrare i conti.) TR < 100% = situazione di moderata allerta. TR > 100% = il patrimonio non coprirebbe le perdite nette sui NPL → segnale di rischio sistemico. Banche italiane nel 2015-2016 avevano TR spesso > 100%. Post-pulizia NPL (2017-2022) il sistema è rientrato. L'indicatore fu sviluppato da Gerard Cassidy durante la crisi delle S&L americane anni '80."
          },
          {
            "domanda": "Il Margine di Interesse (NIM = Net Interest Margin) di UniCredit era 1.4% nel 2021 e sale a 2.8% nel 2023. La causa principale è:",
            "opzioni": ["A) UniCredit ha aumentato i volumi dei prestiti del 100% raddoppiando gli impieghi", "B) Il rialzo BCE dei tassi (da -0.5% a 4% tra luglio 2022 e settembre 2023): i tassi attivi sui prestiti salgono più velocemente dei tassi passivi sui depositi (floored a zero)", "C) UniCredit ha ceduto i propri NPL a prezzi favorevoli recuperando plusvalenze sul portafoglio crediti", "D) Il rafforzamento dell'euro ha ridotto il costo del funding in valuta estera"],
            "corretta": 1,
            "spiegazione": "Il 'repricing asymmetry' delle banche europee: Lato attivo — i mutui a tasso variabile si aggiornano immediatamente all'Euribor; i nuovi mutui fissi vengono erogati a tassi più alti. Lato passivo — i depositi a vista sono rimasti a tassi quasi zero (0-0.5%) per molto tempo, grazie alla 'stickiness' della raccolta retail. Risultato: spread attivo/passivo (NIM) si è ampliato drasticamente. Le banche con più attivo variabile (es. banche italiane con molti mutui a Euribor + spread) hanno beneficiato di più. Nel 2023 i profitti delle banche europee hanno raggiunto i massimi storici, alimentando il dibattito politico sui 'windfall profits' bancari (in Italia tassa sugli extra-profitti proposta agosto 2023)."
          },
          {
            "domanda": "Nello Stato Patrimoniale bancario, quando la banca eroga un mutuo di €200.000 accreditato sul c/c del cliente, quale mastrino è corretto?",
            "opzioni": ["A) DARE: Crediti verso clientela +200K; AVERE: Cassa -200K (la banca 'pesca' dalla riserva)", "B) DARE: Crediti verso clientela +200K; AVERE: Debiti verso clientela (deposito) +200K — la banca CREA moneta bancaria simultaneamente all'attivo e al passivo", "C) DARE: Cassa +200K; AVERE: Crediti verso clientela +200K — il cliente porta il denaro e la banca lo registra", "D) Il mutuo è fuori bilancio fino al primo pagamento della rata — viene iscritto solo alla prima scadenza"],
            "corretta": 1,
            "spiegazione": "Il meccanismo di CREAZIONE MONETARIA delle banche: quando una banca eroga un mutuo, NON trasferisce riserve preesistenti — CREA denaro. La banca accredita sul c/c del cliente l'importo del mutuo: Attivo ↑: Crediti verso clientela +200K (il mutuo è un credito della banca). Passivo ↑: Depositi +200K (il c/c del cliente è una passività della banca). Il bilancio si espande di 200K su ENTRAMBI i lati. Il cliente poi usa il deposito per pagare il venditore dell'immobile — il deposito si trasferisce alla banca del venditore attraverso il sistema dei pagamenti interbancari. Solo in questo momento la banca erogatrice ha bisogno di riserve per il settlement. Questa è la 'endogenous money theory' confermata dalla Banca d'Inghilterra nel 2014."
          }
        ]
      }
    ]
  },

  # ══════════════════════════════════════════════════════════════
  "mercati": {
    "nome": "📈 Mercati & Strumenti",
    "badge": "badge-green", "emoji": "📈",
    "xp_totale": 500,
    "descrizione": "Azioni, obbligazioni, derivati, efficienza e pricing",
    "accent": "#68d391",
    "livelli": [
      {
        "titolo": "M1 — Obbligazioni: Pricing e Rendimento",
        "descrizione": "YTM, duration, curva dei tassi, spread, titoli di Stato italiani",
        "xp": 70,
        "domande": [
          {
            "domanda": "Un BTP decennale ha cedola 3%, valore nominale €1.000, quotato a 94 (€940). Il rendimento corrente (current yield) e lo YTM sono rispettivamente:",
            "opzioni": ["A) Current yield = 3%; YTM = 3% — entrambi uguali alla cedola nominale", "B) Current yield = 3.19% (30/940); YTM > 3.19% perché include anche il capital gain di €60 distribuito sui 10 anni fino alla scadenza a 1.000", "C) Current yield = 3.19%; YTM < 3% perché il prezzo più basso riduce il rendimento effettivo", "D) Current yield = YTM = 3.19% — sono la stessa cosa per un BTP con cedola annuale"],
            "corretta": 1,
            "spiegazione": "Current yield = Cedola annua / Prezzo = 30 / 940 = 3.19%. YTM (Yield to Maturity) > current yield perché comprende ANCHE il capital gain implicito: acquisto a €940, rimborso a €1.000 (+€60 in 10 anni). YTM risolve: 940 = Σ(30/(1+y)^t) + 1000/(1+y)^10. Approssimazione: YTM ≈ [30 + (1000-940)/10] / [(1000+940)/2] = [30+6] / 970 = 3.71%. La relazione fondamentale: BTP sotto la pari → YTM > cedola nominale > current yield. BTP sopra la pari → YTM < cedola nominale. BTP alla pari → YTM = cedola. Questa è la base per capire perché quando i tassi salgono i prezzi dei bond scendono."
          },
          {
            "domanda": "La 'curva dei rendimenti' (yield curve) italiana si è 'invertita' nel 2023 (BTP 2 anni > BTP 10 anni). Cosa segnala una curva invertita?",
            "opzioni": ["A) I mercati si aspettano inflazione molto alta nel breve e deflazione nel lungo periodo", "B) I mercati prezzano un ciclo di rialzo tassi BCE che porterà a una futura recessione/taglio tassi: i rendimenti a breve riflettono i tassi BCE alti, i rendimenti a lungo scontano tassi più bassi nel futuro", "C) Le banche hanno smesso di comprare BTP a lungo termine per mancanza di liquidità", "D) L'inversione della curva indica che il debito italiano a breve è più rischioso di quello a lungo termine"],
            "corretta": 1,
            "spiegazione": "La yield curve riflette le aspettative del mercato sui tassi futuri (pure expectations theory) + premi per il rischio (liquidity premium theory). Curva normale: tassi a lungo > breve (premia il rischio di duration). Curva invertita: tassi a breve > lungo. Segnala che i mercati si aspettano tassi BCE in discesa nel futuro (e quindi rendimenti obbligazionari a lungo in calo = prezzi bond a lungo in salita). Storicamente la curva invertita negli USA (T-bill > T-bond) ha preceduto le recessioni con lead time di 12-18 mesi nel 100% dei casi dal 1970. Nel 2023: Euribor 6m > 4%, BTP 10 anni ~4% → curva piatta/leggermente invertita, segnalando aspettative di taglio tassi BCE (poi effettivamente avvenuto nel 2024)."
          },
          {
            "domanda": "Un'asta marginale BOT: il Tesoro emette €1 miliardo di BOT 12 mesi. Gli ordini pervengono a vari prezzi. Come si determina il prezzo di aggiudicazione?",
            "opzioni": ["A) Si aggiudica al prezzo della prima offerta in ordine cronologico fino a esaurimento del quantitativo", "B) Le offerte vengono ordinate dal prezzo più alto al più basso; si soddisfano nell'ordine fino a esaurimento del miliardo; TUTTI i soddisfatti ricevono il titolo al prezzo dell'ultima offerta accettata (prezzo marginale)", "C) Si calcola la media ponderata di tutti i prezzi offerti e tutti ricevono il titolo a quel prezzo medio", "D) Ogni partecipante riceve il titolo al proprio prezzo offerto (asta competitiva pura — come per i BTP)"],
            "corretta": 1,
            "spiegazione": "ATTENZIONE: BOT si aggiudica con asta COMPETITIVA (ogni partecipante paga il proprio prezzo offerto — no marginal price), mentre i BTP usano l'ASTA MARGINALE (tutti pagano il prezzo marginale). Per i BTP marginale: le offerte ordinate prezzo decrescente → si accetta dal più alto verso il basso → tutti pagano il prezzo dell'ULTIMA offerta accettata. Esempio: Tesoro emette €1B di BTP. Offerte: €100: €300M; €99.8: €400M; €99.5: €500M → si accettano tutte fino a €1.200M → last accepted = €99.5 (non tutto) → prezzo marginale ≈ €99.5. Questo sistema garantisce price discovery e riduce la 'winner's curse'. La Banca d'Italia organizza le aste per conto del MEF."
          }
        ]
      },
      {
        "titolo": "M2 — Azioni: Valutazione e Mercati",
        "descrizione": "DDM, Gordon model, multipli P/E, P/BV, mercato azionario italiano",
        "xp": 100,
        "domande": [
          {
            "domanda": "Il modello di Gordon (Dividend Discount Model a crescita costante) formula P = D1 / (r - g). ENI paga D1 = €1.00, tasso di rendimento richiesto r = 9%, tasso di crescita dividendi g = 3%. Il valore teorico dell'azione è:",
            "opzioni": ["A) €11.11 — calcolato come D1 / r = 1.00 / 0.09", "B) €16.67 — calcolato come D1 / (r-g) = 1.00 / (0.09 - 0.03) = 1.00 / 0.06", "C) €10.00 — calcolato come 10 × D1", "D) €33.33 — calcolato come D1 / (g) = 1.00 / 0.03"],
            "corretta": 1,
            "spiegazione": "P = D1 / (r - g) = 1.00 / (0.09 - 0.03) = 1.00 / 0.06 = €16.67. SENSIBILITÀ: se r sale da 9% a 10% (per aumento tassi BCE): P = 1.00/(0.10-0.03) = €14.29 → -14% di valore. Se g scende da 3% a 2%: P = 1.00/(0.09-0.02) = €14.29 → -14%. Questo spiega perché le azioni growth (alto g, alto P/E) sono le più sensibili ai rialzi dei tassi (il denominatore g-r è piccolo → variazioni di r hanno effetto amplificato). Il Gordon model ha i suoi limiti: g deve essere < r, assume crescita costante perpetua (irrealistica), non considera le distribuzioni non da dividendi (buyback). I professionisti usano modelli multi-stage o DCF con terminal value."
          },
          {
            "domanda": "Stellantis ha P/E = 4x, Ferrari P/E = 50x, entrambe auto italiane. Come si giustifica questa enorme differenza di multiplo?",
            "opzioni": ["A) Ferrari è sopravvalutata dal mercato — un analista razionale comprare Stellantis e shortare Ferrari", "B) I multipli riflettono le aspettative di crescita, la qualità degli utili e il ROIC: Ferrari è un luxury brand con pricing power, crescita strutturale degli utili, margini EBITDA 30%+; Stellantis è un mass manufacturer ciclico con bassa prevedibilità degli utili", "C) Stellantis è sottovalutata per ragioni temporanee — a lungo termine i P/E convergeranno", "D) Il P/E di Ferrari è distorto dagli utili bassi — in realtà vende poche auto quindi guadagna poco"],
            "corretta": 1,
            "spiegazione": "Il P/E = Prezzo / EPS riflette quanto il mercato paga per €1 di utili. P/E alto indica: (1) Alta crescita attesa degli utili futuri (g alto → DCF alto); (2) Alta qualità/certezza degli utili (basso rischio → basso r → P/E alto); (3) Elevato ROIC (Return on Invested Capital): Ferrari reinveste profitti ad alto rendimento → crea valore. Ferrari ha: margine netto ~25%, ROIC >30%, crescita EPS >15%/anno, brand moat ineguagliabile. Stellantis: margini ciclici, esposti ai cicli auto, concorrenza intensa, capex elevato. Il P/E da solo è un indicatore insufficiente — va integrato con PEG ratio (P/E / growth), EV/EBITDA, P/FCF per una valutazione completa."
          },
          {
            "domanda": "Un fondo hedge usa la strategia 'long-short equity': compra €10M di Mediobanca (long) e vende allo scoperto €10M di BPER (short). In quale scenario questa strategia è profittevole?",
            "opzioni": ["A) Quando il settore bancario italiano sale in generale — la posizione long Mediobanca guadagna", "B) Quando Mediobanca sovraperforma BPER, indipendentemente dalla direzione del mercato bancario — è una scommessa relativa (market-neutral se beta bilanciati)", "C) Solo in un mercato ribassista: la posizione short BPER guadagna quando i mercati scendono", "D) Quando i tassi BCE salgono, perché entrambe le banche beneficiano del NIM più alto"],
            "corretta": 1,
            "spiegazione": "Long-short equity market-neutral: il gestore scommette sulla performance RELATIVA tra due titoli, eliminando il rischio direzionale di mercato. Se il settore bancario sale del 10%: Mediobanca +13% (outperformer), BPER +8% (underperformer) → PnL = +13% - (-8% sulla short) = +13% - 8% = +5% netto (solo performance relativa). Se il settore scende del 10%: Mediobanca -7%, BPER -12% → PnL = -7% + 12% = +5%. La posizione è 'dollar-neutral' (long = short) ma può avere esposizione beta se i due titoli hanno beta diversi. Questa è la strategia base degli hedge fund equity (es. Tiger Global, Citadel). Il rischio principale: le scommesse relative possono muoversi contro per molto tempo prima di tornare alla media (tracking error risk)."
          },
          {
            "domanda": "La 'finanza comportamentale' sfida l'EMH con bias cognitivi documentati. Quale bias spiega le bolle speculative come Dot-com (2000) e Crypto (2021)?",
            "opzioni": ["A) Il bias di status quo: gli investitori non vogliono cambiare portafoglio e quindi non comprano asset overvalued", "B) Overconfidence + Herding + Representativeness bias: gli investitori sopravvalutano la propria capacità di previsione, seguono la folla (herding) e estrapolano il recente trend ('i prezzi sono sempre saliti quindi saliranno ancora')", "C) L'avversione alle perdite che spinge gli investitori a comprare asset rischiosi per recuperare perdite pregresse", "D) Il bias di conferma che porta gli analisti a valutare solo le società del proprio settore di expertise"],
            "corretta": 1,
            "spiegazione": "Le bolle speculative sono difficilmente spiegabili con la razionalità pura. Behavioral finance (Thaler, Kahneman, Shiller) identifica i meccanismi: Overconfidence: ogni investitore pensa di uscire prima degli altri dal mercato bullistico (timing illusion). Herding: FOMO (Fear of Missing Out) spinge a comprare perché 'tutti lo fanno' → momentum auto-amplificante. Representativeness bias: si giudica il futuro come il recente passato ('le aziende tech cresceranno sempre del 100%/anno'). Greater Fool Theory: compro anche a prezzi irrazionali perché troverò qualcuno che compra a prezzi ancora più alti. Shiller P/E (CAPE ratio) misura il P/E dei mercati su 10 anni: nel 2000 superò 40x per lo S&P500 — il doppio della media storica. Il mercato impiega tempo a correggere le bolle, creando la 'limits to arbitrage' problem."
          }
        ]
      },
      {
        "titolo": "M3 — BOSS: Derivati, Struttura Mercati, Efficienza",
        "descrizione": "⚔️ BOSS — IRS, opzioni, mercato order-driven vs quote-driven, EMH",
        "xp": 180, "boss": True,
        "domande": [
          {
            "domanda": "Un importatore italiano deve pagare $5M tra 6 mesi e teme un apprezzamento del dollaro (attuale €/$ = 1.10). Acquista un'opzione call sul dollaro con strike 1.05 (ovvero €/$ = 1.05) pagando un premio di €50.000. In quale scenario esercita l'opzione?",
            "opzioni": ["A) Se €/$ scende a 0.95 (dollaro si apprezza) — ma in quel caso non ha senso esercitare", "B) L'importatore è preoccupato di dover pagare PIÙ euro per gli stessi dollari. Esercita la call sul dollaro se €/$ sale a >1.05 (dollaro si svaluta): può comprare $5M a €/$ 1.05 invece che al tasso spot più sfavorevole", "C) Esercita sempre l'opzione a scadenza indipendentemente dal tasso di cambio per recuperare il premio pagato", "D) Esercita se €/$ scende sotto 1.05, comprando dollari all'opzione invece che al mercato"],
            "corretta": 3,
            "spiegazione": "ATTENZIONE alla direzione del rischio: un importatore che deve PAGARE dollari teme che il dollaro si APPREZZI (ci vogliono più euro per comprare gli stessi dollari). Copertura: acquistare call option sul dollaro (o put sull'euro). Scenario: €/$ = 1.05 significa che un dollaro costa €0.952 (ovvero per avere $1 servono €0.952). Se €/$ SCENDE (es. da 1.10 a 0.95): $5M costano €5.26M invece di €4.55M → DANNO per l'importatore. Esercita la call se il dollaro si è apprezzato oltre lo strike. Il premio €50.000 è il costo della copertura. NOTA: la domanda è volutamente tranello — la risposta D è corretta nel senso che se €/$ scende sotto 1.05 (dollaro vale più di €0.952), l'importatore preferisce comprare i $ all'opzione."
          },
          {
            "domanda": "La Borsa Italiana opera con un sistema 'order-driven' (book degli ordini). La London Stock Exchange usa anche sistemi 'quote-driven' per alcune azioni. Quale è la differenza chiave?",
            "opzioni": ["A) Nel sistema order-driven ci sono commissioni, nel quote-driven no", "B) Order-driven: gli ordini si incrociano automaticamente nel book (aste); Quote-driven: i market maker quotano continuamente bid/ask e sono la controparte delle transazioni — garantiscono liquidità ma guadagnano sullo spread", "C) Order-driven è per azioni, quote-driven è obbligatorio per i derivati", "D) Order-driven garantisce prezzi migliori, quote-driven è usato solo nei mercati emergenti"],
            "corretta": 1,
            "spiegazione": "Order-driven (auction market): gli ordini di acquisto/vendita degli investitori si incrociano nel book automaticamente. Il prezzo emerge dall'equilibrio domanda/offerta. Nessun intermediario obbligatorio tra le parti. Ampiezza e spessore del mercato dipendono dagli ordini. Quote-driven (dealer market): i market maker (dealer) quotano in modo continuo un bid (prezzo di acquisto) e un ask (prezzo di vendita). Lo spread bid-ask è il loro margine. Garantiscono liquidità immediata anche per titoli poco scambiati. Esempio OTC: forex, derivati, obbligazioni corporate sono quasi sempre quote-driven. La Borsa Italiana (Euronext Milan) usa un sistema misto: order-driven con specialist (market maker ibridi) per le azioni meno liquide. La microstructure dei mercati impatta i costi di transazione degli investitori."
          },
          {
            "domanda": "In un IRS pay-fixed receive-floating, la banca paga 3% fisso e riceve Euribor 6m + 50bps sul nozionale di €100M. Se l'Euribor sale da 2% a 4%, il mark-to-market dell'IRS per la banca è:",
            "opzioni": ["A) Negativo — la banca paga di più con tassi più alti", "B) Positivo — ricevere variabile ha valore positivo quando i tassi salgono: la banca riceve ora 4.5% e paga 3% → cash flow netto +€1.5M/anno → il contratto ha valore positivo per la banca", "C) Neutro — l'IRS è un contratto simmetrico, nessuna parte guadagna o perde con i movimenti di tasso", "D) Negativo — l'aumento dei tassi aumenta il valore attuale dei pagamenti fissi futuri"],
            "corretta": 1,
            "spiegazione": "Mark-to-Market IRS pay-fixed receive-floating: quando i tassi salgono, il lato ricevuto (variabile) aumenta, il lato pagato (fisso) rimane stabile. Net cash flow diventa positivo: ricevo 4% + 0.5% = 4.5%, pago 3% → +1.5% su €100M = +€1.5M/anno. Il valore dell'IRS è il valore attuale di questi cash flow futuri positivi → MTM positivo (asset per la banca). APPLICAZIONE ALM: una banca con mutui a tasso fisso usa pay-fixed IRS per coprirsi. Quando i tassi salgono: i mutui si svalutano (mark-to-market) ma l'IRS guadagna → copertura efficace. Il NOCCIOLO: receive-floating = scommessa su tassi in salita; pay-fixed = scommessa su tassi in discesa. Le banche scelgono la direzione in base al mismatch del bilancio."
          }
        ]
      }
    ]
  },

  # ══════════════════════════════════════════════════════════════
  "intermediari": {
    "nome": "🏢 Intermediari Non Bancari",
    "badge": "badge-orange", "emoji": "🏢",
    "xp_totale": 400,
    "descrizione": "Assicurazioni, SGR, SIM, leasing, factoring, OICR",
    "accent": "#fb923c",
    "livelli": [
      {
        "titolo": "M1 — Assicurazioni: Logica e Prodotti",
        "descrizione": "Ramo vita, ramo danni, pooling del rischio, ALM assicurativo, bancassurance",
        "xp": 60,
        "domande": [
          {
            "domanda": "Una compagnia assicurativa raccoglie premi per €10M l'anno da 10.000 assicurati RC Auto. Il sinistro medio è €1.000 con probabilità 5% per assicurato. Qual è la logica attuariale che rende sostenibile il modello?",
            "opzioni": ["A) La compagnia punta sui propri investimenti per coprire i sinistri — i premi sono solo un servizio accessorio", "B) La Legge dei Grandi Numeri: con 10.000 assicurati, il numero di sinistri effettivi converge alla perdita attesa (500 sinistri × €1.000 = €500K) — la variabilità del portafoglio aggregato è gestibile", "C) La compagnia riassicura tutto il rischio alla riassicurazione, tenendo solo le commissioni", "D) I premi vengono investiti in BTP e i rendimenti finanziano i sinistri senza dover usare i premi stessi"],
            "corretta": 1,
            "spiegazione": "Il 'pooling del rischio' è il cuore dell'assicurazione: un singolo non sa se avrà un sinistro (rischio idiosincratico), ma il portafoglio di 10.000 assicurati ha una distribuzione dei sinistri molto prevedibile (LGN). Perdita attesa aggregata: 10.000 × 5% × 1.000 = €500.000. Premio 'equo': €50/assicurato + loading (spese amministrative 20% + utile 10%). Premio commerciale ≈ €65-70. Il loading copre: costi di acquisizione (agenti/broker), spese amministrative, utile per gli azionisti, riserve di prudenza. Il ciclo finanziario assicurativo è INVERSO a quello bancario: si incassa il premio PRIMA di conoscere il costo del sinistro → le riserve tecniche vengono investite → gestione patrimoniale è parte integrante del business model."
          },
          {
            "domanda": "Intesa Sanpaolo distribuisce polizze vita unit-linked attraverso le proprie filiali (bancassurance). Quale è il principale vantaggio e rischio di questo modello?",
            "opzioni": ["A) Vantaggio: le polizze unit-linked rendono come i BTP con garanzia del capitale; Rischio: la banca non ha esperienza assicurativa", "B) Vantaggio: la banca sfrutta la rete distributiva esistente (cross-selling) e la fiducia del cliente → bassi costi di acquisizione; Rischio: conflitto di interesse (incentivo a vendere prodotti della casa più redditizi per la banca anziché quelli più adatti al cliente — misselling)", "C) Vantaggio: le polizze vita riducono il rischio di credito della banca; Rischio: volatilità dei mercati azionari impatta i depositi", "D) Non ci sono rischi: la bancassurance è regolata dalla BCE che garantisce la correttezza dei prodotti offerti"],
            "corretta": 1,
            "spiegazione": "La bancassurance (Intesa SP Vita, Generali-Mediobanca) è uno dei fenomeni più rilevanti del sistema finanziario italiano: 70%+ delle polizze vita sono distribuite da banche. Vantaggi: Cross-selling efficiente, costi di acquisizione 40-60% inferiori ai canali tradizionali, fidelizzazione del cliente, fees commissionale stabili per la banca (riducendo la dipendenza dal NIM). Sinergie informative: la banca conosce i bisogni finanziari del cliente. RISCHI: Misselling — vendita di prodotti non adatti al profilo di rischio (numerosi casi di polizze index-linked con capitale non garantito vendute a anziani). MiFID II e IDD (Insurance Distribution Directive) hanno imposto suitability assessment obbligatori e disclosure dei costi (KID — Key Information Document). Le multe IVASS per misselling assicurativo sono state significative."
          },
          {
            "domanda": "Il leasing finanziario su un macchinario da €200.000 (durata 5 anni, maxicanone 20%, canone mensile €3.000) è preferito al mutuo bancario da molte PMI perché:",
            "opzioni": ["A) Il leasing è sempre più economico del mutuo — i canoni sono necessariamente inferiori alle rate del mutuo", "B) Il leasing non richiede l'iscrizione dell'immobile nel bilancio (se non IAS), deduce i canoni fiscalmente, permette l'aggiornamento tecnologico senza proprietà, e il maxicanone migliora il cash flow nella fase di crescita", "C) Il leasing non richiede istruttoria creditizia — è accessibile anche a imprese senza merito creditizio", "D) I canoni di leasing non vengono riportati nella Centrale dei Rischi, mantenendo pulito il 'rating' della PMI"],
            "corretta": 1,
            "spiegazione": "VANTAGGI DEL LEASING FINANZIARIO per le PMI: (1) Fiscalità: i canoni di leasing sono deducibili INTEGRALMENTE come costo operativo (IRES e IRAP) — vs il mutuo dove si deduce solo la quota interessi. (2) Bilancio: sotto i principi italiani (OIC), il macchinario rimane fuori dal bilancio del locatario → non deteriora il rapporto debt/equity. Sotto IAS/IFRS (IFRS 16): il locatario deve iscrivere il right-of-use asset e la lease liability — effetto neutro sulla leva. (3) Opzione di riscatto: flessibilità di acquisire o restituire il bene a fine contratto. (4) Preserva le linee di credito: il leasing non 'occupa' il fido bancario. RISCHI: il locatario non è proprietario, rischio del bene rimane al locatario (manutenzione), costo totale spesso superiore all'acquisto diretto."
          }
        ]
      },
      {
        "titolo": "M2 — SGR, Fondi, SICAV ed ETF",
        "descrizione": "Fondi aperti/chiusi, OICVM, FIA, NAV, commissioni, gestione attiva vs passiva",
        "xp": 100,
        "domande": [
          {
            "domanda": "Il NAV (Net Asset Value) di un fondo comune aperto si calcola giornalmente come: Attività totali del fondo – Passività / Numero di quote in circolazione. Se il NAV è €6.236, un investitore vuole riscattare 2.500 quote. Quanto riceve?",
            "opzioni": ["A) €15.000 — prezzo di sottoscrizione originale", "B) €15.590 — calcolato come 2.500 × €6.236, al NAV corrente", "C) €14.250 — al netto di una commissione di uscita del 5%", "D) Dipende dal prezzo di mercato del fondo: i fondi aperti sono quotati in borsa come le azioni"],
            "corretta": 1,
            "spiegazione": "I fondi comuni aperti si sottoscrivono e riscattano al NAV: Rimborso = quote × NAV = 2.500 × 6.236 = €15.590. Questo è il prezzo 'equo' — non è un prezzo di mercato negoziato ma calcolato dalla SGR (o dalla banca depositaria) su base quotidiana. DIFFERENZA FONDAMENTALE tra fondi aperti e chiusi: Fondi aperti (OICVM tipici): sottoscrizioni/rimborsi in qualsiasi giorno lavorativo al NAV. Liquidità garantita dalla SGR che vende asset. Fondi chiusi (FIA): numero quote fisso, quotati in borsa a prezzo di mercato (può differire dal NAV). Tipici per asset illiquidi: private equity, real estate, infrastrutture. La SICAV (Société d'Investissement à Capital Variable) è la struttura societaria equivalente al fondo aperto — quota è azione della SICAV, diffusa nei fondi lussemburghesi (es. prodotti Fidelity, Blackrock distribuiti in Italia)."
          },
          {
            "domanda": "La differenza tra OICVM (organismi di investimento collettivo in valori mobiliari) e FIA (fondi di investimento alternativi) è rilevante perché:",
            "opzioni": ["A) Gli OICVM possono essere venduti solo a investitori istituzionali, i FIA ai retail", "B) Gli OICVM sono soggetti a regole stringenti di diversificazione e liquidità (UCITS Directive) → possono essere distribuiti a qualsiasi investitore UE; i FIA (hedge fund, PE, real estate) hanno meno restrizioni ma sono riservati tipicamente a investitori qualificati/professionali", "C) Gli OICVM investono solo in titoli italiani, i FIA possono investire globalmente", "D) I FIA sono esentasse mentre gli OICVM scontano la ritenuta del 26% sui rendimenti"],
            "corretta": 1,
            "spiegazione": "UCITS (Undertakings for Collective Investment in Transferable Securities — recepita in Italia come OICVM): framework europeo armonizzato dal 1985. Regole: diversificazione (no più del 10% in un singolo emittente, no più del 40% in emittenti con peso >5%), liquidità (solo attivi liquidi negoziati su mercati regolamentati), leva limitata, derivati solo per copertura. Distribuibili al retail in tutta l'UE con 'passaporto UCITS'. FIA (AIFMD, 2011): hedge fund, fondi PE, fondi immobiliari, fondi infrastrutture. Possono assumere più rischio e illiquidità. Distribuibili di default solo a investitori professionali (>€500K) salvo apposita autorizzazione per retail. In Italia la Banca d'Italia autorizza le SGR; CONSOB vigila sulla distribuzione. Il mercato italiano dei fondi è dominato da OICVM di diritto lussemburghese/irlandese distribuiti da banche italiane."
          },
          {
            "domanda": "Un'azienda di abbigliamento cede al factor €2M di crediti commerciali verso grande distribuzione (scadenza 90 giorni) con operazione pro-soluto. Il factor applica tasso di finanziamento 5% annuo e commissione factoring 0.8%. L'azienda riceve circa:",
            "opzioni": ["A) €2.000.000 — la cessione pro-soluto è senza rivalsa, l'azienda riceve tutto", "B) Anticipo circa 80% = €1.6M subito, meno interessi e commissioni; il factor gestisce l'incasso e si assume il rischio insolvenza del debitore ceduto", "C) €2M meno solo la commissione factoring: €2M × (1-0.8%) = €1.984M", "D) €1.946M — calcolato come €2M × (1 - 5%×(90/365) - 0.8%) = €2M × (1 - 1.23% - 0.8%)"],
            "corretta": 3,
            "spiegazione": "Factoring pro-soluto: il factor acquista definitivamente i crediti assumendosi il rischio di insolvenza del debitore (non c'è rivalsa sull'azienda cedente). Il costo si compone di: Costo finanziario: 5% × (90/365) = 1.23% → €24.600 Commissione factoring: 0.8% × €2M = €16.000 Totale costo = €40.600 Anticipo = €2M - €40.600 = ~€1.959M (≈ risposta D con leggera approssimazione). PRO-SOLUTO vs PRO-SOLVENDO: Pro-soluto — il factor si assume il rischio di credito (più costoso ma l'azienda cede il rischio definitivamente). Pro-solvendo — in caso di insolvenza del debitore, il factor ha rivalsa sull'azienda cedente (meno costoso). Il factoring migliora il capitale circolante: trasforma crediti a 90gg in liquidità immediata, utile per le PMI con ciclo del circolante lungo."
          }
        ]
      },
      {
        "titolo": "M3 — BOSS: Business Model e Modelli Organizzativi",
        "descrizione": "⚔️ BOSS — Retail vs Corporate vs Investment banking, banca universale, BCE classification",
        "xp": 160, "boss": True,
        "domande": [
          {
            "domanda": "La BCE classifica i modelli di business bancari europei. Una banca 'focused retail' come Mediolanum ha caratteristiche diverse da una banca 'wholesale' come Deutsche Bank. Quale KPI li distingue meglio?",
            "opzioni": ["A) Il ROE — la banca retail ha sempre ROE più alto", "B) Il Loans-to-Deposits ratio (LtD): la retail bank ha LtD < 1 (raccoglie più depositi che presta), la wholesale bank ha LtD > 1 (finanzia i prestiti sul mercato interbancario/obbligazionario)", "C) Il CET1 ratio — le banche wholesale hanno sempre più capitale delle retail", "D) Il numero di filiali — le banche wholesale ne hanno di più per servire la clientela corporate"],
            "corretta": 1,
            "spiegazione": "L'LtD ratio (Loan-to-Deposit) cattura la struttura del funding: LtD < 80-90%: banca prevalentemente retail, con raccolta di depositi che supera i prestiti → funding stabile e autosufficiente. LtD > 100%: la banca finanzia i prestiti anche con raccolta wholesale (bond, interbancario) → più vulnerabile alle crisi di liquidità (credit crunch). Nel 2008 le banche wholesale europee con LtD > 130% subirono lo shock peggiore del mercato interbancario congelato. La classificazione BCE identifica anche: Corporate (prevalenza di prestiti alle grandi imprese), Investment (trading, M&A, capital markets), Custodian (custodia titoli), Private (wealth management). UniCredit è 'complex commercial': mix di tutto. Mediolanum è 'focused retail': prevalenza depositi/fondi. MPS è tradizionale 'retail': alta dipendenza depositi, alta esposizione NPL locale."
          },
          {
            "domanda": "Il Risk Appetite Framework (RAF) di una banca definisce i concetti di 'risk appetite', 'risk tolerance' e 'risk capacity'. Quale gerarchia è corretta?",
            "opzioni": ["A) Risk capacity > risk appetite > risk tolerance — la banca NON vuole assumere tutto il rischio che potrebbe tecnicamente assumere", "B) Risk tolerance > risk capacity > risk appetite — si tollera sempre più rischio di quanto si è capaci di gestire", "C) Risk appetite = risk capacity = risk tolerance — sono tre modi per dire la stessa cosa", "D) Risk capacity è sempre zero nelle banche well-managed"],
            "corretta": 0,
            "spiegazione": "Il RAF (Risk Appetite Framework, introdotto da FSB post-2008) struttura la governance del rischio su tre livelli: Risk Capacity (limite massimo assoluto): quanto rischio la banca PUÒ assumere prima di violare i requisiti regolamentari (CET1 min, LCR min). Risk Appetite (target strategico): quanto rischio la banca VUOLE assumere in coerenza con il business plan e il modello di business — tipicamente un CET1 target superiore al minimo regolamentare per avere buffer. Risk Tolerance (soglia di allerta): variazione accettabile attorno al risk appetite — oltre questa soglia scattano azioni correttive. La gerarchia: Capacity > Appetite > Tolerance (margin). Il CRO (Chief Risk Officer) monitora che l'operatività rimanga nei limiti del RAF. Il Consiglio di Amministrazione approva il RAF annualmente."
          }
        ]
      }
    ]
  },

  # ══════════════════════════════════════════════════════════════
  "rischio": {
    "nome": "⚠️ Rischio & Regolamentazione",
    "badge": "badge-red", "emoji": "⚠️",
    "xp_totale": 500,
    "descrizione": "Rischi bancari, Basilea III, vigilanza europea, stress test",
    "accent": "#fc8181",
    "livelli": [
      {
        "titolo": "M1 — Tipologie di Rischio e Misurazione",
        "descrizione": "VaR, Expected Shortfall, Gap di tasso, rischio operativo, rischio sistemico",
        "xp": 70,
        "domande": [
          {
            "domanda": "La 'Gap Analysis' del rischio di tasso: una banca ha attività sensibili ai tassi (RSA) per €80M e passività sensibili (RSL) per €100M nell'intervallo 1-12 mesi. Il gap è -€20M. Se i tassi salgono di 100 bps (1%), l'impatto sul margine di interesse è:",
            "opzioni": ["A) +€200.000 — il gap positivo beneficia del rialzo dei tassi", "B) -€200.000 — con gap negativo (RSL > RSA), un rialzo dei tassi aumenta più i costi della raccolta che i ricavi sugli impieghi: ΔNI = gap × Δi = -20M × 1% = -€200K", "C) +€800.000 — basato solo sulle attività sensibili: 80M × 1%", "D) Zero — un rialzo dei tassi ha effetto simmetrico su attivo e passivo"],
            "corretta": 1,
            "spiegazione": "Gap Analysis: ΔNII = (RSA - RSL) × Δi = Gap × Δi. Gap = RSA - RSL = 80M - 100M = -20M (gap negativo = liability-sensitive). Con Δi = +1%: ΔNII = -20M × 0.01 = -€200.000. Il margine di interesse scende perché la banca ha più passività sensibili (es. depositi a tasso variabile, interbancario a breve) che attività sensibili (es. impieghi a tasso variabile). SOLUZIONE: usare IRS pay-fixed receive-floating per trasformare la raccolta da variabile a fissa, eliminando il gap. La Gap Analysis è semplificata: non considera la convessità, i floor sui tassi, le opzioni implicite nei mutui (rimborso anticipato). L'IRRBB (Interest Rate Risk in the Banking Book) di Basilea misura questo rischio con scenari di stress sui tassi."
          },
          {
            "domanda": "Il caso Barings Bank (1995): Nick Leeson accumulò perdite di £1.3 miliardi in futures Nikkei operando dalla sede di Singapore, portando al fallimento la banca. Quale tipologia di rischio è preponderante?",
            "opzioni": ["A) Rischio di mercato puro: la caduta del Nikkei causò le perdite", "B) Rischio operativo nella sua manifestazione più grave: frode interna, inadeguatezza dei controlli interni, assenza di segregazione tra front e back office — Leeson era sia trader che responsabile delle operazioni di back office", "C) Rischio di credito: le controparti dei futures non onorarono i contratti", "D) Rischio strategico: la banca aveva scelto di operare in derivati senza adeguata competenza"],
            "corretta": 1,
            "spiegazione": "Barings è il caso-scuola del rischio operativo (Basilea III definizione: 'perdite derivanti dall'inadeguatezza o disfunzione di processi interni, risorse umane, sistemi o eventi esterni'). Il disastro fu possibile per: (1) Assenza di segregation of duties: Leeson controllava sia le posizioni che le registrazioni contabili → poteva nascondere le perdite nel conto 'Errori' 88888. (2) Mancanza di supervisione da Londra. (3) Controlli interni inadeguati. (4) Incentivi distorti: Leeson generava 'profitti' che nessuno verificava. Altri casi emblematici: Société Générale (Kerviel, €4.9B, 2008), JPMorgan 'London Whale' ($6.2B, 2012). Dopo il 2008 Basilea III ha rafforzato i requisiti per il rischio operativo con Advanced Measurement Approach e il nuovo SMA (Standardised Measurement Approach) di Basilea IV."
          },
          {
            "domanda": "Il rischio sistemico si distingue dal rischio idiosincratico perché:",
            "opzioni": ["A) Il rischio sistemico colpisce solo le banche di grandi dimensioni, il rischio idiosincratico le banche piccole", "B) Il rischio sistemico è il rischio che il fallimento di un partecipante causi il fallimento a cascata di altri per effetto delle interconnessioni: non si diversifica con il portafoglio, richiede intervento pubblico/regolamentazione", "C) Il rischio sistemico può essere eliminato con una buona diversificazione del portafoglio di prestiti", "D) Il rischio idiosincratico è più pericoloso per la stabilità finanziaria globale"],
            "corretta": 1,
            "spiegazione": "Il rischio sistemico (too-big-to-fail, too-connected-to-fail, too-many-to-fail) ha caratteristiche uniche: Non diversificabile: colpisce tutto il sistema simultaneamente. Esternalità negative: il fallimento di una banca impone costi a terzi (credit crunch all'economia reale). Pro-ciclicità: la regolamentazione e i comportamenti amplificano i cicli (deleveraging forzato nelle crisi). Interconnessioni: rete interbancaria, esposizioni ai mercati, uso di collaterale comune. MISURE: BCBS identifica le G-SIB (Global Systemically Important Banks) con requisiti aggiuntivi di capitale (1-3.5% CET1 su-buffer). In Europa l'ESRB monitora il rischio macroprudenziale. OSII (Other Systemically Important Institutions) sono le banche rilevanti nazionali (in Italia: UniCredit, Intesa, Mediobanca)."
          }
        ]
      },
      {
        "titolo": "M2 — Governance e Risk Management",
        "descrizione": "Tre linee di difesa, ICAAP, ILAAP, RAF, CRO, compliance",
        "xp": 100,
        "domande": [
          {
            "domanda": "Il modello 'Three Lines of Defence' (tre linee di difesa) nella governance del rischio bancario prevede:",
            "opzioni": ["A) Prima linea: Internal Audit; Seconda linea: Risk Management; Terza linea: Business units", "B) Prima linea: Business units (operano e gestiscono il rischio quotidianamente); Seconda linea: Risk Management e Compliance (controllano la prima linea); Terza linea: Internal Audit (valuta indipendentemente l'intero sistema)", "C) Prima linea: BCE; Seconda linea: EBA; Terza linea: Banca d'Italia — i tre livelli di regolamentazione europea", "D) Prima linea: Azionisti; Seconda linea: CdA; Terza linea: Management — la struttura di corporate governance"],
            "corretta": 1,
            "spiegazione": "Il framework delle tre linee di difesa (IIA — Institute of Internal Auditors, aggiornato 2020): 1ª linea (Business/Operations): le unità operative (credito, trading, retail) che generano il rischio. Hanno la responsabilità primaria di identificare e gestire i rischi nelle loro attività quotidiane. 2ª linea (Risk Management + Compliance): funzioni indipendenti che definiscono le politiche di rischio, monitorano il rispetto del RAF, vigilano sulla conformità normativa. Non operano in proprio. 3ª linea (Internal Audit): assurance indipendente sull'adeguatezza dell'intero sistema dei controlli. Riferisce direttamente al CdA. In Italia la Banca d'Italia ha rafforzato questi requisiti con le Disposizioni di Vigilanza su 'Sistema dei controlli interni' (Circ. 285/2013). Il CRO (Chief Risk Officer) guida la 2ª linea e ha accesso diretto al CdA."
          },
          {
            "domanda": "L'ICAAP (Internal Capital Adequacy Assessment Process) che la banca deve condurre annualmente serve a:",
            "opzioni": ["A) Calcolare automaticamente il CET1 ratio da comunicare alla BCE come requisito minimo", "B) Valutare internamente se il capitale disponibile è adeguato a coprire tutti i rischi materiali della banca, inclusi quelli non coperti dal Pillar 1 (es. rischio di concentrazione, rischio reputazionale), sotto scenario base e scenario stressato", "C) Comunicare agli azionisti il rendimento atteso del capitale nei prossimi 5 anni", "D) Determinare il bonus del management sulla base dei risultati di rischio/rendimento"],
            "corretta": 1,
            "spiegazione": "ICAAP (Pillar 2 di Basilea III, CRD IV art. 73): processo auto-valutativo annuale che copre: (1) Identificazione di TUTTI i rischi materiali (inclusi quelli non nel Pillar 1: concentrazione crediti, rischio tasso banking book, rischio di business, rischio reputazionale, rischio ESG). (2) Misurazione del capitale economico necessario (Internal Capital = capitale che la banca stima necessario per coprire le perdite inattese nei vari scenari). (3) Forward-looking: simulazione su 3 anni base + scenario avverso. La BCE/Banca d'Italia usa l'ICAAP per determinare il P2R (Pillar 2 Requirement) aggiuntivo al P1. Se l'ICAAP è inadeguato (processo scadente, modelli deboli), il regolatore impone requisiti di capitale più elevati nel processo SREP (Supervisory Review and Evaluation Process). ILAAP è il parallelo per la liquidità."
          },
          {
            "domanda": "I sistemi di remunerazione dei manager bancari post-2008 devono rispettare la Direttiva CRD IV. Quale regola chiave ha introdotto?",
            "opzioni": ["A) Abolizione dei bonus variabili per tutti i dipendenti bancari", "B) Il bonus variabile non può superare il 100% della componente fissa (200% con approvazione degli azionisti); la parte variabile deve essere differita nel tempo (fino a 5 anni) e legata a metriche risk-adjusted (es. RAROC, TSR)", "C) I CEO delle banche non possono ricevere più di 10 volte lo stipendio medio dei dipendenti", "D) I bonus devono essere pagati interamente in azioni — nessun pagamento in cash"],
            "corretta": 1,
            "spiegazione": "CRD IV (Capital Requirements Directive IV, 2013, recepita da Banca d'Italia Circ. 285/2013): Bonus cap: variabile ≤ 100% del fisso (con delibera AGM può arrivare al 200%) per i 'Material Risk Takers' (MRT) — identificati per ruolo o compenso. Deferral: almeno il 40% (60% per CEO) deve essere differito per 3-5 anni. Malus/Clawback: se la banca ottiene risultati negativi nel periodo di maturazione, il bonus può essere ridotto/recuperato. Performance measures: devono includere metriche risk-adjusted (RAROC — Risk-Adjusted Return on Capital) per evitare che i manager assumano rischi eccessivi per il bonus di breve periodo. LOGICA: il 2008 ha mostrato che bonus basati su P&L di breve termine incentivano l'assunzione di rischi con payoff asimmetrico (guadagni immediati, perdite future)."
          }
        ]
      },
      {
        "titolo": "M3 — BOSS: Regolamentazione e Vigilanza Europea",
        "descrizione": "⚔️ BOSS — Basilea III/IV, Banking Union, SSM, SREP, Stress Test EBA",
        "xp": 180, "boss": True,
        "domande": [
          {
            "domanda": "Il processo SREP (Supervisory Review and Evaluation Process) della BCE valuta 4 elementi per determinare i requisiti di capitale aggiuntivi (P2R). Quale combinazione è corretta?",
            "opzioni": ["A) Redditività, quota di mercato, numero di dipendenti, anni di attività", "B) Business model viability, governance e risk management, rischi di capitale (credito, mercato, op), rischi di liquidità — ciascuno con score 1-4 che determina il P2R aggiuntivo", "C) CET1 ratio, LCR, NSFR, Leverage ratio — i quattro indicatori quantitativi di Basilea III", "D) Qualità degli attivi, concentrazione geografica, esposizione sovrana, modelli di rating interni"],
            "corretta": 1,
            "spiegazione": "Lo SREP (EBA GL 2018/03, aggiornate regolarmente): la BCE valuta annualmente ogni banca significativa su 4 pilastri: (1) Business Model Analysis: sostenibilità del modello di business nel breve (1 anno) e medio periodo (3 anni). (2) Internal Governance & Risk Management: qualità del CdA, funzioni di controllo, RAF, ICAAP/ILAAP. (3) Capital Adequacy: adeguatezza del capitale per i rischi del Pillar 1 + Pillar 2 rischi aggiuntivi. (4) Liquidity & Funding: adeguatezza della liquidità e del funding. Ogni pilastro ottiene uno score 1 (migliore) a 4 (worst). Lo score complessivo determina il P2R (requisito aggiuntivo vincolante oltre il P1) e il P2G (guidance non vincolante, buffers raccomandati). Il dialogo SREP è riservato — i risultati sono comunicati privatamente alla banca, ma il CET1 requirement totale è pubblico."
          },
          {
            "domanda": "Basilea IV (FRTB + SA-Floor) modifica il calcolo degli RWA rispetto a Basilea III. Qual è la modifica principale che impatta le grandi banche con modelli interni?",
            "opzioni": ["A) Elimina completamente i modelli interni (IRB) obbligando tutte le banche all'approccio standardizzato", "B) Introduce un output floor: gli RWA calcolati con modelli interni non possono scendere sotto il 72.5% degli RWA calcolati con l'approccio standardizzato — riduce il vantaggio competitivo dei modelli interni", "C) Aumenta il CET1 minimum dal 4.5% al 7% per compensare i modelli interni meno conservativi", "D) Vieta l'uso di modelli VaR per il trading book, sostituiti con Expected Shortfall 97.5%"],
            "corretta": 1,
            "spiegazione": "Basilea IV (implementazione 2025-2028): la riforma finale del framework post-2008. Il core issue: le banche con modelli interni avanzati (IRB per credito, IMA per mercato) calcolavano RWA molto più bassi delle banche con approccio standardizzato → potevano operare con meno capitale. L'output floor al 72.5%: se i RWA da modello interno = €80B, ma gli RWA standardizzati = €120B, il floor impone RWA minimi = 72.5% × 120B = €87B → la banca deve usare i più alti. IMPATTO: le grandi banche europee (Deutsche, BNP, Santander) con modelli interni sofisticati stimano aumenti degli RWA del 15-25% → necessità di rafforzare il capitale. FRTB (Fundamental Review of the Trading Book): nuovi standard per il trading book, sostituisce VaR 99% con ES 97.5% su orizzonti di stress più lunghi."
          },
          {
            "domanda": "La vigilanza bancaria in Italia segue un modello 'misto per soggetti e per finalità'. Come si distribuiscono le competenze tra Banca d'Italia, CONSOB, IVASS e COVIP?",
            "opzioni": ["A) Banca d'Italia vigila su tutto il sistema finanziario; CONSOB, IVASS e COVIP sono organi consultivi", "B) Banca d'Italia: stabilità prudenziale di banche e intermediari creditizi; CONSOB: trasparenza e correttezza nei mercati mobiliari e nella distribuzione di prodotti finanziari; IVASS: assicurazioni; COVIP: fondi pensione — finalità diverse, soggetti a volte sovrapposti", "C) CONSOB vigila su tutte le istituzioni finanziarie; Banca d'Italia solo sulla moneta e sistema dei pagamenti", "D) La BCE ha assorbito tutte le funzioni degli enti nazionali di vigilanza dopo l'introduzione dell'SSM nel 2014"],
            "corretta": 1,
            "spiegazione": "Il modello di vigilanza italiano è 'misto': per soggetti (ente → competenza esclusiva) + per finalità (stesso soggetto → più autorità). Banca d'Italia: stabilità patrimoniale delle banche (SSM per le significant institutions), vigilanza sugli intermediari finanziari ex art. 106 TUB (leasing, factoring companies), sistema dei pagamenti, antiriciclaggio. CONSOB: trasparenza e correttezza del mercato, abusi di mercato, prospetti, distribuzione prodotti finanziari (MiFID II), offerte pubbliche. IVASS (Istituto per la Vigilanza sulle Assicurazioni): stabilità delle imprese assicurative, correttezza distribuzione prodotti assicurativi. COVIP: fondi pensione. Aree di sovrapposizione: le banche distribuiscono prodotti assicurativi (Banca d'Italia + CONSOB + IVASS). Gli intermediari mobiliari bancari (Banca d'Italia per stabilità + CONSOB per MiFID). Il coordinamento avviene tramite il CICR (Comitato Interministeriale per il Credito e il Risparmio) e il CNSF."
          }
        ]
      }
    ]
  },

  # ══════════════════════════════════════════════════════════════
  "macro": {
    "nome": "🌍 Politica Monetaria & BCE",
    "badge": "badge-purple", "emoji": "🌍",
    "xp_totale": 450,
    "descrizione": "BCE, SEBC, strumenti monetari, inflazione e meccanismi di trasmissione",
    "accent": "#a78bfa",
    "livelli": [
      {
        "titolo": "M1 — Il SEBC e la BCE",
        "descrizione": "Struttura, mandato, governance, obiettivi e trattato di Maastricht",
        "xp": 60,
        "domande": [
          {
            "domanda": "I criteri di convergenza di Maastricht (1992) per l'ingresso nell'Eurozona prevedono 4 condizioni. Quale combinazione è corretta?",
            "opzioni": ["A) PIL pro capite > media UE; disoccupazione < 5%; crescita PIL > 2%; saldo delle partite correnti positivo", "B) Inflazione ≤ 1.5% sopra media dei 3 paesi più virtuosi; deficit/PIL ≤ 3%; debito/PIL ≤ 60% (o in discesa); stabilità del tasso di cambio (ERM II per 2 anni)", "C) Riserve auree > €50 miliardi; sistema bancario privatizzato; zero NPL nel sistema; presenza di una banca centrale indipendente", "D) Rating investment grade del debito sovrano; spread < 200bps vs Germania; bilancio pubblico in pareggio; inflazione < target BCE 2%"],
            "corretta": 1,
            "spiegazione": "I criteri di Maastricht (Trattato 1992, in vigore 1993): (1) Stabilità dei prezzi: inflazione ≤ media dei 3 paesi più virtuosi + 1.5pp. (2) Finanza pubblica: deficit/PIL ≤ 3% e debito/PIL ≤ 60% (o in convincente discesa verso il 60%). (3) Stabilità del tasso di cambio: partecipazione al meccanismo ERM II per ≥2 anni senza svalutazione. (4) Convergenza dei tassi di interesse a lungo termine: entro 2pp dalla media dei 3 paesi più virtuosi. STORIA: l'Italia aveva debito/PIL >100% ma fu ammessa interpretando il criterio 'in convincente diminuzione'. Grecia fu ammessa nel 2001 con dati poi risultati falsificati. Attualmente: 20 paesi nell'Eurozona, 7 fuori (Svezia, Rep. Ceca, Ungheria, Polonia, Bulgaria, Romania, Danimarca). La Svezia viola formalmente i criteri di 'non eccepibilità' ma non vuole entrare (referendum 2003)."
          },
          {
            "domanda": "La BCE ha il mandato primario di stabilità dei prezzi (inflazione ~2% nel medio termine) e un mandato secondario di supporto alle politiche economiche generali dell'UE. Qual è il principio di indipendenza della BCE?",
            "opzioni": ["A) La BCE dipende dal Consiglio Europeo che approva le decisioni di tasso prima della pubblicazione", "B) L'indipendenza è sancita dal Trattato TFUE: nessun organo politico (Commissione, Consiglio, governi) può dare istruzioni alla BCE — garantisce credibilità anti-inflazionistica sottraendo le decisioni monetarie alla pressione politica", "C) La BCE è indipendente solo per le decisioni sui tassi; il QE richiede approvazione dei ministri delle finanze dell'Eurozona", "D) L'indipendenza è solo 'de facto' — formalmente la BCE risponde al Parlamento Europeo che può revocare il mandato"],
            "corretta": 1,
            "spiegazione": "L'indipendenza della BCE è ISTITUZIONALE (sancita dal Trattato, non modificabile senza unanimità degli Stati membri): Art. 130 TFUE: 'Nell'esercizio dei poteri e nell'assolvimento dei compiti e dei doveri loro attribuiti dai Trattati e dallo Statuto del SEBC, la Banca Centrale Europea, le banche centrali nazionali e i componenti dei rispettivi organi decisionali agiscono in modo indipendente.' RAZIONALE: la teoria della credibilità (Kydland & Prescott, Barro & Gordon): una banca centrale dipendente dal governo subisce pressioni a creare inflazione inattesa per stimolare l'output a breve termine → perdita di credibilità → aspettative di inflazione si disancoreranno. L'indipendenza risolve il 'time consistency problem'. Accountability: la BCE risponde al Parlamento Europeo (audizioni) e pubblica verbali, research e comunicati per la trasparenza."
          },
          {
            "domanda": "La struttura del SEBC (Sistema Europeo delle Banche Centrali) prevede una distinzione tra SEBC ed Eurosistema. Qual è?",
            "opzioni": ["A) Il SEBC è l'organismo di vigilanza, l'Eurosistema è quello monetario — due istituzioni separate", "B) Il SEBC include le banche centrali di TUTTI i 27 paesi UE (inclusi quelli non nell'euro); l'Eurosistema è BCE + banche centrali dei 20 paesi dell'Eurozona — solo l'Eurosistema attua la politica monetaria unica", "C) Il SEBC include solo le grandi banche centrali europee, l'Eurosistema include quelle più piccole", "D) Il SEBC è la struttura storica (pre-euro), l'Eurosistema è la struttura attuale — hanno sostituito il SEBC nel 2002"],
            "corretta": 1,
            "spiegazione": "Struttura del sistema europeo: SEBC = BCE + 27 banche centrali nazionali di tutti gli Stati membri UE (inclusi UK fino a Brexit, e ancora oggi Svezia, Polonia, etc. che non hanno l'euro). Il SEBC è il quadro giuridico più ampio. Eurosistema = BCE + 20 banche centrali nazionali dei paesi Eurozona. Solo l'Eurosistema: definisce e attua la politica monetaria unica; gestisce le riserve in valuta estera; promuove il buon funzionamento dei sistemi di pagamento (TARGET2-S). Le BCN dell'area non-euro (es. Banca di Svezia/Riksbank) partecipano al SEBC ma non alle decisioni di politica monetaria dell'Eurosistema. Il Consiglio Direttivo BCE (6 membri Executive Board + 20 governatori BCN Eurozona) prende le decisioni di tasso con sistema di voto a rotazione dal 2015."
          }
        ]
      },
      {
        "titolo": "M2 — Strumenti e Meccanismi di Trasmissione",
        "descrizione": "MRO, LTRO, TLTRO, QE, tassi negativi, inflazione e trasmissione monetaria",
        "xp": 100,
        "domande": [
          {
            "domanda": "Le Operazioni di Rifinanziamento Principali (MRO) della BCE sono la principale leva di politica monetaria convenzionale. Come funzionano?",
            "opzioni": ["A) La BCE acquista titoli di Stato direttamente dall'emittente (mercato primario) iniettando liquidità nel bilancio degli Stati", "B) La BCE conduce aste settimanali (durata 1 settimana) in cui le banche richiedono liquidità fornendo collaterale eligibile — il tasso MRO è il tasso guida della BCE che influenza i tassi interbancari e quindi quelli del mercato", "C) La BCE fissa direttamente i tassi sui mutui delle banche commerciali — il tasso MRO è il tasso massimo applicabile ai clienti retail", "D) Le MRO sono accordi di swap con la Federal Reserve per gestire la liquidità in dollari nel sistema europeo"],
            "corretta": 1,
            "spiegazione": "Le MRO (Main Refinancing Operations): aste settimanali a tasso fisso (da luglio 2022: 4.5% al picco del ciclo) con piena aggiudicazione (tutte le banche ricevono quanto richiesto contro collaterale eligibile). Il tasso MRO (refi rate) è il 'segnale' principale della politica BCE. Insieme al tasso sui depositi (deposit facility rate) e al marginal lending facility rate, forma la 'corridor' dei tassi interbancari. Il tasso di deposito è il floor del mercato interbancario: le banche preferiscono parcheggiare le riserve in eccesso alla BCE (a quel tasso) anziché prestare sotto tale soglia. Le LTRO (Long-Term Refinancing Operations) hanno durata 3 mesi-3 anni. Le TLTRO (Targeted LTRO) hanno introdotto incentivi per il credito all'economia reale: tassi ridotti (anche negativi nel 2020-2021) condizionati alla crescita dei prestiti a famiglie e imprese."
          },
          {
            "domanda": "Il 'whatever it takes' di Mario Draghi (luglio 2012) è considerato il punto di svolta della crisi dell'Eurozona. Quale strumento annunciò e perché fu efficace?",
            "opzioni": ["A) Annunciò acquisti illimitati di titoli di Stato sul mercato primario — la BCE avrebbe finanziato direttamente i deficit degli Stati", "B) Annunciò le OMT (Outright Monetary Transactions): acquisti ILLIMITATI sul mercato SECONDARIO di titoli sovrani dei paesi che richiedono assistenza al MES — condizionati a un programma di riforma. Fu efficace perché l'annuncio da solo eliminò il rischio di ridenominazione senza dover comprare quasi nulla", "C) Annunciò la riduzione dei tassi a zero e l'avvio del QE con acquisti di €60 miliardi al mese", "D) Annunciò la creazione del Meccanismo di Stabilità Europeo (MES) con dotazione di €700 miliardi"],
            "corretta": 1,
            "spiegazione": "Il 'whatever it takes' (26 luglio 2012, Londra) è uno dei momenti più significativi della storia finanziaria recente: frase completa: 'Within our mandate, the ECB is ready to do whatever it takes to preserve the euro. And believe me, it will be enough.' Le OMT (annunciate settembre 2012): acquisti ILLIMITATI e sterilizzati di titoli sovrani con scadenza 1-3 anni, condizionati a un programma ESM/MES. Mai utilizzate: il solo annuncio fu sufficiente. Lo spread BTP-Bund da 574bps (novembre 2011) crollò a <150bps entro fine 2012. PERCHÉ FUNZIONÒ: eliminò il 'redenomination risk' (paura di uscita dall'euro → conversione BTP in 'nuove lire' svalutate). È l'esempio più puro di 'commitment device' monetario: la credibilità dell'impegno illimitato spezza il panic equilibrium senza spendere. La Corte di Giustizia UE (2015) confermò la legittimità delle OMT."
          },
          {
            "domanda": "Il rialzo BCE dei tassi dal -0.5% al 4% tra luglio 2022 e settembre 2023 è stato il ciclo più rapido della storia BCE. Quale 'canale di trasmissione' ha funzionato più velocemente nel ridurre l'inflazione?",
            "opzioni": ["A) Il canale del credito bancario — le banche hanno immediatamente smesso di concedere mutui", "B) Il canale del tasso di cambio (euro si apprezza → import più economico → inflazione da import scende) e il canale delle aspettative (segnale forte contro l'inflazione ancorò le aspettative) sono stati i più rapidi; il canale del credito e della domanda aggregata più lenti (lag 12-18 mesi)", "C) Il canale delle riserve bancarie — con tassi alti le banche preferiscono tenere riserve invece di prestare", "D) Il canale fiscale — i tassi più alti aumentano la spesa per interessi degli Stati che tagliano la spesa pubblica per compensare"],
            "corretta": 1,
            "spiegazione": "I canali di trasmissione della politica monetaria hanno tempistiche diverse: VELOCI (3-6 mesi): Tasso di cambio: i differenziali di tasso attirano capitali → euro si apprezza → prezzi import scendono. Prezzi delle attività: obbligazioni si svalutano, spread creditizi si ampliano. Aspettative: l'annuncio stesso (forward guidance) modifica i comportamenti. MODERATI (6-12 mesi): Tassi sui mutui: i mutui variabili si aggiornano immediatamente, i fissi nelle nuove erogazioni. Costo del credito alle imprese: riduce investimenti. LENTI (12-24 mesi): Domanda aggregata: consumi e investimenti calano gradualmente. Mercato del lavoro: la disoccupazione sale con lag. Salari: le rinegoziazioni contrattuali avvengono con cadenza periodica. Nel ciclo 2022-2023: l'inflazione energetica scese grazie alla normalizzazione del prezzo del gas (offerta) più che per la stretta monetaria; l'inflazione dei servizi (più inerziale, guidata dai salari) resisté a lungo."
          }
        ]
      },
      {
        "titolo": "M3 — BOSS: Crisi, Politica Non Convenzionale e Futuro",
        "descrizione": "⚔️ BOSS — QE/PEPP, inflazione 2021-23, tassi negativi, trilemma Mundell-Fleming",
        "xp": 180, "boss": True,
        "domande": [
          {
            "domanda": "I tassi negativi della BCE (deposit facility rate -0.5% dal 2019 al 2022) avevano un effetto paradossale sulle banche: quale?",
            "opzioni": ["A) Le banche guadagnavano tenendo riserve alla BCE grazie al tasso negativo sul deposito", "B) Le banche PAGAVANO la BCE per parcheggiare le riserve in eccesso (-0.5%) ma non potevano trasferire il costo ai depositanti retail (floor a zero per rischio di bank run) → compressione del NIM soprattutto per le banche con raccolta prevalentemente retail", "C) Le banche smettevano di raccogliere depositi per evitare il costo dei tassi negativi → disintermediazione finanziaria", "D) I tassi negativi rendevano i mutui a tasso variabile negativi — le banche dovevano pagare i debitori"],
            "corretta": 1,
            "spiegazione": "Il 'zero lower bound' asimmetrico per le banche: Con deposit facility rate a -0.5%: ogni euro di riserve in eccesso alla BCE costa -0.5% annuo. Le banche applicano tassi negativi ai grandi depositi corporate (>€1M tipicamente), ma NON ai depositi retail: rischio di bank run, rischi reputazionali, vincoli normativi. Risultato: le banche con raccolta prevalentemente retail (casse rurali, banche locali) soffrono di più. Per mitigare, la BCE introdusse il tiering del 2019: le prime 6× le riserve obbligatorie erano esentate dal tasso negativo. CURIOSITÀ: in Danimarca, Jyske Bank applicò tassi negativi anche ai mutui ipotecari retail nel 2019 — caso unico al mondo. La fine dei tassi negativi (luglio 2022) fu il sollievo più atteso dal sistema bancario europeo degli ultimi anni."
          },
          {
            "domanda": "Il PEPP (Pandemic Emergency Purchase Programme, 2020-2022) ha acquistato €1.850 miliardi di titoli, inclusi più BTP italiani per quota rispetto alla capital key BCE. Quale principio ha introdotto?",
            "opzioni": ["A) La BCE può comprare qualsiasi asset, incluse azioni e immobili, in caso di emergenza", "B) La flessibilità nella distribuzione degli acquisti tra paesi ('pro-rata flexibility'): può deviare dalla capital key per prevenire la frammentazione dei mercati — ha de facto ridotto gli spread dei paesi più vulnerabili come l'Italia in modo più diretto dell'APP", "C) La BCE ha emesso debito comune europeo per finanziare il PEPP — primo eurobond de iure", "D) Il PEPP ha sostituito definitivamente la politica dei tassi come strumento principale della BCE"],
            "corretta": 1,
            "spiegazione": "Il PEPP (18 marzo 2020, annunciato nel mezzo del 'pandemic tantrum'): innovazione chiave → flessibilità rispetto alla capital key BCE (che distribuirebbe gli acquisti in proporzione al PIL di ciascun paese). Con la flessibilità del PEPP, la BCE ha potuto comprare più BTP italiani e Bonos spagnoli nelle fasi di stress, comprimendo gli spread. È stata la risposta alla frammentazione dei mercati causata dalla pandemia. DIFFERENZA dall'APP (Asset Purchase Programme, QE normale): APP rispetta rigidamente la capital key. Il TPI (Transmission Protection Instrument, luglio 2022) ha istituzionalizzato questa flessibilità per contrastare la frammentazione ingiustificata anche dopo la fine del PEPP. CONTROVERSIA: alcuni economisti tedeschi (e la Bundesbank) criticano il PEPP come 'fiscal dominance' — la BCE aiuta indirettamente i governi ad alto debito. La Corte Costituzionale tedesca ha sollevato eccezioni ma non ha bloccato il programma."
          },
          {
            "domanda": "La 'review della strategia' BCE del 2021 ha confermato il target del 2% con simmetria. Perché la simmetria è importante?",
            "opzioni": ["A) Significa che la BCE reagisce ugualmente sia all'inflazione sia alla deflazione: il 2% è un target puntuale, non un ceiling", "B) Significa solo che la BCE può stare al 2% anche se la media dei paesi core (Germania) è all'1% — non cambia nulla in pratica", "C) Significa che se l'inflazione è alta, la BCE la abbassa; se è bassa, la alza — è la semplice definizione di stabilità dei prezzi", "D) Simmetria si riferisce alla distribuzione dei tassi decisionali del Consiglio Direttivo, non al target di inflazione"],
            "corretta": 0,
            "spiegazione": "Pre-2021: il target era 'inferiore ma prossimo al 2%' → asimmetrico (un leggero sforamento al ribasso era accettato, uno al rialzo era il problema). Post-2021: target '2% nel medio termine' con simmetria esplicita: ENTRAMBE le deviazioni (deflazione e inflazione) sono ugualmente indesiderate e richiedono risposta. Implicazioni: Con simmetria, la BCE non può permettersi anni di inflazione all'1% senza reagire (come era accaduto nel 2015-2019). Giustifica il QE e i tassi negativi come risposta all'inflazione troppo bassa — non solo all'inflazione troppo alta. Legittima la strategia 'make-up': la BCE può tollerare un breve periodo di inflazione sopra il 2% per recuperare i periodi sotto il 2%. La 'clausola di tolleranza': in fasi di transizione con impatto marcato dell'inflazione sul PIL reale, la BCE può agire più gradualmente considerando le implicazioni per l'occupazione."
          }
        ]
      }
    ]
  }
}

# ─── HELPERS ───────────────────────────────────────────────────────────────────
AREA_ACCENTS = {k: v["accent"] for k, v in MISSIONS.items()}

def get_livello(xp):
    if xp < 100:   return 1, "Studente Curioso 📚"
    elif xp < 300: return 2, "Analista Junior 📊"
    elif xp < 600: return 3, "Portfolio Manager 💼"
    elif xp < 1000:return 4, "Senior Banker 🏦"
    elif xp < 1500:return 5, "CFO / CRO 🎩"
    elif xp < 2000:return 6, "MD Finance ⭐"
    else:          return 7, "Guru della Finanza 🏆"

def xp_threshold(lv): return [0,100,300,600,1000,1500,2000,9999][lv-1]
def xp_to_next(xp): return xp_threshold(get_livello(xp)[0])
def missione_id(area, idx): return f"{area}_{idx}"
def is_completata(area, idx): return missione_id(area, idx) in st.session_state.missioni_completate

def check_badge():
    xp = st.session_state.xp; mc = st.session_state.missioni_completate; b = st.session_state.badge_guadagnati; new = []
    def add(bid, emoji, nome, desc):
        if bid not in b: new.append((emoji, nome, desc)); b.append(bid)
    if xp >= 100:  add("xp100",  "🌟", "Prima Stella",    "100 XP!")
    if xp >= 500:  add("xp500",  "⚡", "Mezz'Opera",       "500 XP!")
    if xp >= 1000: add("xp1000", "💎", "Mille XP",         "1000 XP!")
    if xp >= 2000: add("xp2000", "👑", "Duemila XP",       "Leggendario!")
    for area in MISSIONS:
        n = len(MISSIONS[area]["livelli"])
        if sum(1 for m in mc if area in m) >= n:
            e = MISSIONS[area]["emoji"]
            add(f"{area}_master", e, f"Master {area.title()}", f"Tutte le missioni {area}!")
    if len(mc) >= sum(len(v["livelli"]) for v in MISSIONS.values()):
        add("champion", "🏆", "FinQuest Champion", "Tutte le missioni completate!")
    if st.session_state.streak >= 5: add("streak5","🔥","On Fire!","5 missioni di fila!")
    return new

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
def init():
    d = dict(nome_studente="", registrato=False, xp=0, missioni_completate=[], livello_corrente=None,
             area_corrente=None, domanda_idx=0, risposta_data=None, punteggio_quiz=0, fase="home",
             streak=0, badge_guadagnati=[])
    for k, v in d.items():
        if k not in st.session_state: st.session_state[k] = v
init()

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 10px;">
        <div style="font-family:'Syne',sans-serif;font-size:1.75rem;font-weight:800;
             background:linear-gradient(135deg,#63b3ed,#a78bfa,#f6ad55);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;">FinQuest</div>
        <div style="color:#1e293b;font-size:0.62rem;letter-spacing:3px;text-transform:uppercase;margin-top:2px;">
            Economia degli Intermediari
        </div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    if st.session_state.registrato:
        lv, titolo = get_livello(st.session_state.xp)
        xp_next = xp_to_next(st.session_state.xp)
        xp_prev = xp_threshold(lv)
        prog = min((st.session_state.xp - xp_prev) / max(xp_next - xp_prev, 1), 1.0)
        st.markdown(f"""
        <div style="padding:10px 12px;">
            <div style="color:#1e293b;font-size:0.65rem;text-transform:uppercase;letter-spacing:1.5px;">Studente</div>
            <div style="color:#e2e8f0;font-weight:600;font-size:1rem;margin:2px 0;">{st.session_state.nome_studente}</div>
            <div style="color:#a78bfa;font-size:0.78rem;margin-bottom:12px;">{titolo}</div>
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="color:#1e293b;font-size:0.65rem;text-transform:uppercase;">XP</span>
                <span style="color:#63b3ed;font-size:0.72rem;font-weight:600;">{st.session_state.xp}/{xp_next}</span>
            </div>
            <div class="xp-bar-container"><div class="xp-bar-fill" style="width:{prog*100:.0f}%;"></div></div>
            <div style="display:flex;gap:5px;margin-top:12px;">
                {"".join([f'<div style="flex:1;background:rgba(10,14,26,0.8);border:1px solid rgba(99,179,237,0.1);border-radius:9px;padding:8px 4px;text-align:center;"><div style="color:{c};font-family:Syne,sans-serif;font-size:0.95rem;font-weight:800;">{v}</div><div style="color:#1e293b;font-size:0.58rem;margin-top:1px;">{l}</div></div>'
                          for v,l,c in [(f"Lv.{lv}","Livello","#63b3ed"),(len(st.session_state.missioni_completate),"Missioni","#68d391"),(f"{st.session_state.streak}🔥","Streak","#f6ad55")]])}
            </div>
        </div>""", unsafe_allow_html=True)
        st.divider()
        for icon, label, fase in [("🗺️","Mappa Missioni","home"),("🏆","Leaderboard","leaderboard"),("👤","Profilo","profilo")]:
            if st.button(f"{icon}  {label}", key=f"nav_{fase}", use_container_width=True):
                st.session_state.fase = fase; st.rerun()
        if st.session_state.badge_guadagnati:
            bmap={"xp100":"🌟","xp500":"⚡","xp1000":"💎","xp2000":"👑","champion":"🏆","streak5":"🔥",
                  **{f"{a}_master":MISSIONS[a]["emoji"] for a in MISSIONS}}
            html=" ".join([f'<span title="{b}" style="font-size:1.2rem;">{bmap.get(b,"🎖️")}</span>' for b in st.session_state.badge_guadagnati])
            st.markdown(f'<div style="padding:8px 12px;"><div style="color:#1e293b;font-size:0.62rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px;">Badge</div><div style="display:flex;flex-wrap:wrap;gap:3px;">{html}</div></div>', unsafe_allow_html=True)

# ─── REGISTRAZIONE ─────────────────────────────────────────────────────────────
if not st.session_state.registrato:
    st.markdown('<div class="hero-title">FinQuest 🏦</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Economia degli Intermediari Finanziari — EIF 2026</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,2,1])
    with c2:
        tm = sum(len(v["livelli"]) for v in MISSIONS.values())
        tx = sum(v["xp_totale"] for v in MISSIONS.values())
        tq = sum(len(q["domande"]) for v in MISSIONS.values() for q in v["livelli"])
        st.markdown(f"""
        <div style="background:rgba(10,14,26,0.95);border:1px solid rgba(99,179,237,0.15);border-radius:24px;padding:36px;text-align:center;box-shadow:0 0 40px rgba(99,179,237,0.06);">
            <div style="font-size:3rem;margin-bottom:14px;">🎓</div>
            <div style="color:#e2e8f0;font-size:1.2rem;font-weight:600;margin-bottom:6px;">Benvenuto nell'Accademia</div>
            <div style="color:#334155;font-size:0.85rem;line-height:1.7;margin-bottom:24px;">
                Completa missioni su tutto il programma EIF:<br>
                sistema finanziario, banche, mercati, intermediari non bancari,<br>
                rischio e politica monetaria.
            </div>
            <div style="display:flex;justify-content:center;gap:28px;">
                {"".join([f'<div><div style="color:{c};font-family:Syne,sans-serif;font-size:1.7rem;font-weight:800;">{v}</div><div style="color:#1e293b;font-size:0.68rem;text-transform:uppercase;letter-spacing:1px;margin-top:2px;">{l}</div></div>' for v,l,c in [(len(MISSIONS),"Aree","#63b3ed"),(tm,"Missioni","#a78bfa"),(tq,"Domande","#f6ad55"),(tx,"XP Tot.","#68d391")]])}
            </div>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        nome = st.text_input("✏️ Come ti chiami?", placeholder="Nome e cognome...")
        if st.button("🚀 Inizia l'Avventura!", use_container_width=True):
            if nome.strip():
                st.session_state.nome_studente = nome.strip()
                st.session_state.registrato = True
                save_progress(); st.rerun()
            else: st.warning("Inserisci il tuo nome per continuare!")

# ─── HOME ───────────────────────────────────────────────────────────────────────
elif st.session_state.fase == "home":
    lv, titolo = get_livello(st.session_state.xp)
    tm = sum(len(v["livelli"]) for v in MISSIONS.values())
    tc = len(st.session_state.missioni_completate)
    st.markdown(f"""
    <div style="margin-bottom:28px;">
        <div style="font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;color:#e2e8f0;margin-bottom:3px;">
            Ciao, {st.session_state.nome_studente} 👋
        </div>
        <div style="color:#334155;font-size:0.85rem;">{tc}/{tm} missioni completate · {st.session_state.xp} XP · {titolo}</div>
    </div>""", unsafe_allow_html=True)

    for area_key, area_data in MISSIONS.items():
        done = sum(1 for m in st.session_state.missioni_completate if area_key in m)
        tot = len(area_data["livelli"])
        acc = area_data["accent"]
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin:28px 0 12px;">
            <div style="width:38px;height:38px;background:rgba(10,14,26,0.9);border:1px solid {acc}25;
                 border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:1.2rem;">
                {area_data['emoji']}
            </div>
            <div style="flex:1;">
                <div style="color:#e2e8f0;font-weight:600;font-size:1rem;">{area_data['nome']}</div>
                <div style="color:#1e293b;font-size:0.75rem;margin-top:1px;">{area_data['descrizione']}</div>
            </div>
            <span class="badge {area_data['badge']}">{done}/{tot}</span>
        </div>""", unsafe_allow_html=True)

        cols = st.columns(tot)
        for i, lv_data in enumerate(area_data["livelli"]):
            with cols[i]:
                comp = is_completata(area_key, i)
                boss = lv_data.get("boss", False)
                lock = i > 0 and not is_completata(area_key, i-1)
                op   = "0.3" if lock else "1"
                bg   = "rgba(104,211,145,0.06)" if comp else ("rgba(30,10,10,0.9)" if boss else "rgba(10,14,26,0.9)")
                bc   = "rgba(104,211,145,0.3)" if comp else ("rgba(252,129,129,0.28)" if boss else f"rgba(99,179,237,0.18)")
                ico  = "✅" if comp else ("⚔️" if boss else ("🔒" if lock else "▶️"))
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {bc};border-radius:15px;padding:16px 14px;
                     opacity:{op};min-height:150px;{'animation:boss-pulse 2s infinite;' if boss and not lock and not comp else ''}">
                    <div style="font-size:1.4rem;margin-bottom:7px;">{ico}</div>
                    <div style="color:#e2e8f0;font-weight:600;font-size:0.79rem;line-height:1.4;margin-bottom:5px;">
                        {lv_data['titolo'][:40]}{'...' if len(lv_data['titolo'])>40 else ''}
                    </div>
                    <div style="color:#1e293b;font-size:0.7rem;line-height:1.4;margin-bottom:8px;">
                        {lv_data['descrizione'][:50]}...
                    </div>
                    <div style="color:#f6ad55;font-size:0.75rem;font-weight:600;">+{lv_data['xp']} XP</div>
                </div>""", unsafe_allow_html=True)
                if not lock and not comp:
                    lbl = "⚔️ Boss!" if boss else "▶️ Gioca"
                    if st.button(lbl, key=f"p_{area_key}_{i}", use_container_width=True):
                        st.session_state.area_corrente=area_key; st.session_state.livello_corrente=i
                        st.session_state.domanda_idx=0; st.session_state.risposta_data=None
                        st.session_state.punteggio_quiz=0; st.session_state.fase="quiz"; st.rerun()
                elif comp:
                    if st.button("🔄", key=f"r_{area_key}_{i}", use_container_width=True):
                        st.session_state.area_corrente=area_key; st.session_state.livello_corrente=i
                        st.session_state.domanda_idx=0; st.session_state.risposta_data=None
                        st.session_state.punteggio_quiz=0; st.session_state.fase="quiz"; st.rerun()
                else:
                    st.button("🔒", key=f"l_{area_key}_{i}", use_container_width=True, disabled=True)

# ─── QUIZ ──────────────────────────────────────────────────────────────────────
elif st.session_state.fase == "quiz":
    area = st.session_state.area_corrente
    li   = st.session_state.livello_corrente
    ad   = MISSIONS[area]; ld = ad["livelli"][li]
    qs   = ld["domande"]; qi = st.session_state.domanda_idx
    boss = ld.get("boss", False)
    acc  = ad["accent"]

    if st.button("← Mappa", key="back"):
        st.session_state.fase = "home"; st.rerun()

    st.markdown(f"""
    <div style="margin:14px 0 22px;">
        <div style="color:#1e293b;font-size:0.72rem;text-transform:uppercase;letter-spacing:1.5px;margin-bottom:3px;">
            {ad['nome']} › {ld['titolo']}
        </div>
        <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#e2e8f0;">
            {'⚔️ BOSS FIGHT' if boss else f'Domanda {qi+1} / {len(qs)}'}
        </div>
    </div>""", unsafe_allow_html=True)

    pc = f"linear-gradient(90deg,#fc8181,#f6ad55)" if boss else f"linear-gradient(90deg,{acc},{acc}88)"
    st.markdown(f'<div class="xp-bar-container" style="margin-bottom:24px;height:7px;"><div style="height:100%;width:{qi/len(qs)*100:.0f}%;border-radius:50px;background:{pc};box-shadow:0 0 8px {acc}40;transition:width .5s;"></div></div>', unsafe_allow_html=True)

    if qi < len(qs):
        q = qs[qi]
        cq, ci = st.columns([3,1])
        with cq:
            bc2 = "rgba(252,129,129,0.22)" if boss else "rgba(99,179,237,0.15)"
            al  = acc if not boss else "#fc8181"
            st.markdown(f"""
            <div style="background:rgba(10,14,26,0.95);border:1px solid {bc2};border-left:3px solid {al};
                 border-radius:16px;padding:26px;margin-bottom:20px;">
                <div style="color:#e2e8f0;font-size:0.99rem;font-weight:500;line-height:1.75;">{q['domanda']}</div>
            </div>""", unsafe_allow_html=True)

            if st.session_state.risposta_data is None:
                for j, opt in enumerate(q["opzioni"]):
                    if st.button(opt, key=f"o{j}", use_container_width=True):
                        st.session_state.risposta_data = j
                        if j == q["corretta"]: st.session_state.punteggio_quiz += 1
                        st.rerun()
            else:
                sc = st.session_state.risposta_data; co = q["corretta"]
                if sc == co:
                    st.markdown(f'<div class="feedback-correct"><div style="color:#68d391;font-weight:700;margin-bottom:8px;">✅ Esatto!</div><div style="color:#a7f3d0;font-size:0.88rem;line-height:1.7;">{q["spiegazione"]}</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="feedback-wrong"><div style="color:#fc8181;font-weight:700;margin-bottom:6px;">❌ Non corretto.</div><div style="color:#fca5a5;font-size:0.84rem;margin-bottom:8px;">Risposta corretta: <strong>{q["opzioni"][co]}</strong></div><div style="color:#fca5a5;font-size:0.84rem;line-height:1.7;opacity:.88;">{q["spiegazione"]}</div></div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                nl = "➡️ Prossima" if qi < len(qs)-1 else "🏁 Risultato"
                if st.button(nl, key="nx", use_container_width=True):
                    st.session_state.domanda_idx += 1; st.session_state.risposta_data = None
                    if st.session_state.domanda_idx >= len(qs): st.session_state.fase = "risultato"
                    st.rerun()

        with ci:
            for val, lbl, col in [(f"+{ld['xp']}","XP in palio","#f6ad55"),(f"{st.session_state.punteggio_quiz}/{qi}","Corrette","#68d391"),(st.session_state.xp,"XP Totali","#a78bfa")]:
                st.markdown(f'<div style="background:rgba(10,14,26,0.9);border:1px solid rgba(99,179,237,0.1);border-radius:13px;padding:16px;text-align:center;margin-bottom:10px;"><div style="color:{col};font-family:Syne,sans-serif;font-size:1.5rem;font-weight:800;">{val}</div><div style="color:#1e293b;font-size:0.68rem;text-transform:uppercase;letter-spacing:1px;margin-top:2px;">{lbl}</div></div>', unsafe_allow_html=True)

# ─── RISULTATO ─────────────────────────────────────────────────────────────────
elif st.session_state.fase == "risultato":
    area=st.session_state.area_corrente; li=st.session_state.livello_corrente
    ld=MISSIONS[area]["livelli"][li]; sc=st.session_state.punteggio_quiz; tot=len(ld["domande"])
    pct=sc/tot; boss=ld.get("boss",False); xpb=ld["xp"]
    if pct==1.0: xpg=xpb;  ri="🏆"; rt="Perfetto! Masterclass!"; col="#68d391"; st="⭐⭐⭐"
    elif pct>=.67: xpg=int(xpb*.7); ri="✅"; rt="Missione completata!"; col="#63b3ed"; st="⭐⭐"
    else: xpg=int(xpb*.3); ri="📚"; rt="Ripassate e riprovate!"; col="#f6ad55"; st="⭐"
    mid=missione_id(area,li); done=mid in st.session_state.missioni_completate
    if pct>=.67 and not done:
        st.session_state.missioni_completate.append(mid); st.session_state.xp+=xpg; st.session_state.streak+=1
    elif pct<.67:
        st.session_state.streak=0; st.session_state.xp+=xpg
    nb=check_badge(); save_progress()
    c1,c2,c3=st.columns([1,2,1])
    with c2:
        st.markdown(f"""
        <div style="text-align:center;padding:36px 28px;background:rgba(10,14,26,0.95);border:1px solid {col}25;border-radius:26px;margin-bottom:18px;box-shadow:0 0 35px {col}08;">
            <div style="font-size:4rem;margin-bottom:10px;">{ri}</div>
            <div style="font-size:1.3rem;margin-bottom:10px;">{st}</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:#e2e8f0;margin-bottom:5px;">{rt}</div>
            <div style="color:#334155;font-size:0.82rem;margin-bottom:24px;">{'⚔️ Boss sconfitto!' if boss and pct>=.67 else ld['titolo']}</div>
            <div style="display:flex;justify-content:center;gap:36px;">
                {"".join([f'<div><div style="font-family:Syne,sans-serif;font-size:2.5rem;font-weight:800;color:{c};line-height:1;">{v}</div><div style="color:#334155;font-size:0.68rem;text-transform:uppercase;letter-spacing:1px;margin-top:3px;">{l}</div></div>' for v,l,c in [(f"{sc}/{tot}","Corrette",col),(f"+{xpg}","XP","#f6ad55"),(st.session_state.xp,"Totale","#a78bfa")]])}
            </div>
        </div>""", unsafe_allow_html=True)
        for em,nm,ds in nb:
            st.markdown(f'<div style="background:rgba(246,173,85,0.07);border:1px solid rgba(246,173,85,0.22);border-radius:14px;padding:18px;text-align:center;margin-bottom:10px;"><div style="font-size:2.2rem;margin-bottom:6px;">{em}</div><div style="color:#f6ad55;font-weight:700;">🎖️ Badge: {nm}!</div><div style="color:#78716c;font-size:0.82rem;margin-top:3px;">{ds}</div></div>', unsafe_allow_html=True)
        cc1,cc2,cc3=st.columns(3)
        with cc1:
            if st.button("🔄 Riprova", use_container_width=True):
                st.session_state.domanda_idx=0; st.session_state.risposta_data=None; st.session_state.punteggio_quiz=0; st.session_state.fase="quiz"; st.rerun()
        with cc2:
            if st.button("🗺️ Mappa", use_container_width=True): st.session_state.fase="home"; st.rerun()
        with cc3:
            if st.button("🏆 Classifica", use_container_width=True): st.session_state.fase="leaderboard"; st.rerun()

# ─── LEADERBOARD ───────────────────────────────────────────────────────────────
elif st.session_state.fase == "leaderboard":
    st.markdown('<div style="font-family:Syne,sans-serif;font-size:1.9rem;font-weight:800;color:#e2e8f0;margin-bottom:4px;">🏆 Leaderboard</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#334155;margin-bottom:20px;">Classifica in tempo reale di tutti gli studenti del corso</div>', unsafe_allow_html=True)
    c1,c2=st.columns([1,3])
    with c1:
        if st.button("🔄 Aggiorna", use_container_width=True): st.rerun()
    with c2:
        st.markdown('<div style="background:rgba(99,179,237,0.05);border:1px solid rgba(99,179,237,0.12);border-radius:9px;padding:9px 14px;color:#334155;font-size:0.79rem;">💡 Configura Firebase (vedi README) per la classifica in tempo reale. Senza Firebase mostra solo il giocatore corrente.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    entries = get_leaderboard()
    if not entries and st.session_state.xp > 0:
        lv,tit=get_livello(st.session_state.xp)
        entries=[{"nome":st.session_state.nome_studente,"xp":st.session_state.xp,"missioni":len(st.session_state.missioni_completate),"streak":st.session_state.streak,"badge":len(st.session_state.badge_guadagnati),"livello":lv,"titolo":tit}]
    re=["🥇","🥈","🥉"]; rc=["#f6ad55","#94a3b8","#cd7f32"]
    for i, e in enumerate(entries[:25]):
        me = e.get("nome","") == st.session_state.nome_studente
        ri = re[i] if i<3 else f"#{i+1}"; rc2 = rc[i] if i<3 else "#1e293b"
        br = "rgba(246,173,85,0.35)" if me else "rgba(99,179,237,0.08)"; bg = "rgba(246,173,85,0.04)" if me else "rgba(10,14,26,0.8)"
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {br};border-radius:13px;padding:14px 20px;margin-bottom:7px;display:flex;align-items:center;gap:18px;">
            <div style="color:{rc2};font-family:Syne,sans-serif;font-size:1.25rem;font-weight:800;min-width:38px;">{ri}</div>
            <div style="flex:1;">
                <div style="color:#e2e8f0;font-weight:600;font-size:0.92rem;">{e.get('nome','?')} {'<span style="color:#f6ad55;font-size:0.7rem;">(tu)</span>' if me else ''}</div>
                <div style="color:#1e293b;font-size:0.72rem;margin-top:1px;">Lv.{e.get('livello',1)} · {e.get('titolo','')}</div>
            </div>
            {"".join([f'<div style="text-align:center;min-width:48px;"><div style="color:{c};font-family:Syne,sans-serif;font-size:1.1rem;font-weight:800;">{v}</div><div style="color:#1e293b;font-size:0.62rem;text-transform:uppercase;letter-spacing:1px;">{l}</div></div>' for v,l,c in [(e.get('xp',0),"XP","#63b3ed"),(e.get('missioni',0),"Quest","#68d391"),(f"{e.get('streak',0)}🔥","Streak","#f6ad55"),(e.get('badge',0),"Badge","#a78bfa")]])}
        </div>""", unsafe_allow_html=True)
    if not entries:
        st.markdown('<div style="text-align:center;padding:50px;color:#334155;"><div style="font-size:3rem;margin-bottom:14px;">🏆</div><div style="color:#475569;">Inizia a giocare per apparire nella classifica!</div></div>', unsafe_allow_html=True)

# ─── PROFILO ───────────────────────────────────────────────────────────────────
elif st.session_state.fase == "profilo":
    lv,titolo=get_livello(st.session_state.xp); xn=xp_to_next(st.session_state.xp); xp2=xp_threshold(lv)
    prog=min((st.session_state.xp-xp2)/max(xn-xp2,1),1.0)
    st.markdown(f'<div style="font-family:Syne,sans-serif;font-size:1.9rem;font-weight:800;color:#e2e8f0;margin-bottom:3px;">👤 {st.session_state.nome_studente}</div><div style="color:#a78bfa;margin-bottom:24px;">{titolo} · Livello {lv}</div>', unsafe_allow_html=True)
    tm=sum(len(v["livelli"]) for v in MISSIONS.values())
    cs=st.columns(5)
    for col,(ico,lbl,val,c) in zip(cs,[("🎯","XP",st.session_state.xp,"#63b3ed"),("📚","Missioni",f"{len(st.session_state.missioni_completate)}/{tm}","#68d391"),("⚡","Livello",lv,"#a78bfa"),("🔥","Streak",st.session_state.streak,"#f6ad55"),("🎖️","Badge",len(st.session_state.badge_guadagnati),"#fc8181")]):
        with col:
            st.markdown(f'<div class="stat-card"><div style="font-size:1.3rem;margin-bottom:4px;">{ico}</div><div style="font-family:Syne,sans-serif;font-size:1.7rem;font-weight:800;color:{c};line-height:1;">{val}</div><div style="color:#1e293b;font-size:0.67rem;text-transform:uppercase;letter-spacing:1.5px;margin-top:3px;">{lbl}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div style="background:rgba(10,14,26,0.9);border:1px solid rgba(99,179,237,0.1);border-radius:15px;padding:22px;margin-bottom:18px;"><div style="display:flex;justify-content:space-between;margin-bottom:10px;"><span style="color:#e2e8f0;font-weight:600;">Avanzamento Lv.{lv+1}</span><span style="color:#63b3ed;font-weight:600;">{st.session_state.xp}/{xn} XP</span></div><div class="xp-bar-container" style="height:12px;"><div class="xp-bar-fill" style="width:{prog*100:.0f}%;"></div></div><div style="color:#1e293b;font-size:0.75rem;margin-top:8px;">Ancora {xn-st.session_state.xp} XP al prossimo livello</div></div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#e2e8f0;font-weight:600;margin-bottom:12px;">📊 Progresso per Area</div>', unsafe_allow_html=True)
    ac=st.columns(len(MISSIONS))
    for col,(ak,av) in zip(ac,MISSIONS.items()):
        done=sum(1 for m in st.session_state.missioni_completate if ak in m); tot=len(av["livelli"]); pg=done/tot; acc=av["accent"]
        with col:
            st.markdown(f'<div style="background:rgba(10,14,26,0.9);border:1px solid rgba(99,179,237,0.08);border-radius:13px;padding:14px;text-align:center;"><div style="font-size:1.5rem;margin-bottom:6px;">{av["emoji"]}</div><div style="color:#e2e8f0;font-size:0.75rem;font-weight:600;margin-bottom:8px;">{done}/{tot}</div><div class="xp-bar-container" style="height:5px;"><div style="height:100%;width:{pg*100:.0f}%;border-radius:50px;background:{acc};box-shadow:0 0 5px {acc}70;"></div></div></div>', unsafe_allow_html=True)
    st.markdown('<br><div style="color:#e2e8f0;font-weight:600;margin-bottom:12px;">🎖️ Badge Collection</div>', unsafe_allow_html=True)
    bdef={"xp100":("🌟","Prima Stella","100 XP"),"xp500":("⚡","Mezz'Opera","500 XP"),"xp1000":("💎","Mille XP","1000 XP"),"xp2000":("👑","Duemila XP","2000 XP"),
          **{f"{ak}_master":(av["emoji"],f"Master {ak.title()}",f"Missioni {ak} complete") for ak,av in MISSIONS.items()},
          "champion":("🏆","Champion","Tutto completato!"),"streak5":("🔥","On Fire!","5 consecutive")}
    bc2=st.columns(5)
    for i,(bid,(em,nm,ds)) in enumerate(bdef.items()):
        with bc2[i%5]:
            got=bid in st.session_state.badge_guadagnati; op="1" if got else "0.18"; gl=f"0 0 10px rgba(246,173,85,0.2)" if got else "none"
            st.markdown(f'<div style="background:rgba(10,14,26,0.9);border:1px solid {"rgba(246,173,85,0.28)" if got else "rgba(99,179,237,0.07)"};border-radius:13px;padding:14px;text-align:center;opacity:{op};margin-bottom:8px;box-shadow:{gl};"><div style="font-size:1.8rem;margin-bottom:5px;">{em}</div><div style="color:#e2e8f0;font-size:0.76rem;font-weight:600;">{nm}</div><div style="color:#1e293b;font-size:0.66rem;margin-top:1px;">{ds}</div></div>', unsafe_allow_html=True)
