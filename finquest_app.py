import streamlit as st
import json
import random
import time
from datetime import datetime

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinQuest 🏦",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

* { font-family: 'Space Grotesk', sans-serif; }

/* Dark theme background */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a0e1a 100%);
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #111827 100%);
    border-right: 1px solid rgba(99, 179, 237, 0.15);
}

/* Title */
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #63b3ed, #f6ad55, #fc8181);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    letter-spacing: -1px;
    margin-bottom: 0;
}

.hero-sub {
    text-align: center;
    color: #94a3b8;
    font-size: 1rem;
    margin-top: 4px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* Mission cards */
.mission-card {
    background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(30,41,59,0.9));
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 16px;
    padding: 24px;
    margin: 12px 0;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.mission-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}

.mission-card.banche::before { background: linear-gradient(90deg, #63b3ed, #4299e1); }
.mission-card.mercati::before { background: linear-gradient(90deg, #68d391, #38a169); }
.mission-card.rischio::before { background: linear-gradient(90deg, #fc8181, #e53e3e); }

.mission-card:hover {
    border-color: rgba(99,179,237,0.5);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(99,179,237,0.15);
}

.mission-locked {
    opacity: 0.45;
    cursor: not-allowed;
}

/* XP bar */
.xp-bar-container {
    background: rgba(15,23,42,0.8);
    border-radius: 50px;
    height: 12px;
    width: 100%;
    overflow: hidden;
    border: 1px solid rgba(99,179,237,0.2);
}

.xp-bar-fill {
    height: 100%;
    border-radius: 50px;
    background: linear-gradient(90deg, #63b3ed, #f6ad55);
    transition: width 0.8s ease;
}

/* Badge */
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.badge-blue { background: rgba(99,179,237,0.15); color: #63b3ed; border: 1px solid rgba(99,179,237,0.3); }
.badge-green { background: rgba(104,211,145,0.15); color: #68d391; border: 1px solid rgba(104,211,145,0.3); }
.badge-red { background: rgba(252,129,129,0.15); color: #fc8181; border: 1px solid rgba(252,129,129,0.3); }
.badge-gold { background: rgba(246,173,85,0.15); color: #f6ad55; border: 1px solid rgba(246,173,85,0.3); }

/* Answer buttons */
.stButton > button {
    background: rgba(15,23,42,0.9) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(99,179,237,0.25) !important;
    border-radius: 12px !important;
    padding: 14px 20px !important;
    font-size: 0.95rem !important;
    font-family: 'Space Grotesk', sans-serif !important;
    width: 100% !important;
    text-align: left !important;
    transition: all 0.2s ease !important;
    font-weight: 400 !important;
}

.stButton > button:hover {
    background: rgba(99,179,237,0.1) !important;
    border-color: rgba(99,179,237,0.6) !important;
    color: #fff !important;
    transform: translateX(4px) !important;
}

/* Stat cards */
.stat-card {
    background: rgba(15,23,42,0.8);
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}

.stat-number {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #63b3ed;
}

.stat-label {
    color: #64748b;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Quiz feedback */
.feedback-correct {
    background: rgba(104,211,145,0.1);
    border: 1px solid rgba(104,211,145,0.4);
    border-radius: 12px;
    padding: 16px;
    color: #68d391;
}

.feedback-wrong {
    background: rgba(252,129,129,0.1);
    border: 1px solid rgba(252,129,129,0.4);
    border-radius: 12px;
    padding: 16px;
    color: #fc8181;
}

/* Progress section */
h1, h2, h3 { color: #e2e8f0 !important; }
p, li { color: #94a3b8; }
label { color: #94a3b8 !important; }

.stMarkdown { color: #94a3b8; }

/* Sidebar text */
.css-1d391kg p { color: #94a3b8; }

/* Divider */
hr { border-color: rgba(99,179,237,0.1) !important; }
</style>
""", unsafe_allow_html=True)

# ─── MISSION DATA ───────────────────────────────────────────────────────────────
MISSIONS = {
    "banche": {
        "nome": "🏦 Banche & Intermediazione",
        "colore": "banche",
        "badge": "badge-blue",
        "emoji": "🏦",
        "xp_totale": 300,
        "descrizione": "Comprendi il ruolo delle banche nel sistema economico",
        "livelli": [
            {
                "titolo": "Missione 1 — Le Basi",
                "descrizione": "Cos'è una banca? Quale funzione svolge?",
                "xp": 50,
                "domande": [
                    {
                        "domanda": "Qual è la funzione principale di trasformazione svolta dalle banche?",
                        "opzioni": [
                            "A) Trasformazione delle valute estere",
                            "B) Trasformazione delle scadenze: raccolgono depositi a breve e concedono crediti a lungo termine",
                            "C) Trasformazione dei titoli azionari in obbligazioni",
                            "D) Trasformazione dei rischi in profitti"
                        ],
                        "corretta": 1,
                        "spiegazione": "Le banche svolgono la fondamentale funzione di trasformazione delle scadenze (maturity transformation): raccolgono fondi a breve termine (depositi) e li reimpiegano in prestiti e investimenti a lungo termine, guadagnando sullo spread tra tassi attivi e passivi."
                    },
                    {
                        "domanda": "Cosa si intende per 'riserva frazionaria' nel sistema bancario?",
                        "opzioni": [
                            "A) La quota di utili che le banche devono riservarsi",
                            "B) Le banche tengono solo una frazione dei depositi in riserva liquida e prestano il resto",
                            "C) La riserva aurea obbligatoria in Banca d'Italia",
                            "D) Il fondo per le frazioni di centesimo nei conti correnti"
                        ],
                        "corretta": 1,
                        "spiegazione": "Il sistema a riserva frazionaria è il meccanismo per cui le banche tengono liquida solo una frazione (la riserva obbligatoria + volontaria) dei depositi raccolti, prestando il restante. Questo crea moneta bancaria e dà origine al moltiplicatore dei depositi."
                    },
                    {
                        "domanda": "Il ROE bancario si calcola come:",
                        "opzioni": [
                            "A) Ricavi totali / Totale attivo",
                            "B) Utile netto / Patrimonio netto",
                            "C) Margine di interesse / Impieghi",
                            "D) Depositi / Prestiti"
                        ],
                        "corretta": 1,
                        "spiegazione": "Il ROE (Return On Equity) = Utile netto / Patrimonio netto. Misura la redditività per gli azionisti. Per le banche è un KPI cruciale; un ROE del 10-15% è considerato soddisfacente nel settore bancario europeo."
                    }
                ]
            },
            {
                "titolo": "Missione 2 — Il Bilancio Bancario",
                "descrizione": "Attivo, Passivo e le voci principali del bilancio di una banca",
                "xp": 100,
                "domande": [
                    {
                        "domanda": "Nel bilancio di una banca, dove troviamo i 'crediti verso clientela'?",
                        "opzioni": [
                            "A) Nel passivo, come debiti verso i clienti",
                            "B) Nell'attivo, perché rappresentano prestiti concessi dalla banca",
                            "C) Nel conto economico, come ricavi da interessi",
                            "D) Fuori bilancio, nelle note integrative"
                        ],
                        "corretta": 1,
                        "spiegazione": "I crediti verso clientela stanno nell'ATTIVO del bilancio bancario: sono risorse che la banca vanta (ha prestato denaro, quindi 'ha diritto a riceverlo indietro'). I depositi dei clienti invece sono nel PASSIVO (la banca deve restituirli)."
                    },
                    {
                        "domanda": "Cosa sono gli NPL (Non-Performing Loans)?",
                        "opzioni": [
                            "A) Prestiti ad alto rendimento concessi alle imprese",
                            "B) Prestiti in sofferenza: il debitore non riesce a rimborsare regolarmente",
                            "C) Nuovi prodotti di lending digitale",
                            "D) Prestiti interbancari overnight"
                        ],
                        "corretta": 1,
                        "spiegazione": "Gli NPL (crediti deteriorati) sono prestiti in cui il debitore è in difficoltà nel rimborso. In Italia post-crisi 2008 erano un problema enorme (~360 mld). Le banche devono effettuare rettifiche di valore (accantonamenti) che erodono il patrimonio."
                    },
                    {
                        "domanda": "Il Net Interest Margin (NIM) di una banca è:",
                        "opzioni": [
                            "A) La differenza tra prestiti concessi e depositi raccolti",
                            "B) Il differenziale tra tasso medio attivo (su impieghi) e tasso medio passivo (su raccolta)",
                            "C) Il margine netto dopo le imposte",
                            "D) Il rapporto tra patrimonio e totale attivo"
                        ],
                        "corretta": 1,
                        "spiegazione": "Il NIM è lo spread tra il rendimento medio degli impieghi e il costo medio della raccolta. Es: tasso medio prestiti 4%, tasso medio depositi 1% → NIM = 3%. È la principale fonte di reddito delle banche tradizionali."
                    }
                ]
            },
            {
                "titolo": "Missione 3 — BOSS: Regolamentazione Prudenziale",
                "descrizione": "⚔️ Affronta il boss: Basilea III e i requisiti patrimoniali",
                "xp": 150,
                "boss": True,
                "domande": [
                    {
                        "domanda": "Secondo Basilea III, qual è il requisito minimo di CET1 Ratio?",
                        "opzioni": [
                            "A) 2%",
                            "B) 4.5%",
                            "C) 8%",
                            "D) 12%"
                        ],
                        "corretta": 1,
                        "spiegazione": "Il CET1 (Common Equity Tier 1) deve essere almeno il 4.5% delle attività ponderate per il rischio (RWA). Con il capital conservation buffer si sale al 7%. Il CET1 è la forma più 'pura' di capitale: azioni ordinarie + utili non distribuiti."
                    },
                    {
                        "domanda": "Il Liquidity Coverage Ratio (LCR) serve a garantire che la banca:",
                        "opzioni": [
                            "A) Abbia profitti sufficienti per 30 anni",
                            "B) Possa sopravvivere a uno stress di liquidità di 30 giorni",
                            "C) Mantenga un portafoglio diversificato per 30 settori",
                            "D) Limiti i prestiti a 30 anni di durata"
                        ],
                        "corretta": 1,
                        "spiegazione": "L'LCR richiede che le attività liquide di alta qualità (HQLA) coprano i deflussi netti di cassa in uno scenario di stress acuto di 30 giorni. LCR ≥ 100%. Risponde alla domanda: 'se domani ci fosse una corsa agli sportelli, reggiamo un mese?'"
                    },
                    {
                        "domanda": "Cosa misura il Leverage Ratio di Basilea III?",
                        "opzioni": [
                            "A) Il rapporto tra debiti e ricavi",
                            "B) Il rapporto tra Tier 1 capital e esposizione totale non ponderata per il rischio",
                            "C) Il numero di filiali rispetto ai dipendenti",
                            "D) Il rapporto tra depositi e prestiti"
                        ],
                        "corretta": 1,
                        "spiegazione": "Il Leverage Ratio = Tier 1 / Esposizione totale (non ponderata per il rischio). Minimo 3%. A differenza del Capital Ratio, non dipende dai modelli interni di ponderazione del rischio, evitando il problema del 'risk weighting gaming'."
                    }
                ]
            }
        ]
    },
    "mercati": {
        "nome": "📈 Mercati Finanziari",
        "colore": "mercati",
        "badge": "badge-green",
        "emoji": "📈",
        "xp_totale": 300,
        "descrizione": "Esplora struttura e funzionamento dei mercati",
        "livelli": [
            {
                "titolo": "Missione 1 — Struttura dei Mercati",
                "descrizione": "Mercati primari, secondari, e tipologie di strumenti",
                "xp": 50,
                "domande": [
                    {
                        "domanda": "Qual è la differenza tra mercato primario e mercato secondario?",
                        "opzioni": [
                            "A) Il primario è per le grandi aziende, il secondario per le PMI",
                            "B) Nel primario si emettono nuovi titoli; nel secondario si scambiano titoli già esistenti tra investitori",
                            "C) Il primario è regolamentato, il secondario è OTC",
                            "D) Il primario è per le azioni, il secondario per le obbligazioni"
                        ],
                        "corretta": 1,
                        "spiegazione": "Il mercato primario è dove i titoli vengono emessi per la prima volta (es. IPO, emissione di BOT). Il mercato secondario è dove gli investitori si scambiano titoli già esistenti (es. Borsa di Milano, NYSE). Il secondario garantisce la liquidità degli strumenti."
                    },
                    {
                        "domanda": "Un'obbligazione con cedola del 5% e valore nominale 1.000€ paga ogni anno:",
                        "opzioni": [
                            "A) 5€",
                            "B) 50€",
                            "C) 500€",
                            "D) Dipende dall'inflazione"
                        ],
                        "corretta": 1,
                        "spiegazione": "Cedola annua = Tasso cedola × Valore nominale = 5% × 1.000€ = 50€. Questo importo è fisso (per un'obbligazione a tasso fisso) e viene pagato indipendentemente dal prezzo di mercato del titolo, che può variare nel tempo."
                    },
                    {
                        "domanda": "Cosa si intende per 'duration' di un'obbligazione?",
                        "opzioni": [
                            "A) La data di scadenza del titolo",
                            "B) La vita media finanziaria, che misura la sensibilità del prezzo alle variazioni dei tassi",
                            "C) La durata media dei contratti repo",
                            "D) Il tempo necessario per la liquidazione"
                        ],
                        "corretta": 1,
                        "spiegazione": "La Duration (Macaulay) è la media ponderata delle scadenze dei flussi di cassa. La Modified Duration misura la sensibilità del prezzo al tasso: se MD = 5, un aumento dei tassi dell'1% → prezzo scende del ~5%. Strumento chiave per la gestione del rischio di tasso."
                    }
                ]
            },
            {
                "titolo": "Missione 2 — Efficienza e Valutazione",
                "descrizione": "Ipotesi di efficienza, modelli di pricing e anomalie",
                "xp": 100,
                "domande": [
                    {
                        "domanda": "L'Ipotesi di Efficienza dei Mercati (EMH) nella forma 'forte' afferma che:",
                        "opzioni": [
                            "A) I prezzi riflettono solo le informazioni pubbliche passate",
                            "B) I prezzi riflettono TUTTE le informazioni, incluse quelle private/insider",
                            "C) I mercati sono sempre in equilibrio",
                            "D) Nessun investitore può battere il mercato usando l'analisi tecnica"
                        ],
                        "corretta": 1,
                        "spiegazione": "Le tre forme EMH: Debole (prezzi riflettono dati storici), Semi-forte (riflettono tutte le info pubbliche), Forte (riflettono TUTTO, incluse info private). La forma forte implica che anche gli insider non possono guadagnare in modo sistematico — empiricamente questa forma è rifiutata."
                    },
                    {
                        "domanda": "Nel modello CAPM, il Beta (β) di un titolo misura:",
                        "opzioni": [
                            "A) Il rendimento atteso del titolo",
                            "B) La sensibilità del rendimento del titolo rispetto al mercato (rischio sistematico)",
                            "C) Il rischio specifico dell'impresa diversificabile",
                            "D) Il rapporto price/earnings"
                        ],
                        "corretta": 1,
                        "spiegazione": "β = Cov(Ri, Rm) / Var(Rm). Se β=1 il titolo si muove come il mercato; β>1 è più volatile (es. titoli tech); β<1 è difensivo (es. utilities). Il CAPM dice: E(Ri) = Rf + β × (Rm - Rf). Solo il rischio sistematico (non diversificabile) viene remunerato."
                    },
                    {
                        "domanda": "Cosa sono i fondi ETF (Exchange Traded Fund)?",
                        "opzioni": [
                            "A) Fondi attivi gestiti da star manager che battono l'indice",
                            "B) Fondi quotati in borsa che replicano passivamente un indice a costi molto bassi",
                            "C) Fondi di private equity non quotati",
                            "D) Strumenti derivati su indici azionari"
                        ],
                        "corretta": 1,
                        "spiegazione": "Gli ETF sono fondi a gestione passiva che replicano un indice (es. S&P500, MSCI World) e si scambiano in borsa come azioni. Hanno TER molto bassi (0.05%-0.5%) vs fondi attivi (1-2%). La ricerca empirica mostra che la maggior parte dei fondi attivi non batte l'indice nel lungo periodo."
                    }
                ]
            },
            {
                "titolo": "Missione 3 — BOSS: Il Crash del 2008",
                "descrizione": "⚔️ Affronta il boss: capire la crisi finanziaria globale",
                "xp": 150,
                "boss": True,
                "domande": [
                    {
                        "domanda": "Cosa sono i CDO (Collateralized Debt Obligations) al centro della crisi 2008?",
                        "opzioni": [
                            "A) Certificati di deposito ordinari emessi dalle banche centrali",
                            "B) Strumenti strutturati che 'impacchettavano' mutui subprime in tranche con rating diversi",
                            "C) Contratti futures su obbligazioni governative",
                            "D) Fondi comuni obbligazionari diversificati"
                        ],
                        "corretta": 1,
                        "spiegazione": "I CDO raggruppavano migliaia di mutui (anche subprime) e li suddividevano in tranche con profili rischio/rendimento diversi. Le agenzie di rating assegnavano AAA alle tranche senior. Quando i mutui iniziarono a deteriorarsi in massa, il meccanismo collassò, diffondendo la crisi globalmente."
                    },
                    {
                        "domanda": "Il 'moral hazard' nel sistema bancario si riferisce a:",
                        "opzioni": [
                            "A) L'obbligo morale delle banche di finanziare progetti sociali",
                            "B) Il rischio che la garanzia pubblica (bail-out) incentivi le banche a prendere rischi eccessivi",
                            "C) I rischi reputazionali legati agli scandali bancari",
                            "D) Il pericolo di truffe informatiche nel banking digitale"
                        ],
                        "corretta": 1,
                        "spiegazione": "Il moral hazard ('azzardo morale') nasce dalla garanzia implicita del salvataggio pubblico (too-big-to-fail): se una banca sa che verrà salvata, ha incentivo a prendere rischi eccessivi, privatizzando i guadagni e socializzando le perdite. Questo è uno dei fallimenti del mercato finanziario."
                    },
                    {
                        "domanda": "Cosa si intende per 'contagio finanziario' (financial contagion)?",
                        "opzioni": [
                            "A) La diffusione di virus informatici tra le banche",
                            "B) La propagazione di crisi tra mercati o istituzioni attraverso interconnessioni finanziarie",
                            "C) Il contagio da scandali di insider trading",
                            "D) La diffusione di prodotti finanziari tossici via email"
                        ],
                        "corretta": 1,
                        "spiegazione": "Il contagio finanziario è il meccanismo per cui una crisi in un'istituzione o mercato si propaga ad altri attraverso le interconnessioni: esposizioni interbancarie, vendite forzate di asset, crisi di fiducia. Nel 2008 il fallimento di Lehman Brothers innescò un contagio globale immediato."
                    }
                ]
            }
        ]
    },
    "rischio": {
        "nome": "⚠️ Rischio & Regolamentazione",
        "colore": "rischio",
        "badge": "badge-red",
        "emoji": "⚠️",
        "xp_totale": 300,
        "descrizione": "Misura, gestisci e regola il rischio finanziario",
        "livelli": [
            {
                "titolo": "Missione 1 — Tipologie di Rischio",
                "descrizione": "Rischio di credito, mercato, liquidità e operativo",
                "xp": 50,
                "domande": [
                    {
                        "domanda": "Qual è la differenza tra rischio sistematico e rischio specifico?",
                        "opzioni": [
                            "A) Il sistematico è il rischio di sistema informatico; il specifico è del singolo prodotto",
                            "B) Il sistematico non è diversificabile (colpisce tutto il mercato); il specifico si elimina con la diversificazione",
                            "C) Il sistematico riguarda le banche sistemiche; il specifico le PMI",
                            "D) Non c'è differenza: sono due nomi per lo stesso concetto"
                        ],
                        "corretta": 1,
                        "spiegazione": "Il rischio sistematico (o di mercato) è legato a fattori macroeconomici che colpiscono tutti gli asset (recessioni, pandemie). Non si può eliminare con la diversificazione. Il rischio specifico (idiosincratico) riguarda la singola impresa e si diversifica via combinando molti titoli in portafoglio."
                    },
                    {
                        "domanda": "Il VaR (Value at Risk) al 99% su 1 giorno di 1 milione di euro significa:",
                        "opzioni": [
                            "A) La banca perderà certamente 1 milione domani",
                            "B) Con probabilità 99%, la perdita massima domani non supererà 1 milione di euro",
                            "C) Il valore del portafoglio scenderà dell'1% al giorno",
                            "D) Il rischio massimo assoluto è 1 milione in qualsiasi scenario"
                        ],
                        "corretta": 1,
                        "spiegazione": "Il VaR(99%, 1d) = 1M€ significa: nel 99% dei giorni la perdita sarà ≤ 1M€, ovvero solo l'1% dei giorni (circa 2-3 giorni lavorativi l'anno) ci aspettiamo una perdita maggiore. Il VaR non dice nulla sulla magnitudo delle perdite nell'1% peggiore (tail risk)."
                    },
                    {
                        "domanda": "Il rischio di liquidità bancaria si manifesta quando:",
                        "opzioni": [
                            "A) Il mercato azionario crolla improvvisamente",
                            "B) La banca non riesce a fare fronte ai propri impegni di pagamento senza perdite eccessive",
                            "C) Il tasso di inflazione supera il tasso cedola",
                            "D) I clienti aprono troppi conti correnti contemporaneamente"
                        ],
                        "corretta": 1,
                        "spiegazione": "Il rischio di liquidità ha due dimensioni: (1) Funding liquidity risk — non riuscire a raccogliere fondi necessari; (2) Market liquidity risk — non riuscire a liquidare posizioni senza impattare i prezzi. Le bank run (corsa agli sportelli) sono l'esempio estremo di rischio di liquidità."
                    }
                ]
            },
            {
                "titolo": "Missione 2 — Gestione del Rischio",
                "descrizione": "Strumenti di hedging, derivati e gestione ALM",
                "xp": 100,
                "domande": [
                    {
                        "domanda": "Un interest rate swap (IRS) permette a due parti di:",
                        "opzioni": [
                            "A) Scambiare azioni con obbligazioni a tasso fisso",
                            "B) Scambiare flussi di interesse: uno paga tasso fisso, l'altro paga tasso variabile",
                            "C) Fissare il tasso di cambio per transazioni future",
                            "D) Coprire il rischio azionario con opzioni"
                        ],
                        "corretta": 1,
                        "spiegazione": "In un IRS standard (plain vanilla): la parte A paga interessi a tasso fisso, la parte B paga interessi a tasso variabile (es. Euribor) sullo stesso nozionale. Non c'è scambio del principale. Utilizzato per trasformare il profilo di rischio tasso: una banca con mutui a tasso fisso può swappare in variabile per coprire il mismatch con i depositi."
                    },
                    {
                        "domanda": "L'Asset Liability Management (ALM) bancario ha l'obiettivo di:",
                        "opzioni": [
                            "A) Massimizzare i profitti a breve termine sui trading book",
                            "B) Gestire il mismatch tra le scadenze/rischi di attivo e passivo per stabilizzare il margine d'interesse",
                            "C) Selezionare i migliori asset da inserire in bilancio",
                            "D) Gestire il portafoglio di partecipazioni azionarie"
                        ],
                        "corretta": 1,
                        "spiegazione": "L'ALM coordina la gestione dell'attivo e del passivo per controllare il rischio di tasso (gap tra durata degli impieghi e raccolta), rischio di liquidità (maturity mismatch) e rischio di cambio. Il COMITATO ALCO (Asset Liability Committee) è l'organo preposto nelle banche."
                    },
                    {
                        "domanda": "Il Credit Default Swap (CDS) funziona come:",
                        "opzioni": [
                            "A) Un prestito interbancario garantito da collaterale",
                            "B) Un'assicurazione contro il default di un emittente: il compratore paga un premio periodico e riceve protezione",
                            "C) Uno swap di valute tra due banche centrali",
                            "D) Un contratto futures sul merito creditizio"
                        ],
                        "corretta": 1,
                        "spiegazione": "Nel CDS: il protection buyer paga un premio (spread) periodico al protection seller. Se l'entità di riferimento va in default, il seller paga la perdita al buyer. Il CDS spread riflette la probabilità di default implicita del mercato. Nel 2008, la massiccia vendita di CDS da AIG senza copertura fu un fattore chiave della crisi."
                    }
                ]
            },
            {
                "titolo": "Missione 3 — BOSS: Stress Test & Vigilanza",
                "descrizione": "⚔️ Affronta il boss: BCE, EBA e supervisione bancaria",
                "xp": 150,
                "boss": True,
                "domande": [
                    {
                        "domanda": "Gli stress test bancari condotti dall'EBA servono a:",
                        "opzioni": [
                            "A) Valutare le competenze del management bancario",
                            "B) Verificare la resilienza delle banche in scenari macroeconomici avversi simulati",
                            "C) Testare i sistemi informatici bancari sotto carico",
                            "D) Controllare la conformità ai requisiti antiriciclaggio"
                        ],
                        "corretta": 1,
                        "spiegazione": "Gli stress test EBA/BCE simulano scenari avversi (recessione severa, crollo immobiliare, shock tassi) e calcolano come il CET1 delle banche si deteriorerebbe. Se scende sotto soglie critiche, la banca deve rafforzare il capitale. Dopo il 2011 sono diventati strumento chiave della supervisione prudenziale europea."
                    },
                    {
                        "domanda": "Il Single Supervisory Mechanism (SSM) è:",
                        "opzioni": [
                            "A) Il sistema di pagamenti interbancari europeo TARGET2",
                            "B) Il sistema di vigilanza bancaria unica europea, con la BCE che supervisiona le banche significative dell'Eurozona",
                            "C) Il meccanismo di risoluzione per le banche in fallimento",
                            "D) Il sistema di reporting standardizzato FINREP/COREP"
                        ],
                        "corretta": 1,
                        "spiegazione": "L'SSM (2014) è il pilastro della Banking Union: la BCE supervisiona direttamente le ~120 banche 'significative' dell'Eurozona (attivi > 30 mld o > 20% del PIL nazionale). Le banche meno significative restano sotto le autorità nazionali (Banca d'Italia) in coordinamento con la BCE."
                    },
                    {
                        "domanda": "Il principio di 'ring-fencing' bancario introdotto dopo la crisi prevede:",
                        "opzioni": [
                            "A) La costruzione di barriere fisiche nelle filiali per la sicurezza",
                            "B) La separazione legale/operativa delle attività retail da quelle di investment banking",
                            "C) L'obbligo di mantenere riserve di liquidità in conti separati",
                            "D) La limitazione geografica delle attività bancarie al paese d'origine"
                        ],
                        "corretta": 1,
                        "spiegazione": "Il ring-fencing mira a proteggere i depositi retail dall'esposizione alle attività speculative di trading/investment banking. Nel UK il Banking Reform Act 2013 ha imposto la separazione strutturale per le grandi banche. L'obiettivo è evitare che i contribuenti paghino per le perdite del trading proprietario."
                    }
                ]
            }
        ]
    }
}

LIVELLO_MINIMO_PER_AREA = {"mercati": 1, "rischio": 1}

# ─── SESSION STATE INIT ─────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "nome_studente": "",
        "registrato": False,
        "xp": 0,
        "missioni_completate": [],
        "livello_corrente": None,
        "area_corrente": None,
        "domanda_idx": 0,
        "risposta_data": None,
        "punteggio_quiz": 0,
        "fase": "home",  # home | quiz | risultato | profilo
        "streak": 0,
        "missioni_sbloccate": {"banche": [0], "mercati": [0], "rischio": [0]},
        "badge_guadagnati": []
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def get_livello(xp):
    if xp < 100: return 1, "Studente Curioso 📚"
    elif xp < 300: return 2, "Analista Junior 📊"
    elif xp < 600: return 3, "Gestore di Portafoglio 💼"
    elif xp < 900: return 4, "Direttore Finanziario 🎩"
    else: return 5, "Guru della Finanza 🏆"

def xp_to_next(xp):
    soglie = [100, 300, 600, 900, 9999]
    lv, _ = get_livello(xp)
    return soglie[lv - 1]

def missione_id(area, idx):
    return f"{area}_{idx}"

def is_completata(area, idx):
    return missione_id(area, idx) in st.session_state.missioni_completate

def check_badge():
    xp = st.session_state.xp
    mc = st.session_state.missioni_completate
    badges = st.session_state.badge_guadagnati
    nuovi = []
    if xp >= 100 and "primo_xp" not in badges:
        nuovi.append(("🌟", "Prima Stella", "Hai guadagnato 100 XP!"))
        badges.append("primo_xp")
    if sum(1 for m in mc if "banche" in m) >= 3 and "banche_master" not in badges:
        nuovi.append(("🏦", "Banchiere", "Completate tutte le missioni banche!"))
        badges.append("banche_master")
    if sum(1 for m in mc if "mercati" in m) >= 3 and "mercati_master" not in badges:
        nuovi.append(("📈", "Trader", "Completate tutte le missioni mercati!"))
        badges.append("mercati_master")
    if sum(1 for m in mc if "rischio" in m) >= 3 and "rischio_master" not in badges:
        nuovi.append(("🛡️", "Risk Manager", "Completate tutte le missioni rischio!"))
        badges.append("rischio_master")
    if len(mc) >= 9 and "finquest_champion" not in badges:
        nuovi.append(("🏆", "FinQuest Champion", "Hai completato TUTTE le missioni!"))
        badges.append("finquest_champion")
    return nuovi

# ─── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 16px 0 8px;">
        <div style="font-family:'Syne',sans-serif; font-size:1.6rem; font-weight:800; 
             background:linear-gradient(135deg,#63b3ed,#f6ad55); 
             -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            FinQuest
        </div>
        <div style="color:#475569; font-size:0.7rem; letter-spacing:2px; text-transform:uppercase;">
            Economia Intermediari
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    if st.session_state.registrato:
        lv, titolo = get_livello(st.session_state.xp)
        xp_next = xp_to_next(st.session_state.xp)
        xp_prev = [0, 100, 300, 600, 900][lv - 1]
        progress = min((st.session_state.xp - xp_prev) / max(xp_next - xp_prev, 1), 1.0)

        st.markdown(f"""
        <div style="padding:12px;">
            <div style="color:#94a3b8; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px;">Studente</div>
            <div style="color:#e2e8f0; font-weight:600; font-size:1.1rem; margin:4px 0;">{st.session_state.nome_studente}</div>
            <div style="color:#f6ad55; font-size:0.85rem; margin-bottom:12px;">{titolo}</div>
            
            <div style="color:#94a3b8; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">
                XP: {st.session_state.xp} / {xp_next}
            </div>
            <div class="xp-bar-container">
                <div class="xp-bar-fill" style="width:{progress*100:.0f}%;"></div>
            </div>
            
            <div style="display:flex; gap:8px; margin-top:16px;">
                <div style="flex:1; background:rgba(15,23,42,0.8); border:1px solid rgba(99,179,237,0.15); 
                     border-radius:8px; padding:8px; text-align:center;">
                    <div style="color:#63b3ed; font-weight:700; font-size:1.1rem;">Lv.{lv}</div>
                    <div style="color:#475569; font-size:0.65rem;">Livello</div>
                </div>
                <div style="flex:1; background:rgba(15,23,42,0.8); border:1px solid rgba(99,179,237,0.15); 
                     border-radius:8px; padding:8px; text-align:center;">
                    <div style="color:#68d391; font-weight:700; font-size:1.1rem;">{len(st.session_state.missioni_completate)}</div>
                    <div style="color:#475569; font-size:0.65rem;">Missioni</div>
                </div>
                <div style="flex:1; background:rgba(15,23,42,0.8); border:1px solid rgba(99,179,237,0.15); 
                     border-radius:8px; padding:8px; text-align:center;">
                    <div style="color:#f6ad55; font-weight:700; font-size:1.1rem;">{st.session_state.streak}🔥</div>
                    <div style="color:#475569; font-size:0.65rem;">Streak</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        if st.button("🗺️  Mappa Missioni", use_container_width=True):
            st.session_state.fase = "home"
            st.rerun()
        if st.button("👤  Il Mio Profilo", use_container_width=True):
            st.session_state.fase = "profilo"
            st.rerun()

        # Badge display
        if st.session_state.badge_guadagnati:
            st.markdown("<div style='color:#64748b; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px; margin-top:16px; padding:0 12px;'>Badge Ottenuti</div>", unsafe_allow_html=True)
            badge_map = {
                "primo_xp": "🌟", "banche_master": "🏦",
                "mercati_master": "📈", "rischio_master": "🛡️", "finquest_champion": "🏆"
            }
            badges_html = " ".join([f"<span style='font-size:1.4rem;'>{badge_map.get(b, '🎖️')}</span>" for b in st.session_state.badge_guadagnati])
            st.markdown(f"<div style='padding:8px 12px;'>{badges_html}</div>", unsafe_allow_html=True)

# ─── MAIN CONTENT ───────────────────────────────────────────────────────────────

# ── REGISTRAZIONE ──────────────────────────────────────────────────────────────
if not st.session_state.registrato:
    st.markdown('<div class="hero-title">FinQuest 🏦</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Economia degli Intermediari Finanziari</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background:rgba(15,23,42,0.9); border:1px solid rgba(99,179,237,0.2); 
             border-radius:20px; padding:40px; text-align:center;">
            <div style="font-size:3rem; margin-bottom:16px;">🎓</div>
            <div style="color:#e2e8f0; font-size:1.3rem; font-weight:600; margin-bottom:8px;">
                Benvenuto nell'Accademia
            </div>
            <div style="color:#64748b; font-size:0.9rem; margin-bottom:28px;">
                Completa missioni, guadagna XP e diventa un maestro della finanza
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        nome = st.text_input("✏️ Come ti chiami?", placeholder="Inserisci il tuo nome...")
        if st.button("🚀 Inizia l'Avventura!", use_container_width=True):
            if nome.strip():
                st.session_state.nome_studente = nome.strip()
                st.session_state.registrato = True
                st.rerun()
            else:
                st.warning("Inserisci il tuo nome per continuare!")

# ── HOME: MAPPA MISSIONI ───────────────────────────────────────────────────────
elif st.session_state.fase == "home":
    lv, titolo = get_livello(st.session_state.xp)

    st.markdown(f"""
    <div style="margin-bottom: 8px;">
        <span style="font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:800; color:#e2e8f0;">
            Ciao, {st.session_state.nome_studente}! 👋
        </span>
    </div>
    <div style="color:#64748b; font-size:0.9rem; margin-bottom:32px;">
        Scegli una missione e metti alla prova le tue conoscenze finanziarie
    </div>
    """, unsafe_allow_html=True)

    # Mostra aree
    for area_key, area_data in MISSIONS.items():
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px; margin: 28px 0 12px;">
            <span style="font-size:1.5rem;">{area_data['emoji']}</span>
            <div>
                <div style="color:#e2e8f0; font-weight:600; font-size:1.1rem;">{area_data['nome']}</div>
                <div style="color:#475569; font-size:0.8rem;">{area_data['descrizione']}</div>
            </div>
            <div style="margin-left:auto;">
                <span class="badge {area_data['badge']}">{sum(1 for m in st.session_state.missioni_completate if area_key in m)}/{len(area_data['livelli'])} completate</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(len(area_data["livelli"]))
        for i, livello in enumerate(area_data["livelli"]):
            with cols[i]:
                completata = is_completata(area_key, i)
                is_boss = livello.get("boss", False)
                bloccata = i > 0 and not is_completata(area_key, i - 1)

                bg_color = "rgba(104,211,145,0.08)" if completata else ("rgba(252,129,129,0.06)" if is_boss else "rgba(15,23,42,0.9)")
                border_color = "rgba(104,211,145,0.4)" if completata else ("rgba(252,129,129,0.3)" if is_boss else "rgba(99,179,237,0.2)")
                opacity = "0.4" if bloccata else "1"

                status_icon = "✅" if completata else ("⚔️" if is_boss else ("🔒" if bloccata else "▶️"))

                st.markdown(f"""
                <div style="background:{bg_color}; border:1px solid {border_color}; border-radius:14px; 
                     padding:18px; opacity:{opacity}; min-height:160px;">
                    <div style="font-size:1.6rem; margin-bottom:8px;">{status_icon}</div>
                    <div style="color:#e2e8f0; font-weight:600; font-size:0.85rem; margin-bottom:6px;">
                        {livello['titolo']}
                    </div>
                    <div style="color:#64748b; font-size:0.75rem; margin-bottom:12px;">
                        {livello['descrizione']}
                    </div>
                    <div style="color:#f6ad55; font-size:0.8rem; font-weight:600;">
                        +{livello['xp']} XP
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if not bloccata and not completata:
                    if st.button(f"{'⚔️ Combatti' if is_boss else '▶️ Gioca'}", key=f"btn_{area_key}_{i}", use_container_width=True):
                        st.session_state.area_corrente = area_key
                        st.session_state.livello_corrente = i
                        st.session_state.domanda_idx = 0
                        st.session_state.risposta_data = None
                        st.session_state.punteggio_quiz = 0
                        st.session_state.fase = "quiz"
                        st.rerun()
                elif completata:
                    st.button("✅ Rigioca", key=f"retry_{area_key}_{i}", use_container_width=True, disabled=False)
                    if st.session_state.get(f"retry_clicked_{area_key}_{i}"):
                        st.session_state.area_corrente = area_key
                        st.session_state.livello_corrente = i
                        st.session_state.domanda_idx = 0
                        st.session_state.risposta_data = None
                        st.session_state.punteggio_quiz = 0
                        st.session_state.fase = "quiz"
                        st.rerun()

# ── QUIZ ───────────────────────────────────────────────────────────────────────
elif st.session_state.fase == "quiz":
    area = st.session_state.area_corrente
    lv_idx = st.session_state.livello_corrente
    area_data = MISSIONS[area]
    livello = area_data["livelli"][lv_idx]
    domande = livello["domande"]
    q_idx = st.session_state.domanda_idx

    is_boss = livello.get("boss", False)

    # Header
    st.markdown(f"""
    <div style="margin-bottom:24px;">
        <div style="color:#475569; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">
            {area_data['nome']} › {livello['titolo']}
        </div>
        <div style="font-family:'Syne',sans-serif; font-size:1.6rem; font-weight:800; color:#e2e8f0;">
            {"⚔️ BOSS FIGHT" if is_boss else f"Domanda {q_idx + 1} di {len(domande)}"}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Progress bar domande
    prog = (q_idx) / len(domande)
    st.markdown(f"""
    <div class="xp-bar-container" style="margin-bottom:32px;">
        <div class="xp-bar-fill" style="width:{prog*100:.0f}%; background:{'linear-gradient(90deg,#fc8181,#f6ad55)' if is_boss else 'linear-gradient(90deg,#63b3ed,#68d391)'};"></div>
    </div>
    """, unsafe_allow_html=True)

    if q_idx < len(domande):
        domanda = domande[q_idx]

        col_q, col_info = st.columns([3, 1])
        with col_q:
            st.markdown(f"""
            <div style="background:rgba(15,23,42,0.9); border:1px solid rgba(99,179,237,0.2); 
                 border-radius:16px; padding:28px; margin-bottom:24px;">
                <div style="color:#e2e8f0; font-size:1.05rem; font-weight:500; line-height:1.6;">
                    {domanda['domanda']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.risposta_data is None:
                for j, opzione in enumerate(domanda["opzioni"]):
                    if st.button(opzione, key=f"opt_{j}", use_container_width=True):
                        st.session_state.risposta_data = j
                        if j == domanda["corretta"]:
                            st.session_state.punteggio_quiz += 1
                        st.rerun()
            else:
                scelta = st.session_state.risposta_data
                corretta = domanda["corretta"]
                corretta_text = domanda["opzioni"][corretta]

                if scelta == corretta:
                    st.markdown(f"""
                    <div class="feedback-correct">
                        <strong>✅ Corretto!</strong><br><br>
                        <span style="color:#a7f3d0; font-size:0.9rem;">{domanda['spiegazione']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="feedback-wrong">
                        <strong>❌ Non esatto.</strong> La risposta corretta era:<br>
                        <span style="color:#fca5a5;">{corretta_text}</span><br><br>
                        <span style="color:#fca5a5; font-size:0.9rem;">{domanda['spiegazione']}</span>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("➡️ Prossima domanda" if q_idx < len(domande) - 1 else "🏁 Vedi risultato", use_container_width=True):
                    st.session_state.domanda_idx += 1
                    st.session_state.risposta_data = None
                    if st.session_state.domanda_idx >= len(domande):
                        st.session_state.fase = "risultato"
                    st.rerun()

        with col_info:
            st.markdown(f"""
            <div style="background:rgba(15,23,42,0.9); border:1px solid rgba(99,179,237,0.15); 
                 border-radius:12px; padding:16px; text-align:center; margin-bottom:12px;">
                <div style="color:#f6ad55; font-size:1.5rem; font-weight:700;">+{livello['xp']}</div>
                <div style="color:#475569; font-size:0.75rem;">XP in palio</div>
            </div>
            <div style="background:rgba(15,23,42,0.9); border:1px solid rgba(99,179,237,0.15); 
                 border-radius:12px; padding:16px; text-align:center;">
                <div style="color:#68d391; font-size:1.5rem; font-weight:700;">{st.session_state.punteggio_quiz}/{q_idx}</div>
                <div style="color:#475569; font-size:0.75rem;">Corrette</div>
            </div>
            """, unsafe_allow_html=True)

# ── RISULTATO ──────────────────────────────────────────────────────────────────
elif st.session_state.fase == "risultato":
    area = st.session_state.area_corrente
    lv_idx = st.session_state.livello_corrente
    livello = MISSIONS[area]["livelli"][lv_idx]
    domande = livello["domande"]
    score = st.session_state.punteggio_quiz
    totale = len(domande)
    percentuale = score / totale
    is_boss = livello.get("boss", False)

    # Calcola XP guadagnati
    xp_base = livello["xp"]
    if percentuale == 1.0:
        xp_gain = xp_base
        risultato_emoji = "🏆"
        risultato_text = "Perfetto! Masterclass completa!"
        color = "#68d391"
    elif percentuale >= 0.66:
        xp_gain = int(xp_base * 0.7)
        risultato_emoji = "✅"
        risultato_text = "Ottimo lavoro! Missione completata!"
        color = "#63b3ed"
    else:
        xp_gain = int(xp_base * 0.3)
        risultato_emoji = "📚"
        risultato_text = "Ripassate il materiale e riprovate!"
        color = "#f6ad55"

    # Aggiorna stato
    mid = missione_id(area, lv_idx)
    if percentuale >= 0.66 and mid not in st.session_state.missioni_completate:
        st.session_state.missioni_completate.append(mid)
        st.session_state.xp += xp_gain
        if percentuale == 1.0 or (score > 0 and st.session_state.streak >= 0):
            st.session_state.streak += 1
    elif percentuale < 0.66:
        st.session_state.streak = 0

    nuovi_badge = check_badge()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align:center; padding:40px; background:rgba(15,23,42,0.9); 
             border:1px solid {color}40; border-radius:24px; margin-bottom:24px;">
            <div style="font-size:4rem; margin-bottom:16px;">{risultato_emoji}</div>
            <div style="font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:800; color:#e2e8f0; margin-bottom:8px;">
                {risultato_text}
            </div>
            <div style="color:#475569; font-size:0.9rem; margin-bottom:28px;">
                {"⚔️ Boss sconfitto!" if is_boss and percentuale >= 0.66 else livello['titolo']}
            </div>
            
            <div style="display:flex; justify-content:center; gap:24px; margin-bottom:24px;">
                <div>
                    <div style="font-family:'Syne',sans-serif; font-size:2.5rem; font-weight:800; color:{color};">
                        {score}/{totale}
                    </div>
                    <div style="color:#475569; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">Risposte corrette</div>
                </div>
                <div style="width:1px; background:rgba(99,179,237,0.1);"></div>
                <div>
                    <div style="font-family:'Syne',sans-serif; font-size:2.5rem; font-weight:800; color:#f6ad55;">
                        +{xp_gain}
                    </div>
                    <div style="color:#475569; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;">XP Guadagnati</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if nuovi_badge:
            for emoji, nome, desc in nuovi_badge:
                st.markdown(f"""
                <div style="background:rgba(246,173,85,0.1); border:1px solid rgba(246,173,85,0.3); 
                     border-radius:12px; padding:16px; text-align:center; margin-bottom:12px;">
                    <div style="font-size:2rem;">{emoji}</div>
                    <div style="color:#f6ad55; font-weight:600;">🎖️ Nuovo Badge: {nome}!</div>
                    <div style="color:#78716c; font-size:0.85rem;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 Riprova", use_container_width=True):
                st.session_state.domanda_idx = 0
                st.session_state.risposta_data = None
                st.session_state.punteggio_quiz = 0
                st.session_state.fase = "quiz"
                st.rerun()
        with col_b:
            if st.button("🗺️ Torna alla Mappa", use_container_width=True):
                st.session_state.fase = "home"
                st.rerun()

# ── PROFILO ────────────────────────────────────────────────────────────────────
elif st.session_state.fase == "profilo":
    lv, titolo = get_livello(st.session_state.xp)

    st.markdown(f"""
    <div style="font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:800; color:#e2e8f0; margin-bottom:4px;">
        👤 Il Tuo Profilo
    </div>
    <div style="color:#475569; margin-bottom:32px;">{st.session_state.nome_studente} • {titolo}</div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    stats = [
        ("🎯", "XP Totali", st.session_state.xp),
        ("📚", "Missioni", len(st.session_state.missioni_completate)),
        ("⚡", "Livello", lv),
        ("🔥", "Streak", st.session_state.streak)
    ]
    for col, (icon, label, val) in zip([col1, col2, col3, col4], stats):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size:1.5rem; margin-bottom:4px;">{icon}</div>
                <div class="stat-number">{val}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Progress per area
    st.markdown("<div style='color:#e2e8f0; font-weight:600; margin-bottom:16px;'>Progresso per Area</div>", unsafe_allow_html=True)
    for area_key, area_data in MISSIONS.items():
        completate = sum(1 for m in st.session_state.missioni_completate if area_key in m)
        tot = len(area_data["livelli"])
        prog = completate / tot

        st.markdown(f"""
        <div style="margin-bottom:16px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="color:#e2e8f0; font-size:0.9rem;">{area_data['nome']}</span>
                <span style="color:#64748b; font-size:0.8rem;">{completate}/{tot}</span>
            </div>
            <div class="xp-bar-container">
                <div class="xp-bar-fill" style="width:{prog*100:.0f}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Badge
    st.markdown("<br><div style='color:#e2e8f0; font-weight:600; margin-bottom:16px;'>🎖️ Badge</div>", unsafe_allow_html=True)
    badge_map = {
        "primo_xp": ("🌟", "Prima Stella", "100 XP guadagnati"),
        "banche_master": ("🏦", "Banchiere", "Tutte le missioni banche"),
        "mercati_master": ("📈", "Trader", "Tutte le missioni mercati"),
        "rischio_master": ("🛡️", "Risk Manager", "Tutte le missioni rischio"),
        "finquest_champion": ("🏆", "FinQuest Champion", "Tutte le missioni completate!")
    }

    badge_cols = st.columns(5)
    for i, (badge_id, (emoji, nome, desc)) in enumerate(badge_map.items()):
        with badge_cols[i % 5]:
            ottenuto = badge_id in st.session_state.badge_guadagnati
            opacity = "1" if ottenuto else "0.25"
            st.markdown(f"""
            <div style="background:rgba(15,23,42,0.9); border:1px solid rgba(99,179,237,0.15); 
                 border-radius:12px; padding:16px; text-align:center; opacity:{opacity}; margin-bottom:8px;">
                <div style="font-size:2rem;">{emoji}</div>
                <div style="color:#e2e8f0; font-size:0.8rem; font-weight:600; margin-top:4px;">{nome}</div>
                <div style="color:#475569; font-size:0.7rem; margin-top:2px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
