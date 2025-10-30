# Investment Strategy & Decision Framework

### 1. Guiding Philosophy: Moderate Growth

Our primary objective is to achieve superior **risk-adjusted returns**. We are not speculators chasing the highest possible raw return; we are managers building a robust, justifiable portfolio. Success is defined by a consistent process and a clear narrative, leading to a portfolio that performs well without taking on excessive, uncompensated risk.

### 2. The Core-Satellite Model

This is the foundational structure of our portfolio. It provides discipline and ensures we maintain a diversified base while allowing for tactical flexibility.

-   **The CORE (40-60% of Portfolio):** The stable center. These are our "always-on" positions that anchor the portfolio.
    -   `IVV`: Core US Equity exposure.
    -   `AGG`: Core US Fixed Income exposure.

-   **MAJOR SATELLITES (20-40% of Portfolio):** Large, directional holdings used to express our primary macro-thematic views.
    -   **Growth/Value Tilts:** `IUSG` (Growth), `IYW` (Tech)
    -   **Size Tilts:** `IJR` (Small-Cap), `IJH` (Mid-Cap)
    -   **International Tilts:** `IEMG` (Emerging), `IEV` (Europe)
    -   **Interest Rate Tilts:** `TLT` (Long-Duration), `LQD` (Corporate)

-   **TACTICAL SATELLITES (5-20% of Portfolio):** Small, targeted positions to capitalize on short-to-medium term sector-specific opportunities identified by our analysis.
    -   **Cyclical Sectors:** `IYF`, `IYG`, `IYJ`, `IYC`, `IYT`, `IYR`
    -   **Defensive Sectors:** `IYH`, `IYK`, `IYZ`
    -   **Thematic/Niche:** `IBB`, `ITA`, `IYE`, `MCHI`, `IFRA`

-   **HEDGING & RISK-OFF SATELLITES (0-20% of Portfolio):** Assets used specifically for risk management.
    -   `SGOV`: Our **cash equivalent**. Capital is parked here during periods of high uncertainty.
    -   `IAU` (Gold): Hedge against inflation and extreme market stress.
    -   `TIP`: Explicit inflation protection.

### 3. The Dynamic Analysis Workflow ("Radar & Scalpel")

To efficiently use our analytical resources, we employ a two-step daily process.

1.  **The Radar (Broad Scan):**
    -   **Objective:** Identify assets with unusual activity.
    -   **Method:** A daily, post-market scan of all 30 ETFs using `yfinance` data.
    -   **Triggers:** An asset is flagged for the "Focus List" if it meets criteria such as:
        -   Price change > 2 standard deviations.
        -   Volume > 150% of 30-day average.
        -   Significant technical crossover (e.g., 50-day moving average).

2.  **The Scalpel (Deep Dive):**
    -   **Objective:** Understand the "why" behind the activity of flagged assets.
    -   **Method:** Allocate API calls (NewsAPI, LLM) ONLY to the ETFs on the Focus List.
    -   **Output:** A rich, qualitative narrative and sentiment score that complements the quantitative trigger.

### 4. Risk Management Protocol

Our primary tool for managing market-wide (systematic) risk is a rules-based protocol tied to the CBOE Volatility Index (VIX).

-   **VIX < 20 (Complacent Market):** Normal operations. Fully invested according to the Core-Satellite model.
-   **VIX 20-30 (Heightened Uncertainty):** Raise caution. Consider trimming highest-risk satellite positions. Increase monitoring frequency.
-   **VIX > 30 (High Fear):** **Risk-Off Trigger.** The model will recommend a significant reduction in equity exposure (especially high-beta satellites like `IYW`, `IJR`) and a reallocation of that capital to `SGOV`. The goal is capital preservation. We remain in this defensive posture until the VIX recedes to a safer level.