# Turing Machine Simulator

A web-based Turing Machine simulator with support for **multi-tape machines**, **step-by-step simulation**, **auto-stepping**, **undo history**, and **dynamic machine creation**. Built with **Flask** for the backend and **vanilla JS/HTML** for the frontend.

---

## Features

* Load pre-defined Turing machines from the backend.
* Step through simulations one step at a time or automatically.
* View tape contents, head positions, and machine states.
* Undo simulation steps and maintain history.
* Multi-tape support.
* Dynamic creation of new Turing machines via a web form.
* Transitions visualization.
* Input specification per tape.

---

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/Reza-namvaran/TM-Sim.git
cd TM-Sim
```

2. **Set up a virtual environment:**

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

---

## Running Locally

```bash
flask run
```

Open your browser at [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

![TM-Flow](./TM-Flow.png)

---

## Backend (Flask)

### Structure

* `app.py` — main Flask application.
* `machines/` — directory storing machine JSON files.
* `turing_machine.py` — TuringMachine class and simulation logic.
* `exceptions.py` — custom exceptions for simulation errors.

### Key Endpoints

| Endpoint          | Method | Description                                             |
| ----------------- | ------ | ------------------------------------------------------- |
| `/machines`       | GET    | List all saved machine names                            |
| `/machine/<name>` | GET    | Get machine configuration JSON                          |
| `/machine/create` | POST   | Create a new machine dynamically                        |
| `/simulate/init`  | POST   | Initialize a simulation with given machine and input(s) |
| `/simulate/step`  | POST   | Advance simulation by one step                          |

---

## Frontend

* The frontend HTML/JS is in `templates/` or served statically.
* Supports:

  * Selecting a machine.
  * Entering tape inputs.
  * Step and auto-step simulations.
  * Undo history.
  * Dynamic machine creation form.
  * Viewing all transitions.

### How to Use

1. Open the web app in your browser.
2. Select a machine from the dropdown.
3. Enter input(s) for tape(s).
4. Click **Initialize** to start simulation.
5. Use **Step** or **Auto-Step** to advance the machine.
6. Undo previous steps using **Undo**.

---

## Notes

* Auto-step speed is adjustable via the frontend slider.
* Transitions visualization allows easy debugging.
* Undo history allows stepping back and forth.

---

## Future Improvements
* create machine with editor
* Multi-tape Turing machines are fully supported.
* Pre-fill transitions automatically based on number of tapes.
* Enforce valid moves (L, R, S) on the frontend.
* Save created machines persistently (database support).
* Mobile-friendly responsive layout.
