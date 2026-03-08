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
    {"id":"first_trade", "icon":"🎯","name":"First Trade",        "desc":"Execute your first decision",           "type":"trades","req":1},
    {"id":"trader_5",    "icon":"⚡","name":"Active Trader",      "desc":"Make 5 trading decisions",             "type":"trades","req":5},
    {"id":"trader_20",   "icon":"🔥","name":"High Frequency",     "desc":"Make 20 trading decisions",            "type":"trades","req":20},
    {"id":"trader_40",   "icon":"🚀","name":"Institutional Grade","desc":"Make 40 trading decisions",            "type":"trades","req":40},
    {"id":"winner_3",    "icon":"💰","name":"Three-Peat",         "desc":"Win 3 trades in a row",                "type":"win_streak","req":3},
    {"id":"winner_5",    "icon":"🏆","name":"Unstoppable",        "desc":"Win 5 trades in a row",                "type":"win_streak","req":5},
    {"id":"coins_500",   "icon":"🏦","name":"Half-K Club",        "desc":"Accumulate 500 FinCoins",              "type":"coins","req":500},
    {"id":"coins_1000",  "icon":"💎","name":"FinCoin Millionaire","desc":"Accumulate 1000 FinCoins",             "type":"coins","req":1000},
    {"id":"xp_500",      "icon":"⭐","name":"XP Rocket",          "desc":"Reach 500 XP",                         "type":"xp","req":500},
    {"id":"xp_1000",     "icon":"🌟","name":"XP Superstar",       "desc":"Reach 1000 XP",                        "type":"xp","req":1000},
    # Topic badges — original
    {"id":"fraud_badge", "icon":"🕵️","name":"Fraud Detective",    "desc":"Complete 3 Fraud Detection scenarios",  "type":"topic","req":3,"topic":"Fraud Detection"},
    {"id":"nlp_badge",   "icon":"💬","name":"Text Alpha",         "desc":"Complete 3 NLP in Finance scenarios",   "type":"topic","req":3,"topic":"NLP in Finance"},
    {"id":"risk_badge",  "icon":"📉","name":"Risk Whisperer",     "desc":"Complete 3 Risk Management scenarios",  "type":"topic","req":3,"topic":"Risk Management"},
    {"id":"credit_badge","icon":"📊","name":"Credit Quant",       "desc":"Complete 3 Credit Risk scenarios",      "type":"topic","req":3,"topic":"Credit Risk"},
    {"id":"algo_badge",  "icon":"📈","name":"Algo Trader",        "desc":"Complete 3 Algo Trading scenarios",     "type":"topic","req":3,"topic":"Algorithmic Trading"},
    # Topic badges — new lessons
    {"id":"ai_badge",    "icon":"🧠","name":"AI Strategist",      "desc":"Complete 3 AI Foundations scenarios",   "type":"topic","req":3,"topic":"AI Foundations"},
    {"id":"data_badge",  "icon":"🔧","name":"Data Engineer",      "desc":"Complete 3 Data Engineering scenarios", "type":"topic","req":3,"topic":"Data Engineering"},
    {"id":"pipe_badge",  "icon":"🏗️","name":"Pipeline Architect", "desc":"Complete 3 Data Pipeline scenarios",    "type":"topic","req":3,"topic":"Data Pipeline"},
    {"id":"feat_badge",  "icon":"⚙️","name":"Feature Wizard",     "desc":"Complete 3 Feature Engineering scenarios","type":"topic","req":3,"topic":"Feature Engineering"},
    {"id":"perf_badge",  "icon":"📏","name":"Metrics Master",     "desc":"Complete 3 Model Performance scenarios","type":"topic","req":3,"topic":"Model Performance"},
    {"id":"llm_badge",   "icon":"🤖","name":"Prompt Engineer",    "desc":"Complete 3 Prompt Engineering scenarios","type":"topic","req":3,"topic":"Prompt Engineering"},
    {"id":"ols_badge",   "icon":"📐","name":"OLS Expert",         "desc":"Complete 3 Linear Models scenarios",    "type":"topic","req":3,"topic":"Linear Models & OLS"},
    {"id":"reg_badge",   "icon":"🎯","name":"Regularization Pro", "desc":"Complete 3 Ridge & Lasso scenarios",    "type":"topic","req":3,"topic":"Ridge & Lasso"},
    {"id":"tree_badge",  "icon":"🌳","name":"Tree Surgeon",       "desc":"Complete 3 Decision Tree scenarios",    "type":"topic","req":3,"topic":"Decision Trees"},
    {"id":"ens_badge",   "icon":"🌲","name":"Forest Ranger",      "desc":"Complete 3 Ensemble Models scenarios",  "type":"topic","req":3,"topic":"Ensemble Models"},
    {"id":"svm_badge",   "icon":"⚡","name":"Kernel Hacker",      "desc":"Complete 3 SVM & kNN scenarios",        "type":"topic","req":3,"topic":"SVM & kNN"},
]

