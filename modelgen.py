import csv
import random
import uuid

# ---------------------------------------
# CONFIGURABLE SIZE
# ---------------------------------------
TOTAL_ROWS = 100000
OUTPUT_FILE = "dataset_100k.csv"

# ---------------------------------------
# MASTER DICTIONARIES (extend anytime)
# ---------------------------------------

SERVICES = [
    "httpd", "nginx", "tomcat", "jboss", "docker",
    "sshd", "chronyd", "postfix", "rsyslog", "auditd"
]

LOG_FILES = [
    "/var/log/messages",
    "/var/log/secure",
    "/var/log/httpd/error_log",
    "/var/log/httpd/access_log",
    "/var/log/nginx/error.log",
    "/var/log/nginx/access.log"
]

DISK_PATHS = [
    "/", "/var", "/var/log", "/opt", "/home", "/tmp"
]

ISSUES = [
    "disk full",
    "cpu high",
    "memory leak",
    "service down",
    "service not responding",
    "port not listening",
    "slow performance",
    "high load average",
    "too many open files",
    "connection timeout",
    "package install error",
    "permission denied",
    "log rotation failed",
    "kernel error",
    "I/O error",
]

# SAFE COMMAND TEMPLATES
COMMAND_TEMPLATES = {
    "disk": [
        "df -h",
        "du -sh {path}/*",
        "find {path} -type f -mtime +30"
    ],
    "service": [
        "systemctl status {service}",
        "journalctl -u {service} -n 200"
    ],
    "service_restart": [
        "systemctl restart {service}",
        "journalctl -u {service} -n 100"
    ],
    "cpu": [
        "ps aux --sort=-%cpu | head -10",
        "top -b -n 1 | head -20"
    ],
    "memory": [
        "ps aux --sort=-%mem | head -10"
    ],
    "logs": [
        "tail -n 200 {logfile}"
    ],
    "network": [
        "ss -tulpn | grep {service}",
        "netstat -tulpn | grep {service}"
    ],
    "security": [
        "tail -n 200 /var/log/secure"
    ],
    "package": [
        "grep -i \"error\" /var/log/yum.log",
        "yum check-update"
    ]
}

ROLLBACKS = {
    "service": "systemctl start {service}",
    "service_restart": "systemctl start {service}"
}

# ---------------------------------------
# ROW GENERATOR
# ---------------------------------------
def generate_row():
    issue = random.choice(ISSUES)
    service = random.choice(SERVICES)
    path = random.choice(DISK_PATHS)
    logfile = random.choice(LOG_FILES)

    instruction = f"{issue} detected on server related to {service} or path {path}"

    cmd_list = []

    # Pick category
    if "disk" in issue:
        cmds = COMMAND_TEMPLATES["disk"]
    elif "cpu" in issue:
        cmds = COMMAND_TEMPLATES["cpu"]
    elif "memory" in issue:
        cmds = COMMAND_TEMPLATES["memory"]
    elif "service" in issue:
        cmds = COMMAND_TEMPLATES["service"]
    elif "port" in issue:
        cmds = COMMAND_TEMPLATES["network"]
    elif "package" in issue:
        cmds = COMMAND_TEMPLATES["package"]
    else:
        cmds = COMMAND_TEMPLATES["logs"]

    for c in cmds:
        c = c.format(service=service, path=path, logfile=logfile)
        cmd_list.append(c)

    explanation = f"This sequence checks {issue}, validates system behavior, and inspects logs or services."

    rollback = ""
    if "service" in issue:
        rollback = ROLLBACKS.get("service", "").format(service=service)

    return [
        instruction,
        "\n".join(cmd_list),
        explanation,
        rollback
    ]

# ---------------------------------------
# MAIN GENERATOR
# ---------------------------------------
with open(OUTPUT_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["instruction", "commands", "explanation", "rollback"])

    for _ in range(TOTAL_ROWS):
        writer.writerow(generate_row())

print(f"✔ DONE! Generated {TOTAL_ROWS} rows in {OUTPUT_FILE}")
