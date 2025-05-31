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

if __name__ == '__main__':
    app.run(debug=True)