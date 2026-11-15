# SPEC-001: Autonomous Scheduled Memory Loop Engine

**Status:** Approved & Implemented  
**Author:** Agentic AI Engineering Team  
**System Identity:** `LOOP_AGENT.ai`  
**Reference Deployment:** [scheduled-memory-loop.vercel.app](https://scheduled-memory-loop.vercel.app/)  
**Primary Spine File:** `progress.md`

---

## 1. Executive Summary

Autonomous agent systems operating over extended horizons require continuous state reflection without unbounded context accumulation. The **Autonomous Scheduled Memory Loop Engine** implements a persistent episodic memory spine. 

On scheduled intervals (heartbeat beats), the agent perceives the repository workspace, isolates newly introduced task signatures against long-term episodic memory, records delta states, and updates the spine file (`progress.md`) in an append-only sequence.

```
+------------------------+
|  Workspace Perception  |  (AST / Lexical Scan for TODO signatures)
+-----------+------------+
            |  O_t = { file:line | text }
            v
+------------------------+
|   Spine Memory Diff    |  (Set difference against known signatures)
|   Δ_t = O_t \ M_t      |
+-----------+------------+
            |
      +-----+-----+
      |           |
 (Δ_t != ∅)   (Δ_t == ∅)
      |           |
      v           v
+-----------+ +-----------+
| Append    | | Heartbeat |
| Delta Log | | Sync Only |
+-----+-----+ +-----+-----+
      |           |
      +-----+-----+
            v
+------------------------+
|      progress.md       |  (Persistent Episodic Spine)
+------------------------+
```

---

## 2. Mathematical Formalism

Let $W_t$ represent the repository workspace at discrete time beat $t \in \mathbb{N}$.

1. **Perception Mapping ($\Phi$):**  
   $$\Phi(W_t) = O_t = \{ \sigma_i \mid \sigma_i = \langle \text{path}_i, \text{line}_i, \text{hash}_i \rangle \}$$  
   where $O_t$ is the finite set of active TODO signatures extracted from eligible files.

2. **Spine Memory Retrieval ($M_t$):**  
   $$M_t = \text{ParseSignatures}(\text{progress.md}_{t-1})$$  
   where $M_t$ represents the union of all task signatures recorded across all past beats $1, \dots, t-1$.

3. **Delta Derivation ($\Delta_t$):**  
   $$\Delta_t = O_t \setminus M_t$$  
   The delta contains strictly those tasks that were created or relocated since the last recorded beat.

4. **Spine Mutation Operator ($S_{t}$):**  
   $$\text{progress.md}_t = \text{progress.md}_{t-1} \mathbin{\Vert} \text{FormatEpisode}(t, \Delta_t)$$  
   where $\mathbin{\Vert}$ denotes the strict append operation. The spine is monotonic: records are never deleted or rewritten in normal operation.

---

## 3. System Invariants & Non-Functional Requirements

### 3.1 Strict Append-Only Guarantee
- The memory spine (`progress.md`) must never be truncated or overwritten during a regular digest beat.
- Deleting `progress.md` resets the baseline, causing the subsequent beat to treat all active observations as novel.

### 3.2 Anti-Self-Digestion Isolation
The perception engine must explicitly filter out system machinery to prevent feedback loops:
- Excluded paths: `progress.md`, `README.md`, `digest.log`, `*.sh`, `digest.py`, `app.py`, `requirements.txt`, `specs/`, `.git/`, `.venv/`.

### 3.3 Serverless / Read-Only Storage Resilience
In serverless runtimes (such as Vercel or AWS Lambda where code resides in `/var/task` under a read-only filesystem):
- The runtime dynamically detects write permissions on `PROJECT_DIR`.
- If read-only (`[Errno 30]`), the engine transparently routes state mutations to `/tmp/progress.md` while seeding from the bundled repository baseline.
- `DATA_DIR` and `PROGRESS_FILE` environment variables provide explicit runtime overrides.

---

## 4. Interface Specifications

### 4.1 Core Python Engine (`digest.py`)

| Function | Signature | Description |
|---|---|---|
| `get_status()` | `() -> Dict[str, Any]` | Returns active observations, delta count, history, and storage telemetry. |
| `run_digest()` | `() -> Dict[str, Any]` | Executes perception, computes $\Delta_t$, appends to spine, and returns formatted entry. |
| `add_test_todo(text, file)` | `(str, str) -> str` | Injects synthetic TODO for integration testing. |
| `reset_memory()` | `() -> None` | Re-initializes spine to virgin `# Progress Log\n` state. |

### 4.2 REST API Contracts

#### `GET /api/status`
Returns complete telemetry and observations.
```json
{
  "success": true,
  "data": {
    "total_todos": 4,
    "known_count": 4,
    "new_count": 0,
    "history_count": 2,
    "storage_path": "/path/to/progress.md",
    "todos": [
      {
        "file": "example.py",
        "line": 5,
        "text": "# TODO: add unit tests for add()",
        "signature": "example.py:5|# TODO: add unit tests for add()",
        "is_new": false
      }
    ],
    "history": []
  }
}
```

#### `POST /api/run-digest`
Triggers immediate cycle execution.
```json
{
  "success": true,
  "message": "Memory loop executed successfully.",
  "new_count": 1,
  "entry": "## 2026-11-16\n\n**1 new TODO since last run:**\n\n- example.py:20 | # TODO: test",
  "data": { ... }
}
```

#### `POST /api/add-todo`
Payload: `{ "todo": "task description", "file": "example.py" }`

#### `POST /api/reset-memory`
Payload: `{}` (Purges spine to `# Progress Log\n`)

---

## 5. Deployment Architecture

- **Web UI & REST Service:** Python 3.12 + Flask + Tailwind CSS.
- **Serverless Host:** Vercel Python Runtime.
- **Local Daemon:** Native PowerShell / Unix execution via `python app.py`.
- **Scheduled Trigger:** Unix `crontab` via `setup_schedule.sh` or external cloud scheduler.
