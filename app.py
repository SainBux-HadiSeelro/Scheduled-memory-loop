from flask import Flask, render_template, jsonify, request
import digest

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status", methods=["GET"])
def api_status():
    try:
        status = digest.get_status()
        return jsonify({"success": True, "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/run-digest", methods=["POST"])
def api_run_digest():
    try:
        result = digest.run_digest()
        return jsonify({
            "success": True,
            "message": "Memory loop executed successfully.",
            "entry": result["entry"],
            "new_count": result["count"],
            "data": result["status"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/add-todo", methods=["POST"])
def api_add_todo():
    try:
        req = request.get_json(silent=True) or {}
        todo_text = req.get("todo", "").strip()
        filename = req.get("file", "example.py").strip() or "example.py"

        if not todo_text:
            return jsonify({"success": False, "error": "TODO text is required."}), 400

        added = digest.add_test_todo(todo_text, filename=filename)
        updated_status = digest.get_status()

        return jsonify({
            "success": True,
            "message": f"Added: {added} to {filename}",
            "data": updated_status
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/reset-memory", methods=["POST"])
def api_reset_memory():
    try:
        digest.reset_memory()
        updated_status = digest.get_status()
        return jsonify({
            "success": True,
            "message": "Spine memory (progress.md) reset successfully.",
            "data": updated_status
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("\n* Scheduled Memory Loop UI running at http://127.0.0.1:5000")
    print("* Press CTRL+C to stop.\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
