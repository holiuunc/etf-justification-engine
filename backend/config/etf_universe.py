"""ETF Universe Configuration

This module defines the complete universe of 30 ETFs available for trading
in the Econ 425 Investment Project. Each ETF is categorized according to
the Core-Satellite investment strategy.
"""

from enum import Enum
from typing import Dict, List


class ETFCategory(str, Enum):
    """ETF category classification for portfolio structure"""
    CORE = "Core"
    MAJOR_SATELLITE = "Major Satellite"
    TACTICAL_SATELLITE = "Tactical Satellite"
    HEDGING = "Hedging"


class AssetClass(str, Enum):
    """Asset class classification"""
    EQUITY = "Equity"
    FIXED_INCOME = "Fixed Income"
    COMMODITIES = "Commodities"
    CASH_EQUIVALENT = "Cash Equivalent"


# Complete 30-ETF universe with metadata
ETF_UNIVERSE: Dict[str, Dict] = {
    # ============================================================================
    # CORE (2) - The stable foundation of the portfolio
    # ============================================================================
    "IVV": {
        "name": "iShares Core S&P 500 ETF",
        "category": ETFCategory.CORE,
        "sector": "Broad Market",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0003,
        "description": "Tracks the S&P 500 index - core US equity exposure"
    },
    "AGG": {
        "name": "iShares Core U.S. Aggregate Bond ETF",
        "category": ETFCategory.CORE,
        "sector": "Fixed Income",
        "geography": "US",
        "asset_class": AssetClass.FIXED_INCOME,
        "expense_ratio": 0.0003,
        "description": "Broad US investment-grade bond exposure"
    },

    # ============================================================================
    # MAJOR SATELLITES (8) - Large directional holdings for macro themes
    # ============================================================================
    "IEMG": {
        "name": "iShares Core MSCI Emerging Markets ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Broad Market",
        "geography": "Emerging Markets",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0009,
        "description": "Emerging markets equity exposure"
    },
    "IJR": {
        "name": "iShares Core S&P Small-Cap ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Small Cap",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0006,
        "description": "US small-cap equity exposure"
    },
    "IJH": {
        "name": "iShares Core S&P Mid-Cap ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Mid Cap",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0005,
        "description": "US mid-cap equity exposure"
    },
    "IUSG": {
        "name": "iShares Core S&P U.S. Growth ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Growth",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0004,
        "description": "US growth stocks exposure"
    },
    "IYW": {
        "name": "iShares U.S. Technology ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Technology",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
        "description": "Technology sector exposure"
    },
    "IEV": {
        "name": "iShares Europe ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Broad Market",
        "geography": "Europe",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0059,
        "description": "European equity exposure"
    },
    "TLT": {
        "name": "iShares 20+ Year Treasury Bond ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Government Bonds",
        "geography": "US",
        "asset_class": AssetClass.FIXED_INCOME,
        "expense_ratio": 0.0015,
        "description": "Long-duration US Treasury bonds"
    },
    "LQD": {
        "name": "iShares iBoxx $ Investment Grade Corporate Bond ETF",
        "category": ETFCategory.MAJOR_SATELLITE,
        "sector": "Corporate Bonds",
        "geography": "US",
        "asset_class": AssetClass.FIXED_INCOME,
        "expense_ratio": 0.0014,
        "description": "Investment-grade corporate bonds"
    },

    # ============================================================================
    # TACTICAL SATELLITES (16) - Sector-specific tactical positions
    # ============================================================================
    "ITA": {
        "name": "iShares U.S. Aerospace & Defense ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Aerospace",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
        "description": "Aerospace and defense sector"
    },
    "MCHI": {
        "name": "iShares MSCI China ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Broad Market",
        "geography": "China",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0059,
        "description": "Chinese equity exposure"
    },
    "IBB": {
        "name": "iShares Biotechnology ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Biotechnology",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0044,
        "description": "Biotechnology sector"
    },
    "IYF": {
        "name": "iShares U.S. Financials ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Financials",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
        "description": "Financial sector exposure"
    },
    "EWC": {
        "name": "iShares MSCI Canada ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Broad Market",
        "geography": "Canada",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0047,
        "description": "Canadian equity exposure"
    },
    "IFRA": {
        "name": "iShares U.S. Infrastructure ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Infrastructure",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0030,
        "description": "US infrastructure sector"
    },
    "IYH": {
        "name": "iShares U.S. Healthcare ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Healthcare",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
        "description": "Healthcare sector exposure"
    },
    "IYG": {
        "name": "iShares U.S. Financial Services ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Financial Services",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
        "description": "Financial services sector"
    },
    "IYJ": {
        "name": "iShares U.S. Industrials ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Industrials",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
        "description": "Industrial sector exposure"
    },
    "IYC": {
        "name": "iShares U.S. Consumer Discretionary ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Consumer Discretionary",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
        "description": "Consumer discretionary sector"
    },
    "IYK": {
        "name": "iShares U.S. Consumer Staples ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Consumer Staples",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
        "description": "Consumer staples sector"
    },
    "IYE": {
        "name": "iShares U.S. Energy ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Energy",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
        "description": "Energy sector exposure"
    },
    "IYZ": {
        "name": "iShares U.S. Telecommunications ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Telecommunications",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
        "description": "Telecommunications sector"
    },
    "MBB": {
        "name": "iShares MBS ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Mortgage-Backed Securities",
        "geography": "US",
        "asset_class": AssetClass.FIXED_INCOME,
        "expense_ratio": 0.0004,
        "description": "Mortgage-backed securities"
    },
    "IYR": {
        "name": "iShares U.S. Real Estate ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Real Estate",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
        "description": "Real estate sector (REITs)"
    },
    "IYT": {
        "name": "iShares U.S. Transportation ETF",
        "category": ETFCategory.TACTICAL_SATELLITE,
        "sector": "Transportation",
        "geography": "US",
        "asset_class": AssetClass.EQUITY,
        "expense_ratio": 0.0039,
        "description": "Transportation sector"
    },

    # ============================================================================
    # HEDGING (4) - Risk management and defensive assets
    # ============================================================================
    "SGOV": {
        "name": "iShares 0-3 Month Treasury Bond ETF",
        "category": ETFCategory.HEDGING,
        "sector": "Cash Equivalent",
        "geography": "US",
        "asset_class": AssetClass.CASH_EQUIVALENT,
        "expense_ratio": 0.0005,
        "description": "Cash equivalent - short-term treasuries"
    },
    "TIP": {
        "name": "iShares TIPS Bond ETF",
        "category": ETFCategory.HEDGING,
        "sector": "Inflation-Protected",
        "geography": "US",
        "asset_class": AssetClass.FIXED_INCOME,
        "expense_ratio": 0.0019,
        "description": "Treasury inflation-protected securities"
    },
    "IAU": {
        "name": "iShares Gold Trust",
        "category": ETFCategory.HEDGING,
        "sector": "Gold",
        "geography": "Global",
        "asset_class": AssetClass.COMMODITIES,
        "expense_ratio": 0.0025,
        "description": "Gold commodity exposure"
    },
    "GSG": {
        "name": "iShares S&P GSCI Commodity-Indexed Trust",
        "category": ETFCategory.HEDGING,
        "sector": "Commodities",
        "geography": "Global",
        "asset_class": AssetClass.COMMODITIES,
        "expense_ratio": 0.0075,
        "description": "Broad commodity exposure"
    },
}


