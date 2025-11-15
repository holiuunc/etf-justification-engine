#!/usr/bin/env python3
"""Main Orchestrator - ETF Justification Engine

Daily analysis workflow that orchestrates all components:
1. Load current portfolio state
2. Fetch market data for all 30 ETFs
3. Run Radar Scan to identify Focus List
4. Fetch VIX and determine risk mode
5. Perform Scalpel Dive (news + LLM analysis) on Focus List
6. Generate trade recommendations
7. Save daily analysis to JSON
8. Update portfolio state

Usage:
    python backend/main.py
"""

import logging
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from config.etf_universe import get_all_tickers
from data.models import (
    DailyAnalysis, MarketOverview, PortfolioSnapshot,
    ExecutionSummary, RiskMode, MarketRegime
)
from data.storage import (
    portfolio_storage, analysis_storage
)
from data.data_fetcher import (
    MarketDataFetcher, fetch_vix, fetch_spy_returns
)
from core.radar_scan import generate_focus_list
from core.risk_manager import (
    determine_risk_mode, validate_portfolio,
    get_risk_adjustment_recommendations, log_risk_assessment
)
from core.scalpel_dive import (
    perform_scalpel_dive, log_scalpel_results, summarize_focus_list
)
from core.portfolio_engine import RecommendationEngine
from core.llm_service import get_llm_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format,
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


# ============================================================================
# Progress Tracking
# ============================================================================

def update_progress(progress: float, message: str):
    """Update analysis progress for API to read

    Args:
        progress: Progress percentage (0-100)
        message: Status message describing current step
    """
    try:
        progress_file = Path(__file__).parent.parent / "data" / "analysis_progress.json"
        progress_file.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "running": True,
            "progress": round(progress, 1),
            "message": message,
            "updated_at": datetime.now().isoformat()
        }

        with open(progress_file, 'w') as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        logger.warning(f"Failed to update progress: {e}")


# ============================================================================
# Main Analysis Workflow
# ============================================================================

