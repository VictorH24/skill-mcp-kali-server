# forensics

Read this page to select a tool, not to learn its flags.

- Typical flow: Images, memory dumps, files, or devices → recovered artifacts, metadata, timelines, and hashes.
- Category caution: Work on copies, preserve originals, hash inputs and outputs, record tool versions, and maintain chain of custody where relevant.

## Tool selection

| Tool | Choose it for | Key distinction or limitation |
|---|---|---|
| `autopsy` | GUI case management and disk-image forensics using Sleuth Kit | Import copies and understand ingest-module effects and case storage |
| `binwalk` | Locating and extracting embedded data in firmware/binaries | Extraction invokes helpers; handle malicious files in isolation |
| `bulk-extractor` | Scanning images/files for emails, URLs, cards, and other features | Produces large amounts of sensitive data and false positives |
| `foremost` | Carving files from raw data using header/footer signatures | Recovered files lose original paths and may be fragmented |
| `galleta` | Parsing legacy Internet Explorer cookie files | Niche/legacy format; preserve timestamps and source context |
| `hashdeep` | Computing, matching, and auditing recursive file hashes | Choose algorithms and comparison mode deliberately; hashes prove identity, not safety |
| `steghide` | Embedding or extracting data in supported media containers | Extraction requires the correct passphrase and supported format |
| `volatility` | Analyzing supported memory images through plugins | Profile/symbol/version must match the captured operating system |
| `sleuthkit` | Command-line filesystem and disk-image forensic utilities | A suite of low-level tools; preserve sector offsets and timezone context |
| `dc3dd` | Forensic disk acquisition with hashing and progress features | Double-check input/output devices; a reversed copy direction is destructive |
| `extundelete` | Recovering deleted files from unmounted ext3/ext4 filesystems | Continued writes reduce recovery chances; operate on an image |
| `scalpel` | Configurable high-performance file carving | Header rules and fragmentation strongly affect results |
| `pdf-parser` | Inspecting PDF objects, streams, names, and suspicious structure | Static indicators do not prove malicious execution |
| `exiftool` | Reading or carefully modifying file metadata | Writes can alter evidence; use read-only operation on forensic originals |


## After selecting a tool

Query the installed executable because package names, flags, and versions vary:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py search-tools TOOL
python3 skills/kali-direct-api/scripts/kali_api.py manual TOOL
```

Use `run` for bounded commands and the session commands for interactive or long-running tools. Keep the authorized target narrow, preserve evidence and exit status, and validate findings rather than equating successful execution with a confirmed result.
