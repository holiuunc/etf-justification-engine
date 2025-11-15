/**
 * API Service for ETF Justification Engine
 * Fetches data from backend JSON files (GitHub raw URLs or local)
 */

import type {
  DailyAnalysis,
  PortfolioState,
  APIError,
  AnalysisStatus,
} from '../types'

// ============================================================================
// Configuration
// ============================================================================

const API_CONFIG = {
  // Backend API base URL (Docker container runs at http://localhost:8000)
  apiBaseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  // For development: Use relative path to local data
  // For production: Use GitHub raw URLs
  baseUrl: import.meta.env.VITE_API_BASE_URL || '/data',
  githubRawBase: import.meta.env.VITE_GITHUB_RAW_BASE || '',
  timeout: 10000, // 10 seconds
}

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Fetch JSON with error handling and timeout
 */
async function fetchJSON<T>(url: string): Promise<T> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout)

  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data as T
  } catch (error) {
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new Error('Request timeout - please try again')
      }
      throw new Error(`Failed to fetch data: ${error.message}`)
    }
    throw new Error('Unknown error occurred')
  } finally {
    clearTimeout(timeoutId)
  }
}

/**
 * Get data URL (local or GitHub)
 */
function getDataUrl(path: string): string {
  // If GitHub raw base is configured, use it
  if (API_CONFIG.githubRawBase) {
    return `${API_CONFIG.githubRawBase}/${path}`
  }
  // Otherwise use local relative path
  return `${API_CONFIG.baseUrl}/${path}`
}

// ============================================================================
// API Functions
// ============================================================================

/**
 * Fetch current portfolio state
 */
export async function fetchPortfolio(): Promise<PortfolioState> {
  // Try backend API first, fallback to static files
  try {
    const url = `${API_CONFIG.apiBaseUrl}/api/portfolio`
    return await fetchJSON<PortfolioState>(url)
  } catch (error) {
    // Fallback to static files if backend is unavailable
    console.warn('Backend API unavailable, falling back to static files')
    const url = getDataUrl('portfolio/current.json')
    return fetchJSON<PortfolioState>(url)
  }
}

/**
 * Fetch latest daily analysis
 */
export async function fetchLatestAnalysis(): Promise<DailyAnalysis> {
  // Try backend API first
  try {
    const url = `${API_CONFIG.apiBaseUrl}/api/analysis/latest`
    return await fetchJSON<DailyAnalysis>(url)
  } catch (error) {
    // Fallback to static files if backend is unavailable
    console.warn('Backend API unavailable, falling back to static files')
    const today = new Date().toISOString().split('T')[0]
    const todayUrl = getDataUrl(`analysis/${today}.json`)

    try {
      return await fetchJSON<DailyAnalysis>(todayUrl)
    } catch (error) {
      console.error('Failed to fetch latest analysis:', error)
      throw error
    }
  }
}

/**
 * Fetch specific date's analysis
 */
export async function fetchAnalysisByDate(date: string): Promise<DailyAnalysis> {
  const url = getDataUrl(`analysis/${date}.json`)
  return fetchJSON<DailyAnalysis>(url)
}

/**
 * Fetch multiple analyses (date range)
 */
export async function fetchAnalysesRange(
  startDate: string,
  endDate: string
): Promise<DailyAnalysis[]> {
  // Generate array of dates
  const dates = getDateRange(startDate, endDate)

  // Fetch all analyses in parallel
  const promises = dates.map((date) =>
    fetchAnalysisByDate(date).catch(() => null) // Ignore errors for missing dates
  )

  const results = await Promise.all(promises)

  // Filter out null results (failed fetches)
  return results.filter((analysis): analysis is DailyAnalysis => analysis !== null)
}

/**
 * Fetch transaction history
 */
export async function fetchTransactionHistory(): Promise<any> {
  const url = getDataUrl('transactions/history.json')
  return fetchJSON(url)
}

/**
 * Fetch ETF metadata
 */
export async function fetchETFMetadata(): Promise<Record<string, any>> {
  const url = getDataUrl('cache/etf_metadata.json')
  return fetchJSON(url)
}

// ============================================================================
// Analysis Control API
// ============================================================================

/**
 * Start a new analysis run
 */
