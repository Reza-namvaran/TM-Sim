import yaml
from .exceptions import InvalidMachineError

def parse_machine(yaml_content):
    try:
        config = yaml.safe_load(yaml_content)
        _validate_config(config)
        _normalize_transitions(config)
        return config
    
    except yaml.YAMLError as e:
        raise InvalidMachineError(f"Invalid YAML: {str(e)}")

def _validate_config(config) -> None:
    required = [
        "name",
        "tapes",
        "blank_symbol",
        "initial_state",
        "transition"
    ]

    # Check required fields
    for field in required:
        if field not in config:
            raise InvalidMachineError(f"Missing required field: {field}")
    
    if not isinstance(config["tapes"], int) or config["tapes"] < 1:
        raise InvalidMachineError("Number of tapes must be a positive integer")

    if "final_state" not in config and "final_states" not in config:
        config["final_states"] = [config["final_state"]]


    for i, trans in enumerate(config['transition']):
        # Validate read symbols
        if len(trans[0][1]) != config['tapes']:
            raise InvalidMachineError(
                f"Transition {i+1}: Expected {config['tapes']} read symbols, "
                f"got {len(trans[0][1])}"
            )
        
        # Validate write symbols
        if len(trans[1][1]) != config['tapes']:
            raise InvalidMachineError(
                f"Transition {i+1}: Expected {config['tapes']} write symbols, "
                f"got {len(trans[1][1])}"
            )
        
        # Validate move directions
        if len(trans[1][2]) != config['tapes']:
            raise InvalidMachineError(
                f"Transition {i+1}: Expected {config['tapes']} move directions, "
                f"got {len(trans[1][2])}"
            )
        
        # Validate move direction values
        valid_moves = {'L', 'R', 'N'}
        for move in trans[1][2]:
            if move.upper() not in valid_moves:
                raise InvalidMachineError(
                    f"Transition {i+1}: Invalid move direction '{move}'. "
                    f"Valid values: L, R, N"
                )

def _normalize_transitions(config):
    normalized = []
    for trans in config['transition']:
        normalized.append([
            [str(trans[0][0]).strip(), 
             [str(s).strip() for s in trans[0][1]]],
            [str(trans[1][0]).strip(),
             [str(s).strip() for s in trans[1][1]],
             [str(m).upper().strip() for m in trans[1][2]]]
        ])
    config['transition'] = normalized