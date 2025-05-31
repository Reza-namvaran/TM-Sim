from flask import Flask, render_template, request, jsonify
from turing import TuringMachine, parse_machine, InvalidMachineError, SimulationError
import logging
import yaml
import os

app = Flask(__name__)
app.config.from_object("config.Config")

logging.basicConfig(level=app.config['LOG_LEVEL'],
                    format=app.config['LOG_FORMAT'],
                    filename=app.config['LOG_FILE'])
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
            "halted": machine.halt 
        }
        return jsonify(response)
    except Exception as err:
        logger.error(f"Initilization error: {str(err)}")
        return jsonify({"error": str(err)}), 400

if __name__ == '__main__':
    app.run(debug=True)