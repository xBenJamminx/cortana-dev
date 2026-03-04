---
name: cs-doc-collab
description: Collaborative document editing toolkit. This skill should be used when multiple parties need to review, comment on, or co-author documents. Supports tracked changes workflows, comment management, version comparison, and merge strategies for Word documents and markdown files.
---

# Collaborative Document Editing

Toolkit for multi-party document review, tracked changes, and version management.

## Collaboration Workflows

| Scenario | Approach |
|----------|----------|
| **Single reviewer** | Tracked changes in Word |
| **Multiple reviewers** | Separate review copies, then merge |
| **Real-time collaboration** | Use Google Docs/Office 365, export to docx |
| **Technical documents** | Markdown + Git |
| **Legal/contract review** | Formal redlining workflow |

## Word Document Review

### Accept/Reject Changes

```python
from docx import Document

doc = Document("reviewed.docx")

# Accept all changes (flatten document)
# Note: python-docx doesn't directly support this
# Convert through pandoc instead:
```

```bash
# Accept all tracked changes
pandoc --track-changes=accept input.docx -o clean.docx

# Reject all tracked changes
pandoc --track-changes=reject input.docx -o original.docx

# Keep all changes visible
pandoc --track-changes=all input.docx -o with_markup.docx
```

### Compare Versions

```bash
# Generate diff between two versions
pandoc original.docx -o original.md
pandoc revised.docx -o revised.md
diff -u original.md revised.md > changes.diff
```

### Merge Multiple Reviews

When multiple reviewers edit the same document:

1. **Create base version**
   ```bash
   cp original.docx base.docx
   ```

2. **Distribute for review**
   - Send copies to reviewers
   - Each reviewer saves with their name: `review_alice.docx`, `review_bob.docx`

3. **Extract changes from each**
   ```bash
   pandoc --track-changes=all review_alice.docx -o alice_changes.md
   pandoc --track-changes=all review_bob.docx -o bob_changes.md
   ```

4. **Manual merge**
   - Review each set of changes
   - Apply accepted changes to master document
   - Resolve conflicts manually

## Comment Handling

### Extract Comments

```python
from docx import Document
from lxml import etree
import zipfile

def extract_comments(docx_path):
    """Get all comments with their anchored text."""
    comments = {}

    with zipfile.ZipFile(docx_path, 'r') as zf:
        # Read comments
        if 'word/comments.xml' in zf.namelist():
            xml = etree.fromstring(zf.read('word/comments.xml'))
            ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

            for comment in xml.findall('.//w:comment', ns):
                cid = comment.get('{%s}id' % ns['w'])
                comments[cid] = {
                    'author': comment.get('{%s}author' % ns['w']),
                    'date': comment.get('{%s}date' % ns['w']),
                    'text': ''.join(comment.itertext()).strip()
                }

    return comments

# Usage
for cid, comment in extract_comments('document.docx').items():
    print(f"[{comment['author']}]: {comment['text']}")
```

### Comments Report

```python
def generate_comment_report(docx_path, output_path):
    """Create markdown report of all comments."""
    comments = extract_comments(docx_path)

    with open(output_path, 'w') as f:
        f.write("# Document Comments\n\n")

        for cid, c in comments.items():
            f.write(f"## Comment by {c['author']}\n")
            f.write(f"*{c['date']}*\n\n")
            f.write(f"> {c['text']}\n\n")
            f.write("---\n\n")
```

## Markdown Collaboration

For technical documents, use markdown with Git:

### Setup

```bash
# Initialize repository
git init
echo "*.docx" >> .gitignore  # Track markdown, not binary

# Create document
echo "# Project Proposal" > proposal.md
git add proposal.md
git commit -m "Initial draft"
```

### Review Process

```bash
# Reviewer creates branch
git checkout -b review/alice

# Make edits
vim proposal.md

# Commit review
git add -A
git commit -m "Alice's review comments"

# Create pull request or merge
git checkout main
git merge review/alice
```

### View Changes

```bash
# See what changed
git diff main..review/alice

# Word-level diff
git diff --word-diff main..review/alice
```

## Version Comparison Tool

```python
import difflib

def compare_documents(file1, file2):
    """Compare two text files and show differences."""
    with open(file1) as f1, open(file2) as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()

    diff = difflib.unified_diff(
        lines1, lines2,
        fromfile=file1, tofile=file2,
        lineterm=''
    )

    return '\n'.join(diff)

def html_diff(file1, file2):
    """Generate HTML diff view."""
    with open(file1) as f1, open(file2) as f2:
        text1 = f1.readlines()
        text2 = f2.readlines()

    differ = difflib.HtmlDiff()
    return differ.make_file(text1, text2)
```

## Conflict Resolution

When changes overlap:

1. **Identify conflicts**
   - Same paragraph edited differently
   - Contradictory changes

2. **Resolution strategies**
   - **Latest wins**: Accept most recent change
   - **Author priority**: Senior reviewer's changes take precedence
   - **Discussion**: Flag for meeting/discussion
   - **Merge**: Combine both changes if compatible

3. **Document decisions**
   ```markdown
   ## Conflict Resolution Log

   ### Section 3.2
   - Alice: Changed "30 days" to "45 days"
   - Bob: Changed "30 days" to "60 days"
   - Resolution: Accepted Bob's change (per legal review)
   ```

## Review Checklist Template

```markdown
# Document Review Checklist

## Reviewer: _______________
## Date: _______________

### Content
- [ ] Accuracy of facts and figures
- [ ] Completeness of information
- [ ] Logical flow and structure
- [ ] Appropriate tone for audience

### Formatting
- [ ] Consistent heading styles
- [ ] Proper numbering/bullets
- [ ] Tables and figures clear
- [ ] Page breaks appropriate

### Language
- [ ] Grammar and spelling
- [ ] Jargon explained
- [ ] Active voice preferred
- [ ] Concise sentences

### Compliance (if applicable)
- [ ] Legal requirements met
- [ ] Brand guidelines followed
- [ ] Accessibility standards
- [ ] Citation format correct

## Comments Summary
[List major feedback items here]
```

## Best Practices

1. **Clear naming**: `document_v1_draft.docx`, `document_v2_alice_review.docx`
2. **Track everything**: Use tracked changes for professional documents
3. **Single source of truth**: Designate one master document
4. **Regular checkpoints**: Save versions at key milestones
5. **Comment over rewrite**: Explain reasoning in comments
