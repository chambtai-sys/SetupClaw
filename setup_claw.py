#!/usr/bin/env python3
"""
SetupClaw - A robust, cross-platform installer for OpenClaw.
Handles prerequisite checks, installation, API key configuration, and verification.
"""

import os
import re
import shutil
import subprocess
import sys
import platform
import getpass
import textwrap

# ─── Constants ──────────────────────────────────────────────────

MIN_NODE_VERSION = (22, 0, 0)
INSTALL_CMD = 'curl -fsSL https://openclaw.ai/install.sh | bash'
DOCS_URL = 'https://docs.openclaw.ai'
SHELL_PROFILES = {
    'bash': os.path.expanduser('~/.bashrc'),
    'zsh': os.path.expanduser('~/.zshrc'),
}

# ─── Colour helpers (disabled when not a TTY) ────────────────

_USE_COLOR = sys.stdout.isatty() and os.environ.get('NO_COLOR') is None


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text


def green(t: str) -> str:
    return _c("32", t)


def red(t: str) -> str:
    return _c("31", t)


def yellow(t: str) -> str:
    return _c("33", t)


def cyan(t: str) -> str:
    return _c("36", t)


def bold(t: str) -> str:
    return _c("1", t)


# ─── Utility functions ────────────

def banner() -> None:
    art = textwrap.dedent(r"""
     ____       _                ____ _
    / ___|  ___| |_ _   _ _ __ / ___| | __ ___      __
    \___ \ / _ \ __| | | | '_ \ |   | |/ _` \ \ /\ / /
     ___) |  __/ |_| |_| | |_) | |__| | (_| |\ V  V /
    |____/ \___|\__|\__,_| .__/ \____|_|\__,_| \_/\_/
                         |_|
    """)
    print(cyan(art))
    print(bold("  OpenClaw Installer & Configuration Tool"))
    print(f"  Platform: {platform.system()} {platform.machine()} | Python {platform.python_version()}")
    print()


def hr() -> None:
    print(cyan("─" * 60))


def run_cmd(cmd: str, capture: bool = True, shell: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        shell=shell,
        capture_output=capture,
        text=True,
    )


def which(binary: str) -> str | None:
    return shutil.which(binary)


def pause() -> None:
    input("\n  Press Enter to return to the menu...")


# ─── Prerequisite checks ─────────────

def check_git() -> bool:
    if which("git") is None:
        return False
    result = run_cmd("git --version")
    return result.returncode == 0


def parse_version(version_str: str) -> tuple[int, ...]:
    match = re.search(r'(\d+)\.(\d+)\.(\d+)', version_str)
    if not match:
        return (0, 0, 0)
    return tuple(int(x) for x in match.groups())


def check_node() -> tuple[bool, str]:
    node = which("node")
    if node is None:
        return False, "not found"
    result = run_cmd("node --version")
    if result.returncode != 0:
        return False, "error running node"
    version_str = result.stdout.strip().lstrip('v')
    version = parse_version(version_str)
    meets = version >= MIN_NODE_VERSION
    return meets, version_str


def check_curl() -> bool:
    return which("curl") is not None


def system_info() -> dict:
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "arch": platform.machine(),
        "python": platform.python_version(),
        "user": getpass.getuser(),
        "home": os.path.expanduser("~"),
        "shell": os.environ.get("SHELL", "unknown"),
    }


def print_system_info() -> None:
    info = system_info()
    hr()
    print(bold("  System Information"))
    hr()
    for key, val in info.items():
        print(f"  {key:<12}: {val}")
    print()


