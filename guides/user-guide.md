# UXDL for Early Adopters — A Practical Guide

> **Status:** Living document. Written for new users, not for machines.
> **Tone:** Grounded, practical, honest. Like a fellow PM explaining what worked
> and what didn't.

---

## The Golden Rule

> **If it has a stable address, it can be referenced. If it can be referenced, it
> can be validated. If it can be validated, it won't drift.**

Everything in UXDL starts from this idea. Stable IDs for every screen, state,
action, and relation — so your team, your AI tools, and your future self all
reference the same thing.

---

## 1. What UXDL Actually Is

UXDL is a **drag-and-drop flow editor** at `uxdl.dev/editor` — no account
needed. You design screens, add states and actions, connect them visually.

The YAML underneath is just the save file, like a `.fig` file behind Figma or a
`.docx` behind Word. Most users never touch it.

**UXDL is not a replacement for:**
- **Figma** — Figma is for pixel-perfect design. UXDL is for behavior.
- **Notion** — Notion is for writing documents. UXDL is for writing specs that
  machines can also read.
- **Mermaid** — Mermaid draws diagrams. UXDL validates your flow for missing
  states and broken references.
- **Code** — You still need to write code. UXDL tells you and your AI tools what
  to build, not how to build it.

### What it gives you

| If you are | UXDL helps you |
|---|---|
| A PM writing specs | Capture requirements in 80% fewer words. Every screen and action has a stable ID your team can reference. |
| An engineer building from specs | Import validated flows instead of interpreting prose. No more "this is not what the spec said." |
| Someone using AI coding tools | Feed your AI tools exact context (~300 tokens per screen) instead of the full PRD (~14,000 tokens). No more hallucinated screens. |
| A QA tester | Generate test scenarios from every navigation path and error state. |
| Anyone reviewing a PRD | Read a generated document that matches the implementation exactly. Not a Notion doc that went stale after sprint 2. |
| A solo developer | Keep a mental map of 30+ screens without getting lost. Export the flow as a prompt for your AI coding tool. |

---

## 2. When UXDL Actually Helps

### Scenario 1: You're writing a spec for a team of 5+

You write a PRD in Notion. The engineer reads it and interprets it differently.
The QA tester finds a gap you didn't spec. Three sprints later, the spec and the
code describe different products.

UXDL helps because every screen, state, action, and relation has a stable address.
The linter catches missing states before the engineer starts coding. The spec
and the code describe the same thing because they reference the same file.

### Scenario 2: You're using Cursor, Claude Code, or similar

AI coding tools hallucinate when they don't have context. You tell it "build a
billing screen" and it generates one — but without the error state, the loading
state, or the empty state. You catch it in QA, fix it, and the cycle repeats.

UXDL helps because your AI tool can query `uxdl_get_screen("billing")` and get
exactly the screens, states, actions, and relations it needs — ~300 tokens
instead of the full spec. The AI knows what you want because you already wrote
it down.

### Scenario 3: You have a product with 20+ screens

Without a shared format, the spec drifts. You update screen A but forget to
update screen B, which connects to A. Your team works from different versions
of the truth.

UXDL helps because the linter checks every reference. Add a new action to screen
A but forget to update screen B? The linter flags it. Missing an error state on
a screen that handles payments? The linter flags it. The spec stays consistent
because it's validated, not just written.

### Scenario 5: You're a solo developer using AI coding tools

You prompt Cursor with "build a billing page." It generates one — but without the
error state, the loading state, or the empty state. You fix it, move on, and
repeat the cycle on every feature.

You also have no mental map of your project past 5 screens. You add features
organically, and by screen 10 you've forgotten what connects to what.

UXDL helps because:
- **AI context management** — Export the flow as a prompt. Your AI tool knows every
  screen, state, and relation. No more hallucinated screens.
- **Visual map** — Drag-and-drop your screens. See the whole flow at a glance.
  Your app's architecture lives in your editor, not in your head.
