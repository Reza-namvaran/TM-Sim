// Global state
let currentSimulation = null;
let currentMachineConfig = null;
let autoStepInterval = null;
let isAutoStepping = false;
let historyStack = [];       // stores all steps for current input
let currentHistoryIndex = -1; // tracks current step for undo

// DOM elements
const machineSelect = document.getElementById('machine-select');
const inputField = document.getElementById('input-string');
const initBtn = document.getElementById('init-btn');
const stepBtn = document.getElementById('step-btn');
const resetBtn = document.getElementById('reset-btn');
const tapesContainer = document.getElementById('tapes-container');
const stateDisplay = document.getElementById('state-display');
const stepDisplay = document.getElementById('step-display');
const statusDisplay = document.getElementById('status-display');
const autoStepBtn = document.getElementById('auto-step-btn');
const speedControl = document.getElementById('speed-control');

// Initialize application
function initApp() {
    loadMachines();
    resetSimulation();
    
    // Add event listeners
    initBtn.addEventListener('click', initSimulation);
    stepBtn.addEventListener('click', stepSimulation);
    resetBtn.addEventListener('click', resetSimulation);
    autoStepBtn.addEventListener('click', toggleAutoStep); 
    speedControl.addEventListener('input', updateSpeed);
    machineSelect.addEventListener('change', async () => {
        await loadMachineConfig(machineSelect.value);
        resetSimulation();
    });
    speedControl.addEventListener('input', function() {
        document.getElementById('speed-display').textContent = this.value + 'ms';
    });
    document.getElementById('speed-display').textContent = speedControl.value + 'ms';    
}

function toggleAutoStep() {
    if (!currentSimulation || currentSimulation.halt) {
        showError('Cannot start auto-step without a running simulation');
        return;
    }
    
    if (isAutoStepping) {
        // Stop auto-stepping
        clearInterval(autoStepInterval);
        autoStepInterval = null;
        isAutoStepping = false;
        autoStepBtn.textContent = 'Play';
        autoStepBtn.classList.remove('active');
        stepBtn.disabled = false;
    } else {
        // Start auto-stepping
        const speed = parseInt(speedControl.value);
        isAutoStepping = true;
        autoStepBtn.textContent = 'Pause';
        autoStepBtn.classList.add('active');
        stepBtn.disabled = true;
        
        // Start the interval
        autoStepInterval = setInterval(() => {
            if (currentSimulation && !currentSimulation.halt) {
                stepSimulation();
            } else {
                // Stop if simulation halts
                clearInterval(autoStepInterval);
                autoStepInterval = null;
                isAutoStepping = false;
                autoStepBtn.textContent = 'Play';
                autoStepBtn.classList.remove('active');
                stepBtn.disabled = false;
            }
        }, speed);
    }
}

// New: Update auto-step speed
function updateSpeed() {
    const speed = parseInt(speedControl.value);
    
    // If auto-stepping is active, restart with new speed
    if (isAutoStepping) {
        clearInterval(autoStepInterval);
        autoStepInterval = setInterval(() => {
            if (currentSimulation && !currentSimulation.halt) {
                stepSimulation();
            } else {
                // Stop if simulation halts
                clearInterval(autoStepInterval);
                autoStepInterval = null;
                isAutoStepping = false;
                autoStepBtn.textContent = 'Play';
                autoStepBtn.classList.remove('active');
                stepBtn.disabled = false;
            }
        }, speed);
    }
}


// Load available machines
async function loadMachines() {
    try {
        const response = await fetch('/machines');
        const machines = await response.json();
        
        // Clear existing options
        machineSelect.innerHTML = '';
        
        // Add new options
        machines.forEach(machine => {
            const option = document.createElement('option');
            option.value = machine;
            option.textContent = machine;
            machineSelect.appendChild(option);
        });
        
        // Load first machine's config
        if (machines.length > 0) {
            await loadMachineConfig(machines[0]);
        }
    } catch (error) {
        console.error('Error loading machines:', error);
        showError('Failed to load machines');
    }
}

