# Professional Claude Code Usage Guide

A practical reference for using Claude Code effectively while maximizing learning. Tailored for intermediate developers working on Django projects.

---

## Table of Contents

1. [Core Mental Model](#1-core-mental-model)
2. [Context Management](#2-context-management)
3. [Agent Strategy](#3-agent-strategy)
4. [Plan Mode Workflow](#4-plan-mode-workflow)
5. [Learning-First Patterns](#5-learning-first-patterns)
6. [Effective Prompting](#6-effective-prompting)
7. [Productivity Features](#7-productivity-features)
8. [Common Mistakes to Avoid](#8-common-mistakes-to-avoid)
9. [Django-Specific Workflows](#9-django-specific-workflows)
10. [Quick Reference Card](#10-quick-reference-card)

---

## 1. Core Mental Model

Claude Code operates in a repeating loop: **gather context → take action → verify results**. It chains tool calls together autonomously — reading files, running commands, editing code — until the task is done or it needs your input.

### The #1 Resource: Context Window

Your entire conversation lives in one context window — every message, every file read, every command output. As it fills up, performance degrades. **Managing context is the single most important skill.**

Track usage:
- `/context` — visual grid showing what's consuming space
- `/cost` — token usage statistics

### You Are Part of the Loop

- Press `Esc` anytime to stop generation and redirect
- Press `Ctrl+C` to cancel completely
- You approve or deny every tool call (unless auto-accepted)

---

## 2. Context Management

### CLAUDE.md Hierarchy

Rules load from multiple locations (all are additive):

| Location | Scope | Commit to git? |
|---|---|---|
| `~/.claude/CLAUDE.md` | All your projects | No |
| `./CLAUDE.md` | This project | Yes |
| `./.claude/CLAUDE.md` | This project (alternative) | Yes |
| `./CLAUDE.local.md` | This project, personal | No (gitignore) |

**What to include:** Build commands, code style rules, architecture decisions, repo conventions.
**What to exclude:** Anything Claude can figure out from the code itself.

### Techniques to Keep Context Clean

**Between unrelated tasks:**
```
/clear
```
Resets the conversation completely. Use this every time you switch topics.

**During a long session:**
```
/compact                              # auto-summarize everything
/compact focus on the model changes   # guided — keeps what matters
```

**Offload exploration to subagents:**
```
Use a subagent to investigate how the enrollment system works,
then summarize findings in 3-5 bullet points
```
The subagent does all the file reading in its own context. Only the summary returns to yours.

**Rule of thumb:** If you've been working for 20+ minutes on different things, `/compact` or `/clear`.

---

## 3. Agent Strategy

### Agent Types

| Agent | Speed | Can Edit? | Best For |
|---|---|---|---|
| **Explore** | Fast (uses Haiku) | No | Codebase research, finding patterns |
| **Plan** | Normal | No | Designing implementation before coding |
| **General-purpose** | Normal | Yes | Complex multi-step tasks |
| **Bash** | Normal | Bash only | Running commands in isolated context |

### How Many Agents to Run

| Situation | Agents | Why |
|---|---|---|
| Small, focused task | 0 (do it directly) | No overhead needed |
| Need to understand one area | 1 Explore | Single focused search |
| Multiple unrelated areas to research | 2-3 Explore in parallel | Faster than sequential |
| Complex implementation | 1 Plan agent | Design before coding |

**Maximum practical limit:** 3 parallel agents. More than that and coordination overhead exceeds the benefit.

### When to Parallelize

**Do parallelize:**
- Independent research across different parts of the codebase
- Checking multiple files/patterns simultaneously
- Running tests while exploring related code

**Do NOT parallelize:**
- Tasks that depend on each other's output
- Multiple agents editing the same files (race conditions)
- Simple tasks where one direct search is enough

### Practical Example

```
# Bad: overkill for a simple task
"Launch 3 agents to find where the User model is defined"

# Good: just use Grep directly
"Find the User model definition"

# Good: parallel agents for broad research
"I need to understand the enrollment flow. Use one agent to explore
the courses app models, another to explore the views and URLs,
and a third to check how templates render course data."
```

---

## 4. Plan Mode Workflow

Activate with `Shift+Tab` (cycle modes) or type `/plan`.

In Plan Mode, Claude can only read — no file edits, no commands. This forces thorough research before any changes.

### The 4-Phase Cycle

```
Phase 1: EXPLORE (Plan Mode)
    "Read the courses app and understand how modules are structured"

Phase 2: PLAN (Plan Mode)
    "Create a plan for adding quiz functionality to lessons"
    Claude writes a plan file you can review

Phase 3: IMPLEMENT (Normal Mode — Shift+Tab to switch)
    "Implement the quiz feature from your plan, then run tests"

Phase 4: VERIFY (Normal Mode)
    "Run python manage.py test courses and fix any failures"
```

### When to Use Plan Mode

**Always use for:**
- Changes spanning 3+ files
- Architectural decisions (new models, new apps)
- Refactoring existing code
- Anything you're not sure how to approach

**Skip for:**
- Single-file fixes (typo, obvious bug)
- Adding a log line
- Running a command

### Pro Tip: Edit the Plan

Press `Ctrl+G` to open the plan file in your editor. You can modify Claude's plan before approving it — add constraints, remove steps, change the approach.

---

## 5. Learning-First Patterns

This is the most important section. Using Claude Code to learn, not just to produce code.

### Pattern 1: Explain Before Implementing

```
# Instead of:
"Add a new Course model with these fields: ..."

# Do this:
"Before we add anything, explain how Django model inheritance works.
How does our SoftDeleteModel in core/models.py use it? What are
abstract models vs proxy models vs multi-table inheritance?"

# Then:
"Now let's design the Course model together. Walk me through
each decision — why SoftDeleteModel, why UUIDMixin, why these
specific field types."
```

### Pattern 2: Use /explain on Existing Code

```
/explain core/managers.py

"Why does SoftDeleteManager override get_queryset() instead of
just filtering in the model's Meta? What would break if we did
it differently?"
```

### Pattern 3: The Interview Pattern

Ask Claude to interview YOU about the implementation:

```
"I want to add a payment system. Interview me about the design
decisions. Ask me questions one at a time about:
- What payment provider to use and why
- How to handle failed payments
- Database schema for transactions
- Security considerations

Challenge my answers if they have gaps."
```

This forces you to think through the problem instead of passively receiving a solution.

### Pattern 4: Code Review for Learning

```
/review courses/views.py

"Review this code and for each issue, explain:
1. What the problem is
2. Why it's a problem (what could go wrong)
3. How to fix it
4. The Django principle or pattern behind the fix"
```

### Pattern 5: Git History as a Textbook

```
"Look at the git history of core/models.py. Walk me through
how the architecture evolved across commits. What changed and why?"
```

### Pattern 6: Writer/Reviewer Two-Session Pattern

**Session A (Writer):**
```
"Implement rate limiting for the API endpoints"
```

**Session B (Reviewer) — start a fresh session:**
```
"I just implemented rate limiting. Review the changes on this branch.
Explain what was done, whether it's correct, and what edge cases
might be missing. I want to understand every line."
```

The fresh session gives you an unbiased review and forces you to understand the code through a different lens.

### Pattern 7: Implement It Yourself First

```
"I'm going to implement the enrollment logic myself.
Don't write any code — just watch what I do and tell me
after each step if I'm on the right track, and explain
any Django patterns I'm missing."
```

### Pattern 8: Ask "Why Not?"

After Claude implements something:
```
"Why did you use select_related() here instead of prefetch_related()?
When would prefetch_related() be better? Show me an example of each."
```

### Pattern 9: Spec-Then-Implement

1. **Session 1:** Interview + discuss → write `docs/SPEC-feature-name.md`
2. **Session 2 (fresh):** "Implement the feature described in docs/SPEC-feature-name.md"

You deeply understand the feature from writing the spec. The implementation session is focused and efficient.

---

## 6. Effective Prompting

### Be Specific for Implementation

```
# Vague (Claude might go in wrong direction)
"Fix the login bug"

# Specific (succeeds first try)
"Users report login fails after session timeout. Check accounts/views.py,
especially the token refresh logic. Write a failing test first, then fix.
Run python manage.py test accounts after."
```

### Be Vague for Exploration

```
"What would you improve in this file?"
"How would a senior Django developer structure this differently?"
```

### Always Give Verification Criteria

```
"Implement email validation for the registration form.
Test cases that must pass:
- user@example.com → valid
- user@.com → invalid
- empty string → invalid
- user@@double.com → invalid
Run the tests after implementing."
```

### Reference Existing Patterns

```
"Look at how CourseListView in courses/views.py works,
then create LessonListView following the same pattern."
```

### Delegate, Don't Dictate

```
# Dictating (worse — you do the thinking, Claude just types)
"Go to courses/models.py line 45, add a field called 'duration'
of type IntegerField with default=0"

# Delegating (better — Claude applies expertise, you learn from choices)
"Courses need a duration. Add it to the model.
Explain your choice of field type and any validators."
```

---

## 7. Productivity Features

### Permissions Allowlist

Stop approving the same safe commands repeatedly. Add to `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(python manage.py test*)",
      "Bash(python manage.py makemigrations*)",
      "Bash(python manage.py migrate*)",
      "Bash(black .)",
      "Bash(git status)",
      "Bash(git diff*)",
      "Bash(git log*)"
    ]
  }
}
```

### Hooks: Auto-Format Python After Edits

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "jq -r '.tool_input.file_path // empty' | grep '\\.py$' | xargs black --quiet 2>/dev/null || true"
      }]
    }]
  }
}
```

Every time Claude edits a `.py` file, `black` formats it automatically.

### Hooks: Notification When Claude Needs Input (macOS)

```json
{
  "hooks": {
    "Notification": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "osascript -e 'display notification \"Claude needs attention\" with title \"Claude Code\"'"
      }]
    }]
  }
}
```

### Background Tasks

Start a long-running command and keep working:
```
Run python manage.py test in the background
```
Or press `Ctrl+B` to background a running task. Check with `/tasks`.

### Session Management

```bash
claude --continue          # Resume most recent session
claude --resume            # Pick from recent sessions
/rename enrollment-feature # Name current session
/rewind                    # Undo to a checkpoint
```

### Checkpoints

Every file Claude edits is snapshotted. Press `Esc + Esc` or type `/rewind` to:
- Restore conversation to a previous point
- Restore code to a previous state
- Restore both
- Summarize from a point (partial compaction)

---

## 8. Common Mistakes to Avoid

### The Kitchen-Sink Session
**Problem:** Mixing unrelated tasks in one session. Context fills up, Claude loses track.
**Fix:** `/clear` between unrelated tasks. One session = one focused goal.

### The Correction Loop
**Problem:** Correcting the same mistake 2-3 times. Each correction adds context bloat.
**Fix:** After 2 failed corrections, `/clear` and write a better prompt incorporating what you learned.

### Bloated CLAUDE.md
**Problem:** Adding every rule you can think of. Claude ignores rules buried in walls of text.
**Fix:** Only add rules Claude gets wrong without them. If it does something right by default, don't add a rule for it.

### Passive Acceptance
**Problem:** Claude produces code, you apply it without understanding.
**Fix:** Use the learning patterns from Section 5. Ask "why?" after every implementation. Use `/explain` on code you don't understand.

### Skipping Plan Mode
**Problem:** Jumping into implementation on complex tasks. Claude edits 5 files, something breaks, hard to undo.
**Fix:** Use Plan Mode for anything touching 3+ files. The 2 minutes spent planning saves 20 minutes debugging.

### Infinite Exploration
**Problem:** "Investigate this entire codebase" fills your context with file contents.
**Fix:** Scope narrowly, or delegate to subagents so exploration stays out of your main context.

---

## 9. Django-Specific Workflows

### Starting a New Feature

```
# 1. Enter plan mode
Shift+Tab (until Plan Mode)

