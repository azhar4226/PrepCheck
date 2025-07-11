/**
 * Timezone utility functions for consistent IST handling in the frontend
 */

// IST timezone constant
const IST_TIMEZONE = 'Asia/Kolkata';

/**
 * Get current date/time in IST
 */
export const getCurrentISTTime = () => {
  return new Date().toLocaleString('en-IN', {
    timeZone: IST_TIMEZONE
  });
};

/**
 * Format date in IST timezone
 */
export const formatISTDate = (dateString, options = {}) => {
  if (!dateString) return '';
  
  const defaultOptions = {
    timeZone: IST_TIMEZONE,
    year: 'numeric',
    month: 'short',
    day: '2-digit'
  };
  
  const finalOptions = { ...defaultOptions, ...options };
  
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', finalOptions);
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Invalid Date';
  }
};

/**
 * Format datetime in IST timezone
 */
export const formatISTDateTime = (dateString, options = {}) => {
  if (!dateString) return '';
  
  const defaultOptions = {
    timeZone: IST_TIMEZONE,
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  };
  
  const finalOptions = { ...defaultOptions, ...options };
  
  try {
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', finalOptions);
  } catch (error) {
    console.error('Error formatting datetime:', error);
    return 'Invalid Date';
  }
};

/**
 * Format time in IST timezone
 */
export const formatISTTime = (dateString, options = {}) => {
  if (!dateString) return '';
  
  const defaultOptions = {
    timeZone: IST_TIMEZONE,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  };
  
  const finalOptions = { ...defaultOptions, ...options };
  
  try {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-IN', finalOptions);
  } catch (error) {
    console.error('Error formatting time:', error);
    return 'Invalid Time';
  }
};

/**
 * Get relative time in IST (e.g., "2 hours ago", "yesterday")
 */
export const getRelativeTimeIST = (dateString) => {
  if (!dateString) return '';
  
  try {
    const date = new Date(dateString);
    const now = new Date();
    
    // Convert both dates to IST for comparison
    const istDate = new Date(date.toLocaleString('en-US', { timeZone: IST_TIMEZONE }));
    const istNow = new Date(now.toLocaleString('en-US', { timeZone: IST_TIMEZONE }));
    
    const diffInMinutes = Math.floor((istNow - istDate) / (1000 * 60));
    
    if (diffInMinutes < 1) {
      return 'Just now';
    } else if (diffInMinutes < 60) {
      return `${diffInMinutes} minute${diffInMinutes === 1 ? '' : 's'} ago`;
    } else if (diffInMinutes < 1440) { // Less than 24 hours
      const hours = Math.floor(diffInMinutes / 60);
      return `${hours} hour${hours === 1 ? '' : 's'} ago`;
    } else if (diffInMinutes < 43200) { // Less than 30 days
      const days = Math.floor(diffInMinutes / 1440);
      return `${days} day${days === 1 ? '' : 's'} ago`;
    } else {
      // For older dates, show formatted date
      return formatISTDate(dateString);
    }
  } catch (error) {
    console.error('Error calculating relative time:', error);
    return 'Invalid Date';
  }
};

/**
 * Check if a date is today in IST
 */
export const isToday = (dateString) => {
  if (!dateString) return false;
  
  try {
    const date = new Date(dateString);
    const today = new Date();
    
    // Convert both to IST dates
    const istDate = new Date(date.toLocaleString('en-US', { timeZone: IST_TIMEZONE }));
    const istToday = new Date(today.toLocaleString('en-US', { timeZone: IST_TIMEZONE }));
    
    return istDate.toDateString() === istToday.toDateString();
  } catch (error) {
    return false;
  }
};

/**
 * Check if a date is yesterday in IST
 */
export const isYesterday = (dateString) => {
  if (!dateString) return false;
  
  try {
    const date = new Date(dateString);
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    
    // Convert both to IST dates
    const istDate = new Date(date.toLocaleString('en-US', { timeZone: IST_TIMEZONE }));
    const istYesterday = new Date(yesterday.toLocaleString('en-US', { timeZone: IST_TIMEZONE }));
    
    return istDate.toDateString() === istYesterday.toDateString();
  } catch (error) {
    return false;
  }
};

/**
 * Get IST timezone offset string
 */
export const getISTOffset = () => {
  return '+05:30';
};

/**
 * Convert UTC date to IST for display
 */
export const utcToIST = (utcDate) => {
  if (!utcDate) return null;
  
  try {
    const date = new Date(utcDate);
    return new Date(date.toLocaleString('en-US', { timeZone: IST_TIMEZONE }));
  } catch (error) {
    console.error('Error converting UTC to IST:', error);
    return null;
  }
};

/**
 * Format duration in a human-readable format
 */
export const formatDuration = (seconds) => {
  if (!seconds || seconds === 0) return '0 seconds';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;
  
  const parts = [];
  
  if (hours > 0) {
    parts.push(`${hours} hour${hours === 1 ? '' : 's'}`);
  }
  
  if (minutes > 0) {
    parts.push(`${minutes} minute${minutes === 1 ? '' : 's'}`);
  }
  
  if (remainingSeconds > 0 || parts.length === 0) {
    parts.push(`${remainingSeconds} second${remainingSeconds === 1 ? '' : 's'}`);
  }
  
  return parts.join(' ');
};

/**
 * Get current IST timestamp for API calls
 */
export const getCurrentISTTimestamp = () => {
  return new Date().toISOString();
};

/**
 * Default export with all functions
 */
export default {
  getCurrentISTTime,
  formatISTDate,
  formatISTDateTime,
  formatISTTime,
  getRelativeTimeIST,
  isToday,
  isYesterday,
  getISTOffset,
  utcToIST,
  formatDuration,
  getCurrentISTTimestamp,
  IST_TIMEZONE
};
