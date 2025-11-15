export default function LoadingSpinner() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="spinner h-16 w-16 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading ETF analysis...</p>
      </div>
    </div>
  )
}
