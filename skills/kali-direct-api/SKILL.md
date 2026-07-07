---
name: kali-direct-api
description: Direct HTTP access to the local Kali Linux API server on port 5000 without using the MCP bridge. Use when Codex needs to search Kali tools, read tool help, run authorized terminal commands, or manage interactive Kali sessions by calling http://127.0.0.1:5000 directly instead of http://127.0.0.1:3333/mcp.
---

# Kali Direct API

## Overview

Use this skill when the MCP bridge is unavailable, unwanted, or unnecessary and the local Kali Flask API is reachable on port 5000.

Prefer the bundled client script for repeatable calls:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py health
```

Set `KALI_API_URL` when the API is not at `http://127.0.0.1:5000`.
Run `python3 skills/kali-direct-api/scripts/kali_api.py curl-examples` when raw `curl` commands are preferred.

## Workflow

1. Confirm the user request is for authorized security testing or local lab work.
2. Check server availability with `health`.
3. Use `search-tools` or `manual` before running unfamiliar tools.
4. Use `run` for one-shot commands that should complete.
5. Use `session-start`, `session-poll`, `session-input`, `session-signal`, and `session-stop` for long-running or interactive tools.
6. Summarize command intent and important output for the user; avoid dumping huge raw output unless requested.

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
here and exemple of john the ripper command:

```sh
python3 "skills/kali-direct-api/scripts/kali_api.py" run "printf '%s\n' 'HASH_HERE' > /tmp/hash.txt; rm -f /tmp/john.pot; john --format=Raw-SHA256 --wordlist=/usr/share/wordlists/rockyou.txt --pot=/tmp/john.pot /tmp/hash.txt; john --format=Raw-SHA256 --pot=/tmp/john.pot --show /tmp/hash.txt" --timeout 300
```
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
docker run -d --restart unless-stopped -p 127.0.0.1:5000:5000 --name skill-mcp-kali-server ghcr.io/victorh24/skill-mcp-kali-server:latest
```

## John the Ripper Result Interpretation

When using `john`, do **not** infer cracked passwords from progress/status lines in `stderr`.

John may print candidate words being tested, for example:

```text
0g 0:00:00:00 DONE ... """anokax"..
```
This does not mean anokax was cracked. It is only a candidate/progress display.

Always determine success only from john --show output.


## Curl Commands

Use these commands when Python should not be used:

```sh
KALI_API_URL=http://127.0.0.1:5000

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

## Kali Categories

Use these known `KALI_CATEGORIES` keys with `search-tools` or `/api/search_tools`:

```python
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
```

## Safety Notes

Treat `run` and session endpoints like shell access to the Kali environment. Do not run destructive, credential attack, exploit, or scanning commands unless the user has clearly framed the target as authorized. Keep the API bound to localhost unless the user has intentionally configured authentication and network controls.
