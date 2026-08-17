# SnapRes → Desktop App: Complete Guide (v2)

This replaces the old GUIDE.md. Your `SnapRes.py` has now been wired in for
real — this is **not demo mode anymore**. Clicking a resolution tile actually
calls `ChangeDisplaySettingsW`, just like the Python version did. Every file
below is already written; you're copying/downloading them into place and
running two commands.

Follow this top to bottom. Every step has a **checkpoint**.

---

## What you need before starting

- **Node.js** (LTS) — download from nodejs.org, run the installer, accept defaults.
- A code editor (VS Code recommended).
- **Windows.** SnapRes is a Windows-only tool (same as the Python build) — the
  resolution-switching script uses Win32 APIs that don't exist elsewhere.

**Checkpoint:** Open Command Prompt and run `node -v` then `npm -v`. Both
print a version number.

---

## Step 1 — Project folder

Make a folder somewhere simple, e.g. `C:\Dev\SnapRes` (avoid spaces in the
path). Lay the files out exactly like this:

```
SnapRes/
├── package.json
├── main.js
├── preload.js
├── native/
│   └── apply-resolution.ps1
├── app/
│   ├── index.html
│   └── assets/
│       ├── fonts/
│       │   ├── Nunito-Light.ttf
│       │   └── Nunito-Black.ttf
│       ├── icons/
│       │   ├── discord.png
│       │   ├── github.png
│       │   └── youtube.png
│       └── logo/
│           ├── Logo_Main.png
│           └── Logo_Dark.png
└── build/
    └── icon.ico
```

Every one of these files is included in the project you were given — copy
them in as-is, nothing to retype by hand this time.

**Checkpoint:** your folder matches the tree above exactly, including
nesting. `native/apply-resolution.ps1` is new — don't skip it, it's the file
that actually talks to Windows.

---

## Step 2 — Install dependencies

In a terminal, inside the `SnapRes` folder:

```
npm install --save-dev electron electron-builder
```

**Checkpoint:** a `node_modules` folder now exists, and the terminal ends
without red "npm error" text (yellow "npm warn" lines are normal).

---

## Step 3 — Run it

```
npm start
```

First run downloads Electron's ~120MB engine binary once — let it finish.

**Checkpoint:** a window opens titled SnapRes — logo, fonts, the
cursor-reactive gradient background, the resolution grid. Click a resolution
tile:

- If that resolution is already registered as a **custom resolution** in
  your GPU control panel (see Step 6 in the in-app **Setup** guide), your
  actual screen resolution changes and the tile lights up green.
  Press **Ctrl+Shift+Alt+B**, `Win+P`, or wait — Windows reverts unrecognized
  resolutions automatically if nothing confirms them, same as it always did.
- If it's not registered yet, you'll see the same red error message the
  Python version gave: *"Try running as Administrator, or that resolution
  isn't registered with your GPU driver yet."*

Either way — something should visibly happen. If clicking does nothing at
all (no toast, no colored status pill), open DevTools with **Ctrl+Shift+I**
and check the Console tab for red text; see Troubleshooting below.

---

## Step 4 — Build the installer

```
npm run dist
```

Produces `dist/SnapRes Setup 1.0.6.exe`. Fonts, icons, and the PowerShell
helper are all bundled inside — nothing else needs to be pre-installed on
the machine it's run on.

**Checkpoint:** run the installer yourself. It installs, adds a Start Menu
shortcut, and launches showing the same UI as Step 3.

---

## What's actually wired up (and what isn't)

| Feature | Status |
|---|---|
| True Stretch / Revert / Custom resolution buttons | **Real.** Calls `native/apply-resolution.ps1`, a direct translation of the `DEVMODE` struct + `ChangeDisplaySettingsW` call from `SnapRes.py`. Same success/error messages. |
| Saved profiles | **Real.** Reads/writes `%APPDATA%\SnapRes\profiles.json` — the exact file the Python build used, so old profiles carry over. |
| Theme toggle, ambient mouse-glow background, animations | **Real** — this was already finished UI work, untouched here. |
| Credits links (YouTube/Discord/GitHub) + email chip | **Fixed.** These previously only showed a toast claiming to open a link, without opening anything. They now actually call `shell.openExternal`. |
| Success/failure messages on resolution switch | **Fixed.** The demo-mode script always displayed "Switched to WxH" regardless of what happened. It now reflects the real result — a failed switch shows the red error state and does *not* light the tile up green. |
| Monitor-driver status card (the "disable generic monitor driver" panel) | **Stub, by design — see below.** |

### About the driver-status card

The UI has a card that offers to detect and disable a "generic monitor
driver." That feature was never implemented in `SnapRes.py` — there's no
hardware ID, no `devcon`/`pnputil` call, nothing to translate. It's UI
groundwork from an earlier design pass that got ahead of the actual Python
logic.

Rather than fake a working toggle (which would show a UAC prompt that does
nothing, or silently lie about your driver state), it's wired to always
report **"not_found"** — the same state the UI already displays as *"Your
setup may not need this step — safe to ignore."* That's an honest,
non-broken result. If you want this feature for real, tell me the exact
device (from Device Manager) it should target and I'll wire in an actual
`pnputil`/`devcon` call with proper elevation — I can't guess a hardware ID
that's specific to your PC.

---

## Troubleshooting

**`npm error code EJSONPARSE`**
An empty/corrupt `package.json`. Delete it and re-copy the one provided.

**`npm start` shows "Downloading electron..." and sits there**
Normal on first run (one-time ~120MB download). If it never finishes after
several minutes, it's a network/firewall issue — re-run `npm start` to
resume.

**Clicking a resolution tile shows the red error every time, even for
resolutions you know work**
Almost always means that exact resolution isn't registered as a custom
resolution in your NVIDIA/AMD/Intel control panel yet — see the in-app
Setup guide, step 2. This matches the Python version's behavior exactly:
Windows has to know about a resolution before `ChangeDisplaySettingsW` can
switch to it.

**Nothing happens at all when you click (no toast, no color change)**
Open DevTools (**Ctrl+Shift+I**) → Console tab, click the button again, and
read the red error. Common causes: a typo if you retyped any file by hand
instead of copying it, or `native/apply-resolution.ps1` missing from the
`native/` folder.

**PowerShell-related error in the console (`ExecutionPolicy`, `is not
recognized`, etc.)**
Some locked-down corporate/school machines block `powershell.exe` entirely
via Group Policy. There's no way around that from inside the app — it needs
that same access the original Python `.exe` needed to call the Win32 API.

**Saved profiles from the old Python app aren't showing up**
They only carry over if both versions used the *same* Windows user account
(profiles live at `%APPDATA%\SnapRes\profiles.json`, which is per-user).
