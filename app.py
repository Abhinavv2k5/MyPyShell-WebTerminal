from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import commands
import nlp
import re

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)

commands.ensure_base()

ALLOWED_CMD_RE = re.compile(
    r"^(?:ls|pwd|cpu|mem|ps)$|"                    # no-arg commands
    r"^(?:cd|mkdir|rm|cat|touch|move)(?:\s+.+)?$", # commands with optional args
    re.IGNORECASE
)


ALLOWED = {
    "ls": commands.list_files,
    "pwd": commands.print_working_dir,
    "cd": commands.change_dir,
    "mkdir": commands.make_dir,
    "touch": commands.touch_file,
    "rm": commands.remove_file,
    "cat": commands.read_file,
    "move": commands.move_file,
    "cpu": commands.cpu_usage,
    "mem": commands.mem_usage,
    "ps": commands.list_processes,
}

def parse_cmd(raw):
    raw = raw.strip()
    if not raw:
        return None, None
    parts = raw.split(maxsplit=1)
    name = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""
    return name, arg

def clean_ai_output(text):
    text = re.sub(r"\b(the|a|an|new|please|recently|is|called|named)\b", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()

@app.route("/api/exec", methods=["POST"])
def api_exec():
    data = request.get_json() or {}
    cmdtext = data.get("cmd", "")

    if cmdtext.lower().startswith("ai "):
        text = cmdtext[3:].strip()
        cmdtext = nlp.nlp_to_command(text) or ""
        cmdtext = clean_ai_output(cmdtext)
        if not cmdtext:
            return jsonify({"ok": False, "error": "AI could not interpret command"}), 400

    # support multiple commands separated by &&
    commands_list = [c.strip() for c in cmdtext.split("&&") if c.strip()]

    # 🔹 Reorder: mkdir → touch → everything else
    mkdir_cmds = [c for c in commands_list if c.startswith("mkdir")]
    touch_cmds = [c for c in commands_list if c.startswith("touch")]
    other_cmds = [c for c in commands_list if not (c.startswith("mkdir") or c.startswith("touch"))]
    commands_list = mkdir_cmds + touch_cmds + other_cmds

    results = []
    for single_cmd in commands_list:
        if not ALLOWED_CMD_RE.match(single_cmd):
            results.append(f"Not allowed: {single_cmd}")
            continue
        name, arg = parse_cmd(single_cmd)
        if name not in ALLOWED:
            results.append(f"Unknown command: {name}")
            continue
        try:
            if name == "move":
                src, dest = arg.split(maxsplit=1)
                out = ALLOWED[name](src.strip(), dest.strip())
            else:
                out = ALLOWED[name](arg)
            results.append(out)
        except Exception as e:
            results.append(str(e))

    return jsonify({"ok": True, "out": "\n".join(results)})

@app.route("/api/nlp", methods=["POST"])
def api_nlp():
    data = request.get_json() or {}
    text = data.get("text", "")
    if not text:
        return jsonify({"ok": False, "error": "Empty text"}), 400
    cmd = nlp.nlp_to_command(text)
    if not cmd:
        return jsonify({"ok": False, "error": "Could not interpret"}), 200
    cmd = clean_ai_output(cmd)
    return jsonify({"ok": True, "interpreted": cmd})

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
