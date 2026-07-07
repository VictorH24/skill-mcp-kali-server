#!/usr/bin/env python3

import argparse, json, logging, os, shlex, subprocess, sys, traceback, threading

import uuid
import time
import select
import pty
import fcntl
import signal

from typing import Dict, Any
from flask import Flask, request, jsonify

# Logging
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


# Variables
SERVER_PORT = int(os.environ.get("SERVER_PORT", 55100))
SERVER_HOST = os.environ.get("SERVER_HOST", "127.0.0.1")
DEBUG_MODE = os.environ.get("DEBUG_MODE", "0").lower() in ("1", "true", "yes", "y", "on")
COMMAND_TIMEOUT = 900  # 15 minutes max for any command
HELP_OUTPUT_LIMIT = 5000  # Limit help output to keep context window usable
SESSION_OUTPUT_LIMIT = 10000  # Limit session output per poll
SESSION_TIMEOUT = 3600  # 1 hour max session lifetime
MAX_COMMAND_OUTPUT = 200000  # Cap command stdout/stderr to avoid memory growth
LOG_COMMANDS = os.environ.get("LOG_COMMANDS", "0").lower() in ("1", "true", "yes", "y", "on")

# Active interactive sessions storage
active_sessions: Dict[str, 'InteractiveSession'] = {}

# Kali Linux tool categories mapping
KALI_CATEGORIES = {
    "information-gathering": [
        "nmap", "masscan", "dmitry", "dnsenum", "dnsrecon", "fierce", "maltego",
        "netdiscover", "recon-ng", "spiderfoot", "theharvester", "wafw00f", "whatweb",
        "whois", "amass", "sublist3r", "enum4linux", "nbtscan", "onesixtyone",
        "smbclient", "smbmap", "snmpwalk", "snmp-check"
    ],
    "vulnerability-analysis": [
        "nikto", "nmap", "openvas", "legion", "lynis", "unix-privesc-check",
        "sqlmap", "wpscan", "nuclei", "searchsploit", "vulscan"
    ],
    "web-application": [
        "burpsuite", "dirb", "dirbuster", "gobuster", "feroxbuster", "ffuf", "nikto",
        "sqlmap", "wpscan", "wfuzz", "whatweb", "zaproxy", "httpx", "hakrawler",
        "arjun", "commix", "xsser", "dalfox"
    ],
    "password-attacks": [
        "hydra", "john", "hashcat", "medusa", "ncrack", "ophcrack", "wordlists",
        "crunch", "cewl", "cupp", "hash-identifier", "hashid", "patator", "thc-pptp-bruter"
    ],
    "wireless-attacks": [
        "aircrack-ng", "airmon-ng", "airodump-ng", "aireplay-ng", "cowpatty", "fern-wifi-cracker",
        "kismet", "pixiewps", "reaver", "wifite", "bully", "hostapd-wpe"
    ],
    "exploitation": [
        "metasploit", "msfconsole", "msfvenom", "armitage", "beef-xss", "exploitdb",
        "searchsploit", "shellnoob", "social-engineering-toolkit", "setoolkit"
    ],
    "sniffing-spoofing": [
        "wireshark", "tshark", "tcpdump", "ettercap", "bettercap", "arpspoof",
        "dnsspoof", "macchanger", "mitmproxy", "responder", "sslstrip", "netsniff-ng"
    ],
    "post-exploitation": [
        "mimikatz", "powersploit", "empire", "bloodhound", "crackmapexec", "evil-winrm",
        "impacket", "pth-toolkit", "smbexec", "wmiexec", "psexec", "proxychains",
        "chisel", "ligolo", "pwncat"
    ],
    "forensics": [
        "autopsy", "binwalk", "bulk-extractor", "foremost", "galleta", "hashdeep",
        "volatility", "sleuthkit", "dc3dd", "extundelete", "scalpel", "pdf-parser"
    ],
    "reporting": [
        "cutycapt", "faraday", "maltego", "metagoofil", "pipal", "recordmydesktop"
    ],
    "reverse-engineering": [
        "ghidra", "radare2", "gdb", "edb-debugger", "ollydbg", "apktool",
        "dex2jar", "jd-gui", "jadx", "rizin", "cutter", "objdump", "strings"
    ],
    "hardware-hacking": [
        "arduino", "dfu-util", "flashrom", "openocd"
    ]
}

