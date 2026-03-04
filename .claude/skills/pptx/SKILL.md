---
name: cs-pptx
description: PowerPoint presentation toolkit. This skill should be used when creating, editing, or analyzing .pptx files. Supports creating presentations from scratch with design guidance, editing existing slides, extracting content, working with templates, and converting to images. Includes curated color palettes and layout recommendations.
---

# PowerPoint Processing

Toolkit for creating, editing, and analyzing presentations (.pptx format).

## Workflow Selection

| Goal | Approach |
|------|----------|
| **Extract content** | Use markitdown or raw XML |
| **Create from scratch** | Use python-pptx |
| **Edit existing** | Use python-pptx or OOXML |
| **Use template** | Load template, modify content |
| **Visual inspection** | Convert to images |

## Extract Content

**Text extraction:**

```bash
python -m markitdown presentation.pptx
```

**Programmatic access:**

```python
from pptx import Presentation

prs = Presentation("deck.pptx")

for slide_num, slide in enumerate(prs.slides, 1):
    print(f"--- Slide {slide_num} ---")
    for shape in slide.shapes:
        if hasattr(shape, "text"):
            print(shape.text)
```

## Create New Presentations

### Design First

Before coding, decide on:

1. **Color palette** (3-5 colors)
2. **Font pairing** (heading + body)
3. **Layout style** (minimal, dense, asymmetric)

### Using python-pptx

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RgbColor
from pptx.enum.text import PP_ALIGN

prs = Presentation()
prs.slide_width = Inches(13.333)  # 16:9 widescreen
prs.slide_height = Inches(7.5)

# Title slide
layout = prs.slide_layouts[6]  # Blank layout
slide = prs.slides.add_slide(layout)

# Add title shape
title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12), Inches(1.5))
title_frame = title_box.text_frame
title_para = title_frame.paragraphs[0]
title_para.text = "Quarterly Report"
title_para.font.size = Pt(44)
title_para.font.bold = True
title_para.alignment = PP_ALIGN.CENTER

# Add subtitle
sub_box = slide.shapes.add_textbox(Inches(0.5), Inches(4), Inches(12), Inches(0.75))
sub_frame = sub_box.text_frame
sub_para = sub_frame.paragraphs[0]
sub_para.text = "Q4 2024 Results"
sub_para.font.size = Pt(24)
sub_para.alignment = PP_ALIGN.CENTER

prs.save("presentation.pptx")
```

### Add Content Slides

```python
# Content slide with bullets
slide = prs.slides.add_slide(prs.slide_layouts[6])

# Heading
heading = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12), Inches(1))
heading.text_frame.paragraphs[0].text = "Key Highlights"
heading.text_frame.paragraphs[0].font.size = Pt(32)
heading.text_frame.paragraphs[0].font.bold = True

# Bullet points
bullets = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(6), Inches(5))
tf = bullets.text_frame
tf.word_wrap = True

points = ["Revenue up 15% YoY", "New market expansion", "Cost reduction initiatives"]
for i, point in enumerate(points):
    if i == 0:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.text = f"• {point}"
    p.font.size = Pt(20)
    p.space_after = Pt(12)
```

### Add Images and Charts

```python
# Image
slide.shapes.add_picture("chart.png", Inches(7), Inches(1.5), width=Inches(5.5))

# Table
rows, cols = 4, 3
table = slide.shapes.add_table(rows, cols, Inches(1), Inches(2), Inches(8), Inches(3)).table

# Set headers
table.cell(0, 0).text = "Product"
table.cell(0, 1).text = "Q3"
table.cell(0, 2).text = "Q4"

# Fill data
data = [("Widget A", "$1.2M", "$1.4M"), ("Widget B", "$800K", "$950K"), ("Widget C", "$600K", "$720K")]
for row_idx, (product, q3, q4) in enumerate(data, 1):
    table.cell(row_idx, 0).text = product
    table.cell(row_idx, 1).text = q3
    table.cell(row_idx, 2).text = q4
```

## Edit Existing Presentations

```python
from pptx import Presentation

prs = Presentation("existing.pptx")

# Modify specific slide
slide = prs.slides[0]

for shape in slide.shapes:
    if hasattr(shape, "text") and "OLD TEXT" in shape.text:
        shape.text_frame.paragraphs[0].text = "NEW TEXT"

# Add new slide at end
new_slide = prs.slides.add_slide(prs.slide_layouts[6])

prs.save("modified.pptx")
```

## Color Palettes

Curated palettes for professional presentations:

| Name | Colors |
|------|--------|
| Corporate Blue | `#1C2833` `#2E4053` `#AAB7B8` `#F4F6F6` |
| Warm Coral | `#5EA8A7` `#277884` `#FE4447` `#FFFFFF` |
| Earth Tones | `#87A96B` `#E07A5F` `#F4F1DE` `#2C2C2C` |
| Bold Contrast | `#292929` `#E33737` `#CCCBCB` `#FFFFFF` |
| Luxury Gold | `#BF9A4A` `#000000` `#F4F6F6` `#FFFFFF` |
| Modern Teal | `#008080` `#004040` `#E0E0E0` `#FFFFFF` |

## Layout Guidelines

**Slide composition:**
- Keep 0.5" margins minimum
- Title: top 15% of slide
- Content: middle 70%
- Footer/page numbers: bottom 15%

**Text sizing:**
- Titles: 32-44pt
- Body: 18-24pt
- Captions: 12-14pt

**Visual hierarchy:**
- One main message per slide
- 3-5 bullet points maximum
- Images > text when possible

## Convert to Images

```bash
# To PDF first
soffice --headless --convert-to pdf presentation.pptx

# PDF to images
pdftoppm -jpeg -r 150 presentation.pdf slide
```

## Structure (OOXML)

```
presentation.pptx (ZIP)
├── ppt/
│   ├── presentation.xml    # Main metadata
│   ├── slides/             # slide1.xml, slide2.xml...
│   ├── slideLayouts/       # Layout templates
│   ├── slideMasters/       # Master templates
│   ├── theme/              # Colors, fonts
│   └── media/              # Images
└── [Content_Types].xml
```

## Dependencies

| Package | Purpose | Install |
|---------|---------|---------|
| python-pptx | Create/edit presentations | `pip install python-pptx` |
| markitdown | Text extraction | `pip install markitdown` |
| LibreOffice | PDF conversion | System package |

## Quick Reference

| Task | Code |
|------|------|
| New presentation | `Presentation()` |
| Add slide | `prs.slides.add_slide(layout)` |
| Add text | `slide.shapes.add_textbox()` |
| Add image | `slide.shapes.add_picture()` |
| Add table | `slide.shapes.add_table()` |
| Save | `prs.save("file.pptx")` |
