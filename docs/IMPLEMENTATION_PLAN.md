# ETF Justification Engine - Complete Implementation Plan

**Created:** 2025-10-30
**Status:** Ready for Implementation
**Estimated Timeline:** 7 days

---

## Table of Contents
1. [Architecture Decisions](#architecture-decisions)
2. [Portfolio Profile](#portfolio-profile)
3. [Complete File Structure](#complete-file-structure)
4. [Data Schemas](#data-schemas)
5. [API Integration Specifications](#api-integration-specifications)
6. [GitHub Actions Configuration](#github-actions-configuration)
7. [Setup Instructions](#setup-instructions)
8. [Implementation Phases](#implementation-phases)
9. [Code Specifications](#code-specifications)

---

## Architecture Decisions

### CRITICAL: Why Not Google Cloud Platform

**Original Plan:** GCP Cloud Functions + Cloud Scheduler
**Problem Discovered:** GCP requires billing account enabled even for free tier
- Cloud Scheduler API: Requires billing
- Cloud Build API: Requires billing

**Solution:** GitHub-based architecture (100% free, no billing)

### Final Architecture Stack

```
┌─────────────────────────────────────────────────────────┐
│  SCHEDULER: GitHub Actions                              │
│  - Cron: 4:30 PM ET daily (Mon-Fri)                     │
│  - Free: 2000 minutes/month                             │
│  - Usage: ~60 minutes/month (~2-3 min/day)              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  COMPUTE: Python Script (runs in GitHub Actions)        │
│  - Fetch market data (yfinance)                         │
│  - Radar scan (all 30 ETFs)                             │
│  - Scalpel dive (Focus List only)                       │
│  - Generate recommendations                             │
│  - Commit JSON to repo                                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  STORAGE: GitHub Repository (data/ directory)           │
│  - Version controlled (full audit trail)                │
│  - Free unlimited for text/JSON                         │
│  - Publicly accessible via raw.githubusercontent.com    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  FRONTEND: Vercel (React + Vite + TypeScript)           │
│  - Fetches JSON from GitHub raw URLs                    │
│  - Free unlimited hosting                               │
│  - Auto-deploy on git push                              │
└─────────────────────────────────────────────────────────┘
```

### Technology Choices

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **Backend Framework** | FastAPI | Async/await for parallel API calls, type hints, lighter than Flask |
| **Scheduler** | GitHub Actions | 100% free, no billing required, 2000 min/month |
| **Storage** | Git repo (JSON files) | Free, version controlled, simple, publicly accessible |
| **Frontend** | React + Vite + TypeScript | Modern, fast, Vercel-optimized |
| **Hosting** | Vercel | 100% free for personal projects |
| **Price Data** | yfinance | Free, unlimited for our usage |
| **News Data** | NewsAPI.org | 100 req/day free (we use ~5/day) |
| **LLM** | Google Gemini | 1500 req/day free (we use ~5/day) |

**REJECTED:** Alpha Vantage (25 req/day too limited for daily 30-ETF analysis)

---

## Portfolio Profile

### Current Holdings (as of 2025-10-30)

| Ticker | Shares | % Holdings | Price | Value | Gain/Loss |
|--------|--------|------------|-------|-------|-----------|
| IVV | 45 | 30% | $690.71 | $31,081.95 | +$1,106.10 (+3.69%) |
| IYW | 128 | 26% | $211.27 | $27,042.56 | +$2,087.04 (+8.36%) |
| IEMG | 303 | 20% | $69.14 | $20,949.42 | +$974.15 (+4.88%) |
| ITA | 97 | 20% | $217.45 | $21,092.65 | +$1,140.24 (+5.71%) |
| AGG | 50 | 5% | $100.79 | $5,039.50 | +$22.51 (+0.45%) |

**Total Portfolio Value:** $105,205.58
**Initial Capital:** $100,000.00
**Total Return:** +$5,205.58 (+5.21%)
**Cash Balance:** $0.00

### Strategy Profile: Growth-Aggressive

**Key Characteristics:**
- **95% Equity Exposure** (only 5% in AGG bonds)
- **Concentrated Sector Bets:** IYW (tech) + ITA (aerospace) = 46%
- **High International Exposure:** 20% in IEMG (emerging markets)
- **Minimal Cash Buffer:** 0% (vs. conservative 5-10%)

### Position Sizing Rules (Adjusted for Aggressive Profile)

```python
POSITION_LIMITS = {
    'core_min': 0.25,              # Lower than conservative (40%)
    'core_max': 0.40,              # Allow more satellite allocation
    'single_position_max': 0.30,   # You have IVV at 30%, IYW at 26%
    'sector_max': 0.50,            # Allow concentrated sector bets
    'tactical_position_max': 0.30, # Large tactical positions OK
    'equity_min': 0.85,            # Minimum 85% equity
    'equity_max': 1.00,            # Can be 100% equities
    'cash_overnight_max': 0.05,    # Project requirement
    'sgov_exempt': True,           # SGOV doesn't count as cash
}
```

### VIX-Based Risk Thresholds (Adjusted)

```python
VIX_THRESHOLDS = {
    'extreme_complacency': 15,     # VIX < 15: reduce risk
    'normal_lower': 15,            # VIX 15-25: full allocation
    'normal_upper': 25,
    'caution': 25,                 # VIX 25-35: trim high-beta
    'risk_off': 35,                # VIX > 35: defensive mode
}
```

**Note:** Conservative strategy uses VIX > 30 for risk-off. Your aggressive profile uses VIX > 35.

---

## Complete File Structure

```
etf-justification-engine/
│
├── .github/
│   └── workflows/
│       └── daily-analysis.yml          # GitHub Actions cron job
│
├── backend/
│   ├── __init__.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── radar_scan.py               # Volume/price spike detection
│   │   ├── scalpel_dive.py             # News + LLM deep analysis
│   │   ├── portfolio_engine.py         # Recommendation generator
│   │   ├── risk_manager.py             # VIX-based risk assessment
│   │   └── llm_service.py              # Gemini API integration
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── data_fetcher.py             # yfinance + NewsAPI wrappers
│   │   ├── storage.py                  # GitHub file operations
│   │   └── models.py                   # Pydantic data models
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py                 # Environment variables
│   │   ├── etf_universe.py             # 30 ETF list + metadata
│   │   └── strategy_params.py          # Allocation rules, VIX thresholds
│   │
│   ├── main.py                         # Entry point for GitHub Actions
│   ├── requirements.txt                # Python dependencies
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_radar.py
│       ├── test_scalpel.py
│       ├── test_portfolio.py
│       └── test_risk.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx           # Main layout
│   │   │   ├── PortfolioSummary.tsx    # Current holdings table
│   │   │   ├── FocusList.tsx           # Today's flagged ETFs
│   │   │   ├── Recommendations.tsx     # Trade suggestions
│   │   │   ├── JustificationPanel.tsx  # Detailed reasoning
│   │   │   ├── PerformanceChart.tsx    # Historical returns
│   │   │   └── RiskIndicator.tsx       # VIX gauge
│   │   │
│   │   ├── services/
│   │   │   └── api.ts                  # GitHub raw URL fetcher
│   │   │
│   │   ├── types/
│   │   │   └── index.ts                # TypeScript interfaces
│   │   │
│   │   ├── utils/
│   │   │   └── formatters.ts           # Number/date formatting
│   │   │
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   │
│   ├── public/
│   │   └── favicon.ico
│   │
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── data/                                # COMMITTED TO REPO (storage)
│   ├── portfolio/
│   │   └── current.json                 # Live portfolio state
│   │
│   ├── analysis/
│   │   ├── 2025-10-30.json
│   │   ├── 2025-10-29.json
│   │   └── ...                          # Daily analysis files
│   │
│   ├── transactions/
│   │   └── history.json                 # All executed trades
│   │
│   └── cache/
│       └── etf_metadata.json            # Sector classifications
│
├── docs/
│   ├── CLAUDE.md                        # AI assistant instructions
│   ├── PROJECT_BRIEF.md                 # Course requirements
│   ├── STRATEGY.md                      # Investment strategy
│   ├── ARCHITECTURE.md                  # System design (to be created)
│   ├── IMPLEMENTATION_PLAN.md           # This file
│   └── SETUP.md                         # Deployment guide (to be created)
│
├── scripts/
│   ├── initialize_portfolio.py          # Import current holdings
│   ├── manual_run.py                    # Local testing
│   └── backtest.py                      # Historical validation
│
├── .env.example                         # Template for environment variables
├── .gitignore
└── README.md
```

**Total Files to Create:** ~45 files

---

## Data Schemas

### 1. Portfolio State (`data/portfolio/current.json`)

```json
{
  "as_of": "2025-10-30T21:30:00Z",
  "initial_capital": 100000.00,
  "total_value": 105205.58,
  "cash_balance": 0.00,
  "total_return_pct": 0.0521,
  "daily_return_pct": 0.0085,

  "positions": {
    "IVV": {
      "shares": 45,
      "cost_basis": 690.71,
      "current_price": 691.50,
      "market_value": 31117.50,
      "weight": 0.296,
      "unrealized_gain": 35.55,
      "unrealized_gain_pct": 0.0011
    },
    "IYW": {
      "shares": 128,
      "cost_basis": 211.27,
      "current_price": 215.30,
      "market_value": 27558.40,
      "weight": 0.262,
      "unrealized_gain": 515.84,
      "unrealized_gain_pct": 0.0191
    }
    // ... other positions
  },

  "allocation_breakdown": {
    "core": 0.35,
    "major_satellites": 0.40,
    "tactical_satellites": 0.25,
    "hedging": 0.00
  },

  "sector_breakdown": {
    "Technology": 0.26,
    "Aerospace": 0.20,
    "Broad_Market": 0.30,
    "Emerging_Markets": 0.20,
    "Fixed_Income": 0.05
  },

  "geography_breakdown": {
    "US": 0.75,
    "International_Developed": 0.00,
    "Emerging_Markets": 0.20,
    "Global": 0.05
  },

  "risk_metrics": {
    "sharpe_ratio_30d": 1.42,
    "volatility_30d": 0.12,
    "max_drawdown": -0.023,
    "beta_to_spy": 1.15,
    "correlation_to_spy": 0.92
  }
}
```

**Pydantic Model:**
```python
from pydantic import BaseModel
from datetime import datetime

class Position(BaseModel):
    shares: int
    cost_basis: float
    current_price: float
    market_value: float
    weight: float
    unrealized_gain: float
    unrealized_gain_pct: float

class PortfolioState(BaseModel):
    as_of: datetime
    initial_capital: float
    total_value: float
    cash_balance: float
    total_return_pct: float
    daily_return_pct: float
    positions: dict[str, Position]
    allocation_breakdown: dict[str, float]
    sector_breakdown: dict[str, float]
    geography_breakdown: dict[str, float]
    risk_metrics: dict[str, float]
```

---

### 2. Daily Analysis (`data/analysis/YYYY-MM-DD.json`)

```json
{
  "date": "2025-10-30",
  "timestamp": "2025-10-30T21:30:00Z",
  "execution_time_seconds": 45.2,

  "market_overview": {
    "vix_level": 18.5,
    "vix_change_pct": -2.3,
    "vix_5d_avg": 19.2,
    "risk_mode": "normal",
    "sp500_close": 5750.50,
    "sp500_return_1d": 0.012,
    "sp500_return_5d": 0.031,
    "market_regime": "bull",
    "key_macro_events": [
      "Fed meeting tomorrow (no rate change expected)",
      "Tech earnings season ongoing"
    ]
  },

  "focus_list": [
    {
      "ticker": "IYW",
      "trigger_type": "volume_spike",
      "trigger_value": 1.65,
      "trigger_description": "Volume 165% of 30-day average",

      "price_data": {
        "current_price": 211.27,
        "price_change_1d": 0.0192,
        "price_change_5d": 0.0421,
        "high_52w": 220.50,
        "low_52w": 165.30,
        "volume_today": 8250000,
        "volume_30d_avg": 5000000,
        "volume_ratio": 1.65
      },

      "technical_indicators": {
        "sma_20": 208.50,
        "sma_50": 205.30,
        "sma_200": 195.00,
        "rsi_14": 62.5,
        "macd_signal": "bullish_crossover",
        "bollinger_position": "upper_band"
      },

      "news_analysis": {
        "news_count": 3,
        "sentiment_score": 0.72,
        "relevance_score": 0.85,
        "headlines": [
          "Tech sector rallies on strong earnings",
          "AI chip demand surges in Q3",
          "Cloud spending accelerates"
        ],
        "llm_summary": "Technology sector showing strong momentum driven by accelerating AI infrastructure spending. Major semiconductor companies reported better-than-expected Q3 earnings with robust guidance for Q4. Cloud service providers increasing capex budgets for 2025. Institutional buying evident from volume spike.",
        "key_themes": ["AI growth", "Strong earnings", "Institutional buying"],
        "risk_factors": ["Valuation concerns", "Potential profit-taking"]
      },

      "recommendation": "HOLD"
    }
  ],

  "recommendations": [
    {
      "ticker": "IYW",
      "action": "HOLD",
      "priority": "medium",
      "confidence": 0.85,

      "allocation": {
        "current_allocation": 0.26,
        "target_allocation": 0.26,
        "allocation_change": 0.00,
        "shares_current": 128,
        "shares_target": 128,
        "shares_to_trade": 0
      },

      "transaction_details": {
        "estimated_price": 211.27,
        "estimated_cost": 0.00,
        "commission": 0.00,
        "total_cost": 0.00,
        "execution_timeframe": "N/A"
      },

      "justification": {
        "thesis": "Technology sector continues to show strong fundamentals with AI-driven growth. Volume spike indicates institutional buying. Maintaining current 26% position aligns with growth-aggressive strategy.",

        "quantitative_evidence": {
          "momentum": "20-day MA ($208.50) crossed above 50-day MA ($205.30) - bullish signal",
          "volume": "165% of average (8.25M vs 5.0M) - strong conviction",
          "relative_strength": "Outperforming SPY by 3.2% over 5 days",
          "volatility": "14-day ATR: $4.20 (normal range)",
          "rsi": "62.5 - bullish but not overbought"
        },

        "qualitative_evidence": {
          "news_catalyst": "Strong Q3 earnings from semiconductor leaders (NVDA, AMD)",
          "sector_outlook": "AI infrastructure spending accelerating into 2025",
          "macro_alignment": "Fed pause supports growth stocks",
          "sentiment": "Institutional sentiment positive (0.72/1.0)"
        },

        "risk_assessment": {
          "primary_risk": "Tech concentration at 26% is aggressive",
          "mitigation": "Stop loss at $195 (-7.7% from current)",
          "sector_correlation": "High correlation to SPY (0.92) limits diversification benefit",
          "valuation_concern": "Trading near 52-week highs"
        },

        "holding_period": "Continue through next prospectus period (Nov 6)",
        "review_triggers": [
          "Price breaks below $200 (stop loss)",
          "VIX crosses above 25",
          "Negative earnings surprise from mega-cap tech"
        ]
      },

      "prospectus_text": "We maintain our 26% allocation to IYW (Technology Select Sector SPDR) based on sustained momentum and AI-driven growth narrative. The sector demonstrated institutional conviction with 165% above-average volume alongside positive price action (+1.9% daily, +4.2% weekly). Our quantitative models show bullish technical setup with moving average crossover and RSI at 62.5, while qualitative analysis of sector news indicates continued earnings strength from semiconductor leaders. This concentrated position aligns with our growth-aggressive mandate while maintaining defined risk parameters (stop loss at $195, representing -7.7% downside protection). We will continue monitoring through the November 6 prospectus period."
    },

    {
      "ticker": "SGOV",
      "action": "INITIATE",
      "priority": "low",
      "confidence": 0.70,

      "allocation": {
        "current_allocation": 0.00,
        "target_allocation": 0.03,
        "allocation_change": 0.03,
        "shares_current": 0,
        "shares_target": 32,
        "shares_to_trade": 32
      },

      "transaction_details": {
        "estimated_price": 100.50,
        "estimated_cost": 3216.00,
        "commission": 10.00,
        "total_cost": 3226.00,
        "source_of_funds": "Trim IVV by 5 shares",
        "execution_timeframe": "Next 2 trading days"
      },

      "justification": {
        "thesis": "Establishing small cash-equivalent buffer to maintain portfolio flexibility. Current 95% equity exposure leaves no dry powder for tactical opportunities identified by our Radar/Scalpel framework.",

        "quantitative_evidence": {
          "current_equity": "95% (AGG is only 5% fixed income)",
          "recommended_cash_buffer": "3-5% for tactical flexibility",
          "opportunity_cost": "Minimal - SGOV yields ~5.3% (near cash)",
          "impact_on_returns": "Negligible drag (~0.05% annually)"
        },

        "qualitative_evidence": {
          "strategic_rationale": "Build tactical reserve for high-conviction opportunities",
          "liquidity_management": "Enable rapid deployment when Focus List generates strong signals",
          "risk_consideration": "Minor diversification benefit during vol spikes",
          "precedent": "Best practice for active management strategies"
        },

        "risk_assessment": {
          "primary_risk": "Opportunity cost if market rallies strongly",
          "mitigation": "Small allocation (3%) limits drag",
          "liquidity_risk": "None - SGOV is T-bill equivalent",
          "credit_risk": "None - backed by US Treasury"
        },

        "holding_period": "Permanent cash buffer (will deploy tactically)",
        "review_triggers": [
          "High-conviction buy signal from Radar scan",
          "Portfolio value grows requiring larger buffer"
        ]
      },

      "execution_plan": {
        "step_1": "SELL 5 shares IVV at market (~$690.71/share = $3,453.55)",
        "step_2": "Commission: -$10.00",
        "step_3": "BUY 32 shares SGOV at market (~$100.50/share = $3,216.00)",
        "step_4": "Commission: -$10.00",
        "net_cash_change": "+$217.55",
        "new_ivv_allocation": "28.5%",
        "new_sgov_allocation": "3.0%"
      },

      "prospectus_text": "We initiated a 3% position in SGOV (iShares 0-3 Month Treasury Bond ETF) to establish a tactical cash buffer. Our current 95% equity allocation, while aligned with our aggressive growth mandate, leaves limited flexibility for opportunistic trades identified by our daily Radar/Scalpel analysis framework. This minor reallocation (funded by trimming IVV by 5 shares from 30% to 28.5%) maintains our equity bias while providing dry powder for high-conviction opportunities. SGOV's T-bill composition offers near-cash liquidity with minimal opportunity cost (~5.3% yield), serving as a permanent tactical reserve to be deployed when our quantitative models identify compelling entry points."
    }
  ],

  "portfolio_snapshot": {
    "total_value": 105205.58,
    "daily_return_pct": 0.0085,
    "total_return_pct": 0.0520,
    "sharpe_ratio_30d": 1.42,
    "max_drawdown": -0.023,
    "days_since_inception": 32,

    "allocation_breakdown": {
      "core": 0.35,
      "satellites": 0.65,
      "equity": 0.95,
      "fixed_income": 0.05,
      "cash_equivalents": 0.00
    },

    "top_performers_1d": [
      {"ticker": "IYW", "return": 0.0192},
      {"ticker": "ITA", "return": 0.0089},
      {"ticker": "IVV", "return": 0.0068}
    ],

    "top_performers_mtd": [
      {"ticker": "IYW", "return": 0.0836},
      {"ticker": "ITA", "return": 0.0571},
      {"ticker": "IEMG", "return": 0.0488}
    ]
  },

  "execution_summary": {
    "analysis_quality": "high",
    "focus_list_count": 1,
    "recommendations_count": 2,
    "api_calls_made": {
      "yfinance": 2,
      "newsapi": 1,
      "gemini": 1
    },
    "errors": [],
    "warnings": [
      "Tech sector concentration at 26% - monitor for diversification"
    ]
  }
}
```

**Pydantic Models:**
```python
class MarketOverview(BaseModel):
    vix_level: float
    vix_change_pct: float
    vix_5d_avg: float
    risk_mode: str
    sp500_close: float
    sp500_return_1d: float
    sp500_return_5d: float
    market_regime: str
    key_macro_events: list[str]

class FocusListItem(BaseModel):
    ticker: str
    trigger_type: str
    trigger_value: float
    trigger_description: str
    price_data: dict
    technical_indicators: dict
    news_analysis: dict
    recommendation: str

class Recommendation(BaseModel):
    ticker: str
    action: str  # HOLD, BUY, SELL, INITIATE, TRIM
    priority: str  # high, medium, low
    confidence: float
    allocation: dict
    transaction_details: dict
    justification: dict
    prospectus_text: str

class DailyAnalysis(BaseModel):
    date: str
    timestamp: datetime
    execution_time_seconds: float
    market_overview: MarketOverview
    focus_list: list[FocusListItem]
    recommendations: list[Recommendation]
    portfolio_snapshot: dict
    execution_summary: dict
```

---

### 3. Transaction History (`data/transactions/history.json`)

```json
{
  "transactions": [
    {
      "id": "txn_001",
      "date": "2025-09-29",
      "ticker": "IVV",
      "action": "BUY",
      "shares": 45,
      "price": 690.71,
      "commission": 10.00,
      "total_cost": 31091.95,
      "justification": "Initial portfolio allocation - core holding",
      "analysis_reference": "2025-09-29.json"
    },
    {
      "id": "txn_002",
      "date": "2025-09-29",
      "ticker": "AGG",
      "action": "BUY",
      "shares": 50,
      "price": 100.79,
      "commission": 10.00,
      "total_cost": 5049.50,
      "justification": "Initial portfolio allocation - core fixed income",
      "analysis_reference": "2025-09-29.json"
    }
    // ... more transactions
  ],

  "summary": {
    "total_transactions": 10,
    "total_commissions_paid": 100.00,
    "total_bought": 55000.00,
    "total_sold": 0.00,
    "net_cash_flow": -55000.00
  }
}
```

---

### 4. ETF Metadata (`data/cache/etf_metadata.json`)

```json
{
  "IVV": {
    "name": "iShares Core S&P 500 ETF",
    "category": "Core",
    "sector": "Broad Market",
    "geography": "US",
    "asset_class": "Equity",
    "expense_ratio": 0.0003,
    "avg_volume": 4500000,
    "description": "Tracks the S&P 500 index"
  },
  "IYW": {
    "name": "iShares U.S. Technology ETF",
    "category": "Major Satellite",
    "sector": "Technology",
    "geography": "US",
    "asset_class": "Equity",
    "expense_ratio": 0.0039,
    "avg_volume": 5000000,
    "description": "Technology sector exposure"
  }
  // ... all 30 ETFs
}
```

---

## API Integration Specifications

### 1. yfinance (Price/Volume Data)

**Free Tier:** Unlimited (uses Yahoo Finance)
**Daily Usage:** ~2-3 calls
**Rate Limiting:** Add 1-second delays between calls

```python
import yfinance as yf
import time

# Batch download for efficiency
tickers = ['IVV', 'IEMG', 'ITA', ...]  # All 30
data = yf.download(
    tickers=tickers,
    period='90d',       # Last 90 days for MA calculations
    interval='1d',
    group_by='ticker',
    auto_adjust=True,
    threads=False       # Sequential to avoid rate limiting
)

# VIX data (separate call)
time.sleep(1)
vix = yf.download('^VIX', period='30d', interval='1d')
```

**Data Retrieved:**
- Open, High, Low, Close, Volume
- 90 days of history (for moving averages)
- Real-time quotes (15-min delay acceptable)

**Error Handling:**
- Retry with exponential backoff (max 3 attempts)
- Fall back to cached data if yfinance fails
- Log errors but continue analysis

---

### 2. NewsAPI.org (News Headlines)

**Free Tier:** 100 requests/day
**Daily Usage:** ~5 requests (one per Focus List ETF)
**Rate Limiting:** 1 request/second

```python
import requests
import time

NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
NEWSAPI_BASE = 'https://newsapi.org/v2/everything'

def fetch_news(ticker: str, etf_name: str) -> list:
    """
    Fetch news for a specific ETF.
    Focus List only (not all 30 ETFs).
    """
    # Search query optimized for ETF sector
    query = f'"{etf_name}" OR "{ticker}" OR sector_keyword'

    params = {
        'q': query,
        'apiKey': NEWSAPI_KEY,
        'language': 'en',
        'sortBy': 'relevancy',
        'pageSize': 5,          # Top 5 articles only
        'from': '2025-10-29',   # Last 24-48 hours
        'to': '2025-10-30'
    }

    response = requests.get(NEWSAPI_BASE, params=params)
    time.sleep(1)  # Rate limiting

    if response.status_code == 200:
        return response.json()['articles']
    else:
        return []

# Example for IYW (Technology)
articles = fetch_news('IYW', 'iShares U.S. Technology ETF')
```

**Optimization Strategy:**
- Only call for ETFs on Focus List (3-5 per day)
- Cache results for 6 hours
- Skip news if Focus List is empty
- Fallback to generic "technology sector news" if no ETF-specific news

---

### 3. Google Gemini API (LLM Summarization)

**Free Tier:** 1,500 requests/day
**Daily Usage:** ~5 requests (one per Focus List ETF)
**Rate Limiting:** 60 requests/minute

```python
import google.generativeai as genai

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

def summarize_news(ticker: str, articles: list) -> dict:
    """
    Use Gemini to summarize news and extract sentiment.
    """
    # Prepare article text
    article_text = "\n\n".join([
        f"Headline: {a['title']}\nSource: {a['source']['name']}\nContent: {a['description']}"
        for a in articles[:5]
    ])

    prompt = f"""
    You are a financial analyst. Analyze the following news articles about {ticker} ETF.

    Articles:
    {article_text}

    Provide:
    1. A 2-3 sentence summary of the main themes
    2. Sentiment score from -1 (very negative) to +1 (very positive)
    3. Relevance score from 0 (not relevant) to 1 (highly relevant)
    4. List of key themes (max 3)
    5. List of risk factors (max 3)

    Format your response as JSON:
    {{
      "summary": "...",
      "sentiment_score": 0.0,
      "relevance_score": 0.0,
      "key_themes": ["theme1", "theme2"],
      "risk_factors": ["risk1", "risk2"]
    }}
    """

    response = model.generate_content(prompt)
    return json.loads(response.text)

# Example usage
summary = summarize_news('IYW', articles)
```

**Prompt Engineering:**
- Structured output (JSON) for easy parsing
- Specific scoring metrics (sentiment, relevance)
- Focused on actionable insights
- Concise output (reduces token usage)

---

## GitHub Actions Configuration

### Workflow File: `.github/workflows/daily-analysis.yml`

```yaml
name: Daily ETF Analysis

on:
  schedule:
    # Runs at 4:30 PM ET (9:30 PM UTC) Monday-Friday
    # Note: GitHub Actions uses UTC time
    - cron: '30 21 * * 1-5'

  workflow_dispatch:  # Allow manual trigger for testing

permissions:
  contents: write  # Required to commit analysis results

jobs:
  analyze:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          fetch-depth: 0  # Full history for git operations

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          cd backend
          pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run daily analysis
        env:
          NEWSAPI_KEY: ${{ secrets.NEWSAPI_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          TZ: 'America/New_York'
        run: |
          cd backend
          python main.py

      - name: Commit analysis results
        run: |
          git config user.name "ETF Advisor Bot"
          git config user.email "advisor@etf-justification-engine.com"
          git add data/

          # Only commit if there are changes
          if ! git diff-index --quiet HEAD; then
            git commit -m "chore: daily analysis $(date +'%Y-%m-%d %H:%M ET')"
            git push
          else
            echo "No changes to commit"
          fi

      - name: Upload logs (on failure)
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: analysis-logs
          path: backend/*.log
          retention-days: 7
```

**Key Features:**
- Runs Monday-Friday at 4:30 PM ET
- Manual trigger available for testing
- Caches pip dependencies (faster runs)
- Auto-commits results to data/ directory
- Uploads logs on failure for debugging
- 10-minute timeout (analysis should take ~2-3 min)

---

## Setup Instructions

### Step 1: GitHub Repository Configuration (5 minutes)

```bash
# 1. Ensure repo is PUBLIC (required for free GitHub Actions)
# Go to Settings → General → Change visibility to Public

# 2. Enable GitHub Actions
# Go to Settings → Actions → General
# Select "Allow all actions and reusable workflows"

# 3. Set branch protection (optional but recommended)
# Go to Settings → Branches → Add rule for 'main'
# Enable "Require status checks to pass before merging"
```

---

### Step 2: Configure API Keys (3 minutes)

```bash
# 1. Get NewsAPI key
#    - Go to https://newsapi.org/register
#    - Free tier: 100 requests/day
#    - Copy API key

# 2. Get Gemini API key
#    - Go to https://aistudio.google.com/app/apikey
#    - Create new API key
#    - Free tier: 1500 requests/day
#    - Copy API key

# 3. Add secrets to GitHub
#    - Go to Settings → Secrets and variables → Actions
#    - Click "New repository secret"
#    - Add:
#      Name: NEWSAPI_KEY
#      Value: [your key]
#
#    - Add:
#      Name: GEMINI_API_KEY
#      Value: [your key]
```

---

### Step 3: Initialize Data Structure (5 minutes)

```bash
# 1. Create data directory structure
mkdir -p data/{portfolio,analysis,transactions,cache}

# 2. Run initialization script
python scripts/initialize_portfolio.py

# This will create:
# - data/portfolio/current.json (your 5 holdings imported)
# - data/transactions/history.json (initial trades)
# - data/cache/etf_metadata.json (30 ETF details)

# 3. Commit initial data
git add data/
git commit -m "chore: initialize portfolio data"
git push
```

---

### Step 4: Test GitHub Actions Workflow (5 minutes)

```bash
# 1. Push the workflow file
git add .github/workflows/daily-analysis.yml
git commit -m "feat: add daily analysis workflow"
git push

# 2. Manually trigger workflow (for testing)
# Go to Actions tab → "Daily ETF Analysis" → "Run workflow"

# 3. Monitor execution
# Click on the running workflow to see logs
# Should complete in ~2-3 minutes

# 4. Verify results
# Check data/analysis/ for new JSON file
# Check git history for auto-commit
```

---

### Step 5: Deploy Frontend to Vercel (10 minutes)

```bash
# 1. Go to https://vercel.com and sign in with GitHub

# 2. Click "Add New Project"

# 3. Select your repository: etf-justification-engine

# 4. Configure project:
#    Framework Preset: Vite
#    Root Directory: frontend
#    Build Command: npm run build
#    Output Directory: dist
#    Install Command: npm install

# 5. Add environment variables (if needed):
#    VITE_GITHUB_RAW_BASE=https://raw.githubusercontent.com/[username]/etf-justification-engine/main/data

# 6. Click "Deploy"

# 7. Vercel will:
#    - Install dependencies
#    - Build React app
#    - Deploy to [project-name].vercel.app
#    - Auto-deploy on future git pushes to main
```

---

### Step 6: Verify End-to-End Flow (5 minutes)

```bash
# 1. Wait for next scheduled run (4:30 PM ET) OR trigger manually

# 2. Check GitHub Actions succeeded
# Go to Actions tab → Should show green checkmark

# 3. Check data was committed
# Go to data/analysis/ → Should have today's JSON file

# 4. Check frontend displays data
# Go to [your-app].vercel.app
# Should show:
#   - Current portfolio
#   - Today's focus list
#   - Recommendations

# 5. Check git history
# git log
# Should see auto-commit from "ETF Advisor Bot"
```

---

## Implementation Phases

### Phase 1: Foundation (Day 1) - 4 hours

**Goals:**
- Complete file structure
- Configuration files
- Data directory setup
- Initial portfolio import

**Tasks:**
1. Create all directories
2. Create `backend/config/etf_universe.py` with 30 ETFs
3. Create `backend/config/strategy_params.py` with your rules
4. Create `backend/config/settings.py` for environment variables
5. Create `scripts/initialize_portfolio.py`
6. Run initialization script
7. Commit initial structure

**Validation:**
- All directories exist
- `data/portfolio/current.json` contains your 5 holdings
- `data/cache/etf_metadata.json` contains all 30 ETFs

---

### Phase 2: Data Layer (Day 2) - 6 hours

**Goals:**
- Data fetching (yfinance, NewsAPI)
- Data models (Pydantic)
- Storage operations

**Tasks:**
1. Create `backend/data/models.py` (all Pydantic models)
2. Create `backend/data/data_fetcher.py`:
   - `fetch_market_data()` - yfinance batch download
   - `fetch_vix_data()` - VIX index
   - `fetch_news()` - NewsAPI for specific ticker
3. Create `backend/data/storage.py`:
   - `load_portfolio()` - read current.json
   - `save_portfolio()` - write current.json
   - `save_analysis()` - write daily analysis
   - `append_transaction()` - log trades
4. Write unit tests for data layer
5. Test with local `.env` file

**Validation:**
- `fetch_market_data(['IVV', 'IYW'])` returns 90 days of OHLCV
- `fetch_vix_data()` returns current VIX level
- `fetch_news('IYW', 'iShares U.S. Technology ETF')` returns articles
- Models validate correctly

---

### Phase 3: Core Analysis Engine (Day 3) - 8 hours

**Goals:**
- Radar scan (all 30 ETFs)
- Risk manager (VIX-based)
- Portfolio engine (recommendations)

**Tasks:**
1. Create `backend/core/radar_scan.py`:
   - `calculate_volume_spike()` - compare to 30-day avg
   - `calculate_price_move()` - compare to historical volatility
   - `calculate_technical_indicators()` - MA, RSI, MACD
   - `generate_focus_list()` - return 3-5 flagged ETFs

2. Create `backend/core/risk_manager.py`:
   - `get_vix_level()` - current VIX
   - `determine_risk_mode()` - normal/caution/risk-off
   - `calculate_equity_allocation()` - dynamic based on VIX
   - `check_position_limits()` - validate against rules

3. Create `backend/core/portfolio_engine.py`:
   - `calculate_current_allocation()` - from portfolio state
   - `generate_target_allocation()` - based on risk mode
   - `generate_recommendations()` - BUY/SELL/HOLD decisions
   - `calculate_trade_details()` - shares, cost, commission

4. Write unit tests
5. Test with real market data

**Validation:**
- Radar scan correctly identifies high-volume ETFs
- VIX > 35 triggers risk-off mode
- Portfolio engine respects position limits
- Recommendations include proper justifications

---

### Phase 4: Intelligence Layer (Day 4) - 6 hours

**Goals:**
- LLM integration (Gemini)
- Scalpel dive (deep analysis)
- Justification generation

**Tasks:**
1. Create `backend/core/llm_service.py`:
   - `configure_gemini()` - API setup
   - `summarize_news()` - articles → summary + sentiment
   - `generate_justification()` - create prospectus text
   - `extract_themes()` - key themes and risks

2. Create `backend/core/scalpel_dive.py`:
   - `analyze_focus_etf()` - combine news + LLM + technicals
   - `enrich_recommendation()` - add qualitative evidence
   - `generate_prospectus_snippet()` - ready-to-use text

3. Handle API errors gracefully
4. Test with various news scenarios
5. Validate JSON output format

**Validation:**
- Gemini correctly extracts sentiment from news
- Summaries are concise (2-3 sentences)
- Prospectus snippets are professional and specific
- Handles case of "no news available"

---

### Phase 5: Main Orchestrator (Day 5) - 4 hours

**Goals:**
- Complete `main.py` entry point
- Orchestrate all modules
- Generate complete daily analysis

**Tasks:**
1. Create `backend/main.py`:
   ```python
   def main():
       # 1. Load current portfolio
       # 2. Fetch market data for all 30 ETFs
       # 3. Run Radar scan → Focus List
       # 4. Fetch VIX → Risk mode
       # 5. For each Focus List ETF:
       #    - Fetch news
       #    - Run Scalpel dive
       #    - Enrich with LLM
       # 6. Generate recommendations
       # 7. Save daily analysis JSON
       # 8. Update portfolio state
       # 9. Log execution summary
   ```

2. Add comprehensive logging
3. Add error handling (retry logic)
4. Test complete end-to-end flow
5. Optimize for ~2-minute runtime

**Validation:**
- Completes in under 5 minutes
- Generates valid `data/analysis/YYYY-MM-DD.json`
- Updates `data/portfolio/current.json` with new prices
- Logs execution metrics

---

### Phase 6: Frontend (Days 6-7) - 12 hours

**Goals:**
- React dashboard
- All components
- API integration
- Deploy to Vercel

**Tasks:**

**Day 6 (Backend Integration):**
1. Set up Vite + React + TypeScript
2. Create `frontend/src/services/api.ts`:
   - `fetchLatestAnalysis()` - from GitHub raw
   - `fetchPortfolio()` - current holdings
   - `fetchHistoricalAnalysis()` - last 30 days
3. Create `frontend/src/types/index.ts` (TypeScript interfaces)
4. Build basic layout with Tailwind CSS

**Day 7 (Components):**
5. Create `PortfolioSummary.tsx`:
   - Table of current holdings
   - Total value, return %, Sharpe ratio
   - Allocation pie chart

6. Create `FocusList.tsx`:
   - Today's flagged ETFs
   - Trigger reasons
   - Price changes, volume ratios

7. Create `Recommendations.tsx`:
   - Trade suggestions (BUY/SELL/HOLD)
   - Shares to trade, estimated cost
   - Clickable to expand justification

8. Create `JustificationPanel.tsx`:
   - Full thesis
   - Quantitative evidence
   - Qualitative evidence
   - Risk assessment
   - Prospectus snippet (copy button)

9. Create `PerformanceChart.tsx`:
   - Line chart of portfolio value over time
   - Benchmark comparison (SPY)
   - Drawdown visualization

10. Create `RiskIndicator.tsx`:
    - VIX gauge
    - Risk mode badge (normal/caution/risk-off)
    - Color-coded

11. Polish UI/UX
12. Deploy to Vercel
13. Test on mobile

**Validation:**
- Dashboard loads data from GitHub
- All components render correctly
- Charts display properly
- Responsive on mobile
- Deployed URL accessible

---

### Phase 7: Testing & Refinement (Day 7 evening) - 2 hours

**Tasks:**
1. Run complete analysis manually
2. Verify GitHub Actions workflow
3. Check auto-commit works
4. Test frontend updates automatically
5. Review first real daily analysis
6. Iterate on any issues

**Validation:**
- Workflow runs successfully at 4:30 PM ET
- Analysis JSON is high-quality
- Recommendations are actionable
- Frontend displays correctly
- No errors in logs

---

## Code Specifications

### ETF Universe Configuration

**File:** `backend/config/etf_universe.py`

```python
from enum import Enum
from typing import Dict

class ETFCategory(str, Enum):
    CORE = "Core"
    MAJOR_SATELLITE = "Major Satellite"
    TACTICAL_SATELLITE = "Tactical Satellite"
    HEDGING = "Hedging"

class AssetClass(str, Enum):
    EQUITY = "Equity"
    FIXED_INCOME = "Fixed Income"
    COMMODITIES = "Commodities"
    CASH_EQUIVALENT = "Cash Equivalent"

# Complete 30-ETF universe
ETF_UNIVERSE = {
    # CORE (2)
    "IVV": {
        "name": "iShares Core S&P 500 ETF",
        "category": ETFCategory.CORE,
        "sector": "Broad Market",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0003,
    },
    "AGG": {
        "name": "iShares Core U.S. Aggregate Bond ETF",
        "category": ETFCategory.CORE,
        "sector": "Fixed Income",
        "geography": "US",
        "asset_class": AssetClass.FIXED_INCOME,
        "expense_ratio": 0.0003,
    },

    # MAJOR SATELLITES (8)
    "IEMG": {
        "name": "iShares Core MSCI Emerging Markets ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Broad Market",
        "geography": "Emerging Markets",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0009,
    },
    "IJR": {
        "name": "iShares Core S&P Small-Cap ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Small Cap",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0006,
    },
    "IJH": {
        "name": "iShares Core S&P Mid-Cap ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Mid Cap",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0005,
    },
    "IUSG": {
        "name": "iShares Core S&P U.S. Growth ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Growth",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0004,
    },
    "IYW": {
        "name": "iShares U.S. Technology ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Technology",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
    },
    "IEV": {
        "name": "iShares Europe ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Broad Market",
        "geography": "Europe",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0059,
    },
    "TLT": {
        "name": "iShares 20+ Year Treasury Bond ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Government Bonds",
        "geography": "US",
        "asset_class": AssetClass.FIXED_INCOME,
        "expense_ratio": 0.0015,
    },
    "LQD": {
        "name": "iShares iBoxx $ Investment Grade Corporate Bond ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Corporate Bonds",
        "geography": "US",
        "asset_class": AssetClass.FIXED_INCOME,
        "expense_ratio": 0.0014,
    },

    # TACTICAL SATELLITES (16)
    "ITA": {
        "name": "iShares U.S. Aerospace & Defense ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Aerospace",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
    },
    "MCHI": {
        "name": "iShares MSCI China ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Broad Market",
        "geography": "China",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0059,
    },
    "IBB": {
        "name": "iShares Biotechnology ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Biotechnology",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0044,
    },
    "IYF": {
        "name": "iShares U.S. Financials ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Financials",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
    },
    "EWC": {
        "name": "iShares MSCI Canada ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Broad Market",
        "geography": "Canada",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0047,
    },
    "IFRA": {
        "name": "iShares U.S. Infrastructure ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Infrastructure",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0030,
    },
    "IYH": {
        "name": "iShares U.S. Healthcare ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Healthcare",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
    },
    "IYG": {
        "name": "iShares U.S. Financial Services ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Financial Services",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
    },
    "IYJ": {
        "name": "iShares U.S. Industrials ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Industrials",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
    },
    "IYC": {
        "name": "iShares U.S. Consumer Discretionary ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Consumer Discretionary",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
    },
    "IYK": {
        "name": "iShares U.S. Consumer Staples ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Consumer Staples",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
    },
    "IYE": {
        "name": "iShares U.S. Energy ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Energy",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
    },
    "IYZ": {
        "name": "iShares U.S. Telecommunications ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Telecommunications",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
    },
    "MBB": {
        "name": "iShares MBS ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Mortgage-Backed Securities",
        "geography": "US",
        "asset_class": AssetClass.FIXED_INCOME,
        "expense_ratio": 0.0004,
    },
    "IYR": {
        "name": "iShares U.S. Real Estate ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Real Estate",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
    },
    "IYT": {
        "name": "iShares U.S. Transportation ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Transportation",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
    },

    # HEDGING (4)
    "SGOV": {
        "name": "iShares 0-3 Month Treasury Bond ETF",
        "category": ETFCategory.HEDGING,
        "sector": "Cash Equivalent",
        "geography": "US",
        "asset_class": AssetClass.CASH_EQUIVALENT,
        "expense_ratio": 0.0005,
    },
    "TIP": {
        "name": "iShares TIPS Bond ETF",
        "category": ETFCategory.HEDGING,
        "sector": "Inflation-Protected",
        "geography": "US",
        "asset_class": AssetClass.FIXED_INCOME,
        "expense_ratio": 0.0019,
    },
    "IAU": {
        "name": "iShares Gold Trust",
        "category": ETFCategory.HEDGING,
        "sector": "Gold",
        "geography": "Global",
        "asset_class": AssetClass.COMMODITIES,
        "expense_ratio": 0.0025,
    },
    "GSG": {
        "name": "iShares S&P GSCI Commodity-Indexed Trust",
        "category": ETFCategory.HEDGING,
        "sector": "Commodities",
        "geography": "Global",
        "asset_class": AssetClass.COMMODITIES,
        "expense_ratio": 0.0075,
    },
}

# Helper functions
def get_all_tickers() -> list[str]:
    return list(ETF_UNIVERSE.keys())

def get_etf_info(ticker: str) -> Dict:
    return ETF_UNIVERSE.get(ticker, {})

def get_etfs_by_category(category: ETFCategory) -> list[str]:
    return [
        ticker for ticker, info in ETF_UNIVERSE.items()
        if info["category"] == category
    ]

def get_etfs_by_sector(sector: str) -> list[str]:
    return [
        ticker for ticker, info in ETF_UNIVERSE.items()
        if info["sector"] == sector
    ]
```

---

### Strategy Parameters

**File:** `backend/config/strategy_params.py`

```python
# User's Growth-Aggressive Profile

# Position Limits
POSITION_LIMITS = {
    'core_min': 0.25,              # Minimum core allocation
    'core_max': 0.40,              # Maximum core allocation
    'single_position_max': 0.30,   # Max % in any single ETF
    'sector_max': 0.50,            # Max % in any sector
    'tactical_position_max': 0.30, # Max % in single tactical satellite
    'equity_min': 0.85,            # Minimum equity exposure
    'equity_max': 1.00,            # Maximum equity exposure (can be 100%)
    'cash_overnight_max': 0.05,    # Project constraint
    'sgov_exempt': True,           # SGOV doesn't count as cash
}

# VIX-Based Risk Thresholds
VIX_THRESHOLDS = {
    'extreme_complacency': 15,     # VIX < 15
    'normal_lower': 15,
    'normal_upper': 25,
    'caution': 25,                 # VIX 25-35
    'risk_off': 35,                # VIX > 35 (more aggressive than standard 30)
}

# Risk Mode Equity Allocations
RISK_MODE_ALLOCATIONS = {
    'extreme_complacency': {       # VIX < 15
        'equity': 0.85,
        'fixed_income': 0.10,
        'cash_equivalent': 0.05,
    },
    'normal': {                    # VIX 15-25
        'equity': 0.95,
        'fixed_income': 0.05,
        'cash_equivalent': 0.00,
    },
    'caution': {                   # VIX 25-35
        'equity': 0.80,
        'fixed_income': 0.15,
        'cash_equivalent': 0.05,
    },
    'risk_off': {                  # VIX > 35
        'equity': 0.60,
        'fixed_income': 0.20,
        'cash_equivalent': 0.20,
    },
}

# Radar Scan Triggers
RADAR_TRIGGERS = {
    'price_move_threshold': 0.015,    # 1.5% daily move (vs 2% for conservative)
    'volume_spike_threshold': 1.30,   # 130% of 30-day avg (vs 150%)
    'price_stddev_threshold': 2.0,    # 2 standard deviations
    'momentum_crossover': True,       # Flag MA crossovers
    'focus_list_max_size': 7,         # Max ETFs on Focus List
}

# Trading Rules
TRADING_RULES = {
    'commission_per_trade': 10.00,
    'allow_margin': False,
    'allow_partial_shares': False,
    'min_trade_size_usd': 500.00,     # Don't trade < $500 (commission too high)
}

# Rebalancing Triggers
REBALANCE_TRIGGERS = {
    'core_drift_threshold': 0.10,     # Rebalance if core drifts >10% from target
    'position_drift_threshold': 0.05,  # Rebalance if position drifts >5%
    'days_between_rebalance': 7,      # Minimum 7 days between rebalances
}

# Prospectus Settings
PROSPECTUS_SETTINGS = {
    'min_justification_length': 100,  # Min characters for justification
    'include_prospectus_snippet': True,
    'prospectus_snippet_length': 300, # Target length for snippet
}
```

---

### Environment Variables

**File:** `.env.example`

```bash
# API Keys (DO NOT commit actual keys - use GitHub Secrets)
NEWSAPI_KEY=your_newsapi_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# GitHub Configuration (for local development)
GITHUB_REPO=username/etf-justification-engine
GITHUB_RAW_BASE=https://raw.githubusercontent.com/username/etf-justification-engine/main/data

# Portfolio Settings
INITIAL_CAPITAL=100000.00
PORTFOLIO_START_DATE=2025-09-29

# Analysis Settings
MARKET_DATA_PERIOD=90d
VIX_TICKER=^VIX
BENCHMARK_TICKER=SPY

# Logging
LOG_LEVEL=INFO
LOG_FILE=analysis.log
```

---

## Success Metrics

### Daily Analysis Quality
- Execution time: < 5 minutes
- API calls: < 10 total (within free tiers)
- Focus List: 3-7 ETFs identified
- Recommendations: At least 1 actionable trade
- Justifications: > 100 characters each
- Prospectus snippets: Ready to copy-paste

### System Reliability
- GitHub Actions success rate: > 95%
- Auto-commit success rate: 100%
- Frontend deployment: < 2 minutes
- Data freshness: Updated by 4:45 PM ET daily

### Portfolio Performance
- Sharpe Ratio: > 1.0
- Max Drawdown: < 20%
- Tracking Error vs SPY: Moderate (we're active, not passive)
- Commission Efficiency: < 0.2% of portfolio value/month

### Prospectus Readiness
- Every trade has detailed justification
- Quantitative + qualitative evidence
- Risk assessment included
- Professional narrative tone
- Data-backed claims

---

## Cost Breakdown (Monthly)

| Service | Limit | Usage | Cost |
|---------|-------|-------|------|
| GitHub Actions | 2000 min | 60 min | $0.00 |
| GitHub Storage | Unlimited | 1 MB | $0.00 |
| Vercel | Unlimited | 1 site | $0.00 |
| yfinance | Unlimited | ~50 calls | $0.00 |
| NewsAPI | 100/day | ~100/month | $0.00 |
| Gemini | 1500/day | ~100/month | $0.00 |
| **TOTAL** | | | **$0.00** |

---

## Emergency Procedures

### If GitHub Actions Fails
1. Check logs in Actions tab
2. Verify API keys are set correctly
3. Run `python backend/main.py` locally
4. Manually commit results: `git add data/ && git commit && git push`

### If yfinance Fails
1. Check Yahoo Finance status
2. Retry with exponential backoff (already implemented)
3. Use cached data from previous day
4. Log warning but continue analysis

### If NewsAPI Fails
1. Check rate limit (100/day)
2. Skip news analysis for today
3. Use technical indicators only
4. Generate recommendations without qualitative evidence

### If Gemini Fails
1. Check API key validity
2. Fall back to rule-based sentiment (positive/negative word count)
3. Generate basic justifications without LLM
4. Log error for manual review

### If Frontend Doesn't Update
1. Check Vercel deployment status
2. Verify GitHub raw URLs are accessible
3. Check CORS settings
4. Manually redeploy: `vercel --prod`

---

## Next Steps for Tomorrow

1. **Review this document thoroughly**
2. **Confirm all API keys are ready** (NewsAPI, Gemini)
3. **Start with Phase 1** (Foundation setup)
4. **Ask questions if any section is unclear**
5. **I'll be ready to implement all code systematically**

---

**Document Status:** Complete and ready for implementation
**Last Updated:** 2025-10-30
**Next Review:** After Phase 1 completion
