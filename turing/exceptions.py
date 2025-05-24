class TuringError(Exception):
    """Base class for all Turing-related errors"""

class SimulationError(TuringError):
    """Raised during machine execution"""
