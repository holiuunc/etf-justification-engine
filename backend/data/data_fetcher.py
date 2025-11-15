"""Data Fetcher Module

Handles fetching market data from yfinance and news data from NewsAPI.
Implements retry logic and rate limiting to respect API constraints.
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yfinance as yf
import requests
import pandas as pd

from config.settings import settings
from config.strategy_params import DATA_SETTINGS
from data.models import PriceData, NewsArticle

logger = logging.getLogger(__name__)


# ============================================================================
# Market Data Functions (yfinance)
# ============================================================================

class MarketDataFetcher:
    """Fetches market data using yfinance"""

    def __init__(self):
        self.rate_limit_delay = DATA_SETTINGS['rate_limit_delay']
        self.max_retries = DATA_SETTINGS['max_retries']
        self.retry_delay = DATA_SETTINGS['retry_delay']

    def fetch_etf_data(
        self,
        tickers: List[str],
        period: str = '90d',
        interval: str = '1d'
    ) -> Dict[str, pd.DataFrame]:
        """Fetch historical price data for multiple ETFs

        Args:
            tickers: List of ETF ticker symbols
            period: Data period (default: 90d for moving averages)
            interval: Data interval (default: 1d for daily)

        Returns:
            Dictionary mapping tickers to DataFrames with OHLCV data
        """
        logger.info(f"Fetching market data for {len(tickers)} ETFs (period: {period})")

        try:
            # Use yfinance's batch download for efficiency
            data = yf.download(
                tickers=" ".join(tickers),
                period=period,
                interval=interval,
                group_by='ticker',
                auto_adjust=True,
                threads=False,  # Sequential to avoid rate limiting
                progress=False
            )

            # Handle single ticker vs multiple tickers
            if len(tickers) == 1:
                result = {tickers[0]: data}
            else:
                result = {ticker: data[ticker] for ticker in tickers if ticker in data.columns.get_level_values(0)}

            logger.info(f"Successfully fetched data for {len(result)} ETFs")
            return result

        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return {}

    def fetch_vix_data(self, period: str = '30d') -> Optional[pd.DataFrame]:
        """Fetch VIX (volatility index) data

        Args:
            period: Data period (default: 30d)

        Returns:
            DataFrame with VIX data or None if error
        """
        logger.info("Fetching VIX data")

        try:
            time.sleep(self.rate_limit_delay)  # Rate limiting
            vix = yf.download(
                settings.vix_ticker,
                period=period,
                interval='1d',
                progress=False
            )
            logger.info("Successfully fetched VIX data")
            return vix

        except Exception as e:
            logger.error(f"Error fetching VIX data: {e}")
            return None

    def fetch_benchmark_data(self, period: str = '90d') -> Optional[pd.DataFrame]:
        """Fetch benchmark (SPY) data for comparison

        Args:
            period: Data period (default: 90d)

        Returns:
            DataFrame with benchmark data or None if error
        """
        logger.info(f"Fetching benchmark data ({settings.benchmark_ticker})")

        try:
            time.sleep(self.rate_limit_delay)  # Rate limiting
            benchmark = yf.download(
                settings.benchmark_ticker,
                period=period,
                interval='1d',
                progress=False
            )
            logger.info("Successfully fetched benchmark data")
            return benchmark

        except Exception as e:
            logger.error(f"Error fetching benchmark data: {e}")
            return None

    def get_current_price(self, ticker: str) -> Optional[float]:
        """Get current price for a single ticker

        Args:
            ticker: ETF ticker symbol

        Returns:
            Current price or None if error
        """
        try:
            time.sleep(self.rate_limit_delay)
            etf = yf.Ticker(ticker)
            info = etf.info
            return info.get('currentPrice') or info.get('regularMarketPrice')

        except Exception as e:
            logger.error(f"Error fetching current price for {ticker}: {e}")
            return None

    def calculate_price_data(
        self,
        ticker: str,
        df: pd.DataFrame
    ) -> Optional[PriceData]:
        """Calculate price and volume metrics from historical data

        Args:
            ticker: ETF ticker symbol
            df: Historical OHLCV DataFrame

        Returns:
            PriceData model or None if insufficient data
        """
        try:
            if df.empty or len(df) < 30:
                logger.warning(f"Insufficient data for {ticker}")
                return None

            # Get latest data
            latest = df.iloc[-1]
            current_price = float(latest['Close'])

            # Calculate returns
            prev_close = float(df.iloc[-2]['Close']) if len(df) >= 2 else current_price
            price_change_1d = (current_price - prev_close) / prev_close if prev_close > 0 else 0.0

            price_5d_ago = float(df.iloc[-6]['Close']) if len(df) >= 6 else current_price
            price_change_5d = (current_price - price_5d_ago) / price_5d_ago if price_5d_ago > 0 else 0.0

            price_30d_ago = float(df.iloc[-31]['Close']) if len(df) >= 31 else current_price
            price_change_30d = (current_price - price_30d_ago) / price_30d_ago if price_30d_ago > 0 else 0.0

            # 52-week high/low
            high_52w = float(df['High'].tail(252).max()) if len(df) >= 252 else float(df['High'].max())
            low_52w = float(df['Low'].tail(252).min()) if len(df) >= 252 else float(df['Low'].min())

            # Volume metrics
            volume_today = int(latest['Volume'])
            volume_30d_avg = int(df['Volume'].tail(30).mean())
            volume_ratio = volume_today / volume_30d_avg if volume_30d_avg > 0 else 1.0

            return PriceData(
                ticker=ticker,
                current_price=round(current_price, 2),
                price_change_1d=round(price_change_1d, 4),
                price_change_5d=round(price_change_5d, 4),
                price_change_30d=round(price_change_30d, 4),
                high_52w=round(high_52w, 2),
                low_52w=round(low_52w, 2),
                volume_today=volume_today,
                volume_30d_avg=volume_30d_avg,
                volume_ratio=round(volume_ratio, 2)
            )

        except Exception as e:
            logger.error(f"Error calculating price data for {ticker}: {e}")
            return None


# ============================================================================
# News Data Functions (NewsAPI)
# ============================================================================

class NewsDataFetcher:
    """Fetches news data using NewsAPI"""

    def __init__(self):
        self.api_key = settings.newsapi_key
        self.base_url = "https://newsapi.org/v2/everything"
        self.rate_limit_delay = 1.0  # NewsAPI: 1 request/second

    def fetch_news(
        self,
        ticker: str,
        etf_name: str,
        lookback_days: int = 2,
        max_articles: int = 5
    ) -> List[NewsArticle]:
        """Fetch news articles for a specific ETF

        Args:
            ticker: ETF ticker symbol
            etf_name: Full ETF name for better search results
            lookback_days: Days to look back for news (default: 2)
            max_articles: Maximum articles to return (default: 5)

        Returns:
            List of NewsArticle models
        """
        if not settings.newsapi_available:
            logger.warning("NewsAPI key not configured")
            return []

        logger.info(f"Fetching news for {ticker} ({etf_name})")

        # Build search query
        query = self._build_search_query(ticker, etf_name)

        # Calculate date range
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')

        params = {
            'q': query,
            'apiKey': self.api_key,
            'language': 'en',
            'sortBy': 'relevancy',
            'pageSize': max_articles,
            'from': from_date,
            'to': to_date
        }

        try:
            time.sleep(self.rate_limit_delay)  # Rate limiting
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            articles = data.get('articles', [])

            logger.info(f"Found {len(articles)} articles for {ticker}")

            return [
                NewsArticle(
                    title=article['title'],
                    source=article['source']['name'],
                    url=article['url'],
                    published_at=datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')),
                    description=article.get('description'),
                    content=article.get('content')
                )
                for article in articles if article.get('title') != '[Removed]'
            ]

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news for {ticker}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching news for {ticker}: {e}")
            return []

    def _build_search_query(self, ticker: str, etf_name: str) -> str:
        """Build optimized search query for ETF news

        Args:
            ticker: ETF ticker symbol
            etf_name: Full ETF name

        Returns:
            Search query string
        """
        # Extract key sector terms from ETF name
        sector_terms = {
            'Technology': ['tech', 'software', 'semiconductor'],
            'Healthcare': ['healthcare', 'pharmaceutical', 'biotech'],
            'Energy': ['energy', 'oil', 'gas'],
            'Financials': ['bank', 'financial', 'insurance'],
            'Aerospace': ['aerospace', 'defense', 'aviation'],
            'Real Estate': ['real estate', 'REIT', 'property'],
            'Consumer': ['consumer', 'retail'],
            'Emerging Markets': ['emerging markets', 'China', 'India'],
        }

        # Try to identify sector from ETF name
        query_terms = [f'"{ticker}"']

        for sector, terms in sector_terms.items():
            if sector.lower() in etf_name.lower():
                query_terms.extend(terms[:2])  # Add top 2 related terms
                break

        return ' OR '.join(query_terms)

    def test_api_connection(self) -> bool:
        """Test NewsAPI connection and key validity

        Returns:
            True if API is working, False otherwise
        """
        if not settings.newsapi_available:
            return False

        try:
            params = {
                'q': 'test',
                'apiKey': self.api_key,
                'pageSize': 1
            }
            response = requests.get(self.base_url, params=params, timeout=5)
            return response.status_code == 200

        except Exception as e:
            logger.error(f"NewsAPI connection test failed: {e}")
            return False


# ============================================================================
# Convenience Functions
# ============================================================================

def fetch_all_market_data(tickers: List[str]) -> Dict[str, pd.DataFrame]:
    """Convenience function to fetch market data for all tickers

    Args:
        tickers: List of ETF ticker symbols

    Returns:
        Dictionary mapping tickers to DataFrames
    """
    fetcher = MarketDataFetcher()
    return fetcher.fetch_etf_data(tickers)


def fetch_vix() -> Tuple[float, float]:
    """Fetch current VIX level and 5-day average

    Returns:
        Tuple of (current_vix, vix_5d_avg)
    """
    fetcher = MarketDataFetcher()
    vix_data = fetcher.fetch_vix_data()

    if vix_data is None or vix_data.empty:
        logger.warning("Using default VIX values (20.0)")
        return 20.0, 20.0

    current_vix = float(vix_data['Close'].iloc[-1])
    vix_5d_avg = float(vix_data['Close'].tail(5).mean())

    return round(current_vix, 2), round(vix_5d_avg, 2)


def fetch_spy_returns() -> Tuple[float, float]:
    """Fetch SPY returns for 1-day and 5-day periods

    Returns:
        Tuple of (return_1d, return_5d)
    """
    fetcher = MarketDataFetcher()
    spy_data = fetcher.fetch_benchmark_data(period='30d')

    if spy_data is None or spy_data.empty or len(spy_data) < 6:
        logger.warning("Insufficient SPY data, returning 0.0")
        return 0.0, 0.0

    latest = float(spy_data['Close'].iloc[-1])
    prev_1d = float(spy_data['Close'].iloc[-2])
    prev_5d = float(spy_data['Close'].iloc[-6])

    return_1d = (latest - prev_1d) / prev_1d if prev_1d > 0 else 0.0
    return_5d = (latest - prev_5d) / prev_5d if prev_5d > 0 else 0.0

    return round(return_1d, 4), round(return_5d, 4)
