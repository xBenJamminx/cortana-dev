#!/usr/bin/env python3
# DEPRECATED — use sleep_pipeline.py instead.
# This shim exists for backwards compatibility only.
import subprocess, sys
subprocess.run([sys.executable,
    '/root/.openclaw/workspace/core/content/sleep/pipeline.py'] + sys.argv[1:])
