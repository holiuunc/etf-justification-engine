import type { FocusListItem } from '../types'
import { formatPercent, snakeToTitle } from '../utils/formatters'

interface FocusListProps {
  focusList: FocusListItem[]
}

export default function FocusList({ focusList }: FocusListProps) {
  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Focus List</h2>
          <p className="card-subtitle">ETFs flagged by Radar Scan for unusual activity</p>
        </div>
        <span className="badge bg-primary-100 text-primary-800 text-lg px-3 py-1">
          {focusList.length} ETF{focusList.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="space-y-4">
        {focusList.map((item) => (
          <div
            key={item.ticker}
            className="border border-gray-200 rounded-lg p-4 hover:border-primary-300 transition-colors"
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 font-mono">
                  {item.ticker}
                </h3>
                <p className="text-sm text-gray-600">
                  {item.trigger_description}
                </p>
              </div>
              <span className={`badge ${
                item.news_analysis
                  ? item.news_analysis.sentiment_score > 0.3
                    ? 'bg-success-100 text-success-800'
                    : item.news_analysis.sentiment_score < -0.3
                    ? 'bg-danger-100 text-danger-800'
                    : 'bg-gray-100 text-gray-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {snakeToTitle(item.trigger_type)}
              </span>
            </div>

            {/* Price & Volume Data */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
              <div>
                <p className="text-xs text-gray-500">Price Change</p>
                <p className={`text-sm font-semibold ${
                  item.price_data.price_change_1d >= 0 ? 'text-success-600' : 'text-danger-600'
                }`}>
                  {formatPercent(item.price_data.price_change_1d)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Volume Ratio</p>
                <p className="text-sm font-semibold text-gray-900">
                  {item.price_data.volume_ratio.toFixed(2)}x
                </p>
              </div>
              {item.technical_indicators.rsi_14 && (
                <div>
                  <p className="text-xs text-gray-500">RSI (14)</p>
                  <p className="text-sm font-semibold text-gray-900">
                    {item.technical_indicators.rsi_14.toFixed(1)}
                  </p>
                </div>
              )}
              {item.technical_indicators.macd_signal && (
                <div>
                  <p className="text-xs text-gray-500">MACD Signal</p>
                  <p className="text-sm font-semibold text-gray-900 capitalize">
                    {item.technical_indicators.macd_signal.replace('_', ' ')}
                  </p>
                </div>
              )}
            </div>

            {/* News Analysis */}
            {item.news_analysis && item.news_analysis.news_count > 0 && (
              <div className="bg-gray-50 rounded-lg p-3 mt-3">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-xs font-medium text-gray-700">
                    News Analysis ({item.news_analysis.news_count} articles)
                  </p>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-500">Sentiment:</span>
                    <span className={`text-xs font-semibold ${
                      item.news_analysis.sentiment_score > 0 ? 'text-success-600' : 'text-danger-600'
                    }`}>
                      {item.news_analysis.sentiment_score > 0 ? '+' : ''}
                      {item.news_analysis.sentiment_score.toFixed(2)}
                    </span>
                  </div>
                </div>

                {item.news_analysis.llm_summary && (
                  <p className="text-sm text-gray-700 mb-2">
                    {item.news_analysis.llm_summary}
                  </p>
                )}

                {item.news_analysis.key_themes.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-2">
                    {item.news_analysis.key_themes.map((theme, idx) => (
                      <span
                        key={idx}
                        className="badge bg-primary-50 text-primary-700 text-xs"
                      >
                        {theme}
                      </span>
                    ))}
                  </div>
                )}

                {item.news_analysis.risk_factors.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs font-medium text-gray-600 mb-1">Risks:</p>
                    <div className="flex flex-wrap gap-1">
                      {item.news_analysis.risk_factors.map((risk, idx) => (
                        <span
                          key={idx}
                          className="badge bg-warning-50 text-warning-700 text-xs"
                        >
                          {risk}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