// Load machine configuration
async function loadMachineConfig(machineName) {
    try {
        const response = await fetch(`/machine/${encodeURIComponent(machineName)}`);
        currentMachineConfig = await response.json();
        
        // Update input placeholder with example
        if (currentMachineConfig.input_spec && currentMachineConfig.input_spec.length > 0) {
            inputField.placeholder = `e.g. ${currentMachineConfig.input_spec[0].example}`;
        }
    } catch (error) {
        console.error('Error loading machine config:', error);
        showError('Failed to load machine configuration');
    }
}

// Initialize simulation
async function initSimulation() {
    const machineName = machineSelect.value;
    const input = inputField.value;
    
    if (!machineName) {
        showError('Please select a machine');
        return;
    }
    
    try {
        const response = await fetch('/simulate/init', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                machine: machineName,
                input: input
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Initialization failed');
        }
        
        const data = await response.json();
        currentSimulation = {
            machine: machineName,
            state: data.state,
            tapes: data.tapes,
            heads: data.heads,
            halt: data.halt,
            step_count: 0
        };
        
        renderTapes();
        updateStatus();
        stepBtn.disabled = false;
        autoStepBtn.disabled = false;
        showSuccess('Simulation initialized!');

    } catch (error) {
        console.error('Initialization error:', error);
        showError(error.message);
    }
}

function recordStep() {
    if (!currentSimulation) return;

    // Deep copy of current simulation state
    const snapshot = {
        state: currentSimulation.state,
        tapes: JSON.parse(JSON.stringify(currentSimulation.tapes)),
        heads: [...currentSimulation.heads],
        halt: currentSimulation.halt,
        step_count: currentSimulation.step_count
    };

    // remove any "future" steps if  undid before
    historyStack = historyStack.slice(0, currentHistoryIndex + 1);

    historyStack.push(snapshot);
    currentHistoryIndex = historyStack.length - 1;

    renderHistory();
}


// Step through simulation
async function stepSimulation() {
    if (!currentSimulation || currentSimulation.halt) {
        showError('Simulation not initialized or already halted');
        return;
    }
    
    try {
        const response = await fetch('/simulate/step', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                machine: currentSimulation.machine,
                state: currentSimulation.state,
                tapes: currentSimulation.tapes,
                heads: currentSimulation.heads,
                halt: currentSimulation.halt
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Step failed');
        }
        
        const data = await response.json();
        
        // Update simulation state
        currentSimulation.state = data.state;
        currentSimulation.tapes = data.tapes;
        currentSimulation.heads = data.heads;
        currentSimulation.halt = data.halt;
        currentSimulation.step_count = data.step_count || 
            (currentSimulation.step_count + 1);
        
        renderTapes();
        updateStatus();
        
        if (currentSimulation.halt) {
            stepBtn.disabled = true;
            autoStepBtn.disabled = true;

            if (isAutoStepping) {
                clearInterval(autoStepInterval);
                autoStepInterval = null;
                isAutoStepping = false;
                autoStepBtn.textContent = 'Play';
                autoStepBtn.classList.remove('active');
            }

            if (currentMachineConfig.final_states && 
                currentMachineConfig.final_states.includes(currentSimulation.state)) {
                showSuccess('Accepted! Machine halted in final state.');
            } else {
                showError('Rejected! Machine halted in non-final state.');
            }
        }

        recordStep();
    } catch (error) {
        console.error('Step error:', error);
        showError(error.message);
    }
}

// Reset simulation
function resetSimulation() {
    if (isAutoStepping) {
        clearInterval(autoStepInterval);
        autoStepInterval = null;
        isAutoStepping = false;
        autoStepBtn.textContent = 'Play';
        autoStepBtn.classList.remove('active');
    }

    currentSimulation = null;
    historyStack = [];
    currentHistoryIndex = -1;

    tapesContainer.innerHTML = '';
    const historyContainer = document.getElementById('history-container');
    if (historyContainer) historyContainer.innerHTML = '';

    updateStatus();
    stepBtn.disabled = true;
    autoStepBtn.disabled = true;
    statusDisplay.textContent = 'Not initialized';
    statusDisplay.className = 'status-value status-ready';
}


