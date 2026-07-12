# John the Ripper

Use John the Ripper to audit authorized password hashes offline. Read this page for workflow and interpretation; query the live manual for the installed version's exact syntax.

## Before running

1. Confirm that the hash and wordlist are authorized for testing.
2. Identify the hash from its source format, not appearance alone. `hashid` and `hash-identifier` provide candidates, but many encodings are ambiguous.
3. Prefer the format emitted by the source application. `Raw-MD5` and `Raw-SHA256` apply only to unsalted raw digests, not to most application password formats.
4. Check that the intended wordlist exists. Kali may ship RockYou compressed as `/usr/share/wordlists/rockyou.txt.gz` rather than extracted.
5. Use a dedicated pot file so earlier results cannot be mistaken for results from the current audit.

Discover formats and confirm the wordlist:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py run "john --list=formats | head -50; test -f /usr/share/wordlists/rockyou.txt && echo rockyou-ready || echo rockyou-missing" --timeout 30
```

## Audit one raw SHA-256 hash

Replace `HASH_HERE` with an authorized raw SHA-256 digest:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py run "printf '%s\n' 'HASH_HERE' > /tmp/john-sha256.txt; rm -f /tmp/john-sha256.pot; john --format=Raw-SHA256 --wordlist=/usr/share/wordlists/rockyou.txt --pot=/tmp/john-sha256.pot /tmp/john-sha256.txt; john --format=Raw-SHA256 --pot=/tmp/john-sha256.pot --show /tmp/john-sha256.txt" --timeout 300
```

## Audit one raw MD5 hash

Replace `HASH_HERE` with an authorized raw MD5 digest:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py run "printf '%s\n' 'HASH_HERE' > /tmp/john-md5.txt; rm -f /tmp/john-md5.pot; john --format=Raw-MD5 --wordlist=/usr/share/wordlists/rockyou.txt --pot=/tmp/john-md5.pot /tmp/john-md5.txt; john --format=Raw-MD5 --pot=/tmp/john-md5.pot --show /tmp/john-md5.txt" --timeout 300
```

For multiple hashes, place one correctly formatted record per line. Do not combine unrelated formats in one input file unless the installed John format explicitly supports it.

## Interpret results

Use `john --show` output as the confirmation source. Do not infer a recovered password from status or candidate text in stderr. A line resembling this can show a candidate being tested rather than a successful recovery:

```text
0g 0:00:00:00 DONE ... candidate..
```

Interpret `0 password hashes cracked` as no confirmed recovery for the selected format and pot file. If the API times out, treat output as partial and run `--show` against the same pot and input files before drawing a conclusion.

## Clean up

After preserving only the authorized result evidence the user needs, remove the temporary inputs and pot files:

```sh
python3 skills/kali-direct-api/scripts/kali_api.py run "rm -f /tmp/john-sha256.txt /tmp/john-sha256.pot /tmp/john-md5.txt /tmp/john-md5.pot" --timeout 30
```

Do not expose recovered passwords in logs or summaries unless the user explicitly needs the value. Prefer reporting counts and remediation guidance.
