<div align="center">

# 🐾 SetupClaw

**A robust, cross-platform Python installer for [OpenClaw](https://openclaw.ai)**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Installer-FF6B35?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PC9zdmc+)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## Introduction

**SetupClaw** is an interactive command-line tool that streamlines the installation and configuration of [OpenClaw](https://openclaw.ai). It handles prerequisite verification, one-command installation, API key management, and post-install diagnostics — all from a single Python script with **zero external dependencies**.

## Prerequisites

| Requirement | Minimum Version | Purpose |
|---|---|---|
| **Python** | 3.10+ | Runs the installer |
| **Node.js** | 22.0.0+ | Required by OpenClaw |
| **Git** | Any recent | Cloning & version control |
| **curl** | Any recent | Downloading the install script |

> SetupClaw will check all prerequisites for you and report what's missing.

## Installation

```bash
# Clone the repository
git clone https://github.com/chambtai-sys/SetupClaw.git
cd SetupClaw

# Run the installer
python3 setup_claw.py
```

No `pip install` needed — SetupClaw uses only the Python standard library.

## Usage

Launch the interactive menu:

```bash
python3 setup_claw.py
```

You'll see:

```
  Main Menu
────────────────────────────────────────
  [1] Install OpenClaw
  [2] Setup API Keys (Anthropic / OpenAI)
  [3] Verify Installation & Run Doctor
  [4] Documentation & Resources
  [5] Run Prerequisite Checks
  [6] Explore Agent Examples
  [q] Quit
```

### Option Details

| Option | What It Does |
|---|---|
| **1 — Install OpenClaw** | Runs prerequisite checks, then executes the official installer (`curl -fsSL https://openclaw.ai/install.sh \| bash`). |
| **2 — Setup API Keys** | Detects your shell profile (`~/.bashrc` or `~/.zshrc`), shows existing keys, and writes new `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` exports. |
| **3 — Verify & Doctor** | Confirms `openclaw` is on your PATH, prints its version, and runs `openclaw doctor` for a full health check. |
| **4 — Documentation** | Links to official docs, GitHub, and Discord. Optionally opens docs in your browser. |
| **5 — Prerequisites** | Checks Node.js, Git, and curl without installing anything. |
| **6 — Agent Examples** | Explore pre-configured agent templates for research and coding. |

## Features

- **Zero dependencies** — pure Python standard library; no `pip install` required.
- **Cross-platform** — works on Linux, macOS, and WSL.
- **Smart shell detection** — automatically finds `~/.zshrc` or `~/.bashrc`.
- **Non-destructive key management** — detects existing API keys, masks them, and asks before overwriting.
- **Coloured output** — respects `NO_COLOR` and non-TTY environments.
- **Safe execution** — confirms destructive actions before running.
- **Agent Examples** — Explore pre-configured agent templates for research and coding.

## Project Structure

```
SetupClaw/
├── setup_claw.py      # Main installer script
├── README.md          # This file
├── LICENSE            # MIT License
├── requirements.txt   # Empty (stdlib only)
└── examples/          # Agent and skill templates
```

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository.
2. Create a feature branch: `git checkout -b feature/my-improvement`.
3. Commit your changes: `git commit -m "Add my improvement"`.
4. Push to your branch: `git push origin feature/my-improvement`.
5. Open a **Pull Request**.

Please ensure your code:
- Passes all existing tests (`python3 -m pytest tests/ -x -q`).
- Uses only the Python standard library.
- Follows the existing code style.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
