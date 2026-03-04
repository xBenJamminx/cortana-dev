# Comments in Word Documents

Comments are stored in `word/comments.xml` and referenced from `word/document.xml`.

## Structure

**comments.xml:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:comment w:id="0" w:author="Reviewer" w:date="2024-01-15T10:00:00Z" w:initials="R">
    <w:p>
      <w:r>
        <w:t>Please clarify this section.</w:t>
      </w:r>
    </w:p>
  </w:comment>
</w:comments>
```

**document.xml reference:**

```xml
<w:p>
  <w:commentRangeStart w:id="0"/>
  <w:r><w:t>Text being commented on</w:t></w:r>
  <w:commentRangeEnd w:id="0"/>
  <w:r>
    <w:commentReference w:id="0"/>
  </w:r>
</w:p>
```

## Reading Comments

```python
from lxml import etree
import zipfile

def read_comments(docx_path):
    """Extract all comments from a document."""
    comments = []

    with zipfile.ZipFile(docx_path, 'r') as zf:
        if 'word/comments.xml' in zf.namelist():
            xml_content = zf.read('word/comments.xml')
            root = etree.fromstring(xml_content)

            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

            for comment in root.findall(".//w:comment", ns):
                comments.append({
                    "id": comment.get("{%s}id" % ns["w"]),
                    "author": comment.get("{%s}author" % ns["w"]),
                    "date": comment.get("{%s}date" % ns["w"]),
                    "text": "".join(comment.itertext()).strip()
                })

    return comments

# Usage
for c in read_comments("document.docx"):
    print(f'{c["author"]}: {c["text"]}')
```

## Adding Comments

```python
from lxml import etree
import zipfile
import os
from datetime import datetime

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

def add_comment(unpacked_dir, comment_id, author, text, target_text):
    """Add a comment to specific text in an unpacked document."""

    # 1. Add to comments.xml (create if doesn't exist)
    comments_path = os.path.join(unpacked_dir, "word", "comments.xml")

    if os.path.exists(comments_path):
        tree = etree.parse(comments_path)
        root = tree.getroot()
    else:
        root = etree.Element(f"{{{WORD_NS}}}comments")
        root.set("xmlns:w", WORD_NS)

    # Create comment element
    comment = etree.SubElement(root, f"{{{WORD_NS}}}comment")
    comment.set(f"{{{WORD_NS}}}id", str(comment_id))
    comment.set(f"{{{WORD_NS}}}author", author)
    comment.set(f"{{{WORD_NS}}}date", datetime.now().isoformat())

    p = etree.SubElement(comment, f"{{{WORD_NS}}}p")
    r = etree.SubElement(p, f"{{{WORD_NS}}}r")
    t = etree.SubElement(r, f"{{{WORD_NS}}}t")
    t.text = text

    # Save comments.xml
    tree = etree.ElementTree(root)
    tree.write(comments_path, xml_declaration=True, encoding="UTF-8")

    # 2. Add reference in document.xml
    doc_path = os.path.join(unpacked_dir, "word", "document.xml")
    doc_tree = etree.parse(doc_path)
    doc_root = doc_tree.getroot()

    ns = {"w": WORD_NS}

    # Find target text and wrap with comment markers
    for run in doc_root.findall(".//w:r", ns):
        text_elem = run.find("w:t", ns)
        if text_elem is not None and target_text in (text_elem.text or ""):
            parent = run.getparent()
            run_index = list(parent).index(run)

            # Insert commentRangeStart before run
            start = etree.Element(f"{{{WORD_NS}}}commentRangeStart")
            start.set(f"{{{WORD_NS}}}id", str(comment_id))
            parent.insert(run_index, start)

            # Insert commentRangeEnd and reference after run
            end = etree.Element(f"{{{WORD_NS}}}commentRangeEnd")
            end.set(f"{{{WORD_NS}}}id", str(comment_id))
            parent.insert(run_index + 2, end)

            ref_run = etree.Element(f"{{{WORD_NS}}}r")
            ref = etree.SubElement(ref_run, f"{{{WORD_NS}}}commentReference")
            ref.set(f"{{{WORD_NS}}}id", str(comment_id))
            parent.insert(run_index + 3, ref_run)

            break

    doc_tree.write(doc_path, xml_declaration=True, encoding="UTF-8")
```

## Updating Content Types

If creating comments.xml for the first time, update `[Content_Types].xml`:

```xml
<Override PartName="/word/comments.xml"
          ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>
```

And add relationship in `word/_rels/document.xml.rels`:

```xml
<Relationship Id="rIdComments"
              Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
              Target="comments.xml"/>
```