- **State linter** — The editor flags missing states (loading, error, empty)
  before you ask the AI to build. No more discovering gaps in QA.

**One-file mode** is all you need. Three minutes to map, one click to export.
Even a 2-screen flow is worth visualizing — you'll spot connections you missed.

### Scenario 4: You're reviewing a PRD (or having yours reviewed)

Without UXDL, reviewing a PRD means reading a Notion doc, checking the tasks in
Linear, and hoping the code matches. Three different sources of truth.

With UXDL, you review one file. The same file generates: a readable Markdown
document, task descriptions, AI context for coding tools, and test scenarios.
They all agree because they come from the same source.

---

## 3. The Four Concepts (30 Seconds)

```yaml
screens:
  sign_in:
    name: Sign In
    type: page
    states:
      default: Ready for input
      invalid_otp: The code is incorrect
    actions:
      submit_otp:
        name: Submit OTP
        relations:
          valid:
            to: home
            when: OTP is correct
          invalid:
            to: sign_in
            state: invalid_otp
            when: OTP is incorrect
```

| Concept | What it is | Example |
|---|---|---|
| **Screen** | A place the user can be | `sign_in`, `dashboard`, `settings` |
| **State** | A meaningful variation of a screen | `default`, `loading`, `error`, `empty` |
| **Action** | Something the user can do | `submit_otp`, `cancel`, `delete_account` |
| **Relation** | Where an action leads, and under what condition | `valid → home`, `invalid → sign_in` |

That's it. Four concepts. If you understand these, you can read and write UXDL.

> 💡 **In the visual editor**, you drag screens onto a canvas and connect them
> visually — no YAML syntax needed. The YAML below is generated automatically.

### What the linter catches

The editor runs checks as you build. Here's what it flags:

```
❌ Missing state: screen "checkout" has action "submit_payment" but no "loading" state
❌ Broken reference: screen "dashboard" action "view_order" → "order_detail" (screen not found)
❌ Orphan screen: "legacy_settings" has no incoming relations from any screen
❌ Unreachable path: relation "expired" on screen "verify_otp" has no corresponding screen
```

These run **in the editor in real time**, not in CI after you've committed. You fix
them as you design, not after someone finds the bug.

---

## 4. How to Organize Your Project

### One file vs. multiple files

**One file (`product.uxdl.yaml`):** Good for small projects (1-5 screens).
Everything in one YAML file. Simple, no setup needed.

**Multiple files (project profile):** Good for larger projects (5+ screens).
Structure:

```
product/
├── uxdl.project.yaml          # Manifest, project metadata, module list
├── flows/
│   ├── auth.uxdl.yaml         # Authentication screens
│   ├── billing.uxdl.yaml      # Payment screens
│   └── editor.uxdl.yaml       # Editor screens
└── slices/
    └── product.slices.uxdl.yaml  # Cross-cutting requirements
```

Each flow file contains screens for one domain. The manifest (`uxdl.project.yaml`)
lists which files are part of the project. The editor composes them into a single
validated document.

### What each part contains

| File | Contains | Example |
|---|---|---|
| `uxdl.project.yaml` | Project identity, metadata, module list | App name, epic, in-scope/out-of-scope |
| `flows/*.uxdl.yaml` | Screens, states, actions, relations | `sign_in`, `submit_otp`, `valid → home` |
| `slices/*.uxdl.yaml` | Cross-cutting stories and tasks | `login_otp`, `billing_flow` |

---

## 6. When NOT to Use UXDL

UXDL is not the right tool for every situation. Here's when to skip it:

| Situation | Why |
|---|---|
| **Pure infrastructure (APIs, databases, no UI)** | UXDL models user-facing flows. If there are no screens, there's nothing to model. |
| **Your team won't adopt a spec tool** | UXDL requires someone to maintain the flow files. The visual editor lowers the barrier, but if no one on the team will maintain the flows, they'll go stale. |
| **Single-use prototype** | If you're building a prototype that will be thrown away, a quick Figma flow is faster. |
| **You need pixel-perfect design specs** | UXDL describes behavior, not layout. Keep Figma for design. |

