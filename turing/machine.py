from .exceptions import SimulationError
import logging

logger = logging.getLogger(__name__)

class TuringMachine: 
    def __init__(self, config : dict):
        self.number_of_tape = config['tapes']
        self.blank_symbol = config['blank_symbol']
        self.transitions = config['transition']
        self.iniial_state = config['initial_state']
        self.final_state = config.get('final_state', [])

        # Initialize tapes and heads
        self.tapes = []
        self.heads = [0] * self.number_of_tape
        self.current_state = self.iniial_state
        self.halt = False
        self.step_count = 0

        # Logging properties
        self.logger = logger.getChild(self.__class__.__name__)
        self.logger.debug("Initializing Turing Machine with config: %s", config)

        def initialize_tape(self, inputs:  list[str]) -> None: 
            """Initialize tapes with input strings"""
            self.tapes = []
            for i in range(self.number_of_tape):
                input_str = inputs[i] if i < len(inputs) else ''
                self.tapes.append(list(input_str.strip()))
        
        def step(self) -> None:
            if self.halt:
                self.logger.warning("Attempted to step halted machine")
                raise SimulationError("Machine Already Halted!")

            self.logger.debug(
                "Step %d - State: %s, Heads: %s, Tapes: %s",
                self.step_count, self.current_state, self.heads, self.tapes
            )

            current_symbols = self._read_symbols()
            transition = self._find_transition(current_symbols)

            if not transition:
                self.halt = True
                return
            
            self._apply_transition(transition)
            self.step_count += 1

            self.logger.debug(
                "After transition - New state: %s, Heads: %s, Tapes: %s",
                self.current_state, self.heads, self.tapes
            )

            if self.current_state in self.final_states:
                self.halted = True

        def _read_symbol():
            pass

        def _apply_transition(self, transition):
            pass

        def _find_transition(self, symbols):
            pass