def run_daily_analysis() -> DailyAnalysis:
    """Execute complete daily analysis workflow

    Returns:
        DailyAnalysis model with complete results
    """
    start_time = time.time()
    date_str = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now()

    logger.info("=" * 80)
    logger.info(f"ETF JUSTIFICATION ENGINE - Daily Analysis")
    logger.info(f"Date: {date_str}")
    logger.info(f"Time: {timestamp.strftime('%H:%M:%S %Z')}")
    logger.info("=" * 80)
    logger.info("")

    # Initialize API call counter
    api_calls = {'yfinance': 0, 'newsapi': 0, 'gemini': 0}
    errors = []
    warnings = []

    # Step 1: Load current portfolio
    update_progress(0, "Initializing analysis...")
    logger.info("[1/8] Loading current portfolio state...")
    portfolio = portfolio_storage.load()
    if portfolio is None:
        error_msg = "Portfolio state not found. Run scripts/initialize_portfolio.py first."
        logger.error(error_msg)
        errors.append(error_msg)
        raise RuntimeError(error_msg)

    logger.info(f"  Portfolio value: ${portfolio.total_value:,.2f}")
    logger.info(f"  Positions: {len(portfolio.positions)}")
    update_progress(12.5, "Portfolio loaded successfully")
    logger.info("")

    # Step 2: Fetch market data for all 30 ETFs
    update_progress(12.5, "Fetching market data for 30 ETFs...")
    logger.info("[2/8] Fetching market data for all 30 ETFs...")
    tickers = get_all_tickers()
    market_fetcher = MarketDataFetcher()

    market_data = market_fetcher.fetch_etf_data(tickers)
    api_calls['yfinance'] += 1

    if not market_data:
        error_msg = "Failed to fetch market data"
        logger.error(error_msg)
        errors.append(error_msg)

    # Calculate PriceData for each ticker
    price_data_dict = {}
    for ticker, df in market_data.items():
        if df is not None and not df.empty:
            price_data = market_fetcher.calculate_price_data(ticker, df)
            if price_data:
                price_data_dict[ticker] = price_data

    logger.info(f"  Successfully fetched data for {len(price_data_dict)} ETFs")
    update_progress(25, f"Market data fetched ({len(price_data_dict)} ETFs)")
    logger.info("")

    # Step 3: Run Radar Scan
    update_progress(25, "Running Radar Scan (technical analysis)...")
    logger.info("[3/8] Running Radar Scan to identify Focus List...")
    focus_list = generate_focus_list(market_data, price_data_dict)
    logger.info(f"  Focus List: {len(focus_list)} ETFs flagged")
    for item in focus_list:
        logger.info(f"    - {item.ticker}: {item.trigger_description}")
    update_progress(37.5, f"Radar Scan complete ({len(focus_list)} ETFs flagged)")
    logger.info("")

    # Step 4: Fetch VIX and determine risk mode
    update_progress(37.5, "Analyzing market risk (VIX)...")
    logger.info("[4/8] Fetching VIX and determining risk mode...")
    vix_level, vix_5d_avg = fetch_vix()
    api_calls['yfinance'] += 1

    risk_mode, risk_description = determine_risk_mode(vix_level, vix_5d_avg)
    logger.info(f"  VIX Level: {vix_level:.2f}")
    logger.info(f"  Risk Mode: {risk_mode.value}")
    logger.info(f"  {risk_description}")
    update_progress(50, f"Risk mode determined: {risk_mode.value}")
    logger.info("")

    # Get SPY returns for market overview
    spy_return_1d, spy_return_5d = fetch_spy_returns()
    api_calls['yfinance'] += 1

    # Determine market regime (simple logic)
    if spy_return_5d > 0.02:
        market_regime = MarketRegime.BULL
    elif spy_return_5d < -0.02:
        market_regime = MarketRegime.BEAR
    else:
        market_regime = MarketRegime.SIDEWAYS

    # Create market overview
    market_overview = MarketOverview(
        vix_level=vix_level,
        vix_change_pct=((vix_level - vix_5d_avg) / vix_5d_avg) if vix_5d_avg > 0 else 0.0,
        vix_5d_avg=vix_5d_avg,
        risk_mode=risk_mode,
        sp500_close=0.0,  # Would fetch from SPY data
        sp500_return_1d=spy_return_1d,
        sp500_return_5d=spy_return_5d,
        market_regime=market_regime,
        key_macro_events=[]  # Would be manually curated or fetched from calendar API
    )

    # Validate portfolio against risk parameters
    log_risk_assessment(risk_mode, vix_level, portfolio)

    # Step 5: Perform Scalpel Dive (news + LLM analysis)
    if focus_list and settings.enable_news_analysis and settings.enable_llm_analysis:
        update_progress(50, f"Performing Scalpel Dive ({len(focus_list)} ETFs)...")
        logger.info("[5/8] Performing Scalpel Dive on Focus List...")
        enriched_focus_list = perform_scalpel_dive(focus_list)
        api_calls['newsapi'] += len(focus_list)
        api_calls['gemini'] += len(focus_list)

        log_scalpel_results(enriched_focus_list)
        focus_list = enriched_focus_list
        update_progress(62.5, "Scalpel Dive complete (news + LLM analysis)")
    else:
        logger.info("[5/8] Skipping Scalpel Dive (disabled or empty Focus List)")
        if not focus_list:
            warnings.append("Empty Focus List - no ETFs triggered alerts")
        update_progress(62.5, "Scalpel Dive skipped")

    logger.info("")

    # Step 6: Generate trade recommendations
    update_progress(62.5, "Generating trade recommendations...")
    logger.info("[6/8] Generating trade recommendations...")
    rec_engine = RecommendationEngine(portfolio, risk_mode)
    recommendations = rec_engine.generate_recommendations(focus_list)

    logger.info(f"  Generated {len(recommendations)} recommendations:")
    for rec in recommendations:
        logger.info(f"    - {rec.ticker}: {rec.action.value} (priority: {rec.priority.value}, confidence: {rec.confidence:.0%})")
    update_progress(75, f"{len(recommendations)} recommendations generated")
    logger.info("")

    # Step 7: Create portfolio snapshot
    update_progress(75, "Creating portfolio snapshot...")
    logger.info("[7/8] Creating portfolio snapshot...")
    portfolio_snapshot = PortfolioSnapshot(
        total_value=portfolio.total_value,
        daily_return_pct=portfolio.daily_return_pct,
        total_return_pct=portfolio.total_return_pct,
        sharpe_ratio_30d=portfolio.risk_metrics.sharpe_ratio_30d,
        max_drawdown=portfolio.risk_metrics.max_drawdown,
        days_since_inception=30,  # Would calculate from start date
        allocation_breakdown={
            'core': portfolio.allocation_breakdown.core,
            'satellites': portfolio.allocation_breakdown.major_satellites + portfolio.allocation_breakdown.tactical_satellites,
            'equity': sum(p.weight for t, p in portfolio.positions.items()),
            'fixed_income': 0.05,  # Simplified
            'cash_equivalents': 0.0
        },
        top_performers_1d=[],  # Would calculate from positions
        top_performers_mtd=[]
    )

    # Step 8: Create execution summary
    execution_time = time.time() - start_time
    update_progress(87.5, "Saving analysis results...")
    logger.info(f"[8/8] Finalizing daily analysis...")

    # Determine analysis quality
    if len(errors) > 0:
        quality = "low"
    elif len(warnings) > 1:
        quality = "medium"
    else:
        quality = "high"

    execution_summary = ExecutionSummary(
        analysis_quality=quality,
        focus_list_count=len(focus_list),
        recommendations_count=len(recommendations),
        api_calls_made=api_calls,
        errors=errors,
        warnings=warnings
    )

    # Create complete daily analysis
    daily_analysis = DailyAnalysis(
        date=date_str,
        timestamp=timestamp,
        execution_time_seconds=round(execution_time, 2),
        market_overview=market_overview,
        focus_list=focus_list,
        recommendations=recommendations,
        portfolio_snapshot=portfolio_snapshot,
        execution_summary=execution_summary
    )

    # Save to file
    logger.info(f"  Saving analysis to data/analysis/{date_str}.json...")
    success = analysis_storage.save(daily_analysis)

    if success:
        logger.info("  ✓ Analysis saved successfully")
        update_progress(100, "Analysis complete!")
    else:
        errors.append("Failed to save analysis file")
        logger.error("  ✗ Failed to save analysis")
        update_progress(100, "Analysis complete (with errors)")

    # Log summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("ANALYSIS COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Execution Time: {execution_time:.2f}s")
    logger.info(f"Analysis Quality: {quality.upper()}")
    logger.info(f"Focus List: {len(focus_list)} ETFs")
    logger.info(f"Recommendations: {len(recommendations)}")
    logger.info(f"API Calls: yfinance={api_calls['yfinance']}, newsapi={api_calls['newsapi']}, gemini={api_calls['gemini']}")

    if errors:
        logger.warning(f"Errors: {len(errors)}")
        for error in errors:
            logger.warning(f"  - {error}")

    if warnings:
        logger.info(f"Warnings: {len(warnings)}")
        for warning in warnings:
            logger.info(f"  - {warning}")

    logger.info("=" * 80)
    logger.info("")

    return daily_analysis


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    try:
        # Validate configuration
        is_valid, config_errors = settings.validate_configuration()
        if not is_valid:
            logger.error("Configuration errors detected:")
            for error in config_errors:
                logger.error(f"  - {error}")
            sys.exit(1)

        # Test LLM connection (optional)
        if settings.enable_llm_analysis:
            llm_service = get_llm_service()
            if llm_service.test_connection():
                logger.info("✓ Gemini API connection verified")
            else:
                logger.warning("⚠ Gemini API connection failed - continuing without LLM")

        # Run daily analysis
        daily_analysis = run_daily_analysis()

        # Success
        logger.info("Daily analysis completed successfully!")
        sys.exit(0)

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(130)

    except Exception as e:
        logger.error(f"Fatal error during analysis: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
