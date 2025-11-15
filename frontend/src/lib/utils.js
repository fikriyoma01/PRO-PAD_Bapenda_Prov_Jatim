import { clsx } from 'clsx';

/**
 * Utility function for merging class names
 */
export function cn(...inputs) {
  return clsx(inputs);
}

/**
 * Format number to Indonesian Rupiah
 */
export function formatRupiah(number) {
  if (!number && number !== 0) return 'Rp 0';

  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(number);
}

/**
 * Format large numbers with K, M, B, T suffixes
 */
export function formatCompactNumber(number) {
  if (!number && number !== 0) return '0';

  const absNum = Math.abs(number);
  const sign = number < 0 ? '-' : '';

  if (absNum >= 1e12) {
    return `${sign}${(absNum / 1e12).toFixed(2)} T`;
  } else if (absNum >= 1e9) {
    return `${sign}${(absNum / 1e9).toFixed(2)} M`;
  } else if (absNum >= 1e6) {
    return `${sign}${(absNum / 1e6).toFixed(2)} Jt`;
  } else if (absNum >= 1e3) {
    return `${sign}${(absNum / 1e3).toFixed(2)} Rb`;
  }
  return `${sign}${absNum.toFixed(2)}`;
}

/**
 * Format percentage
 */
export function formatPercentage(number, decimals = 2) {
  if (!number && number !== 0) return '0%';
  return `${number.toFixed(decimals)}%`;
}

/**
 * Calculate percentage change
 */
export function calculatePercentageChange(oldValue, newValue) {
  if (!oldValue || oldValue === 0) return 0;
  return ((newValue - oldValue) / oldValue) * 100;
}

/**
 * Parse CSV string to array of objects
 */
export function parseCSV(csvText) {
  const lines = csvText.trim().split('\n');
  const headers = lines[0].split(',').map(h => h.trim());

  return lines.slice(1).map(line => {
    const values = line.split(',').map(v => v.trim());
    return headers.reduce((obj, header, index) => {
      obj[header] = values[index];
      return obj;
    }, {});
  });
}

/**
 * Deep clone an object
 */
export function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}

/**
 * Debounce function
 */
export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Calculate statistics from array of numbers
 */
export function calculateStats(numbers) {
  if (!numbers || numbers.length === 0) {
    return {
      mean: 0,
      median: 0,
      std: 0,
      min: 0,
      max: 0,
    };
  }

  const sorted = [...numbers].sort((a, b) => a - b);
  const mean = numbers.reduce((sum, n) => sum + n, 0) / numbers.length;
  const median = sorted.length % 2 === 0
    ? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
    : sorted[Math.floor(sorted.length / 2)];

  const variance = numbers.reduce((sum, n) => sum + Math.pow(n - mean, 2), 0) / numbers.length;
  const std = Math.sqrt(variance);

  return {
    mean,
    median,
    std,
    min: sorted[0],
    max: sorted[sorted.length - 1],
  };
}
