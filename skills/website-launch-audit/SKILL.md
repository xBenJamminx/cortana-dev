---
name: website-launch-audit
description: Comprehensive pre-launch audit for React, Next.js, and React Native projects. Detects project type automatically and runs appropriate checks for security (exposed secrets, npm vulnerabilities), code quality (TypeScript errors, ESLint, console.logs, TODOs), links (broken internal links, 404s), SEO (meta tags, favicon), accessibility (missing alt text, ARIA labels), forms, and design consistency. For React Native, also checks secure storage usage, responsive design, and app configuration. Use when asked to audit a website, check if a site is ready for launch, find issues before deployment, or review a project for production readiness.
---

# Website Launch Audit

Audit React, Next.js, and React Native projects for launch readiness.

## Usage

Run the audit script on a project directory:

```bash
python scripts/audit.py /path/to/project
```

Save report to file:

```bash
python scripts/audit.py /path/to/project ./audit-report.md
```

## Project Detection

The script auto-detects project type from `package.json`:
- `next` in dependencies → Next.js
- `react-native` in dependencies → React Native  
- `react-dom` in dependencies → React web app

## Checks Performed

### All Projects

| Check | What it finds |
|-------|---------------|
| Secrets | API keys, tokens, connection strings in code |
| Console logs | `console.log/debug/warn/error` left in code |
| TODOs | TODO, FIXME, XXX, HACK comments |
| npm audit | Vulnerable dependencies |
| TypeScript | Type errors (if tsconfig.json exists) |
| ESLint | Linting errors (if configured) |
| Env files | Missing .env.example when .env exists |

### Web Only (Next.js / React)

| Check | What it finds |
|-------|---------------|
| Broken links | Internal hrefs that don't match routes |
| Images | Missing alt attributes |
| Meta tags | Missing title, metadata, favicon |
| Accessibility | Icon buttons without labels, inputs without labels |
| Forms | Forms without onSubmit handlers |
| Design | Excessive hardcoded colors in inline styles |

### React Native Only

| Check | What it finds |
|-------|---------------|
| Secure storage | Sensitive data in AsyncStorage |
| Dimensions | Excessive hardcoded pixel values |
| App config | Missing icon/splash in app.json |

## Report Format

Output is Markdown with:
- Summary (error/warning/info counts)
- List of checks run
- Issues grouped by category
- File:line references for each issue

## Extending

To add custom checks, add a function following this pattern:

```python
def check_custom(project_path: Path, result: AuditResult):
    result.add_check("Custom Check Name")
    
    # Find issues...
    result.add(Issue(
        category="Category Name",
        severity="error",  # or "warning" or "info"
        message="Description of the issue",
        file="relative/path.tsx",  # optional
        line=42  # optional
    ))
```

Then call it from `run_audit()` in the appropriate section.
