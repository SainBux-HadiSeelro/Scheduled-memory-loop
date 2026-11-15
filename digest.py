import os
import re
from datetime import date
from typing import Dict, List, Any

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(PROJECT_DIR, "progress.md")

DEFAULT_EXCLUDES = {
    "progress.md",
    "README.md",
    "digest.log",
    "daily_digest.sh",
    "setup_schedule.sh",
    "digest.py",
    "app.py",
    "requirements.txt",
    ".git",
    ".gitignore",
    "__pycache__",
    "templates",
    "static",
    "venv",
    ".venv",
}


def ensure_progress_file() -> None:
    """Ensure progress.md exists."""
    if not os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            f.write("# Progress Log\n")


def get_known_signatures() -> set[str]:
    """Parse all known TODO signatures already recorded in progress.md.
    Matches lines formatted as: '- path:line | text'
    """
    ensure_progress_file()
    known = set()
    pattern = re.compile(r"^\s*-\s+([^|]+?)\s*\|\s*(.*)$")
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            match = pattern.match(line)
            if match:
                path_line = match.group(1).strip()
                content = match.group(2).strip()
                known.add(f"{path_line}|{content}")
    return known


def scan_repo_todos() -> List[Dict[str, Any]]:
    """Scan the repository for open TODO comments."""
    todos = []
    for root, dirs, files in os.walk(PROJECT_DIR):
        # Exclude directories
        dirs[:] = [
            d for d in dirs
            if d not in DEFAULT_EXCLUDES and not d.startswith(".")
        ]

        for file in files:
            if file in DEFAULT_EXCLUDES or file.startswith("."):
                continue

            rel_path = os.path.relpath(os.path.join(root, file), PROJECT_DIR)
            # Normalize path separators to forward slash for cross-platform consistency
            rel_path = rel_path.replace("\\", "/")

            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, start=1):
                        if "TODO" in line:
                            clean_line = line.strip()
                            signature = f"{rel_path}:{line_num}|{clean_line}"
                            todos.append({
                                "file": rel_path,
                                "line": line_num,
                                "text": clean_line,
                                "signature": signature,
                            })
            except Exception:
                continue

    return sorted(todos, key=lambda x: (x["file"], x["line"]))


def parse_history() -> List[Dict[str, Any]]:
    """Parse past run entries from progress.md into structured data."""
    ensure_progress_file()
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by level 2 headings '## YYYY-MM-DD'
    sections = re.split(r"\n(?=##\s+)", content)
    history = []

    for sec in sections:
        sec = sec.strip()
        if not sec.startswith("##"):
            continue

        lines = sec.splitlines()
        date_line = lines[0].replace("##", "").strip()
        body_lines = [l for l in lines[1:] if l.strip()]

        todos_recorded = []
        summary = ""

        for bl in body_lines:
            bullet_match = re.match(r"^\s*-\s+([^|]+?)\s*\|\s*(.*)$", bl)
            if bullet_match:
                todos_recorded.append({
                    "loc": bullet_match.group(1).strip(),
                    "text": bullet_match.group(2).strip()
                })
            elif not summary:
                summary = bl.strip()

        history.append({
            "date": date_line,
            "summary": summary,
            "todos": todos_recorded,
            "count": len(todos_recorded),
            "raw": sec
        })

    # Return in reverse chronological order (newest first)
    return list(reversed(history))


def get_status() -> Dict[str, Any]:
    """Get complete status of repository TODOs and spine memory."""
    known = get_known_signatures()
    current_todos = scan_repo_todos()

    enriched_todos = []
    new_todos = []
    for item in current_todos:
        is_new = item["signature"] not in known
        todo_data = {
            **item,
            "is_new": is_new
        }
        enriched_todos.append(todo_data)
        if is_new:
            new_todos.append(todo_data)

    history = parse_history()

    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        raw_progress = f.read()

    return {
        "todos": enriched_todos,
        "new_todos": new_todos,
        "total_todos": len(enriched_todos),
        "new_count": len(new_todos),
        "known_count": len(known),
        "history": history,
        "raw_progress": raw_progress,
        "history_count": len(history)
    }


def run_digest() -> Dict[str, Any]:
    """Execute one beat of the daily digest loop, appending only NEW TODOs to progress.md."""
    status = get_status()
    new_todos = status["new_todos"]
    today_str = date.today().strftime("%Y-%m-%d")
    count = len(new_todos)

    if count == 0:
        if status["total_todos"] == 0:
            summary = "No new TODOs since last run (the repo currently has no TODO comments at all)."
        else:
            summary = "No new TODOs since last run."
        entry = f"## {today_str}\n\n{summary}\n"
    else:
        plural = "s" if count != 1 else ""
        entry = f"## {today_str}\n\n**{count} new TODO{plural} since last run:**\n\n"
        for t in new_todos:
            loc = f"{t['file']}:{t['line']}"
            entry += f"- {loc} | {t['text']}\n"

    # Append to progress.md
    with open(PROGRESS_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{entry}")

    updated_status = get_status()
    return {
        "entry": entry,
        "count": count,
        "status": updated_status
    }


def add_test_todo(text: str, filename: str = "example.py") -> str:
    """Helper to append a new TODO to a file to test the memory loop."""
    target_path = os.path.join(PROJECT_DIR, filename)
    clean_text = text.strip()
    if not clean_text.upper().startswith("TODO") and not clean_text.startswith("#"):
        clean_text = f"# TODO: {clean_text}"
    elif not clean_text.startswith("#"):
        clean_text = f"# {clean_text}"

    with open(target_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n{clean_text}\n")

    return clean_text


def reset_memory() -> None:
    """Reset the spine memory (progress.md) to initial state."""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        f.write("# Progress Log\n")


if __name__ == "__main__":
    result = run_digest()
    print(result["entry"])
