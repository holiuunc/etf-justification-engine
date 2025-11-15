import { useState } from 'react'
import type { Recommendation } from '../types'
import {
  formatCurrency,
  formatPercent,
  getActionColor,
  getPriorityColor,
} from '../utils/formatters'

interface RecommendationsListProps {
  recommendations: Recommendation[]
}

export default function RecommendationsList({ recommendations }: RecommendationsListProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  return (
    <div className="card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Trade Recommendations</h2>
          <p className="card-subtitle">AI-generated recommendations with complete justifications</p>
        </div>
        <span className="badge bg-success-100 text-success-800 text-lg px-3 py-1">
          {recommendations.length} Recommendation{recommendations.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="space-y-4">
        {recommendations.map((rec) => (
          <RecommendationCard
            key={rec.ticker}
            recommendation={rec}
            isExpanded={expandedId === rec.ticker}
            onToggle={() => setExpandedId(expandedId === rec.ticker ? null : rec.ticker)}
          />
        ))}
      </div>
    </div>
  )
}

interface RecommendationCardProps {
  recommendation: Recommendation
  isExpanded: boolean
  onToggle: () => void
}

function RecommendationCard({ recommendation, isExpanded, onToggle }: RecommendationCardProps) {
  const rec = recommendation

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden hover:border-primary-300 transition-colors">
      {/* Header - Always Visible */}
      <div
        className="p-4 cursor-pointer bg-white hover:bg-gray-50 transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <h3 className="text-xl font-bold font-mono text-gray-900">
                {rec.ticker}
              </h3>
              <span className={`badge ${getActionColor(rec.action)}`}>
                {rec.action}
              </span>
              <span className={`badge ${getPriorityColor(rec.priority)}`}>
                {rec.priority} priority
              </span>
              <span className="text-sm text-gray-500">
                {(rec.confidence * 100).toFixed(0)}% confidence
              </span>
            </div>

            <p className="text-sm text-gray-700 mb-3">
              {rec.justification.thesis}
            </p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-gray-500">Current Allocation</p>
                <p className="text-sm font-semibold text-gray-900">
                  {formatPercent(rec.allocation.current_allocation, 1)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Target Allocation</p>
                <p className="text-sm font-semibold text-gray-900">
                  {formatPercent(rec.allocation.target_allocation, 1)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Shares to Trade</p>
                <p className={`text-sm font-semibold ${
                  rec.allocation.shares_to_trade > 0 ? 'text-success-600' : 'text-danger-600'
                }`}>
                  {rec.allocation.shares_to_trade > 0 ? '+' : ''}
                  {rec.allocation.shares_to_trade}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Estimated Cost</p>
                <p className="text-sm font-semibold text-gray-900">
                  {formatCurrency(rec.transaction_details.total_cost)}
                </p>
              </div>
            </div>
          </div>

          <button
            className="ml-4 text-gray-400 hover:text-gray-600 transition-colors"
            onClick={onToggle}
          >
            <svg
              className={`h-6 w-6 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="border-t border-gray-200 bg-gray-50 p-4 space-y-4">
          {/* Quantitative Evidence */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 mb-2">
              📊 Quantitative Evidence
            </h4>
            <dl className="space-y-1">
              {Object.entries(rec.justification.quantitative_evidence).map(([key, value]) => (
                <div key={key} className="flex">
                  <dt className="text-sm text-gray-600 w-40 flex-shrink-0">
                    {key.replace(/_/g, ' ')}:
                  </dt>
                  <dd className="text-sm text-gray-900 font-medium">{value}</dd>
                </div>
              ))}
            </dl>
          </div>

          {/* Qualitative Evidence */}
          {Object.keys(rec.justification.qualitative_evidence).length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-2">
                💭 Qualitative Evidence
              </h4>
              <dl className="space-y-1">
                {Object.entries(rec.justification.qualitative_evidence).map(([key, value]) => (
                  <div key={key} className="flex">
                    <dt className="text-sm text-gray-600 w-40 flex-shrink-0">
                      {key.replace(/_/g, ' ')}:
                    </dt>
                    <dd className="text-sm text-gray-900">{value}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}

          {/* Risk Assessment */}
          {Object.keys(rec.justification.risk_assessment).length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-2">
                ⚠️ Risk Assessment
              </h4>
              <dl className="space-y-1">
                {Object.entries(rec.justification.risk_assessment).map(([key, value]) => (
                  <div key={key} className="flex">
                    <dt className="text-sm text-gray-600 w-40 flex-shrink-0">
                      {key.replace(/_/g, ' ')}:
                    </dt>
                    <dd className="text-sm text-gray-900">{value}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}

          {/* Holding Period & Review Triggers */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-2">
                ⏱️ Holding Period
              </h4>
              <p className="text-sm text-gray-700">
                {rec.justification.holding_period}
              </p>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-gray-900 mb-2">
                🔔 Review Triggers
              </h4>
              <ul className="text-sm text-gray-700 space-y-1">
                {rec.justification.review_triggers.map((trigger, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-primary-500 mr-2">•</span>
                    {trigger}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Prospectus Text */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-semibold text-gray-900">
                📝 Prospectus Text (Ready to Copy)
              </h4>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(rec.prospectus_text)
                  alert('Copied to clipboard!')
                }}
                className="text-xs text-primary-600 hover:text-primary-700 font-medium"
              >
                Copy
              </button>
            </div>
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
              {rec.prospectus_text}
            </p>
          </div>

          {/* Transaction Details */}
          <div className="bg-primary-50 border border-primary-200 rounded-lg p-3">
            <h4 className="text-sm font-semibold text-primary-900 mb-2">
              💰 Transaction Details
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              <div>
                <p className="text-primary-600">Estimated Price</p>
                <p className="font-medium text-primary-900">
                  {formatCurrency(rec.transaction_details.estimated_price)}
                </p>
              </div>
              <div>
                <p className="text-primary-600">Estimated Cost</p>
                <p className="font-medium text-primary-900">
                  {formatCurrency(rec.transaction_details.estimated_cost)}
                </p>
              </div>
              <div>
                <p className="text-primary-600">Commission</p>
                <p className="font-medium text-primary-900">
                  {formatCurrency(rec.transaction_details.commission)}
                </p>
              </div>
              <div>
                <p className="text-primary-600">Total Cost</p>
                <p className="font-medium text-primary-900">
                  {formatCurrency(rec.transaction_details.total_cost)}
                </p>
              </div>
            </div>
            <p className="text-xs text-primary-700 mt-2">
              Execution: {rec.transaction_details.execution_timeframe}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
