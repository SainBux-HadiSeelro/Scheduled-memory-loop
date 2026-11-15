import os
import re
import tempfile
import shutil
from datetime import date
from typing import Dict, List, Any

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

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


def get_writable_dir() -> str:
    """Determine a safe, writable directory.
    In serverless platforms (e.g. Vercel, AWS Lambda where root is /var/task),
    the file system is read-only. In that case, fallback to /tmp or system temp dir.
    """
    if "DATA_DIR" in os.environ:
        os.makedirs(os.environ["DATA_DIR"], exist_ok=True)
        return os.environ["DATA_DIR"]

    # Test if PROJECT_DIR is writable
    test_path = os.path.join(PROJECT_DIR, f".write_test_{os.getpid()}")
    try:
        with open(test_path, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(test_path)
        return PROJECT_DIR
    except (OSError, IOError, PermissionError):
        pass

    # Serverless fallback: /tmp on Unix/Lambda/Vercel or system tempdir on Windows
    tmp_candidate = "/tmp" if os.path.exists("/tmp") and os.access("/tmp", os.W_OK) else tempfile.gettempdir()
    os.makedirs(tmp_candidate, exist_ok=True)
    return tmp_candidate


def get_progress_file_path() -> str:
    """Get the active progress.md path.
    If the project root is read-only (such as /var/task),
    seeds and returns a writable copy in the temporary directory.
    """
    if "PROGRESS_FILE" in os.environ:
        return os.environ["PROGRESS_FILE"]

    writable_dir = get_writable_dir()
    bundled_file = os.path.join(PROJECT_DIR, "progress.md")

    if os.path.abspath(writable_dir) == os.path.abspath(PROJECT_DIR):
        return bundled_file

    target_file = os.path.join(writable_dir, "progress.md")
    if not os.path.exists(target_file):
        if os.path.exists(bundled_file):
            try:
                shutil.copy2(bundled_file, target_file)
            except Exception:
                pass
        else:
            try:
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write("# Progress Log\n")
            except Exception:
                pass

    return target_file


def ensure_progress_file() -> str:
    """Ensure the spine progress.md exists and return its path."""
    target = get_progress_file_path()
    if not os.path.exists(target):
        try:
            with open(target, "w", encoding="utf-8") as f:
                f.write("# Progress Log\n")
        except Exception:
            # Fallback to absolute temp directory
            fallback = os.path.join(tempfile.gettempdir(), "progress.md")
            with open(fallback, "w", encoding="utf-8") as f:
                f.write("# Progress Log\n")
            return fallback
    return target


def get_known_signatures() -> set[str]:
    """Parse all known TODO signatures already recorded in progress.md.
    Matches lines formatted as: '- path:line | text'
    """
    progress_file = ensure_progress_file()
    known = set()
    pattern = re.compile(r"^\s*-\s+([^|]+?)\s*\|\s*(.*)$")
    if os.path.exists(progress_file):
        with open(progress_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                match = pattern.match(line)
                if match:
                    path_line = match.group(1).strip()
                    content = match.group(2).strip()
                    known.add(f"{path_line}|{content}")
    return known


def get_writable_file_path(filename: str = "example.py") -> str:
    """Get writable path for a project file (copies to tmp in read-only environments)."""
    writable_dir = get_writable_dir()
    bundled_path = os.path.join(PROJECT_DIR, filename)

    if os.path.abspath(writable_dir) == os.path.abspath(PROJECT_DIR):
        return bundled_path

    target_path = os.path.join(writable_dir, filename)
    if not os.path.exists(target_path) and os.path.exists(bundled_path):
        try:
            shutil.copy2(bundled_path, target_path)
        except Exception:
            pass
    return target_path


def scan_repo_todos() -> List[Dict[str, Any]]:
    """Scan the repository for open TODO comments."""
    todos = []
    writable_dir = get_writable_dir()
    overridden_files = {}

    # In serverless environments, check if writable overrides exist
    if os.path.abspath(writable_dir) != os.path.abspath(PROJECT_DIR):
        for root, dirs, files in os.walk(writable_dir):
            for file in files:
                if file.endswith(".py"):
                    rel = os.path.relpath(os.path.join(root, file), writable_dir).replace("\\", "/")
                    overridden_files[rel] = os.path.join(root, file)

    for root, dirs, files in os.walk(PROJECT_DIR):
        dirs[:] = [
            d for d in dirs
            if d not in DEFAULT_EXCLUDES and not d.startswith(".")
        ]

        for file in files:
            if file in DEFAULT_EXCLUDES or file.startswith("."):
                continue

            rel_path = os.path.relpath(os.path.join(root, file), PROJECT_DIR).replace("\\", "/")
            file_path = overridden_files.get(rel_path, os.path.join(root, file))

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
    progress_file = ensure_progress_file()
    content = ""
    if os.path.exists(progress_file):
        with open(progress_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

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
    progress_file = ensure_progress_file()

    raw_progress = ""
    if os.path.exists(progress_file):
        with open(progress_file, "r", encoding="utf-8", errors="ignore") as f:
            raw_progress = f.read()

    return {
        "todos": enriched_todos,
        "new_todos": new_todos,
        "total_todos": len(enriched_todos),
        "new_count": len(new_todos),
        "known_count": len(known),
        "history": history,
        "raw_progress": raw_progress,
        "history_count": len(history),
        "storage_path": progress_file
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

    progress_file = ensure_progress_file()
    with open(progress_file, "a", encoding="utf-8") as f:
        f.write(f"\n{entry}")

    updated_status = get_status()
    return {
        "entry": entry,
        "count": count,
        "status": updated_status
    }


def add_test_todo(text: str, filename: str = "example.py") -> str:
    """Helper to append a new TODO to a file to test the memory loop."""
    target_path = get_writable_file_path(filename)
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
    progress_file = ensure_progress_file()
    with open(progress_file, "w", encoding="utf-8") as f:
        f.write("# Progress Log\n")


if __name__ == "__main__":
    result = run_digest()
    print(result["entry"])
