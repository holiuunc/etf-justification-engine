/**
 * TypeScript Interfaces for ETF Justification Engine
 * Matches backend Pydantic models for type safety
 */

// ============================================================================
// Enums
// ============================================================================

export enum ActionType {
  BUY = 'BUY',
  SELL = 'SELL',
  HOLD = 'HOLD',
  INITIATE = 'INITIATE',
  TRIM = 'TRIM',
  ADD = 'ADD',
}

export enum PriorityLevel {
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

export enum RiskMode {
  EXTREME_COMPLACENCY = 'extreme_complacency',
  NORMAL = 'normal',
  CAUTION = 'caution',
  RISK_OFF = 'risk_off',
}

export enum MarketRegime {
  BULL = 'bull',
  BEAR = 'bear',
  SIDEWAYS = 'sideways',
}

export enum TriggerType {
  VOLUME_SPIKE = 'volume_spike',
  PRICE_MOVE = 'price_move',
  MOMENTUM_CROSSOVER = 'momentum_crossover',
  RSI_EXTREME = 'rsi_extreme',
  MANUAL = 'manual',
}

// ============================================================================
// Portfolio Models
// ============================================================================

export interface Position {
  ticker: string
  shares: number
  cost_basis: number
  current_price: number
  market_value: number
  weight: number
  unrealized_gain: number
  unrealized_gain_pct: number
}

export interface AllocationBreakdown {
  core: number
  major_satellites?: number
  tactical_satellites?: number
  hedging?: number
}

export interface RiskMetrics {
  sharpe_ratio_30d?: number | null
  volatility_30d?: number | null
  max_drawdown?: number | null
  beta_to_spy?: number | null
  correlation_to_spy?: number | null
}

export interface PortfolioState {
  as_of: string
  initial_capital: number
  total_value: number
  cash_balance: number
  total_return_pct: number
  daily_return_pct: number
  positions: Record<string, Position>
  allocation_breakdown: AllocationBreakdown
  sector_breakdown: Record<string, number>
  geography_breakdown: Record<string, number>
  risk_metrics: RiskMetrics
}

// ============================================================================
// Market Data Models
// ============================================================================

export interface PriceData {
  ticker: string
  current_price: number
  price_change_1d: number
  price_change_5d?: number | null
  price_change_30d?: number | null
  high_52w?: number | null
  low_52w?: number | null
  volume_today: number
  volume_30d_avg: number
  volume_ratio: number
}

export interface TechnicalIndicators {
  sma_20?: number | null
  sma_50?: number | null
  sma_200?: number | null
  rsi_14?: number | null
  macd?: number | null
  macd_signal?: string | null
  bollinger_upper?: number | null
  bollinger_lower?: number | null
  bollinger_position?: string | null
}

export interface NewsAnalysis {
  ticker: string
  news_count: number
  sentiment_score: number
  relevance_score: number
  headlines: string[]
  llm_summary?: string | null
  key_themes: string[]
  risk_factors: string[]
}

// ============================================================================
// Analysis Models
// ============================================================================

export interface MarketOverview {
  vix_level: number
  vix_change_pct: number
  vix_5d_avg: number
  risk_mode: RiskMode
  sp500_close: number
  sp500_return_1d: number
  sp500_return_5d?: number | null
  market_regime: MarketRegime
  key_macro_events: string[]
}

export interface FocusListItem {
  ticker: string
  trigger_type: TriggerType
  trigger_value: number
  trigger_description: string
  price_data: PriceData
  technical_indicators: TechnicalIndicators
  news_analysis?: NewsAnalysis | null
  recommendation: ActionType
}

export interface AllocationDetails {
  current_allocation: number
  target_allocation: number
  allocation_change: number
  shares_current: number
  shares_target: number
  shares_to_trade: number
}

export interface TransactionDetails {
  estimated_price: number
  estimated_cost: number
  commission: number
  total_cost: number
  execution_timeframe: string
  source_of_funds?: string | null
}

export interface Justification {
  thesis: string
  quantitative_evidence: Record<string, string>
  qualitative_evidence: Record<string, string>
  risk_assessment: Record<string, string>
  holding_period: string
  review_triggers: string[]
}

export interface Recommendation {
  ticker: string
  action: ActionType
  priority: PriorityLevel
  confidence: number
  allocation: AllocationDetails
  transaction_details: TransactionDetails
  justification: Justification
  prospectus_text: string
}

export interface PortfolioSnapshot {
  total_value: number
  daily_return_pct: number
  total_return_pct: number
  sharpe_ratio_30d?: number | null
  max_drawdown?: number | null
  days_since_inception: number
  allocation_breakdown: Record<string, number>
  top_performers_1d: Array<Record<string, number>>
  top_performers_mtd: Array<Record<string, number>>
}

export interface ExecutionSummary {
  analysis_quality: string
  focus_list_count: number
  recommendations_count: number
  api_calls_made: Record<string, number>
  errors: string[]
  warnings: string[]
}

export interface DailyAnalysis {
  date: string
  timestamp: string
  execution_time_seconds: number
  market_overview: MarketOverview
  focus_list: FocusListItem[]
  recommendations: Recommendation[]
  portfolio_snapshot: PortfolioSnapshot
  execution_summary: ExecutionSummary
}

// ============================================================================
// Utility Types
// ============================================================================

export interface APIError {
  message: string
  details?: string
}

export interface LoadingState {
  isLoading: boolean
  error: APIError | null
}

export interface AnalysisStatus {
  running: boolean
  progress: number
  message: string
  started_at?: string | null
  estimated_completion?: string | null
}