// Render tape visualization
function renderTapes() {
    if (!currentSimulation) return;
    
    tapesContainer.innerHTML = '';
    
    currentSimulation.tapes.forEach((tape, tapeIndex) => {
        const tapeDiv = document.createElement('div');
        tapeDiv.className = 'tape-container';
        
        const tapeTitle = document.createElement('h3');
        tapeTitle.textContent = `Tape ${tapeIndex + 1}`;
        tapeDiv.appendChild(tapeTitle);
        
        const tapeElement = document.createElement('div');
        tapeElement.className = 'tape';
        tapeDiv.appendChild(tapeElement);
        
        tapesContainer.appendChild(tapeDiv);
        
        const headPosition = currentSimulation.heads[tapeIndex];
        
        // Create cells for the tape
        for (let i = 0; i < tape.length; i++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.textContent = tape[i];
            
            if (i === headPosition) {
                cell.classList.add('active');
                
                const headMarker = document.createElement('div');
                headMarker.className = 'head';
                headMarker.textContent = '\u2193';
                cell.appendChild(headMarker);
            }
            
            tapeElement.appendChild(cell);
        }
    });
}

// Update status display
function updateStatus() {
    if (!currentSimulation) {
        stateDisplay.textContent = 'N/A';
        stepDisplay.textContent = '0';
        statusDisplay.textContent = 'Not initialized';
        statusDisplay.className = 'status-value status-ready';
        return;
    }
    
    stateDisplay.textContent = currentSimulation.state;
    stepDisplay.textContent = currentSimulation.step_count;
    
    if (currentSimulation.halt) {
        // Check if we're in a final state
        if (currentMachineConfig.final_states && 
            currentMachineConfig.final_states.includes(currentSimulation.state)) {
            statusDisplay.textContent = 'Accepted!';
            statusDisplay.className = 'status-value status-accepted';
        } else {
            statusDisplay.textContent = 'Rejected';
            statusDisplay.className = 'status-value status-rejected';
        }
    } else {
        statusDisplay.textContent = 'Running';
        statusDisplay.className = 'status-value status-running';
    }
}

