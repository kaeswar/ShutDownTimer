# Shutdown Timer

<img src="app_icon.png" width="96" align="right">

A small Windows app that shuts your PC down after a countdown.

> **Windows only.** It relies on the Windows `shutdown` command, so it will not work on macOS or Linux.

## Features

- One-click presets: 30m, 1h, 1.5h, 2h
- Custom timer from 1 to 1440 minutes
- Live countdown ring showing the exact shutdown time
- Instant cancel, no confirmation
- The timer is saved to `%APPDATA%\ShutdownTimer\timer.json`, so Cancel still works after you close and reopen the app
- About window with app details and a UPI donate/copy button

## Run

Requires Windows and Python 3 (Tkinter is included with the standard installer).

```
pythonw "python-shutdown-timer .pyw"
```

Or double-click `python-shutdown-timer .pyw`. Keep `app_icon.png` next to it.

## Files

| File | What it is |
| --- | --- |
| `python-shutdown-timer .pyw` | The real app (Tkinter) |
| `shutdown-timer.bat` | Simple console menu version |
| `shutdown-timer-app.tsx` | React visual mock of the UI. It does not shut anything down |
| `app_icon.png`, `app_icon.ico` | App icon |

## Credits

Thought provider: **Kaeswar** — kaeswar@gmail.com

If interested, donate via UPI: `kaeswar@oksbi`
