import type { PortfolioState } from '../types'
import {
  formatCurrency,
  formatPercent,
  formatDate,
  getValueColorClass,
} from '../utils/formatters'

interface PortfolioSummaryProps {
  portfolio: PortfolioState
}

export default function PortfolioSummary({ portfolio }: PortfolioSummaryProps) {
  const positions = Object.values(portfolio.positions)

  return (
    <div className="space-y-4">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <p className="text-sm font-medium text-gray-500">Total Value</p>
          <p className="text-2xl font-bold text-gray-900">
            {formatCurrency(portfolio.total_value)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Initial: {formatCurrency(portfolio.initial_capital)}
          </p>
        </div>

        <div className="card">
          <p className="text-sm font-medium text-gray-500">Total Return</p>
          <p className={`text-2xl font-bold ${getValueColorClass(portfolio.total_return_pct)}`}>
            {formatPercent(portfolio.total_return_pct)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {formatCurrency(portfolio.total_value - portfolio.initial_capital)} gain
          </p>
        </div>

        <div className="card">
          <p className="text-sm font-medium text-gray-500">Daily Return</p>
          <p className={`text-2xl font-bold ${getValueColorClass(portfolio.daily_return_pct)}`}>
            {formatPercent(portfolio.daily_return_pct)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Since {formatDate(portfolio.as_of, 'MMM dd')}
          </p>
        </div>

        <div className="card">
          <p className="text-sm font-medium text-gray-500">Positions</p>
          <p className="text-2xl font-bold text-gray-900">
            {positions.length}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Cash: {formatCurrency(portfolio.cash_balance)}
          </p>
        </div>
      </div>

      {/* Holdings Table */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Current Holdings</h2>
          <p className="card-subtitle">As of {formatDate(portfolio.as_of)}</p>
        </div>

        <div className="overflow-x-auto">
          <table className="table">
            <thead>
              <tr>
                <th>Ticker</th>
                <th className="text-right">Shares</th>
                <th className="text-right">Price</th>
                <th className="text-right">Market Value</th>
                <th className="text-right">Weight</th>
                <th className="text-right">Gain/Loss</th>
                <th className="text-right">Return %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {positions
                .sort((a, b) => b.market_value - a.market_value)
                .map((position) => (
                  <tr key={position.ticker}>
                    <td className="font-mono font-semibold text-gray-900">
                      {position.ticker}
                    </td>
                    <td className="text-right text-gray-600">
                      {position.shares}
                    </td>
                    <td className="text-right text-gray-900">
                      {formatCurrency(position.current_price)}
                    </td>
                    <td className="text-right font-medium text-gray-900">
                      {formatCurrency(position.market_value)}
                    </td>
                    <td className="text-right text-gray-600">
                      {formatPercent(position.weight, 1)}
                    </td>
                    <td className={`text-right font-medium ${getValueColorClass(position.unrealized_gain)}`}>
                      {formatCurrency(position.unrealized_gain)}
                    </td>
                    <td className={`text-right font-medium ${getValueColorClass(position.unrealized_gain_pct)}`}>
                      {formatPercent(position.unrealized_gain_pct)}
                    </td>
                  </tr>
                ))}
            </tbody>
            <tfoot className="border-t-2 border-gray-300 bg-gray-50">
              <tr>
                <td colSpan={3} className="font-semibold text-gray-900">
                  Total
                </td>
                <td className="text-right font-bold text-gray-900">
                  {formatCurrency(portfolio.total_value)}
                </td>
                <td className="text-right font-semibold text-gray-900">
                  {formatPercent(
                    positions.reduce((sum, p) => sum + p.weight, 0)
                  )}
                </td>
                <td className={`text-right font-bold ${getValueColorClass(portfolio.total_value - portfolio.initial_capital)}`}>
                  {formatCurrency(portfolio.total_value - portfolio.initial_capital)}
                </td>
                <td className={`text-right font-bold ${getValueColorClass(portfolio.total_return_pct)}`}>
                  {formatPercent(portfolio.total_return_pct)}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      {/* Allocation Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">
            Strategy Allocation
          </h3>
          <div className="space-y-2">
            <AllocationBar
              label="Core"
              value={portfolio.allocation_breakdown.core}
              color="bg-primary-500"
            />
            <AllocationBar
              label="Major Satellites"
              value={portfolio.allocation_breakdown.major_satellites || 0}
              color="bg-primary-400"
            />
            <AllocationBar
              label="Tactical Satellites"
              value={portfolio.allocation_breakdown.tactical_satellites || 0}
              color="bg-primary-300"
            />
            <AllocationBar
              label="Hedging"
              value={portfolio.allocation_breakdown.hedging || 0}
              color="bg-gray-400"
            />
          </div>
        </div>

        <div className="card">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">
            Sector Breakdown
          </h3>
          <div className="space-y-2">
            {Object.entries(portfolio.sector_breakdown)
              .sort(([, a], [, b]) => b - a)
              .map(([sector, allocation]) => (
                <AllocationBar
                  key={sector}
                  label={sector}
                  value={allocation}
                  color="bg-success-500"
                />
              ))}
          </div>
        </div>
      </div>

      {/* Risk Metrics (if available) */}
      {portfolio.risk_metrics && (
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">
            Risk Metrics (30-Day)
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {portfolio.risk_metrics.sharpe_ratio_30d != null && (
              <MetricCard
                label="Sharpe Ratio"
                value={portfolio.risk_metrics.sharpe_ratio_30d.toFixed(2)}
              />
            )}
            {portfolio.risk_metrics.volatility_30d != null && (
              <MetricCard
                label="Volatility"
                value={formatPercent(portfolio.risk_metrics.volatility_30d)}
              />
            )}
            {portfolio.risk_metrics.max_drawdown != null && (
              <MetricCard
                label="Max Drawdown"
                value={formatPercent(portfolio.risk_metrics.max_drawdown)}
                valueColor={getValueColorClass(portfolio.risk_metrics.max_drawdown)}
              />
            )}
            {portfolio.risk_metrics.beta_to_spy != null && (
              <MetricCard
                label="Beta (SPY)"
                value={portfolio.risk_metrics.beta_to_spy.toFixed(2)}
              />
            )}
            {portfolio.risk_metrics.correlation_to_spy != null && (
              <MetricCard
                label="Correlation"
                value={portfolio.risk_metrics.correlation_to_spy.toFixed(2)}
              />
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Helper Components

function AllocationBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium text-gray-900">{formatPercent(value, 1)}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`${color} h-2 rounded-full transition-all`}
          style={{ width: `${value * 100}%` }}
        />
      </div>
    </div>
  )
}

function MetricCard({
  label,
  value,
  valueColor = 'text-gray-900',
}: {
  label: string
  value: string
  valueColor?: string
}) {
  return (
    <div>
      <p className="text-xs text-gray-500">{label}</p>
      <p className={`text-lg font-semibold ${valueColor}`}>{value}</p>
    </div>
  )
}