// Show error message
function showError(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification error';
    notification.textContent = message;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Show success message
function showSuccess(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification success';
    notification.textContent = message;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);

function initApp() {
    loadMachines();
    resetSimulation();
    
    // Add event listeners
    initBtn.addEventListener('click', initSimulation);
    stepBtn.addEventListener('click', stepSimulation);
    resetBtn.addEventListener('click', resetSimulation);
    autoStepBtn.addEventListener('click', toggleAutoStep); 
    speedControl.addEventListener('input', updateSpeed);
    machineSelect.addEventListener('change', async () => {
        await loadMachineConfig(machineSelect.value);
        resetSimulation();
    });
    speedControl.addEventListener('input', function() {
        document.getElementById('speed-display').textContent = this.value + 'ms';
    });
    document.getElementById('speed-display').textContent = speedControl.value + 'ms';

    setupTransitionsUI();
}

// --- Diagnostic + safe setup for transitions UI ---
function setupTransitionsUI() {
    const transitionsSection = document.getElementById('transitions-section');
    const transitionsContainer = document.getElementById('transitions-container');
    const backBtn = document.getElementById('back-btn');
    const viewTransitionsBtn = document.getElementById('view-transitions-btn');

    viewTransitionsBtn.addEventListener('click', () => {
        if (!currentMachineConfig) {
            showError('No machine loaded!');
            return;
        }
        const transitions = currentMachineConfig.transition || [];
        renderTransitions(transitions);
        transitionsSection.style.display = 'block';  // show transitions
        viewTransitionsBtn.style.display = 'none';   // hide button when open
    });

    backBtn.addEventListener('click', () => {
        transitionsSection.style.display = 'none';   // hide transitions
        viewTransitionsBtn.style.display = 'inline-block'; // show button again
    });
}

// Robust renderer — queries container each time to avoid scoping issues
function renderTransitions(transitions) {
    const transitionsContainer = document.getElementById('transitions-container');
    if (!transitionsContainer) {
        console.error('renderTransitions: container not found');
        return;
    }

    transitionsContainer.innerHTML = '';

    if (!Array.isArray(transitions) || transitions.length === 0) {
        transitionsContainer.innerHTML = '<p>No transitions defined.</p>';
        return;
    }

    const escapeHtml = (str) => String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');

    transitions.forEach((trans, index) => {
        try {
            let state = '(unknown)';
            let readSymbols = [];
            let newState = '(unknown)';
            let writeSymbols = [];
            let moves = [];

            if (Array.isArray(trans)) {
                const read = trans[0] || [];
                const writeMove = trans[1] || [];

                state = read[0] ?? state;
                readSymbols = Array.isArray(read[1]) ? read[1] : (read[1] !== undefined ? [read[1]] : []);
                newState = writeMove[0] ?? newState;
                writeSymbols = Array.isArray(writeMove[1]) ? writeMove[1] : (writeMove[1] !== undefined ? [writeMove[1]] : []);
                moves = Array.isArray(writeMove[2]) ? writeMove[2] : (writeMove[2] !== undefined ? [writeMove[2]] : []);
            } else if (trans && typeof trans === 'object') {
                const from = trans.from || trans[0] || {};
                const to = trans.to || trans[1] || {};
                state = from.state ?? from[0] ?? state;
                readSymbols = from.read ?? from[1] ?? [];
                newState = to.state ?? to[0] ?? newState;
                writeSymbols = to.write ?? to[1] ?? [];
                moves = to.move ?? to[2] ?? [];
            } else {
                throw new Error('Unsupported transition format');
            }

            readSymbols = (Array.isArray(readSymbols) ? readSymbols : [readSymbols]).map(String);
            writeSymbols = (Array.isArray(writeSymbols) ? writeSymbols : [writeSymbols]).map(String);
            moves = (Array.isArray(moves) ? moves : [moves]).map(String);

            const transDiv = document.createElement('div');
            transDiv.className = 'transition';
            transDiv.innerHTML = `
                <strong>Transition ${index + 1}</strong><br>
                From State: <code>${escapeHtml(state)}</code><br>
                Read Symbols: <code>[${readSymbols.map(escapeHtml).join(', ')}]</code><br>
                To State: <code>${escapeHtml(newState)}</code><br>
                Write Symbols: <code>[${writeSymbols.map(escapeHtml).join(', ')}]</code><br>
                Moves: <code>[${moves.map(escapeHtml).join(', ')}]</code>
                <hr>
            `;
            transitionsContainer.appendChild(transDiv);
        } catch (err) {
            console.error('Error rendering transition', err, trans);
            const errDiv = document.createElement('div');
            errDiv.className = 'transition error';
            errDiv.textContent = `Error rendering transition ${index + 1}`;
            transitionsContainer.appendChild(errDiv);
        }
    });
}

function renderHistory() {
    const container = document.getElementById('history-container');
    if (!container) return;

    container.innerHTML = '';

    historyStack.forEach((item, idx) => {
        const div = document.createElement('div');
        div.className = 'history-item';
        div.innerHTML = `
            <strong>Step ${idx + 1}</strong><br>
            State: <code>${item.state}</code><br>
            Tape(s): ${item.tapes.map(t => `<code>[${t.join(', ')}]</code>`).join(' ')}<br>
            Head(s): <code>[${item.heads.join(', ')}]</code>
        `;
        if (idx === currentHistoryIndex) {
            div.style.backgroundColor = 'rgba(243, 156, 18, 0.5)';
        }
        container.appendChild(div);
    });

    // Scroll to last item
    container.scrollTop = container.scrollHeight;
}

document.getElementById('undo-btn').addEventListener('click', () => {
    if (currentHistoryIndex <= 0) return;

    currentHistoryIndex--;
    const prevStep = historyStack[currentHistoryIndex];

    if (prevStep) {
        currentSimulation.state = prevStep.state;
        currentSimulation.tapes = JSON.parse(JSON.stringify(prevStep.tapes));
        currentSimulation.heads = [...prevStep.heads];
        currentSimulation.halt = prevStep.halt;
        currentSimulation.step_count = prevStep.step_count;

        renderTapes();
        updateStatus();
        renderHistory();

        // Re-enable step button if there are steps ahead
        if (!currentSimulation.halt || currentHistoryIndex < historyStack.length - 1) {
            stepBtn.disabled = false;
        }
        // Re-enable auto-step only if simulation not halted
        autoStepBtn.disabled = currentSimulation.halt;
    }
});
