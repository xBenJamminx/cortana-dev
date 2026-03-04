---
name: excel-reader
description: Read and process Excel (.xlsx, .xls) and CSV files. Use when asked to read spreadsheets, extract data, summarize tables, or analyze tabular data.
---

# Excel Reader

Read, preview, and process Excel and CSV files.

## Usage

```bash
python3 /root/.openclaw/workspace/scripts/excel-processor.py <filepath>
```

Processes the file and creates a readable summary with:
- Sheet names and dimensions
- Column headers and types
- Preview of first 50 rows
- Basic statistics

## Supported Formats

- `.xlsx` (Excel 2007+)
- `.xls` (Legacy Excel)
- `.csv` (Comma-separated values)

## When to Use

- User shares a spreadsheet and asks "what's in this?"
- Need to extract data from Excel for analysis
- Converting spreadsheet data to other formats

## Dependencies

- `pandas` (installed in workspace-os venv)
- `openpyxl` for .xlsx files
