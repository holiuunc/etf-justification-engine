"""Portfolio Engine Module

Generates trade recommendations based on analysis from Radar Scan, Risk Manager,
and Scalpel Dive modules. Produces actionable recommendations with complete
justifications suitable for prospectus writing.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from config.etf_universe import ETF_UNIVERSE, get_etf_info
from config.strategy_params import (
    TRADING_RULES, POSITION_LIMITS, PROSPECTUS_SETTINGS
)
from data.models import (
    PortfolioState, FocusListItem, Recommendation,
    ActionType, PriorityLevel, AllocationDetails,
    TransactionDetails, Justification, RiskMode
)
from core.risk_manager import (
    calculate_safe_position_size, get_target_allocation
)

logger = logging.getLogger(__name__)


# ============================================================================
# Recommendation Generation
# ============================================================================

class RecommendationEngine:
    """Generates trade recommendations"""

    def __init__(
        self,
        portfolio: PortfolioState,
        risk_mode: RiskMode
    ):
        self.portfolio = portfolio
        self.risk_mode = risk_mode
        self.target_allocation = get_target_allocation(risk_mode)

    def generate_recommendations(
        self,
        focus_list: List[FocusListItem]
    ) -> List[Recommendation]:
        """Generate all recommendations

        Args:
            focus_list: List of ETFs flagged for analysis

        Returns:
            List of Recommendation models
        """
        logger.info(f"Generating recommendations for {len(focus_list)} Focus List items...")

        recommendations = []

        # Generate recommendations for Focus List items
        for focus_item in focus_list:
            rec = self._generate_recommendation_for_focus_item(focus_item)
            if rec:
                recommendations.append(rec)

        # Generate recommendations for existing holdings not on Focus List
        existing_recommendations = self._generate_recommendations_for_holdings()
        recommendations.extend(existing_recommendations)

        # Sort by priority
        recommendations.sort(
            key=lambda r: (
                0 if r.priority == PriorityLevel.HIGH else
                1 if r.priority == PriorityLevel.MEDIUM else 2
            )
        )

        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations

    def _generate_recommendation_for_focus_item(
        self,
        focus_item: FocusListItem
    ) -> Optional[Recommendation]:
        """Generate recommendation for a Focus List ETF

        Args:
            focus_item: FocusListItem model

        Returns:
            Recommendation model or None
        """
        ticker = focus_item.ticker

        # Check if currently held
        is_held = ticker in self.portfolio.positions
        current_position = self.portfolio.positions.get(ticker)

        # Determine action based on signals and news
        action = self._determine_action(focus_item, is_held)

        # Calculate target allocation
        target_allocation = self._calculate_target_allocation(
            focus_item, action, is_held
        )

        # Calculate allocation details
        allocation_details = self._calculate_allocation_details(
            ticker, target_allocation, current_position
        )

        # Skip if no change needed
        if allocation_details.shares_to_trade == 0:
            logger.debug(f"No trade needed for {ticker}")
            return None

        # Calculate transaction details
        transaction_details = self._calculate_transaction_details(
            focus_item.price_data.current_price,
            allocation_details.shares_to_trade,
            action
        )

        # Determine priority and confidence
        priority, confidence = self._calculate_priority_and_confidence(
            focus_item, action
        )

        # Generate justification
        justification = self._generate_justification(
            focus_item, action, allocation_details, transaction_details
        )

        # Generate prospectus text
        prospectus_text = self._generate_prospectus_text(
            ticker, action, justification, allocation_details
        )

        return Recommendation(
            ticker=ticker,
            action=action,
            priority=priority,
            confidence=confidence,
            allocation=allocation_details,
            transaction_details=transaction_details,
            justification=justification,
            prospectus_text=prospectus_text
        )

    def _determine_action(
        self,
        focus_item: FocusListItem,
        is_held: bool
    ) -> ActionType:
        """Determine what action to take

        Args:
            focus_item: FocusListItem model
            is_held: Whether position is currently held

        Returns:
            ActionType
        """
        # Start with preliminary technical recommendation
        action = focus_item.recommendation

        # Refine based on news sentiment (if available)
        if focus_item.news_analysis:
            sentiment = focus_item.news_analysis.sentiment_score

            # Strong positive sentiment + bullish technicals = BUY/ADD
            if sentiment > 0.5 and action == ActionType.HOLD:
                action = ActionType.ADD if is_held else ActionType.INITIATE

            # Strong negative sentiment = TRIM/SELL
            elif sentiment < -0.3 and is_held:
                action = ActionType.TRIM

        # Risk mode overrides
        if self.risk_mode == RiskMode.RISK_OFF:
            # In risk-off mode, prefer HOLD/TRIM over BUY
            if action in [ActionType.INITIATE, ActionType.ADD]:
                action = ActionType.HOLD
        elif self.risk_mode == RiskMode.CAUTION:
            # In caution mode, be selective about adding
            if action == ActionType.ADD:
                action = ActionType.HOLD

        return action

    def _calculate_target_allocation(
        self,
        focus_item: FocusListItem,
        action: ActionType,
        is_held: bool
    ) -> float:
        """Calculate target allocation for the ETF

        Args:
            focus_item: FocusListItem model
            action: Proposed action
            is_held: Whether currently held

        Returns:
            Target allocation (0.0 to 1.0)
        """
        ticker = focus_item.ticker
        etf_info = get_etf_info(ticker)

        # Get current allocation
        if is_held:
            current_position = self.portfolio.positions[ticker]
            current_allocation = current_position.weight
        else:
            current_allocation = 0.0

        # Determine target based on action
        if action == ActionType.HOLD:
            return current_allocation

        elif action == ActionType.INITIATE:
            # Start with tactical position
            if etf_info['category'] == 'Major Satellite':
                return 0.10  # 10% for major satellites
            else:
                return 0.05  # 5% for tactical

        elif action == ActionType.ADD:
            # Increase by 3-5%
            increase = 0.03
            return min(current_allocation + increase, POSITION_LIMITS['single_position_max'])

        elif action == ActionType.TRIM:
            # Reduce by 3-5%
            decrease = 0.03
            return max(current_allocation - decrease, 0.0)

        elif action == ActionType.SELL:
            return 0.0

        return current_allocation

    def _calculate_allocation_details(
        self,
        ticker: str,
        target_allocation: float,
        current_position: Optional[any]
    ) -> AllocationDetails:
        """Calculate allocation change details

        Args:
            ticker: ETF ticker
            target_allocation: Target allocation (0-1)
            current_position: Current Position model or None

        Returns:
            AllocationDetails model
        """
        if current_position:
            current_allocation = current_position.weight
            shares_current = current_position.shares
        else:
            current_allocation = 0.0
            shares_current = 0

        allocation_change = target_allocation - current_allocation

        # Calculate target shares
        target_value = self.portfolio.total_value * target_allocation
        current_price = self._get_current_price(ticker)
        shares_target = int(target_value / current_price) if current_price > 0 else 0

        shares_to_trade = shares_target - shares_current

        return AllocationDetails(
            current_allocation=round(current_allocation, 4),
            target_allocation=round(target_allocation, 4),
            allocation_change=round(allocation_change, 4),
            shares_current=shares_current,
            shares_target=shares_target,
            shares_to_trade=shares_to_trade
        )

    def _calculate_transaction_details(
        self,
        estimated_price: float,
        shares_to_trade: int,
        action: ActionType
    ) -> TransactionDetails:
        """Calculate transaction execution details

        Args:
            estimated_price: Estimated execution price
            shares_to_trade: Number of shares (positive for buy, negative for sell)
            action: Action type

        Returns:
            TransactionDetails model
        """
        abs_shares = abs(shares_to_trade)
        estimated_cost = abs_shares * estimated_price
        commission = TRADING_RULES['commission_per_trade'] if shares_to_trade != 0 else 0.0
        total_cost = estimated_cost + commission

        # Determine execution timeframe
        if action in [ActionType.INITIATE, ActionType.BUY, ActionType.ADD]:
            timeframe = "Next 1-2 trading days"
        elif action == ActionType.TRIM:
            timeframe = "Next 2-3 trading days (non-urgent)"
        elif action == ActionType.SELL:
            timeframe = "Immediate execution recommended"
        else:
            timeframe = "N/A"

        return TransactionDetails(
            estimated_price=round(estimated_price, 2),
            estimated_cost=round(estimated_cost, 2),
            commission=commission,
            total_cost=round(total_cost, 2),
            execution_timeframe=timeframe,
            source_of_funds=None  # Will be determined during execution
        )

    def _calculate_priority_and_confidence(
        self,
        focus_item: FocusListItem,
        action: ActionType
    ) -> Tuple[PriorityLevel, float]:
        """Calculate recommendation priority and confidence

        Args:
            focus_item: FocusListItem model
            action: Proposed action

        Returns:
            Tuple of (PriorityLevel, confidence_score)
        """
        # Base confidence on trigger strength and news sentiment
        confidence = 0.7  # Base confidence

        # Adjust for trigger strength
        if focus_item.trigger_value > 2.0:
            confidence += 0.1

        # Adjust for news sentiment alignment
        if focus_item.news_analysis:
            sentiment = focus_item.news_analysis.sentiment_score
            relevance = focus_item.news_analysis.relevance_score

            if relevance > 0.7:
                if sentiment > 0.5:
                    confidence += 0.1
                elif sentiment < -0.3:
                    confidence += 0.05  # Negative news also adds conviction

        # Determine priority
        if action in [ActionType.SELL, ActionType.INITIATE] and confidence > 0.8:
            priority = PriorityLevel.HIGH
        elif action in [ActionType.ADD, ActionType.TRIM]:
            priority = PriorityLevel.MEDIUM
        else:
            priority = PriorityLevel.LOW

        return priority, min(confidence, 0.95)

    def _generate_recommendations_for_holdings(self) -> List[Recommendation]:
        """Generate HOLD recommendations for existing positions not on Focus List

        Returns:
            List of Recommendation models
        """
        recommendations = []

        for ticker in self.portfolio.positions.keys():
            # Skip if already in focus list (will be handled separately)
            # This is a simplified HOLD recommendation
            # In practice, we'd want more sophisticated logic here

            pass  # TODO: Implement HOLD recommendations for existing positions

        return recommendations

    def _get_current_price(self, ticker: str) -> float:
        """Get current price for ticker

        Args:
            ticker: ETF ticker

        Returns:
            Current price or estimated price
        """
        if ticker in self.portfolio.positions:
            return self.portfolio.positions[ticker].current_price

        # Would fetch from market data in real implementation
        return 100.0  # Placeholder

    def _generate_justification(
        self,
        focus_item: FocusListItem,
        action: ActionType,
        allocation: AllocationDetails,
        transaction: TransactionDetails
    ) -> Justification:
        """Generate comprehensive trade justification

        Args:
            focus_item: FocusListItem model
            action: Proposed action
            allocation: AllocationDetails
            transaction: TransactionDetails

        Returns:
            Justification model
        """
        # Generate thesis
        thesis = self._generate_thesis(focus_item, action)

        # Collect quantitative evidence
        quant_evidence = self._collect_quantitative_evidence(focus_item)

        # Collect qualitative evidence
        qual_evidence = self._collect_qualitative_evidence(focus_item)

        # Generate risk assessment
        risk_assessment = self._generate_risk_assessment(focus_item, allocation)

        # Determine holding period
        holding_period = self._determine_holding_period(action)

        # Generate review triggers
        review_triggers = self._generate_review_triggers(focus_item, action)

        return Justification(
            thesis=thesis,
            quantitative_evidence=quant_evidence,
            qualitative_evidence=qual_evidence,
            risk_assessment=risk_assessment,
            holding_period=holding_period,
            review_triggers=review_triggers
        )

    def _generate_thesis(self, focus_item: FocusListItem, action: ActionType) -> str:
        """Generate investment thesis statement"""
        etf_info = get_etf_info(focus_item.ticker)
        name = etf_info['name']

        if action in [ActionType.INITIATE, ActionType.ADD]:
            return (
                f"{name} demonstrates strong momentum with {focus_item.trigger_description}. "
                f"Technical indicators and {('positive news sentiment' if focus_item.news_analysis and focus_item.news_analysis.sentiment_score > 0 else 'market dynamics')} "
                f"support {'initiating a position' if action == ActionType.INITIATE else 'adding to our position'}."
            )
        elif action == ActionType.TRIM:
            return (
                f"While {name} shows activity ({focus_item.trigger_description}), "
                f"current risk environment and valuation suggest prudent profit-taking is warranted."
            )
        else:
            return f"Maintaining current position in {name} based on balanced risk/reward profile."

    def _collect_quantitative_evidence(self, focus_item: FocusListItem) -> Dict[str, str]:
        """Collect quantitative evidence"""
        evidence = {}

        # Price momentum
        evidence['price_momentum'] = (
            f"1-day: {focus_item.price_data.price_change_1d:+.2%}, "
            f"5-day: {focus_item.price_data.price_change_5d:+.2%}"
        )

        # Volume
        evidence['volume'] = (
            f"{focus_item.price_data.volume_today:,} shares "
            f"({focus_item.price_data.volume_ratio:.1%} of 30-day avg)"
        )

        # Technical indicators
        if focus_item.technical_indicators.rsi_14:
            evidence['rsi'] = f"RSI at {focus_item.technical_indicators.rsi_14:.1f}"

        if focus_item.technical_indicators.macd_signal:
            evidence['macd'] = f"MACD signal: {focus_item.technical_indicators.macd_signal}"

        return evidence

    def _collect_qualitative_evidence(self, focus_item: FocusListItem) -> Dict[str, str]:
        """Collect qualitative evidence"""
        evidence = {}

        if focus_item.news_analysis:
            news = focus_item.news_analysis

            evidence['news_sentiment'] = (
                f"Sentiment score: {news.sentiment_score:+.2f}/1.0 "
                f"(relevance: {news.relevance_score:.2f})"
            )

            if news.key_themes:
                evidence['key_themes'] = ", ".join(news.key_themes[:3])

            if news.llm_summary:
                evidence['news_summary'] = news.llm_summary[:200] + "..."

        etf_info = get_etf_info(focus_item.ticker)
        evidence['sector_context'] = f"{etf_info['sector']} sector, {etf_info['geography']} geography"

        return evidence

    def _generate_risk_assessment(
        self,
        focus_item: FocusListItem,
        allocation: AllocationDetails
    ) -> Dict[str, str]:
        """Generate risk assessment"""
        assessment = {}

        # Primary risk
        if allocation.target_allocation > 0.20:
            assessment['concentration_risk'] = (
                f"Position size of {allocation.target_allocation:.1%} represents concentrated bet"
            )

        # Volatility risk
        if focus_item.technical_indicators.rsi_14:
            rsi = focus_item.technical_indicators.rsi_14
            if rsi > 70:
                assessment['overbought_risk'] = f"RSI at {rsi:.1f} suggests overbought conditions"
            elif rsi < 30:
                assessment['oversold_risk'] = f"RSI at {rsi:.1f} suggests potential reversal"

        # News risk
        if focus_item.news_analysis and focus_item.news_analysis.risk_factors:
            assessment['news_risks'] = ", ".join(focus_item.news_analysis.risk_factors[:2])

        return assessment

    def _determine_holding_period(self, action: ActionType) -> str:
        """Determine recommended holding period"""
        if action in [ActionType.INITIATE, ActionType.ADD]:
            return "Medium-term (3-6 months), review at next prospectus period"
        elif action == ActionType.TRIM:
            return "Reduce position over 1-2 weeks"
        else:
            return "Continue monitoring"

    def _generate_review_triggers(
        self,
        focus_item: FocusListItem,
        action: ActionType
    ) -> List[str]:
        """Generate conditions that warrant position review"""
        triggers = []

        # Price-based triggers
        current_price = focus_item.price_data.current_price
        triggers.append(f"Price breaks below ${current_price * 0.93:.2f} (-7% stop loss)")
        triggers.append(f"Price exceeds ${current_price * 1.15:.2f} (+15% profit target)")

        # VIX-based trigger
        triggers.append("VIX crosses above 30 (risk-off threshold)")

        # News-based trigger
        triggers.append("Material negative news or earnings miss")

        return triggers

    def _generate_prospectus_text(
        self,
        ticker: str,
        action: ActionType,
        justification: Justification,
        allocation: AllocationDetails
    ) -> str:
        """Generate prospectus-ready text snippet

        Args:
            ticker: ETF ticker
            action: Action type
            justification: Justification model
            allocation: AllocationDetails

        Returns:
            Professional prospectus text
        """
        etf_info = get_etf_info(ticker)

        # Build prospectus text
        text = f"**{ticker} ({etf_info['name']}) - {action.value} Recommendation**\n\n"

        text += f"{justification.thesis} "

        # Add key quantitative points
        if 'price_momentum' in justification.quantitative_evidence:
            text += f"Price momentum ({justification.quantitative_evidence['price_momentum']}) "

        if 'volume' in justification.quantitative_evidence:
            text += f"with elevated volume activity. "

        # Add allocation details
        if action != ActionType.HOLD:
            text += (
                f"We recommend {'initiating' if action == ActionType.INITIATE else 'adjusting'} "
                f"our position to {allocation.target_allocation:.1%} of the portfolio "
                f"({allocation.allocation_change:+.1%} change). "
            )

        # Add risk note
        text += (
            f"Risk management includes defined stop loss and regular monitoring per "
            f"our established triggers. "
        )

        # Add holding period
        text += f"Expected holding period: {justification.holding_period}."

        return text
