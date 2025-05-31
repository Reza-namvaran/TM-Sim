import requests
import time

BASE_URL = "http://localhost:5000"
MACHINE_NAME = "Palindrome Checker"
INPUT_STRING = "abba" 
MAX_STEPS = 100

def run_simulation():
    print(f"\nStarting simulation for '{MACHINE_NAME}' with input: '{INPUT_STRING}'")
    
    # Get the machine configuration first
    print(f"Fetching machine configuration for {MACHINE_NAME}...")
    machine_config = requests.get(f"{BASE_URL}/machine/{MACHINE_NAME}").json()
    if 'error' in machine_config:
        print(f"Error: {machine_config['error']}")
        return
    
    final_states = machine_config.get('final_states', [])
    blank_symbol = machine_config.get('blank_symbol', '_')
    print(f"Blank symbol: '{blank_symbol}'")
    print(f"Final states: {final_states}")
    
    # Initialize the simulation
    print("\n=== Initializing Machine ===")
    init_data = {
        "machine": MACHINE_NAME,
        "input": INPUT_STRING
    }
    init_response = requests.post(
        f"{BASE_URL}/simulate/init",
        json=init_data
    )
    
    if init_response.status_code != 200:
        print(f"Initialization failed: {init_response.text}")
        return
        
    state = init_response.json()
    print(f"State: {state['state']}")
    print(f"Tape: {state['tapes'][0]}")
    print(f"Head: {state['heads'][0]}")
    
    # Run simulation until halt
    step_count = 0
    while not state.get('halt', False) and step_count < MAX_STEPS:
        step_count += 1
        
        # Execute step
        step_data = {
            "machine": MACHINE_NAME,
            "state": state["state"],
            "tapes": state["tapes"],
            "heads": state["heads"],
            "halt": state.get("halt", False)
        }
        
        step_response = requests.post(
            f"{BASE_URL}/simulate/step",
            json=step_data
        )
        
        if step_response.status_code != 200:
            print(f"Step {step_count} failed: {step_response.text}")
            return
            
        state = step_response.json()
        
        print(f"\nStep {step_count}:")
        print(f"State: {state['state']}")
        print(f"Tape: {state['tapes'][0]}")
        print(f"Head position: {state['heads'][0]}")
        
        head_pos = state['heads'][0]
        tape = state['tapes'][0]
        if head_pos < len(tape):
            current_symbol = tape[head_pos]
        else:
            current_symbol = blank_symbol  # Use blank symbol if beyond tape
        print(f"Head → Symbol: '{current_symbol}'")
        
        time.sleep(0.5)
    
    print("\n" + "="*50)
    print(f"Simulation completed in {step_count} steps")
    print(f"Final state: {state['state']}")
    
    if state['state'] in final_states:
        print("STRING ACCEPTED")
    else:
        print("STRING REJECTED")
    print("="*50)

if __name__ == "__main__":
    run_simulation()