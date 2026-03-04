---
name: cs-xlsx
description: Excel spreadsheet toolkit. This skill should be used when creating, editing, or analyzing .xlsx files. Supports creating spreadsheets with formulas and formatting, reading/analyzing data with pandas, modifying existing files while preserving formulas, and building financial models. Includes best practices for formula construction and data visualization.
---

# Excel Spreadsheet Processing

Toolkit for creating, editing, and analyzing Excel files (.xlsx format).

## Core Principle: Use Formulas

**Always use Excel formulas instead of hardcoding calculated values.** This keeps spreadsheets dynamic and auditable.

```python
# WRONG - hardcoded calculation
sheet['B10'] = 5000  # Result of sum

# CORRECT - Excel formula
sheet['B10'] = '=SUM(B2:B9)'
```

## Workflow Selection

| Goal | Tool |
|------|------|
| **Read/analyze data** | pandas |
| **Create with formulas** | openpyxl |
| **Simple data export** | pandas |
| **Complex formatting** | openpyxl |
| **Financial models** | openpyxl with standards |

## Read & Analyze Data

```python
import pandas as pd

# Read single sheet
df = pd.read_excel('data.xlsx')

# Read all sheets
sheets = pd.read_excel('data.xlsx', sheet_name=None)  # Returns dict

# Analysis
print(df.head())
print(df.describe())
print(df.info())

# Filter and aggregate
summary = df.groupby('category')['amount'].sum()
```

## Create Spreadsheets

### Basic Creation

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

wb = Workbook()
ws = wb.active
ws.title = "Sales Report"

# Headers
headers = ["Product", "Q1", "Q2", "Q3", "Q4", "Total"]
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True)
    cell.fill = PatternFill(start_color="366092", fill_type="solid")
    cell.font = Font(bold=True, color="FFFFFF")

# Data with formulas
data = [
    ["Widget A", 1200, 1350, 1400, 1550],
    ["Widget B", 800, 850, 900, 950],
    ["Widget C", 600, 620, 680, 720],
]

for row_idx, row_data in enumerate(data, 2):
    for col_idx, value in enumerate(row_data, 1):
        ws.cell(row=row_idx, column=col_idx, value=value)
    # Total formula
    ws.cell(row=row_idx, column=6, value=f"=SUM(B{row_idx}:E{row_idx})")

# Column totals
for col in range(2, 7):
    col_letter = chr(64 + col)
    ws.cell(row=5, column=col, value=f"=SUM({col_letter}2:{col_letter}4)")

ws.cell(row=5, column=1, value="Total")
ws.cell(row=5, column=1).font = Font(bold=True)

# Column widths
ws.column_dimensions['A'].width = 15
for col in 'BCDEF':
    ws.column_dimensions[col].width = 12

wb.save("sales_report.xlsx")
```

### Number Formatting

```python
from openpyxl.styles import numbers

# Currency
cell.number_format = '$#,##0.00'

# Percentage
cell.number_format = '0.0%'

# Negative in parentheses
cell.number_format = '$#,##0;($#,##0)'

# Date
cell.number_format = 'YYYY-MM-DD'
```

## Edit Existing Files

```python
from openpyxl import load_workbook

# Preserve formulas (default)
wb = load_workbook('existing.xlsx')

# Read calculated values only
wb_values = load_workbook('existing.xlsx', data_only=True)

ws = wb.active

# Modify cell
ws['A1'] = 'Updated Header'

# Add new data
ws.append(['New Row', 100, 200, 300])

# Insert row
ws.insert_rows(3)

# Delete column
ws.delete_cols(2)

wb.save('modified.xlsx')
```

## Financial Model Standards

### Color Conventions

| Color | Usage |
|-------|-------|
| Blue text | Hardcoded inputs, assumptions |
| Black text | Formulas and calculations |
| Green text | Links from other sheets |
| Yellow background | Cells needing review |

```python
from openpyxl.styles import Font

# Input cell (blue)
cell.font = Font(color="0000FF")

# Formula cell (black)
cell.font = Font(color="000000")

# Cross-sheet link (green)
cell.font = Font(color="008000")
```

### Formula Best Practices

```python
# Separate assumptions
ws['B1'] = 'Growth Rate'
ws['C1'] = 0.05  # Assumption cell
ws['C1'].font = Font(color="0000FF")

# Reference assumptions in formulas
ws['B5'] = '=B4*(1+$C$1)'  # Not =B4*1.05
```

## Common Formulas

```python
# Sum
'=SUM(A1:A10)'

# Average
'=AVERAGE(B2:B20)'

# Conditional sum
'=SUMIF(A:A,"Category",B:B)'

# Lookup
'=VLOOKUP(A2,Data!A:C,3,FALSE)'

# If statement
'=IF(A1>100,"High","Low")'

# Nested calculation
'=ROUND(SUM(A1:A10)*1.08,2)'
```

## Charts with pandas

```python
import pandas as pd

df = pd.read_excel('data.xlsx')

# Create chart and save to new Excel
with pd.ExcelWriter('with_chart.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Data', index=False)

    # Add chart using openpyxl
    from openpyxl.chart import BarChart, Reference

    workbook = writer.book
    worksheet = writer.sheets['Data']

    chart = BarChart()
    chart.title = "Sales by Product"
    data = Reference(worksheet, min_col=2, min_row=1, max_row=5, max_col=2)
    categories = Reference(worksheet, min_col=1, min_row=2, max_row=5)
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(categories)
    worksheet.add_chart(chart, "E2")
```

## Validation & Error Checking

Common formula errors to prevent:

| Error | Cause | Prevention |
|-------|-------|------------|
| `#REF!` | Invalid cell reference | Check ranges exist |
| `#DIV/0!` | Division by zero | Use `=IF(B1=0,0,A1/B1)` |
| `#VALUE!` | Wrong data type | Validate inputs |
| `#NAME?` | Unknown formula | Check spelling |
| `#N/A` | Lookup not found | Use `IFERROR()` wrapper |

## Dependencies

| Package | Purpose | Install |
|---------|---------|---------|
| openpyxl | Create/edit with formulas | `pip install openpyxl` |
| pandas | Data analysis | `pip install pandas` |
| xlrd | Read .xls (legacy) | `pip install xlrd` |

## Quick Reference

| Task | Code |
|------|------|
| New workbook | `Workbook()` |
| Load existing | `load_workbook('file.xlsx')` |
| Active sheet | `wb.active` |
| Set cell | `ws['A1'] = value` |
| Add formula | `ws['B1'] = '=SUM(A1:A10)'` |
| Append row | `ws.append([values])` |
| Save | `wb.save('file.xlsx')` |
