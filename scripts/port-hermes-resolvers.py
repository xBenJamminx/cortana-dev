#!/usr/bin/env python3
"""Port the Hermes path/env/gateway resolvers into another agent's workspace.

Cortana runs this against a sibling agent on the same host (Scout, MiMoo, ...)
to apply the same OpenClaw -> Hermes migration this repository went through.

    # See what would change, touching nothing:
    python3 scripts/port-hermes-resolvers.py --target /path/to/scout

    # Apply it:
    python3 scripts/port-hermes-resolvers.py --target /path/to/scout --apply

Dry run is the default. Nothing is written without --apply.

What it does:
  1. installs lib/{paths,env,gateway}.py into the target (agent-neutral, no
     configuration needed -- they discover the workspace from their location)
  2. rewrites hardcoded /root/clawd, /root/.openclaw, /root/.clawdbot paths in
     Python to the resolvers, inserting the import bootstrap
  3. rewrites `source ~/.openclaw/.env` in shell to a Hermes-first loop
  4. replaces per-script _load_env() copies with the shared lib.env loader

What it deliberately does NOT touch:
  - dated memory, reports, published post copy, cached source material
  - utilities whose job is removing legacy state (cleanup-user-systemd.sh)
  - systemd unit names, logrotate configs, crontabs, gateway HTTP endpoints

Those are listed under NEEDS MANUAL REVIEW so a human decides.
"""
import argparse
import re
import subprocess
import sys
import tarfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
RESOLVERS = ("paths.py", "env.py", "gateway.py")

# Paths never rewritten: records, published copy, legacy-removal tools.
SKIP_DIRS = {
    "memory", "reports", "social_posts", "node_modules", "venv", ".git",
    "__pycache__", "logs", "data",
}
SKIP_NAMES = {
    "ERROR_LOG.md", "learnings_patch.md", "OPENCLAW-MIGRATION.md",
    "cleanup-user-systemd.sh", "sync-cli-sessions.sh",
    "port-hermes-resolvers.py",
}
SKIP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}.*\.md$")

Q = r"""['"]"""
WS = r"(?:clawd|\.openclaw/workspace)"
HOME = r"\.(?:openclaw|clawdbot)"

# (pattern, replacement, resolver name required)
RULES = [
    (rf"{Q}/root/{HOME}/memory/main\.sqlite{Q}", "memory_db()", "memory_db"),
    (rf"{Q}/root/{HOME}/(google_credentials\.json){Q}", r'agent_file("\1")', "agent_file"),
    (rf"Path\({Q}/root/{WS}/logs/([\w.\-]+){Q}\)", r'log_file("\1")', "log_file"),
    (rf"{Q}/root/{WS}/logs/([\w.\-]+){Q}", r'str(log_file("\1"))', "log_file"),
    (rf"Path\({Q}/root/{WS}/memory/([\w.\-]+){Q}\)", r'memory_file("\1")', "memory_file"),
    (rf"{Q}/root/{WS}/scripts/([\w.\-]+){Q}", r'str(SCRIPTS / "\1")', "SCRIPTS"),
    (rf"Path\({Q}/root/{WS}/(ERROR_LOG\.md|USER\.md){Q}\)", r'WORKSPACE / "\1"', "WORKSPACE"),
    (rf"Path\({Q}/root/{WS}/(reports|memory|drafts|config|identity){Q}\)", r'WORKSPACE / "\1"', "WORKSPACE"),
    (rf"{Q}/root/{WS}/(config|identity|skills)/([\w./\-]+){Q}", r'str(WORKSPACE / "\1" / "\2")', "WORKSPACE"),
    (rf"Path\({Q}/root/clawd{Q}\)", "WORKSPACE", "WORKSPACE"),
    (rf"{Q}/root/clawd{Q}", "str(WORKSPACE)", "WORKSPACE"),
    (rf"{Q}/root/{HOME}/([\w./\-]+){Q}", r'agent_file("\1")', "agent_file"),
]

# Whole-function replacement for per-script env loaders.
LOADER_RE = re.compile(r"\ndef _load_env\(\):\n(?:.*?\n)*?_load_env\(\)\n", re.M)

SH_ENV = '''for _env in "$HOME/.hermes/.env" "$HOME/.openclaw/.env"; do
  [ -f "$_env" ] && { set -a; . "$_env"; set +a; break; }
done'''
SH_SOURCE_RE = re.compile(
    r"^[ \t]*(?:source|\.)[ \t]+(?:/root/\.(?:openclaw|clawdbot)|\$HOME/\.(?:openclaw|clawdbot)|~/\.(?:openclaw|clawdbot))/\.env[ \t]*$",
    re.M,
)

