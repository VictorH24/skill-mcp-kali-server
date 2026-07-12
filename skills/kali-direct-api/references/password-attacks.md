# password-attacks

Read this page to select a tool, not to learn its flags.

- Typical flow: Authorized hashes, wordlists, or authentication endpoints → audit results or recovered test credentials.
- Category caution: Prefer offline auditing. Online attempts can lock accounts, create alerts, and violate policy; never treat a candidate/status line as a crack.

## Tool selection

| Tool | Choose it for | Key distinction or limitation |
|---|---|---|
| `hydra` | Parallel online login auditing across many protocols | Account lockout and service impact are primary risks |
| `john` | Flexible CPU-based hash auditing and format detection | Use --show for confirmed results; candidate/progress text is not a crack |
| `hashcat` | High-performance GPU/CPU hash auditing with attack modes and rules | Correct hash mode is essential; monitor temperature and workload |
| `medusa` | Parallel modular online authentication testing | Similar to Hydra; choose based on protocol-module support |
| `ncrack` | Nmap-family network authentication auditing | Useful with Nmap workflows; enforce rate and lockout constraints |
| `ophcrack` | Recovering Windows passwords from LM/NTLM rainbow tables | Requires appropriate tables; modern strong passwords resist this approach |
| `wordlists` | Providing candidate dictionaries for auditing and discovery | Treat lists as sensitive data and match them to the language/context |
| `crunch` | Generating candidate wordlists from explicit patterns and character sets | Combinatorial output grows extremely quickly; estimate size first |
| `cewl` | Building target-context wordlists from website content | Crawling is active and collected words may contain personal data |
| `cupp` | Generating profile-based password candidates | Profile inputs are sensitive and should only concern authorized test identities |
| `hash-identifier` | Interactively guessing likely hash families from appearance | Many formats are indistinguishable; verify using source context |
| `hashid` | Classifying hash strings and suggesting Hashcat/John modes | Suggestions are candidates, not definitive identification |
| `patator` | Flexible multi-protocol online authentication and fuzzing framework | Highly configurable and easy to over-parallelize |
| `thc-pptp-bruter` | Auditing legacy PPTP/MS-CHAP authentication | Relevant to obsolete protocols; can disrupt fragile VPN services |

## Detailed workflows

- [John the Ripper](john.md) — hash formats, wordlist auditing, pot files, cleanup, and reliable result interpretation.

## After selecting a tool

Query the installed executable because package names, flags, and versions vary:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py search-tools TOOL
python3 skills/kali-direct-api/scripts/kali_api.py manual TOOL
```

Use `run` for bounded commands and the session commands for interactive or long-running tools. Keep the authorized target narrow, preserve evidence and exit status, and validate findings rather than equating successful execution with a confirmed result.