export async function startAnalysis(): Promise<{ status: string; message: string }> {
  const url = `${API_CONFIG.apiBaseUrl}/api/analysis/start`

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    if (response.status === 409) {
      throw new Error('Analysis already running')
    }
    throw new Error(`Failed to start analysis: ${response.status}`)
  }

  return response.json()
}

/**
 * Get current analysis progress
 */
export async function getAnalysisProgress(): Promise<AnalysisStatus> {
  const url = `${API_CONFIG.apiBaseUrl}/api/analysis/progress`
  return fetchJSON<AnalysisStatus>(url)
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Generate array of date strings between start and end
 */
function getDateRange(startDate: string, endDate: string): string[] {
  const dates: string[] = []
  const current = new Date(startDate)
  const end = new Date(endDate)

  while (current <= end) {
    dates.push(current.toISOString().split('T')[0])
    current.setDate(current.getDate() + 1)
  }

  return dates
}

/**
 * Get date N days ago
 */
export function getDaysAgo(days: number): string {
  const date = new Date()
  date.setDate(date.getDate() - days)
  return date.toISOString().split('T')[0]
}

/**
 * Check if data is stale (older than threshold)
 */
export function isDataStale(timestamp: string, thresholdHours: number = 24): boolean {
  const dataDate = new Date(timestamp)
  const now = new Date()
  const hoursDiff = (now.getTime() - dataDate.getTime()) / (1000 * 60 * 60)
  return hoursDiff > thresholdHours
}

// ============================================================================
// Mock Data for Development
// ============================================================================

/**
 * Generate mock portfolio for development/testing
 */
export function getMockPortfolio(): PortfolioState {
  return {
    as_of: new Date().toISOString(),
    initial_capital: 100000,
    total_value: 99976.05,
    cash_balance: 23.95,
    total_return_pct: -0.0002,
    daily_return_pct: 0.0008,
    positions: {
      IVV: {
        ticker: 'IVV',
        shares: 45,
        cost_basis: 666.67,
        current_price: 691.50,
        market_value: 31117.50,
        weight: 0.311,
        unrealized_gain: 1117.35,
        unrealized_gain_pct: 0.0373,
      },
      IYW: {
        ticker: 'IYW',
        shares: 128,
        cost_basis: 195.31,
        current_price: 215.30,
        market_value: 27558.40,
        weight: 0.276,
        unrealized_gain: 2559.12,
        unrealized_gain_pct: 0.1024,
      },
      IEMG: {
        ticker: 'IEMG',
        shares: 303,
        cost_basis: 66.01,
        current_price: 69.50,
        market_value: 21058.50,
        weight: 0.211,
        unrealized_gain: 1057.47,
        unrealized_gain_pct: 0.0529,
      },
      ITA: {
        ticker: 'ITA',
        shares: 97,
        cost_basis: 206.19,
        current_price: 205.80,
        market_value: 19962.60,
        weight: 0.200,
        unrealized_gain: -37.83,
        unrealized_gain_pct: -0.0019,
      },
      AGG: {
        ticker: 'AGG',
        shares: 50,
        cost_basis: 100.00,
        current_price: 102.55,
        market_value: 5127.50,
        weight: 0.051,
        unrealized_gain: 127.50,
        unrealized_gain_pct: 0.0255,
      },
    },
    allocation_breakdown: {
      core: 0.35,
      major_satellites: 0.40,
      tactical_satellites: 0.25,
      hedging: 0.00,
    },
    sector_breakdown: {
      'Broad Market': 0.50,
      Technology: 0.26,
      'Emerging Markets': 0.20,
    },
    geography_breakdown: {
      US: 0.80,
      'Emerging Markets': 0.20,
    },
    risk_metrics: {
      sharpe_ratio_30d: 1.42,
      volatility_30d: 0.12,
      max_drawdown: -0.023,
      beta_to_spy: 1.15,
      correlation_to_spy: 0.92,
    },
  }
}

// ============================================================================
// Error Handling
// ============================================================================

/**
 * Create standardized API error
 */
export function createAPIError(message: string, details?: string): APIError {
  return {
    message,
    details,
  }
}

/**
 * Handle API errors gracefully
 */
export function handleAPIError(error: unknown): APIError {
  if (error instanceof Error) {
    return createAPIError(error.message)
  }
  return createAPIError('An unknown error occurred')
}
