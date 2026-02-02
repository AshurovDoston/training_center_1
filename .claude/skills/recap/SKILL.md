---
name: recap
description: Shows a comprehensive summary of recent work - git commits, uncommitted changes, recently modified files, and TODO comments. Use when opening a project after time away to quickly recall what you were working on.
allowed-tools: Bash, Grep, Glob
---

# Project Recap - What Did I Work On?

Generate a quick but comprehensive summary of recent activity in this project.

## Information to Gather and Present

### 1. Current State
Run these commands and summarize the output:
```bash
git branch --show-current
git status --short
```

### 2. Recent Commits (Last 5)
Run and present in a readable format:
```bash
git log --oneline --date=relative --format="%h %ar: %s" -5
```

### 3. Uncommitted Changes
If there are uncommitted changes, show:
```bash
git diff --stat
git diff --cached --stat
```

### 4. Recently Modified Files
Use Glob to find files modified recently (check timestamps), focusing on:
- Python files (`**/*.py`)
- Template files (`**/*.html`)
- Config files

### 5. TODO/FIXME Comments
Use Grep to search for incomplete work markers:
- `TODO`
- `FIXME`
- `XXX`
- `HACK`

## Output Format

Present the information in this structure:

```
## Current Branch: [branch-name]

## Recent Commits
- [hash] [time ago]: [message]
- ...

## Uncommitted Changes
[status summary or "Working directory clean"]

## Recently Modified Files
[list of files with relative modification times]

## Open TODOs
[list of TODO/FIXME comments with file locations, or "None found"]

## Quick Summary
[1-2 sentence natural language summary of what was being worked on based on the above]
```

## Guidelines

- Keep output concise and scannable
- Focus on actionable information
- If no uncommitted changes, say "Working directory clean"
- Group related information together
- The Quick Summary should help the user immediately understand the context
