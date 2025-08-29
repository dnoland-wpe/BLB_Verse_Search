# BLB Verse Search (Alfred Workflow)

**Keyword:** `blb`  
Open Blue Letter Bible in **Google Chrome** for either:
- **Verse lookups**: `rom 8:28`, `jn 3 16`, `ps 23`, `1 cor 13:4-7`
- **Keyword searches**: `justification by faith`, `Moses tabernacle`

## Features
- Auto-detects verse references vs. keyword searches
- Translation override: `-t NIV`, `(NKJV)`, or `[NASB95]`
- Force keyword search: prefix with `?`, `search:`, or add `-s` anywhere
- Always opens in **Google Chrome** (falls back to default browser if Chrome not found)

## System Requirements
- Macbook laptop or iMac desktop
- Alfred Powerpack license

## Install
1. Download and open the `.alfredworkflow` file below.
2. Alfred will prompt to import the workflow.
3. In Alfred, go to **Workflows** → *BLB Verse Search* and verify the keyword is `blb`.

> No macOS Automation permission is required; the script uses `open -a "Google Chrome" URL`.

## Usage Examples
- `blb rom 8:28` → Romans 8:28 (ESV by default)
- `blb jn 1:1 -t NIV` → John 1:1 (NIV)
- `blb ps 23` → Psalm 23
- `blb justification by faith` → keyword search in BLB
- `blb ? rom 8:28` → **force** keyword search for the words “rom 8:28”
- `blb search: faith hope love` → keyword search
- `blb rom 8 (NKJV)` → chapter lookup in NKJV

## Notes
- Default translation is **ESV**. Override with `-t`, or trailing `(NIV)` / `[NASB95]`, etc.
- Chapter-only references (e.g., `rom 8`) open the chapter at verse 1.
- Ranges like `1 cor 13:4-7` open at the **first** verse in the range (13:4).

## Troubleshooting
- Nothing opens: ensure Google Chrome is installed. The script falls back to your default browser if Chrome isn’t found.
- If your macOS blocks launching apps, try: `System Settings → Privacy & Security → Full Disk Access` (not usually needed).
- On some systems, `python3` may live at a different path. Edit the workflow’s **Run Script** to use `/opt/homebrew/bin/python3` if needed.

## Credits
- Built by David T. Noland..
