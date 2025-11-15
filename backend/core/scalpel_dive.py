"""Scalpel Dive Module

Implements the "Scalpel" component of the Radar/Scalpel strategy.
Performs deep analysis on Focus List ETFs by fetching news, analyzing
sentiment with LLM, and enriching recommendations with qualitative evidence.
"""

import logging
from typing import List

from config.etf_universe import get_etf_info
from config.strategy_params import NEWS_LLM_SETTINGS
from data.models import FocusListItem, NewsAnalysis
from data.data_fetcher import NewsDataFetcher
from core.llm_service import get_llm_service

logger = logging.getLogger(__name__)


# ============================================================================
# Scalpel Dive Analysis
# ============================================================================

def perform_scalpel_dive(focus_list: List[FocusListItem]) -> List[FocusListItem]:
    """Perform deep analysis on all Focus List items

    Fetches news and uses LLM to analyze sentiment and extract themes.
    Enriches each FocusListItem with NewsAnalysis.

    Args:
        focus_list: List of FocusListItem models from Radar Scan

    Returns:
        Enriched list of FocusListItem models with news analysis
    """
    logger.info(f"Performing Scalpel Dive on {len(focus_list)} ETFs...")

    news_fetcher = NewsDataFetcher()
    llm_service = get_llm_service()

    enriched_list = []

    for focus_item in focus_list:
        ticker = focus_item.ticker
        logger.info(f"  Analyzing {ticker}...")

        # Get ETF info
        etf_info = get_etf_info(ticker)
        etf_name = etf_info['name']

        # Fetch news
        articles = news_fetcher.fetch_news(
            ticker=ticker,
            etf_name=etf_name,
            lookback_days=NEWS_LLM_SETTINGS['news_lookback_days'],
            max_articles=NEWS_LLM_SETTINGS['news_articles_per_etf']
        )

        if not articles:
            logger.warning(f"  No news found for {ticker} - using technical analysis only")
            # Create empty news analysis
            news_analysis = NewsAnalysis(
                ticker=ticker,
                news_count=0,
                sentiment_score=0.0,
                relevance_score=0.0,
                headlines=[],
                llm_summary="No recent news available for analysis",
                key_themes=[],
                risk_factors=[]
            )
        else:
            # Analyze news with LLM
            logger.info(f"  Found {len(articles)} articles, analyzing with LLM...")
            llm_result = llm_service.analyze_news(ticker, etf_name, articles)

            if llm_result:
                # Create NewsAnalysis from LLM result
                news_analysis = NewsAnalysis(
                    ticker=ticker,
                    news_count=len(articles),
                    sentiment_score=llm_result['sentiment_score'],
                    relevance_score=llm_result['relevance_score'],
                    headlines=[article.title for article in articles[:5]],
                    llm_summary=llm_result['summary'],
                    key_themes=llm_result['key_themes'],
                    risk_factors=llm_result['risk_factors']
                )
                logger.info(f"  ✓ {ticker} analysis complete (sentiment: {news_analysis.sentiment_score:+.2f})")
            else:
                # LLM failed, create basic analysis
                news_analysis = NewsAnalysis(
                    ticker=ticker,
                    news_count=len(articles),
                    sentiment_score=0.0,
                    relevance_score=0.5,
                    headlines=[article.title for article in articles[:5]],
                    llm_summary="LLM analysis unavailable",
                    key_themes=[],
                    risk_factors=[]
                )
                logger.warning(f"  LLM analysis failed for {ticker}")

        # Enrich focus item with news analysis
        focus_item.news_analysis = news_analysis
        enriched_list.append(focus_item)

    logger.info(f"Scalpel Dive complete: {len(enriched_list)} ETFs enriched with news analysis")
    return enriched_list


def analyze_single_etf(ticker: str) -> NewsAnalysis:
    """Perform Scalpel Dive analysis on a single ETF

    Useful for manual analysis outside the daily workflow.

    Args:
        ticker: ETF ticker symbol

    Returns:
        NewsAnalysis model
    """
    logger.info(f"Performing deep analysis on {ticker}...")

    # Get ETF info
    etf_info = get_etf_info(ticker)
    if not etf_info:
        logger.error(f"Unknown ticker: {ticker}")
        return None

    etf_name = etf_info['name']

    # Fetch news
    news_fetcher = NewsDataFetcher()
    articles = news_fetcher.fetch_news(
        ticker=ticker,
        etf_name=etf_name,
        lookback_days=NEWS_LLM_SETTINGS['news_lookback_days'],
        max_articles=NEWS_LLM_SETTINGS['news_articles_per_etf']
    )

    if not articles:
        logger.warning(f"No news found for {ticker}")
        return NewsAnalysis(
            ticker=ticker,
            news_count=0,
            sentiment_score=0.0,
            relevance_score=0.0,
            headlines=[],
            llm_summary="No recent news available",
            key_themes=[],
            risk_factors=[]
        )

    # Analyze with LLM
    llm_service = get_llm_service()
    llm_result = llm_service.analyze_news(ticker, etf_name, articles)

    if not llm_result:
        return NewsAnalysis(
            ticker=ticker,
            news_count=len(articles),
            sentiment_score=0.0,
            relevance_score=0.5,
            headlines=[article.title for article in articles[:5]],
            llm_summary="LLM analysis failed",
            key_themes=[],
            risk_factors=[]
        )

    # Create NewsAnalysis
    return NewsAnalysis(
        ticker=ticker,
        news_count=len(articles),
        sentiment_score=llm_result['sentiment_score'],
        relevance_score=llm_result['relevance_score'],
        headlines=[article.title for article in articles[:5]],
        llm_summary=llm_result['summary'],
        key_themes=llm_result['key_themes'],
        risk_factors=llm_result['risk_factors']
    )


