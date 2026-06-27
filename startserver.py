import subprocess
import signal
import sys
import os
import time
import threading
from datetime import datetime

VENV_PYTHON = ".venv/bin/python"
LOG_DIR = "./log"

children = []
stop_event = threading.Event()


def ensure_logs_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def stream_output(name: str, proc: subprocess.Popen, log_file):
    """
    Read stdout line-by-line, print it live, and also write to the log file.
    """
    for line in iter(proc.stdout.readline, ""):
        if stop_event.is_set():
            break

        if not isinstance(line, str):
            continue
            
        line = line.rstrip("\n")
        msg = f"[{name}] {line}"
        print(msg, flush=True)
        log_file.write(msg + "\n")
        log_file.flush()


def start_script(script_path: str, name: str):
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Required script not found: {script_path}")

    ensure_logs_dir()
    log_path = os.path.join(LOG_DIR, f"{name}.log")

    log_file = open(log_path, "a", encoding="utf-8")
    log_file.write(f"\n\n===== START {script_path} {datetime.now()} =====\n")
    log_file.flush()

    # start a new process group so we can stop whole tree
    proc = subprocess.Popen(
        [VENV_PYTHON, script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # merge stderr into stdout
        text=True,
        encoding="utf-8",
        errors="backslashreplace",
        bufsize=1,
        preexec_fn=os.setsid
    )
    # proc = subprocess.Popen(
    #     [VENV_PYTHON, script_path],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.STDOUT,
    #     text=False,               # ✅ bytes
    #     bufsize=0,
    #     preexec_fn=os.setsid
    # )

    children.append((name, proc, log_file))
    print(f"Started {script_path} as {name} (PID={proc.pid}) log={log_path}", flush=True)

    # reader thread (prints live + writes logs)
    t = threading.Thread(target=stream_output, args=(name, proc, log_file), daemon=True)
    t.start()

    return proc


def shutdown(signum, frame):
    if stop_event.is_set():
        return

    stop_event.set()
    print(f"\nReceived signal {signum}. Stopping children...", flush=True)

    # send SIGTERM to each process group
    for name, proc, log_file in children:
        if proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                log_file.write(f"\n===== STOP (SIGTERM) {datetime.now()} =====\n")
                log_file.flush()
            except ProcessLookupError:
                pass

    # give time for graceful shutdown
    time.sleep(2)

    # force kill if still running
    for name, proc, log_file in children:
        if proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                log_file.write(f"\n===== FORCE STOP (SIGKILL) {datetime.now()} =====\n")
                log_file.flush()
            except ProcessLookupError:
                pass

    # close log files
    for _, _, log_file in children:
        try:
            log_file.close()
        except Exception:
            pass

    print("All children stopped. Exiting.", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    # handle Ctrl+C and docker stop
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    start_script("kali_server.py", "kali_server")
    start_script("mcp_server_remote.py", "mcp_server_remote")

    print("Supervisor running. Press Ctrl+C to stop everything.", flush=True)

    # Keep running until interrupted.
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown(signal.SIGINT, None)
