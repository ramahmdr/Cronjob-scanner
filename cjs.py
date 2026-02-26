#!/usr/bin/env python3

import os
import stat
import pwd
import grp

# ====== COLOR CONFIG ======
RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

CRON_PATHS = [
    "/etc/crontab",
    "/etc/cron.d",
]

def color_print(text, color):
    print(color + text + RESET)

def get_owner(path):
    st = os.stat(path)
    return pwd.getpwuid(st.st_uid).pw_name, st.st_mode

def is_writable_by_non_root(path):
    st = os.stat(path)
    mode = st.st_mode
    if mode & stat.S_IWOTH:
        return True
    if mode & stat.S_IWGRP:
        return True
    return False

def check_file_security(path, context="binary"):
    try:
        owner, mode = get_owner(path)
    except:
        return

    perm = oct(mode)[-3:]

    print(f"        → {context}: {path}")
    print(f"          Owner: {owner}")
    print(f"          Perm : {perm}")

    # Root execution risk
    if owner != "root":
        color_print("          [CRITICAL] Executed file NOT owned by root!", RED)

    if is_writable_by_non_root(path):
        color_print("          [CRITICAL] File writable by non-root!", RED)

    if owner == "root" and not is_writable_by_non_root(path):
        color_print("          [SAFE] Ownership & permission look good", GREEN)


def extract_binary(cmd):
    parts = cmd.split()
    for p in parts:
        if p.startswith("/"):
            return p
    return None


def scan_cron_file(path):
    try:
        owner, mode = get_owner(path)
    except:
        return

    print(f"\n{BOLD}{BLUE}[+] Checking: {path}{RESET}")
    print(f"    Owner: {owner}")
    print(f"    Perm : {oct(mode)[-3:]}")

    if owner != "root":
        color_print("    [CRITICAL] Cron file not owned by root!", RED)

    if is_writable_by_non_root(path):
        color_print("    [CRITICAL] Cron file writable by non-root!", RED)

    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except:
        return

    for line in lines:
        if line.strip() == "" or line.startswith("#"):
            continue

        parts = line.split()
        if len(parts) < 6:
            continue

        user = parts[5]
        command = " ".join(parts[6:])

        print(f"\n      → Runs as: {user}")
        print(f"      → Command: {command}")

        binary = extract_binary(command)

        if binary and os.path.exists(binary):
            check_file_security(binary)
        elif binary:
            color_print("          [WARNING] Binary path does not exist", YELLOW)


def scan_directory(path):
    try:
        files = os.listdir(path)
    except PermissionError:
        color_print(f"[INFO] Permission denied: {path}", YELLOW)
        return

    for file in files:
        full = os.path.join(path, file)
        if os.path.isfile(full):
            scan_cron_file(full)


print(BOLD + "\n=== Cronjob Misconfiguratin ===\n" + RESET)

for path in CRON_PATHS:
    if os.path.isfile(path):
        scan_cron_file(path)
    elif os.path.isdir(path):
        scan_directory(path)