#!/usr/bin/env python3
import os
import pwd
import re

# ===== COLOR CONFIG =====
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

print(BOLD + CYAN + "="*60 + RESET)
print(BOLD + CYAN + "   Sibermuda CronHunter v2 - Advanced Scanner" + RESET)
print(BOLD + CYAN + "="*60 + RESET)

CURRENT_USER = pwd.getpwuid(os.getuid()).pw_name

def is_writable(path):
    return os.access(path, os.W_OK)

def get_owner(path):
    return pwd.getpwuid(os.stat(path).st_uid).pw_name

def info(msg):
    print(BLUE + "[INFO] " + RESET + msg)

def good(msg):
    print(GREEN + "[OK] " + RESET + msg)

def warn(msg):
    print(YELLOW + "[WARNING] " + RESET + msg)

def critical(msg):
    print(RED + BOLD + "[CRITICAL] " + RESET + msg)

# ===== CHECK CRON FILES =====
def check_cron_files():
    print("\n" + CYAN + "[+] Checking cron configuration files...\n" + RESET)
    cron_paths = [
        "/etc/crontab",
        "/etc/cron.d",
        "/var/spool/cron",
        "/var/spool/cron/crontabs"
    ]

    for path in cron_paths:
        if os.path.exists(path):
            info(f"Found: {path}")

            if is_writable(path):
                critical(f"{path} writable by {CURRENT_USER}")

            owner = get_owner(path)
            if owner != "root":
                critical(f"{path} owned by {owner}, not root")
            else:
                good(f"{path} owned by root")

# ===== EXTRACT SCRIPTS =====
def extract_scripts_from_cron():
    scripts = []
    try:
        with open("/etc/crontab", "r") as f:
            lines = f.readlines()
            for line in lines:
                if not line.startswith("#") and len(line.split()) >= 7:
                    cmd = " ".join(line.split()[6:])
                    scripts.append(cmd.split()[0])
    except:
        pass
    return list(set(scripts))

# ===== ANALYZE SCRIPT =====
def analyze_script(script_path):
    if not os.path.exists(script_path):
        return

    print("\n" + CYAN + f"[ANALYZING] {script_path}" + RESET)

    if is_writable(script_path):
        critical("Script is writable!")

    owner = get_owner(script_path)
    if owner != "root":
        warn(f"Script owned by {owner}")
    else:
        good("Script owned by root")

    try:
        with open(script_path, "r") as f:
            content = f.read()

            if "*" in content:
                warn("Wildcard (*) detected — possible injection")

            if re.search(r"\b(tar|cp|mv|bash|sh|python)\b", content):
                if not re.search(r"/(bin|usr/bin|usr/local/bin)/", content):
                    warn("Relative binary execution — PATH hijack possible")

            cd_matches = re.findall(r"cd\s+([^\n]+)", content)
            for directory in cd_matches:
                directory = directory.strip()
                if os.path.exists(directory) and is_writable(directory):
                    critical(f"Script operates inside writable dir: {directory}")

            if "--checkpoint-action" in content:
                critical("Tar checkpoint-action detected!")

    except:
        warn("Could not read script")

# ===== CHECK PATH =====
def check_path():
    print("\n" + CYAN + "[+] Checking PATH for hijacking...\n" + RESET)
    path_dirs = os.environ.get("PATH", "").split(":")
    for d in path_dirs:
        if os.path.exists(d) and is_writable(d):
            critical(f"Writable PATH directory: {d}")
        else:
            good(f"{d} safe")

# ===== MAIN =====
def main():
    check_cron_files()
    scripts = extract_scripts_from_cron()

    for script in scripts:
        analyze_script(script)

    check_path()

    print("\n" + GREEN + BOLD + "[✔] Scan Complete.\n" + RESET)

if __name__ == "__main__":
    main()