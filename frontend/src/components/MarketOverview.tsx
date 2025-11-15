import type { MarketOverview as MarketOverviewType } from '../types'
import { formatPercent, getRiskModeColor, snakeToTitle } from '../utils/formatters'

interface MarketOverviewProps {
  marketOverview: MarketOverviewType
}

export default function MarketOverview({ marketOverview }: MarketOverviewProps) {
  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Market Overview
      </h2>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* VIX */}
        <div className="border-r border-gray-200 pr-4">
          <p className="text-sm text-gray-500 mb-1">VIX Level</p>
          <p className="text-2xl font-bold text-gray-900">
            {marketOverview.vix_level.toFixed(2)}
          </p>
          <p className={`text-sm ${marketOverview.vix_change_pct >= 0 ? 'text-danger-600' : 'text-success-600'}`}>
            {formatPercent(marketOverview.vix_change_pct / 100)} today
          </p>
        </div>

        {/* Risk Mode */}
        <div className="border-r border-gray-200 pr-4">
          <p className="text-sm text-gray-500 mb-1">Risk Mode</p>
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getRiskModeColor(marketOverview.risk_mode)}`}>
            {snakeToTitle(marketOverview.risk_mode)}
          </span>
          <p className="text-xs text-gray-500 mt-2">
            5D Avg: {marketOverview.vix_5d_avg.toFixed(2)}
          </p>
        </div>

        {/* S&P 500 */}
        <div className="border-r border-gray-200 pr-4">
          <p className="text-sm text-gray-500 mb-1">S&P 500</p>
          <p className="text-2xl font-bold text-gray-900">
            {marketOverview.sp500_close > 0 ? marketOverview.sp500_close.toFixed(2) : 'N/A'}
          </p>
          <p className={`text-sm ${marketOverview.sp500_return_1d >= 0 ? 'text-success-600' : 'text-danger-600'}`}>
            {formatPercent(marketOverview.sp500_return_1d)} today
          </p>
        </div>

        {/* Market Regime */}
        <div>
          <p className="text-sm text-gray-500 mb-1">Market Regime</p>
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
            marketOverview.market_regime === 'bull' ? 'bg-success-100 text-success-800' :
            marketOverview.market_regime === 'bear' ? 'bg-danger-100 text-danger-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {marketOverview.market_regime.toUpperCase()}
          </span>
          {marketOverview.sp500_return_5d != null && (
            <p className="text-xs text-gray-500 mt-2">
              5D: {formatPercent(marketOverview.sp500_return_5d)}
            </p>
          )}
        </div>
      </div>

      {/* Macro Events */}
      {marketOverview.key_macro_events.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm font-medium text-gray-700 mb-2">Key Events:</p>
          <ul className="space-y-1">
            {marketOverview.key_macro_events.map((event, index) => (
              <li key={index} className="text-sm text-gray-600 flex items-start">
                <span className="text-primary-500 mr-2">•</span>
                {event}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
