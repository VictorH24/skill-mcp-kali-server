# wireless-attacks

Read this page to select a tool, not to learn its flags.

- Typical flow: Authorized interfaces, captures, access points, or clients → wireless inventory, handshakes, and control-test results.
- Category caution: Monitor mode, injection, deauthentication, and rogue AP tests can disconnect users and may require compatible hardware.

## Tool selection

| Tool | Choose it for | Key distinction or limitation |
|---|---|---|
| `aircrack-ng` | Recovering WEP keys or auditing WPA handshakes offline | Needs valid captures; success depends on protocol and password strength |
| `airmon-ng` | Preparing wireless interfaces for monitor mode | Changes interface state and may disconnect normal networking |
| `airodump-ng` | Capturing 802.11 frames and surveying APs/clients | Channel hopping can miss traffic; captures contain sensitive data |
| `aireplay-ng` | Injecting or replaying 802.11 frames for controlled tests | Active injection/deauthentication disrupts nearby clients |
| `cowpatty` | Offline WPA-PSK auditing from captured handshakes | Older workflow; correct SSID and valid handshake are required |
| `fern-wifi-cracker` | GUI wrapper for wireless auditing workflows | Automation hides disruptive steps; inspect actions before running |
| `kismet` | Passive wireless discovery, capture, and device correlation | Long-running and data-rich; protect location and device identifiers |
| `pixiewps` | Offline analysis of vulnerable WPS implementations | Only applies to specific weak WPS nonce behavior |
| `reaver` | Online WPS PIN auditing | Slow and disruptive; AP lockout protections are common |
| `wifite` | Automating several wireless audit tools | Convenient but potentially disruptive; review selected attacks first |
| `bully` | WPS PIN auditing alternative to Reaver | Still subject to lockouts, rate constraints, and WPS applicability |
| `hostapd-wpe` | Running a controlled enterprise-Wi-Fi credential-capture test AP | High-risk rogue AP behavior; requires explicit scenario authorization |


## After selecting a tool

Query the installed executable because package names, flags, and versions vary:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py search-tools TOOL
python3 skills/kali-direct-api/scripts/kali_api.py manual TOOL
```

Use `run` for bounded commands and the session commands for interactive or long-running tools. Keep the authorized target narrow, preserve evidence and exit status, and validate findings rather than equating successful execution with a confirmed result.
