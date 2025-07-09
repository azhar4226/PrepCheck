"""
Timezone utility functions for IST handling across the application
All dates and times are handled in IST (India Standard Time)
"""

from datetime import datetime, timezone, timedelta
import pytz

# IST timezone
IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    """Get current datetime in IST timezone"""
    return datetime.now(IST)

def utc_to_ist(utc_dt):
    """Convert UTC datetime to IST"""
    if utc_dt is None:
        return None
    
    # If the datetime is naive (no timezone info), assume it's UTC
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    
    # Convert to IST
    return utc_dt.astimezone(IST)

def ist_to_utc(ist_dt):
    """Convert IST datetime to UTC for database storage"""
    if ist_dt is None:
        return None
    
    # If the datetime is naive, assume it's IST
    if ist_dt.tzinfo is None:
        ist_dt = IST.localize(ist_dt)
    
    # Convert to UTC and remove timezone info for database storage
    return ist_dt.astimezone(timezone.utc).replace(tzinfo=None)

def format_ist_datetime(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """Format datetime in IST timezone"""
    if dt is None:
        return None
    
    ist_dt = utc_to_ist(dt)
    if ist_dt is None:
        return None
    return ist_dt.strftime(format_str)

def format_ist_date(dt):
    """Format date in IST timezone"""
    return format_ist_datetime(dt, '%Y-%m-%d')

def format_ist_time(dt):
    """Format time in IST timezone"""
    return format_ist_datetime(dt, '%H:%M:%S')

def parse_ist_datetime(date_str, format_str='%Y-%m-%d %H:%M:%S'):
    """Parse datetime string as IST and return UTC datetime for storage"""
    if not date_str:
        return None
    
    # Parse the datetime string
    ist_dt = datetime.strptime(date_str, format_str)
    
    # Localize to IST and convert to UTC for storage
    ist_dt = IST.localize(ist_dt)
    return ist_dt.astimezone(timezone.utc).replace(tzinfo=None)

def get_ist_isoformat(dt):
    """Get ISO format string in IST timezone"""
    if dt is None:
        return None
    
    ist_dt = utc_to_ist(dt)
    if ist_dt is None:
        return None
    return ist_dt.isoformat()

def current_ist_timestamp():
    """Get current timestamp in IST for database storage"""
    return ist_to_utc(get_ist_now())
