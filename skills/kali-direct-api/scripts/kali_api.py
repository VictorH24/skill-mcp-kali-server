#!/usr/bin/env python3
"""Small CLI client for the local MCP Kali Server Flask API."""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
import socket

DEFAULT_BASE_URL = "http://127.0.0.1:55100"


def curl_examples() -> str:
    url = base_url()
    return f"""# Set a reusable base URL.
KALI_API_URL={url}

# Health check.
curl -s "$KALI_API_URL/health" | jq .

# List Kali tool categories.
curl -s "$KALI_API_URL/api/list_categories" | jq .

# Search tools by name or category.
curl -s -X POST "$KALI_API_URL/api/search_tools" \\
  -H 'Content-Type: application/json' \\
  -d '{{"query":"nmap"}}' | jq .

curl -s -X POST "$KALI_API_URL/api/search_tools" \\
  -H 'Content-Type: application/json' \\
  -d '{{"query":"web-application"}}' | jq .

# Read a tool manual/help summary.
curl -s -X POST "$KALI_API_URL/api/read_tool_manual" \\
  -H 'Content-Type: application/json' \\
  -d '{{"tool":"nmap"}}' | jq .

# Run a one-shot command.
curl -s -X POST "$KALI_API_URL/api/run_terminal_command" \\
  -H 'Content-Type: application/json' \\
  -d '{{"command":"nmap --version","timeout":30}}' | jq .

# Start an interactive session.
curl -s -X POST "$KALI_API_URL/api/session/start" \\
  -H 'Content-Type: application/json' \\
  -d '{{"command":"python3 -i"}}' | jq .

# Poll, send input, signal, stop, and list sessions.
curl -s -X POST "$KALI_API_URL/api/session/poll" \\
  -H 'Content-Type: application/json' \\
  -d '{{"session_id":"SESSION_ID","clear":true}}' | jq .

curl -s -X POST "$KALI_API_URL/api/session/input" \\
  -H 'Content-Type: application/json' \\
  -d '{{"session_id":"SESSION_ID","input":"print(123)","send_enter":true}}' | jq .

curl -s -X POST "$KALI_API_URL/api/session/signal" \\
  -H 'Content-Type: application/json' \\
  -d '{{"session_id":"SESSION_ID","signal":"SIGINT"}}' | jq .

curl -s -X POST "$KALI_API_URL/api/session/stop" \\
  -H 'Content-Type: application/json' \\
  -d '{{"session_id":"SESSION_ID"}}' | jq .

curl -s "$KALI_API_URL/api/session/list" | jq ."""


def base_url() -> str:
    return os.environ.get("KALI_API_URL", DEFAULT_BASE_URL).rstrip("/")


def request_json(method: str, path: str, payload=None, timeout: int = 60):
    url = f"{base_url()}{path}"

    data = None
    headers = {"Accept": "application/json"}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")

            if not body.strip():
                return {}

            try:
                return json.loads(body)
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "invalid_json_response",
                    "detail": body,
                    "url": url,
                }

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")

        try:
            detail = json.loads(body) if body else {}
        except json.JSONDecodeError:
            detail = {"body": body}

        return {
            "success": False,
            "error": "http_error",
            "status": exc.code,
            "reason": exc.reason,
            "detail": detail,
            "url": url,
        }

    except socket.timeout:
        return {
            "success": False,
            "error": "client_timeout",
            "message": f"The HTTP client timed out after {timeout} seconds waiting for the Kali API response.",
            "hint": "The command may still be running server-side. For long scans, use session-start and session-poll instead of the blocking run command.",
            "url": url,
        }

    except TimeoutError:
        return {
            "success": False,
            "error": "timeout",
            "message": f"The request timed out after {timeout} seconds.",
            "url": url,
        }

    except urllib.error.URLError as exc:
        return {
            "success": False,
            "error": "connection_error",
            "message": str(exc.reason),
            "url": url,
        }

    except OSError as exc:
        return {
            "success": False,
            "error": "network_error",
            "message": str(exc),
            "url": url,
        }


