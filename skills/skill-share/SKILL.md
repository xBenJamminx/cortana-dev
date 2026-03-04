---
name: cs-skill-share
description: Skill packaging and distribution toolkit. This skill should be used when preparing Claude skills for sharing with others. Provides validation, packaging into distributable ZIP files, and documentation generation for skill distribution.
---

# Skill Packaging & Distribution

Toolkit for validating, packaging, and sharing Claude skills.

## Skill Structure

A valid skill contains:

```
skill-name/
├── SKILL.md           # Required: Main instructions
├── scripts/           # Optional: Executable code
├── references/        # Optional: Reference documentation
└── assets/            # Optional: Templates, images, etc.
```

## SKILL.md Requirements

### Frontmatter

```yaml
---
name: skill-name
description: Clear description of what this skill does and when to use it. Should explain the skill's purpose in third person.
---
```

### Body

- Clear purpose statement
- Usage instructions
- Reference to bundled resources
- Examples where helpful

## Validation

Before sharing, validate the skill:

```python
import os
import yaml
import re

def validate_skill(skill_path):
    """Validate a skill directory."""
    errors = []
    warnings = []

    # Check SKILL.md exists
    skill_md = os.path.join(skill_path, 'SKILL.md')
    if not os.path.exists(skill_md):
        errors.append("Missing SKILL.md")
        return errors, warnings

    # Read and validate frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter format
    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
    else:
        # Extract frontmatter
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])

                # Check required fields
                if 'name' not in frontmatter:
                    errors.append("Frontmatter missing 'name' field")
                elif not re.match(r'^[a-z0-9-]+$', frontmatter['name']):
                    errors.append("Name must be lowercase with hyphens only")

                if 'description' not in frontmatter:
                    errors.append("Frontmatter missing 'description' field")
                elif len(frontmatter['description']) < 50:
                    warnings.append("Description seems short (< 50 chars)")

            except yaml.YAMLError as e:
                errors.append(f"Invalid YAML frontmatter: {e}")

    # Check body content
    body = parts[2] if len(parts) >= 3 else ''
    if len(body.strip()) < 100:
        warnings.append("SKILL.md body seems very short")

    # Check for referenced files
    for ref_type in ['scripts/', 'references/', 'assets/']:
        if ref_type in content:
            ref_path = os.path.join(skill_path, ref_type.rstrip('/'))
            if not os.path.exists(ref_path):
                warnings.append(f"References {ref_type} but directory doesn't exist")

    return errors, warnings

# Usage
errors, warnings = validate_skill('/path/to/skill')
if errors:
    print("ERRORS:", errors)
if warnings:
    print("WARNINGS:", warnings)
if not errors:
    print("Skill is valid!")
```

## Packaging

Create a distributable ZIP file:

```python
import zipfile
import os

def package_skill(skill_path, output_path=None):
    """Package a skill into a ZIP file."""
    skill_name = os.path.basename(skill_path.rstrip('/'))

    if output_path is None:
        output_path = f"{skill_name}.zip"

    # Validate first
    errors, warnings = validate_skill(skill_path)
    if errors:
        raise ValueError(f"Skill validation failed: {errors}")

    # Create ZIP
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # Skip hidden files and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            files = [f for f in files if not f.startswith('.')]

            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.join(
                    skill_name,
                    os.path.relpath(file_path, skill_path)
                )
                zf.write(file_path, arc_name)

    print(f"Packaged: {output_path}")
    return output_path

# Usage
package_skill('/path/to/my-skill')
```

## Documentation Generation

Generate a README for your skill:

```python
import yaml
import os

def generate_readme(skill_path):
    """Generate README.md from skill contents."""

    with open(os.path.join(skill_path, 'SKILL.md'), 'r') as f:
        content = f.read()

    # Parse frontmatter
    parts = content.split('---', 2)
    frontmatter = yaml.safe_load(parts[1])
    body = parts[2].strip()

    # Build README
    readme = f"""# {frontmatter['name']}

{frontmatter['description']}

## Installation

1. Download `{frontmatter['name']}.zip`
2. Extract to your Claude skills directory:
   - **macOS**: `~/Library/Application Support/Claude/skills/`
   - **Windows**: `%APPDATA%\\Claude\\skills\\`
3. Restart Claude Code

## Contents

"""

    # List contents
    for item in ['scripts', 'references', 'assets']:
        item_path = os.path.join(skill_path, item)
        if os.path.exists(item_path):
            files = os.listdir(item_path)
            if files:
                readme += f"### {item}/\n"
                for f in files:
                    readme += f"- `{f}`\n"
                readme += "\n"

    readme += f"""## Usage

{body[:500]}{'...' if len(body) > 500 else ''}

## License

[Specify your license here]
"""

    return readme
```

## Distribution Checklist

Before sharing a skill:

- [ ] SKILL.md has valid frontmatter
- [ ] Description clearly explains when to use
- [ ] All referenced files exist
- [ ] No sensitive data (API keys, credentials)
- [ ] Scripts are tested and working
- [ ] Documentation is clear
- [ ] License is specified
- [ ] Packaged as ZIP with correct structure

## Sharing Options

1. **Direct file share**: Send ZIP file
2. **GitHub**: Create repository with skill
3. **Gist**: For simple, single-file skills
4. **Internal wiki**: For team/company skills

## Installation Instructions

Include these for recipients:

```markdown
## Installing This Skill

1. Download `skill-name.zip`
2. Extract the contents
3. Move the `skill-name` folder to:
   - **macOS**: `~/Library/Application Support/Claude/skills/`
   - **Windows**: `%APPDATA%\Claude\skills\`
   - **Linux**: `~/.config/Claude/skills/`
4. Restart Claude Code (if running)
5. The skill will be available automatically
```
