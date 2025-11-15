"""Radar Scan Module

Implements the "Radar" component of the Radar/Scalpel strategy.
Performs a broad, efficient scan across all 30 ETFs to identify those
with unusual activity (price moves, volume spikes, technical signals)
worthy of deep analysis.
"""

import logging
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from config.strategy_params import RADAR_TRIGGERS, TECHNICAL_PARAMS
from data.models import (
    PriceData, TechnicalIndicators, FocusListItem,
    TriggerType, ActionType
)

logger = logging.getLogger(__name__)


# ============================================================================
# Technical Indicator Calculations
# ============================================================================

def calculate_sma(prices: pd.Series, period: int) -> float:
    """Calculate Simple Moving Average

    Args:
        prices: Series of prices
        period: Number of periods for MA

    Returns:
        SMA value or None if insufficient data
    """
    if len(prices) < period:
        return None
    return float(prices.tail(period).mean())


def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """Calculate Relative Strength Index

    Args:
        prices: Series of prices
        period: RSI period (default: 14)

    Returns:
        RSI value (0-100) or None if insufficient data
    """
    if len(prices) < period + 1:
        return None

    # Calculate price changes
    delta = prices.diff()

    # Separate gains and losses
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)

    # Calculate average gains and losses
    avg_gains = gains.rolling(window=period).mean()
    avg_losses = losses.rolling(window=period).mean()

    # Calculate RS and RSI
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))

    return float(rsi.iloc[-1])


