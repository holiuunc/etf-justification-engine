# ETF Justification Engine - Development Roadmap

**Project Status:** Backend Complete ✅ | Docker Setup Complete ✅ | Frontend In Progress 🔨

Last Updated: 2025-11-13

---

## 🎯 Project Overview

Build an automated ETF analysis engine that generates professional trade recommendations with complete justifications suitable for investment prospectuses.

**Key Features:**
- Daily analysis of 30 ETFs with Radar/Scalpel strategy
- VIX-based risk management
- LLM-powered news analysis (Google Gemini)
- Professional justification text generation
- Web dashboard for visualization

---

## ✅ Phase 1: Backend Configuration (COMPLETE)

**Status:** ✅ Done | **Duration:** ~2 hours

### Completed Items:
- [x] Project directory structure
- [x] ETF Universe configuration (30 ETFs with metadata)
- [x] Strategy parameters (position limits, VIX thresholds, risk allocations)
- [x] Environment settings with Pydantic
- [x] Comprehensive data models (20+ Pydantic models)
- [x] Portfolio initialization script

**Deliverables:**
- `backend/config/etf_universe.py`
- `backend/config/strategy_params.py`
- `backend/config/settings.py`
- `backend/data/models.py`
- `scripts/initialize_portfolio.py`

---

## ✅ Phase 2: Data Layer (COMPLETE)

**Status:** ✅ Done | **Duration:** ~2 hours

### Completed Items:
- [x] Market data fetcher (yfinance integration)
- [x] News data fetcher (NewsAPI integration)
- [x] VIX and benchmark data fetching
- [x] JSON file storage operations
- [x] Portfolio state management
- [x] Transaction history tracking
- [x] Cache storage utilities

**Deliverables:**
- `backend/data/data_fetcher.py`
- `backend/data/storage.py`

**Key Features:**
- Batch download for efficiency
- Retry logic with exponential backoff
- Rate limiting compliance
- Type-safe data models

---

## ✅ Phase 3: Core Analysis Engine (COMPLETE)

**Status:** ✅ Done | **Duration:** ~3 hours

### Completed Items:
- [x] Radar Scan module (technical analysis)
  - Volume spike detection
  - Price movement analysis
  - Technical indicators (SMA, RSI, MACD, Bollinger Bands)
  - Focus List generation
- [x] Risk Manager module
  - VIX-based regime detection
  - Position limit validation
  - Risk metrics calculation
  - Safe position sizing
- [x] Portfolio Engine
  - Recommendation generation
  - Allocation calculations
  - Transaction details
  - Priority and confidence scoring

**Deliverables:**
- `backend/core/radar_scan.py`
- `backend/core/risk_manager.py`
- `backend/core/portfolio_engine.py`

**Key Features:**
- Automated trigger detection across 30 ETFs
- Multi-regime risk management (4 modes)
- Professional justification generation

---

## ✅ Phase 4: Intelligence Layer (COMPLETE)

**Status:** ✅ Done | **Duration:** ~2 hours

### Completed Items:
- [x] Google Gemini LLM integration
- [x] News sentiment analysis
- [x] Theme and risk factor extraction
- [x] Scalpel Dive workflow
- [x] Justification enhancement

**Deliverables:**
- `backend/core/llm_service.py`
- `backend/core/scalpel_dive.py`

**Key Features:**
- Structured LLM prompts with JSON output
- Sentiment scoring (-1.0 to +1.0)
- Relevance filtering
- Fallback handling for API failures

---

## ✅ Phase 5: Main Orchestrator (COMPLETE)

**Status:** ✅ Done | **Duration:** ~1 hour

### Completed Items:
- [x] Complete daily analysis workflow
- [x] Comprehensive logging
- [x] Error handling and recovery
- [x] API call tracking
- [x] Execution time monitoring
- [x] Manual run utilities

**Deliverables:**
- `backend/main.py`
- `backend/requirements.txt`
- `scripts/manual_run.py`
- `SETUP.md`

**Workflow Steps:**
1. Load portfolio state
2. Fetch market data (all 30 ETFs)
3. Run Radar Scan → Focus List
4. Determine VIX-based risk mode
5. Perform Scalpel Dive (news + LLM)
6. Generate recommendations
7. Save analysis to JSON
8. Update portfolio metrics

---

## ✅ Phase 6: Docker Containerization (COMPLETE)

**Status:** ✅ Done | **Duration:** ~30 minutes

### Completed Items:
- [x] Multi-stage Dockerfile for backend
- [x] Docker Compose orchestration
- [x] Volume mounts for data persistence
- [x] .dockerignore optimization
- [x] Non-root user security
- [x] Health checks

**Deliverables:**
- `backend/Dockerfile`
- `docker-compose.yml`
- `.dockerignore`

**Key Features:**
- Optimized image size with multi-stage build
- Live code reload during development
- Data persistence via volume mounts
- Resource limits and health checks
- Easy deployment to cloud platforms

**Docker Commands:**
```bash
# Build and start
docker-compose up --build -d

# Run analysis
docker-compose exec backend python main.py

# Initialize portfolio
docker-compose exec backend python ../scripts/initialize_portfolio.py

# View logs
docker-compose logs -f backend

# Stop
docker-compose down
```

---

