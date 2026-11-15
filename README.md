<div align="center">

# 🧠 Autonomous Scheduled Memory Loop
### Long-Horizon Episodic Memory Spine for Autonomous AI Agents

*Reliable state reflection and monotonic delta isolation without unbounded context window explosion.*

<br/>

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel%20Active-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://scheduled-memory-loop.vercel.app/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-10b981?style=for-the-badge)](LICENSE)

<br/>

[🌐 **Live Dashboard**](https://scheduled-memory-loop.vercel.app/) &nbsp;•&nbsp;
[📋 **Technical Spec (SPEC-001)**](specs/SPECIFICATION.md) &nbsp;•&nbsp;
[🚀 **Quickstart**](#-quickstart--local-setup) &nbsp;•&nbsp;
[🏗️ **Architecture**](#-architecture--control-flow) &nbsp;•&nbsp;
[📡 **REST API**](#-rest-api-reference)

---

</div>

## 💡 Overview

Autonomous agent workflows spanning extended operating horizons face two critical challenges:
1. **Context Window Ballooning:** Repeatedly dumping full project histories into LLM prompts quickly exhausts tokens.
2. **State Amnesia:** Agent state is lost across process reboots, ephemeral cloud containers, and serverless teardowns.

**Scheduled Memory Loop** implements an immutable, append-only **Episodic Memory Spine** (`progress.md`). Operating as an autonomous heartbeat loop or on-demand pulse, the system:

* 🔍 **Perceives** actionable task comments (`TODO` signatures) across the repository.
* ⚡ **Computes Set Differences** between real-time observations and historically recorded signatures.
* 📝 **Persists Only Novel Deltas ($\Delta_t$)** to preserve an unbroken, non-redundant history.
* 🛡️ **Survives Serverless Lifecycles** using zero-config automatic failover to `/tmp` in read-only containers.

---

## ✨ Key Highlights

| Feature | Description |
| :--- | :--- |
| **🧠 Zero Context Bloat** | Isolates atomic delta states rather than bloating prompt context with raw repository dumps. |
| **📐 Monotonic Spine** | Strictly append-only mathematical guarantees ($\|M_t\| \le \|M_{t+1}\|$) ensuring historical immutability. |
| **🛡️ Serverless Resilience** | Detects read-only filesystems (e.g., Vercel, AWS Lambda) and seamlessly writes to `/tmp/progress.md`. |
| **📊 Real-Time Web Telemetry** | High-performance cyber-dashboard powered by Flask & Tailwind CSS with live monospace counters. |
| **🧪 Live Harness Test Injector** | In-browser test injector to dynamically add TODOs to `example.py` and watch deltas isolate in real time. |
| **⏰ Automated Scheduling** | Ready-to-use Unix cron scripts (`daily_digest.sh`) and REST endpoints for webhook automation. |

---

## 🏗️ Architecture & Control Flow

The engine operates on a deterministic **Perception $\rightarrow$ Diff $\rightarrow$ Persistence** control loop:

```mermaid
flowchart TD
    subgraph P["🔍 1. Perception Phase"]
        W["📁 Workspace Files (.py, .js, .sh)"] -->|Lexical Scan| PE["⚙️ Perception Engine"]
        PE -->|Extract Signatures| O["📋 Current Observations: O_t"]
    end

    subgraph D["⚡ 2. Memory Diff Engine"]
        O --> DIFF{"Set Difference<br/>Δ_t = O_t \\ M_t"}
        S["📖 Episodic Spine (progress.md)"] -->|Historical Signatures: M_t| DIFF
    end

    subgraph R["💾 3. Persistence Layer"]
        DIFF -->|Δ_t ≠ ∅ (Novel Deltas)| REC["📝 Append Delta Records"]
        DIFF -->|Δ_t = ∅ (No Changes)| HB["💓 Record Heartbeat Sync"]
        REC --> SPINE["🗄️ progress.md (Updated Spine)"]
        HB --> SPINE
    end

    classDef primary fill:#0f172a,stroke:#3b82f6,stroke-width:2px,color:#f8fafc;
    classDef accent fill:#1e1e38,stroke:#8b5cf6,stroke-width:2px,color:#f8fafc;
    classDef success fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#f8fafc;
    classDef warning fill:#451a03,stroke:#f59e0b,stroke-width:2px,color:#f8fafc;

    class W,PE,O primary;
    class DIFF accent;
    class REC,SPINE success;
    class HB warning;
```

---

## 📐 Mathematical Formulation

At discrete loop cycle $t \in \mathbb{N}$:

$$\Phi(W_t) = O_t = \{ \sigma_i \mid \sigma_i = \langle \text{path}_i, \text{line}_i, \text{content}_i \rangle \}$$

$$M_t = \text{Signatures}(\text{progress.md}_{t-1})$$

$$\Delta_t = O_t \setminus M_t$$

$$\text{progress.md}_t = \text{progress.md}_{t-1} \mathbin{\Vert} \text{Record}(t, \Delta_t)$$

> [!NOTE]
> - **Monotonic Growth:** $\forall t, |M_t| \le |M_{t+1}|$ — known signature set is non-decreasing; past historical episodes are strictly immutable.
> - **Idempotency:** Re-executing cycle $t$ when workspace $W_t$ remains unchanged yields $\Delta_t = \emptyset$, recording only a heartbeat sync without duplicate entries.

---

## 🌐 Live Web Telemetry Dashboard

Test the live interactive agent telemetry dashboard deployed on Vercel:

👉 **[https://scheduled-memory-loop.vercel.app/](https://scheduled-memory-loop.vercel.app/)**

### Dashboard Features
- **📡 Monospace Telemetry Grid:** Live counters for Active Observations, Persisted Signatures, and Pending Deltas.
- **⚡ Interactive Loop Trigger:** Manually pulse the `TRIGGER_LOOP_BEAT` cycle on demand.
- **🧪 Harness Test Injector:** Injects synthetic `TODO` observations into `example.py` to preview real-time delta detection.
- **📜 Dual-Pane Log Viewer:** Live workspace observation stream side-by-side with parsed episodic changelogs and raw markdown.

---

## 🚀 Quickstart & Local Setup

### 1. Clone & Install
```bash
git clone https://github.com/SainBux-HadiSeelro/Scheduled-memory-loop.git
cd Scheduled-memory-loop

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch the Web Dashboard
```bash
python app.py
```
Visit **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

### 3. Headless CLI Execution
Run a standalone perception & persistence cycle from the command line:
```bash
python digest.py
```

### 4. Unix Cron Automation (Scheduled Heartbeat)
Install a daily background cron job (runs automatically at `09:00 AM`):
```bash
chmod +x setup_schedule.sh daily_digest.sh
./setup_schedule.sh
```
Execution logs are maintained in `digest.log`.

---

## 🛡️ Cloud & Serverless Resilience

> [!IMPORTANT]
> **Zero-Configuration Read-Only Fallback**
>
> On serverless runtimes (such as Vercel or AWS Lambda where `/var/task` is mounted read-only):
> - The storage manager automatically probes directory write capabilities.
> - When write restrictions (`[Errno 30]`) are detected, state writes transparently fall back to `/tmp/progress.md`, seeded directly from the baseline repository snapshot.
> - Zero manual configuration required; seamless operation across local, VPS, and serverless environments.

---

## 📡 REST API Reference

The dashboard and external schedulers communicate via clean REST endpoints:

| Endpoint | Method | Payload | Description |
| :--- | :---: | :--- | :--- |
| `/api/status` | `GET` | _None_ | Retrieves active observations, delta counts, and spine history |
| `/api/run-digest` | `POST` | _None_ | Executes a single loop beat, persisting deltas to the spine |
| `/api/add-todo` | `POST` | `{"todo": "text", "file": "example.py"}` | Injects a test TODO observation into the workspace |
| `/api/reset-memory` | `POST` | _None_ | Resets memory spine to initial clean baseline |

### Example Request & Response
```bash
# Execute a loop beat
curl -X POST http://127.0.0.1:5000/api/run-digest
```
```json
{
  "success": true,
  "message": "Memory loop executed successfully.",
  "new_count": 2,
  "entry": "## 2026-11-16\n- example.py:12 | Add token rate limiting...",
  "data": { ... }
}
```

---

## 📂 Repository Structure

```plaintext
Scheduled-memory-loop/
├── app.py                  # Flask web server & REST API
├── digest.py               # Core perception & spine delta engine
├── example.py              # Monitored workspace file with active TODO items
├── progress.md             # Episodic memory spine (ground truth)
├── daily_digest.sh         # Shell script for headless heartbeat execution
├── setup_schedule.sh       # Unix cron scheduler automated installer
├── requirements.txt        # Runtime dependencies
├── templates/
│   └── index.html          # Cyberpunk/Agentic UI dashboard (Tailwind CSS)
├── specs/
│   └── SPECIFICATION.md    # Formal engineering specification (SPEC-001)
└── README.md               # Project documentation
```

---

## 🤝 Contributing

Contributions are welcomed! Feel free to open an issue or submit a pull request:
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/NewFeature`)
3. Commit your Changes (`git commit -m 'feat: Add NewFeature'`)
4. Push to the Branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

<div align="center">
<sub>Built with 🧠 for autonomous agent loops by the Agentic AI Engineering Team</sub>
</div>
