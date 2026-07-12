# information-gathering

Read this page to select a tool, not to learn its flags.

- Typical flow: Hosts, networks, domains, names, or URLs → discovered assets, records, ports, services, and technologies.
- Category caution: Start passive and narrow. Active discovery creates traffic; high-rate scanners can disrupt networks or trigger defenses.

## Tool selection

| Tool | Choose it for | Key distinction or limitation |
|---|---|---|
| `nmap` | General host, port, service, OS, and NSE-assisted discovery | Versatile and evidence-rich; slower than dedicated high-rate port scanners |
| `masscan` | Finding open TCP ports across very large address ranges | Optimized for speed, not deep service analysis; set an explicitly safe rate |
| `dmitry` | Quick WHOIS, subdomain, email, and TCP information gathering | An older convenience tool; corroborate results with current sources |
| `dnsenum` | Enumerating DNS records, names, transfers, and brute-force candidates | Can be noisy; zone transfers usually fail on correctly configured servers |
| `dnsrecon` | Structured DNS enumeration across several record and discovery techniques | Choose when you want multiple DNS checks with reportable output |
| `fierce` | Finding non-contiguous IP space and hostnames through DNS | Discovery aid rather than a vulnerability scanner |
| `maltego` | Graphing relationships among people, domains, infrastructure, and data sources | Transform availability and licensing affect results |
| `netdiscover` | Discovering hosts on a local Ethernet segment with ARP | Limited to the local broadcast domain |
| `recon-ng` | Managing repeatable OSINT collection through modules and workspaces | API keys and third-party modules may be required |
| `spiderfoot` | Automated broad OSINT correlation from many data sources | Large result sets contain false relationships; validate key links |
| `theharvester` | Collecting public emails, names, hosts, and URLs from search sources | Source availability and rate limits change frequently |
| `wafw00f` | Fingerprinting a web application firewall | A vendor guess is not proof of a specific policy or bypass |
| `whatweb` | Fingerprinting web servers, frameworks, CMSs, and plugins | Treat signatures as indicators, not confirmed versions or flaws |
| `whois` | Reading domain registration and IP allocation records | Privacy redaction and referral servers can make records incomplete |
| `amass` | Deep subdomain and attack-surface mapping from passive and active sources | Powerful but potentially long-running; configure data sources deliberately |
| `sublist3r` | Fast search-engine-based subdomain enumeration | Older data sources may fail; combine with DNS validation |
| `enum4linux` | Collecting SMB/NetBIOS information from Windows or Samba hosts | Legacy wrapper; enum4linux-ng may provide better structured results |
| `nbtscan` | Finding NetBIOS names and services on IPv4 networks | Useful mainly for legacy/local Windows discovery |
| `onesixtyone` | Fast SNMP community-string discovery | Online guessing can trigger alerts; constrain hosts and community lists |
| `massdns` | Resolving very large lists of DNS names quickly | Input quality and resolver choice strongly affect false positives |
| `smbclient` | Browsing and transferring files through SMB/CIFS | Interactive by default; avoid exposing passwords in command lines |
| `smbmap` | Summarizing SMB share permissions and accessible content | Access checks can touch many shares; use the least-privileged account |
| `snmpwalk` | Walking SNMP object trees to inventory exposed management data | A full walk can be large and sensitive; prefer a narrow OID subtree |
| `snmp-check` | Producing a human-readable summary from SNMP data | Convenient triage, but less precise than targeted snmpwalk queries |
| `arp-scan` | Fast local-LAN host discovery by ARP | Cannot discover hosts beyond the current Layer-2 segment |
| `assetfinder` | Quick passive subdomain collection from public sources | Output is candidates only; resolve and deduplicate before use |
| `autorecon` | Orchestrating many reconnaissance tools against selected hosts | Generates substantial traffic and artifacts; review its scan plan first |
| `naabu` | Fast TCP port discovery with pipeline-friendly output | Follow with a service scanner; a port result alone does not identify a service |
| `certgraph` | Mapping certificate relationships across Internet infrastructure | Shared certificates/CDNs can create misleading ownership links |
| `cloud-enum` | Finding public assets associated with cloud naming patterns | Guesses may identify unrelated tenants; verify ownership carefully |
| `cloudbrute` | Enumerating cloud resources from names and providers | Potentially noisy and prone to naming collisions |
| `eyewitness` | Capturing screenshots and metadata from web services | Rendered pages may execute active content; isolate the browser |
| `findomain` | Fast passive subdomain enumeration with multiple sources | Validate and resolve candidates before treating them as assets |
| `httprobe` | Checking which candidate hosts respond over HTTP or HTTPS | Reachability does not establish ownership or application identity |
| `httpx-toolkit` | Probing many HTTP services and collecting titles, status, and technology hints | Not the same package as Python httpx; confirm the installed executable |
| `ldeep` | Enumerating LDAP directory information | Queries can expose sensitive identity data and require valid directory context |


## After selecting a tool

Query the installed executable because package names, flags, and versions vary:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py search-tools TOOL
python3 skills/kali-direct-api/scripts/kali_api.py manual TOOL
```

Use `run` for bounded commands and the session commands for interactive or long-running tools. Keep the authorized target narrow, preserve evidence and exit status, and validate findings rather than equating successful execution with a confirmed result.
