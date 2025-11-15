/**
 * Utility Functions for Formatting
 * Numbers, dates, percentages, currency, etc.
 */

import { format, formatDistance, parseISO } from 'date-fns'

// ============================================================================
// Number Formatting
// ============================================================================

/**
 * Format number as currency (USD)
 */
export function formatCurrency(value: number, decimals: number = 2): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

/**
 * Format number as compact currency (e.g., $1.2M, $500K)
 */
export function formatCompactCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value)
}

/**
 * Format number as percentage
 */
export function formatPercent(value: number, decimals: number = 2): string {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
    signDisplay: 'always',
  }).format(value)
}

/**
 * Format number with thousands separator
 */
export function formatNumber(value: number, decimals: number = 0): string {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value)
}

/**
 * Format large numbers in compact notation (K, M, B)
 */
export function formatCompactNumber(value: number): string {
  return new Intl.NumberFormat('en-US', {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value)
}

// ============================================================================
// Date Formatting
// ============================================================================

/**
 * Format ISO date string to human-readable format
 */
export function formatDate(dateString: string, formatStr: string = 'MMM dd, yyyy'): string {
  try {
    const date = parseISO(dateString)
    return format(date, formatStr)
  } catch {
    return dateString
  }
}

/**
 * Format ISO datetime string to human-readable format
 */
export function formatDateTime(dateString: string): string {
  return formatDate(dateString, 'MMM dd, yyyy h:mm a')
}

/**
 * Format date as relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(dateString: string): string {
  try {
    const date = parseISO(dateString)
    return formatDistance(date, new Date(), { addSuffix: true })
  } catch {
    return dateString
  }
}

// ============================================================================
// Color Helpers
// ============================================================================

/**
 * Get color class for positive/negative values
 */
export function getValueColorClass(value: number): string {
  if (value > 0) return 'text-success-600'
  if (value < 0) return 'text-danger-600'
  return 'text-gray-600'
}

/**
 * Get background color class for positive/negative values
 */
export function getValueBgColorClass(value: number): string {
  if (value > 0) return 'bg-success-50'
  if (value < 0) return 'bg-danger-50'
  return 'bg-gray-50'
}

/**
 * Get color for risk mode
 */
export function getRiskModeColor(riskMode: string): string {
  switch (riskMode.toLowerCase()) {
    case 'normal':
      return 'text-success-600 bg-success-50'
    case 'caution':
      return 'text-warning-600 bg-warning-50'
    case 'risk_off':
      return 'text-danger-600 bg-danger-50'
    case 'extreme_complacency':
      return 'text-primary-600 bg-primary-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

/**
 * Get color for priority level
 */
export function getPriorityColor(priority: string): string {
  switch (priority.toLowerCase()) {
    case 'high':
      return 'text-danger-600 bg-danger-50'
    case 'medium':
      return 'text-warning-600 bg-warning-50'
    case 'low':
      return 'text-gray-600 bg-gray-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

/**
 * Get color for action type
 */
export function getActionColor(action: string): string {
  switch (action.toUpperCase()) {
    case 'BUY':
    case 'INITIATE':
    case 'ADD':
      return 'text-success-700 bg-success-100 font-semibold'
    case 'SELL':
    case 'TRIM':
      return 'text-danger-700 bg-danger-100 font-semibold'
    case 'HOLD':
      return 'text-gray-700 bg-gray-100'
    default:
      return 'text-gray-700 bg-gray-100'
  }
}

// ============================================================================
// Text Helpers
// ============================================================================

/**
 * Truncate text to specified length
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

/**
 * Capitalize first letter
 */
export function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1)
}

/**
 * Convert snake_case to Title Case
 */
export function snakeToTitle(text: string): string {
  return text
    .split('_')
    .map(capitalize)
    .join(' ')
}

// ============================================================================
// Validation
// ============================================================================

/**
 * Check if value is valid number
 */
export function isValidNumber(value: any): value is number {
  return typeof value === 'number' && !isNaN(value) && isFinite(value)
}

/**
 * Safe number formatting (returns fallback if invalid)
 */
export function safeFormatNumber(
  value: any,
  formatter: (v: number) => string,
  fallback: string = 'N/A'
): string {
  return isValidNumber(value) ? formatter(value) : fallback
}