# 2. Explore
"Read the courses app and understand the current model structure.
How do Course, Module, and Lesson relate?"

# 3. Plan
"Plan how to add a Quiz model. It should follow our patterns:
SoftDeleteModel, UUIDMixin, SlugMixin. Explain each design decision."

# 4. Switch to normal mode
Shift+Tab

# 5. Implement with learning
"Implement the Quiz model. After each file you edit, explain
what you did and why. Run makemigrations and test after."
```

### Model Changes

```
"Add a 'duration' field to the Course model.
- Explain your field type choice
- Create the migration
- Run python manage.py makemigrations --check to verify
- Run python manage.py test courses
- Format with black ."
```

### Debugging

```
"The enrollment count on the course detail page shows wrong numbers.
Don't fix it yet — first explain what query is running and why
the result might be wrong. Show me the SQL Django generates."
```

### Before Committing

```
/review          # Review your changes
black .          # Format (or let the hook do it)
python manage.py test  # Run tests
```

---

## 10. Quick Reference Card

### Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Esc` | Stop generation (keeps context) |
| `Esc + Esc` | Rewind menu |
| `Ctrl+C` | Cancel completely |
| `Ctrl+G` | Open prompt/plan in text editor |
| `Ctrl+L` | Clear terminal display |
| `Ctrl+B` | Background running task |
| `Shift+Tab` | Cycle: Default → Auto-accept → Plan Mode |
| `@` | File path autocomplete |
| `!command` | Run bash directly |
| `/command` | Slash command / skill |

