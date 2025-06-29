from .exceptions import SimulationError

class TuringMachine: 
    def __init__(self, config : dict):
        self.number_of_tapes = config['tapes']
        self.blank_symbol = config['blank_symbol']
        self.transitions = config['transition']
        self.initial_state = config['initial_state']

        self.final_states = config.get('final_states', [])
        if not self.final_states and 'final_state' in config:
            self.final_states = [config['final_state']]

        # Initialize tapes and heads
        self.tapes = []
        self.heads = [0] * self.number_of_tapes
        self.current_state = self.initial_state
        self.halt = False
        self.step_count = 0

    def initialize_tape(self, inputs:  list[str]) -> None: 
        """Initialize tapes with input strings"""
        self.tapes = []
        for i in range(self.number_of_tapes):
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
            self.halt = True
            self.logger.info(f"Reached final state: {self.current_state}")

    def _read_symbols(self) -> list:
        symbols = []
        for i in range(self.number_of_tapes):
            if self.heads[i] < len(self.tapes[i]):
                symbols.append(self.tapes[i][self.heads[i]])
            else:
                symbols.append(self.blank_symbol)
        return symbols

    def _find_transition(self, symbols) -> list[list[str]]:
        for trans in self.transitions:
            if (trans[0][0] == self.current_state and 
                trans[0][1] == symbols):
                return trans
        return None
   
    def _apply_transition(self, transition) -> None:
        new_state, write_symbols, moves = transition[1]
        self.current_state = new_state

        for i in range(self.number_of_tapes):
            # Ensure tape has enough cells BEFORE writing
            while self.heads[i] >= len(self.tapes[i]):
                self.tapes[i].append(self.blank_symbol)
                
            # Write symbol
            self.tapes[i][self.heads[i]] = write_symbols[i]
            
            # Move head
            if moves[i] == 'R':
                self.heads[i] += 1
            elif moves[i] == 'L':
                self.heads[i] = max(0, self.heads[i] - 1)
                
            # Ensure tape has enough cells AFTER moving
            while self.heads[i] >= len(self.tapes[i]):
                self.tapes[i].append(self.blank_symbol)