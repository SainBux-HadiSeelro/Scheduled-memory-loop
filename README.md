<div align="center">

# 🧠 Autonomous Scheduled Memory Loop
### Long-Term Episodic Memory Spine for Autonomous Agents

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel%20Active-06b6d4?style=for-the-badge&logo=vercel&logoColor=white)](https://scheduled-memory-loop.vercel.app/)
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-emerald?style=for-the-badge)](LICENSE)

<br/>

**[🌐 Experience the Live Agent Dashboard](https://scheduled-memory-loop.vercel.app/)** &bull; **[📋 Read the Engineering Specifications](specs/SPECIFICATION.md)**

</div>

---

## ⚡ Overview

Autonomous agent workflows spanning extended operating horizons require reliable state reflection without ballooning LLM context windows. 

**Scheduled Memory Loop** implements an immutable, append-only **Episodic Memory Spine** (`progress.md`). Operating as an autonomous heartbeat loop, the agent:
1. **Perceives** all actionable task comments (`TODO` signatures) across the repository.
2. **Computes the set difference** against historically recorded signatures.
3. **Persists only novel state transitions ($\Delta_t$)** into the spine.
4. **Survives across runtime reboots and serverless teardowns** using the file-based spine as ground truth.

---

## 🏛️ Architecture & Control Flow

```
                      ┌────────────────────────┐
                      │  Repository Workspace  │
                      └───────────┬────────────┘
                                  │ (Periodic Scan / Trigger)
                                  ▼
                      ┌────────────────────────┐
                      │   Perception Engine    │
                      │  Extracts O_t (TODOs)  │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │   Spine Diff Engine    │
                      │    Δ_t = O_t \ M_t     │
                      └───────────┬────────────┘
                                  │
                   ┌──────────────┴──────────────┐
                   │                             │
             [ Δ_t != ∅ ]                  [ Δ_t == ∅ ]
                   │                             │
                   ▼                             ▼
        ┌─────────────────────┐       ┌─────────────────────┐
        │  Format New Deltas  │       │  Log Sync Heartbeat │
        └──────────┬──────────┘       └──────────┬──────────┘
                   │                             │
                   └──────────────┬──────────────┘
                                  ▼
                   ┌─────────────────────────────┐
                   │   Episodic Memory Spine     │
                   │        progress.md          │
                   └─────────────────────────────┘
```

---

## 📐 Mathematical Formulation

At discrete loop cycle $t \in \mathbb{N}$:

$$\Phi(W_t) = O_t = \{ \sigma_i \mid \sigma_i = \langle \text{path}_i, \text{line}_i, \text{content}_i \rangle \}$$

$$M_t = \text{Signatures}(\text{progress.md}_{t-1})$$

$$\Delta_t = O_t \setminus M_t$$

$$\text{progress.md}_t = \text{progress.md}_{t-1} \mathbin{\Vert} \text{Record}(t, \Delta_t)$$

- **Monotonicity:** $\forall t, |M_t| \le |M_{t+1}|$
- **Strict Invariance:** Past historical episodes are immutable.

---

## 🚀 Live Demo & Web Dashboard

Try the live interactive agent dashboard deployed on Vercel:

👉 **[https://scheduled-memory-loop.vercel.app/](https://scheduled-memory-loop.vercel.app/)**

### Dashboard Capabilities:
- **Real-Time Telemetry:** Monospace telemetry displaying Active Observations, Persisted Signatures, and Pending Deltas.
- **Interactive Loop Trigger:** `⚡ TRIGGER_LOOP_BEAT` manually triggers the perception-diff-persist cycle.
- **Harness Test Injector:** Dynamically injects synthetic observations into `example.py` to observe delta isolation in real time.
- **Dual-Pane View:** Live workspace observation stream side-by-side with episodic changelog and raw markdown preview.

---

## 💻 Local Setup & Execution

### 1. Clone & Install
```bash
git clone https://github.com/SainBux-HadiSeelro/Scheduled-memory-loop.git
cd Scheduled-memory-loop
pip install -r requirements.txt
```

### 2. Launch the Agent Dashboard
```bash
python app.py
```
Visit **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

### 3. Headless CLI Execution
```bash
python digest.py
```

### 4. Unix Cron Automation (Heartbeat)
```bash
chmod +x setup_schedule.sh daily_digest.sh
./setup_schedule.sh
```
Installs a daily `09:00` heartbeat cron job logging to `digest.log`.

---

## 🛡️ Serverless & Read-Only Storage Resilience

On serverless runtimes (such as Vercel or AWS Lambda where `/var/task` is mounted read-only):
- The storage manager automatically probes directory write capabilities.
- When write restrictions (`[Errno 30]`) are detected, state writes transparently fall back to `/tmp/progress.md`, seeded directly from the baseline repository snapshot.
- Zero configuration required; full runtime compatibility out of the box.

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/status` | `GET` | Fetches active observations, delta counts, and spine history |
| `/api/run-digest` | `POST` | Executes a single loop beat, persisting deltas to spine |
| `/api/add-todo` | `POST` | Injects synthetic observation: `{ "todo": "task text" }` |
| `/api/reset-memory` | `POST` | Purges memory spine to default baseline state |

---

## 📁 Repository Structure

```
Scheduled-memory-loop/
├── app.py                  # Flask REST API and web application server
├── digest.py               # Core perception & spine delta engine
├── example.py              # Active workspace file containing sample TODO comments
├── progress.md             # The episodic memory spine (ground truth)
├── daily_digest.sh         # Shell-based heartbeat implementation
├── setup_schedule.sh       # Unix cron scheduler installer
├── templates/
│   └── index.html          # Sleek Agentic AI telemetry web dashboard
├── specs/
│   └── SPECIFICATION.md    # Formal engineering specification (SPEC-001)
├── requirements.txt        # Runtime dependencies
└── README.md               # Technical project documentation
```

---

## 📄 Specifications

For the complete technical RFC, state machine diagram, and interface contract, see **[specs/SPECIFICATION.md](specs/SPECIFICATION.md)**.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