### Essential Slash Commands

| Command | When to Use |
|---|---|
| `/clear` | Between unrelated tasks |
| `/compact` | Session getting long, need to free context |
| `/context` | Check how full your context window is |
| `/plan` | Enter plan mode |
| `/rewind` | Undo Claude's changes |
| `/explain` | Understand code deeply |
| `/review` | Check code quality before committing |
| `/recap` | Returning to project after time away |
| `/tasks` | Check background tasks |
| `/cost` | See token usage |

### Agent Decision Tree

```
Is the task simple (1-2 files, clear fix)?
  → YES: Do it directly, no agents needed
  → NO: Continue...

Do you need to understand the codebase first?
  → YES: Use 1-3 Explore agents
  → NO: Continue...

Does the task touch 3+ files or involve design decisions?
  → YES: Use Plan Mode (Shift+Tab)
  → NO: Just describe the task and let Claude work

Do you want to learn from the implementation?
  → YES: Add "explain each decision" to your prompt
  → ALWAYS YES: You should always want to learn
```

### The Golden Workflow

```
1. /recap                    (if returning after a break)
2. /clear                    (fresh context)
3. Shift+Tab → Plan Mode     (for non-trivial tasks)
4. Explore the relevant code
5. Review Claude's plan, edit with Ctrl+G
6. Shift+Tab → Normal Mode
7. Implement with "explain your decisions"
8. /review                   (check the result)
9. Ask "why?" about anything you don't understand
10. Test, format, commit
```
