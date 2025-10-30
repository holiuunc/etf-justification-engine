# Econ 425 ETF Investment Advisor

## Overview

This project is a sophisticated web-based decision-support tool for the Econ 425 Investment Project. It transforms raw market data and news into actionable, justifiable investment strategies for a portfolio limited to 30 specific ETFs. The application's primary goal is not just to recommend trades, but to generate the deep analytical narrative required for the project's graded prospectuses.

The system operates on an end-of-day (EOD) basis, running a comprehensive analysis after market close to prepare a strategic plan for the following morning.

---

## Core Features

-   **Dynamic Tiered Analysis:** Implements a "Radar & Scalpel" model. It performs a lightweight daily scan on all 30 ETFs and automatically allocates deep-dive resources (API calls for news and sentiment) only to the most active and relevant assets.
-   **LLM-Powered News Summarization:** Leverages a Large Language Model (LLM) to process daily news, providing qualitative sentiment analysis and generating concise, human-readable briefings that explain market movements.
-   **Core-Satellite Strategy Engine:** The advisor's logic is built on a professional portfolio management model, balancing a stable core (IVV, AGG) with tactical satellite positions to express specific market views.
-   **Data-Driven Risk Management:** Automatically monitors market volatility (via the VIX index) and recommends moving to cash-equivalent assets (SGOV) during periods of extreme market fear.
-   **$0 Budget Architecture:** The entire application is designed to run on the free tiers of modern cloud services and APIs, incurring no financial cost.

---

## The Strategy

The application's investment philosophy is centered around a **Moderate Growth** mandate. The goal is to achieve strong risk-adjusted returns through disciplined, data-driven decisions. The strategy is detailed further in `STRATEGY.md`, but its key pillars are:

1.  **Core-Satellite Allocation:** A majority of the portfolio remains in broad market index funds, providing stability.
2.  **Macro-Informed Tilts:** The system makes tactical adjustments based on macroeconomic data (inflation, interest rates).
3.  **Justification Over Prediction:** Every recommended action is paired with a clear "why," combining both quantitative data and qualitative news analysis.

---

## Tech Stack & Architecture

| Component          | Technology / Service                      | Purpose                                |
| ------------------ | ----------------------------------------- | -------------------------------------- |
| **Frontend**       | React (Vite)                              | User Interface & Data Visualization    |
| **Backend**        | Python (Flask/FastAPI)                    | Data Analysis, API Logic, LLM Gateway  |
| **Hosting**        | Vercel (Frontend), Render (Backend)       | $0 Cost Deployment                     |
| **Price Data API** | `yfinance` Python Library                 | Bulk historical price/volume data      |
| **News Data API**  | NewsAPI.org                               | Structured news articles               |
| **LLM Provider**   | Google AI Studio (Gemini API)             | News summarization & sentiment analysis|

### System Workflow (End-of-Day)

1.  **4:30 PM ET:** The Python backend is triggered.
2.  **Data Ingestion:** Pulls closing price/volume for all 30 ETFs using `yfinance`.
3.  **Radar Scan:** Identifies ETFs with unusual price or volume activity to create a daily "Focus List".
4.  **Scalpel Dive:** For the Focus List ETFs, makes targeted API calls to NewsAPI.org.
5.  **LLM Analysis:** Sends news articles to the Gemini API for summarization and sentiment scoring.
6.  **Strategy Output:** Generates a daily briefing, trade recommendations, and justifications.
7.  **Frontend Display:** The React app fetches and displays this analysis for the user's morning review.

---

## Setup & Installation

**Prerequisites:**
-   Node.js and npm
-   Python 3.8+ and pip
-   Git

**1. Clone the repository:**
```bash
git clone https://github.com/your-username/econ425-advisor.git
cd econ425-advisor