# Reported, never auto-edited.
MANUAL_RE = re.compile(
    r"openclaw-gateway|systemctl|journalctl|crontab|logrotate|/api/models|/api/ai/|clawdbot\.json|openclaw\.json",
    re.I,
)

LEGACY_RE = re.compile(r"/root/(?:clawd|\.openclaw|\.clawdbot)|~/\.(?:openclaw|clawdbot)|~/clawd")


# Where sibling agent workspaces tend to live on a Hermes host.
SEARCH_ROOTS = ("/root", "/home", "/srv", "/opt")

# A directory looks like an agent workspace if it has these.
MARKERS = ("AGENTS.md", "CLAUDE.md", "SOUL.md", "IDENTITY.md")


def discover() -> list[tuple[Path, str]]:
    """Find sibling agent workspaces on this host.

    Looks two levels deep under the usual roots for directories carrying agent
    marker files, and skips this repository.
    """
    found, seen = [], set()
    for root in SEARCH_ROOTS:
        base = Path(root)
        if not base.is_dir():
            continue
        candidates = [base]
        try:
            candidates += [p for p in base.iterdir() if p.is_dir()]
            for child in list(candidates):
                if child != base:
                    try:
                        candidates += [p for p in child.iterdir() if p.is_dir()]
                    except PermissionError:
                        pass
        except PermissionError:
            continue

        for path in candidates:
            try:
                resolved = path.resolve()
            except OSError:
                continue
            if resolved in seen or resolved == HERE:
                continue
            if resolved.name.startswith(".") or "node_modules" in resolved.parts:
                continue
            hits = [m for m in MARKERS if (resolved / m).exists()]
            if not hits:
                continue
            seen.add(resolved)
            ported = (resolved / "lib" / "paths.py").exists()
            why = f"has {', '.join(hits[:2])}"
            why += "; already ported" if ported else "; NOT yet ported"
            found.append((resolved, why))
    return sorted(found)