# ============================================================================
# Helper Functions
# ============================================================================

def get_all_tickers() -> List[str]:
    """Return list of all ETF tickers in the universe"""
    return list(ETF_UNIVERSE.keys())


def get_etf_info(ticker: str) -> Dict:
    """Get metadata for a specific ETF ticker

    Args:
        ticker: ETF ticker symbol

    Returns:
        Dictionary containing ETF metadata, or empty dict if not found
    """
    return ETF_UNIVERSE.get(ticker, {})


def get_etfs_by_category(category: ETFCategory) -> List[str]:
    """Get all ETF tickers in a specific category

    Args:
        category: ETFCategory enum value

    Returns:
        List of ticker symbols
    """
    return [
        ticker for ticker, info in ETF_UNIVERSE.items()
        if info["category"] == category
    ]


def get_etfs_by_sector(sector: str) -> List[str]:
    """Get all ETF tickers in a specific sector

    Args:
        sector: Sector name (e.g., "Technology", "Healthcare")

    Returns:
        List of ticker symbols
    """
    return [
        ticker for ticker, info in ETF_UNIVERSE.items()
        if info["sector"] == sector
    ]


def get_etfs_by_asset_class(asset_class: AssetClass) -> List[str]:
    """Get all ETF tickers in a specific asset class

    Args:
        asset_class: AssetClass enum value

    Returns:
        List of ticker symbols
    """
    return [
        ticker for ticker, info in ETF_UNIVERSE.items()
        if info["asset_class"] == asset_class
    ]


def get_etfs_by_geography(geography: str) -> List[str]:
    """Get all ETF tickers for a specific geography

    Args:
        geography: Geography name (e.g., "US", "China", "Europe")

    Returns:
        List of ticker symbols
    """
    return [
        ticker for ticker, info in ETF_UNIVERSE.items()
        if info["geography"] == geography
    ]


def validate_ticker(ticker: str) -> bool:
    """Check if a ticker is in the allowed universe

    Args:
        ticker: ETF ticker symbol

    Returns:
        True if ticker is valid, False otherwise
    """
    return ticker in ETF_UNIVERSE


# Universe statistics for validation
UNIVERSE_STATS = {
    "total_etfs": len(ETF_UNIVERSE),
    "core_count": len(get_etfs_by_category(ETFCategory.CORE)),
    "major_satellite_count": len(get_etfs_by_category(ETFCategory.MAJOR_SATELLITE)),
    "tactical_satellite_count": len(get_etfs_by_category(ETFCategory.TACTICAL_SATELLITE)),
    "hedging_count": len(get_etfs_by_category(ETFCategory.HEDGING)),
    "equity_count": len(get_etfs_by_asset_class(AssetClass.EQUITY)),
    "fixed_income_count": len(get_etfs_by_asset_class(AssetClass.FIXED_INCOME)),
    "commodity_count": len(get_etfs_by_asset_class(AssetClass.COMMODITIES)),
    "cash_equivalent_count": len(get_etfs_by_asset_class(AssetClass.CASH_EQUIVALENT)),
}