app = Flask(__name__)

class CommandExecutor:
    """Class to handle command execution with better timeout management"""
    
    def __init__(self, command: str, timeout: int = COMMAND_TIMEOUT):
        self.command = command
        self.timeout = timeout
        self.process = None
        self.stdout_data = ""
        self.stderr_data = ""
        self.stdout_thread = None
        self.stderr_thread = None
        self.return_code = None
        self.timed_out = False
        self._stop_event = threading.Event()
        self._stdout_lock = threading.Lock()
        self._stderr_lock = threading.Lock()
    
    def _read_stdout(self):
        """Thread function to continuously read stdout"""
        for line in iter(self.process.stdout.readline, ''):
            if self._stop_event.is_set():
                break
            with self._stdout_lock:
                self.stdout_data += line
                if len(self.stdout_data) > MAX_COMMAND_OUTPUT:
                    self.stdout_data = self.stdout_data[-MAX_COMMAND_OUTPUT:]
    
    def _read_stderr(self):
        """Thread function to continuously read stderr"""
        for line in iter(self.process.stderr.readline, ''):
            if self._stop_event.is_set():
                break
            with self._stderr_lock:
                self.stderr_data += line
                if len(self.stderr_data) > MAX_COMMAND_OUTPUT:
                    self.stderr_data = self.stderr_data[-MAX_COMMAND_OUTPUT:]
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command and handle timeout gracefully"""
        logger.info(f"Executing command: {self.command}")
        
        try:
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="backslashreplace",
                bufsize=1  # Line buffered
            )
            
            # Start threads to read output continuously
            self.stdout_thread = threading.Thread(target=self._read_stdout)
            self.stderr_thread = threading.Thread(target=self._read_stderr)
            self.stdout_thread.daemon = True
            self.stderr_thread.daemon = True
            self.stdout_thread.start()
            self.stderr_thread.start()
            
            # Wait for the process to complete or timeout
            try:
                self.return_code = self.process.wait(timeout=self.timeout)
                # Process completed, join the threads
                self._stop_event.set()
                self.stdout_thread.join()
                self.stderr_thread.join()
            except subprocess.TimeoutExpired:
                # Process timed out but we might have partial results
                self.timed_out = True
                logger.warning(f"Command timed out after {self.timeout} seconds. Terminating process.")
                
                # Try to terminate gracefully first
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)  # Give it 5 seconds to terminate
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate
                    logger.warning("Process not responding to termination. Killing.")
                    self.process.kill()
                finally:
                    self._stop_event.set()
                    if self.stdout_thread:
                        self.stdout_thread.join(timeout=2)
                    if self.stderr_thread:
                        self.stderr_thread.join(timeout=2)
                
                # Update final output
                self.return_code = -1
            
            # Always consider it a success if we have output, even with timeout
            success = True if self.timed_out and (self.stdout_data or self.stderr_data) else (self.return_code == 0)
            
            result = {
                "stdout": self.stdout_data,
                "stderr": self.stderr_data,
                "return_code": self.return_code,
                "success": success,
                "timed_out": self.timed_out,
                "partial_results": self.timed_out and (self.stdout_data or self.stderr_data)
            }
            return result
        
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "stdout": self.stdout_data,
                "stderr": f"Error executing command: {str(e)}\n{self.stderr_data}",
                "return_code": -1,
                "success": False,
                "timed_out": False,
                "partial_results": bool(self.stdout_data or self.stderr_data)
            }
        finally:
            try:
                if self.process and self.process.stdout:
                    self.process.stdout.close()
                if self.process and self.process.stderr:
                    self.process.stderr.close()
            except Exception:
                pass


def execute_command(command: str) -> Dict[str, Any]:
    """
    Execute a shell command and return the result
    
    Args:
        command: The command to execute
        
    Returns:
        A dictionary containing the stdout, stderr, and return code
    """
    executor = CommandExecutor(command)
    return executor.execute()


class InteractiveSession:
    """Class to manage interactive terminal sessions for tools like responder, ntlmrelayx, etc."""
    
    def __init__(self, command: str, session_id: str):
        self.command = command
        self.session_id = session_id
        self.process = None
        self.master_fd = None
        self.slave_fd = None
        self.output_buffer = ""
        self.started_at = time.time()
        self.last_activity = time.time()
        self.is_running = False
        self.return_code = None
        self.lock = threading.Lock()
        self.reader_thread = None
    
    def start(self) -> bool:
        """Start the interactive session with a PTY"""
        try:
            # Create a pseudo-terminal
            self.master_fd, self.slave_fd = pty.openpty()
            
            # Make master non-blocking
            flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
            fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            
            # Start the process with the PTY
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdin=self.slave_fd,
                stdout=self.slave_fd,
                stderr=self.slave_fd,
                preexec_fn=os.setsid  # Create new session
            )
            
            self.is_running = True
            
            # Start background reader thread
            self.reader_thread = threading.Thread(target=self._read_output_loop, daemon=True)
            self.reader_thread.start()
            
            logger.info(f"Started interactive session {self.session_id}: {self.command}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start interactive session: {str(e)}")
            self.cleanup()
            return False
    
    def _read_output_loop(self):
        """Background thread to continuously read output from the PTY"""
        while self.is_running:
            try:
                # Check if process is still running
                if self.process.poll() is not None:
                    self.return_code = self.process.returncode
                    self.is_running = False
                    break
                
                # Try to read from master
                ready, _, _ = select.select([self.master_fd], [], [], 0.5)
                if ready:
                    try:
                        data = os.read(self.master_fd, 4096)
                        if data:
                            with self.lock:
                                self.output_buffer += data.decode('utf-8', errors='replace')
                                self.last_activity = time.time()
                                # Trim buffer if too large (keep last 50KB)
                                if len(self.output_buffer) > 50000:
                                    self.output_buffer = self.output_buffer[-50000:]
                    except (OSError, IOError):
                        pass
                        
            except Exception as e:
                logger.error(f"Error in session reader: {str(e)}")
                break
        
        # Final read attempt
        try:
            while True:
                ready, _, _ = select.select([self.master_fd], [], [], 0.1)
                if not ready:
                    break
                data = os.read(self.master_fd, 4096)
                if not data:
                    break
                with self.lock:
                    self.output_buffer += data.decode('utf-8', errors='replace')
        except:
            pass
    
    def get_output(self, clear: bool = True) -> str:
        """Get accumulated output, optionally clearing the buffer"""
        with self.lock:
            output = self.output_buffer
            if clear:
                self.output_buffer = ""
            return output
    
    def send_input(self, text: str) -> bool:
        """Send input to the interactive session"""
        try:
            if self.master_fd and self.is_running:
                os.write(self.master_fd, text.encode('utf-8'))
                self.last_activity = time.time()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to send input to session: {str(e)}")
            return False
    
    def send_signal(self, sig: int) -> bool:
        """Send a signal to the process (e.g., SIGINT for Ctrl+C)"""
        try:
            if self.process and self.is_running:
                os.killpg(os.getpgid(self.process.pid), sig)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to send signal to session: {str(e)}")
            return False
    
    def stop(self) -> Dict[str, Any]:
        """Stop the interactive session"""
        final_output = self.get_output(clear=False)
        
        try:
            if self.process and self.is_running:
                # Try SIGTERM first
                try:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                    self.process.wait(timeout=2)
                except ProcessLookupError:
                    pass
                
                self.return_code = self.process.returncode
        except Exception as e:
            logger.error(f"Error stopping session: {str(e)}")
        
        self.is_running = False
        self.cleanup()
        
        return {
            "session_id": self.session_id,
            "final_output": final_output,
            "return_code": self.return_code,
            "runtime_seconds": time.time() - self.started_at
        }
    
    def cleanup(self):
        """Clean up file descriptors"""
        try:
            if self.master_fd:
                os.close(self.master_fd)
        except:
            pass
        try:
            if self.slave_fd:
                os.close(self.slave_fd)
        except:
            pass
        self.master_fd = None
        self.slave_fd = None
    
    def get_status(self) -> Dict[str, Any]:
        """Get session status information"""
        return {
            "session_id": self.session_id,
            "command": self.command,
            "is_running": self.is_running,
            "started_at": self.started_at,
            "runtime_seconds": time.time() - self.started_at,
            "last_activity": self.last_activity,
            "idle_seconds": time.time() - self.last_activity,
            "return_code": self.return_code,
            "output_buffer_size": len(self.output_buffer)
        }


def cleanup_expired_sessions():
    """Remove sessions that have exceeded the timeout"""
    current_time = time.time()
    expired = []
    
    for session_id, session in active_sessions.items():
        if current_time - session.started_at > SESSION_TIMEOUT:
            expired.append(session_id)
        elif not session.is_running and current_time - session.last_activity > 300:  # 5 min after stopped
            expired.append(session_id)
    
    for session_id in expired:
        try:
            session = active_sessions.pop(session_id)
            session.stop()
            logger.info(f"Cleaned up expired session: {session_id}")
        except:
            pass


@app.route("/api/search_tools", methods=["POST"])
def search_tools():
    """Search for available tools in Kali Linux by name or category."""
    try:
        params = request.json
        query = params.get("query", "").lower().strip()
        
        if not query:
            logger.warning("Search tools called without query parameter")
            return jsonify({
                "error": "Query parameter is required"
            }), 400
        
        results = []
        
        # Check if query is a category name
        if query in KALI_CATEGORIES:
            # Return all tools in this category
            for tool in KALI_CATEGORIES[query]:
                # Check if tool exists on system
                quoted_tool = shlex.quote(tool)
                which_result = execute_command(f"which {quoted_tool} 2>/dev/null")
                tool_path = which_result.get("stdout", "").strip() if which_result.get("success") else None
                
                results.append({
                    "tool": tool,
                    "category": query,
                    "path": tool_path if tool_path else "not installed",
                    "installed": bool(tool_path)
                })
            
            return jsonify({
                "query": query,
                "type": "category",
                "results": results,
                "total": len(results),
                "installed_count": sum(1 for r in results if r["installed"])
            })
        
        # Search for tool by name across all categories
        matched_tools = []
        for category, tools in KALI_CATEGORIES.items():
            for tool in tools:
                if query in tool:
                    quoted_tool = shlex.quote(tool)
                    which_result = execute_command(f"which {quoted_tool} 2>/dev/null")
                    tool_path = which_result.get("stdout", "").strip() if which_result.get("success") else None
                    
                    matched_tools.append({
                        "tool": tool,
                        "category": category,
                        "path": tool_path if tool_path else "not installed",
                        "installed": bool(tool_path)
                    })
        
        # Also try to find the tool directly on the system using 'which' and 'apt-cache'
        if not matched_tools:
            # Try which command
            quoted_query = shlex.quote(query)
            which_result = execute_command(f"which {quoted_query} 2>/dev/null")
            if which_result.get("success") and which_result.get("stdout", "").strip():
                tool_path = which_result["stdout"].strip()
                matched_tools.append({
                    "tool": query,
                    "category": "system",
                    "path": tool_path,
                    "installed": True
                })
            
            # Try apt-cache search for packages
            apt_query = shlex.quote(f"^{query}")
            apt_result = execute_command(f"apt-cache search --names-only {apt_query} 2>/dev/null | head -20")
            if apt_result.get("success") and apt_result.get("stdout", "").strip():
                for line in apt_result["stdout"].strip().split("\n"):
                    if line:
                        parts = line.split(" - ", 1)
                        pkg_name = parts[0].strip()
                        description = parts[1].strip() if len(parts) > 1 else ""
                        # Check if installed
                        quoted_pkg_name = shlex.quote(pkg_name)
                        which_pkg = execute_command(f"which {quoted_pkg_name} 2>/dev/null")
                        pkg_path = which_pkg.get("stdout", "").strip() if which_pkg.get("success") else None
                        
                        matched_tools.append({
                            "tool": pkg_name,
                            "category": "apt-package",
                            "path": pkg_path if pkg_path else "not installed",
                            "description": description,
                            "installed": bool(pkg_path)
                        })
        
        return jsonify({
            "query": query,
            "type": "tool_search",
            "results": matched_tools,
            "total": len(matched_tools),
            "installed_count": sum(1 for r in matched_tools if r["installed"]),
            "available_categories": list(KALI_CATEGORIES.keys())
        })
        
    except Exception as e:
        logger.error(f"Error in search_tools endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500


@app.route("/api/read_tool_manual", methods=["POST"])
def read_tool_manual():
    """Get the help/manual for a specified tool."""
    try:
        params = request.json
        tool = params.get("tool", "").strip()
        
        if not tool:
            logger.warning("Read tool manual called without tool parameter")
            return jsonify({
                "error": "Tool parameter is required"
            }), 400
        
        # First check if tool exists
        quoted_tool = shlex.quote(tool)
        which_result = execute_command(f"which {quoted_tool} 2>/dev/null")
        if not which_result.get("success") or not which_result.get("stdout", "").strip():
            return jsonify({
                "error": f"Tool '{tool}' not found on system",
                "suggestion": "Use search_tools to find available tools"
            }), 404
        
        tool_path = which_result["stdout"].strip()
        
        # Try different help options in order of preference
        help_commands = [
            f"{quoted_tool} --help 2>&1",
            f"{quoted_tool} -h 2>&1",
            f"{quoted_tool} help 2>&1",
            f"man {quoted_tool} 2>/dev/null | col -b | head -200"
        ]
        
        help_output = None
        help_source = None
        
        for cmd in help_commands:
            result = execute_command(cmd)
            output = result.get("stdout", "") + result.get("stderr", "")
            
            # Check if we got useful output (not just error messages about invalid options)
            if output and len(output.strip()) > 50:
                # Filter out common error patterns that indicate the help failed
                if not any(err in output.lower() for err in ["unknown option", "invalid option", "unrecognized option", "no manual entry"]):
                    help_output = output
                    help_source = cmd.split()[0] if "man" in cmd else "--help"
                    break
        
        if not help_output:
            return jsonify({
                "tool": tool,
                "path": tool_path,
                "error": "Could not retrieve help for this tool",
                "suggestion": "Try running the tool directly to see usage information"
            }), 200
        
        # Truncate output to keep context window usable
        truncated = False
        if len(help_output) > HELP_OUTPUT_LIMIT:
            help_output = help_output[:HELP_OUTPUT_LIMIT]
            # Try to cut at a newline for cleaner output
            last_newline = help_output.rfind("\n")
            if last_newline > HELP_OUTPUT_LIMIT - 500:
                help_output = help_output[:last_newline]
            help_output += "\n\n... [OUTPUT TRUNCATED - Use the tool directly for full help]"
            truncated = True
        
        return jsonify({
            "tool": tool,
            "path": tool_path,
            "help_source": help_source,
            "help_output": help_output,
            "truncated": truncated,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Error in read_tool_manual endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500


@app.route("/api/run_terminal_command", methods=["POST"])
def run_terminal_command():
    """Execute any terminal command provided in the request."""
    try:
        params = request.json
        command = params.get("command", "")
        timeout = params.get("timeout", COMMAND_TIMEOUT)
        
        if not command:
            logger.warning("Run terminal command called without command parameter")
            return jsonify({
                "error": "Command parameter is required"
            }), 400
        
        # Use custom timeout if provided
        executor = CommandExecutor(command, timeout=timeout)
        result = executor.execute()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in run_terminal_command endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500


@app.route("/api/session/start", methods=["POST"])
def start_session():
    """Start a new interactive session for long-running or interactive tools."""
    try:
        # Cleanup old sessions first
        cleanup_expired_sessions()
        
        params = request.json
        command = params.get("command", "")
        
        if not command:
            return jsonify({"error": "Command parameter is required"}), 400
        
        # Generate session ID
        session_id = str(uuid.uuid4())[:8]
        
        # Create and start session
        session = InteractiveSession(command, session_id)
        if not session.start():
            return jsonify({"error": "Failed to start session"}), 500
        
        active_sessions[session_id] = session
        
        # Wait a moment for initial output
        time.sleep(0.5)
        initial_output = session.get_output()
        
        return jsonify({
            "session_id": session_id,
            "command": command,
            "status": "running",
            "initial_output": initial_output[:SESSION_OUTPUT_LIMIT] if len(initial_output) > SESSION_OUTPUT_LIMIT else initial_output,
            "message": "Session started. Use /api/session/poll to get output, /api/session/input to send input, and /api/session/stop to terminate."
        })
        
    except Exception as e:
        logger.error(f"Error starting session: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/session/poll", methods=["POST"])
def poll_session():
    """Poll for new output from an interactive session."""
    try:
        params = request.json
        session_id = params.get("session_id", "")
        clear_buffer = params.get("clear", True)
        
        if not session_id:
            return jsonify({"error": "session_id parameter is required"}), 400
        
        session = active_sessions.get(session_id)
        if not session:
            return jsonify({"error": f"Session {session_id} not found"}), 404
        
        output = session.get_output(clear=clear_buffer)
        status = session.get_status()
        
        # Truncate output if too large
        truncated = False
        if len(output) > SESSION_OUTPUT_LIMIT:
            output = output[-SESSION_OUTPUT_LIMIT:]  # Keep the most recent output
            truncated = True
        
        return jsonify({
            "session_id": session_id,
            "output": output,
            "truncated": truncated,
            "is_running": status["is_running"],
            "runtime_seconds": status["runtime_seconds"],
            "return_code": status["return_code"]
        })
        
    except Exception as e:
        logger.error(f"Error polling session: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/session/input", methods=["POST"])
def send_session_input():
    """Send input to an interactive session."""
    try:
        params = request.json
        session_id = params.get("session_id", "")
        input_text = params.get("input", "")
        send_enter = params.get("send_enter", True)
        
        if not session_id:
            return jsonify({"error": "session_id parameter is required"}), 400
        
        session = active_sessions.get(session_id)
        if not session:
            return jsonify({"error": f"Session {session_id} not found"}), 404
        
        if not session.is_running:
            return jsonify({"error": "Session is no longer running"}), 400
        
        # Add newline if requested
        if send_enter and not input_text.endswith('\n'):
            input_text += '\n'
        
        success = session.send_input(input_text)
        
        # Brief wait for response
        time.sleep(0.3)
        output = session.get_output()
        
        return jsonify({
            "session_id": session_id,
            "input_sent": success,
            "output": output[:SESSION_OUTPUT_LIMIT] if len(output) > SESSION_OUTPUT_LIMIT else output
        })
        
    except Exception as e:
        logger.error(f"Error sending input to session: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/session/signal", methods=["POST"])
def send_session_signal():
    """Send a signal to an interactive session (e.g., Ctrl+C)."""
    try:
        params = request.json
        session_id = params.get("session_id", "")
        signal_name = params.get("signal", "SIGINT")  # Default to Ctrl+C
        
        if not session_id:
            return jsonify({"error": "session_id parameter is required"}), 400
        
        session = active_sessions.get(session_id)
        if not session:
            return jsonify({"error": f"Session {session_id} not found"}), 404
        
        # Map signal names to signal numbers
        signal_map = {
            "SIGINT": signal.SIGINT,
            "SIGTERM": signal.SIGTERM,
            "SIGKILL": signal.SIGKILL,
            "SIGHUP": signal.SIGHUP,
            "SIGTSTP": signal.SIGTSTP,  # Ctrl+Z
        }
        
        sig = signal_map.get(signal_name.upper())
        if sig is None:
            return jsonify({"error": f"Unknown signal: {signal_name}"}), 400
        
        success = session.send_signal(sig)
        
        # Brief wait for response
        time.sleep(0.5)
        output = session.get_output()
        
        return jsonify({
            "session_id": session_id,
            "signal_sent": signal_name,
            "success": success,
            "output": output[:SESSION_OUTPUT_LIMIT] if len(output) > SESSION_OUTPUT_LIMIT else output,
            "is_running": session.is_running
        })
        
    except Exception as e:
        logger.error(f"Error sending signal to session: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/session/stop", methods=["POST"])
def stop_session():
    """Stop an interactive session and get final output."""
    try:
        params = request.json
        session_id = params.get("session_id", "")
        
        if not session_id:
            return jsonify({"error": "session_id parameter is required"}), 400
        
        session = active_sessions.pop(session_id, None)
        if not session:
            return jsonify({"error": f"Session {session_id} not found"}), 404
        
        result = session.stop()
        
        return jsonify({
            "session_id": session_id,
            "status": "stopped",
            "final_output": result["final_output"][-SESSION_OUTPUT_LIMIT:] if len(result["final_output"]) > SESSION_OUTPUT_LIMIT else result["final_output"],
            "return_code": result["return_code"],
            "runtime_seconds": result["runtime_seconds"]
        })
        
    except Exception as e:
        logger.error(f"Error stopping session: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/session/list", methods=["GET"])
def list_sessions():
    """List all active sessions."""
    try:
        cleanup_expired_sessions()
        
        sessions = []
        for session_id, session in active_sessions.items():
            sessions.append(session.get_status())
        
        return jsonify({
            "sessions": sessions,
            "total": len(sessions)
        })
        
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/api/list_categories", methods=["GET"])
def list_categories():
    """List all available Kali tool categories."""
    return jsonify({
        "categories": list(KALI_CATEGORIES.keys()),
        "total": len(KALI_CATEGORIES)
    })


# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    # Check if essential tools are installed
    essential_tools = ["nmap", "gobuster", "dirb", "nikto"]
    tools_status = {}
    
    for tool in essential_tools:
        try:
            quoted_tool = shlex.quote(tool)
            result = execute_command(f"which {quoted_tool}")
            tools_status[tool] = result["success"]
        except:
            tools_status[tool] = False
    
    all_essential_tools_available = all(tools_status.values())
    
    return jsonify({
        "status": "healthy",
        "message": "Kali Linux Tools API Server is running",
        "tools_status": tools_status,
        "all_essential_tools_available": all_essential_tools_available
    })

@app.route("/mcp/capabilities", methods=["GET"])
def get_capabilities():
    # Return tool capabilities similar to our existing MCP server
    pass

@app.route("/mcp/tools/kali_tools/<tool_name>", methods=["POST"])
def execute_tool(tool_name):
    # Direct tool execution without going through the API server
    pass

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Kali Linux API Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--port", type=int, default=SERVER_PORT, help=f"Port for the API server (default: {SERVER_PORT})")
    parser.add_argument("--ip", type=str, default=SERVER_HOST, help=f"IP address to bind the server to (default: {SERVER_HOST})")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    # Set configuration from command line arguments
    if args.debug:
        DEBUG_MODE = True
        os.environ["DEBUG_MODE"] = "1"
        logger.setLevel(logging.DEBUG)
    
    if args.port != SERVER_PORT:
        SERVER_PORT = args.port
    
    logger.info(f"Starting Kali Linux Tools API Server on {args.ip}:{SERVER_PORT}")
    app.run(host=args.ip, port=SERVER_PORT, debug=DEBUG_MODE)
