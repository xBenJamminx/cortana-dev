"""
Portable script-path resolution for Cortana.

Cortana runs in more than one place: the production box (/root/cortana), the
older clawd tree (/root/clawd), and ephemeral Claude Code containers that get a
fresh clone of cortana-dev under a completely different root. Cron prompts that
hardcode an absolute server path break everywhere except the box they were
written on.

The failure is also misleading. Python reports [Errno 13] Permission denied both
when a file exists but is unreadable AND when any parent directory is not
searchable -- so a cron running as a non-root user against /root/cortana/... gets
"permission denied" whether or not the script is there at all. This module
probes each candidate and says which of those it actually is.

Usage:
    from lib.paths import resolve_script, ScriptNotFound

    try:
        path = resolve_script("hungryroot_api.py")
    except ScriptNotFound as e:
        print(e)  # includes every location tried and why each one failed
"""
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Ordered by trust: explicit override, then the tree we are running from, then
# the known server layouts.
_DEFAULT_ROOTS = (
    os.environ.get("CORTANA_HOME"),
    REPO_ROOT,
    Path.home() / "cortana",
    "/root/cortana",
    Path.home() / "clawd",
    "/root/clawd",
)

# Subdirectories searched inside each root, in order.
_SUBDIRS = ("scripts", "")


def candidate_roots(extra_roots=None):
    """Candidate Cortana roots, de-duplicated, in search order."""
    roots = []
    seen = set()
    for root in list(extra_roots or ()) + [r for r in _DEFAULT_ROOTS if r]:
        path = Path(root).expanduser()
        if path not in seen:
            seen.add(path)
            roots.append(path)
    return roots


def _probe(path):
    """Return (found, reason) for one candidate path.

    reason explains a miss precisely enough to act on: missing tree, missing
    file, unreadable file, or an ancestor directory this process cannot search.
    """
    try:
        if not path.exists():
            blocker = _unsearchable_ancestor(path)
            if blocker:
                return False, f"unsearchable parent {blocker} (running as uid {os.getuid()})"
            return False, "not found"
    except PermissionError:
        blocker = _unsearchable_ancestor(path)
        return False, f"unsearchable parent {blocker or path.parent} (running as uid {os.getuid()})"

    if not path.is_file():
        return False, "not a file"
    if not os.access(path, os.R_OK):
        return False, f"exists but not readable by uid {os.getuid()}"
    return True, "ok"


def _unsearchable_ancestor(path):
    """Deepest ancestor of path that exists but cannot be searched, if any."""
    for parent in path.parents:
        try:
            if parent.exists() and not os.access(parent, os.X_OK):
                return parent
        except PermissionError:
            continue
    return None


class ScriptNotFound(FileNotFoundError):
    """Raised when a script cannot be resolved in any candidate root."""

    def __init__(self, name, attempts):
        self.name = name
        self.attempts = attempts
        lines = [f"Could not resolve script {name!r}. Tried:"]
        lines += [f"  {path}  ->  {reason}" for path, reason in attempts]
        lines.append(
            "Fix: commit the script to this repo under scripts/, or set "
            "CORTANA_HOME to a tree this process can read."
        )
        super().__init__("\n".join(lines))


def resolve_script(name, extra_roots=None):
    """Return the readable Path to a Cortana script, searching known roots.

    An absolute or explicitly relative name is honoured as-is and only probed
    for readability, so callers can still pass a specific file.

    Raises:
        ScriptNotFound: with every location tried and why each one failed.
    """
    given = Path(name).expanduser()
    if given.is_absolute() or name.startswith((".", "..")):
        found, reason = _probe(given)
        if found:
            return given
        raise ScriptNotFound(name, [(given, reason)])

    attempts = []
    for root in candidate_roots(extra_roots):
        for subdir in _SUBDIRS:
            candidate = root / subdir / given if subdir else root / given
            found, reason = _probe(candidate)
            if found:
                return candidate
            attempts.append((candidate, reason))
    raise ScriptNotFound(name, attempts)
