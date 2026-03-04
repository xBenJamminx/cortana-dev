# Static Form Filling

For PDF forms without interactive fields, text must be added as annotations at specific coordinates.

## Workflow Overview

1. Convert PDF pages to images
2. Identify field locations visually
3. Define field coordinates in JSON
4. Generate filled PDF with annotations

## Step 1: Convert to Images

```python
from pdf2image import convert_from_path

pages = convert_from_path("form.pdf", dpi=150)
for idx, page in enumerate(pages):
    page.save(f"page_{idx + 1}.png", "PNG")
```

## Step 2: Analyze Field Locations

Examine each image and identify:
- **Label text** (e.g., "Name:", "Date:")
- **Entry areas** (blank lines, boxes, or spaces for input)

For each field, determine bounding box coordinates: `[left, top, right, bottom]` in pixels.

### Common Form Patterns

**Inline label with line:**
```
Name: _______________________
```
Entry area: right of label, above the line

**Label above field:**
```
Email Address
_______________________
```
Entry area: between label and line

**Label below line (signature style):**
```
_______________________
Signature
```
Entry area: above the line

**Checkbox:**
```
[ ] I agree to terms
```
Entry area: the small square only (mark with "X")

## Step 3: Create Field Definition

```json
{
  "pages": [
    {"page": 1, "width": 1275, "height": 1650}
  ],
  "fields": [
    {
      "page": 1,
      "name": "full_name",
      "label_box": [72, 200, 150, 220],
      "entry_box": [155, 200, 500, 220],
      "value": "John Smith",
      "font_size": 12
    },
    {
      "page": 1,
      "name": "agree_checkbox",
      "label_box": [90, 400, 200, 420],
      "entry_box": [72, 402, 86, 418],
      "value": "X",
      "font_size": 14
    }
  ]
}
```

## Step 4: Generate Filled PDF

```python
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import json

def fill_static_form(input_pdf, fields_json, output_pdf):
    with open(fields_json) as f:
        config = json.load(f)

    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Group fields by page
    fields_by_page = {}
    for field in config["fields"]:
        pg = field["page"]
        if pg not in fields_by_page:
            fields_by_page[pg] = []
        fields_by_page[pg].append(field)

    for page_num, page in enumerate(reader.pages, 1):
        page_info = next((p for p in config["pages"] if p["page"] == page_num), None)

        if page_num in fields_by_page and page_info:
            # Create annotation overlay
            packet = BytesIO()
            media_box = page.mediabox
            pdf_width = float(media_box.width)
            pdf_height = float(media_box.height)

            c = canvas.Canvas(packet, pagesize=(pdf_width, pdf_height))

            img_width = page_info["width"]
            img_height = page_info["height"]

            for field in fields_by_page[page_num]:
                # Convert image coords to PDF coords
                box = field["entry_box"]
                x = (box[0] / img_width) * pdf_width
                # PDF y=0 is bottom, image y=0 is top
                y = pdf_height - ((box[1] / img_height) * pdf_height)

                font_size = field.get("font_size", 12)
                c.setFont("Helvetica", font_size)
                c.drawString(x, y - font_size, field["value"])

            c.save()
            packet.seek(0)

            # Merge annotation onto page
            from pypdf import PdfReader as OverlayReader
            overlay = OverlayReader(packet)
            page.merge_page(overlay.pages[0])

        writer.add_page(page)

    with open(output_pdf, "wb") as f:
        writer.write(f)

# Usage
fill_static_form("blank_form.pdf", "fields.json", "completed_form.pdf")
```

## Validation

Before generating the final PDF:

1. **Visual check**: Create debug images showing bounding boxes
2. **No overlap**: Entry boxes should not contain label text
3. **Sizing**: Entry boxes must be tall enough for the font size

```python
from PIL import Image, ImageDraw

def visualize_fields(image_path, fields, output_path):
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    for field in fields:
        # Blue for labels
        draw.rectangle(field["label_box"], outline="blue", width=2)
        # Red for entry areas
        draw.rectangle(field["entry_box"], outline="red", width=2)

    img.save(output_path)
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Text misaligned | Coordinate conversion error | Verify image dimensions match PDF |
| Text too high/low | Y-axis direction | PDF origin is bottom-left |
| Text cut off | Box too small | Increase entry_box height |
| Wrong page | Page numbering | Pages are 1-indexed in config |
