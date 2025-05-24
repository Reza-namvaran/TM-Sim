class TuringError(Exception):
    """Base class for all Turing-related errors"""

class InvalidMachineError(Exception):
    """Raised for invalid machine configurations"""
    
class SimulationError(TuringError):
    """Raised during machine execution"""
