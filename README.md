<div align="center">

# Auto Backup & Delete

**Automatically back up your folders. Delete old archives effortlessly.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter%20%2B%20Forest--ttk-2E7D32?style=flat-square)](https://docs.python.org/3/library/tkinter.html)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-blue?style=flat-square)](https://github.com/valuthringer)
[![Version](https://img.shields.io/badge/Version-3.1-orange?style=flat-square)](https://valuthringer.github.io)
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)](LICENSE)

*Python desktop application with a graphical interface — Forest Dark theme*

</div>

---

## Overview

**Auto Backup & Delete** is a tool for automatic file backup and cleanup. It compresses your important folders into timestamped `.zip` archives, sends them to one or more destination folders, and automatically deletes archives that are too old — all through a minimalist graphical interface.

---

## Features

### Backup
- **Manual backup** — trigger an immediate backup with a single click
- **Scheduled automatic backup** — set a frequency (every N days) and a precise time
- **Multi-source** — add multiple source folders into a single archive
- **Multi-destination** — back up simultaneously to multiple locations (local drive, NAS, USB...)
- **Naming format**: `Backup_DD-MM-YYYY_N.zip` with automatic incrementing
- **Real-time progress bar**

### Automatic Deletion
- **Scheduled deletion** of `.zip` files older than N days, every day at the configured time
- **Manual deletion** on demand
- **Force Purge** — wipe all monitored folders entirely (double confirmation required)
- **Real-time simulation**: size to delete, number of eligible files, estimated size after cleanup

### Disk Information (real-time)
- Total size of source folders
- Available space at the destination
- Estimated remaining space after backup (with warning if insufficient)
- Next scheduled backup time

### Configuration Profiles
- Save and reload complete configurations (sources, destinations, schedule, deletion settings)
- **Auto-save** of the active profile every 5 minutes
- Profiles stored in `%APPDATA%\Auto-Backup-and-Delete\profiles.json`

---

## Interface

![Interface preview](view.png)

---

## Installation

### Requirements

- Python 3.8 or higher
- pip

### From source

```bash
git clone https://github.com/valuthringer/Auto-Backup-and-Delete.git
cd Auto-Backup-and-Delete
pip install schedule
python autobackup.py
```

### From the executable (.exe)

Download the latest `.exe` from the [Releases](https://github.com/valuthringer/Auto-Backup-and-Delete/releases) page and run it directly — no Python installation required.

To recompile the executable yourself:

```bash
pip install pyinstaller
pyinstaller autobackup.spec
```

---

## Usage Guide

### Backup

1. Click **+ Add Source Folder** to add the folders you want to back up
2. Click **+ Add Destination Folder** to choose one or more destinations
3. Set the frequency (every N days) and time in the **Schedule** section
4. Toggle **Enable Auto-Backup** for scheduled backups, or click **Manual Backup** for an immediate backup

> Backups are `.zip` files named `Backup_DD-MM-YYYY_N.zip`.  
> If multiple destinations are configured, the file is copied to each one simultaneously.

### Deletion

1. Click **+ Add Deletion Folder** to monitor one or more folders
2. Set the retention period in **Keep backups since**
3. Set the daily cleanup time in **Daily schedule**
4. Toggle **Enable Auto-Delete** or click **Manual Delete** to run the cleanup

> Only `.zip` files are targeted by scheduled/manual deletion.  
> **Force Purge All** deletes all content in the monitored folders (double confirmation required).

### Profiles

| Action | Description |
|---|---|
| **New Profile** | Resets all fields to start fresh |
| **Save Profile As** | Saves the current configuration under a new name |
| **Save Profile** | Updates the currently active profile |
| **Load Profile** | Applies the selected profile from the list |
| **Delete Profile** | Permanently removes the selected profile |

The active profile is **auto-saved every 5 minutes** in the background.

---

## Tech Stack

| Component | Detail |
|---|---|
| Language | Python 3.8+ |
| GUI | Tkinter + ttk |
| UI Theme | [Forest-ttk-theme](https://github.com/rdbende/Forest-ttk-theme) (dark) |
| Compression | `zipfile` (ZIP_DEFLATED) |
| Scheduling | `schedule` |
| Threading | `threading` (non-blocking operations) |
| Persistence | JSON (`%APPDATA%\Auto-Backup-and-Delete\profiles.json`) |
| Build | PyInstaller |

---

## Author

Developed by **Valentin Luthringer** — [@valuthringer](https://valuthringer.github.io)

Version **3.1** — May 2026
