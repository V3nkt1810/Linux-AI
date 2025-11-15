# validator.py
import re, json
from jsonschema import validate, ValidationError

# JSON schema expected from model
SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string"},
        "commands": {
            "type": "array",
            "items": {"type": "string"}
        },
        "explanation": {"type": ["string","null"]},
        "rollback": {"type": ["string","null"]}
    },
    "required": ["action","commands"]
}

# Whitelist: list of compiled regex patterns (from earlier conversation)
WHITELIST_PATTERNS = [
    re.compile(r"^systemctl\s+(status|restart|start|stop|is-active)\s+[A-Za-z0-9._@-]+(\.service)?$"),
    re.compile(r"^journalctl\s+-u\s+[A-Za-z0-9._@-]+(\s+-n\s+\d+)?$"),
    re.compile(r"^tail\s+-n\s+\d+\s+(/[\w/.\-]+)$"),
    re.compile(r"^df\s+-h$"),
    re.compile(r"^du\s+-sh\s+(/[\w/.\-]+)(/\*)?$"),
    re.compile(r"^find\s+(/[\w/.\-]+)\s+-type\s+f\s+-name\s+\"?[\w\*\.\-]+\"?(\s+-mtime\s+\+\d+)?$"),
    re.compile(r"^ps\s+aux(\s+--sort=\S+)?\s*\|\s*head(\s+-\d+)?$"),
    re.compile(r"^kill\s+-9\s+\d+$"),
    re.compile(r"^yum\s+check-update$"),
    re.compile(r"^rpm\s+-qa(\s+\|\s*grep\s+[\w-]+)?$"),
    re.compile(r"^smartctl\s+-a\s+\/dev\/[a-z0-9]+$"),
    re.compile(r"^docker\s+ps(\s+-a)?$"),
    re.compile(r"^docker\s+system\s+prune\s+-af$")
]

def is_command_allowed(cmd: str) -> bool:
    cmd = cmd.strip()
    for pat in WHITELIST_PATTERNS:
        if pat.match(cmd):
            return True
    return False

def validate_model_output(parsed_obj):
    # Ensure schema
    try:
        validate(parsed_obj, SCHEMA)
    except ValidationError as e:
        return False, f"Schema validation failed: {e.message}"

    # Validate commands
    for c in parsed_obj.get("commands", []):
        if not is_command_allowed(c):
            return False, f"Command not allowed: {c}"
    # If rollback present, validate it too
    rb = parsed_obj.get("rollback")
    if rb:
        if not is_command_allowed(rb):
            return False, f"Rollback not allowed: {rb}"
    return True, "OK"

if __name__ == "__main__":
    import sys
    text = sys.stdin.read()
    try:
        obj = json.loads(text)
    except Exception as e:
        print("Invalid JSON input")
        sys.exit(2)
    ok, msg = validate_model_output(obj)
    print(ok, msg)
