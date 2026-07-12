# web-application

Read this page to select a tool, not to learn its flags.

- Typical flow: Authorized URLs, requests, or captured traffic → routes, parameters, technologies, and test findings.
- Category caution: Use test accounts and conservative concurrency. Content discovery and payload testing can change state or overload an application.

## Tool selection

| Tool | Choose it for | Key distinction or limitation |
|---|---|---|
| `burpsuite` | Intercepting, replaying, and manually testing HTTP/WebSocket traffic | Interactive proxy; scope it before browsing to prevent unintended capture |
| `dirb` | Simple wordlist-based web content discovery | Older and less flexible; every request reaches the target |
| `dirbuster` | GUI-based threaded directory and file discovery | Can create high request volume; tune threads and extensions |
| `gobuster` | Fast discovery of web paths, DNS names, or virtual hosts | Choose the correct mode; high concurrency can overload targets |
| `feroxbuster` | Recursive, fast web content discovery | Recursion expands traffic quickly; constrain depth, rate, and status handling |
| `ffuf` | Highly flexible HTTP fuzzing for paths, parameters, headers, and hosts | Calibrate filters to avoid drowning in uniform or wildcard responses |
| `nikto` | Checking web servers for known risky files and configurations | Noisy signature scanner; manually validate every reported issue |
| `sqlmap` | Automating detection and controlled validation of SQL injection | Can modify data or stress databases; begin with low risk/level settings |
| `wpscan` | Enumerating and assessing WordPress core, plugins, themes, and users | Vulnerability data may require an API token; enumeration can be noisy |
| `wfuzz` | Payload-driven web fuzzing with response filtering | Powerful but syntax-heavy; establish a baseline response first |
| `whatweb` | Fingerprinting web servers, frameworks, CMSs, and plugins | Treat signatures as indicators, not confirmed versions or flaws |
| `zaproxy` | Intercepting proxy plus automated web crawling and scanning | Active scan changes traffic substantially; define context and exclusions |
| `httpx` | Python HTTP client/library or CLI depending on installation | Resolve this name ambiguity with search-tools and manual before use |
| `hakrawler` | Extracting links and endpoints by crawling web pages | JavaScript-heavy applications may require a browser-based crawler |
| `arjun` | Discovering hidden HTTP parameters | Many requests and heuristic results; retest promising parameters manually |
| `commix` | Testing and exploiting command-injection conditions | Potentially executes commands; use only for explicit controlled validation |
| `xsser` | Testing reflected and other cross-site-scripting candidates | Browser context determines exploitability; validate safely in the real sink |
| `dalfox` | Fast XSS parameter analysis and payload verification | Automation can miss DOM context or create noisy payload traffic |


## After selecting a tool

Query the installed executable because package names, flags, and versions vary:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py search-tools TOOL
python3 skills/kali-direct-api/scripts/kali_api.py manual TOOL
```

Use `run` for bounded commands and the session commands for interactive or long-running tools. Keep the authorized target narrow, preserve evidence and exit status, and validate findings rather than equating successful execution with a confirmed result.