def filter_by_relevance(
    focus_list: List[FocusListItem],
    min_relevance: float = 0.3
) -> List[FocusListItem]:
    """Filter Focus List by news relevance score

    Args:
        focus_list: List of FocusListItem models
        min_relevance: Minimum relevance score (0-1)

    Returns:
        Filtered list
    """
    filtered = [
        item for item in focus_list
        if item.news_analysis and item.news_analysis.relevance_score >= min_relevance
    ]

    if len(filtered) < len(focus_list):
        logger.info(
            f"Filtered {len(focus_list) - len(filtered)} items below "
            f"{min_relevance:.0%} relevance threshold"
        )

    return filtered


def prioritize_by_sentiment(focus_list: List[FocusListItem]) -> List[FocusListItem]:
    """Re-prioritize Focus List by news sentiment

    Args:
        focus_list: List of FocusListItem models

    Returns:
        Sorted list (strongest signals first)
    """
    # Sort by absolute sentiment score (strongest conviction, positive or negative)
    sorted_list = sorted(
        focus_list,
        key=lambda x: abs(x.news_analysis.sentiment_score) if x.news_analysis else 0,
        reverse=True
    )

    logger.info("Focus List re-prioritized by sentiment strength")
    return sorted_list


def summarize_focus_list(focus_list: List[FocusListItem]) -> Dict[str, any]:
    """Generate summary statistics for Focus List

    Args:
        focus_list: List of FocusListItem models

    Returns:
        Summary dict
    """
    if not focus_list:
        return {
            'total_items': 0,
            'avg_sentiment': 0.0,
            'avg_relevance': 0.0,
            'bullish_count': 0,
            'bearish_count': 0,
            'neutral_count': 0
        }

    sentiments = [
        item.news_analysis.sentiment_score
        for item in focus_list if item.news_analysis
    ]

    relevances = [
        item.news_analysis.relevance_score
        for item in focus_list if item.news_analysis
    ]

    bullish = sum(1 for s in sentiments if s > 0.3)
    bearish = sum(1 for s in sentiments if s < -0.3)
    neutral = len(sentiments) - bullish - bearish

    return {
        'total_items': len(focus_list),
        'avg_sentiment': round(sum(sentiments) / len(sentiments), 3) if sentiments else 0.0,
        'avg_relevance': round(sum(relevances) / len(relevances), 3) if relevances else 0.0,
        'bullish_count': bullish,
        'bearish_count': bearish,
        'neutral_count': neutral,
        'has_news': sum(1 for item in focus_list if item.news_analysis and item.news_analysis.news_count > 0)
    }


def log_scalpel_results(focus_list: List[FocusListItem]):
    """Log detailed Scalpel Dive results

    Args:
        focus_list: Enriched focus list
    """
    logger.info("=" * 60)
    logger.info("SCALPEL DIVE RESULTS")
    logger.info("=" * 60)

    summary = summarize_focus_list(focus_list)
    logger.info(f"Total ETFs Analyzed: {summary['total_items']}")
    logger.info(f"Average Sentiment: {summary['avg_sentiment']:+.2f}")
    logger.info(f"Average Relevance: {summary['avg_relevance']:.2f}")
    logger.info(f"Bullish: {summary['bullish_count']}, Bearish: {summary['bearish_count']}, Neutral: {summary['neutral_count']}")
    logger.info(f"ETFs with News: {summary['has_news']}/{summary['total_items']}")
    logger.info("")

    logger.info("Individual Results:")
    for item in focus_list:
        if item.news_analysis:
            sentiment_label = (
                "Bullish" if item.news_analysis.sentiment_score > 0.3 else
                "Bearish" if item.news_analysis.sentiment_score < -0.3 else
                "Neutral"
            )
            logger.info(
                f"  {item.ticker}: {sentiment_label} "
                f"(sentiment: {item.news_analysis.sentiment_score:+.2f}, "
                f"relevance: {item.news_analysis.relevance_score:.2f}, "
                f"articles: {item.news_analysis.news_count})"
            )

    logger.info("=" * 60)
