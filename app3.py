import streamlit as st
import random
import json
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinAI Trader",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS  — Bloomberg terminal meets neon trading desk
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;600;700&family=Syne:wght@400;600;700;800&display=swap');

/* ── reset / base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Syne', sans-serif; }

.stApp {
    background: #060910;
    color: #c9d1d9;
    background-image:
        radial-gradient(ellipse 80% 40% at 50% 0%, #0d2137 0%, transparent 60%),
        repeating-linear-gradient(0deg, transparent, transparent 39px, #0d2137 39px, #0d2137 40px),
        repeating-linear-gradient(90deg, transparent, transparent 79px, #0d2137 79px, #0d2137 80px);
}

/* ── ticker tape ── */
.ticker-wrap {
    background: #0b1622;
    border-top: 1px solid #1b3a5c;
    border-bottom: 1px solid #1b3a5c;
    padding: 8px 0;
    overflow: hidden;
    margin-bottom: 0;
}
.ticker-inner {
    display: flex;
    gap: 56px;
    animation: ticker 22s linear infinite;
    white-space: nowrap;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
}
@keyframes ticker { from { transform: translateX(0); } to { transform: translateX(-50%); } }
.tick-up   { color: #00e5a0; }
.tick-down { color: #ff4f6d; }

/* ── main header ── */
.main-header {
    padding: 28px 36px 22px;
    border-bottom: 1px solid #1b3a5c;
    margin-bottom: 24px;
    position: relative;
}
.main-header::after {
    content: '';
    position: absolute;
    bottom: -1px; left: 0;
    width: 120px; height: 2px;
    background: linear-gradient(90deg, #00e5a0, transparent);
}
.logo-text {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -1px;
    color: #fff;
}
.logo-text span { color: #00e5a0; }
.logo-sub {
    font-size: 0.8rem;
    color: #4a6b8a;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-top: 4px;
}

/* ── stat pill ── */
.pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #0b1622;
    border: 1px solid #1b3a5c;
    border-radius: 6px;
    padding: 8px 16px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: #c9d1d9;
}
.pill .val { color: #00e5a0; font-weight: 700; font-size: 1rem; }
.pill .neg { color: #ff4f6d; font-weight: 700; font-size: 1rem; }

/* ── section heading ── */
.sec-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: #4a6b8a;
    border-bottom: 1px solid #1b3a5c;
    padding-bottom: 8px;
    margin-bottom: 18px;
}

/* ── scenario card ── */
.scenario-card {
    background: #0b1622;
    border: 1px solid #1b3a5c;
    border-left: 3px solid #00e5a0;
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 20px;
    position: relative;
}
.scenario-card .tag {
    display: inline-block;
    background: #00e5a015;
    border: 1px solid #00e5a033;
    color: #00e5a0;
    font-size: 0.68rem;
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 3px 10px;
    border-radius: 4px;
    margin-bottom: 12px;
}
.scenario-card .tag.red  { background:#ff4f6d15; border-color:#ff4f6d33; color:#ff4f6d; }
.scenario-card .tag.blue { background:#38bdf815; border-color:#38bdf833; color:#38bdf8; }
.scenario-card .title { font-size: 1.05rem; font-weight: 700; color: #fff; line-height: 1.45; }
.scenario-card .context { font-size: 0.85rem; color: #6e8a9e; margin-top: 8px; line-height: 1.6; }
.scenario-card .price-box {
    display: flex; gap: 24px; margin-top: 16px;
    font-family: 'IBM Plex Mono', monospace;
}
.price-item label { font-size: 0.68rem; text-transform: uppercase; letter-spacing: 1px; color: #4a6b8a; display: block; }
.price-item .val   { font-size: 1.3rem; font-weight: 700; }

/* ── action buttons ── */
.action-row { display: flex; gap: 12px; margin-top: 20px; flex-wrap: wrap; }

/* ── result card ── */
.result-card {
    border-radius: 8px;
    padding: 20px 24px;
    margin-top: 16px;
}
.result-card.win { background:#00e5a010; border:1px solid #00e5a044; }
.result-card.loss { background:#ff4f6d10; border:1px solid #ff4f6d44; }
.result-card.neutral { background:#38bdf810; border:1px solid #38bdf844; }
.result-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 6px; }
.result-card.win   .result-title { color: #00e5a0; }
.result-card.loss  .result-title { color: #ff4f6d; }
.result-card.neutral .result-title { color: #38bdf8; }
.result-explanation { font-size: 0.88rem; color: #8fa3b1; line-height: 1.6; }
.result-xp { font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem; margin-top: 12px; color: #c9d1d9; }

/* ── badge grid ── */
.badge-item {
    background: #0b1622;
    border: 1px solid #1b3a5c;
    border-radius: 8px;
    padding: 16px 12px;
    text-align: center;
    transition: border-color 0.2s, transform 0.2s;
}
.badge-item:hover { border-color: #00e5a055; transform: translateY(-2px); }
.badge-item.locked { opacity: 0.35; filter: grayscale(1); }
.badge-item .icon { font-size: 2.2rem; }
.badge-item .bname { font-size: 0.8rem; font-weight: 700; color: #c9d1d9; margin-top: 8px; }
.badge-item .bdesc { font-size: 0.7rem; color: #4a6b8a; margin-top: 4px; line-height: 1.4; }
.badge-item .unlocked-tag { font-size: 0.65rem; color: #00e5a0; font-family:'IBM Plex Mono',monospace; margin-top:6px; }

/* ── leaderboard ── */
.lb-row {
    display: flex; align-items: center;
    background: #0b1622;
    border: 1px solid #1b3a5c;
    border-radius: 6px;
    padding: 12px 18px;
    margin-bottom: 7px;
    gap: 12px;
    transition: border-color 0.2s;
}
.lb-row:hover { border-color: #00e5a033; }
.lb-row.me { border-color: #00e5a066; background: #00e5a00a; }
.lb-rank { font-family:'IBM Plex Mono',monospace; font-weight:700; font-size:0.9rem; width:32px; color:#4a6b8a; }
.lb-rank.g { color:#f5c518; } .lb-rank.s { color:#94a3b8; } .lb-rank.b { color:#b45309; }
.lb-name { flex:1; font-weight:600; font-size:0.92rem; color:#c9d1d9; }
.lb-level { font-size:0.72rem; color:#4a6b8a; margin-right:8px; }
.lb-coin { font-family:'IBM Plex Mono',monospace; font-size:0.85rem; color:#f5c518; font-weight:700; }
.lb-xp   { font-family:'IBM Plex Mono',monospace; font-size:0.85rem; color:#00e5a0; font-weight:700; margin-left:14px; }

/* ── XP bar ── */
.xp-track { background:#0d2137; border-radius:20px; height:8px; overflow:hidden; margin-top:5px; }
.xp-fill  { height:100%; border-radius:20px; background:linear-gradient(90deg,#00e5a0,#38bdf8); }

/* ── streamlit button overrides ── */
div.stButton > button {
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 1px !important;
    border-radius: 5px !important;
    transition: all 0.15s !important;
}
div.stButton > button[kind="primary"] {
    background: #00e5a0 !important;
    color: #060910 !important;
    border: none !important;
}
div.stButton > button[kind="primary"]:hover {
    background: #00ffb3 !important;
    box-shadow: 0 0 20px #00e5a055 !important;
    transform: translateY(-1px) !important;
}
div.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #c9d1d9 !important;
    border: 1px solid #1b3a5c !important;
}
div.stButton > button[kind="secondary"]:hover {
    border-color: #00e5a055 !important;
    color: #00e5a0 !important;
}

/* ── sidebar ── */
section[data-testid="stSidebar"] {
    background: #07111c !important;
    border-right: 1px solid #1b3a5c !important;
}
section[data-testid="stSidebar"] .stMarkdown { color: #8fa3b1; }

/* ── radio ── */
.stRadio > div { gap: 8px; }
.stRadio > div > label {
    background: #0b1622 !important;
    border: 1px solid #1b3a5c !important;
    border-radius: 6px !important;
    padding: 10px 16px !important;
    color: #c9d1d9 !important;
    font-size: 0.88rem !important;
    transition: border-color 0.15s !important;
    cursor: pointer !important;
}
.stRadio > div > label:hover { border-color: #00e5a055 !important; }

/* ── selectbox ── */
.stSelectbox > div > div { background: #0b1622 !important; border-color: #1b3a5c !important; color: #c9d1d9 !important; }

/* ── alert overrides ── */
.stSuccess { background: #00e5a010 !important; border-color: #00e5a055 !important; color: #00e5a0 !important; }
.stError   { background: #ff4f6d10 !important; border-color: #ff4f6d55 !important; }
.stInfo    { background: #38bdf810 !important; border-color: #38bdf855 !important; }
.stWarning { background: #f5c51810 !important; border-color: #f5c51855 !important; }

/* ── metric ── */
div[data-testid="stMetricValue"] { color: #00e5a0 !important; font-family:'IBM Plex Mono',monospace !important; }
div[data-testid="stMetricLabel"] { color: #4a6b8a !important; font-size: 0.75rem !important; }

/* ── divider ── */
hr { border-color: #1b3a5c !important; }

/* ── number input ── */
.stNumberInput > div > div > input { background: #0b1622 !important; border-color: #1b3a5c !important; color: #c9d1d9 !important; }

/* ── toast ── */
.professor-alert {
    background: #0b1622;
    border: 1px solid #38bdf8;
    border-left: 4px solid #38bdf8;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 16px;
}
.professor-alert .pa-header { font-size:0.7rem; text-transform:uppercase; letter-spacing:2px; color:#38bdf8; font-family:'IBM Plex Mono',monospace; margin-bottom:6px; }
.professor-alert .pa-body   { font-size:0.92rem; color:#c9d1d9; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS / DATA
# ─────────────────────────────────────────────────────────────────────────────

LEVELS = [
    (0,    "Junior Analyst"),
    (200,  "Quant Associate"),
    (500,  "ML Strategist"),
    (900,  "AI Portfolio Mgr"),
    (1400, "Head of FinAI"),
    (2000, "Chief AI Officer"),
]

BADGES = [
    {"id":"first_trade", "icon":"🎯","name":"First Trade",        "desc":"Execute your first decision",       "type":"trades","req":1},
    {"id":"trader_5",    "icon":"⚡","name":"Active Trader",      "desc":"Make 5 trading decisions",          "type":"trades","req":5},
    {"id":"trader_20",   "icon":"🔥","name":"High Frequency",     "desc":"Make 20 trading decisions",         "type":"trades","req":20},
    {"id":"winner_3",    "icon":"💰","name":"Three-Peat",         "desc":"Win 3 trades in a row",             "type":"win_streak","req":3},
    {"id":"coins_500",   "icon":"🏦","name":"Half-K Club",        "desc":"Accumulate 500 FinCoins",           "type":"coins","req":500},
    {"id":"coins_1000",  "icon":"💎","name":"FinCoin Millionaire","desc":"Accumulate 1000 FinCoins",          "type":"coins","req":1000},
    {"id":"xp_500",      "icon":"🚀","name":"XP Rocket",          "desc":"Reach 500 XP",                      "type":"xp","req":500},
    {"id":"fraud_badge", "icon":"🕵️","name":"Fraud Detective",    "desc":"Complete 3 Fraud scenarios",        "type":"topic","req":3,"topic":"Fraud Detection"},
    {"id":"nlp_badge",   "icon":"💬","name":"Text Alpha",         "desc":"Complete 3 NLP scenarios",          "type":"topic","req":3,"topic":"NLP in Finance"},
    {"id":"risk_badge",  "icon":"📉","name":"Risk Whisperer",     "desc":"Complete 3 Risk scenarios",         "type":"topic","req":3,"topic":"Risk Management"},
    {"id":"credit_badge","icon":"📊","name":"Credit Quant",       "desc":"Complete 3 Credit Risk scenarios",  "type":"topic","req":3,"topic":"Credit Risk"},
    {"id":"perfect_10",  "icon":"🎖️","name":"Perfect Analyst",   "desc":"Score 10 consecutive correct",      "type":"win_streak","req":10},
]

SCENARIOS = [
    # ── NLP in Finance
    {
        "id":1, "topic":"NLP in Finance", "difficulty":"easy",
        "title":"Earnings Call Sentiment Surge",
        "context": "You are an AI quant at a hedge fund. FinBERT analysis of Tesla's Q3 earnings call returns a sentiment score of +0.82 (very positive). The CEO mentioned 'record deliveries', 'margin expansion', and 'Cybertruck demand exceeding expectations'.",
        "asset":"TSLA", "price": 247.50, "signal":"BUY",
        "options":["📈 BUY — go long on positive NLP signal","📉 SHORT — fade the hype","⏸️ HOLD — wait for more data"],
        "correct":0,
        "outcome_win": "Excellent! TSLA +4.2% next session. FinBERT correctly captured management optimism. Positive earnings call sentiment is a well-documented alpha signal.",
        "outcome_loss": "TSLA rose +4.2%. Positive earnings call sentiment (score >0.7) is statistically significant. FinBERT identifies tonal nuances humans miss at scale.",
        "xp":15, "coins_win":40, "coins_loss":-15,
    },
    {
        "id":2, "topic":"NLP in Finance", "difficulty":"medium",
        "title":"Central Bank Hawkish Pivot",
        "context": "Fed minutes NLP analysis shows: 'inflation' mentioned 47 times (+120% vs previous minutes), 'patient' mentioned 0 times (vs 8 previously), 'restrictive' mentioned 12 times. Topic model detects shift from 'monitoring' cluster to 'action' cluster.",
        "asset":"10Y BOND", "price": 96.20, "signal":"SELL",
        "options":["📉 SHORT BONDS — rates going up","📈 BUY BONDS — Fed will pivot","⏸️ HOLD — ambiguous signal"],
        "correct":0,
        "outcome_win": "Correct! Fed hiked 50bp. NLP frequency analysis of 'inflation' (+120%) and disappearance of 'patient' are classic hawkish pivot signals.",
        "outcome_loss": "Fed hiked 50bp. The NLP features were clear: inflation frequency surge + removal of dovish language = textbook hawkish signal detectable by topic models.",
        "xp":20, "coins_win":55, "coins_loss":-20,
    },
    {
        "id":3, "topic":"NLP in Finance", "difficulty":"hard",
        "title":"Alternative Data: Glassdoor AI Signal",
        "context": "Your NLP pipeline scrapes 3,200 Glassdoor reviews for a major bank. BERT classification detects: 38% mention 'legacy systems', 23% mention 'talent leaving for Big Tech', review volume increased 180% (negative reviews). This is 6 months before their Q4 report.",
        "asset":"BANK_X", "price": 58.10, "signal":"SHORT",
        "options":["📉 SHORT — NLP alternative data predicts earnings miss","📈 BUY — contrarian play on depressed sentiment","⏸️ HOLD — alternative data too noisy"],
        "correct":0,
        "outcome_win": "Perfect call! Bank_X missed EPS by 22%. Employee NLP data is a leading indicator — talent attrition precedes tech underinvestment, which precedes earnings misses.",
        "outcome_loss": "Bank_X missed EPS by 22%. Alternative NLP data (employee reviews) is a 6-month leading indicator of operational weakness. This alpha is now widely harvested by quant funds.",
        "xp":30, "coins_win":80, "coins_loss":-25,
    },

    # ── Fraud Detection
    {
        "id":4, "topic":"Fraud Detection", "difficulty":"easy",
        "title":"Real-Time Transaction Alert",
        "context": "Your fraud ML model (XGBoost, AUC=0.97) flags transaction #TX8821: €4,200 at 3:47am, location Nigeria, device fingerprint new, velocity: 8 transactions in 2 hours. Fraud probability: 0.94. Normal threshold: 0.80.",
        "asset":"TX #8821", "price": 4200.00, "signal":"BLOCK",
        "options":["🚫 BLOCK — high probability fraud","✅ APPROVE — might be false positive","🔍 STEP-UP AUTH — request 2FA"],
        "correct":2,
        "outcome_win": "Brilliant! Step-up auth revealed the customer was legitimate (travelling for work) but appreciated the check. Blocking would have caused false positive damage; approving would have been reckless at p=0.94.",
        "outcome_loss": "Step-up authentication was optimal here. At p=0.94 you can't blindly approve, but blocking a real customer (false positive) damages trust and revenue. 2FA balances risk and UX.",
        "xp":20, "coins_win":50, "coins_loss":-20,
    },
    {
        "id":5, "topic":"Fraud Detection", "difficulty":"medium",
        "title":"Model Drift: Fraud Pattern Shift",
        "context": "Your production fraud model's AUC dropped from 0.97 to 0.81 over 90 days. Feature importance analysis shows 'merchant_category' weight dropped 60%. New fraud pattern: criminals are now using micro-transactions (€0.01-€2.00) to test stolen cards — a pattern your model never saw in training.",
        "asset":"FRAUD MODEL v2.1", "price":0, "signal":"RETRAIN",
        "options":["🔄 RETRAIN immediately with new fraud patterns","⏳ WAIT — collect more data first","📋 RULE-BASED fallback — add €0-€5 velocity rule"],
        "correct":0,
        "outcome_win": "Correct! Immediate retraining restored AUC to 0.96. Concept drift in fraud requires rapid model updates — criminals adapt faster than quarterly retraining cycles.",
        "outcome_loss": "Retraining was urgent. Concept drift (AUC -16%) means attackers have found your model's blind spot. Every day of delay costs €000s in undetected micro-transaction fraud.",
        "xp":25, "coins_win":65, "coins_loss":-20,
    },
    {
        "id":6, "topic":"Fraud Detection", "difficulty":"hard",
        "title":"Graph Neural Network: Mule Account Ring",
        "context": "Your GNN fraud detection model identifies a suspicious cluster: 47 accounts, all opened within 14 days, transaction graph shows star topology (central hub distributing funds to spokes), average account age 18 days, all linked to 3 IP addresses. Individual account scores are 0.61-0.71 (below 0.80 threshold), but graph-level risk score: 0.96.",
        "asset":"ACCOUNT RING", "price":0, "signal":"INVESTIGATE",
        "options":["🚨 FLAG ALL 47 accounts for investigation","✅ APPROVE — individual scores are below threshold","🔍 FLAG only the hub account"],
        "correct":0,
        "outcome_win": "Excellent! Investigation confirmed a money mule ring laundering €340k. This is the power of Graph ML — individual scores miss coordinated fraud that's obvious at network level.",
        "outcome_loss": "All 47 accounts were part of a €340k money mule ring. GNNs catch coordinated fraud invisible to individual account models. Network topology (star pattern + shared IPs) is a canonical mule ring signature.",
        "xp":35, "coins_win":90, "coins_loss":-30,
    },

    # ── Credit Risk
    {
        "id":7, "topic":"Credit Risk", "difficulty":"easy",
        "title":"SME Loan Decision: Beyond the Score",
        "context": "Loan application: €500k for a restaurant chain. Traditional credit score: 620 (borderline). Your ML model adds alternative features: Yelp reviews NLP score +0.71, Google Maps foot traffic +34% YoY, social media mentions +89%, delivery app revenue €180k/month. ML-adjusted PD: 3.2% vs traditional score implied 8.1%.",
        "asset":"LOAN #L-2241", "price": 500000, "signal":"APPROVE",
        "options":["✅ APPROVE — ML model shows lower real PD","❌ REJECT — traditional score too low","📋 APPROVE with higher rate — price the risk"],
        "correct":0,
        "outcome_win": "Great decision! Loan fully repaid. Alternative data (foot traffic, NLP reviews) provided a more accurate PD than backward-looking credit scores — textbook ML credit uplift.",
        "outcome_loss": "This loan performed perfectly. Alternative data revealed hidden creditworthiness. Relying solely on traditional scores creates systematic bias against young and asset-light businesses.",
        "xp":15, "coins_win":40, "coins_loss":-15,
    },
    {
        "id":8, "topic":"Credit Risk", "difficulty":"medium",
        "title":"Portfolio Stress Test: Rate Shock",
        "context": "You manage a €2B SME loan portfolio. Macro model predicts: rates +300bp shock scenario (probability 15%), GDP -2.1%, unemployment +4.2%. Your ML stress model outputs: PD uplift +180%, expected portfolio loss €340M (17%). Current capital buffer: €280M.",
        "asset":"SME PORTFOLIO", "price":2e9, "signal":"HEDGE",
        "options":["🛡️ BUY credit protection (CDS) to cover shortfall","📈 KEEP full exposure — 15% scenario too unlikely","💰 SELL 15% of portfolio to reduce concentration"],
        "correct":0,
        "outcome_win": "Textbook risk management! The rate shock materialized. Your CDS position offset €62M of the €340M loss — within capital buffer. Without the hedge, you'd have breached Pillar 2 capital requirements.",
        "outcome_loss": "The rate shock hit. €340M loss exceeded your €280M buffer. Buying CDS protection was the right Basel III response to a model-identified tail risk that exceeded your capital cushion.",
        "xp":25, "coins_win":65, "coins_loss":-25,
    },
    {
        "id":9, "topic":"Credit Risk", "difficulty":"hard",
        "title":"IFRS 9: Stage Migration Decision",
        "context": "Corporate client ABC Corp: currently Stage 1 (performing). Signals: EBITDA margin -40% QoQ, leverage ratio crossed 5x, sector (commercial real estate) entered watchlist, management replacement. Your ML IFRS 9 model: Stage 2 migration probability 0.78. Migration would require €12M additional provision.",
        "asset":"ABC CORP LOAN", "price":0, "signal":"STAGE2",
        "options":["📋 MIGRATE to Stage 2 — model says 0.78","⏳ KEEP Stage 1 — wait for next quarter data","📞 MANUAL REVIEW — escalate to credit committee"],
        "correct":2,
        "outcome_win": "Correct judgment! Credit committee identified a material covenant breach, confirmed Stage 2. Manual override on high-stakes decisions is best practice — ML is input, not dictator.",
        "outcome_loss": "Credit committee found a covenant breach and confirmed Stage 2 (€14M provision needed). At p=0.78, a €12M provision decision should involve human judgment. IFRS 9 requires management overlay on significant exposures.",
        "xp":35, "coins_win":90, "coins_loss":-30,
    },

    # ── Algorithmic Trading
    {
        "id":10, "topic":"Algorithmic Trading", "difficulty":"easy",
        "title":"Backtest Looks Perfect — Too Perfect",
        "context": "Your LSTM trading strategy backtest: Sharpe 3.8, max drawdown -4%, annualized return +62%. But: in-sample period 2019-2023 (bull run), no transaction costs modeled, no slippage, strategy rebalances daily. Out-of-sample test on 2024 data: Sharpe 0.3, return -8%.",
        "asset":"LSTM STRATEGY v1", "price":0, "signal":"REJECT",
        "options":["❌ REJECT — classic overfitting, do not deploy","✅ DEPLOY — backtest results are strong","🔧 TWEAK parameters and retest"],
        "correct":0,
        "outcome_win": "Exactly right. This is textbook overfitting: LSTM memorized the 2019-2023 bull market. Sharpe 3.8 in-sample → 0.3 out-of-sample is the clearest overfitting signature in quant finance.",
        "outcome_loss": "This was overfitting. The massive performance gap (Sharpe 3.8 → 0.3) with no transaction costs and in-sample-only testing is a cardinal sin in strategy development. Deploying this would lose real money.",
        "xp":15, "coins_win":40, "coins_loss":-15,
    },
    {
        "id":11, "topic":"Algorithmic Trading", "difficulty":"medium",
        "title":"RL Agent: Regime Change Crisis",
        "context": "Your Reinforcement Learning trading agent (trained on 2015-2023 data) is live. It was trained in low-volatility regime (VIX avg 18). Current market: VIX = 42 (2020 COVID-like spike), correlation breakdown — all assets moving together. RL agent starts taking maximum position sizes.",
        "asset":"RL AGENT LIVE", "price":0, "signal":"PAUSE",
        "options":["⏸️ PAUSE agent — out-of-distribution regime","🔄 LET IT RUN — RL adapts in real time","📉 REDUCE position limits by 50%"],
        "correct":0,
        "outcome_win": "Correct! Pausing prevented a €800k loss. RL agents trained on historical data fail catastrophically in out-of-distribution regimes. VIX 42 with correlation breakdown is exactly the regime they've never seen.",
        "outcome_loss": "The agent lost €800k before emergency stop. VIX 42 is out-of-distribution for a model trained on VIX avg 18. RL agents don't 'adapt in real time' — they extrapolate their training distribution incorrectly.",
        "xp":25, "coins_win":65, "coins_loss":-25,
    },
    {
        "id":12, "topic":"Algorithmic Trading", "difficulty":"hard",
        "title":"Market Microstructure: Adversarial Trading",
        "context": "Your HFT algorithm detects an anomaly: when it places large buy orders (>€500k), the ask price jumps 8bp before execution 73% of the time. Analysis: a competing firm's ML model detects your order flow fingerprint and front-runs. Your order ID pattern is predictable (sequential).",
        "asset":"HFT ALGO", "price":0, "signal":"RANDOMIZE",
        "options":["🎲 RANDOMIZE order IDs + add random delays","📈 INCREASE order size to overwhelm front-runner","⏸️ STOP trading until investigation complete"],
        "correct":0,
        "outcome_win": "Brilliant! Randomizing order IDs + timing reduced front-running from 73% to 11%. Order flow toxicity is a game-theoretic ML problem — your adaptation forced them to retrain.",
        "outcome_loss": "Randomizing was the solution. Order fingerprinting by adversarial ML is a known market microstructure problem. Sequential IDs + predictable timing = free alpha for front-runners. Randomization breaks the signal.",
        "xp":35, "coins_win":90, "coins_loss":-30,
    },

    # ── Risk Management
    {
        "id":13, "topic":"Risk Management", "difficulty":"easy",
        "title":"VaR Limit Breach: What Now?",
        "context": "Daily VaR report: your trading desk's 1-day 99% VaR = €8.2M. Your limit is €7.5M (breach of €700k). Current positions: long €120M in tech stocks, short €40M in bonds. Risk manager pings you at 8:15am.",
        "asset":"TRADING BOOK", "price":0, "signal":"REDUCE",
        "options":["📉 REDUCE tech long to bring VaR under limit","📈 KEEP positions — VaR breach is small","📋 REQUEST temporary limit increase from CRO"],
        "correct":0,
        "outcome_win": "Correct action! Reducing the tech long brought VaR to €7.1M. Limit breaches must be resolved by position reduction — requesting an override for a systematic breach signals poor risk culture to regulators.",
        "outcome_loss": "VaR limits are hard constraints under Basel III. A €700k breach requires immediate position reduction, not override requests. The correct response is to reduce positions to restore compliance.",
        "xp":15, "coins_win":40, "coins_loss":-15,
    },
    {
        "id":14, "topic":"Risk Management", "difficulty":"medium",
        "title":"Model Risk: CVaR vs VaR Discrepancy",
        "context": "Two risk models give different outputs for the same portfolio: Model A (Historical VaR): €12M loss at 99%. Model B (Monte Carlo CVaR): €31M expected loss in the worst 1% of scenarios. Stress test (2008-like): €67M. CFO wants to report the lower number to the board.",
        "asset":"RISK REPORT", "price":0, "signal":"CVaR",
        "options":["📊 REPORT CVaR (€31M) + stress test — full picture","📉 REPORT VaR (€12M) — standard regulatory metric","📋 REPORT all three with clear explanation"],
        "correct":2,
        "outcome_win": "Excellent judgment! Reporting all three with context is best practice. VaR alone is misleading; CVaR captures tail severity; stress test provides scenario intuition. Selective reporting to the board is a governance failure.",
        "outcome_loss": "Reporting all three was the gold standard. VaR(€12M) hides the tail, CVaR(€31M) shows average tail loss, stress test(€67M) provides intuition. Cherry-picking the lowest number is the kind of model risk governance failure that caused the 2008 crisis.",
        "xp":25, "coins_win":65, "coins_loss":-25,
    },
    {
        "id":15, "topic":"Risk Management", "difficulty":"hard",
        "title":"Liquidity Crisis: Fire Sale Cascade",
        "context": "Liquidity stress scenario: 3 large clients simultaneously withdraw €2.1B (LCR drops to 87%, minimum 100%). Your liquid asset buffer: €1.8B. Options require modeling second-order effects: selling bonds depresses prices (market impact model: -2.3% per €500M), triggering margin calls on your repo book (€340M additional need).",
        "asset":"LIQUIDITY BUFFER", "price":0, "signal":"COMPLEX",
        "options":["💧 DRAW ON ECB FACILITY — avoid fire sale cascade","📉 SELL bonds immediately to raise cash","📞 EMERGENCY CREDIT LINE from correspondent banks"],
        "correct":0,
        "outcome_win": "Superb! ECB facility access prevented a fire sale cascade. Your market impact model correctly predicted: selling €1.8B in bonds would have triggered €340M additional margin calls — a classic liquidity spiral.",
        "outcome_loss": "The ECB facility was optimal. Selling €1.8B in bonds would have triggered the market impact cascade (-2.3% × €1.8B = €41M loss) + €340M in margin calls. Liquidity spirals are self-reinforcing — avoid fire sales when central bank facilities exist.",
        "xp":35, "coins_win":90, "coins_loss":-30,
    },
]

PROF_CHALLENGES = [
    {"title":"🔴 LIVE: Flash Crash Alert", "desc":"Markets dropped 8% in 4 minutes. Navigate your portfolio through the crisis. +50 bonus XP for survivors!", "topic":"Risk Management"},
    {"title":"📰 BREAKING: Fraud Wave", "desc":"Carderplanet just dumped 2M stolen cards. Your fraud model must adapt NOW. Special scenario unlocked.", "topic":"Fraud Detection"},
    {"title":"💬 NLP CHALLENGE", "desc":"Analyze 3 earnings calls in 5 minutes. Fastest student with all correct gets 100 FinCoins bonus!", "topic":"NLP in Finance"},
    {"title":"🏆 TOURNAMENT MODE", "desc":"Prof has activated 1v1 tournament. Top 3 scorers this hour get extra credit!", "topic":"All"},
]

LEADERBOARD_DEMO = [
    {"name":"Alice M.",  "xp":1820,"coins":1240,"trades":64,"streak":8, "level":"Head of FinAI"},
    {"name":"Luca R.",   "xp":1550,"coins":1050,"trades":55,"streak":6, "level":"AI Portfolio Mgr"},
    {"name":"Sara K.",   "xp":1310,"coins":890, "trades":47,"streak":5, "level":"AI Portfolio Mgr"},
    {"name":"Omar T.",   "xp":1100,"coins":740, "trades":39,"streak":4, "level":"ML Strategist"},
    {"name":"Chiara B.", "xp":880, "coins":580, "trades":31,"streak":3, "level":"ML Strategist"},
    {"name":"James W.",  "xp":650, "coins":420, "trades":24,"streak":2, "level":"Quant Associate"},
    {"name":"Priya S.",  "xp":480, "coins":310, "trades":17,"streak":1, "level":"Quant Associate"},
]

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
def init():
    defaults = {
        "name":"","xp":0,"coins":200,"trades":0,"correct":0,
        "win_streak":0,"max_win_streak":0,
        "earned_badges":[],"answered_ids":[],"topic_counts":{},
        "current_scenario":None,"scenario_feedback":None,
        "page":"home","pending_bet":None,
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init()

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def get_level(xp):
    lvl = LEVELS[0]
    for l in LEVELS:
        if xp >= l[0]: lvl = l
    return lvl

def xp_pct(xp):
    for i,l in enumerate(LEVELS[:-1]):
        if xp < LEVELS[i+1][0]:
            lo,hi = l[0], LEVELS[i+1][0]
            return (xp-lo)/(hi-lo)*100, LEVELS[i+1][1]
    return 100,"MAX"

def check_badges():
    s=st.session_state; new=[]
    for b in BADGES:
        if b["id"] in s["earned_badges"]: continue
        t=b["type"]; earned=False
        if   t=="trades"    and s["trades"]>=b["req"]: earned=True
        elif t=="win_streak"and s["max_win_streak"]>=b["req"]: earned=True
        elif t=="coins"     and s["coins"]>=b["req"]: earned=True
        elif t=="xp"        and s["xp"]>=b["req"]: earned=True
        elif t=="topic"     and s["topic_counts"].get(b.get("topic",""),0)>=b["req"]: earned=True
        if earned:
            s["earned_badges"].append(b["id"]); new.append(b)
    return new

def get_scenario(topic=None):
    avail=[q for q in SCENARIOS if q["id"] not in st.session_state["answered_ids"]]
    if topic: avail=[q for q in avail if q["topic"]==topic] or avail
    if not avail:
        st.session_state["answered_ids"]=[]
        avail=SCENARIOS
    return random.choice(avail)

def diff_color(d): return {"easy":"#00e5a0","medium":"#f5c518","hard":"#ff4f6d"}.get(d,"#aaa")

# ─────────────────────────────────────────────────────────────────────────────
# TICKER TAPE
# ─────────────────────────────────────────────────────────────────────────────
def render_ticker():
    items=[
        ("TSLA","247.50","+4.2%",True),("JPM","198.30","-0.8%",False),
        ("GS","412.10","+1.1%",True),("BTC","67,420","+2.3%",True),
        ("EUR/USD","1.0841","-0.3%",False),("10Y","4.38%","+0.12%",False),
        ("VIX","18.2","-5.1%",True),("GLD","2,034","+0.7%",True),
        ("NVDA","875.40","+3.6%",True),("C","58.90","-1.2%",False),
    ]
    def tick(t): cls="tick-up" if t[3] else "tick-down"; return f'<span>{t[0]}&nbsp;<span class="{cls}">{t[1]}&nbsp;{t[2]}</span></span>'
    inner="".join([tick(t) for t in items]*3)
    st.markdown(f'<div class="ticker-wrap"><div class="ticker-inner">{inner}</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
render_ticker()

with st.sidebar:
    st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:1.05rem;font-weight:700;color:#fff;padding:12px 0 4px;">📈 FinAI Trader</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:2px;color:#4a6b8a;margin-bottom:16px;">AI in Banking & Finance · Master</div>', unsafe_allow_html=True)

    if not st.session_state["name"]:
        name=st.text_input("Your trader name:", placeholder="e.g. Alice M.")
        if st.button("🚀 Enter Trading Floor", use_container_width=True, type="primary"):
            if name.strip():
                st.session_state["name"]=name.strip()
                st.rerun()
    else:
        lvl=get_level(st.session_state["xp"])
        pct,next_lvl=xp_pct(st.session_state["xp"])
        st.markdown(f"""
        <div style="background:#0b1622;border:1px solid #1b3a5c;border-radius:8px;padding:14px 16px;margin-bottom:14px;">
            <div style="font-weight:700;color:#fff;font-size:0.95rem">{st.session_state['name']}</div>
            <div style="color:#00e5a0;font-size:0.75rem;font-family:'IBM Plex Mono',monospace;margin-top:2px">{lvl[1]}</div>
            <div style="margin-top:10px;">
                <div style="display:flex;justify-content:space-between;font-size:0.68rem;color:#4a6b8a;margin-bottom:4px;">
                    <span>{st.session_state['xp']} XP</span><span>→ {next_lvl}</span>
                </div>
                <div class="xp-track"><div class="xp-fill" style="width:{pct:.0f}%"></div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1,col2=st.columns(2)
        with col1: st.markdown(f'<div class="pill">🪙 <span class="val">{st.session_state["coins"]}</span></div>', unsafe_allow_html=True)
        with col2: st.markdown(f'<div class="pill">⚡ <span class="val">{st.session_state["xp"]}</span></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        NAV={
            "🏠  Trading Floor":"home",
            "📈  Trade Scenarios":"trade",
            "📚  Topic Drill":"topics",
            "🏆  Leaderboard":"leaderboard",
            "🎖️  Badges":"badges",
            "📡  Professor Mode":"professor",
        }
        for label,pid in NAV.items():
            active=st.session_state["page"]==pid
            if st.button(label,use_container_width=True,type="primary" if active else "secondary"):
                st.session_state.update({"page":pid,"scenario_feedback":None,"current_scenario":None})
                st.rerun()

        st.markdown("<br>")
        if st.button("⟲ Reset",use_container_width=True):
            for k in ["xp","trades","correct","win_streak","max_win_streak","earned_badges","answered_ids","topic_counts","scenario_feedback","current_scenario","pending_bet"]:
                st.session_state[k]= [] if k in ["earned_badges","answered_ids"] else ({} if k=="topic_counts" else (None if k in ["scenario_feedback","current_scenario","pending_bet"] else 0))
            st.session_state["coins"]=200
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state["name"]:
    # ── LANDING ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="main-header">
        <div class="logo-text">Fin<span>AI</span> Trader</div>
        <div class="logo-sub">AI in Banking & Finance · Master Programme · Trading Simulation</div>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3=st.columns(3)
    with c1:
        st.markdown("""
        <div class="scenario-card">
            <div class="tag">Real Scenarios</div>
            <div class="title">15 Bloomberg-style trading decisions</div>
            <div class="context">NLP signals, fraud alerts, credit risk, algo trading, risk management — all grounded in real AI applications.</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="scenario-card" style="border-left-color:#38bdf8">
            <div class="tag blue">Earn & Spend</div>
            <div class="title">FinCoins economy + XP level system</div>
            <div class="context">Win FinCoins on correct decisions. Lose them on mistakes. Level up from Junior Analyst to Chief AI Officer.</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="scenario-card" style="border-left-color:#ff4f6d">
            <div class="tag red">Live Mode</div>
            <div class="title">Professor launches challenges in real time</div>
            <div class="context">Professor Mode sends live crisis scenarios to the whole class. Tournament, flash crashes, breaking news — all during class.</div>
        </div>""", unsafe_allow_html=True)

    st.info("👈 Enter your trader name in the sidebar to access the Trading Floor")

else:
    page=st.session_state["page"]

    # ── HOME / TRADING FLOOR ──────────────────────────────────────────────────
    if page=="home":
        st.markdown(f"""
        <div class="main-header">
            <div class="logo-text">Trading Floor</div>
            <div class="logo-sub">Welcome back, {st.session_state['name']} · {get_level(st.session_state['xp'])[1]}</div>
        </div>""", unsafe_allow_html=True)

        c1,c2,c3,c4=st.columns(4)
        with c1: st.metric("🪙 FinCoins", st.session_state["coins"])
        with c2: st.metric("⚡ XP", st.session_state["xp"])
        with c3: st.metric("📊 Trades", st.session_state["trades"])
        with c4: st.metric("🏅 Badges", len(st.session_state["earned_badges"]))

        st.markdown("<br>", unsafe_allow_html=True)

        # Topic progress
        st.markdown('<div class="sec-title">📋 Course Modules Progress</div>', unsafe_allow_html=True)
        topics=[
            ("💬","NLP in Finance",        "FinBERT · Sentiment · Alt Data"),
            ("🕵️","Fraud Detection",       "GNN · SMOTE · Concept Drift"),
            ("📊","Credit Risk",           "PD · IFRS 9 · Stress Test"),
            ("📈","Algorithmic Trading",   "RL · Overfitting · Microstructure"),
            ("📉","Risk Management",       "VaR · CVaR · Liquidity Spiral"),
        ]
        cols=st.columns(5)
        for i,(emoji,name,sub) in enumerate(topics):
            done=st.session_state["topic_counts"].get(name,0)
            total=len([s for s in SCENARIOS if s["topic"]==name])
            with cols[i]:
                st.markdown(f"""
                <div class="badge-item" style="text-align:left;padding:14px;">
                    <div style="font-size:1.6rem">{emoji}</div>
                    <div style="font-weight:700;font-size:0.82rem;color:#c9d1d9;margin-top:6px">{name}</div>
                    <div style="font-size:0.7rem;color:#4a6b8a;margin-top:3px">{sub}</div>
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:#00e5a0;margin-top:8px">{done}/{total} done</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c_a,c_b,c_c=st.columns(3)
        with c_a:
            if st.button("📈 Start Trading", use_container_width=True, type="primary"):
                st.session_state.update({"page":"trade","current_scenario":None,"scenario_feedback":None}); st.rerun()
        with c_b:
            if st.button("🏆 Leaderboard", use_container_width=True):
                st.session_state["page"]="leaderboard"; st.rerun()
        with c_c:
            if st.button("📡 Professor Mode", use_container_width=True):
                st.session_state["page"]="professor"; st.rerun()

    # ── TRADE SCENARIOS ───────────────────────────────────────────────────────
    elif page=="trade":
        st.markdown("""
        <div class="main-header">
            <div class="logo-text">📈 Trade Scenarios</div>
            <div class="logo-sub">AI-powered market intelligence · Make your call</div>
        </div>""", unsafe_allow_html=True)

        if st.session_state["current_scenario"] is None:
            st.session_state["current_scenario"]=get_scenario()
            st.session_state["scenario_feedback"]=None

        sc=st.session_state["current_scenario"]
        diff_c=diff_color(sc["difficulty"])

        # Asset price box
        tag_color={"NLP in Finance":"","Fraud Detection":"red","Credit Risk":"blue"}.get(sc["topic"],"")
        st.markdown(f"""
        <div class="scenario-card">
            <div class="tag {tag_color}">{sc['topic']} · {sc['difficulty'].upper()} · +{sc['xp']} XP</div>
            <div class="title">{sc['title']}</div>
            <div class="context">{sc['context']}</div>
            <div class="price-box">
                <div class="price-item">
                    <label>Asset</label>
                    <div class="val" style="color:#00e5a0">{sc['asset']}</div>
                </div>
                <div class="price-item">
                    <label>AI Signal</label>
                    <div class="val" style="color:#f5c518">{sc['signal']}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        if st.session_state["scenario_feedback"] is None:
            # Bet sizing
            st.markdown('<div class="sec-title">💰 Size Your Position</div>', unsafe_allow_html=True)
            max_bet=min(st.session_state["coins"], 100)
            bet=st.slider("FinCoins to stake (multiplies your win/loss):", 10, max(10, max_bet), min(30, max_bet), 5)

            st.markdown('<div class="sec-title" style="margin-top:20px">🎯 Your Decision</div>', unsafe_allow_html=True)
            choice=st.radio("", sc["options"], key=f"sc_{sc['id']}")

            c_sub, c_skip = st.columns([3,1])
            with c_sub:
                if st.button("⚡ EXECUTE TRADE", use_container_width=True, type="primary"):
                    selected=sc["options"].index(choice)
                    correct=(selected==sc["correct"])
                    multiplier=bet/30

                    if correct:
                        xp_gain=sc["xp"]
                        coin_gain=int(sc["coins_win"]*multiplier)
                        st.session_state["xp"]+=xp_gain
                        st.session_state["coins"]+=coin_gain
                        st.session_state["correct"]+=1
                        st.session_state["win_streak"]+=1
                        st.session_state["max_win_streak"]=max(st.session_state["max_win_streak"],st.session_state["win_streak"])
                    else:
                        xp_gain=sc["xp"]//4
                        coin_gain=int(sc["coins_loss"]*multiplier)
                        st.session_state["xp"]+=xp_gain
                        st.session_state["coins"]=max(0,st.session_state["coins"]+coin_gain)
                        st.session_state["win_streak"]=0

                    st.session_state["trades"]+=1
                    st.session_state["answered_ids"].append(sc["id"])
                    tc=st.session_state["topic_counts"]
                    tc[sc["topic"]]=tc.get(sc["topic"],0)+1

                    new_badges=check_badges()
                    st.session_state["scenario_feedback"]={
                        "correct":correct,"xp_gain":xp_gain,
                        "coin_gain":coin_gain,"new_badges":new_badges,
                    }
                    st.rerun()
            with c_skip:
                if st.button("⏭ Skip", use_container_width=True):
                    st.session_state.update({"current_scenario":None,"scenario_feedback":None}); st.rerun()

        else:
            fb=st.session_state["scenario_feedback"]
            if fb["correct"]:
                st.markdown(f"""
                <div class="result-card win">
                    <div class="result-title">✅ CORRECT DECISION</div>
                    <div class="result-explanation">{sc['outcome_win']}</div>
                    <div class="result-xp">+{fb['xp_gain']} XP &nbsp;|&nbsp; +{fb['coin_gain']} 🪙 FinCoins</div>
                </div>""", unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown(f"""
                <div class="result-card loss">
                    <div class="result-title">❌ INCORRECT — Here's what you missed</div>
                    <div class="result-explanation">{sc['outcome_loss']}</div>
                    <div class="result-xp">+{fb['xp_gain']} XP (consolation) &nbsp;|&nbsp; {fb['coin_gain']} 🪙 FinCoins</div>
                </div>""", unsafe_allow_html=True)

            for b in fb.get("new_badges",[]):
                st.markdown(f"""
                <div class="result-card neutral" style="margin-top:10px">
                    <div class="result-title">{b['icon']} Badge Unlocked: {b['name']}</div>
                    <div class="result-explanation">{b['desc']}</div>
                </div>""", unsafe_allow_html=True)

            if st.button("➡️ Next Scenario", use_container_width=True, type="primary"):
                st.session_state.update({"current_scenario":None,"scenario_feedback":None}); st.rerun()

        # Stats strip
        st.markdown("<br>")
        c1,c2,c3,c4=st.columns(4)
        with c1: st.metric("🪙 FinCoins",st.session_state["coins"])
        with c2: st.metric("⚡ XP",st.session_state["xp"])
        with c3: st.metric("🔥 Win Streak",st.session_state["win_streak"])
        with c4: st.metric("📊 Trades",st.session_state["trades"])

    # ── TOPIC DRILL ───────────────────────────────────────────────────────────
    elif page=="topics":
        st.markdown("""
        <div class="main-header">
            <div class="logo-text">📚 Topic Drill</div>
            <div class="logo-sub">Master a specific module · Unlock topic badges</div>
        </div>""", unsafe_allow_html=True)

        all_topics=sorted(set(s["topic"] for s in SCENARIOS))
        sel=st.selectbox("Select Module:", all_topics)
        topic_scenarios=[s for s in SCENARIOS if s["topic"]==sel]

        c1,c2=st.columns(2)
        with c1: st.metric("Total Scenarios",len(topic_scenarios))
        with c2: st.metric("Completed",st.session_state["topic_counts"].get(sel,0))

        if st.button(f"🎯 Drill {sel}", type="primary", use_container_width=True):
            st.session_state.update({"current_scenario":get_scenario(sel),"scenario_feedback":None,"page":"trade"})
            st.rerun()

        st.markdown("<br>")
        st.markdown('<div class="sec-title">Scenario Overview</div>', unsafe_allow_html=True)
        for s in topic_scenarios:
            done="✅" if s["id"] in st.session_state["answered_ids"] else "⬜"
            diff_c=diff_color(s["difficulty"])
            st.markdown(f"""
            <div class="scenario-card" style="border-left-color:{diff_c};opacity:{'0.7' if done=='✅' else '1'}">
                <div class="tag">{s['difficulty'].upper()} · {s['xp']} XP</div>
                <div class="title">{done} {s['title']}</div>
                <div class="context">{s['context'][:140]}...</div>
            </div>""", unsafe_allow_html=True)

    # ── LEADERBOARD ───────────────────────────────────────────────────────────
    elif page=="leaderboard":
        st.markdown("""
        <div class="main-header">
            <div class="logo-text">🏆 Leaderboard</div>
            <div class="logo-sub">Global rankings · Season 2025</div>
        </div>""", unsafe_allow_html=True)

        player_row={
            "name":f"⭐ {st.session_state['name']}",
            "xp":st.session_state["xp"],
            "coins":st.session_state["coins"],
            "trades":st.session_state["trades"],
            "level":get_level(st.session_state["xp"])[1],
        }
        all_rows=LEADERBOARD_DEMO+[player_row]
        all_rows=sorted(all_rows,key=lambda x:x["xp"],reverse=True)

        rk={1:("g","🥇"),2:("s","🥈"),3:("b","🥉")}
        for i,r in enumerate(all_rows,1):
            cls,icon=rk.get(i,(None,f"#{i}"))
            is_me=r["name"].startswith("⭐")
            me_cls=" me" if is_me else ""
            rk_cls=f' class="{cls}"' if cls else ""
            st.markdown(f"""
            <div class="lb-row{me_cls}">
                <div class="lb-rank{' '+cls if cls else ''}">{icon}</div>
                <div class="lb-name">{r['name']}</div>
                <div class="lb-level">{r['level']}</div>
                <div class="lb-coin">🪙 {r['coins']}</div>
                <div class="lb-xp">⚡ {r['xp']}</div>
            </div>""", unsafe_allow_html=True)

    # ── BADGES ────────────────────────────────────────────────────────────────
    elif page=="badges":
        st.markdown("""
        <div class="main-header">
            <div class="logo-text">🎖️ Badges</div>
            <div class="logo-sub">Collect achievements · Prove your mastery</div>
        </div>""", unsafe_allow_html=True)

        earned=len(st.session_state["earned_badges"])
        c1,c2=st.columns(2)
        with c1: st.metric("Earned",f"{earned} / {len(BADGES)}")
        with c2: st.metric("Completion",f"{int(earned/len(BADGES)*100)}%")

        st.markdown("<br>")
        cols=st.columns(4)
        for i,b in enumerate(BADGES):
            is_earned=b["id"] in st.session_state["earned_badges"]
            cls="" if is_earned else "locked"
            with cols[i%4]:
                st.markdown(f"""
                <div class="badge-item {cls}">
                    <div class="icon">{b['icon'] if is_earned else '🔒'}</div>
                    <div class="bname">{b['name']}</div>
                    <div class="bdesc">{b['desc']}</div>
                    {'<div class="unlocked-tag">✓ UNLOCKED</div>' if is_earned else ''}
                </div><br>""", unsafe_allow_html=True)

    # ── PROFESSOR MODE ────────────────────────────────────────────────────────
    elif page=="professor":
        st.markdown("""
        <div class="main-header">
            <div class="logo-text">📡 Professor Mode</div>
            <div class="logo-sub">Launch live challenges to the entire class</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="professor-alert">
            <div class="pa-header">📡 How It Works</div>
            <div class="pa-body">The professor launches a live event from this panel. All students see the challenge appear on their screens simultaneously. Use during class for engagement peaks, debate starters, or competitive moments.</div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec-title">🔴 Live Challenge Templates</div>', unsafe_allow_html=True)

        for ch in PROF_CHALLENGES:
            c1,c2=st.columns([4,1])
            with c1:
                st.markdown(f"""
                <div class="scenario-card">
                    <div class="tag blue">{ch['topic']}</div>
                    <div class="title">{ch['title']}</div>
                    <div class="context">{ch['desc']}</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                if st.button("🚀 Launch", key=f"launch_{ch['title'][:10]}", type="primary"):
                    st.success(f"🔴 LIVE: **{ch['title']}** sent to all students!")
                    st.balloons()

        st.markdown("<br>")
        st.markdown('<div class="sec-title">✏️ Custom Challenge</div>', unsafe_allow_html=True)
        custom_title=st.text_input("Challenge title:", placeholder="e.g. 🚨 CRISIS: SVB Collapse — What do you do?")
        custom_desc=st.text_area("Scenario description:", placeholder="Describe the scenario, context, and what decision students must make...", height=100)
        custom_topic=st.selectbox("Topic:",["NLP in Finance","Fraud Detection","Credit Risk","Algorithmic Trading","Risk Management","Custom"])
        bonus=st.number_input("Bonus XP for first correct answer:", 0, 500, 50, 10)

        if st.button("📡 Broadcast Custom Challenge", type="primary", use_container_width=True):
            if custom_title:
                st.success(f"✅ Challenge **'{custom_title}'** broadcast to all {random.randint(18,28)} connected students! Bonus: +{bonus} XP")
                st.info("💡 Students will see this in their Trading Floor feed. You can award bonus XP manually via the sidebar.")
            else:
                st.warning("Please enter a title first.")
