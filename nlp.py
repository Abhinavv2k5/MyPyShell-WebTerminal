# nlp.py
import os
import re
import requests
from dotenv import load_dotenv

# Load .env in development (optional). Ensure .env is in .gitignore
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN", "").strip()
MODEL = "eta-llama/Llama-3.2-1B"

def simple_rule_parse(text):
    t = text.lower().strip()

    # Split multiple commands separated by "and"
    commands_list = [c.strip() for c in re.split(r"\s+and\s+", t)]
    parsed_commands = []
    last_created = None  # track last created file/folder for pronouns like "it"

    for cmd in commands_list:
        # -------------------------
        # MOVE FILE/FOLDER
        # -------------------------
        m_move = re.search(
            r"(move|transfer)\s+([\w\-\_\.]+(?:\s*,\s*[\w\-\_\.]+)*)\s+(?:into|to|inside)\s+([\w\-\_]+)",
            cmd, re.IGNORECASE
        )

        if m_move:
            src = m_move.group(2)
            dest = m_move.group(3)
            # Replace pronoun 'it' with last_created for all sources
            src_list = [s.strip() if s.strip().lower() not in ["it", "this", "that"] else last_created
                        for s in re.split(r"\s*,\s*", src)]

            for s in src_list:
                parsed_commands.append(f"move {s} {dest}")

            continue

        # -------------------------
        # CREATE FOLDER (priority before file)
        # -------------------------
        folder_match = re.search(
            r"(create|make|add|new|generate|build|initiate)\s+"
            r"(?:the|a|an|my|please|recently)?\s*"
            r"(?:folders?|directories|dirs?|subfolders?|file\s*containers?)?\s*"
            r"(?:called|named|as|is)?\s*"
            r"(?!.*\bfile\b)"
            r"([\w\-\_\s,]+)",
            cmd, re.IGNORECASE
        )
        if folder_match:
            names = re.split(r"\s*,\s*|\s+", folder_match.group(1 if folder_match.lastindex is None else 2).strip()) \
                if False else re.split(r"\s*,\s*|\s+", folder_match.group(1 if folder_match.lastindex is None else 1).strip())
            # NOTE: above preserves the original behavior; fallback below uses a safe extraction:
            try:
                # Prefer the captured group if available; some regex engines may vary
                names = re.split(r"\s*,\s*|\s+", folder_match.group(1).strip())
            except Exception:
                names = []
            names = [n for n in names if n and n.lower() not in ("folder", "folders", "directory", "directories", "dir", "dirs", "subfolder", "subfolders", "file", "container", "containers")]
            if names:
                parsed_commands.append("mkdir " + " ".join(names))
                last_created = names[-1]
            continue

        # -------------------------
        # CREATE FILE
        # -------------------------
        file_match = re.search(
            r"(create|add|make|new|generate|build|initiate)\s+"
            r"(?:the|a|an|my|please|recently|new)?\s*"
            r"(?:files?|documents?|texts?)?\s*"
            r"(?:called|named|as|is)?\s*"
            r"([\w][\w\-\_\.]*(?:\s*,\s*[\w\-\_\.]+)*)",
            cmd, re.IGNORECASE
        )
        if file_match:
            names = re.split(r"\s*,\s*|\s+", file_match.group(1 if file_match.lastindex is None else 1).strip()) \
                if False else re.split(r"\s*,\s*|\s+", file_match.group(1).strip())
            try:
                names = re.split(r"\s*,\s*|\s+", file_match.group(1).strip())
            except Exception:
                names = []
            names = [n for n in names if n and n.lower() not in ("file", "files", "document", "documents", "text", "texts")]
            if names:
                parsed_commands.append("touch " + " ".join(names))
                last_created = names[-1]
            continue

        # -------------------------
        # DELETE FILE/FOLDER
        # -------------------------
        m2 = re.search(
            r"(delete|remove|rm|erase|discard|clear|terminate)\s+"
            r"(?:the|my|recent)?\s*"
            r"(?:folders?|directories|dirs?|files?|subfolders?)?\s*"
            r"(?:called|named|as|is)?\s*"
            r"([\w\-\_\.]+(?:\s*,\s*[\w\-\_\.]+)*)",
            cmd, re.IGNORECASE
        )
        if m2:
            targets = re.sub(r"\s*,\s*", " ", m2.group(1 if m2.lastindex is None else 1).strip()) \
                if False else re.sub(r"\s*,\s*", " ", m2.group(1).strip())
            try:
                targets = re.sub(r"\s*,\s*", " ", m2.group(1).strip())
            except Exception:
                targets = ""
            parsed_commands.append(f"rm {targets}")
            continue

        # -------------------------
        # CHANGE DIRECTORY
        # -------------------------
        m3 = re.search(
            r"(go to|cd to|change directory to|enter|open)\s+"
            r"(?:the|a|an|my)?\s*"
            r"(?:new\s+)?"
            r"(?:folder|directory|dir|subfolder)?\s*"
            r"(?:called|named|as|is)?\s*"
            r"([\w\-\_\/\.]+|/)",
            cmd, re.IGNORECASE
        )
        if m3:
            parsed_commands.append(f"cd {m3.group(1 if m3.lastindex is None else 1)}")
            try:
                parsed_commands.append(f"cd {m3.group(1)}")
            except Exception:
                parsed_commands.append(f"cd {m3.group(0)}")
            continue

        # -------------------------
        # READ FILE
        # -------------------------
        m4 = re.search(
            r"(read|open|cat|show content of|display)\s+"
            r"(?:the|a|an|my)?\s*"
            r"(?:new\s+)?"
            r"(?:file|document|text)?\s*"
            r"(?:called|named|as|is)?\s*"
            r"([\w\-\_\.]+)",
            cmd, re.IGNORECASE
        )
        if m4:
            parsed_commands.append(f"cat {m4.group(1 if m4.lastindex is None else 1)}")
            try:
                parsed_commands.append(f"cat {m4.group(1)}")
            except Exception:
                parsed_commands.append(f"cat {m4.group(0)}")
            continue

        # -------------------------
        # SIMPLE NO-ARG COMMANDS
        # -------------------------
        if any(k in cmd for k in ["list", "show files", "show folders", "ls", "show all files", "show all folders", "show"]):
            parsed_commands.append("ls")
        elif any(k in cmd for k in ["where am i", "current directory", "current path", "path", "pwd"]):
            parsed_commands.append("pwd")
        elif "cpu" in cmd:
            parsed_commands.append("cpu")
        elif "mem" in cmd or "ram" in cmd:
            parsed_commands.append("mem")
        elif "process" in cmd or "ps" in cmd:
            parsed_commands.append("ps")

    return " && ".join(parsed_commands) if parsed_commands else None

def call_hf_inference(text):
    if not HF_TOKEN:
        return None
    try:
        api = f"https://api-inference.huggingface.co/models/{MODEL}"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        prompt = (
            "Convert the user's natural language into a terminal command: "
            "ls, pwd, cd <dir>, mkdir <dir>, touch <file>, rm <target>, move <file> <folder>, cpu, mem, ps, cat <file>. "
            "Handle multiple commands separated by 'and'. Remove filler words: the, a, an, called, named, is. "
            f"User input: {text}\nOutput command:"
        )
        payload = {"inputs": prompt, "parameters": {"max_new_tokens": 100}}
        r = requests.post(api, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        out = r.json()
        if isinstance(out, list):
            txt = out[0].get("generated_text", "")
        elif isinstance(out, dict) and "error" in out:
            return None
        else:
            txt = str(out)
        return txt.strip().splitlines()[0]
    except Exception:
        return None

def nlp_to_command(text):
    cmd = simple_rule_parse(text)
    if cmd:
        return cmd
    cmd = call_hf_inference(text)
    if not cmd:
        return None
    return re.sub(r"\b(the|a|an|new|please|recently|is|called|named)\b", "", cmd, flags=re.IGNORECASE).strip()
