# 📝 TODO List – Turing Machine Simulator

---

## ✅ Project Setup

- [x] Initialize Flask backend
- [x] Basic HTML/CSS/JS frontend
- [x] Set up YAML/JSON-based machine config loader
- [x] Implement single-tape TM logic

---

## 🔧 Backend (Python + Flask)

### Core Logic
- [x] Parse transition functions from YAML
- [x] Simulate single-tape Turing machine step-by-step
- [x] Add reset and halt state detection
- [x] Add detailed error handling for invalid machine definitions

### API Endpoints
- [x] `/step` – Execute machine step(s)
- [x] `/machines` – Load machine configuration
- [x] `/init` – Initialize machine

---

## 🎨 Frontend (JavaScript + HTML/CSS)

### UI Features
- [x] Tape visualization (HTML divs or SVGs)
- [x] Step-by-step execution with delay
- [x] Show current state and head position
- [x] Add controls: Step, Run, Pause, Reset
- [x] Highlight accepted/rejected state visually

### Input / Output
- [x] Allow user to input custom strings
- [x] Display final result (Accepted / Rejected)
- [ ] Add machine state diagram (optional)

---

## 🚀 Future Enhancements

- [ ] Support for 2-tape and 3-tape machines
- [ ] Machine export/import feature (JSON/YAML)
- [ ] Step-back functionality (undo step)