## 🔨 Phase 7: Frontend Implementation (IN PROGRESS)

**Status:** 🔨 In Progress | **Estimated Duration:** ~4 hours

### Planned Items:
- [ ] Initialize Vite + React + TypeScript project
- [ ] Configure Tailwind CSS
- [ ] Set up folder structure
- [ ] Create TypeScript interfaces (match backend models)
- [ ] Build API service for data fetching
- [ ] Implement core components:
  - [ ] Dashboard layout
  - [ ] PortfolioSummary (with pie chart)
  - [ ] FocusList
  - [ ] RecommendationCard
  - [ ] JustificationPanel
  - [ ] PerformanceChart (recharts)
  - [ ] RiskIndicator
  - [ ] MarketOverview
- [ ] Wire up data flow
- [ ] Styling and polish
- [ ] Responsive design

**Target Deliverables:**
- `frontend/` directory with full React app
- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/tailwind.config.js`
- `frontend/src/` with components and services

**Frontend Stack:**
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite (fast dev server + HMR)
- **Styling:** Tailwind CSS
- **Charts:** Recharts
- **State Management:** React hooks + context (no Redux needed)
- **Data Fetching:** Fetch API (with error boundaries)

### Deployment Target:
- Vercel (free tier)
- Auto-deploy from GitHub
- Fetches data from GitHub raw URLs

---

## 📋 Phase 8: Testing & Refinement (TODO)

**Status:** 📋 Planned | **Estimated Duration:** ~2 hours

### Planned Items:
- [ ] Manual backend testing
- [ ] Portfolio initialization with real data
- [ ] Full analysis run (verify all modules)
- [ ] Frontend testing with real JSON data
- [ ] Error handling verification
- [ ] Performance optimization
- [ ] Documentation review
- [ ] Edge case testing (no news, API failures, etc.)

---

## 📊 Progress Summary

| Phase | Status | Files Created | Lines of Code (Est.) |
|-------|--------|---------------|---------------------|
| 1. Backend Configuration | ✅ Complete | 5 | ~800 |
| 2. Data Layer | ✅ Complete | 2 | ~600 |
| 3. Core Analysis Engine | ✅ Complete | 3 | ~1200 |
| 4. Intelligence Layer | ✅ Complete | 2 | ~500 |
| 5. Main Orchestrator | ✅ Complete | 3 | ~600 |
| 6. Docker Setup | ✅ Complete | 3 | ~150 |
| 7. Frontend | 🔨 In Progress | 0/25 | 0/~1500 |
| 8. Testing | 📋 Planned | - | - |
| **TOTAL** | **~75% Done** | **18/43** | **3850/5350** |

---

## 🎯 Current Sprint Goals

### This Session:
1. ✅ Add Docker containerization
2. 🔨 Initialize frontend project
3. 🔨 Build core frontend components
4. 🔨 Connect frontend to backend data
5. 📋 Update SETUP.md with Docker + Frontend instructions

### Next Session:
1. Complete remaining frontend components
2. Polish UI/UX
3. Test end-to-end workflow
4. Deploy to Vercel
5. Create demo video/screenshots

---

## 🚀 Quick Start (Current State)

### Backend (Ready to Use):
```bash
# Option 1: Docker (Recommended)
docker-compose up --build -d
docker-compose exec backend python ../scripts/initialize_portfolio.py
docker-compose exec backend python main.py

# Option 2: Local Python
cd backend
pip install -r requirements.txt
python ../scripts/initialize_portfolio.py
python main.py
```

### Frontend (Coming Soon):
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## 📝 Known Issues & TODOs

### Backend:
- [ ] Add more comprehensive error handling for API failures
- [ ] Implement caching for expensive calculations
- [ ] Add unit tests (optional, not critical for course project)
- [ ] Optimize yfinance batch downloads

### Frontend:
- [ ] TBD - will track as we build

### Documentation:
- [x] Create ROADMAP.md
- [ ] Update SETUP.md with Docker instructions
- [ ] Add architecture diagram
- [ ] Create API documentation

---

## 📚 Resources & References

- **yfinance Documentation:** https://pypi.org/project/yfinance/
- **NewsAPI:** https://newsapi.org/docs
- **Google Gemini API:** https://ai.google.dev/docs
- **React + TypeScript:** https://react-typescript-cheatsheet.netlify.app/
- **Tailwind CSS:** https://tailwindcss.com/docs
- **Recharts:** https://recharts.org/en-US/

---

## 🎓 Learning Outcomes

### Technical Skills Demonstrated:
- ✅ Python backend architecture with clean separation of concerns
- ✅ Pydantic for type-safe data validation
- ✅ API integration (yfinance, NewsAPI, Gemini)
- ✅ LLM prompt engineering for structured outputs
- ✅ Docker containerization
- 🔨 React + TypeScript frontend development
- 📋 Full-stack application deployment

### Financial Domain Knowledge:
- ✅ Technical analysis (RSI, MACD, Bollinger Bands)
- ✅ Portfolio risk management (VIX-based regimes)
- ✅ Position sizing and allocation strategies
- ✅ Investment thesis development
- ✅ Prospectus writing

---

**Maintained By:** Claude Code (AI Assistant)
**Project Owner:** Hong Liu
**Course:** Econ 425 Investment Project
