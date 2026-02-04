#!/usr/bin/env python3
"""
Excel/CSV Processor for OpenClaw
Handles large spreadsheet files by extracting content to readable format
"""
import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

# Use the workspace-os venv
VENV_PATH = '/root/clawd/workspace-os/venv'
sys.path.insert(0, f'{VENV_PATH}/lib/python3.12/site-packages')

import pandas as pd

MEDIA_DIR = Path('/root/.openclaw/media/inbound')
OUTPUT_DIR = Path('/root/.openclaw/media/processed')
SUMMARY_DIR = Path('/root/clawd/memory/spreadsheets')

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

def get_file_hash(filepath):
    return hashlib.md5(Path(filepath).read_bytes()).hexdigest()[:8]

def process_spreadsheet(filepath, max_rows_preview=50, max_cols=20):
    """Process Excel/CSV file and create a readable summary"""
    filepath = Path(filepath)

    try:
        ext = filepath.suffix.lower()
        if ext == '.csv':
            df = pd.read_csv(filepath, nrows=1000)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(filepath, nrows=1000)
        else:
            return {'error': f'Unsupported format: {ext}'}

        total_rows = len(df)
        total_cols = len(df.columns)

        if total_cols > max_cols:
            df = df.iloc[:, :max_cols]

        file_hash = get_file_hash(filepath)
        summary_file = SUMMARY_DIR / f'{filepath.stem}_{file_hash}.md'

        lines = [
            f'# Spreadsheet: {filepath.name}',
            f'*Processed: {datetime.now().isoformat()}*',
            '',
            '## Overview',
            f'- **Total Rows**: {total_rows}',
            f'- **Total Columns**: {total_cols}',
            f'- **Columns**: {list(df.columns[:max_cols])}',
            '',
            '## Data Types',
            '```',
        ]

        for col, dtype in df.dtypes.items():
            lines.append(f'{col}: {dtype}')
        lines.append('```')

        lines.extend([
            '',
            f'## Preview (first {min(max_rows_preview, total_rows)} rows)',
            '',
            df.head(max_rows_preview).to_markdown(index=False),
            '',
        ])

        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            lines.extend([
                '## Numeric Summary',
                '',
                df[numeric_cols].describe().to_markdown(),
                '',
            ])

        summary_content = '\n'.join(lines)
        summary_file.write_text(summary_content)

        full_file = OUTPUT_DIR / f'{filepath.stem}_{file_hash}_full.csv'
        df.to_csv(full_file, index=False)

        return {
            'status': 'processed',
            'original': str(filepath),
            'summary_file': str(summary_file),
            'full_csv': str(full_file),
            'rows': total_rows,
            'cols': total_cols,
            'columns': list(df.columns[:max_cols]),
            'preview': summary_content[:2000]
        }

    except Exception as e:
        return {'error': str(e), 'file': str(filepath)}

def find_recent_spreadsheets(hours=24):
    """Find spreadsheet files from the last N hours"""
    import time
    cutoff = time.time() - (hours * 3600)

    files = []
    for f in MEDIA_DIR.glob('*'):
        if f.suffix.lower() in ['.csv', '.xlsx', '.xls']:
            if f.stat().st_mtime > cutoff:
                files.append(f)
    return sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        result = process_spreadsheet(sys.argv[1])
    else:
        files = find_recent_spreadsheets()
        if files:
            print(f'Found {len(files)} recent spreadsheet(s)')
            for f in files:
                print(f'\nProcessing: {f.name}')
                result = process_spreadsheet(f)
                print(json.dumps(result, indent=2))
        else:
            print('No recent spreadsheets found')
            result = {'status': 'no_files'}

    if len(sys.argv) > 1:
        print(json.dumps(result, indent=2))
