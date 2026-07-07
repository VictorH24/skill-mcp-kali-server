#!/usr/bin/env python3

import logging
import os
from typing import Any, Dict, Optional

import requests
from fastmcp import FastMCP


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

API_BASE_URL = os.environ.get("KALI_API_URL", "http://127.0.0.1:55100").rstrip("/")
MCP_HOST = os.environ.get("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.environ.get("MCP_PORT", "3333"))
MCP_PATH = os.environ.get("MCP_PATH", "/mcp")
COMMAND_TIMEOUT = int(os.environ.get("KALI_COMMAND_TIMEOUT", "900"))
REQUEST_TIMEOUT = int(os.environ.get("KALI_API_REQUEST_TIMEOUT", str(COMMAND_TIMEOUT)))
MCP_STATELESS_HTTP = os.environ.get("MCP_STATELESS_HTTP", "1").lower() in ("1", "true", "yes", "y")

mcp = FastMCP("kali")


def api_request(method: str, path: str, request_timeout: Optional[int] = None, **kwargs: Any) -> Dict[str, Any]:
    url = f"{API_BASE_URL}{path}"
    timeout = request_timeout if request_timeout is not None else REQUEST_TIMEOUT
    try:
        response = requests.request(method, url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.error("Request to Kali API failed: %s", exc)
        return {"success": False, "error": str(exc)}
    except ValueError as exc:
        logger.error("Kali API returned non-JSON response: %s", exc)
        return {"success": False, "error": "Kali API returned a non-JSON response"}


@mcp.tool()
def search_tools(query: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Search Kali tools by name or category."""
    return api_request("POST", "/api/search_tools", json={"query": query})


@mcp.tool()
def read_tool_manual(tool: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Read help/manual output for an installed Kali tool."""
    return api_request("POST", "/api/read_tool_manual", json={"tool": tool})


@mcp.tool()
def run_terminal_command(
    command: str,
    timeout: Optional[int] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Run an authorized terminal command on the Kali server."""
    payload: Dict[str, Any] = {"command": command}
    command_timeout = timeout if timeout is not None else COMMAND_TIMEOUT
    payload["timeout"] = command_timeout
    return api_request(
        "POST",
        "/api/run_terminal_command",
        request_timeout=command_timeout + 10,
        json=payload,
    )


@mcp.tool()
def start_interactive_session(command: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Start an interactive terminal session for a long-running command."""
    return api_request("POST", "/api/session/start", json={"command": command})


@mcp.tool()
def poll_session(
    session_id: str,
    clear: bool = True,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Poll output from an interactive terminal session."""
    return api_request("POST", "/api/session/poll", json={"session_id": session_id, "clear": clear})


@mcp.tool()
def send_session_input(
    session_id: str,
    input_text: str,
    send_enter: bool = True,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Send input to an interactive terminal session."""
    return api_request(
        "POST",
        "/api/session/input",
        json={"session_id": session_id, "input": input_text, "send_enter": send_enter},
    )


@mcp.tool()
def send_session_signal(
    session_id: str,
    signal_name: str = "SIGINT",
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a signal such as SIGINT or SIGTERM to an interactive terminal session."""
    return api_request(
        "POST",
        "/api/session/signal",
        json={"session_id": session_id, "signal": signal_name},
    )


@mcp.tool()
def stop_session(session_id: str, description: Optional[str] = None) -> Dict[str, Any]:
    """Stop an interactive terminal session."""
    return api_request("POST", "/api/session/stop", json={"session_id": session_id})


@mcp.tool()
def list_sessions() -> Dict[str, Any]:
    """List active interactive terminal sessions."""
    return api_request("GET", "/api/session/list")


@mcp.tool()
def list_categories() -> Dict[str, Any]:
    """List available Kali tool categories."""
    return api_request("GET", "/api/list_categories")


def run_mcp_server() -> None:
    run_options: Dict[str, Any] = {
        "host": MCP_HOST,
        "port": MCP_PORT,
        "path": MCP_PATH,
    }

    if MCP_STATELESS_HTTP:
        run_options["stateless_http"] = True

    try:
        mcp.run(transport="streamable-http", **run_options)
    except TypeError:
        run_options.pop("stateless_http", None)
        mcp.run(transport="streamable-http", **run_options)
    except ValueError:
        run_options.pop("stateless_http", None)
        mcp.run(transport="http", **run_options)


if __name__ == "__main__":
    logger.info("Starting Kali MCP bridge on %s:%s%s", MCP_HOST, MCP_PORT, MCP_PATH)
    logger.info("Forwarding tool calls to Kali API at %s", API_BASE_URL)
    logger.info("Stateless MCP HTTP mode: %s", MCP_STATELESS_HTTP)
    run_mcp_server()
