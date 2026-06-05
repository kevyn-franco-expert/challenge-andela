class WatchdogException(Exception):
    """Base application exception."""
    pass


class ParseException(WatchdogException):
    """Raised when log parsing fails."""
    pass


class DetectionException(WatchdogException):
    """Raised when anomaly detection fails."""
    pass


class DispatchException(WatchdogException):
    """Raised when webhook dispatch fails."""
    pass