def walk(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.name in SKIP_NAMES or SKIP_RE.match(path.name):
            continue
        yield path, rel


def bootstrap(depth: int, names) -> list[str]:
    up = "_os.path.dirname(" * (depth + 1) + "_os.path.abspath(__file__)" + ")" * (depth + 1)
    return [
        "import os as _os",
        "import sys as _sys",
        f"_sys.path.insert(0, {up})",
        f"from lib.paths import {', '.join(sorted(names))}",
        "",
    ]


def insert_index(lines: list[str]) -> int:
    """First index safe for a top-level import: after shebang and docstring."""
    i = 1 if lines and lines[0].startswith("#!") else 0
    while i < len(lines) and (not lines[i].strip() or lines[i].lstrip().startswith("#")):
        i += 1
    if i < len(lines):
        stripped = lines[i].lstrip()
        for quote in ('"""', "'''"):
            if stripped.startswith(quote):
                body = stripped.rstrip()
                if len(body) > 5 and body.endswith(quote):
                    return i + 1
                i += 1
                while i < len(lines) and quote not in lines[i]:
                    i += 1
                return i + 1
    return i


def migrate_python(src: str, rel: Path) -> tuple[str, set[str]]:
    out, needed = src, set()
    for pattern, repl, name in RULES:
        out, n = re.subn(pattern, repl, out)
        if n:
            needed.add(name)

    out, loaders = LOADER_RE.subn("\nfrom lib.env import load_env\n\nload_env()\n", out, count=1)
    if loaders:
        needed.add("__env__")

    if not needed:
        return src, set()

    resolvers = {n for n in needed if n != "__env__"}
    lines = out.split("\n")
    if "from lib.paths import" not in src:
        block = bootstrap(len(rel.parts) - 1, resolvers) if resolvers else []
        if loaders:
            depth = len(rel.parts) - 1
            up = "_os.path.dirname(" * (depth + 1) + "_os.path.abspath(__file__)" + ")" * (depth + 1)
            block = [
                "import os as _os",
                "import sys as _sys",
                f"_sys.path.insert(0, {up})",
            ]
            if resolvers:
                block.append(f"from lib.paths import {', '.join(sorted(resolvers))}")
            block.append("")
        at = insert_index(lines)
        lines[at:at] = block
    return "\n".join(lines), needed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", help="the other agent's workspace root")
    ap.add_argument("--discover", action="store_true",
                    help="list sibling agent workspaces on this host and exit")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--no-backup", action="store_true",
                    help="skip the pre-change backup archive (not advised)")
    args = ap.parse_args()

    if args.discover:
        found = discover()
        if not found:
            print("No sibling agent workspaces found.")
            print("Searched:", ", ".join(SEARCH_ROOTS))
            return 1
        print("Sibling agent workspaces on this host:\n")
        for path, why in found:
            print(f"  {path}\n      ({why})")
        print("\nRun against one with:")
        print(f"  python3 {Path(__file__).name} --target <path>")
        return 0

    if not args.target:
        ap.error("--target is required (or use --discover to find one)")

    target = Path(args.target).expanduser().resolve()
    if not target.is_dir():
        print(f"error: {target} is not a directory", file=sys.stderr)
        return 2
    if target == HERE:
        print("error: target is this repository; nothing to port", file=sys.stderr)
        return 2

    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"=== Port Hermes resolvers -> {target}  [{mode}] ===\n")

    # Warn on uncommitted work: git is the only undo.
    if (target / ".git").exists():
        dirty = subprocess.run(["git", "-C", str(target), "status", "--porcelain"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            print("WARNING: target has uncommitted changes. Commit first so this is revertible.\n")
    else:
        print("Note: target is not a git repository, so the backup archive below\n"
              "      is the only way to undo this run.\n")

    # 1. resolvers
    lib = target / "lib"
    print("-- resolvers --")
    writes = []          # (path, text) to write after backup
    overwrites = []      # existing files this run would replace
    for name in RESOLVERS:
        dest = lib / name
        state = "overwrite" if dest.exists() else "install"
        print(f"  {state}: lib/{name}")
        if dest.exists():
            overwrites.append(dest)
        writes.append((dest, (HERE / "lib" / name).read_text()))
    init = lib / "__init__.py"
    if not init.exists():
        print("  install: lib/__init__.py")
        writes.append((init, '"""Shared utilities."""\n'))

    # 2. code
    changed, manual = [], []
    print("\n-- code --")
    for path, rel in walk(target):
        if rel.parts[0] == "lib" and path.name in RESOLVERS:
            continue
        try:
            src = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue

        new, needed = src, set()
        if path.suffix == ".py":
            new, needed = migrate_python(src, rel)
        elif path.suffix == ".sh" or (path.suffix == "" and src.startswith("#!")):
            new, n = SH_SOURCE_RE.subn(SH_ENV, src)
            if n:
                needed = {"__sh__"}

        if needed and new != src:
            changed.append((rel, sorted(needed)))
            # Preserve original line endings.
            if "\r\n" in src and "\r\n" not in new:
                new = new.replace("\n", "\r\n")
            writes.append((path, new))
            overwrites.append(path)

        rest = new if needed else src
        if MANUAL_RE.search(rest) or LEGACY_RE.search(rest):
            hits = sorted({
                m.group(0) for m in MANUAL_RE.finditer(rest)
            } | {
                m.group(0) for m in LEGACY_RE.finditer(rest)
            })
            manual.append((rel, hits[:4]))

    if changed:
        for rel, needed in changed:
            print(f"  migrated: {rel}  ({', '.join(needed)})")
    else:
        print("  nothing to migrate")

    if manual:
        print("\n-- NEEDS MANUAL REVIEW (not auto-edited) --")
        for rel, hits in manual:
            print(f"  {rel}: {', '.join(hits)}")

    print(f"\n{len(changed)} file(s) migrated, {len(manual)} need review.")

    if not args.apply:
        print("\nDry run. Re-run with --apply to write.")
        return 0

    # 3. back up everything about to be overwritten, then write.
    # For a target with no git history this archive is the only undo, so it is
    # created by default and only skipped when explicitly waived.
    archive = None
    if overwrites and not args.no_backup:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        archive = target.parent / f"{target.name}-pre-hermes-{stamp}.tar.gz"
        try:
            with tarfile.open(archive, "w:gz") as tar:
                for path in sorted(set(overwrites)):
                    if path.exists():
                        tar.add(path, arcname=str(path.relative_to(target)))
        except OSError as e:
            print(f"\nerror: could not write backup {archive}: {e}", file=sys.stderr)
            print("Nothing was modified. Re-run with --no-backup to override.",
                  file=sys.stderr)
            return 3
        print(f"\nBackup: {archive}")

    for path, text in writes:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    print("\nVerify before restarting the agent:")
    print(f"  cd {target} && python3 -m py_compile $(find . -name '*.py' -not -path './.git/*')")
    print(f"  cd {target} && python3 -c \"from lib.paths import WORKSPACE, LOGS; print(WORKSPACE, LOGS)\"")
    print("  ^ WORKSPACE must print this agent's checkout.")
    if archive:
        print(f"\nRoll back with:\n  tar -xzf {archive} -C {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
