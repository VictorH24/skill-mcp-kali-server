# reporting

Read this page to select a tool, not to learn its flags.

- Typical flow: Assessment evidence and metadata → screenshots, correlated findings, metrics, or report artifacts.
- Category caution: Remove secrets and unnecessary personal data; preserve provenance and distinguish observed facts from interpretation.

## Tool selection

| Tool | Choose it for | Key distinction or limitation |
|---|---|---|
| `cutycapt` | Capturing web pages as images using an older headless WebKit stack | Rendering may differ from modern browsers and execute page content |
| `faraday` | Collaborative vulnerability-management and finding correlation | Import quality and deduplication rules affect reporting accuracy |
| `maltego` | Graphing relationships among people, domains, infrastructure, and data sources | Transform availability and licensing affect results |
| `metagoofil` | Extracting metadata from publicly available documents | Search-source changes limit coverage; metadata may contain personal data |
| `pipal` | Analyzing password-list statistics and patterns | Use only sanitized authorized datasets; results can expose user behavior |
| `recordmydesktop` | Recording a Linux desktop assessment session | May capture secrets, notifications, or unrelated user activity |


## After selecting a tool

Query the installed executable because package names, flags, and versions vary:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py search-tools TOOL
python3 skills/kali-direct-api/scripts/kali_api.py manual TOOL
```

Use `run` for bounded commands and the session commands for interactive or long-running tools. Keep the authorized target narrow, preserve evidence and exit status, and validate findings rather than equating successful execution with a confirmed result.
