import { useState, useEffect } from 'react'
import type { DailyAnalysis, PortfolioState, APIError } from './types'
import { fetchLatestAnalysis, fetchPortfolio, getMockPortfolio, handleAPIError } from './services/api'
import Dashboard from './components/Dashboard'
import LoadingSpinner from './components/LoadingSpinner'
import ErrorDisplay from './components/ErrorDisplay'
import AnalysisControl from './components/AnalysisControl'

function App() {
  const [portfolio, setPortfolio] = useState<PortfolioState | null>(null)
  const [analysis, setAnalysis] = useState<DailyAnalysis | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<APIError | null>(null)
  const [useMockData, setUseMockData] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    setIsLoading(true)
    setError(null)

    try {
      // Try to fetch real data
      const [portfolioData, analysisData] = await Promise.all([
        fetchPortfolio(),
        fetchLatestAnalysis(),
      ])

      setPortfolio(portfolioData)
      setAnalysis(analysisData)
      setUseMockData(false)
    } catch (err) {
      console.error('Failed to load data:', err)

      // Fallback to mock data for development
      console.warn('Using mock data for development')
      setPortfolio(getMockPortfolio())
      setUseMockData(true)

      // Set error for display
      setError(handleAPIError(err))
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (error && !useMockData) {
    return (
      <ErrorDisplay
        error={error}
        onRetry={loadData}
      />
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                ETF Justification Engine
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Automated ETF analysis with professional trade recommendations
              </p>
            </div>
            {useMockData && (
              <div className="badge bg-warning-100 text-warning-800">
                Using Mock Data
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Analysis Control */}
        <div className="mb-6">
          <AnalysisControl onAnalysisComplete={loadData} />
        </div>

        {/* Dashboard */}
        {portfolio && (
          <Dashboard
            portfolio={portfolio}
            analysis={analysis}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            Built with staff engineer-level code quality | Econ 425 Investment Project
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
