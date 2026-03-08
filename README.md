# 🏦 FinAI Trader v3
### Gamification Platform — Artificial Intelligence in Banking & Finance
**Sapienza University of Rome · Prof. Valentina Lagasio**

---

## 🎯 What is FinAI Trader?

FinAI Trader is an **interactive gamification app** for the Master course *AI in Banking & Finance*. Students make real-world AI/ML decisions in banking scenarios, earn XP and FinCoins, unlock badges, and compete on a live leaderboard.

Every scenario is grounded in real course content — from CAPM and Fama-French factor models to SMOTE, RAG, and IFRS 9 stage migration.

---

## 📊 Content Overview

| # | Module | Topics Covered | Scenarios |
|---|--------|---------------|-----------|
| 1 | 🧠 AI Foundations | AI Act, LLMs, GenAI Risk, Prompt Injection | 4 |
| 2 | 🔧 Data Engineering | Survivorship Bias, Look-Ahead, Feedback Loops, Non-Stationarity | 4 |
| 3 | 🏗️ Data Pipeline | Class Imbalance, SMOTE, Cost Matrix, Forward-Fill vs Interpolation | 4 |
| 4 | ⚙️ Feature Engineering | Altman Z-Score, Log Returns, ADF Test, Target Encoding, Alt Data | 4 |
| 5 | 📊 Model Performance | ROC vs PR-AUC, TimeSeriesSplit, Calibration, Overfitting | 4 |
| 6 | 🤖 Prompt Engineering | CoT, RAG, Tree of Thoughts, Few-Shot, Tabular CoT | 5 |
| 7 | 📐 Linear Models & OLS | CAPM, Fama-French 5-Factor, VIF, Heteroskedasticity | 4 |
| 8 | 🎯 Ridge & Lasso | Ridge vs Lasso, λ Tuning, ElasticNet, Factor Zoo, p>n | 4 |
| 9 | 🌳 Decision Trees | Gini Impurity, Pruning, GDPR Article 22, 2008 Parallel | 4 |
| 10 | 🌲 Ensemble Models | Random Forest, XGBoost, Boosting, McNemar Test | 4 |
| 11 | ⚡ SVM & kNN | RBF Kernel, M&A Peer Groups, C Parameter, Distance Metrics | 4 |
| 12 | 💬 NLP in Finance | FinBERT, FOMC Minutes, Employee Reviews, Regulatory NLP | 4 |
| 13 | 🕵️ Fraud Detection | GNN Money Mule Rings, Concept Drift, SMOTE Strategy | 4 |
| 14 | 📈 Algorithmic Trading | Backtest Overfitting, RL Regime Break, HFT Fingerprinting | 4 |
| 15 | 📉 Risk Management | VaR/CVaR, Liquidity Spiral, Model Risk SR 11-7 | 4 |
| 16 | 💳 Credit Risk | Alt Data Scoring, Stress Testing, IFRS 9, IRBA PD/LGD/EAD | 4 |

**Total: 90+ scenarios across 16 topics**

---

## 🚀 Deployment Guide (Free — 5 Minutes)

### Step 1: Upload to GitHub

