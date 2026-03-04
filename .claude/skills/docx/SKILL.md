---
name: cs-docx
description: Word document processing toolkit. This skill should be used when creating, editing, or analyzing .docx files. Supports document creation with formatting, editing with tracked changes, extracting content, working with comments, and document conversion. Essential for professional, legal, and business document workflows.
---

# Word Document Processing

Toolkit for creating, editing, and analyzing Word documents (.docx format).

## Choosing Your Workflow

| Goal | Approach |
|------|----------|
| **Read content** | Use pandoc for text extraction |
| **Create new document** | Use python-docx or docx-js |
| **Edit existing document** | Use python-docx for simple edits |
| **Professional review** | Use tracked changes workflow |
| **Legal/business edits** | Always use tracked changes |

## Extract Content

**Convert to markdown (preserves structure):**

```bash
pandoc document.docx -o output.md

# Include tracked changes in output
pandoc --track-changes=all document.docx -o output.md
```

**Extract text programmatically:**

```python
from docx import Document

doc = Document("report.docx")

for para in doc.paragraphs:
    print(para.text)

# Get text from tables too
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            print(cell.text)
```

## Create New Documents

### Using python-docx

```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

# Title
title = doc.add_heading("Project Report", level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Body text
doc.add_paragraph("Executive summary goes here.")

# Styled paragraph
para = doc.add_paragraph()
run = para.add_run("Important: ")
run.bold = True
para.add_run("Review all sections before approval.")

# Bullet list
doc.add_paragraph("First item", style="List Bullet")
doc.add_paragraph("Second item", style="List Bullet")

# Table
table = doc.add_table(rows=3, cols=2)
table.style = "Table Grid"
table.cell(0, 0).text = "Name"
table.cell(0, 1).text = "Status"
table.cell(1, 0).text = "Project A"
table.cell(1, 1).text = "Complete"

# Image
doc.add_picture("chart.png", width=Inches(4))

doc.save("report.docx")
```

### Using docx-js (Node.js)

```javascript
const { Document, Packer, Paragraph, TextRun, HeadingLevel } = require("docx");
const fs = require("fs");

const doc = new Document({
  sections: [{
    children: [
      new Paragraph({
        text: "Quarterly Report",
        heading: HeadingLevel.HEADING_1,
      }),
      new Paragraph({
        children: [
          new TextRun({ text: "Status: ", bold: true }),
          new TextRun("In Progress"),
        ],
      }),
    ],
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("report.docx", buffer);
});
```

## Edit Existing Documents

### Simple Text Edits

```python
from docx import Document

doc = Document("existing.docx")

# Find and replace text
for para in doc.paragraphs:
    if "OLD_COMPANY" in para.text:
        for run in para.runs:
            run.text = run.text.replace("OLD_COMPANY", "NEW_COMPANY")

# Modify specific paragraph
doc.paragraphs[0].text = "Updated introduction text."

doc.save("modified.docx")
```

### Add New Content

```python
from docx import Document

doc = Document("existing.docx")

# Append paragraph
doc.add_paragraph("Additional content at the end.")

# Insert after specific heading
for i, para in enumerate(doc.paragraphs):
    if para.text == "Section 2":
        # Insert new paragraph after this one
        new_para = doc.paragraphs[i]._element
        new_p = doc.add_paragraph("New content for Section 2.")._element
        new_para.addnext(new_p)
        break

doc.save("expanded.docx")
```

## Tracked Changes Workflow

For professional document review where edits must be visible and approvable.

### Overview

1. Extract markdown version of document
2. Plan all changes with precise locations
3. Implement changes using OOXML tracked change elements
4. Verify all changes applied correctly

### Implementation

See `references/tracked-changes.md` for detailed OOXML patterns and the Document library API.

**Key principles:**
- Only mark text that actually changed (not entire sentences)
- Use `<w:ins>` for insertions, `<w:del>` for deletions
- Preserve original formatting where text is unchanged
- Group related changes in batches for easier debugging

## Working with Comments

**Read comments:**

```python
from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT

doc = Document("reviewed.docx")

# Access comments through XML
from lxml import etree
comments_part = doc.part.related_parts.get(RT.COMMENTS)
if comments_part:
    comments_xml = etree.parse(comments_part.blob)
    for comment in comments_xml.findall(".//w:comment", namespaces={"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}):
        author = comment.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author")
        text = "".join(comment.itertext())
        print(f"{author}: {text}")
```

**Add comments** (requires OOXML manipulation):

See `references/comments.md` for adding comments via XML.

## Document Conversion

**To PDF:**

```bash
soffice --headless --convert-to pdf document.docx
```

**To images (for visual inspection):**

```bash
# Convert to PDF first
soffice --headless --convert-to pdf document.docx

# Then to images
pdftoppm -jpeg -r 150 document.pdf page
# Creates page-1.jpg, page-2.jpg, etc.
```

**To HTML:**

```bash
pandoc document.docx -o output.html
```

## Document Structure (OOXML)

A .docx file is a ZIP archive containing XML:

```
document.docx (ZIP)
├── word/
│   ├── document.xml     # Main content
│   ├── styles.xml       # Style definitions
│   ├── comments.xml     # Comments
│   └── media/           # Embedded images
├── _rels/
└── [Content_Types].xml
```

**Unpack for direct XML access:**

```bash
unzip document.docx -d unpacked/
```

**Repack after editing:**

```bash
cd unpacked && zip -r ../modified.docx . && cd ..
```

## Dependencies

| Package | Purpose | Install |
|---------|---------|---------|
| python-docx | Create/edit documents | `pip install python-docx` |
| pandoc | Text extraction, conversion | System package |
| docx (npm) | Create documents (JS) | `npm install docx` |
| lxml | XML parsing | `pip install lxml` |
| LibreOffice | PDF conversion | System package |

## Quick Reference

| Task | Tool | Key Code |
|------|------|----------|
| Read text | python-docx | `doc.paragraphs[i].text` |
| Create doc | python-docx | `Document()` + `add_paragraph()` |
| Find/replace | python-docx | Loop through `para.runs` |
| To markdown | pandoc | `pandoc file.docx -o file.md` |
| Tracked changes | OOXML | `<w:ins>`, `<w:del>` elements |
| To PDF | LibreOffice | `soffice --headless --convert-to pdf` |

## References

- `references/tracked-changes.md` - OOXML patterns for tracked changes
- `references/comments.md` - Adding and reading comments via XML
