# Scheduled Memory Loop (daily-digest)

A scheduled scan loop with persistent state memory (a spine). Periodically, it scans the repository for open `TODO` comments, compares them against what past runs already recorded in `progress.md`, and appends an entry listing **only the NEW TODOs**.

The only state that survives between runs is `progress.md` — that is what makes the memory work.

---

## 🚀 Interactive Web UI Dashboard

A modern, responsive Flask & Tailwind CSS web dashboard is included to monitor and test the memory loop visually in real time.

### Run the Web UI

1. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the dashboard:**
   ```bash
   python app.py
   ```

3. **Open in browser:**
   ```
   http://127.0.0.1:5000
   ```

### UI Features
- **Live Repo TODO Tracker:** Scans files in real time and flags comments as either `✓ KNOWN` (already saved in spine) or `★ NEW` (awaiting digest).
- **1-Click Beat Execution:** Click **"Run Digest Beat Now"** to record new findings into `progress.md`.
- **Test TODO Injector:** Add test tasks directly from the web interface to watch the memory loop isolate only newly added tasks.
- **Spine Timeline & Raw Viewer:** Visual changelog with badges and dates, plus a raw markdown view of `progress.md`.
- **Reset Spine Memory:** Easily reset `progress.md` to start fresh testing.

---

## 📁 Repository Structure

- `app.py` — Flask backend application and REST API endpoints.
- `templates/index.html` — Modern responsive Tailwind CSS dashboard interface.
- `digest.py` — Cross-platform Python core engine for scanning and spine management (Windows, macOS, Linux).
- `daily_digest.sh` — Bash implementation of one scan beat.
- `setup_schedule.sh` — Installs a daily 09:00 cron job (Linux / macOS / Git Bash).
- `progress.md` — The spine: a dated log of every past run.
- `example.py` — Sample demo file containing TODO comments.
- `requirements.txt` — Python dependencies (`Flask`).

---

## 🧪 Testing the Memory (CLI)

### Cross-Platform Python Engine:
```bash
python digest.py
```

### Bash Shell:
```bash
./daily_digest.sh                      # run 1: reports whatever TODOs exist
echo "# TODO: fake task" >> example.py
./daily_digest.sh                      # run 2: reports ONLY the new TODO
```

Look at the entries in `progress.md`: the second entry will mention only the new TODO you added, not the previously existing ones. Running it again without changes will report `No new TODOs since last run.`

---

## ⏰ Automated Cron Schedule (Linux / macOS)

```bash
./setup_schedule.sh
```

Installs a cron job running `daily_digest.sh` every day at 09:00, logging output to `digest.log`.

---

## 📝 Notes

- **Exclusions:** The scanner automatically excludes project machinery (`progress.md`, `README.md`, `digest.log`, scripts, `templates/`, `.git/`, virtual environments) so the system never digests itself.
- **Signatures:** A TODO is uniquely identified by `path:line` and its content, so modifying or relocating a TODO will register as a new finding.
