---
name: review
description: Reviews code for security, performance, maintainability, and Django/Python best practices. Use when someone asks "review this code", "is this code good?", "check this for issues", or wants feedback on code quality.
argument-hint: path/to/file.py or directory to review
allowed-tools: Read, Grep, Glob
---

# Django/Python Code Review

You are a senior developer conducting a thorough code review. Your goal is to identify issues, suggest improvements, and recognize good patterns—all while being constructive and educational.

## Review Output Structure

### 1. Quick Summary
Start with a one-line verdict summarizing the overall code quality.
Example: "Solid implementation with 1 security concern and 2 performance opportunities."

### 2. Severity Overview
Provide a quick visual count of issues found:
```
CRITICAL: X | WARNING: X | INFO: X | PASS: X
```

### 3. Security Review
Check for these Django/Python security concerns:

**Authentication & Authorization**
- [ ] Views have proper `@login_required` or permission decorators
- [ ] Authorization checks before data access (user can only access their own data)
- [ ] No hardcoded secrets, API keys, or passwords

**Input Validation**
- [ ] User input is validated before use
- [ ] No raw SQL queries with string formatting (use parameterized queries or ORM)
- [ ] File uploads validated (type, size, stored outside web root)

**Django Security**
- [ ] CSRF protection not bypassed (`@csrf_exempt` should be rare and justified)
- [ ] No use of `|safe` template filter with untrusted data
- [ ] QuerySet filtering prevents data leakage between users

### 4. Performance Review
Check for these performance concerns:

**Database**
- [ ] No N+1 query problems (use `select_related()` for FK/OneToOne, `prefetch_related()` for M2M/reverse FK)
- [ ] No queries inside loops
- [ ] `.only()` or `.defer()` used when fetching large models with unused fields
- [ ] Appropriate indexes exist for filtered/ordered fields

**Code Efficiency**
- [ ] No unnecessary computations inside loops
- [ ] List comprehensions/generators used appropriately
- [ ] Expensive operations cached when repeated

### 5. Code Quality Review
Check for these maintainability concerns:

**SOLID Principles**
- [ ] Single Responsibility: Functions/classes do one thing
- [ ] No "God objects" with too many responsibilities
- [ ] Dependencies injected rather than hardcoded

**Code Smells**
- [ ] No overly long functions (>30 lines is a smell)
- [ ] No deep nesting (>3 levels is a smell)
- [ ] No duplicate code (DRY violation)
- [ ] No magic numbers/strings (use constants)

**Naming & Readability**
- [ ] Variables/functions have descriptive names
- [ ] Consistent naming conventions (snake_case for Python)
- [ ] Complex logic has explanatory comments

### 6. Django-Specific Review
Check for these Django best practices:

**Models**
- [ ] `__str__` method defined for admin/debugging
- [ ] `Meta.ordering` set if default ordering needed
- [ ] `related_name` set on ForeignKey for reverse lookups
- [ ] Appropriate field types (e.g., `EmailField` not `CharField` for emails)

**Views**
- [ ] Class-based views used appropriately (not overcomplicating simple views)
- [ ] `get_object_or_404` used instead of manual try/except
- [ ] Form validation done in Form class, not view

**QuerySets**
- [ ] `.exists()` used instead of `len(qs) > 0` or `bool(qs)`
- [ ] `.count()` used instead of `len(qs)`
- [ ] Slicing with `[:n]` instead of fetching all then slicing in Python

### 7. Line-by-Line Issues
For each issue found, use this format:
```
Line X: `the problematic code`
→ Issue: Clear description of the problem
→ Severity: CRITICAL | WARNING | INFO
→ Why: Explanation of why this matters
→ Fix: Concrete suggestion for improvement
```

### 8. What's Done Well
Highlight positive patterns found in the code:
- Good practices being followed
- Clean code patterns
- Appropriate use of Django features

### 9. Recommended Actions
Provide a prioritized list of improvements:
1. **[CRITICAL]** Fix X because...
2. **[WARNING]** Consider Y to improve...
3. **[INFO]** Optional: Z would make this cleaner...

---

## Review Guidelines

- **Be constructive**: Explain problems, don't just point them out
- **Prioritize**: Critical security issues > Performance > Code quality > Style
- **Context matters**: Consider if this is production code, a learning project, or a prototype
- **Provide solutions**: Don't just say "this is wrong"—show how to fix it
- **Acknowledge good work**: Developers need positive feedback too
- **Be specific**: Reference line numbers and exact code snippets

## Code to Review

$ARGUMENTS

<!--
=============================================================================
HOW THIS SKILL WORKS (for developers curious about Claude Code skills):
=============================================================================

1. LOCATION: Skills live in `.claude/skills/<name>/SKILL.md`
   This file is at: .claude/skills/review/SKILL.md

2. YAML FRONTMATTER (the part between ---):
   - name: The slash command name (user types /review)
   - description: Helps Claude decide when to use this skill automatically
   - allowed-tools: Security feature - restricts which tools the skill can use
     (this skill can only Read, Grep, and Glob - no editing or bash)

3. $ARGUMENTS PLACEHOLDER:
   When user types `/review courses/models.py`, the $ARGUMENTS above gets
   replaced with "courses/models.py". Claude then reads that file and follows
   the review instructions.

4. THE MARKDOWN BODY:
   Everything between the frontmatter and this comment is the prompt that
   guides Claude's behavior. It's like giving Claude a detailed rubric.

5. TO CREATE YOUR OWN SKILL:
   - Create: .claude/skills/your-skill-name/SKILL.md
   - Add YAML frontmatter with name, description, allowed-tools
   - Write instructions for Claude to follow
   - Use $ARGUMENTS where user input should go
   - Use /your-skill-name to invoke it

Example skill structure:
```
---
name: my-skill
description: When to use this skill
allowed-tools: Read, Grep
---

Instructions for Claude...

$ARGUMENTS
```
=============================================================================
-->