SCENARIOS = [
    # ══════════════════════════════════════════════════════
    # LESSON 1 — Introduction to AI in Banking & Finance
    # ══════════════════════════════════════════════════════
    {
        "id":101, "topic":"AI Foundations", "difficulty":"easy",
        "title":"AI vs Rule-Based: Fraud System Upgrade",
        "context": "Your bank uses a 15-year-old rule-based fraud system: 'block if amount > €5,000 AND foreign country'. It blocks 3,800 legitimate transactions/day (false positives). A vendor proposes an ML model (XGBoost, AUC=0.97) trained on 10M transactions. IT says the new system will cost €400k to deploy. The current false-positive rate costs €190k/month in customer service + churn.",
        "asset":"FRAUD SYSTEM", "price":400000, "signal":"UPGRADE",
        "options":["🤖 APPROVE ML upgrade — ROI is clear","📋 KEEP rules — ML is a black box regulators won't like","🔍 PILOT on 10% of traffic first"],
        "correct":2,
        "outcome_win": "Smart call! The 10% pilot confirmed AUC=0.96 in production (slightly below lab) and revealed a timezone data issue. Full rollout then achieved €165k/month savings — ROI in 2.4 months. Piloting before full deployment is best practice for any production ML system.",
        "outcome_loss": "The pilot approach was optimal. In the AI lifecycle (Lesson 1), full deployment without a production test is high risk. The pilot revealed a timezone data alignment bug invisible in the lab — catching it saved a costly rollback.",
        "xp":15, "coins_win":40, "coins_loss":-15,
    },
    {
        "id":102, "topic":"AI Foundations", "difficulty":"medium",
        "title":"The Turing Test in Customer Service",
        "context": "Your bank deployed an LLM-powered chatbot for customer complaints. In an internal test (Turing-style evaluation), 61% of customers could not tell it was AI. Customer satisfaction scores: +18% vs old IVR system. BUT: the chatbot hallucinated a mortgage rate policy (Moffatt v. Air Canada scenario — wrong bereavement policy), and a customer took a financial decision based on the false info. Legal is flagging liability.",
        "asset":"CHATBOT v2.1", "price":0, "signal":"GOVERN",
        "options":["🔒 SHUT DOWN — liability risk too high","📋 ADD human-in-the-loop for financial advice queries","⚡ ADD RAG — ground chatbot in verified policy documents"],
        "correct":2,
        "outcome_win": "Excellent! RAG (Retrieval-Augmented Generation) grounds the LLM in your official policy database. Hallucination rate dropped from 4.2% to 0.3% on financial queries. The chatbot now cites the exact policy document. This is the industry-standard fix for LLM hallucination in regulated environments.",
        "outcome_loss": "RAG was the right answer. Shutting down loses €165k/month in customer savings. Human-in-the-loop alone doesn't scale. RAG fetches verified policy docs at query time, eliminating hallucination on factual questions — the Moffatt v. Air Canada scenario is precisely what RAG prevents.",
        "xp":20, "coins_win":55, "coins_loss":-20,
    },
    {
        "id":103, "topic":"AI Foundations", "difficulty":"hard",
        "title":"AI Act Compliance: High-Risk Classification",
        "context": "Your bank's credit scoring model (used for €2B/year in loan decisions) is under review for EU AI Act compliance. Legal says it qualifies as 'high-risk AI' under Annex III. Requirements include: conformity assessment, human oversight mechanism, post-market monitoring, and logging of all decisions. Your model was built in 2021 — it has no audit logs, no drift monitoring, and no human override UI. Deadline: 6 months. Budget: €800k.",
        "asset":"CREDIT MODEL v4.2", "price":0, "signal":"COMPLY",
        "options":["🔄 REBUILD model from scratch with compliance architecture","🛠️ RETROFIT existing model with logging + oversight UI","⏳ REQUEST extension — compliance is technically infeasible in 6 months"],
        "correct":1,
        "outcome_win": "Correct! Retrofitting is faster and preserves 3 years of production calibration. You added: decision logging (immutable DB), human override UI for borderline cases (0.45–0.55 PD range), drift monitoring (PSI monthly). Compliant in 5.5 months, under budget. Full rebuild would have taken 18 months.",
        "outcome_loss": "Retrofitting was optimal. Rebuilding from scratch loses hard-won calibration and risks 18+ months of delay. Requesting extension signals non-commitment to regulators. The AI Act specifically allows compliance engineering on existing systems — logging + oversight + monitoring achieves all Annex III requirements.",
        "xp":35, "coins_win":90, "coins_loss":-30,
    },

    # ══════════════════════════════════════════════════════
    # LESSON 2 — Python for Financial ML / Data Pipeline
    # ══════════════════════════════════════════════════════
    {
        "id":201, "topic":"Data Engineering", "difficulty":"easy",
        "title":"Survivorship Bias in Backtest",
        "context": "A quant analyst built a strategy backtested on the S&P 500 from 2010–2023. It shows Sharpe=2.1 and annualised return 34%. You notice the backtest used only CURRENT S&P 500 constituents (500 stocks as of 2023). In 2010, the S&P 500 had many companies now delisted, bankrupt, or acquired.",
        "asset":"STRATEGY v1", "price":0, "signal":"INVALID",
        "options":["❌ REJECT — survivorship bias invalidates the backtest","✅ APPROVE — 13 years of data is long enough","🔧 ADD missing companies and re-run"],
        "correct":2,
        "outcome_win": "Correct! Re-running with point-in-time constituent data (including delisted stocks) reduced Sharpe from 2.1 to 0.7. The strategy was selecting survivors — companies that happened to survive to 2023. Survivorship bias is Pitfall #3 from Lesson 3: always use point-in-time datasets.",
        "outcome_loss": "Re-running with full point-in-time data was required. Survivorship bias systematically inflates backtests by 5–10% annually. The strategy's 34% return dropped to 9% after correction. This is one of the most common and costly errors in quantitative finance.",
        "xp":15, "coins_win":40, "coins_loss":-15,
    },
    {
        "id":202, "topic":"Data Engineering", "difficulty":"medium",
        "title":"Look-Ahead Bias: Annual Report Timing",
        "context": "Your fundamental ML model uses Q4 financial statement data (revenue, EBITDA, leverage) to predict next-quarter stock returns. In your data pipeline, you merge Q4 data AS OF December 31. But Q4 annual reports are typically published 60–90 days AFTER year-end (February–March). Your backtest Sharpe = 3.4. A colleague suspects look-ahead bias (Pitfall #2, Lesson 3).",
        "asset":"FUNDAMENTAL MODEL", "price":0, "signal":"FIX",
        "options":["🗓️ APPLY 90-day publication lag before using annual data","✅ KEEP pipeline — markets price in estimates before filing","📊 USE only quarterly data (10-Q) which is available earlier"],
        "correct":0,
        "outcome_win": "Correct! Applying the 90-day publication lag reduced Sharpe from 3.4 to 1.2. The model was using information that wasn't available at decision time. This is classic look-ahead bias — using publication date instead of reference date. Lesson 3 covers this as Pitfall #2.",
        "outcome_loss": "The 90-day lag was essential. Markets do price in estimates, but your MODEL was using actual confirmed figures unavailable at trade time. The 2.2 Sharpe difference is entirely explained by temporal cheating. Always use publication date (SimFin provides 'publish_date') not period-end date.",
        "xp":25, "coins_win":65, "coins_loss":-25,
    },
    {
        "id":203, "topic":"Data Engineering", "difficulty":"hard",
        "title":"Feedback Loop: Reject Inference Problem",
        "context": "Your bank's credit model is trained on historical applicants. Problem: the model itself decided who was approved in the past. You only have outcome labels (default/repay) for APPROVED applicants. The rejected 30% have no labels. Your model retrains monthly on approved applicants only. A risk analyst flags: 'We're training on a biased sample — the model learns only from the applicants it liked.' (Lesson 2, Reality Check 3: Feedback Loops & Reject Inference)",
        "asset":"CREDIT MODEL", "price":0, "signal":"DEBIAS",
        "options":["📊 APPLY reject inference — augment rejected applicants with imputed outcomes","🔄 USE all applicants with conservative bad flag for rejected","📈 INCREASE training data by approving more applicants to get labels"],
        "correct":0,
        "outcome_win": "Excellent! Reject inference (using champion/challenger scoring + domain expertise to impute outcomes for rejectees) reduced the feedback bias. Model KS improved from 38 to 44. You now train on a more representative population — critical for fair lending compliance and SR 11-7 model risk management.",
        "outcome_loss": "Reject inference was the right solution. Simply approving more applicants to get labels creates new risk. Using all applicants with conservative labels introduces label noise. Reject inference — augmenting the rejected segment — is the industry-standard fix described in Lesson 2's Reality Check 3.",
        "xp":35, "coins_win":90, "coins_loss":-30,
    },

    # ══════════════════════════════════════════════════════
    # LESSON 3 — Data Pipeline & Imbalanced Datasets
    # ══════════════════════════════════════════════════════
    {
        "id":301, "topic":"Data Pipeline", "difficulty":"easy",
        "title":"Class Imbalance: 99.9% Accuracy Trap",
        "context": "Your fraud detection model reports 99.9% accuracy on the test set. Your manager is impressed. You dig deeper: fraud rate in the dataset is 0.1% (10,000 frauds in 10M transactions). Confusion matrix: the model predicted 'no fraud' for EVERYTHING. It never flagged a single transaction. (Lesson 3: Metrics for Imbalanced Classification)",
        "asset":"FRAUD MODEL", "price":0, "signal":"FIX",
        "options":["📊 SWITCH metric to PR-AUC and F1 — accuracy is misleading","🔧 APPLY SMOTE + class_weight='balanced'","📋 BOTH: fix metrics AND handle imbalance"],
        "correct":2,
        "outcome_win": "Correct! Fixing BOTH is the right answer. New model: PR-AUC=0.84, F1=0.71, catching 68% of frauds with 12% false positive rate. Accuracy was meaningless at 99.9% — a null model achieves that. Lesson 3 teaches: accuracy is misleading with IR>10; use precision-recall curves instead.",
        "outcome_loss": "Both fixes were needed. Switching metrics alone shows you the problem but doesn't fix it. SMOTE alone doesn't help if you're still measuring the wrong thing. The combination — PR-AUC as metric + SMOTE for rebalancing — is the standard approach for imbalanced fraud datasets.",
        "xp":15, "coins_win":40, "coins_loss":-15,
    },
    {
        "id":302, "topic":"Data Pipeline", "difficulty":"medium",
        "title":"Cost-Sensitive Learning: Default vs Fraud Cost Matrix",
        "context": "Credit approval model. Cost matrix (Lesson 3): Bad loan approved (False Negative) = -€15,000. Good loan rejected (False Positive) = -€200 (opportunity cost). Current model threshold = 0.5, optimising accuracy. A risk model consultant says: 'Your threshold is way too low for this cost asymmetry — you should be much more conservative.'",
        "asset":"CREDIT THRESHOLD", "price":0, "signal":"OPTIMISE",
        "options":["📈 RAISE threshold to 0.91 — cost-optimal per Lesson 5 formula","📉 LOWER threshold — catch more defaults even with more false positives","⏸️ KEEP 0.5 — standard industry practice"],
        "correct":0,
        "outcome_win": "Correct! Optimal threshold formula: τ* = L/(R+L) = 15000/(200+15000) = 0.987. At τ=0.91 (conservative), portfolio expected loss dropped 34% with only 8% approval rate reduction. This is the cost-sensitive threshold optimisation from Lesson 5: default τ=0.5 is never optimal under asymmetric costs.",
        "outcome_loss": "Raising the threshold was correct. The formula from Lesson 5: τ* = C_FN/(C_FN + C_FP) = 15000/15200 ≈ 0.99. At τ=0.5, the model was far too liberal — approving applicants where expected loss >> expected revenue. Financial metrics trump statistical defaults.",
        "xp":25, "coins_win":65, "coins_loss":-25,
    },
    {
        "id":303, "topic":"Data Pipeline", "difficulty":"hard",
        "title":"Frequency Mismatch: Daily vs Quarterly Data Merge",
        "context": "You're building a model that combines: daily stock prices (Yahoo Finance), quarterly earnings (EDGAR), monthly macro data (FRED). A junior analyst merges all three on 'date' with a simple pd.merge(). The result: 95% of rows have NaN quarterly earnings (because earnings are only 4 rows/year). The analyst proposes interpolating quarterly earnings to fill in daily gaps. (Lesson 3, Pitfall #1: Frequency Mismatch)",
        "asset":"MERGED DATASET", "price":0, "signal":"FIX",
        "options":["📅 FORWARD-FILL quarterly data — carry last known value forward","📈 INTERPOLATE — smooth quarterly to daily values","🔄 RESAMPLE all data to quarterly frequency"],
        "correct":0,
        "outcome_win": "Correct! Forward-fill is the only temporally valid approach. Q4 earnings published in March remain unchanged until Q1 earnings — you carry the last known value. Interpolation is look-ahead bias: it uses future quarters to fill today's gaps. This is Lesson 3, Pitfall #1: always forward-fill low-frequency financial data.",
        "outcome_loss": "Forward-fill was essential. Interpolation uses future data — if Q4=100 and Q1=120, interpolating day 45 as 110 is using information not available at day 45. Resampling to quarterly loses 95% of your price data. The only correct approach: forward-fill, preserving point-in-time accuracy.",
        "xp":35, "coins_win":90, "coins_loss":-30,
    },

    # ══════════════════════════════════════════════════════
    # LESSON 4 — Feature Engineering & EDA
    # ══════════════════════════════════════════════════════
    {
        "id":401, "topic":"Feature Engineering", "difficulty":"easy",
        "title":"Altman Z-Score: Distress Signal",
        "context": "You are a credit analyst at a PE fund. Target company XYZ Corp financials: Working Capital/TA = 0.08, Retained Earnings/TA = 0.04, EBIT/TA = 0.03, Market Cap/Total Debt = 0.45, Revenue/TA = 0.62. Altman Z = 1.2(0.08) + 1.4(0.04) + 3.3(0.03) + 0.6(0.45) + 1.0(0.62) = 0.096 + 0.056 + 0.099 + 0.27 + 0.62 = 1.14. Z < 1.81 = distress zone.",
        "asset":"XYZ CORP", "price":0, "signal":"DISTRESS",
        "options":["🚨 FLAG as high credit risk — Z=1.14 is in distress zone","✅ APPROVE credit — Z-score is outdated (1968 model)","📊 REQUEST updated financials + DCF before deciding"],
        "correct":2,
        "outcome_win": "Excellent judgment! Altman Z is a powerful screening signal (Lesson 4: Classic Composite Scores) but not a substitute for full due diligence. Updated financials revealed Q3 improvement: Z rose to 1.95 (grey zone). DCF showed positive free cash flow. Credit approved at higher spread — the Z-score correctly triggered the review.",
        "outcome_loss": "Requesting updated data was optimal. Altman Z (1968) is a powerful screen — Z=1.14 is a serious red flag warranting investigation. But automated rejection based solely on a single composite score misses current context. The Z-score is a feature, not the final decision. Always combine with forward-looking analysis.",
        "xp":15, "coins_win":40, "coins_loss":-15,
    },
    {
        "id":402, "topic":"Feature Engineering", "difficulty":"medium",
        "title":"Target Encoding Leakage in Credit Scoring",
        "context": "A data scientist encodes 'loan_purpose' (categorical: mortgage, car, personal, business) using target encoding: for each category, she computes mean(default_rate) across the ENTIRE training+test dataset, then maps each loan to its category's mean. The model AUC jumps from 0.76 to 0.89. You review the code and see the issue (Lesson 3/4: Target Encoding Leakage).",
        "asset":"ENCODING PIPELINE", "price":0, "signal":"FIX",
        "options":["🔧 RE-ENCODE using training fold only (out-of-fold encoding)","✅ KEEP — AUC improvement is real, model is better","📋 SWITCH to one-hot encoding to avoid the problem entirely"],
        "correct":0,
        "outcome_win": "Correct! Out-of-fold target encoding recomputed properly: each fold's encoding uses only training rows. AUC dropped to 0.79 — the 0.89 was entirely fake signal from data leakage. The model was using the test set's default rates to encode the test features. Lesson 4 calls this 'Naive Target Encoding (Leakage!)'.",
        "outcome_loss": "Out-of-fold encoding was essential. The AUC 0.89 was pure data leakage — the model already 'knew' each loan's group default rate because it was computed on the full dataset including the test set. In production, this model performs at 0.77. Lesson 3 explicitly shows the wrong/right way to do target encoding.",
        "xp":25, "coins_win":65, "coins_loss":-25,
    },
    {
        "id":403, "topic":"Feature Engineering", "difficulty":"hard",
        "title":"Log Returns, Stationarity & ADF Test",
        "context": "You're building an ML model to predict next-day S&P 500 returns. A colleague uses raw prices (SPY closing price) as a feature. ADF test on SPY prices: p-value = 0.94 (non-stationary, unit root). ADF test on log-returns: p-value = 0.0001 (stationary). The model trained on raw prices shows out-of-sample R² = -0.12 (worse than predicting the mean). The colleague argues: 'Prices contain more information than returns.'",
        "asset":"SPY FEATURE", "price":0, "signal":"TRANSFORM",
        "options":["📈 SWITCH to log returns — stationarity is required for ML","⚡ USE both prices AND returns — let the model decide","🔧 DIFFERENCE the prices (Δprice) — same information, simpler"],
        "correct":0,
        "outcome_win": "Correct! Log returns are the foundation of financial ML (Lesson 2 & 4). ADF confirms non-stationarity of prices (unit root: p=0.94). ML models trained on I(1) processes memorise the trend, not the signal. Switching to log returns: R² improved to +0.03 (small but statistically significant). Stationarity is non-negotiable.",
        "outcome_loss": "Log returns were the right choice. Raw prices are I(1) — random walks with unit roots. ML models trained on them learn spurious relationships between price levels, not returns. Log returns are approximately stationary I(0), time-additive, and approximately normally distributed. This is covered in depth in Lessons 2 and 4.",
        "xp":35, "coins_win":90, "coins_loss":-30,
    },

    # ══════════════════════════════════════════════════════
    # LESSON 5 — Model Performance & Financial Metrics
    # ══════════════════════════════════════════════════════
    {
        "id":501, "topic":"Model Performance", "difficulty":"easy",
        "title":"ROC vs PR-AUC: Which Metric for Fraud?",
        "context": "Your fraud detection model reports ROC-AUC = 0.95. The team is celebrating. You check the PR-AUC: 0.31. Fraud rate in your data: 0.08% (very rare). ROC-AUC looks great because TN >> TP (most transactions are legitimate). A correct model that identifies 0 frauds still gets ROC-AUC ≈ 0.95 just from the huge TN denominator. (Lesson 5: Limitations of ROC in Imbalanced Data)",
        "asset":"FRAUD MODEL METRICS", "price":0, "signal":"PR-AUC",
        "options":["📊 REPORT PR-AUC as primary metric — ROC is misleading here","✅ KEEP ROC-AUC — it's the industry standard","📋 REPORT BOTH with clear explanation to the board"],
        "correct":2,
        "outcome_win": "Correct! Reporting both with clear context is best practice. Board presentation: 'ROC-AUC=0.95 measures ranking; PR-AUC=0.31 measures precision at the fraud prevalence level we care about. Our target is PR-AUC > 0.60.' This is exactly the nuance Lesson 5 teaches: different metrics answer different questions.",
        "outcome_loss": "Reporting both was the gold standard. PR-AUC=0.31 is actually the critical number here — at 0.08% fraud rate, ROC-AUC is inflated by the massive true negative count. But abandoning ROC-AUC entirely loses comparability with industry benchmarks. Report both, explain what each measures.",
        "xp":15, "coins_win":40, "coins_loss":-15,
    },
    {
        "id":502, "topic":"Model Performance", "difficulty":"medium",
        "title":"K-Fold CV on Time Series: The Classic Mistake",
        "context": "A quant uses standard 5-fold cross-validation to evaluate a trading signal model. In fold 3, training data includes 2023 data and test data includes 2019 data. The CV score is Sharpe=2.8. You recognise this as look-ahead bias in model evaluation (Lesson 5: Cross-Validation; Lesson 9: TimeSeriesSplit). The colleague says: 'k-fold is unbiased by construction.'",
        "asset":"CV METHODOLOGY", "price":0, "signal":"FIX",
        "options":["🕐 SWITCH to TimeSeriesSplit (walk-forward CV)","✅ KEEP k-fold — shuffling breaks autocorrelation artificially","📈 USE nested cross-validation — more robust"],
        "correct":0,
        "outcome_win": "Correct! TimeSeriesSplit enforces temporal ordering: training always precedes test. After correction, Sharpe dropped from 2.8 to 0.6 — the entire performance was look-ahead bias. K-fold random shuffling allows models to 'see the future' when autocorrelation is present. Lesson 5 and 9 both cover this as a critical pitfall.",
        "outcome_loss": "TimeSeriesSplit was the right fix. Standard k-fold violates the sequential nature of time series. In fold 3, the model trained on 2023 data to predict 2019 — it knew the market's future. Sharpe fell from 2.8 to 0.6 after correction. Walk-forward validation is the only valid evaluation for any financial time series model.",
        "xp":25, "coins_win":65, "coins_loss":-25,
    },
    {
        "id":503, "topic":"Model Performance", "difficulty":"hard",
        "title":"Calibration vs Discrimination: AUC ≠ Probabilities",
        "context": "Your credit model has AUC=0.85 (excellent discrimination). You deploy it for IFRS 9 provisions, which require well-calibrated PD estimates. Calibration plot shows: when the model outputs PD=0.10, actual default rate = 0.24. At PD=0.30, actual rate = 0.54. The model ranks applicants correctly (high AUC) but systematically underestimates default probabilities. (Lesson 2: Stage 6 Calibration; Lesson 5: Why AUC is not enough)",
        "asset":"PD MODEL CALIBRATION", "price":0, "signal":"CALIBRATE",
        "options":["📐 APPLY Platt scaling or isotonic regression to recalibrate","✅ KEEP — AUC=0.85 means discrimination is excellent","🔄 RETRAIN model from scratch — calibration cannot be fixed post-hoc"],
        "correct":0,
        "outcome_win": "Correct! Platt scaling (logistic regression on model outputs) recalibrated PDs: at model output 0.10, new PD = 0.22 (vs actual 0.24 — much better). IFRS 9 ECL calculations are now accurate. AUC remained 0.85 — calibration doesn't change discrimination. This is the key insight from Lesson 2's calibration section.",
        "outcome_loss": "Platt scaling was correct. AUC measures ranking only, not probability accuracy. A model can rank perfectly (AUC=1.0) but output systematically wrong probabilities. Retraining from scratch is wasteful when post-hoc calibration achieves the same result. IFRS 9 requires calibrated PDs — discrimination alone is insufficient.",
        "xp":35, "coins_win":90, "coins_loss":-30,
    },

    # ══════════════════════════════════════════════════════
    # LESSON 6 — Prompt Engineering & LLMs
    # ══════════════════════════════════════════════════════
    {
        "id":601, "topic":"Prompt Engineering", "difficulty":"easy",
        "title":"Zero-Shot vs Chain-of-Thought: CET1 Calculation",
        "context": "You need an LLM to check CET1 compliance. Zero-shot prompt: 'Does this bank meet capital requirements? CET1=€45B, RWA=€350B.' The model answers: 'Yes, the bank appears to be adequately capitalised.' No calculation shown, no threshold cited. You apply Chain-of-Thought (Lesson 6): 'Calculate CET1 ratio. Think step by step. Compare to Basel III 10.5% minimum.'",
        "asset":"CET1 ANALYSIS", "price":0, "signal":"COT",
        "options":["🧠 USE Chain-of-Thought — shows reasoning and is auditable","✅ KEEP zero-shot — faster and the answer is the same","📋 USE tabular CoT — each step documented for regulatory audit"],
        "correct":2,
        "outcome_win": "Excellent! Tabular CoT for regulatory calculations: Step 1: CET1 ratio = 45/350 = 12.86%. Step 2: Minimum requirement = 10.5% (Basel III Pillar 1 + conservation buffer). Step 3: Buffer = 12.86 - 10.5 = 2.36%. Step 4: PASS ✅. This audit trail is exactly what regulators require under SR 11-7. Zero-shot gave a vague answer — unacceptable in a regulated context.",
        "outcome_loss": "Tabular CoT was the gold standard. Zero-shot might get the answer right or wrong — you can't tell because no reasoning is shown. Regulators require documented calculation steps (SR 11-7, AI Act). Regular CoT works, but tabular CoT structures each step for easy audit. Lesson 6 covers all three prompting styles.",
        "xp":15, "coins_win":40, "coins_loss":-15,
    },
    {
        "id":602, "topic":"Prompt Engineering", "difficulty":"medium",
        "title":"RAG vs Hallucination: Basel IV Compliance",
        "context": "Your compliance team uses an LLM to answer internal queries about Basel IV capital requirements. Without RAG, the model answers: 'Under Basel IV, the output floor is 72.5% of standardised RWA.' This is correct BUT it is training-data knowledge that could be outdated. A new EBA circular amended the implementation timeline. The model confidently gives the old timeline (hallucination risk + outdatedness). (Lesson 6: RAG)",
        "asset":"COMPLIANCE LLM", "price":0, "signal":"RAG",
        "options":["🔍 IMPLEMENT RAG — connect to your regulatory document database","✅ KEEP — model knows Basel IV thoroughly from training","📅 ADD system prompt: 'Always caveat that information may be outdated'"],
        "correct":0,
        "outcome_win": "Correct! RAG implementation: semantic search retrieves the latest EBA circular (published 3 months ago), injects it into context, and the model answers with the updated timeline + cites the exact document. The caveat approach (option 3) doesn't prevent wrong answers — it just disclaims them. RAG prevents hallucinations on verifiable facts.",
        "outcome_loss": "RAG was the right solution. Adding a caveat doesn't prevent the model from giving a wrong answer — it just adds a disclaimer. Training knowledge becomes stale. RAG (Retrieval-Augmented Generation, Lesson 6) fetches verified current documents at query time, solving both hallucination and staleness simultaneously.",
        "xp":25, "coins_win":65, "coins_loss":-25,
    },
    {
        "id":603, "topic":"Prompt Engineering", "difficulty":"hard",
        "title":"Tree of Thoughts: Multi-Expert M&A Analysis",
        "context": "You need an LLM to evaluate whether a bank should acquire a fintech for €800M. Standard prompt returns a generic one-dimensional analysis. You apply Tree of Thoughts (Lesson 6): 'Imagine three experts — a risk manager, a CFO, and a compliance officer — each evaluating this acquisition. Each writes one step, then shares. If an expert finds a fatal flaw, they exit.' The ToT prompt reveals: risk manager flags credit model integration risk, CFO flags overpayment (P/S multiple 8x vs peers 4x), compliance flags GDPR data transfer issues.",
        "asset":"FINTECH ACQUISITION", "price":800e6, "signal":"TOT",
        "options":["📊 USE ToT output — three independent expert views before deciding","✅ PROCEED with acquisition — ToT is over-engineering","🔍 ESCALATE to human M&A committee with ToT analysis as input"],
        "correct":2,
        "outcome_win": "Perfect judgment! The ToT output is input for human decision-makers, not a replacement. You escalated to the M&A committee with the structured analysis. They negotiated price down to €620M (addressing CFO's overpayment concern) and added regulatory pre-clearance conditions. The GDPR issue was mitigated contractually. €180M saved.",
        "outcome_loss": "Escalation to the human committee was correct. ToT is a multi-perspective analysis tool (Lesson 6), not a final decision engine. For an €800M acquisition, LLM analysis is high-quality input that surfaces blind spots — but the final decision requires human judgment, fiduciary responsibility, and regulatory accountability.",
        "xp":35, "coins_win":90, "coins_loss":-30,
    },

    # ══════════════════════════════════════════════════════
    # LESSON 7 — Linear Models & OLS / Asset Pricing
    # ══════════════════════════════════════════════════════
    {
        "id":701, "topic":"Linear Models & OLS", "difficulty":"easy",
        "title":"CAPM Beta: Defensive or Aggressive?",
        "context": "You run a CAPM regression (Lesson 7) for two stocks: Stock A: Rᵢ - Rf = α + β(Rm - Rf). Results: Stock A β=1.45, α=0.002 (not significant). Stock B β=0.38, α=0.001 (not significant). Your client is a pension fund with a liability-matching mandate (needs stable, predictable returns). Which stock fits their mandate?",
        "asset":"PENSION PORTFOLIO", "price":0, "signal":"BETA",
        "options":["📉 STOCK B (β=0.38) — defensive, dampens market movements","📈 STOCK A (β=1.45) — higher expected return for pension","⚖️ MIX both 50/50 — portfolio beta = 0.92"],
        "correct":0,
        "outcome_win": "Correct! β=0.38 is a defensive stock — when the market falls 10%, it falls only 3.8%. Pension funds have stable liabilities: they need assets that don't collapse during drawdowns. β=1.45 amplifies market moves — great for aggressive growth, wrong for liability-matching. Alpha is insignificant in both cases (CAPM holds).",
        "outcome_loss": "Stock B (β=0.38) was the right choice. Lesson 7 covers CAPM interpretation: β<1 are defensive stocks that dampen market moves — ideal for liability-matching mandates. Pension funds' priority is avoiding large drawdowns that could breach solvency capital requirements, not maximising expected return.",
        "xp":15, "coins_win":40, "coins_loss":-15,
    },
    {
        "id":702, "topic":"Linear Models & OLS", "difficulty":"medium",
        "title":"Multicollinearity in Credit Scoring Model",
        "context": "Your logistic regression credit model has 8 features. VIF analysis (Lesson 7): debt_to_income VIF=12.4, loan_to_income VIF=11.8, payment_to_income VIF=13.2. These three are highly collinear (all measure leverage). The model's coefficients are unstable across bootstrap samples. One bootstrap shows debt_to_income coefficient = +2.3, another shows -1.8. (Lesson 7: VIF > 10 = severe multicollinearity)",
        "asset":"SCORING MODEL", "price":0, "signal":"FIX-VIF",
        "options":["🔧 DROP two leverage features — keep only DTI (most interpretable)","📐 APPLY Ridge regression — shrinks collinear coefficients","🔄 CREATE composite feature: average_leverage_ratio"],
        "correct":1,
        "outcome_win": "Excellent! Ridge regression (Lesson 9) is exactly the right tool for multicollinearity. It shrinks all three collinear coefficients toward zero smoothly without dropping information. Coefficient stability improved: bootstrap std dropped from ±2.1 to ±0.3. AUC: 0.79 → 0.81. Ridge doesn't require manual feature selection when multicollinearity is the issue.",
        "outcome_loss": "Ridge regression was optimal. Dropping features loses information — DTI, LTI, and PTI capture slightly different leverage dimensions. A composite feature requires domain justification. Ridge (L2 penalty) handles multicollinearity by distributing importance across correlated features, exactly addressing the VIF>10 problem from Lesson 7.",
        "xp":25, "coins_win":65, "coins_loss":-25,
    },
    {
        "id":703, "topic":"Linear Models & OLS", "difficulty":"hard",
        "title":"Fama-French 5-Factor: Decompose ETF Returns",
        "context": "You run a Fama-French 5-factor regression (Lesson 7) on a 'sustainable growth' ETF: α=0.0008 (not significant), βMKT=0.92, βSMB=-0.31 (negative = large-cap tilt), βHML=-0.28 (negative = growth tilt), βRMW=+0.45 (positive = profitable firms), βCMA=-0.38 (negative = aggressive investment). The ETF charges 0.85% annual fee and claims to offer 'alpha through ESG screening'.",
        "asset":"ESG ETF", "price":0, "signal":"ANALYSE",
        "options":["❌ REJECT — no alpha (α not significant), factor exposures explain all returns","✅ BUY — RMW+0.45 shows quality tilt that adds value","📊 CHALLENGE fee — same exposure achievable with cheaper factor ETFs"],
        "correct":2,
        "outcome_win": "Brilliant analysis! The factor regression shows the ETF's 'alpha' is entirely explained by known factors (quality: RMW+0.45, growth: HML-0.28). You can replicate this exposure with: QMJ ETF (0.25% fee) + MTUM ETF (0.15% fee) = 0.40% vs 0.85%. Challenging the fee is the correct institutional response to a Fama-French decomposition showing zero true alpha.",
        "outcome_loss": "Fee challenge was the optimal response. The 5-factor decomposition shows every unit of return is explained by priced factors. α=0.0008 (p>0.05) means zero skill. The 0.85% fee vs 0.40% for equivalent factor exposure is a 0.45% annual drag. Lesson 7's asset pricing section teaches factor models to decompose 'active' fund returns.",
        "xp":35, "coins_win":90, "coins_loss":-30,
    },

    # ══════════════════════════════════════════════════════
    # LESSON 9 — Ridge, Lasso & Regularization
    # ══════════════════════════════════════════════════════
    {
        "id":901, "topic":"Ridge & Lasso", "difficulty":"easy",
        "title":"Ridge vs Lasso: 150 Macro Factors",
        "context": "You're building a model to predict corporate bond spreads using 150 macro/financial variables. You expect MOST variables to contribute a small effect (macro variables all move together). Lasso solution: zeroes out 138 variables, keeps 12. Ridge solution: keeps all 150 with small coefficients. Your economic prior: spreads are driven by many small effects, not a few dominant ones. (Lesson 9: When to use Ridge vs Lasso)",
        "asset":"SPREAD MODEL", "price":0, "signal":"CHOOSE",
        "options":["📐 USE Ridge — prior is diffuse signal across many variables","✂️ USE Lasso — 12 variables is more interpretable","⚡ USE ElasticNet — balance sparsity and stability"],
        "correct":0,
        "outcome_win": "Correct! Ridge is optimal when signals are diffuse (many small effects). Lasso's aggressiveness is wrong here — it arbitrarily selects 12 from 150 correlated macro factors, discarding real signal. Lesson 9: 'Ridge is suitable when you expect many variables to matter a little (diffuse signals), for example macro + micro factors that all contribute small effects.'",
        "outcome_loss": "Ridge was the right answer. When you expect many small contributing factors (your economic prior for macro variables), Lasso's sparsity is harmful — it throws away real signal from correlated variables. Ridge shrinks all coefficients, preserving all signals. Lesson 9 is explicit: match the penalty to your prior about the data-generating process.",
        "xp":15, "coins_win":40, "coins_loss":-15,
    },
    {
        "id":902, "topic":"Ridge & Lasso", "difficulty":"medium",
        "title":"Lambda Tuning: Bias-Variance Tradeoff",
        "context": "Your Lasso credit model is tuned with CV. You test λ values from 0.001 to 100. Results: λ=0.001 (OLS-like): train R²=0.91, test R²=0.43 (overfitting). λ=100: train R²=0.31, test R²=0.29 (underfitting). λ=0.8 (CV-optimal): train R²=0.74, test R²=0.71. A manager insists: 'The higher the R², the better — use λ=0.001.' (Lesson 9: Role of λ, Bias-Variance Tradeoff)",
        "asset":"LASSO λ", "price":0, "signal":"λ=0.8",
        "options":["📐 USE λ=0.8 — CV-optimal balances bias and variance","📈 USE λ=0.001 — highest training R² means best model","📊 USE λ=100 — most regularized = most robust"],
        "correct":0,
        "outcome_win": "Correct! CV-optimal λ=0.8 achieves the best generalization. The manager's logic is wrong: λ=0.001 overfits (train R²=0.91 vs test R²=0.43 — a 0.48 gap). λ=0.8 closes the gap to 0.03. Lesson 9: 'λ=0 corresponds to OLS: minimum training error but risk of overfitting.' In production, the test R² is all that matters.",
        "outcome_loss": "λ=0.8 was correct. High training R² without corresponding test R² is pure overfitting — the model memorizes training data, not patterns. The 0.48 train-test gap at λ=0.001 is a textbook overfit. Cross-validation exists precisely to find the λ that generalizes. Lesson 9: increasing λ reduces variance at the cost of bias — find the sweet spot.",
        "xp":25, "coins_win":65, "coins_loss":-25,
    },
    {
        "id":903, "topic":"Ridge & Lasso", "difficulty":"hard",
        "title":"Factor Zoo: p > n Problem with Lasso",
        "context": "You're testing 150 equity factors (p=150) to predict cross-sectional returns. Problem: you only have 120 monthly observations (n=120). OLS is undefined (p>n). Lasso selects 18 factors with non-zero coefficients, Sharpe=1.8. But a colleague warns: with 150 factors and 120 observations, multiple testing inflates your Sharpe. He cites Harvey et al. (2016): a factor needs t-stat > 3.0 (not 1.96) to survive multiple testing. Your 18 factors: 7 have t-stat > 3.0, 11 have t-stat between 1.5–3.0. (Lesson 9, Case Study 2: Factor Zoo)",
        "asset":"FACTOR MODEL", "price":0, "signal":"PRUNE",
        "options":["✂️ PRUNE to 7 factors with t-stat > 3.0 — multiple testing adjustment","📈 KEEP all 18 — Lasso already handles selection","🔄 RE-RUN with more data (extend to daily, n=2600)"],
        "correct":2,
        "outcome_win": "Brilliant! Extending to daily data (n=2600) resolves both problems: p<n is satisfied, t-stats stabilize, and you can apply proper multiple testing correction. With daily data, 9 factors survive t>3.0 with stable Sharpe=1.4 (lower but robust). Lesson 9's Factor Zoo case study teaches exactly this: data scarcity drives spurious factor discovery.",
        "outcome_loss": "Extending to daily data was optimal. Pruning to 7 factors throws away factors that might be real — the 11 moderate-t-stat factors may simply need more data to confirm. Lesson 9 covers this: in the Factor Zoo setting, more data > more aggressive selection. Lasso addresses p>n but not the multiple testing problem, which requires either Bonferroni correction or more observations.",
        "xp":35, "coins_win":90, "coins_loss":-30,
    },

    # ══════════════════════════════════════════════════════
    # LESSON 10 — Decision Trees in Banking
    # ══════════════════════════════════════════════════════
    {
        "id":1001, "topic":"Decision Trees", "difficulty":"easy",
        "title":"Gini Impurity: Credit Score Split",
        "context": "You're building a decision tree for credit approval. At the root node: 1,000 applicants, 700 no-default, 300 default. Gini(parent) = 1 - 0.70² - 0.30² = 0.42. You evaluate a split on credit score < 650 vs >= 650. Left node (score<650): 400 applicants, 100 no-default, 300 default. Right node (score>=650): 600 applicants, 600 no-default, 0 default. Weighted Gini after split: (400/1000)(0.375) + (600/1000)(0) = 0.15. Information gain = 0.42 - 0.15 = 0.27. (Lesson 10: Gini Impurity example)",
        "asset":"CREDIT TREE SPLIT", "price":0, "signal":"SPLIT",
        "options":["✅ USE this split — high information gain (0.27) on credit score","🔍 TEST other splits — maybe DTI ratio does better","📋 USE entropy instead of Gini — more theoretically sound"],
        "correct":1,
        "outcome_win": "Correct judgment! Testing other splits is best practice — you never commit to the first good split without exploring alternatives. DTI ratio split achieved IG=0.31 > 0.27. The tree chooses DTI as the root node. Lesson 10: decision trees evaluate ALL possible splits at each node; credit score at 650 was good, but not optimal.",
        "outcome_loss": "Testing other splits was correct. A Gini IG of 0.27 is good, but the algorithm evaluates all possible splits at all possible thresholds. DTI achieved IG=0.31. Decision trees are greedy algorithms — they don't commit until all splits are evaluated. Gini vs entropy rarely matters in practice (Lesson 10 covers both).",
        "xp":15, "coins_win":40, "coins_loss":-15,
    },
    {
        "id":1002, "topic":"Decision Trees", "difficulty":"medium",
        "title":"Regulatory Overfitting: 2008 Parallel",
        "context": "Your bank's credit decision tree was trained on 2018–2022 data (stable economic environment). max_depth=None (fully grown). AUC=0.94 in-sample, AUC=0.71 out-of-sample. In early 2023 (rate shock environment), the model starts approving risky borrowers (false negatives increase 280%). The tree memorized 2018–2022 patterns that are now invalid. The ECB stresses this mirrors pre-2008 credit models. (Lesson 10: Overfitting & Regulatory Implications)",
        "asset":"CREDIT TREE 2022", "price":0, "signal":"PRUNE",
        "options":["✂️ PRUNE: set max_depth=5, min_samples_leaf=50 — reduce complexity","🔄 RETRAIN on 2021–2023 data including rate shock","📋 BOTH: prune AND retrain on data including the new regime"],
        "correct":2,
        "outcome_win": "Correct! Both interventions together: retraining on 2021–2023 (including rate shocks) and pruning (max_depth=5) achieved AUC=0.83 out-of-sample in 2023 conditions. Pruning alone on old data still learns wrong patterns. New data alone with a deep tree re-overfits to 2023. Lesson 10: pruning + regime-inclusive training is the right combination.",
        "outcome_loss": "Both fixes together were optimal. Lesson 10 explicitly covers this: 'A deeply-grown tree memorizes historical loan data, including market anomalies. During economic downturns, the model fails on new patterns.' Pruning controls complexity; retraining on new regime data provides the right patterns to learn. Either alone is insufficient.",
        "xp":25, "coins_win":65, "coins_loss":-25,
    },
    {
        "id":1003, "topic":"Decision Trees", "difficulty":"hard",
        "title":"Decision Tree vs Logistic Regression: GDPR",
        "context": "Your bank must decide between two credit models for retail loans: Model A (Decision Tree, max_depth=6): AUC=0.81, easily visualised as rules ('if credit_score < 650 AND DTI > 0.45 → decline'). Model B (XGBoost, 500 trees): AUC=0.87, requires SHAP for explanation. Both are deployed under GDPR Article 22: customers have the right to a meaningful explanation of automated decisions. Legal says XGBoost SHAP explanations are 'technically accurate but incomprehensible to average customers.' (Lesson 10: Decision Tree vs Logistic Regression; Lesson 2: GDPR)",
        "asset":"RETAIL CREDIT MODEL", "price":0, "signal":"CHOOSE",
        "options":["🌳 CHOOSE Decision Tree — rule-based, human-interpretable, GDPR-safe","🤖 CHOOSE XGBoost — 6 AUC points of performance is worth it","📋 DEPLOY XGBoost with simplified rule extraction for GDPR explanations"],
        "correct":2,
        "outcome_win": "Excellent! The hybrid approach: XGBoost in production (AUC=0.87), plus a Decision Tree 'explanation surrogate' trained to mimic its decisions, generating customer-facing rules. Legal approved: explanations are simple rules derived from a tree trained on XGBoost outputs. Regulators accepted the methodology. Performance + compliance achieved simultaneously.",
        "outcome_loss": "The hybrid approach was the professional solution. GDPR doesn't require the model to BE interpretable — it requires the EXPLANATION to be comprehensible. Deploying a surrogate explainer (simple tree mirroring XGBoost) satisfies Article 22 while preserving the 6 AUC-point advantage. Lesson 10 frames the Decision Tree vs XGBoost tradeoff exactly in these terms.",
        "xp":35, "coins_win":90, "coins_loss":-30,
    },

    # ══════════════════════════════════════════════════════
    # LESSON 11 — Random Forest & Ensemble Models
    # ══════════════════════════════════════════════════════
    {
        "id":1101, "topic":"Ensemble Models", "difficulty":"easy",
        "title":"Random Forest vs Single Tree: Stability",
        "context": "Two models for predicting loan default: Model A (Single Decision Tree, max_depth=8): AUC=0.79, but when you run it on 10 different 80/20 splits, AUC varies from 0.61 to 0.89 (high variance). Model B (Random Forest, 200 trees): AUC=0.84, AUC variation across splits: 0.81–0.87 (stable). Both trained on same data. A risk manager prefers Model A because 'it's simpler and easier to explain to the audit committee.' (Lesson 11: From Tree to Forest)",
        "asset":"DEFAULT MODEL", "price":0, "signal":"RF",
        "options":["🌲 CHOOSE Random Forest — stability is critical in production credit models","🌳 CHOOSE Single Tree — interpretability > 5 AUC points","📋 RUN both in parallel — use RF for decisions, tree for explanations"],
        "correct":2,
        "outcome_win": "Smart solution! RF in production (AUC=0.84, stable), decision tree as SHAP-proxy for audit explanations. Risk managers see clear rules; quants trust the RF's stability. Lesson 11: RF reduces variance by aggregating 200 independent trees — the high variance of a single tree (0.61–0.89) makes it unsuitable for production credit systems.",
        "outcome_loss": "Running both in parallel was optimal. You need RF's stability (AUC variance 0.81–0.87 vs 0.61–0.89) for safe production deployment, but the audit committee legitimately needs interpretability. Lesson 11 teaches the stability advantage of ensemble methods — high variance in a single tree is directly equivalent to operational risk in a production credit model.",
        "xp":15, "coins_win":40, "coins_loss":-15,
    },
    {
        "id":1102, "topic":"Ensemble Models", "difficulty":"medium",
        "title":"Gradient Boosting: Learning Rate Tuning",
        "context": "You're comparing XGBoost configurations for a fraud model. Config A: learning_rate=0.3, n_estimators=100 → AUC=0.91, training time 2 min. Config B: learning_rate=0.01, n_estimators=1000 → AUC=0.94, training time 22 min. Config C: learning_rate=0.01, n_estimators=200 (early stopped) → AUC=0.91, training time 4 min. Lesson 11: 'Learning rate controls each tree's contribution; number of trees is a trade-off between accuracy and overfitting.' Production requires daily retraining on 50M transactions.",
        "asset":"XGBOOST CONFIG", "price":0, "signal":"OPTIMISE",
        "options":["⚡ CONFIG C — early stopping captures 97% of B's performance at 18% of training time","📈 CONFIG B — best AUC is always worth it","🔧 CONFIG A — simplest, fastest, acceptable AUC"],
        "correct":0,
        "outcome_win": "Correct! Config C with early stopping is the professional choice for daily production retraining. 22 min daily training (Config B) vs 4 min (Config C) matters at scale. The 0.03 AUC difference between B and C is operationally insignificant for fraud. Lesson 11: 'Critical parameters: learning rate controls contribution; number of trees = trade-off between accuracy and overfitting' — early stopping finds that trade-off automatically.",
        "outcome_loss": "Config C was optimal. The 0.03 AUC gain from Config B costs 18 additional minutes of daily retraining. At 50M transactions/day, time-to-deploy matters more than marginal AUC. Early stopping (Lesson 11's best practice) finds the point where additional trees stop adding value — giving Config B's quality at Config A's training budget.",
        "xp":25, "coins_win":65, "coins_loss":-25,
    },
    {
        "id":1103, "topic":"Ensemble Models", "difficulty":"hard",
        "title":"McNemar Test: Model Comparison Statistical Significance",
        "context": "You compare Random Forest (AUC=0.847) vs XGBoost (AUC=0.861) on 10,000 test loans. McNemar test (Lesson 11, Statistical Tests for Model Comparison): RF correct, XGBoost wrong = 312 cases. RF wrong, XGBoost correct = 498 cases. McNemar statistic = (312-498)²/(312+498) = 42.7, p<0.0001. The CFO says: '0.014 AUC difference is trivial — keep the simpler RF.'",
        "asset":"MODEL SELECTION", "price":0, "signal":"XGBOOST",
        "options":["📊 DEPLOY XGBoost — McNemar confirms statistically significant difference","🌲 KEEP Random Forest — 0.014 AUC is practically insignificant","📋 TRANSLATE to financial impact — statistical ≠ economic significance"],
        "correct":2,
        "outcome_win": "Excellent! Translating to financial impact: 186 additional correct predictions (498-312) on 10,000 loans. If each correct detection saves €5,000 average, that's €930k/year. McNemar says the difference is REAL (not random), and the financial translation says it MATTERS. This is Lesson 11's key insight: statistical significance + economic significance must both be confirmed.",
        "outcome_loss": "Translating to financial impact was the right final step. McNemar (Lesson 11) tells you the difference is statistically real — not by chance. But the CFO's question is valid: does 0.014 AUC matter in euros? The answer: 186 additional correct decisions × €5k average = €930k/year. Both statistical and financial significance confirmed — deploy XGBoost.",
        "xp":35, "coins_win":90, "coins_loss":-30,
    },

    # ══════════════════════════════════════════════════════
    # LESSON 12 — SVM & kNN in Finance
    # ══════════════════════════════════════════════════════
    {
        "id":1201, "topic":"SVM & kNN", "difficulty":"easy",
        "title":"kNN Peer Groups: Scaling Problem",
        "context": "You're building a peer group model for M&A comparables (Lesson 12). Features: Revenue (€50M–€5,000M), EBITDA margin (5%–35%), Net Debt/EBITDA (0.5–8.0), Market cap (€100M–€50,000M). Without scaling, kNN identifies peers based mainly on revenue (huge scale dominates distance). A €500M revenue company is matched to €520M revenue peers regardless of very different margins and leverage. (Lesson 12: The Scaling Problem)",
        "asset":"M&A COMPARABLES", "price":0, "signal":"SCALE",
        "options":["📐 APPLY StandardScaler before kNN — z-score all features","📏 APPLY MinMaxScaler — preserve relative relationships","⚡ APPLY StandardScaler + weight features by financial importance"],
        "correct":2,
        "outcome_win": "Excellent! StandardScaler + domain-weighted features (EBITDA margin weight × 1.5, leverage weight × 2.0 — as they're the primary valuation drivers) produced peers with median EV/EBITDA multiple within 0.4x vs 2.1x without scaling. Lesson 12 covers this: 'The combination of distance metric and scaling method can produce completely different peer groups for the same company.'",
        "outcome_loss": "Weighted StandardScaler was optimal. Raw StandardScaler treats all features equally — but in M&A comparables, profitability and leverage drive multiples more than revenue alone. Lesson 12: 'Financial variables operate on completely different scales... This disparity distorts distance calculations and therefore the selection of nearest neighbors.' Domain knowledge in feature weighting adds material value.",
        "xp":15, "coins_win":40, "coins_loss":-15,
    },
    {
        "id":1202, "topic":"SVM & kNN", "difficulty":"medium",
        "title":"SVM Kernel Choice: Credit Boundary",
        "context": "You're classifying corporate bonds as Investment Grade vs High Yield using SVM (Lesson 12). Features: 8 financial ratios after StandardScaler. Linear kernel SVM: AUC=0.81. RBF kernel SVM: AUC=0.88. Polynomial (degree=3) kernel: AUC=0.86, but training crashes on datasets >50k bonds. The production system classifies 200k bonds daily. Your grid search found: RBF optimal γ=0.1, C=10.",
        "asset":"BOND CLASSIFIER", "price":0, "signal":"RBF",
        "options":["⭕ USE RBF kernel — best AUC + scalable","📈 USE Polynomial degree=3 — theoretically richer","📏 USE Linear kernel — interpretable, acceptable AUC"],
        "correct":0,
        "outcome_win": "Correct! RBF kernel (γ=0.1, C=10) is optimal: best AUC=0.88 at 200k daily predictions. Polynomial crashes at scale. Lesson 12: 'RBF: The Most Used — can handle complex decision boundaries, maps into infinite-dimensional space, very flexible.' The 7 AUC-point advantage over linear is worth the interpretability trade-off in a production classification system.",
        "outcome_loss": "RBF kernel was the right choice. Lesson 12: 'Start with RBF — works well in most cases.' The polynomial kernel's scaling failure eliminates it for 200k daily predictions. Linear kernel's 7-point AUC deficit matters at scale: on 200k bonds, that's potentially thousands of misclassified bonds per day. RBF delivers both performance and scalability.",
        "xp":25, "coins_win":65, "coins_loss":-25,
    },
    {
        "id":1203, "topic":"SVM & kNN", "difficulty":"hard",
        "title":"SVM Soft Margin C Parameter: Risk Tolerance",
        "context": "You're classifying distressed vs healthy companies with SVM (Lesson 12: Hard vs Soft Margin, Parameter C). C=0.01 (very small): wide margin, 18% training misclassifications, AUC=0.79. C=100 (very large): narrow margin, 2% training misclassifications, AUC=0.82 train / AUC=0.68 test (overfitting). C=1.0 (GridSearchCV optimal): AUC=0.84 train / AUC=0.81 test. The chief risk officer wants C=100: 'Only 2% training misclassifications means the model is more accurate.'",
        "asset":"DISTRESS CLASSIFIER", "price":0, "signal":"C=1.0",
        "options":["⚙️ USE C=1.0 — cross-validated optimal, best test AUC","📈 USE C=100 — lower training error as CRO wants","📉 USE C=0.01 — wide margin = most robust generalization"],
        "correct":0,
        "outcome_win": "Correct — and well argued! C=1.0 gives AUC=0.81 test vs C=100's AUC=0.68 test. You explain to the CRO: 'C=100 has lower training error but we deploy on NEW companies. The 0.13 test AUC gap means C=100 memorizes training data.' Lesson 12: 'Small C → wide margin, allows violations → simpler, more general model. Large C → narrow margin → risk of overfitting.'",
        "outcome_loss": "C=1.0 was correct. The CRO's reasoning — lower training error = better model — is the most common executive misunderstanding of ML. Lesson 12: large C = 'LOW bias, HIGH variance classifier... Risk: overfitting.' The 0.13 AUC difference on test data (0.81 vs 0.68) directly translates to thousands of wrong corporate distress assessments annually.",
        "xp":35, "coins_win":90, "coins_loss":-30,
    },

    # ══════════════════════════════════════════════════════
    # ORIGINAL SCENARIOS (kept as-is)
    # ══════════════════════════════════════════════════════
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
    {"title":"🌳 DECISION TREE DUEL", "desc":"Two models: Decision Tree vs XGBoost for GDPR compliance. Which do you deploy? Class votes live!", "topic":"Decision Trees"},
    {"title":"📐 OLS LIVE LAB", "desc":"Run a CAPM regression on live AAPL data. First student to find Jensen's alpha wins 80 FinCoins!", "topic":"Linear Models & OLS"},
    {"title":"🎯 LASSO FACE-OFF", "desc":"150 macro factors, 120 observations. P>N crisis! How do you build the model? 3-min group challenge.", "topic":"Ridge & Lasso"},
    {"title":"🔧 DATA LEAKAGE HUNT", "desc":"Find the 3 data leakage bugs hidden in this ML pipeline. First team to identify all 3 gets +100 XP!", "topic":"Data Engineering"},
    {"title":"🧠 PROMPT BATTLE", "desc":"Best Chain-of-Thought prompt for CET1 compliance check wins class vote. Submit yours now!", "topic":"Prompt Engineering"},
    {"title":"⚡ SVM KERNEL QUIZ", "desc":"60 seconds: which kernel for THIS dataset? RBF, Linear, or Polynomial? Class votes simultaneously!", "topic":"SVM & kNN"},
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
        st.markdown('<div class="sec-title">📋 Course Modules Progress — All 12 Lessons</div>', unsafe_allow_html=True)
        topics=[
            ("🧠","AI Foundations",        "AI Act · LLMs · Governance"),
            ("🔧","Data Engineering",      "Survivorship · Leakage · Feedback"),
            ("🏗️","Data Pipeline",         "SMOTE · Imbalance · Cost Matrix"),
            ("⚙️","Feature Engineering",  "Altman Z · Log Returns · EDA"),
            ("📊","Model Performance",     "ROC · PR-AUC · Calibration"),
            ("💬","Prompt Engineering",    "CoT · RAG · ToT · Few-Shot"),
            ("📐","Linear Models & OLS",   "CAPM · FF5 · Multicollinearity"),
            ("🎯","Ridge & Lasso",         "Regularization · λ Tuning · CV"),
            ("🌳","Decision Trees",        "Gini · Pruning · GDPR"),
            ("🌲","Ensemble Models",       "RF · XGBoost · McNemar"),
            ("⚡","SVM & kNN",             "Kernel Trick · Peer Groups"),
            ("💬","NLP in Finance",        "FinBERT · Sentiment · Alt Data"),
            ("🕵️","Fraud Detection",       "GNN · Drift · Micro-transactions"),
            ("📈","Algorithmic Trading",   "RL · Overfitting · HFT"),
            ("📉","Risk Management",       "VaR · CVaR · Liquidity"),
            ("📊","Credit Risk",           "PD · IFRS 9 · Stress Test"),
        ]
        cols=st.columns(4)
        for i,(emoji,name,sub) in enumerate(topics):
            done=st.session_state["topic_counts"].get(name,0)
            total=len([s for s in SCENARIOS if s["topic"]==name])
            with cols[i%4]:
                st.markdown(f"""
                <div class="badge-item" style="text-align:left;padding:14px;margin-bottom:8px;">
                    <div style="font-size:1.4rem">{emoji}</div>
                    <div style="font-weight:700;font-size:0.78rem;color:#c9d1d9;margin-top:5px">{name}</div>
                    <div style="font-size:0.67rem;color:#4a6b8a;margin-top:2px">{sub}</div>
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#00e5a0;margin-top:6px">{done}/{total} done</div>
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
