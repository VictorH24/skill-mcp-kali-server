# reverse-engineering

Read this page to select a tool, not to learn its flags.

- Typical flow: Binaries, bytecode, packages, or processes → disassembly, decompilation, symbols, strings, and behavior evidence.
- Category caution: Analyze untrusted samples in isolation. Static decompilation is approximate; confirm important conclusions dynamically when safe.

## Tool selection

| Tool | Choose it for | Key distinction or limitation |
|---|---|---|
| `ghidra` | Static disassembly, decompilation, symbols, and scripting across architectures | Decompiler output is an approximation; project imports may analyze automatically |
| `radare2` | Scriptable command-line binary inspection and reverse engineering | Powerful but steep syntax; save reproducible commands |
| `gdb` | Dynamic debugging of native programs and process state | Running a sample executes code; isolate it and account for anti-debugging |
| `edb-debugger` | Graphical Linux debugger inspired by OllyDbg | Best for interactive native debugging; architecture support varies |
| `ollydbg` | Legacy Windows user-mode debugger | Primarily suited to 32-bit Windows software |
| `apktool` | Decoding and rebuilding Android resources and smali | Rebuilt APKs require signing and may not reproduce the original exactly |
| `dex2jar` | Converting Android DEX bytecode to Java class/JAR form | Conversion can fail on obfuscation or newer bytecode features |
| `jd-gui` | Browsing decompiled Java class files graphically | Decompiled source loses comments and may misrepresent control flow |
| `jadx` | Decompiling Android APK/DEX to readable Java and resources | Use smali or disassembly when decompilation is incomplete |
| `rizin` | Fork-derived command-line reverse-engineering framework | Syntax/ecosystem differ from radare2 despite shared history |
| `cutter` | Graphical reverse-engineering frontend for Rizin | GUI analysis settings and backend version influence results |
| `objdump` | Inspecting object headers, sections, symbols, and disassembly | Architecture and disassembly syntax must match the file |
| `strings` | Quickly extracting printable sequences from binaries | Encoding and minimum length affect results; strings lack execution context |


## After selecting a tool

Query the installed executable because package names, flags, and versions vary:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py search-tools TOOL
python3 skills/kali-direct-api/scripts/kali_api.py manual TOOL
```

Use `run` for bounded commands and the session commands for interactive or long-running tools. Keep the authorized target narrow, preserve evidence and exit status, and validate findings rather than equating successful execution with a confirmed result.
