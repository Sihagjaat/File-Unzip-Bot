from datetime import datetime


def format_size(bytes_size):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def format_date(date):
    """Format datetime to readable string"""
    if not date:
        return "Never"
    return date.strftime("%d %b %Y, %I:%M %p")


def format_duration(seconds):
    """Convert seconds to human-readable duration"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def calculate_usdt_price(inr_price):
    """Convert INR to USDT (1 USDT = 100 INR)"""
    return round(inr_price / 100, 2)


def progress_bar(current, total, width=20):
    """Generate a horizontal progress bar"""
    percentage = (current / total) * 100
    filled = int(width * current / total)
    bar = '█' * filled + '░' * (width - filled)
    return f"{bar} {percentage:.1f}%"


def get_file_extension(filename):
    """Get file extension from filename"""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def is_archive_file(filename):
    """Check if file is a supported archive"""
    from config import SUPPORTED_EXTENSIONS
    ext = get_file_extension(filename)
    return f'.{ext}' in SUPPORTED_EXTENSIONS
