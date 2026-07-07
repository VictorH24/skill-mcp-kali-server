# SKILL and MCP Kali Server

API and MCP bridge that exposes Kali Linux command-line tools for programmatic access, enabling searching, tool documentation retrieval, and command execution with timeouts. It supports both direct API calls and interactive terminal sessions, deployable as a Docker container for authorized security testing workflows.

This project is intended for authorized security testing in a local lab or against systems you have explicit permission to assess. It exposes endpoints that can execute shell commands, so keep it bound to localhost unless you have added your own authentication and network controls.

inspired from https://gitlab.com/kalilinux/packages/mcp-kali-server

## What It Provides

- Flask API for searching installed Kali tools and reading help output.
- Terminal command execution with timeouts and capped output.
- Interactive terminal sessions for long-running tools.
- Optional MCP bridge on `http://localhost:3333/mcp`.
- Docker image based on `kalilinux/kali-rolling`.

## Quick Start

### Download the image:

```sh
docker pull ghcr.io/victorh24/skill-mcp-kali-server:latest
```

### Start the container:

```sh
docker run -d --restart unless-stopped -p 127.0.0.1:5000:5000 --name skill-mcp-kali-server ghcr.io/victorh24/skill-mcp-kali-server:latest
```

### Build the image:

```sh
docker build -t skill-mcp-kali-server .
```

Run the MCP server:

```sh
docker run -it --restart unless-stopped -p 127.0.0.1:3333:3333 -d skill-mcp-kali-server 
```

Run the kali api only (no MCP, to use the skills only) 

```sh
docker run -it --restart unless-stopped -p 127.0.0.1:5000:5000 -d skill-mcp-kali-server 
```

or both

```sh
docker run -it --restart unless-stopped -p 127.0.0.1:5000:5000 -p 127.0.0.1:3333:3333 -d mcp-kali-server 
```

The container publishes the API on `http://localhost:5000` and the MCP bridge on `http://localhost:3333/mcp`.

## Skill

This repository includes a Codex skill for using the Kali API directly when you do not want to use the MCP bridge:

- Skill folder: `skills/kali-direct-api`
- Skill name: `$kali-direct-api`
- Direct API target: `http://127.0.0.1:5000`

The skill includes a small helper script and raw `curl` examples for every API endpoint.

Check API health with the skill helper:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py health
```

Print `curl` commands for using the API without Python:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py curl-examples
```

Run a direct command through the API:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py run "nmap --version" --timeout 30
```

If the API is not running on `http://127.0.0.1:5000`, set `KALI_API_URL`:

```sh
KALI_API_URL=http://127.0.0.1:5000 python3 skills/kali-direct-api/scripts/kali_api.py health
```

## MCP Client Configuration

Example MCP cline (clien_mcp_settings.json):

```json
{
  "mcpServers": {
    "kali": {
      "autoApprove": [
        "start_interactive_session",
        "poll_session",
        "run_terminal_command",
        "search_tools"
      ],
      "disabled": false,
      "timeout": 3600,
      "type": "streamableHttp",
      "url": "http://localhost:3333/mcp"
    }
  }
}
```

For opencode or Vscode clients:

```json
{
  "kali": {
    "type": "remote",
    "url": "http://localhost:3333/mcp",
    "enabled": true,
    "timeout": 3600000
  }
}
```

## API Endpoints

- `GET /health`
- `GET /api/list_categories`
- `POST /api/search_tools` with `{"query": "nmap"}`
- `POST /api/read_tool_manual` with `{"tool": "nmap"}`
- `POST /api/run_terminal_command` with `{"command": "nmap --version", "timeout": 30}`
- `POST /api/session/start`
- `POST /api/session/poll`
- `POST /api/session/input`
- `POST /api/session/signal`
- `POST /api/session/stop`
- `GET /api/session/list`

## Local Development

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python kali_server.py
```

In another shell, start the MCP bridge:

```sh
python mcp_server_remote.py
```

Or run both with the supervisor:

```sh
python startserver.py
```

The MCP bridge defaults to stateless HTTP mode to avoid stale MCP session ids after restarts. Set `MCP_STATELESS_HTTP=0` if your client requires stateful streamable HTTP sessions.

## Security Notes

- Do not expose this service directly to the public internet.
- The command execution endpoint is intentionally powerful and should be treated like local shell access.
- Runtime logs are ignored by git because commands may contain target details or sensitive parameters.
- Only use this tool for legal, authorized testing.