def calculate_macd(
    prices: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> tuple[float, float, str]:
    """Calculate MACD indicator

    Args:
        prices: Series of prices
        fast_period: Fast EMA period
        slow_period: Slow EMA period
        signal_period: Signal line period

    Returns:
        Tuple of (macd, signal, signal_type)
    """
    if len(prices) < slow_period + signal_period:
        return None, None, "insufficient_data"

    # Calculate EMAs
    ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
    ema_slow = prices.ewm(span=slow_period, adjust=False).mean()

    # Calculate MACD line
    macd_line = ema_fast - ema_slow

    # Calculate signal line
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

    # Determine signal
    current_macd = float(macd_line.iloc[-1])
    current_signal = float(signal_line.iloc[-1])
    prev_macd = float(macd_line.iloc[-2])
    prev_signal = float(signal_line.iloc[-2])

    if current_macd > current_signal and prev_macd <= prev_signal:
        signal_type = "bullish_crossover"
    elif current_macd < current_signal and prev_macd >= prev_signal:
        signal_type = "bearish_crossover"
    elif current_macd > current_signal:
        signal_type = "bullish"
    else:
        signal_type = "bearish"

    return current_macd, current_signal, signal_type


def calculate_bollinger_bands(
    prices: pd.Series,
    period: int = 20,
    std_dev: int = 2
) -> tuple[float, float, float, str]:
    """Calculate Bollinger Bands

    Args:
        prices: Series of prices
        period: MA period
        std_dev: Standard deviation multiplier

    Returns:
        Tuple of (upper_band, middle_band, lower_band, position)
    """
    if len(prices) < period:
        return None, None, None, "insufficient_data"

    middle = prices.tail(period).mean()
    std = prices.tail(period).std()

    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    current_price = float(prices.iloc[-1])

    # Determine position
    if current_price >= upper:
        position = "upper_band"
    elif current_price <= lower:
        position = "lower_band"
    else:
        position = "middle"

    return float(upper), float(middle), float(lower), position


def calculate_technical_indicators(
    df: pd.DataFrame,
    ticker: str
) -> TechnicalIndicators:
    """Calculate all technical indicators for an ETF

    Args:
        df: DataFrame with OHLCV data
        ticker: ETF ticker symbol

    Returns:
        TechnicalIndicators model
    """
    if df.empty or len(df) < 200:
        logger.warning(f"Insufficient data for technical indicators: {ticker}")
        return TechnicalIndicators()

    prices = df['Close']

    # Moving averages
    sma_20 = calculate_sma(prices, TECHNICAL_PARAMS['sma_short'])
    sma_50 = calculate_sma(prices, TECHNICAL_PARAMS['sma_medium'])
    sma_200 = calculate_sma(prices, TECHNICAL_PARAMS['sma_long'])

    # RSI
    rsi_14 = calculate_rsi(prices, TECHNICAL_PARAMS['rsi_period'])

    # MACD
    macd, macd_signal_line, macd_signal_type = calculate_macd(
        prices,
        TECHNICAL_PARAMS['macd_fast'],
        TECHNICAL_PARAMS['macd_slow'],
        TECHNICAL_PARAMS['macd_signal']
    )

    # Bollinger Bands
    bb_upper, bb_middle, bb_lower, bb_position = calculate_bollinger_bands(
        prices,
        TECHNICAL_PARAMS['bollinger_period'],
        TECHNICAL_PARAMS['bollinger_stddev']
    )

    return TechnicalIndicators(
        sma_20=round(sma_20, 2) if sma_20 else None,
        sma_50=round(sma_50, 2) if sma_50 else None,
        sma_200=round(sma_200, 2) if sma_200 else None,
        rsi_14=round(rsi_14, 2) if rsi_14 else None,
        macd=round(macd, 4) if macd else None,
        macd_signal=macd_signal_type,
        bollinger_upper=round(bb_upper, 2) if bb_upper else None,
        bollinger_lower=round(bb_lower, 2) if bb_lower else None,
        bollinger_position=bb_position
    )


# ============================================================================
# Trigger Detection
# ============================================================================

def detect_volume_spike(price_data: PriceData) -> Optional[dict]:
    """Detect unusual volume activity

    Args:
        price_data: PriceData model

    Returns:
        Trigger dict if spike detected, None otherwise
    """
    threshold = RADAR_TRIGGERS['volume_spike_threshold']

    if price_data.volume_ratio >= threshold:
        return {
            'type': TriggerType.VOLUME_SPIKE,
            'value': price_data.volume_ratio,
            'description': f"Volume {price_data.volume_ratio:.1%} of 30-day average"
        }

    return None


def detect_price_move(price_data: PriceData, df: pd.DataFrame) -> Optional[dict]:
    """Detect significant price movement

    Args:
        price_data: PriceData model
        df: DataFrame with historical prices

    Returns:
        Trigger dict if significant move detected, None otherwise
    """
    threshold = RADAR_TRIGGERS['price_move_threshold']
    abs_change = abs(price_data.price_change_1d)

    # Check absolute threshold
    if abs_change >= threshold:
        return {
            'type': TriggerType.PRICE_MOVE,
            'value': price_data.price_change_1d,
            'description': f"Price moved {price_data.price_change_1d:+.2%} (>{threshold:.1%} threshold)"
        }

    # Check standard deviation threshold
    if len(df) >= 30:
        returns = df['Close'].pct_change()
        std_dev = returns.tail(30).std()
        z_score = abs(price_data.price_change_1d / std_dev) if std_dev > 0 else 0

        if z_score >= RADAR_TRIGGERS['price_stddev_threshold']:
            return {
                'type': TriggerType.PRICE_MOVE,
                'value': z_score,
                'description': f"Price moved {z_score:.1f} standard deviations"
            }

    return None


def detect_momentum_crossover(technical_indicators: TechnicalIndicators) -> Optional[dict]:
    """Detect bullish/bearish momentum crossovers

    Args:
        technical_indicators: TechnicalIndicators model

    Returns:
        Trigger dict if crossover detected, None otherwise
    """
    if not RADAR_TRIGGERS['momentum_crossover']:
        return None

    # Check MACD crossover
    if technical_indicators.macd_signal in ['bullish_crossover', 'bearish_crossover']:
        return {
            'type': TriggerType.MOMENTUM_CROSSOVER,
            'value': 1.0,
            'description': f"MACD {technical_indicators.macd_signal.replace('_', ' ')}"
        }

    # Check SMA crossovers (20/50)
    if technical_indicators.sma_20 and technical_indicators.sma_50:
        if technical_indicators.sma_20 > technical_indicators.sma_50:
            # Potential golden cross scenario
            ratio = technical_indicators.sma_20 / technical_indicators.sma_50
            if 1.0 < ratio < 1.02:  # Recent crossover
                return {
                    'type': TriggerType.MOMENTUM_CROSSOVER,
                    'value': ratio,
                    'description': "20-day MA crossed above 50-day MA (golden cross)"
                }

    return None


def detect_rsi_extreme(technical_indicators: TechnicalIndicators) -> Optional[dict]:
    """Detect RSI overbought/oversold conditions

    Args:
        technical_indicators: TechnicalIndicators model

    Returns:
        Trigger dict if extreme RSI detected, None otherwise
    """
    if not technical_indicators.rsi_14:
        return None

    rsi = technical_indicators.rsi_14
    overbought = RADAR_TRIGGERS['rsi_overbought']
    oversold = RADAR_TRIGGERS['rsi_oversold']

    if rsi >= overbought:
        return {
            'type': TriggerType.RSI_EXTREME,
            'value': rsi,
            'description': f"RSI at {rsi:.1f} (overbought)"
        }
    elif rsi <= oversold:
        return {
            'type': TriggerType.RSI_EXTREME,
            'value': rsi,
            'description': f"RSI at {rsi:.1f} (oversold)"
        }

    return None


# ============================================================================
# Focus List Generation
# ============================================================================

def scan_etf(
    ticker: str,
    df: pd.DataFrame,
    price_data: PriceData
) -> Optional[FocusListItem]:
    """Scan a single ETF for triggers

    Args:
        ticker: ETF ticker symbol
        df: DataFrame with historical OHLCV data
        price_data: PriceData model

    Returns:
        FocusListItem if triggers detected, None otherwise
    """
    # Calculate technical indicators
    technical_indicators = calculate_technical_indicators(df, ticker)

    # Check all triggers
    triggers = []

    # Volume spike
    volume_trigger = detect_volume_spike(price_data)
    if volume_trigger:
        triggers.append(volume_trigger)

    # Price movement
    price_trigger = detect_price_move(price_data, df)
    if price_trigger:
        triggers.append(price_trigger)

    # Momentum crossover
    momentum_trigger = detect_momentum_crossover(technical_indicators)
    if momentum_trigger:
        triggers.append(momentum_trigger)

    # RSI extremes
    rsi_trigger = detect_rsi_extreme(technical_indicators)
    if rsi_trigger:
        triggers.append(rsi_trigger)

    # If any triggers found, create Focus List item
    if triggers:
        # Use the first (most significant) trigger
        primary_trigger = triggers[0]

        # Determine preliminary recommendation
        recommendation = determine_preliminary_action(
            price_data, technical_indicators, primary_trigger
        )

        return FocusListItem(
            ticker=ticker,
            trigger_type=primary_trigger['type'],
            trigger_value=primary_trigger['value'],
            trigger_description=primary_trigger['description'],
            price_data=price_data,
            technical_indicators=technical_indicators,
            news_analysis=None,  # Will be added by Scalpel Dive
            recommendation=recommendation
        )

    return None


def determine_preliminary_action(
    price_data: PriceData,
    technical_indicators: TechnicalIndicators,
    trigger: dict
) -> ActionType:
    """Determine preliminary action based on technical signals

    Args:
        price_data: PriceData model
        technical_indicators: TechnicalIndicators model
        trigger: Trigger dictionary

    Returns:
        Preliminary ActionType (HOLD by default, refined by Scalpel Dive)
    """
    # This is a simplified preliminary assessment
    # The Scalpel Dive will refine this with news/LLM analysis

    bullish_signals = 0
    bearish_signals = 0

    # Check price momentum
    if price_data.price_change_1d > 0:
        bullish_signals += 1
    else:
        bearish_signals += 1

    # Check technical indicators
    if technical_indicators.macd_signal in ['bullish', 'bullish_crossover']:
        bullish_signals += 1
    elif technical_indicators.macd_signal in ['bearish', 'bearish_crossover']:
        bearish_signals += 1

    if technical_indicators.rsi_14:
        if technical_indicators.rsi_14 < 30:
            bullish_signals += 1  # Oversold = potential buy
        elif technical_indicators.rsi_14 > 70:
            bearish_signals += 1  # Overbought = potential sell

    # Preliminary decision (conservative - default to HOLD)
    if bullish_signals > bearish_signals + 1:
        return ActionType.HOLD  # Will be refined to BUY if news is positive
    elif bearish_signals > bullish_signals + 1:
        return ActionType.HOLD  # Will be refined to TRIM/SELL if news is negative
    else:
        return ActionType.HOLD


def generate_focus_list(
    market_data: Dict[str, pd.DataFrame],
    price_data_dict: Dict[str, PriceData]
) -> List[FocusListItem]:
    """Generate Focus List from market data

    Args:
        market_data: Dict mapping tickers to DataFrames
        price_data_dict: Dict mapping tickers to PriceData models

    Returns:
        List of FocusListItem models
    """
    logger.info("Generating Focus List from Radar scan...")

    focus_list = []

    for ticker in market_data.keys():
        df = market_data.get(ticker)
        price_data = price_data_dict.get(ticker)

        if df is None or df.empty or price_data is None:
            logger.warning(f"Skipping {ticker} - insufficient data")
            continue

        # Scan for triggers
        focus_item = scan_etf(ticker, df, price_data)
        if focus_item:
            focus_list.append(focus_item)
            logger.info(f"  ✓ {ticker}: {focus_item.trigger_description}")

    # Sort by trigger significance (volume ratio for now)
    focus_list.sort(key=lambda x: x.trigger_value, reverse=True)

    # Limit to max size
    max_size = RADAR_TRIGGERS['focus_list_max_size']
    if len(focus_list) > max_size:
        logger.info(f"Trimming Focus List from {len(focus_list)} to {max_size} items")
        focus_list = focus_list[:max_size]

    logger.info(f"Focus List generated: {len(focus_list)} ETFs flagged")
    return focus_list
