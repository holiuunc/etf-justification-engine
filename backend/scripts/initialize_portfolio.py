#!/usr/bin/env python3
"""Portfolio Initialization Script

Initializes the portfolio with current holdings and creates the necessary
data files for tracking portfolio state and transaction history.

Usage:
    python scripts/initialize_portfolio.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from config.etf_universe import ETF_UNIVERSE, get_etf_info
from config.strategy_params import PORTFOLIO_SETTINGS
from data.models import (
    Position, PortfolioState, AllocationBreakdown, RiskMetrics,
    Transaction, TransactionHistory, ActionType
)

# ============================================================================
# Current Holdings (as of PROJECT_BRIEF.md)
# ============================================================================

CURRENT_HOLDINGS = [
    {
        "ticker": "IVV",
        "shares": 45,
        "cost_basis": 690.71,
        "current_price": 690.71,  # Will be updated with real data
        "purchase_date": "2025-09-29"
    },
    {
        "ticker": "IYW",
        "shares": 128,
        "cost_basis": 211.27,
        "current_price": 211.27,
        "purchase_date": "2025-09-29"
    },
    {
        "ticker": "IEMG",
        "shares": 303,
        "cost_basis": 69.14,
        "current_price": 69.14,
        "purchase_date": "2025-09-29"
    },
    {
        "ticker": "ITA",
        "shares": 97,
        "cost_basis": 217.45,
        "current_price": 217.45,
        "purchase_date": "2025-09-29"
    },
    {
        "ticker": "AGG",
        "shares": 50,
        "cost_basis": 100.79,
        "current_price": 100.79,
        "purchase_date": "2025-09-29"
    }
]

# Commission per trade
COMMISSION = 10.00

# ============================================================================
# Helper Functions
# ============================================================================

def calculate_position_metrics(holding: Dict) -> Position:
    """Calculate position metrics from holding data"""
    shares = holding["shares"]
    cost_basis = holding["cost_basis"]
    current_price = holding["current_price"]

    market_value = shares * current_price
    unrealized_gain = shares * (current_price - cost_basis)
    unrealized_gain_pct = (current_price - cost_basis) / cost_basis if cost_basis > 0 else 0.0

    return Position(
        ticker=holding["ticker"],
        shares=shares,
        cost_basis=cost_basis,
        current_price=current_price,
        market_value=market_value,
        weight=0.0,  # Will be calculated after total value is known
        unrealized_gain=unrealized_gain,
        unrealized_gain_pct=unrealized_gain_pct
    )


def calculate_allocation_breakdown(positions: Dict[str, Position]) -> AllocationBreakdown:
    """Calculate core vs satellite allocation"""
    from config.etf_universe import ETFCategory

    total_value = sum(pos.market_value for pos in positions.values())

    core = 0.0
    major_satellites = 0.0
    tactical_satellites = 0.0
    hedging = 0.0

    for ticker, position in positions.items():
        etf_info = get_etf_info(ticker)
        category = etf_info.get("category")
        allocation = position.market_value / total_value

        if category == ETFCategory.CORE:
            core += allocation
        elif category == ETFCategory.MAJOR_SATELLITE:
            major_satellites += allocation
        elif category == ETFCategory.TACTICAL_SATELLITE:
            tactical_satellites += allocation
        elif category == ETFCategory.HEDGING:
            hedging += allocation

    return AllocationBreakdown(
        core=round(core, 4),
        major_satellites=round(major_satellites, 4),
        tactical_satellites=round(tactical_satellites, 4),
        hedging=round(hedging, 4)
    )


def calculate_sector_breakdown(positions: Dict[str, Position]) -> Dict[str, float]:
    """Calculate sector allocation"""
    total_value = sum(pos.market_value for pos in positions.values())

    sector_breakdown = {}
    for ticker, position in positions.items():
        etf_info = get_etf_info(ticker)
        sector = etf_info.get("sector", "Unknown")
        allocation = position.market_value / total_value

        if sector in sector_breakdown:
            sector_breakdown[sector] += allocation
        else:
            sector_breakdown[sector] = allocation

    return {k: round(v, 4) for k, v in sector_breakdown.items()}


def calculate_geography_breakdown(positions: Dict[str, Position]) -> Dict[str, float]:
    """Calculate geography allocation"""
    total_value = sum(pos.market_value for pos in positions.values())

    geo_breakdown = {}
    for ticker, position in positions.items():
        etf_info = get_etf_info(ticker)
        geography = etf_info.get("geography", "Unknown")
        allocation = position.market_value / total_value

        if geography in geo_breakdown:
            geo_breakdown[geography] += allocation
        else:
            geo_breakdown[geography] = allocation

    return {k: round(v, 4) for k, v in geo_breakdown.items()}


def create_initial_portfolio_state() -> PortfolioState:
    """Create initial portfolio state from current holdings"""

    # Calculate positions
    positions = {}
    for holding in CURRENT_HOLDINGS:
        position = calculate_position_metrics(holding)
        positions[holding["ticker"]] = position

    # Calculate total value
    total_value = sum(pos.market_value for pos in positions.values())

    # Update position weights
    for position in positions.values():
        position.weight = round(position.market_value / total_value, 4)

    # Calculate allocations
    allocation_breakdown = calculate_allocation_breakdown(positions)
    sector_breakdown = calculate_sector_breakdown(positions)
    geography_breakdown = calculate_geography_breakdown(positions)

    # Initial metrics (will be calculated properly with historical data)
    risk_metrics = RiskMetrics(
        sharpe_ratio_30d=None,
        volatility_30d=None,
        max_drawdown=0.0,
        beta_to_spy=None,
        correlation_to_spy=None
    )

    # Calculate returns
    initial_capital = PORTFOLIO_SETTINGS["initial_capital"]
    total_return_pct = (total_value - initial_capital) / initial_capital

    return PortfolioState(
        as_of=datetime.now(),
        initial_capital=initial_capital,
        total_value=round(total_value, 2),
        cash_balance=0.0,  # Fully invested initially
        total_return_pct=round(total_return_pct, 6),
        daily_return_pct=0.0,  # First day
        positions=positions,
        allocation_breakdown=allocation_breakdown,
        sector_breakdown=sector_breakdown,
        geography_breakdown=geography_breakdown,
        risk_metrics=risk_metrics
    )


def create_initial_transactions() -> TransactionHistory:
    """Create initial transaction history"""
    transactions = []

    for idx, holding in enumerate(CURRENT_HOLDINGS, start=1):
        total_cost = holding["shares"] * holding["cost_basis"] + COMMISSION

        transaction = Transaction(
            id=f"txn_{idx:03d}",
            date=holding["purchase_date"],
            ticker=holding["ticker"],
            action=ActionType.BUY,
            shares=holding["shares"],
            price=holding["cost_basis"],
            commission=COMMISSION,
            total_cost=round(total_cost, 2),
            justification="Initial portfolio allocation",
            analysis_reference=None
        )
        transactions.append(transaction)

    history = TransactionHistory(transactions=transactions)
    return history


def create_etf_metadata_cache() -> Dict:
    """Create ETF metadata cache from universe"""
    return {ticker: info for ticker, info in ETF_UNIVERSE.items()}


def main():
    """Initialize portfolio and create data files"""
    print("=" * 80)
    print("ETF Justification Engine - Portfolio Initialization")
    print("=" * 80)
    print()

    # Get data directory
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"

    # Create portfolio state
    print("Creating initial portfolio state...")
    portfolio_state = create_initial_portfolio_state()

    # Display summary
    print(f"\nPortfolio Summary:")
    print(f"  Initial Capital:  ${portfolio_state.initial_capital:,.2f}")
    print(f"  Current Value:    ${portfolio_state.total_value:,.2f}")
    print(f"  Total Return:     {portfolio_state.total_return_pct:+.2%}")
    print(f"  Positions:        {len(portfolio_state.positions)}")
    print()

    print("Position Details:")
    print(f"  {'Ticker':<8} {'Shares':>8} {'Price':>10} {'Value':>12} {'Weight':>8}")
    print(f"  {'-' * 8} {'-' * 8} {'-' * 10} {'-' * 12} {'-' * 8}")
    for ticker, pos in portfolio_state.positions.items():
        print(f"  {ticker:<8} {pos.shares:>8} ${pos.current_price:>9.2f} ${pos.market_value:>11.2f} {pos.weight:>7.1%}")
    print()

    print("Allocation Breakdown:")
    print(f"  Core:               {portfolio_state.allocation_breakdown.core:.1%}")
    print(f"  Major Satellites:   {portfolio_state.allocation_breakdown.major_satellites:.1%}")
    print(f"  Tactical Satellites:{portfolio_state.allocation_breakdown.tactical_satellites:.1%}")
    print(f"  Hedging:            {portfolio_state.allocation_breakdown.hedging:.1%}")
    print()

    # Save portfolio state
    portfolio_file = data_dir / "portfolio" / "current.json"
    print(f"Saving portfolio state to: {portfolio_file}")
    portfolio_file.parent.mkdir(parents=True, exist_ok=True)
    with open(portfolio_file, 'w') as f:
        json.dump(portfolio_state.model_dump(mode='json'), f, indent=2, default=str)
    print("  ✓ Portfolio state saved")

    # Create transaction history
    print("\nCreating transaction history...")
    transaction_history = create_initial_transactions()
    print(f"  Initial transactions: {len(transaction_history.transactions)}")

    transactions_file = data_dir / "transactions" / "history.json"
    transactions_file.parent.mkdir(parents=True, exist_ok=True)
    with open(transactions_file, 'w') as f:
        json.dump(transaction_history.model_dump(mode='json'), f, indent=2, default=str)
    print(f"  ✓ Transaction history saved to: {transactions_file}")

    # Create ETF metadata cache
    print("\nCreating ETF metadata cache...")
    metadata = create_etf_metadata_cache()
    print(f"  Total ETFs in universe: {len(metadata)}")

    metadata_file = data_dir / "cache" / "etf_metadata.json"
    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    with open(metadata_file, 'w') as f:
        # Convert Enum values to strings for JSON serialization
        metadata_serializable = {}
        for ticker, info in metadata.items():
            info_copy = info.copy()
            info_copy['category'] = str(info['category'].value)
            info_copy['asset_class'] = str(info['asset_class'].value)
            metadata_serializable[ticker] = info_copy
        json.dump(metadata_serializable, f, indent=2)
    print(f"  ✓ ETF metadata saved to: {metadata_file}")

    print()
    print("=" * 80)
    print("Initialization Complete!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Verify .env file has API keys configured")
    print("  2. Install dependencies: pip install -r backend/requirements.txt")
    print("  3. Run manual analysis: python backend/main.py")
    print()


if __name__ == "__main__":
    main()
