import { useState, useEffect } from 'react'
import { startAnalysis, getAnalysisProgress } from '../services/api'
import type { AnalysisStatus } from '../types'

interface AnalysisControlProps {
  onAnalysisComplete?: () => void
}

export default function AnalysisControl({ onAnalysisComplete }: AnalysisControlProps) {
  const [status, setStatus] = useState<AnalysisStatus | null>(null)
  const [isStarting, setIsStarting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Poll for progress updates when analysis is running
  useEffect(() => {
    let intervalId: number | undefined

    const pollProgress = async () => {
      try {
        const progressData = await getAnalysisProgress()
        setStatus(progressData)

        // If analysis just completed, trigger callback and stop polling
        if (!progressData.running && status?.running && progressData.progress === 100) {
          onAnalysisComplete?.()
        }
      } catch (err) {
        console.error('Failed to fetch progress:', err)
      }
    }

    // Only poll if analysis is running
    if (status?.running) {
      intervalId = window.setInterval(pollProgress, 2000) // Poll every 2 seconds
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId)
      }
    }
  }, [status?.running, onAnalysisComplete])

  // Initial status check on mount
  useEffect(() => {
    getAnalysisProgress()
      .then(setStatus)
      .catch(err => console.error('Failed to get initial status:', err))
  }, [])

  const handleStartAnalysis = async () => {
    setIsStarting(true)
    setError(null)

    try {
      await startAnalysis()

      // Immediately poll for progress to update UI
      const progressData = await getAnalysisProgress()
      setStatus(progressData)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start analysis'
      setError(errorMessage)
      console.error('Failed to start analysis:', err)
    } finally {
      setIsStarting(false)
    }
  }

  const isRunning = status?.running || false
  const progress = status?.progress || 0
  const message = status?.message || 'Ready to run analysis'

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Analysis Control</h2>
        <p className="card-subtitle">Manually trigger ETF analysis</p>
      </div>

      <div className="space-y-4">
        {/* Status Message */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {isRunning && (
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary-500 border-t-transparent" />
            )}
            <span className={`text-sm font-medium ${isRunning ? 'text-primary-700' : 'text-gray-600'}`}>
              {message}
            </span>
          </div>
          {isRunning && (
            <span className="text-sm font-bold text-primary-700">
              {progress.toFixed(0)}%
            </span>
          )}
        </div>

        {/* Progress Bar */}
        {isRunning && (
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className="bg-primary-500 h-3 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="p-3 bg-danger-50 border border-danger-200 rounded-lg">
            <p className="text-sm text-danger-800">{error}</p>
          </div>
        )}

        {/* Action Button */}
        <button
          onClick={handleStartAnalysis}
          disabled={isRunning || isStarting}
          className={`
            w-full py-3 px-4 rounded-lg font-semibold text-white
            transition-all duration-200
            ${
              isRunning || isStarting
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-primary-600 hover:bg-primary-700 active:bg-primary-800'
            }
          `}
        >
          {isStarting ? 'Starting...' : isRunning ? 'Analysis Running...' : 'Run Analysis Now'}
        </button>

        {/* Info Text */}
        <p className="text-xs text-gray-500 text-center">
          Analysis typically takes 2-5 minutes to complete.
          {isRunning && ' You can leave this page while it runs.'}
        </p>
      </div>
    </div>
  )
}
