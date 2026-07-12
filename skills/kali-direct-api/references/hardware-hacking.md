# hardware-hacking

Read this page to select a tool, not to learn its flags.

- Typical flow: Authorized devices, buses, firmware, or debug interfaces → device information, dumps, traces, or programmed state.
- Category caution: Wrong voltage, target, layout, or write command can permanently damage or brick hardware; identify and back up before writing.

## Tool selection

| Tool | Choose it for | Key distinction or limitation |
|---|---|---|
| `arduino` | Building and uploading sketches to supported microcontrollers | Board, port, voltage, and bootloader must be identified first |
| `dfu-util` | Reading/writing firmware through USB Device Firmware Upgrade mode | Wrong target/alternate setting or write can brick a device |
| `flashrom` | Identifying, reading, verifying, and writing flash chips | Always make and verify multiple backups before any write |
| `openocd` | Driving JTAG/SWD debug adapters for embedded targets | Requires correct adapter, target config, pinout, and voltage |


## After selecting a tool

Query the installed executable because package names, flags, and versions vary:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py search-tools TOOL
python3 skills/kali-direct-api/scripts/kali_api.py manual TOOL
```

Use `run` for bounded commands and the session commands for interactive or long-running tools. Keep the authorized target narrow, preserve evidence and exit status, and validate findings rather than equating successful execution with a confirmed result.