def print_json(value) -> int:
    print(json.dumps(value, indent=2, sort_keys=True))

    if isinstance(value, dict) and value.get("success", True) is False:
        return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Call the local Kali API server directly.")
    parser.add_argument("--base-url", help=f"API base URL (default: {DEFAULT_BASE_URL})")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health", help="Check API health")
    subparsers.add_parser("categories", help="List Kali tool categories")
    subparsers.add_parser("session-list", help="List active interactive sessions")
    subparsers.add_parser("curl-examples", help="Print curl examples for every API endpoint")

    search = subparsers.add_parser("search-tools", help="Search tools by name or category")
    search.add_argument("query")

    manual = subparsers.add_parser("manual", help="Read help/manual output for a tool")
    manual.add_argument("tool")

    run = subparsers.add_parser("run", help="Run a one-shot terminal command")
    run.add_argument("shell_command")
    run.add_argument("--timeout", type=int, default=900)

    session_start = subparsers.add_parser("session-start", help="Start an interactive session")
    session_start.add_argument("shell_command")

    session_poll = subparsers.add_parser("session-poll", help="Poll an interactive session")
    session_poll.add_argument("session_id")
    session_poll.add_argument("--no-clear", action="store_true")

    session_input = subparsers.add_parser("session-input", help="Send input to a session")
    session_input.add_argument("session_id")
    session_input.add_argument("input_text")
    session_input.add_argument("--no-enter", action="store_true")

    session_signal = subparsers.add_parser("session-signal", help="Send a signal to a session")
    session_signal.add_argument("session_id")
    session_signal.add_argument("signal", nargs="?", default="SIGINT")

    session_stop = subparsers.add_parser("session-stop", help="Stop an interactive session")
    session_stop.add_argument("session_id")

    args = parser.parse_args()
    if args.base_url:
        os.environ["KALI_API_URL"] = args.base_url

    if args.command == "health":
        return print_json(request_json("GET", "/health"))
    if args.command == "categories":
        return print_json(request_json("GET", "/api/list_categories"))
    if args.command == "session-list":
        return print_json(request_json("GET", "/api/session/list"))
    if args.command == "curl-examples":
        print(curl_examples())
        return 0
    if args.command == "search-tools":
        return print_json(request_json("POST", "/api/search_tools", {"query": args.query}))
    if args.command == "manual":
        return print_json(request_json("POST", "/api/read_tool_manual", {"tool": args.tool}))
    # if args.command == "run":
    #     payload = {"command": args.shell_command, "timeout": args.timeout}
    #     return print_json(request_json("POST", "/api/run_terminal_command", payload, args.timeout + 15))
    if args.command == "run":
        payload = {"command": args.shell_command, "timeout": args.timeout}

        result = request_json(
            "POST",
            "/api/run_terminal_command",
            payload,
            args.timeout + 15,
        )

        if isinstance(result, dict) and result.get("error") in {"client_timeout", "timeout"}:
            result["command_timeout"] = args.timeout
            result["client_timeout"] = args.timeout + 15
            result["recommendation"] = (
                "Use session-start/session-poll for long-running commands like nikto, nmap, gobuster, ffuf, etc."
            )

        return print_json(result)
    if args.command == "session-start":
        return print_json(request_json("POST", "/api/session/start", {"command": args.shell_command}))
    if args.command == "session-poll":
        payload = {"session_id": args.session_id, "clear": not args.no_clear}
        return print_json(request_json("POST", "/api/session/poll", payload))
    if args.command == "session-input":
        payload = {
            "session_id": args.session_id,
            "input": args.input_text,
            "send_enter": not args.no_enter,
        }
        return print_json(request_json("POST", "/api/session/input", payload))
    if args.command == "session-signal":
        payload = {"session_id": args.session_id, "signal": args.signal}
        return print_json(request_json("POST", "/api/session/signal", payload))
    if args.command == "session-stop":
        return print_json(request_json("POST", "/api/session/stop", {"session_id": args.session_id}))

    parser.error(f"Unhandled command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
