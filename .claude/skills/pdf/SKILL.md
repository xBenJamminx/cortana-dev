---
name: cs-pdf
description: PDF document processing toolkit. This skill should be used when working with PDF files - reading content, combining documents, splitting pages, extracting data, creating new PDFs, or filling forms. Supports text extraction, table parsing, document merging/splitting, page manipulation, form filling (both interactive and static forms), OCR for scanned documents, and PDF generation.
---

# PDF Document Processing

Toolkit for PDF manipulation including reading, writing, merging, splitting, and form handling.

## Task Workflows

### Read & Extract Content

**Extract text from a PDF:**

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        print(page.extract_text())
```

**Extract tables as DataFrames:**

```python
import pdfplumber
import pandas as pd

with pdfplumber.open("report.pdf") as pdf:
    tables = []
    for page in pdf.pages:
        for table in page.extract_tables():
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                tables.append(df)

    if tables:
        combined = pd.concat(tables, ignore_index=True)
        combined.to_csv("extracted.csv", index=False)
```

**Get document metadata:**

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
info = reader.metadata
print(f"Title: {info.title}, Author: {info.author}, Pages: {len(reader.pages)}")
```

### Combine & Split Documents

**Merge multiple PDFs:**

```python
from pypdf import PdfWriter, PdfReader

output = PdfWriter()
for filename in ["part1.pdf", "part2.pdf", "part3.pdf"]:
    reader = PdfReader(filename)
    for page in reader.pages:
        output.add_page(page)

with open("combined.pdf", "wb") as f:
    output.write(f)
```

**Split into individual pages:**

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("multipage.pdf")
for idx, page in enumerate(reader.pages, 1):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{idx}.pdf", "wb") as f:
        writer.write(f)
```

**Extract specific page range:**

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages[4:10]:  # Pages 5-10 (0-indexed)
    writer.add_page(page)

with open("excerpt.pdf", "wb") as f:
    writer.write(f)
```

### Page Manipulation

**Rotate pages:**

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("sideways.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.rotate(90)  # 90, 180, or 270 degrees clockwise
    writer.add_page(page)

with open("rotated.pdf", "wb") as f:
    writer.write(f)
```

**Add watermark overlay:**

```python
from pypdf import PdfReader, PdfWriter

watermark = PdfReader("watermark.pdf").pages[0]
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as f:
    writer.write(f)
```

**Encrypt with password:**

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

writer.encrypt(user_password="viewonly", owner_password="fullaccess")

with open("secured.pdf", "wb") as f:
    writer.write(f)
```

### Create New PDFs

**Simple text document:**

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("output.pdf", pagesize=letter)
width, height = letter

c.setFont("Helvetica-Bold", 24)
c.drawString(72, height - 72, "Document Title")

c.setFont("Helvetica", 12)
c.drawString(72, height - 120, "Content goes here.")

c.save()
```

**Multi-page report with styles:**

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
content = []

content.append(Paragraph("Annual Report", styles['Title']))
content.append(Spacer(1, 24))
content.append(Paragraph("Executive summary text here.", styles['Normal']))
content.append(PageBreak())
content.append(Paragraph("Section 2", styles['Heading1']))
content.append(Paragraph("Detailed content.", styles['Normal']))

doc.build(content)
```

### OCR Scanned Documents

**Extract text from image-based PDFs:**

```python
from pdf2image import convert_from_path
import pytesseract

pages = convert_from_path("scanned.pdf", dpi=300)
full_text = []

for idx, page_img in enumerate(pages, 1):
    text = pytesseract.image_to_string(page_img)
    full_text.append(f"--- Page {idx} ---\n{text}")

print("\n".join(full_text))
```

### Form Handling

PDF forms come in two types: **interactive** (fillable fields) and **static** (visual forms requiring annotation).

#### Check Form Type

```python
from pypdf import PdfReader

reader = PdfReader("form.pdf")
fields = reader.get_fields()

if fields:
    print("Interactive form detected")
    for name, field in fields.items():
        print(f"  {name}: {field.get('/FT', 'unknown type')}")
else:
    print("Static form - use annotation method")
```

#### Fill Interactive Forms

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("form.pdf")
writer = PdfWriter()
writer.append(reader)

writer.update_page_form_field_values(
    writer.pages[0],
    {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com"
    }
)

with open("filled.pdf", "wb") as f:
    writer.write(f)
```

#### Fill Static Forms (Annotation Method)

For forms without interactive fields, see `references/static-forms.md` for the visual annotation workflow.

## Command Line Tools

```bash
# Extract text (poppler-utils)
pdftotext document.pdf output.txt
pdftotext -layout document.pdf output.txt  # Preserve formatting

# Merge with qpdf
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf document.pdf --pages . 1-5 -- first_five.pdf

# Rotate
qpdf document.pdf rotated.pdf --rotate=+90:1-3  # Rotate pages 1-3

# Remove password
qpdf --password=secret --decrypt locked.pdf unlocked.pdf

# Extract images (poppler-utils)
pdfimages -j document.pdf images/prefix
```

## Dependencies

| Package | Purpose | Install |
|---------|---------|---------|
| pypdf | Read/write/merge/split | `pip install pypdf` |
| pdfplumber | Text/table extraction | `pip install pdfplumber` |
| reportlab | Create PDFs | `pip install reportlab` |
| pdf2image | Convert to images | `pip install pdf2image` |
| pytesseract | OCR | `pip install pytesseract` + Tesseract binary |
| pandas | Table processing | `pip install pandas` |

System tools: `poppler-utils` (pdftotext, pdfimages), `qpdf`, `tesseract-ocr`

## Quick Reference

| Task | Tool | Key Method |
|------|------|------------|
| Read text | pdfplumber | `page.extract_text()` |
| Read tables | pdfplumber | `page.extract_tables()` |
| Merge | pypdf | `PdfWriter.add_page()` |
| Split | pypdf | Iterate `reader.pages` |
| Rotate | pypdf | `page.rotate(degrees)` |
| Create | reportlab | `Canvas` or `SimpleDocTemplate` |
| Fill forms | pypdf | `update_page_form_field_values()` |
| OCR | pytesseract | `image_to_string()` |

## References

- `references/static-forms.md` - Workflow for filling non-interactive forms using visual annotation