**For solo developers using AI coding tools:** Even 2 screens benefit from a
visual flow map. The export to AI prompt alone saves more iteration time than
the spec costs. Don't skip it just because you're alone — the AI context
injection is the payoff.

**Rule of thumb:** If you're building something with 3+ screens that will be
maintained for more than one sprint, or if you're using AI coding tools and
tired of hallucinated screens, UXDL will save you time.

---

## 7. Your First 15 Minutes

UXDL is designed to deliver value in minutes, not days. Here's the fastest path:

### Minute 1-2: Open the editor
1. Open `uxdl.dev/editor` — no account needed
2. Pick a template: "Sign In" or "Blank Canvas" (templates save you 5 minutes)

### Minute 3-5: Map your flow
1. Drag 3-5 screens onto the canvas
2. Name them (e.g., `sign_in`, `dashboard`, `settings`)
3. Add at least one state per screen (start with `default`)
4. Add actions and connect them with arrows (relations)

### Minute 6-8: Let the linter help
1. The editor highlights any missing states or broken connections
2. Add a `loading` and `error` state to screens that make API calls
3. Fix any relations that point to screens that don't exist yet

### Minute 9-12: Export and use
1. Click "Copy AI Prompt" — this generates a spec summary you can paste into
   Cursor, Claude Code, or any AI coding tool
2. Paste the prompt and ask the AI to build one screen from the spec
3. See if the result matches what you designed

### Minute 13-15: Iterate
1. Does the AI output match your flow? Add missing screens or states.
2. Re-export and try again. Each iteration takes 30 seconds.

### Going deeper
Once your first flow is working, explore:
- **Templates gallery** — Start from a complete sign-in, checkout, or onboarding flow
- **Multi-file projects** — Split larger products into domain modules
- **MCP integration** — Connect Cursor/Claude Code directly so the AI queries your spec without copy-paste
- **Slices and coverage** — Map acceptance criteria to specific screens and actions

---

## 8. How the Community Can Help

### Share templates

A good template captures a common flow (login, checkout, onboarding) that others
can start from. A good template is 30-50 lines, covers the happy path and the
most common error states, and includes comments explaining the design decisions.

### Report gaps

UXDL is 0.1. There are flows it can't express well yet. When you find one:
- What were you trying to describe?
- How did you try to describe it in UXDL?
- What was missing or awkward?

This is the most valuable feedback you can give. It shapes the format.

### Write custom validation rules

The linter supports custom rules for your domain. For example, if your team
requires every payment screen to have a confirmation step, you can write a rule
that checks for it. Share rules that work well — they might become built-in.

---

## 9. Quick Reference

### Screen fields

| Field | Required | What it does |
|---|---|---|
| `name` | Yes | Human-readable label |
| `type` | No | `page`, `modal`, `drawer`, `panel`, etc. |
| `parent` | No | Host screen for modals/overlays |
| `states` | No | Variations of this screen (loading, error, etc.) |
| `actions` | No | Things the user can do from this screen |
| `metadata` | No | Open context (description, requirements, analytics, etc.) |

### State forms

```yaml
# Compact — for simple cases
states:
  default: Ready for input

# Expanded — when you need more context
states:
  invalid_otp:
    name: Invalid OTP
    metadata:
      message: The code is incorrect or expired.
```

### Requirement forms

```yaml
# Compact — for 90% of cases
requirements:
  otp_expiry: OTP expires after 10 minutes

# Expanded — when you need an external reference
requirements:
  otp_expiry:
    title: OTP expires after 10 minutes
    external_ref: AUTH-42
```

### Coverage

```yaml
coverage:
  generated_from_revision: 4
  acceptance:
    verify_success:
      - otp_verification.actions.verify.relations.success
    handle_expired:
      - otp_verification.actions.verify.relations.expired
```

