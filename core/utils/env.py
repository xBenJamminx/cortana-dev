"""Environment utilities for loading .env files."""
import os
from pathlib import Path

_env_loaded = False


def load_env(env_path: Path = None) -> dict:
    """Parse .env file into os.environ (idempotent).
    
    Args:
        env_path: Path to .env file. Defaults to ~/.openclaw/.env
        
    Returns:
        Dict of loaded environment variables
    """
    global _env_loaded
    
    if _env_loaded:
        return dict(os.environ)
        
    if env_path is None:
        env_path = Path('/root/.openclaw/.env')
    
    env_vars = {}
    
    if not env_path.exists():
        return env_vars
        
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        # Handle 'export KEY=VAL' format
        if line.startswith('export '):
            line = line[7:]
        if '=' not in line:
            continue
        key, _, val = line.partition('=')
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)
        env_vars[key] = val
    
    _env_loaded = True
    return env_vars


# Backwards compatibility alias
_load_env = load_env
