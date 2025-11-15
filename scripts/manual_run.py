#!/usr/bin/env python3
"""Manual Run Script

Convenience script for running the analysis engine locally for testing.
Provides options for single ticker analysis and other testing scenarios.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

import argparse
import logging
from datetime import datetime

from config.settings import settings
from config.etf_universe import get_all_tickers, validate_ticker
from data.storage import analysis_storage, portfolio_storage
from core.scalpel_dive import analyze_single_etf
from main import run_daily_analysis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def run_full_analysis():
    """Run complete daily analysis"""
    logger.info("Running full daily analysis...")
    try:
        analysis = run_daily_analysis()
        logger.info(f"Analysis complete! Results saved to: data/analysis/{analysis.date}.json")
        return 0
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return 1


def analyze_ticker(ticker: str):
    """Analyze a single ticker"""
    if not validate_ticker(ticker):
        logger.error(f"Invalid ticker: {ticker}")
        logger.info(f"Valid tickers: {', '.join(get_all_tickers())}")
        return 1

    logger.info(f"Analyzing {ticker}...")
    try:
        news_analysis = analyze_single_etf(ticker)

        print(f"\n{'=' * 60}")
        print(f"News Analysis for {ticker}")
        print(f"{'=' * 60}")
        print(f"News Count: {news_analysis.news_count}")
        print(f"Sentiment Score: {news_analysis.sentiment_score:+.2f}/1.0")
        print(f"Relevance Score: {news_analysis.relevance_score:.2f}/1.0")
        print(f"\nSummary:")
        print(f"  {news_analysis.llm_summary}")
        print(f"\nKey Themes:")
        for theme in news_analysis.key_themes:
            print(f"  - {theme}")
        print(f"\nRisk Factors:")
        for risk in news_analysis.risk_factors:
            print(f"  - {risk}")
        print(f"\nHeadlines:")
        for headline in news_analysis.headlines:
            print(f"  - {headline}")
        print(f"{'=' * 60}\n")

        return 0

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return 1


def show_portfolio():
    """Display current portfolio state"""
    logger.info("Loading portfolio...")
    portfolio = portfolio_storage.load()

    if portfolio is None:
        logger.error("Portfolio not found. Run scripts/initialize_portfolio.py first.")
        return 1

    print(f"\n{'=' * 60}")
    print(f"Portfolio Summary (as of {portfolio.as_of})")
    print(f"{'=' * 60}")
    print(f"Total Value: ${portfolio.total_value:,.2f}")
    print(f"Total Return: {portfolio.total_return_pct:+.2%}")
    print(f"Cash Balance: ${portfolio.cash_balance:,.2f}")
    print(f"Positions: {len(portfolio.positions)}")
    print(f"\nPositions:")
    print(f"  {'Ticker':<8} {'Shares':>8} {'Price':>10} {'Value':>12} {'Weight':>8} {'Gain':>10}")
    print(f"  {'-' * 8} {'-' * 8} {'-' * 10} {'-' * 12} {'-' * 8} {'-' * 10}")

    for ticker, pos in portfolio.positions.items():
        print(f"  {ticker:<8} {pos.shares:>8} ${pos.current_price:>9.2f} ${pos.market_value:>11.2f} {pos.weight:>7.1%} {pos.unrealized_gain:>+9.2f}")

    print(f"\nAllocation:")
    print(f"  Core: {portfolio.allocation_breakdown.core:.1%}")
    print(f"  Major Satellites: {portfolio.allocation_breakdown.major_satellites:.1%}")
    print(f"  Tactical Satellites: {portfolio.allocation_breakdown.tactical_satellites:.1%}")
    print(f"  Hedging: {portfolio.allocation_breakdown.hedging:.1%}")
    print(f"{'=' * 60}\n")

    return 0


def show_latest_analysis():
    """Display latest analysis results"""
    logger.info("Loading latest analysis...")
    analysis = analysis_storage.load_latest()

    if analysis is None:
        logger.error("No analysis found. Run analysis first.")
        return 1

    print(f"\n{'=' * 60}")
    print(f"Latest Analysis ({analysis.date})")
    print(f"{'=' * 60}")
    print(f"Execution Time: {analysis.execution_time_seconds:.2f}s")
    print(f"Quality: {analysis.execution_summary.analysis_quality}")
    print(f"\nMarket Overview:")
    print(f"  VIX: {analysis.market_overview.vix_level:.2f}")
    print(f"  Risk Mode: {analysis.market_overview.risk_mode.value}")
    print(f"  S&P 500 1D: {analysis.market_overview.sp500_return_1d:+.2%}")
    print(f"  Market Regime: {analysis.market_overview.market_regime.value}")
    print(f"\nFocus List ({len(analysis.focus_list)} ETFs):")
    for item in analysis.focus_list:
        sentiment_str = f" (sentiment: {item.news_analysis.sentiment_score:+.2f})" if item.news_analysis else ""
        print(f"  - {item.ticker}: {item.trigger_description}{sentiment_str}")

    print(f"\nRecommendations ({len(analysis.recommendations)}):")
    for rec in analysis.recommendations:
        print(f"  - {rec.ticker}: {rec.action.value} (priority: {rec.priority.value}, confidence: {rec.confidence:.0%})")

    print(f"{'=' * 60}\n")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Manual run script for ETF Justification Engine"
    )

    parser.add_argument(
        'command',
        choices=['run', 'analyze', 'portfolio', 'latest'],
        help='Command to execute'
    )

    parser.add_argument(
        '--ticker',
        help='Ticker symbol for analyze command'
    )

    args = parser.parse_args()

    if args.command == 'run':
        return run_full_analysis()

    elif args.command == 'analyze':
        if not args.ticker:
            logger.error("--ticker required for analyze command")
            return 1
        return analyze_ticker(args.ticker.upper())

    elif args.command == 'portfolio':
        return show_portfolio()

    elif args.command == 'latest':
        return show_latest_analysis()


if __name__ == "__main__":
    sys.exit(main())