Coverage is generated by the tool, not written by hand. It maps each acceptance
criterion to the exact UXDL addresses that satisfy it.

---

## 10. Limitations (Honest)

| UXDL can | UXDL cannot |
|---|---|
| Describe product flows with stable IDs | Write code — you still need to build it |
| Validate structural references | Validate content — metadata is free text |
| Generate coverage from acceptance criteria | Generate product decisions — AI proposes, you approve |
| Export Markdown, tasks, and MCP context | Export Figma files, PDFs, or design assets |
| Track versions via Git (plain YAML files) | Provide in-app version history — Git is better at this |
| Scale to 100+ screens | Scale to 10,000+ screens without grouping — you'll need to organize |

UXDL is a tool, not a platform. It does one thing — describe product behavior
with stable addresses — and does it well. It doesn't replace your project
management tool, your design tool, or your code editor. It connects them.

---

## Appendix A: Common Mistakes (and How to Avoid Them)

### Mistake 1: Writing requirements as a list

```yaml
# DON'T — no stable IDs, slices can't reference them
metadata:
  requirements:
    - "OTP expires after 10 minutes"
    - "Max 5 failed attempts"

# DO — each requirement has a stable ID
metadata:
  requirements:
    otp_expiry: OTP expires after 10 minutes
    max_attempts: Max 5 failed attempts before 15-minute lockout
```

**Why it matters:** A slice that references `otp_expiry` always points to the
same requirement, even if the screen is renamed or reordered. A list has no
stable reference — you can only say "the third item," which breaks when items
are added or removed.

### Mistake 2: Using numbers in screen IDs

```yaml
# DON'T — linter rejects this
01_landing_page:
02_docs_center:

# DO — use descriptive names
landing_page:
docs_center:
```

**Why it matters:** Screen IDs are permanent identifiers. If you number them
(`01_landing_page`) and later insert a new screen between 01 and 02, you either
renumber everything (breaking all references) or live with out-of-order numbers.
Descriptive names don't have this problem.

### Mistake 3: Duplicating requirements in slices

```yaml
# DON'T — same text in two places, guaranteed to drift
screens:
  otp_verification:
    metadata:
      requirements:
        otp_expiry: OTP expires after 10 minutes
slices:
  login_otp:
    acceptance:
      handle_expired: OTP expires after 10 minutes  # duplicate!

# DO — slice references the screen-level requirement
screens:
  otp_verification:
    metadata:
      requirements:
        otp_expiry: OTP expires after 10 minutes
slices:
  login_otp:
    acceptance:
      handle_expired:
        title: User can request a new code after expiry
        requirements: [otp_verification.requirements.otp_expiry]
```

**Why it matters:** When the requirement changes (e.g., "OTP expires after 5
minutes"), you change it in one place and the slice automatically picks it up.
If you duplicate it, you'll forget to update one of the copies.

### Mistake 4: Adding status or task fields to requirements

```yaml
# DON'T — status and task drift from reality
metadata:
  requirements:
    otp_expiry:
      title: OTP expires after 10 minutes
      status: done
      task: internal-task

# DO — keep it simple, let coverage track status
metadata:
  requirements:
    otp_expiry:
      title: OTP expires after 10 minutes
      external_ref: internal-task
```

**Why it matters:** `status` is a field that looks like it should be maintained
but will inevitably go stale. Every requirement in the prototype is already
marked `status: done` — which means nobody updates it. Status is better tracked
by whether the requirement has coverage mapping, not by a manually written field.

### Mistake 5: Writing overly verbose requirement IDs

```yaml
# DON'T — slug from the full title, hard to read and reference
do_not_show_yaml_on_first_load_place_files:

# DO — 2-4 meaningful words
hide_yaml_by_default:
```

**Why it matters:** Requirement IDs are reference handles. You'll type them in
slice criteria, coverage mappings, and discussions. Keep them short enough to
remember, descriptive enough to recognize.