def run_prerequisite_checks() -> bool:
    hr()
    print(bold("  Prerequisite Checks"))
    hr()

    all_ok = True

    # Git
    git_ok = check_git()
    status = green("✔ found") if git_ok else red("✘ missing")
    print(f"  Git          : {status}")
    if not git_ok:
        print(yellow("    → Install Git: https://git-scm.com/downloads"))
        all_ok = False

    # Node.js
    node_ok, node_ver = check_node()
    if node_ok:
        status = green(f"✔ v{node_ver}")
    elif node_ver == "not found":
        status = red("✘ missing")
    else:
        status = red(f"✘ v{node_ver} (need ≥{'.'.join(map(str, MIN_NODE_VERSION))})")
    print(f"  Node.js      : {status}")
    if not node_ok:
        print(yellow("    → Install Node ≥22: https://nodejs.org/"))
        all_ok = False

    # curl
    curl_ok = check_curl()
    status = green("✔ found") if curl_ok else red("✘ missing")
    print(f"  curl         : {status}")
    if not curl_ok:
        print(yellow("    → curl is required for the installer"))
        all_ok = False

    print()
    if all_ok:
        print(green("  All prerequisites satisfied!"))
    else:
        print(red("  Some prerequisites are missing. Please install them first."))

    return all_ok


# ─── Menu actions ─────────────

def action_install() -> None:
    hr()
    print(bold("  Install OpenClaw"))
    hr()

    prereqs_ok = run_prerequisite_checks()
    if not prereqs_ok:
        print()
        print(yellow("  ⚠  Resolve missing prerequisites before installing."))
        pause()
        return

    print()
    print(f"  This will run:")
    print(f"    {cyan(INSTALL_CMD)}")
    print()

    confirm = input("  Proceed with installation? [y/N] ").strip().lower()
    if confirm not in ('y', 'yes'):
        print(yellow("  Installation cancelled."))
        pause()
        return

    print()
    print(bold("  Running installer…"))
    print()
    result = run_cmd(INSTALL_CMD, capture=False)

    if result.returncode == 0:
        print()
        print(green("  ✔ OpenClaw installed successfully!"))
    else:
        print()
        print(red(f"  ✘ Installation failed (exit code {result.returncode})."))
        print(yellow(f"    Check {DOCS_URL} for troubleshooting."))

    pause()


def detect_shell_profile() -> str | None:
    shell = os.environ.get('SHELL', '')
    if 'zsh' in shell and os.path.exists(SHELL_PROFILES['zsh']):
        return SHELL_PROFILES['zsh']
    if os.path.exists(SHELL_PROFILES['bash']):
        return SHELL_PROFILES['bash']
    # Fallback: try zsh then bash even if SHELL doesn't match
    for path in SHELL_PROFILES.values():
        if os.path.exists(path):
            return path
    return None


def _read_existing_keys(profile_path: str) -> dict[str, str]:
    keys: dict[str, str] = {}
    try:
        with open(profile_path, 'r') as f:
            for line in f:
                for var in ('ANTHROPIC_API_KEY', 'OPENAI_API_KEY'):
                    m = re.match(rf'^export\s+{var}=["\']?(.+?)["\']?\s*$', line)
                    if m:
                        keys[var] = m.group(1)
    except OSError:
        pass
    return keys


def _write_key(profile_path: str, var_name: str, value: str) -> None:
    export_line = f'export {var_name}="{value}"'
    # Read existing content
    lines: list[str] = []
    replaced = False
    try:
        with open(profile_path, 'r') as f:
            for line in f:
                if re.match(rf'^export\s+{var_name}=', line):
                    lines.append(export_line + '\n')
                    replaced = True
                else:
                    lines.append(line)
    except FileNotFoundError:
        pass

    if not replaced:
        # Add a comment header the first time
        if not lines or not any('SetupClaw' in l for l in lines):
            lines.append('\n# ── Added by SetupClaw ──\n')
        lines.append(export_line + '\n')

    with open(profile_path, 'w') as f:
        f.writelines(lines)


