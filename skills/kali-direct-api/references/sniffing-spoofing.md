# sniffing-spoofing

Read this page to select a tool, not to learn its flags.

- Typical flow: Authorized interfaces or traffic paths → packet captures, decoded flows, or controlled interception evidence.
- Category caution: Captures can contain secrets and personal data. Active spoofing changes network behavior; encrypt, minimize, and delete evidence appropriately.

## Tool selection

| Tool | Choose it for | Key distinction or limitation |
|---|---|---|
| `wireshark` | Deep interactive packet and protocol analysis | GUI-oriented; display filters differ from capture filters |
| `tshark` | Scriptable Wireshark decoding and field extraction | Excellent for reproducible analysis; quote complex filters carefully |
| `tcpdump` | Lightweight packet capture and quick filtering | Capture filters use BPF syntax and may silently exclude needed traffic |
| `ettercap` | LAN interception and active man-in-the-middle testing | ARP poisoning changes traffic paths and can break connectivity |
| `bettercap` | Extensible network/BLE/Wi-Fi reconnaissance and active MITM framework | Caplets can perform multiple active actions; inspect them first |
| `arpspoof` | Redirecting local IPv4 traffic with forged ARP replies | Requires forwarding/cleanup and affects a Layer-2 segment |
| `dnsspoof` | Returning forged DNS answers during a controlled interception test | Only sees applicable traffic and can redirect real users |
| `macchanger` | Changing a network interface MAC address | Resets may drop connectivity; does not provide anonymity by itself |
| `mitmproxy` | Interactive/scriptable HTTP(S) interception proxy | TLS interception requires trusted test certificates and captures secrets |
| `responder` | Poisoning local name-resolution protocols to capture authentication attempts | High-impact credential-capture behavior; use only in an explicit scenario |
| `sslstrip` | Demonstrating legacy HTTPS-to-HTTP downgrade exposure | Modern HSTS limits applicability; active MITM is required |
| `netsniff-ng` | High-performance Linux packet capture, replay, and traffic tooling | Low-level suite; choose the correct subtool and interface |
| `tcpflow` | Reassembling TCP streams into per-flow files | Useful for content review; encrypted sessions remain opaque |


## After selecting a tool

Query the installed executable because package names, flags, and versions vary:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py search-tools TOOL
python3 skills/kali-direct-api/scripts/kali_api.py manual TOOL
```

Use `run` for bounded commands and the session commands for interactive or long-running tools. Keep the authorized target narrow, preserve evidence and exit status, and validate findings rather than equating successful execution with a confirmed result.
