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

def _validate_config():
    pass

def _normalize_transitions(config):
    pass