# Tracked Changes in OOXML

Tracked changes (redlining) allows reviewers to see what was modified in a document.

## XML Elements

| Element | Purpose |
|---------|---------|
| `<w:ins>` | Marks inserted text |
| `<w:del>` | Marks deleted text |
| `<w:delText>` | Contains deleted text content |
| `<w:t>` | Contains regular/inserted text |

## Basic Patterns

### Simple Insertion

```xml
<w:ins w:id="1" w:author="Reviewer" w:date="2024-01-15T10:30:00Z">
  <w:r>
    <w:t>newly added text</w:t>
  </w:r>
</w:ins>
```

### Simple Deletion

```xml
<w:del w:id="2" w:author="Reviewer" w:date="2024-01-15T10:30:00Z">
  <w:r>
    <w:delText>removed text</w:delText>
  </w:r>
</w:del>
```

### Replacement (Delete + Insert)

Changing "30 days" to "60 days" in "The term is 30 days."

```xml
<w:r><w:t>The term is </w:t></w:r>
<w:del w:id="1" w:author="Reviewer" w:date="2024-01-15T10:30:00Z">
  <w:r><w:delText>30</w:delText></w:r>
</w:del>
<w:ins w:id="2" w:author="Reviewer" w:date="2024-01-15T10:30:00Z">
  <w:r><w:t>60</w:t></w:r>
</w:ins>
<w:r><w:t> days.</w:t></w:r>
```

## Best Practice: Minimal Edits

**Wrong** - replacing entire sentence:

```xml
<w:del><w:r><w:delText>The term is 30 days.</w:delText></w:r></w:del>
<w:ins><w:r><w:t>The term is 60 days.</w:t></w:r></w:ins>
```

**Correct** - only mark what changed:

```xml
<w:r><w:t>The term is </w:t></w:r>
<w:del><w:r><w:delText>30</w:delText></w:r></w:del>
<w:ins><w:r><w:t>60</w:t></w:r></w:ins>
<w:r><w:t> days.</w:t></w:r>
```

## Python Implementation

```python
from lxml import etree
import zipfile
import os

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NSMAP = {"w": WORD_NS}

def w(tag):
    return f"{{{WORD_NS}}}{tag}"

def create_insertion(text, author="Claude", change_id=1):
    """Create an insertion element."""
    ins = etree.Element(w("ins"), nsmap=NSMAP)
    ins.set(w("id"), str(change_id))
    ins.set(w("author"), author)

    r = etree.SubElement(ins, w("r"))
    t = etree.SubElement(r, w("t"))
    t.text = text

    return ins

def create_deletion(text, author="Claude", change_id=1):
    """Create a deletion element."""
    delete = etree.Element(w("del"), nsmap=NSMAP)
    delete.set(w("id"), str(change_id))
    delete.set(w("author"), author)

    r = etree.SubElement(delete, w("r"))
    deltext = etree.SubElement(r, w("delText"))
    deltext.text = text

    return delete

def apply_replacement(paragraph_element, old_text, new_text, author="Claude"):
    """Replace text with tracked change."""
    # Find the run containing old_text
    for run in paragraph_element.findall(".//w:r", NSMAP):
        text_elem = run.find("w:t", NSMAP)
        if text_elem is not None and old_text in (text_elem.text or ""):
            full_text = text_elem.text
            before, after = full_text.split(old_text, 1)

            # Clear original text
            text_elem.text = before

            # Add deletion
            deletion = create_deletion(old_text, author)
            run.addnext(deletion)

            # Add insertion
            insertion = create_insertion(new_text, author)
            deletion.addnext(insertion)

            # Add remaining text
            if after:
                remainder = etree.Element(w("r"))
                t = etree.SubElement(remainder, w("t"))
                t.text = after
                insertion.addnext(remainder)

            return True
    return False
```

## Workflow for Document Review

1. **Unpack document:**
   ```bash
   unzip document.docx -d unpacked/
   ```

2. **Parse document.xml:**
   ```python
   tree = etree.parse("unpacked/word/document.xml")
   root = tree.getroot()
   ```

3. **Find target text and apply changes:**
   ```python
   for para in root.findall(".//w:p", NSMAP):
       para_text = "".join(para.itertext())
       if "search term" in para_text:
           apply_replacement(para, "old", "new")
   ```

4. **Save and repack:**
   ```python
   tree.write("unpacked/word/document.xml", xml_declaration=True, encoding="UTF-8")
   ```
   ```bash
   cd unpacked && zip -r ../modified.docx . && cd ..
   ```

## Managing Change IDs

Each tracked change needs a unique ID within the document:

```python
def get_next_change_id(root):
    """Find highest existing change ID and return next."""
    max_id = 0
    for elem in root.iter():
        id_val = elem.get(w("id"))
        if id_val and id_val.isdigit():
            max_id = max(max_id, int(id_val))
    return max_id + 1
```

## Verification

After applying changes, verify with pandoc:

```bash
pandoc --track-changes=all modified.docx -o verify.md
grep "new text" verify.md  # Should find insertions
```