def action_setup_keys() -> None:
    hr()
    print(bold("  Setup API Keys"))
    hr()

    profile = detect_shell_profile()
    if profile is None:
        print(red("  Could not detect shell profile (~/.bashrc or ~/.zshrc)."))
        print(yellow("  You can manually export your keys in your shell config."))
        pause()
        return

    print(f"  Detected profile: {cyan(profile)}")
    existing = _read_existing_keys(profile)
    print()

    keys_to_write: dict[str, str] = {}

    for label, var in [("Anthropic", "ANTHROPIC_API_KEY"), ("OpenAI", "OPENAI_API_KEY")]:
        current = existing.get(var)
        if current:
            masked = current[:8] + "…" + current[-4:] if len(current) > 14 else "****"
            print(f"  {label} key ({var}): {green('set')} → {masked}")
            overwrite = input(f"    Overwrite? [y/N] ").strip().lower()
            if overwrite not in ('y', 'yes'):
                continue
        else:
            print(f"  {label} key ({var}): {yellow('not set')}")

        value = input(f"    Enter {label} API key (blank to skip): ").strip()
        if value:
            keys_to_write[var] = value

    if not keys_to_write:
        print(yellow("\n  No changes made."))
        pause()
        return

    for var, value in keys_to_write.items():
        _write_key(profile, var, value)
        print(green(f"  ✔ {var} written to {profile}"))

    print()
    print(yellow(f"  Run `source {profile}` or open a new terminal to apply changes."))
    pause()


def action_verify() -> None:
    hr()
    print(bold("  Verify Installation"))
    hr()

    openclaw = which("openclaw")
    if openclaw is None:
        print(red("  ✘ 'openclaw' not found on PATH."))
        print(yellow("    Install OpenClaw first (option 1), or ensure it's on your PATH."))
        pause()
        return

    print(green(f"  ✔ openclaw found: {openclaw}"))
    print()

    # Version
    ver_result = run_cmd("openclaw --version")
    if ver_result.returncode == 0:
        print(f"  Version: {ver_result.stdout.strip()}")
    print()

    # Doctor
    print(bold("  Running `openclaw doctor`…"))
    print()
    result = run_cmd("openclaw doctor", capture=False)

    if result.returncode == 0:
        print()
        print(green("  ✔ openclaw doctor passed!"))
    else:
        print()
        print(red(f"  ✘ openclaw doctor reported issues (exit code {result.returncode})."))

    pause()


def action_docs() -> None:
    hr()
    print(bold("  OpenClaw Documentation"))
    hr()
    print()
    print(f"  Official docs : {cyan(DOCS_URL)}")
    print(f"  GitHub        : {cyan('https://github.com/openclaw-ai/openclaw')}")
    print(f"  Discord       : {cyan('https://discord.gg/openclaw')}")
    print()

    # Try to open in browser
    try:
        import webbrowser
        open_it = input("  Open docs in browser? [y/N] ").strip().lower()
        if open_it in ('y', 'yes'):
            webbrowser.open(DOCS_URL)
            print(green("  ✔ Opened in browser."))
    except Exception:
        pass

    pause()


# ─── Main loop ────────

def main_menu() -> None:
    banner()
    print_system_info()

    while True:
        hr()
        print(bold("  Main Menu"))
        hr()
        print("  [1] Install OpenClaw")
        print("  [2] Setup API Keys (Anthropic / OpenAI)")
        print("  [3] Verify Installation & Run Doctor")
        print("  [4] Documentation & Resources")
        print("  [5] Run Prerequisite Checks")
        print("  [q] Quit")
        print()

        choice = input("  Select an option: ").strip().lower()

        if choice == '1':
            action_install()
        elif choice == '2':
            action_setup_keys()
        elif choice == '3':
            action_verify()
        elif choice == '4':
            action_docs()
        elif choice == '5':
            run_prerequisite_checks()
            pause()
        elif choice in ('q', 'quit', 'exit'):
            print()
            print(green("  Goodbye! 🐾"))
            print()
            break
        else:
            print(red("  Invalid option. Try again."))


if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n")
        print(yellow("  Interrupted. Exiting."))
        sys.exit(130)
