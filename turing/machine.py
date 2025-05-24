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

        def initialize_tape() -> None: pass 