1. Create a free account at [github.com](https://github.com)
2. Click **"New Repository"** → name it `finai-trader` → set to **Private**
3. Upload these two files:
   - `app.py`
   - `requirements.txt`

### Step 2: Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)** → Sign up with GitHub (free)
2. Click **"New app"**
3. Select:
   - **Repository**: `your-username/finai-trader`
   - **Branch**: `main`
   - **Main file**: `app.py`
4. Click **"Deploy!"** — takes ~60 seconds

### Step 3: Share the URL

- Streamlit gives you a URL like:  
  `https://your-username-finai-trader-app-xxxx.streamlit.app`
- **Share this exact URL** with all students before class
- All students who use this URL appear on the **shared leaderboard**

> ⚠️ **Important**: Students who run `streamlit run app.py` locally will NOT appear on the shared leaderboard. Everyone must use the deployed URL.

---

## 📋 Student Quick Start

1. **Open the URL** shared by your professor
2. **Enter your full name** (e.g., "Mario Rossi") — this is your leaderboard identity
3. **Start Trading** — scenarios are randomly selected from all 16 modules
4. **Use Topic Drill** to focus on a specific lesson you want to practice
5. **Bet FinCoins** on each decision — start with 200 coins
6. **Read every explanation** — right or wrong, it's where the learning happens
7. **Check the Leaderboard** to see your ranking vs classmates

---

## 👩‍🏫 Professor Quick Start

### Before Class
- Deploy the app once, share the URL with students
- Students should register before the session starts

### During Class
1. Go to **📡 Professor Mode**
2. Launch a **pre-built challenge** matching today's topic
3. Students see a notification and compete in real-time
4. Check **Live Class Statistics** to see engagement
5. Award extra credit to top 3 leaderboard players (optional)

### After Class
- The leaderboard shows cumulative progress across all sessions
- Use Topic Drill performance to identify weak areas for review

---

## 🎮 Game Mechanics

### XP & Levels
| Level | XP Required | Emoji |
|-------|------------|-------|
| Junior Analyst | 0 | 🌱 |
| Quant Associate | 150 | 📊 |
| ML Strategist | 400 | 🤖 |
| AI Portfolio Manager | 800 | 💼 |
| Head of FinAI | 1,400 | 🧠 |
| Chief AI Officer | 2,200 | 🏆 |

### FinCoins
- Start with **200 FinCoins**
- Bet 10–100 coins per trade using the slider
- Win: **+bet + fixed reward** (15–90 coins per scenario difficulty)
- Lose: **-bet + fixed penalty** (15–30 coins)
- Coins can never go below 0

### Difficulty & Rewards
| Difficulty | XP | Win Coins | Loss Coins |
|-----------|----|-----------|----|
| 🟢 Easy | 15 | +40 | -15 |
| 🟡 Medium | 20–25 | +55–65 | -20–25 |
| 🔴 Hard | 30–35 | +80–90 | -25–30 |

### Badges (28 total)
Badges unlock automatically for:
- **Milestone badges**: First trade, 5/20/50 trades, streak 3/7/12
- **Wealth badges**: 500/1,000/2,500 FinCoins
- **XP badges**: 500/1,500 XP
- **Module badges**: Complete 3+ scenarios in each of the 16 modules

---

## 🔧 Technical Notes

### Requirements
```
streamlit>=1.32.0
```
No additional dependencies. Uses only standard Python libraries + Streamlit.

### Architecture
- **Single-file application** — everything in `app.py`
- **Session-state based** — all player data stored in browser session
- **No database required** — works out of the box
- **Leaderboard**: All players on the same deployed instance share one leaderboard (session-aggregated)

### Persistent Leaderboard (Optional Upgrade)
The current leaderboard is session-aggregated — it works within a class session but resets if the app restarts. For a semester-long competition, add a free Supabase database:

```python
# Add to requirements.txt:
# supabase

# In app.py, replace save_to_leaderboard() with:
from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_to_leaderboard():
    supabase.table("leaderboard").upsert({
        "name": st.session_state["name"],
        "xp": st.session_state["xp"],
        "coins": st.session_state["coins"],
        "trades": st.session_state["trades"],
        "correct": st.session_state["correct"],
    }).execute()
```

Store `SUPABASE_URL` and `SUPABASE_KEY` in Streamlit Cloud Secrets.

---

## 📁 File Structure
```
finai-trader/
├── app.py           ← Main application (single file)
├── requirements.txt ← Streamlit dependency
└── README.md        ← This file
```

---

## 🎓 Course Integration Ideas

| Use Case | How |
|----------|-----|
| Pre-class warm-up | Students play 5 scenarios on today's topic before arriving |
| In-class competition | Launch Professor Mode challenges during the lecture |
| Weekly homework | Assign specific module drill as homework |
| Exam revision | Open access 1 week before exam — all topics available |
| Graded participation | Top 3 leaderboard weekly → 0.1 bonus point each |
| Group projects | Teams compete as groups — name format "TeamA-Mario" |

---

## 📬 Contact
**Prof. Valentina Lagasio** — valentina.lagasio@uniroma1.it  
Google Classroom code: **6hbcepwr**

---

*Built for the Master course "Artificial Intelligence in Banking & Finance" · Sapienza University of Rome*
