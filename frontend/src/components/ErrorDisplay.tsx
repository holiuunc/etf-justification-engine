import type { APIError } from '../types'

interface ErrorDisplayProps {
  error: APIError
  onRetry?: () => void
}

export default function ErrorDisplay({ error, onRetry }: ErrorDisplayProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full">
        <div className="card text-center">
          <div className="text-danger-600 mb-4">
            <svg
              className="h-16 w-16 mx-auto"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Failed to Load Data
          </h2>
          <p className="text-gray-600 mb-1">{error.message}</p>
          {error.details && (
            <p className="text-sm text-gray-500 mb-4">{error.details}</p>
          )}
          {onRetry && (
            <button
              onClick={onRetry}
              className="btn btn-primary mt-4"
            >
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
