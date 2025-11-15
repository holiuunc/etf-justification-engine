import type { DailyAnalysis, PortfolioState } from '../types'
import PortfolioSummary from './PortfolioSummary'
import MarketOverview from './MarketOverview'
import FocusList from './FocusList'
import RecommendationsList from './RecommendationsList'

interface DashboardProps {
  portfolio: PortfolioState
  analysis: DailyAnalysis | null
}

export default function Dashboard({ portfolio, analysis }: DashboardProps) {
  return (
    <div className="space-y-6">
      {/* Market Overview (if analysis available) */}
      {analysis && (
        <MarketOverview marketOverview={analysis.market_overview} />
      )}

      {/* Portfolio Summary */}
      <PortfolioSummary portfolio={portfolio} />

      {/* Focus List (if analysis available) */}
      {analysis && analysis.focus_list.length > 0 && (
        <FocusList focusList={analysis.focus_list} />
      )}

      {/* Recommendations (if analysis available) */}
      {analysis && analysis.recommendations.length > 0 && (
        <RecommendationsList recommendations={analysis.recommendations} />
      )}

      {/* No Analysis Available */}
      {!analysis && (
        <div className="card text-center py-8">
          <div className="text-gray-400 mb-2">
            <svg
              className="h-12 w-12 mx-auto"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-1">
            No Analysis Available
          </h3>
          <p className="text-gray-500">
            Run the backend analysis to generate recommendations
          </p>
          <code className="mt-4 inline-block bg-gray-100 px-3 py-1 rounded text-sm text-gray-700">
            python backend/main.py
          </code>
        </div>
      )}
    </div>
  )
}
