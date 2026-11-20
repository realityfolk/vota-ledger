# Afferent desktop

A small desktop app that opens your Afferent server in its own window, the way the Claude desktop app opens claude.ai.
It holds no Python, no database and no patient data. Every screen comes from the server, so new features show up
without reinstalling the app, and the browser keeps working exactly as before.

## Run it on the Mac (or any computer with Node 20 or newer)

```
cd desktop
npm install
npm start
```

`npm install` is only needed once; it downloads Electron (about 100 MB).

It opens `http://100.108.189.122:8080` (the Mac Mini over Tailscale). Sign in as you would in the browser.

## Icon

The app icon is the Afferent mark (the same one as the browser tab), redrawn at 1024 px for the Dock: `build/icon.png`,
made from `build/icon.svg`. Builds pick it up on their own; `npm start` sets it in the Dock too.

## Dock badge

The Afferent icon in the Dock shows the total number of referrals on the queues pinned to your bar (the same numbers
the bar shows). It refreshes every minute while the app is open, and clears when you sign out, when the server can't
be reached and when you quit. No pinned queues, no badge. The browser is unchanged.

## Point it at another server

First found wins:

1. The `AFFERENT_SERVER_URL` environment variable, e.g. `AFFERENT_SERVER_URL=http://localhost:8080 npm start`.
2. Your own `config.json` in the app's settings folder. **Afferent > Server settings…** (File menu on Windows) creates it and shows it.
   On a Mac it is `~/Library/Application Support/Afferent/config.json`.
3. The `config.json` shipped next to this README.

Only `http` and `https` addresses are accepted, and never one with a user name or password in it.

## Build an installer

```
npm run dist:mac
```

That makes a .zip and a .dmg in `desktop/dist` (see "Copy it to another Mac"). `npm run dist:win` makes a Windows installer (build it on Windows).

These are **not signed**. macOS will say the app is from an unidentified developer: right-click it, choose Open, then Open again.
Fine for your own computers; signing and notarising are needed before anyone else installs it.

## Desktop alerts

When an urgent referral (Urgent, ASAP or STAT) arrives at one of the queues pinned to your bar, the Mac shows an alert
such as "2 new urgent referrals in Central Intake". Clicking it opens that queue. It checks once a minute.

- "Arrives" means new referrals and ones routed or moved in from another queue. Moving between states inside a queue doesn't count.
- Routine referrals don't alert; they show on the badge.
- Alerts only show when Afferent isn't the window in front. If you're looking at it, the badge and bar are enough.
- Alerts say the queue and a count, never anything about a patient, because they can show on a locked or shared screen.
- Nothing from before the app opened (or before you signed in) ever alerts.
- To turn them off, or change how they look, use System Settings > Notifications > Afferent (or Electron, when run with `npm start`).
  The first time, macOS may ask whether to allow them.

## Copy it to another Mac

On this Mac, in `desktop`:

```
npm run dist:mac
```

That makes `Afferent-0.1.0-arm64-mac.zip` (and a .dmg) in `desktop/dist`, for Apple Silicon Macs (M1 and newer).
Copy either one to the other Mac (AirDrop, a USB stick or a shared folder), unzip it, and drag `Afferent.app` into Applications.

The app is not signed by a registered Apple developer, so the first time macOS will refuse to open it:

1. Try to open it once, and close the warning.
2. Open System Settings > Privacy & Security, scroll down to the line about Afferent, and click Open Anyway.

If macOS instead says the app "is damaged", that's the download quarantine. In Terminal on that Mac:

```
xattr -dr com.apple.quarantine /Applications/Afferent.app
```

The other Mac needs Tailscale on (it opens the same address, `http://100.108.189.122:8080`), and you sign in there as usual.
Nothing else needs installing: no Node, no npm.

## What it does to keep things safe

- Pages get no Node: context isolation and the sandbox are on, and the only thing exposed is `window.afferentDesktop` (`isDesktop`, `retry`, `setBadge`, `alertSince`, `arrivals`). The badge and alert numbers are accepted only from a top-level page of the server, and checked field by field.
- Only the server's own pages open in the window. Any other web or mail link opens in your normal browser; anything else is refused.
- Camera, microphone, location, notifications and other device features are refused.
- Certificate errors are not overridden.
- The page cache is cleared when you reach the sign-in page and when the app quits. The sign-in cookie is kept, as in a browser.
- If the server can't be reached, a "Can't reach the server" page tries again every 20 seconds, or when you click Try again.
- Developer tools are only available when running from source (`npm start`), not in a built app.

## Not built yet

Signing with a registered Apple developer certificate and notarising, automatic updates, a tray icon, and a
"choose your server" first-run screen. Say the word if you want any of them.

## Tests

`npm test` runs the rules tests with plain Node (no Electron needed). The Python suite runs them too (`tests/test_desktop_shell.py`).
