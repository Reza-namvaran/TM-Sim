from flask import Flask, render_template, request, jsonify
from turing import TuringMachine, parse_machine, InvalidMachineError, SimulationError
import logging
import yaml
import os
import sys

app = Flask(__name__)
app.config.from_object("config.Config")

if app.config.get('LOG_TO_FILE', False):
    # Local development: log to file
    logging.basicConfig(
        level=app.config['LOG_LEVEL'],
        format=app.config['LOG_FORMAT'],
        filename=app.config['LOG_FILE']
    )
else:
    # Production: log to stdout
    logging.basicConfig(
        level=app.config['LOG_LEVEL'],
        format=app.config['LOG_FORMAT'],
        stream=sys.stdout
    )

logger = logging.getLogger(__name__)

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), 'samples')
samples = {}

for filename in os.listdir(SAMPLE_DIR):
    if filename.endswith(('.yml', '.yaml')):
        try:
            with open(os.path.join(SAMPLE_DIR, filename), 'r') as sample_file:
                content = sample_file.read()
                config = parse_machine(content)
                samples[config['name']] = config
                logger.info(f"Loaded Machine {config['name']}")
        except Exception as err: 
            logger.error(f"Error Loading {filename}: {str(err)}")



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/debug/samples')
def debug_samples():
    return jsonify({
        "sample_dir": SAMPLE_DIR,
        "loaded_samples": list(samples.keys())
    })

@app.route('/machines')
def list_machines():
    """List all available machines"""
    return jsonify(list(samples.keys()))

@app.route('/machine/<name>')
def get_machine(name):
    """Get configuration for a specific machine"""
    if name in samples:
        return jsonify(samples[name])
    return jsonify({"error": "Machine not found"}), 404

@app.route('/simulate/init', methods=["POST"])
def init_simulate():
    data = request.get_json()
    machine_name = data.get('machine')
    input_string = data.get('input', '')

    if machine_name not in samples:
        return jsonify({"error": "Machine not found"}), 404

    config = samples[machine_name]

    try:
        machine = TuringMachine(config)
        machine.initialize_tape([input_string])


        response = {
            "state": machine.current_state,
            "tapes": machine.tapes,
            "heads": machine.heads,
            "halt": machine.halt 
        }
        return jsonify(response)
    except Exception as err:
        logger.error(f"Initilization error: {str(err)}")
        return jsonify({"error": str(err)}), 400

@app.route('/simulate/step', methods=["POST"])
def step_simulation():
    """Execute a single step in the simulation"""
    data = request.get_json()
    machine_name = data.get('machine')
    current_state = data.get('state')
    tapes = data.get('tapes')
    heads = data.get('heads')
    halted = data.get('halt', False)
    
    if machine_name not in samples:
        return jsonify({"error": "Machine not found"}), 404
    
    config = samples[machine_name]
    
    try:
        # Recreate machine at current state
        machine = TuringMachine(config)
        machine.current_state = current_state
        machine.tapes = tapes
        machine.heads = heads
        machine.halt = halted
        
        # Execute step
        if not machine.halt:
            machine.step()
        
        # Prepare response
        response = {
            "state": machine.current_state,
            "tapes": machine.tapes,
            "heads": machine.heads,
            "halt": machine.halt,
            "step_count": machine.step_count
        }
        return jsonify(response)
    
    except SimulationError as e:
        logger.warning(f"Simulation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Step error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)