---
name: kali-direct-api
description: Direct HTTP access to the local Kali Linux API server on port 55100 without using the MCP bridge. Use when Codex needs to search Kali tools, read tool help, run authorized terminal commands, or manage interactive Kali sessions by calling http://127.0.0.1:55100 directly instead of http://127.0.0.1:3333/mcp.
---

# Kali Direct API

## Overview

Use this skill when the MCP bridge is unavailable, unwanted, or unnecessary and the local Kali Flask API is reachable on port 55100.

Prefer the bundled client script for repeatable calls:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py health
```

Set `KALI_API_URL` when the API is not at `http://127.0.0.1:55100`.
Run `python3 skills/kali-direct-api/scripts/kali_api.py curl-examples` when raw `curl` commands are preferred.

## Workflow

1. Confirm the user request is for authorized security testing or local lab work.
2. Check server availability with `health`, if not reachable, start the Docker container with `docker start skill-mcp-kali-server` or pull and run it with the provided commands.
3. Use `search-tools` or `manual` before running unfamiliar tools.
4. If a required tool is missing, offer to install its verified package only after receiving explicit user approval and confirming the container permits package installation.
5. Use `run` for one-shot commands that should complete.
6. Use `session-start`, `session-poll`, `session-input`, `session-signal`, and `session-stop` for long-running or interactive tools.
7. Summarize command intent and important output for the user; avoid dumping huge raw output unless requested.

## Optional pentest documentation workspace

Documentation is strictly opt-in. Do not create folders, write notes, save command output, or otherwise persist target information unless the user explicitly asks to document, record, preserve, or report the pentest. Normal Kali API use remains ephemeral apart from behavior already provided by the server.

When the user opts in, read [references/pentest-documentation.md](references/pentest-documentation.md) before testing. Create one dedicated folder per pentest and use the canonical structure in that reference for every engagement. Record the authorized target and scope, planned strategy, activity timeline, evidence, and findings throughout the work rather than reconstructing them at the end.

If the user asks to stop documentation, stop all further workspace writes immediately while leaving existing files intact. Never delete an existing pentest workspace unless the user explicitly requests deletion.

## Tool references

When the correct tool is unclear, open [references/index.md](references/index.md), then read only the relevant category page for selection guidance and important limitations. Do not load every category. After selecting a tool, query its live manual for version-specific syntax. Skip the references when the tool is already known.

## Commands

Health check:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py health
```

List tool categories:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py categories
```

Search for a tool or category:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py search-tools nmap
python3 skills/kali-direct-api/scripts/kali_api.py search-tools web-application
```

Read a tool manual/help summary:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py manual nmap
```

Run a one-shot command:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py run "nmap --version" --timeout 30
```

For authorized John the Ripper hash-auditing workflows and reliable result interpretation, read [references/john.md](references/john.md).

## Installing a missing tool

Do not install a package automatically. When `search-tools` reports that a required tool is missing:

1. Explain why the tool is needed and ask the user for explicit approval to modify the container.
2. Confirm package-management permission and identify the correct package. Do not assume the executable and package names are identical.
3. Accept only a literal Debian package name containing lowercase letters, digits, `+`, `.`, or `-`; never interpolate untrusted text into the shell command.
4. Install only the approved package, then verify the executable with `search-tools` and `manual`.
5. Report that an ad-hoc installation lives in the container's writable layer and may disappear when the container is replaced. For a durable installation, propose adding the package to the Dockerfile and rebuilding the image.

Check identity and available package metadata before requesting or performing installation:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py run "id; command -v apt-get; apt-cache show -- PACKAGE | sed -n '1,20p'" --timeout 30
```

After approval, and only when the API process has sufficient container permissions, install the verified package:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py run "apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends -- PACKAGE" --timeout 900
```

Replace `PACKAGE` with the verified literal package name. Do not add repositories, import signing keys, use installation scripts from the web, or upgrade unrelated packages unless the user separately approves that broader change.

Start and manage an interactive session:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py session-start "python3 -i"
python3 skills/kali-direct-api/scripts/kali_api.py session-poll SESSION_ID
python3 skills/kali-direct-api/scripts/kali_api.py session-input SESSION_ID "print('ok')"
python3 skills/kali-direct-api/scripts/kali_api.py session-signal SESSION_ID SIGINT
python3 skills/kali-direct-api/scripts/kali_api.py session-stop SESSION_ID
```

List sessions:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py session-list
```

Print raw `curl` examples for every API endpoint:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py curl-examples
```
## if the API is not reachable. You can start the Docker container with the following command:

```sh
docker start skill-mcp-kali-server
```

## if the container is not present, you can pull and run it with:

```sh
docker pull ghcr.io/victorh24/skill-mcp-kali-server:latest
```

```sh
docker run -d --restart unless-stopped -p 127.0.0.1:55100:55100 --name skill-mcp-kali-server ghcr.io/victorh24/skill-mcp-kali-server:latest
```

## Curl Commands

Use these commands when Python should not be used:

```sh
KALI_API_URL=http://127.0.0.1:55100

curl -s "$KALI_API_URL/health" | jq .
curl -s "$KALI_API_URL/api/list_categories" | jq .
curl -s "$KALI_API_URL/api/session/list" | jq .
```

```sh
curl -s -X POST "$KALI_API_URL/api/search_tools" \
  -H 'Content-Type: application/json' \
  -d '{"query":"nmap"}' | jq .

curl -s -X POST "$KALI_API_URL/api/read_tool_manual" \
  -H 'Content-Type: application/json' \
  -d '{"tool":"nmap"}' | jq .

curl -s -X POST "$KALI_API_URL/api/run_terminal_command" \
  -H 'Content-Type: application/json' \
  -d '{"command":"nmap --version","timeout":30}' | jq .
```

```sh
curl -s -X POST "$KALI_API_URL/api/session/start" \
  -H 'Content-Type: application/json' \
  -d '{"command":"python3 -i"}' | jq .

curl -s -X POST "$KALI_API_URL/api/session/poll" \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"SESSION_ID","clear":true}' | jq .

curl -s -X POST "$KALI_API_URL/api/session/input" \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"SESSION_ID","input":"print(123)","send_enter":true}' | jq .

curl -s -X POST "$KALI_API_URL/api/session/signal" \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"SESSION_ID","signal":"SIGINT"}' | jq .

curl -s -X POST "$KALI_API_URL/api/session/stop" \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"SESSION_ID"}' | jq .
```

## API Shape

The script wraps these endpoints:

- `GET /health`
- `GET /api/list_categories`
- `POST /api/search_tools` with `{"query": "..."}`
- `POST /api/read_tool_manual` with `{"tool": "..."}`
- `POST /api/run_terminal_command` with `{"command": "...", "timeout": 30}`
- `POST /api/session/start` with `{"command": "..."}`
- `POST /api/session/poll` with `{"session_id": "...", "clear": true}`
- `POST /api/session/input` with `{"session_id": "...", "input": "...", "send_enter": true}`
- `POST /api/session/signal` with `{"session_id": "...", "signal": "SIGINT"}`
- `POST /api/session/stop` with `{"session_id": "..."}`
- `GET /api/session/list`

## Kali tool categories

Retrieve the categories currently exposed by the running server:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py categories
```

Inspect the installed tools in a category:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py search-tools information-gathering
```

When tool selection is unclear, read [references/index.md](references/index.md) and load only the relevant category page. Treat the running server as authoritative because its configured tools may change independently of this skill.

## Safety Notes

Treat `run` and session endpoints like shell access to the Kali environment. Do not run destructive, credential attack, exploit, or scanning commands unless the user has clearly framed the target as authorized. Keep the API bound to localhost unless the user has intentionally configured authentication and network controls.
