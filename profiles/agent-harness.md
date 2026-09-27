# UXDL-First AI Agent Development Harness

> **Status:** Initial operating contract for review and incremental automation.
> The objective is reliable product implementation with the smallest capable
> model, not maximum agent autonomy.

## 1. Objective

Use UXDL as the canonical product-behavior input for software delivery while
giving implementation agents only the context they need. A frontier reasoning
agent should spend time on ambiguous product, design, format, architecture, and
security decisions. Once those decisions are frozen into a bounded task contract,
a lighter model should be able to implement or test them without reinterpreting
the whole product.

The harness optimizes for:

- traceability from product behavior to code and tests;
- smaller context and lower token use for bounded workers;
- explicit stop conditions instead of plausible invention;
- reproducible validation and review;
- safe coordination across specification and application work areas in one
  private monorepo.

It does not assume that valid YAML guarantees a complete or correct product.

## 2. Contract hierarchy

Agents use these sources in order:

1. `agents.md` — operating and safety rules;
2. one claimed `Tasks/*.md` file — execution authority and scope;
3. `examples/team-workspace/uxdl.project.yaml` plus its declared modules — editable canonical
   product behavior;
4. `examples/team-workspace/uxdl.project.yaml` — active generated single-file
   projection, never a hand-edited source;
5. `uxdl.dev/design.md` — approved interaction and presentation decisions;
6. linked technical/security/testing documents — implementation constraints;
7. current source code and tests — implementation state, never product authority.

When sources conflict, the worker stops. It does not choose the convenient source.
The thinker reconciles the conflict before implementation resumes.

## 3. Monorepo work-area boundaries

| Work area | Path | Owns |
| --- | --- | --- |
| Specification and operations | workspace root | UXDL standard, canonical product YAML, design/technical contracts, agent harness, tasks, experiments |
| Application | `uxdl.dev/` | Next.js website, editor, application tests, application dependencies |

Both areas belong to the workspace root Git repository. `uxdl.dev/` must not have
its own `.git` directory or be converted into a submodule. A task still identifies
one primary work area so builders receive narrow context and allowed paths.
Cross-area work requires explicit allowed paths but produces one workspace commit.

Run Git commands from the workspace root. Run package, test, build, and development
commands from `uxdl.dev/` so Next.js and test workers use the correct process
context. Task status always lives in the root `Tasks/` directory.

The monorepo remote is private. Publishing the standard to a separate public
repository is a deferred release workflow that requires an explicit allowlist;
application code, internal notes, experiments, tasks, and private operational
documents are excluded unless the owner explicitly approves them.

### 3.1 Generated UXDL artifact placement

When an agent generates UXDL (forward PRD conversion, candidate generation, or observed reverse-projection), it must strictly follow `docs/guides/uxdl-file-placement-and-generation-protocol.md`:

- **Canonical Product (`uxdl.dev`)**: Place in `product/flows/<module>.uxdl.yaml`, declare in `examples/team-workspace/uxdl.project.yaml`, and compile to `examples/team-workspace/uxdl.project.yaml`.
- **External Apps & Experiments**: Place in `docs/experiments/<feature>.uxdl.yaml` (or `docs/experiments/<app_name>/`). Never place in `product/`.
- **Pinned Baselines**: Place in `baseline/<name>.uxdl.yaml` only with verification and cataloging in `baseline/BASELINE.md`.
- **Root Pollution**: Never write `.yaml` files in the repository root or scratch directories.

## 4. Agent roles and capability routing

### 4.1 Thinker — frontier reasoning

Use for:

- product, UXDL format, schema, architecture, security, and experiment decisions;
- requirements with material ambiguity or competing valid approaches;
- cross-cutting changes that affect several product surfaces or repositories;
- decomposition, risk analysis, and task-contract creation;
- final go/no-go or iterate decisions.

The thinker should not consume frontier capacity implementing a deterministic
task once the contract is complete. It creates or refines a `todo` task instead.

### 4.2 Builder — light or standard model

Use a **light** builder only when all light-readiness gates in Section 7 pass. Use
a **standard** builder for bounded work that requires local code reasoning but no
new product or architecture decision.

Builders:

- implement only allowed paths;
- preserve unknown UXDL metadata;
- run listed checks;
- record evidence and deviations;
- stop when the contract is insufficient.

### 4.3 Reviewer — independent model or deterministic tooling

The reviewer compares the diff and evidence with the same frozen task contract.
It does not reward extra scope. Deterministic checks should replace model review
wherever possible.

Use frontier review for security, irreversible migrations, canonical format
changes, and high-impact architecture. A light reviewer can verify mechanical docs,
tests, styling tokens, or bounded component behavior with exact assertions.

### 4.4 Orchestrator

The orchestrator validates readiness, prepares context, dispatches one task per
worker, collects evidence, and stops invalid runs. It must not silently fill an
open product decision merely to keep workers busy.

## 5. Task contract

Every implementation-ready task should declare:

```yaml
status: "todo"
domain: "FE"
assignee: "unassigned"
model_tier: "light"        # light | standard | frontier
task_type: "implementation" # decision | implementation | test | review | docs
primary_repo: "uxdl.dev"    # work-area routing: root | uxdl.dev
risk: "low"                 # low | medium | high
depends_on: ["TASK-ID"]
```

Its body must contain:

1. **Outcome** — one observable result, not a broad theme.
2. **Product contract** — exact slice IDs and UXDL addresses, or an explicit
   statement that the operational task changes no shipping product behavior.
3. **Design and technical contract** — exact approved `design.md` decisions and
   relevant technical sections in one heading; explicitly state when either side
   is not applicable.
4. **Allowed paths** — files or narrow directories the worker may change.
5. **Forbidden scope** — adjacent features that must remain untouched.
6. **Acceptance criteria** — observable and testable statements.
7. **Required checks** — exact commands and browser viewports when relevant.
8. **Stop conditions** — ambiguity, conflicts, missing APIs, unexpected files,
   failing baseline, or required scope expansion.
9. **Handoff evidence** — changed files, checks, screenshots/DOM assertions,
    limitations, and commit SHA when authorized.

Templates live under `.agents/templates/`.

## 6. Scoped UXDL context package

A light worker should not read a 1,000-line product contract and decide what is
relevant. The thinker or a deterministic packager creates:

```text
.agents/context/<task-id>.context.yaml
```

The generated package contains:

```yaml
task_id: internal-task
canonical_source: examples/team-workspace/uxdl.project.yaml # multi-file manifest
source_revision: <git-sha-or-content-hash>
slices: [public_editor_alpha]
addresses:
  - local_editor
  - property_sidebar
requirements: []
dependencies:
  actors: []
  screens: []
  incoming_relations: []
  outgoing_relations: []
design_sections: ["7. Selection and inspector navigation"]
technical_sections: []
unresolved_questions: []
```

The task declares the exact requested scope in frontmatter. Both lists are
required and at least one must be non-empty; IDs and addresses are exact strings,
not search terms. `expected_source_hash` is optional, but when present it must be
the lowercase SHA-256 hash of the canonical file and a mismatch rejects the run.

```yaml
context_scope:
  slices: [public_editor_alpha]
  addresses:
    - local_editor
    - property_sidebar
  expected_source_hash: <optional lowercase sha256>
```

The deterministic packager preserves the selected slice definitions and includes
the screen owners of declared addresses, slice screen anchors, all recursive
screen parents, and one relation hop entering or leaving those seed screens. It
includes the full owned state/action/relation content of those selected screens
and every actor referenced by a selected slice or selected-screen action. It does
not expand generated slice coverage, infer semantic relevance, or traverse a
second relation hop. A missing reference, alias, malformed YAML, duplicate scope
entry, stale expected hash, or unsafe output path rejects the run.

The package is a generated projection, not a second editable PRD. It must include
the source revision, fail when requested IDs are missing, include the minimum
dependency closure, and be regenerated when the generated compatibility source
changes. Workers may quote it, but product changes go back to
`examples/team-workspace/uxdl.project.yaml` and its owning module first.

Until the packager exists, the thinker writes the same scoped fields directly into
the task. Do not compensate by asking every light worker to interpret the full YAML.

## 7. Light-model readiness gate

A task may be marked `model_tier: "light"` only when every answer is **yes**:

| Gate | Question |
| --- | --- |
| Product | Are all required behaviors already explicit in UXDL? |
| Design | Are all relevant interaction and visual decisions approved? |
| Architecture | Does the task use an existing pattern without choosing a new architecture? |
| Scope | Is the outcome bounded to one feature and a narrow allowed-path set? |
| Safety | Does it avoid auth, billing, secrets, destructive data changes, migrations, and security policy? |
| Verification | Are deterministic checks and expected results specified? |
| Reversibility | Is the change easy to review and revert? |
| Baseline | Is the starting test/build state known and passing? |

If any answer is no, route to a standard/frontier task or return it to the thinker.

Typical light tasks:

- extract approved tokens into shared primitives;
- add a bounded component state from an approved design;
- add unit/browser tests for already-defined behavior;
- update deterministic documentation paths or generated examples;
- implement a fully specified CLI with fixtures and exact output.

Never route these to a light model without frontier review:

- new UXDL syntax or validation semantics;
- product completeness or prioritization decisions;
- auth, billing, permissions, privacy, or data migration;
- dependency/library selection;
- changes spanning several unresolved user workflows;
- destructive Git/filesystem operations.

## 8. Execution lifecycle

### Stage A — Think and freeze

1. Classify the request as exploration, decision, implementation, test, or review.
2. Claim the matching task.
3. Resolve product/design/technical questions.
4. Update the editable UXDL project and `design.md` where required.
5. Create bounded worker tasks and mark model tier.
6. Freeze the scoped context revision and baseline checks.

### Stage B — Worker preflight

Before editing, the worker records:

- claimed task and assignee;
- primary work area and workspace-root branch/status;
- required files present;
- context revision matches canonical source;
- baseline checks pass or the exact pre-existing failures;
- no stop condition is already true.

If preflight fails, the run is `INVALID_TASK_CONTEXT`; no implementation begins.

### Stage C — Implement

- Change only allowed paths.
- Use existing patterns and approved UI primitives.
- Do not “improve” adjacent behavior.
- Report a requirement gap instead of inventing a default.
- Keep canonical IDs in tests, accessible names, or trace comments where the task
  specifies them; avoid scattering long UXDL paths through presentation code.

### Stage D — Verify

Run checks in the task from cheapest to most expensive:

1. focused unit tests or validators;
2. type and lint checks;
3. focused integration/browser contract;
4. production build or performance gate when required.

For UI work, verification includes DOM/accessibility assertions and a small fixed
viewport matrix. A pretty screenshot alone is not evidence of behavior.

### Stage E — Review and handoff

The handoff reports:

- outcome against each acceptance criterion;
- changed files and any unexpected file;
- commands and results;
- browser assertions and screenshots when applicable;
- deviations, remaining risk, and whether product/design docs changed;
- workspace commit SHA only when commits were authorized.

The task returns to the thinker if implementation exposes a product decision. It is
marked done only when every required check passes and no unapproved scope remains.

## 9. Fail-closed conditions

Stop without implementation when:

- a task is unclaimed, already assigned, or lacks allowed paths;
- a required UXDL ID/slice is missing, stale, duplicated, or contradictory;
- `design.md` labels a required decision unresolved;
- the request would change product behavior without a canonical UXDL update;
- the workspace Git root and application command working directory are confused;
- baseline validation fails in an affected area and the task does not authorize a
  repair;
- secrets, user data, auth, billing, security, or destructive operations enter a
  light task;
- completing the task requires modifying forbidden paths or installing an
  unapproved dependency.

## 10. Measuring whether the harness works

Track per task:

- model tier and retries;
- input/output tokens when provider telemetry is available;
- context package bytes/lines versus full canonical input;
- first-pass acceptance checks passed;
- defects found in independent review;
- unplanned files changed;
- requirement questions escalated rather than guessed;
- time and cost to accepted completion.

The harness is valuable when lighter workers complete bounded tasks with equal or
better correctness and lower correction cost—not merely when their first response
uses fewer tokens.

## 11. Initial automation backlog

The first automation should be deterministic and separately tasked:

1. validate enriched task frontmatter and required sections;
2. extract a UXDL slice/address dependency closure into a revisioned context pack;
3. verify allowed-path diffs across the correct monorepo work area;
4. run task-declared checks and capture machine-readable evidence;
5. reject stale context before dispatch.

Do not build an autonomous multi-agent platform before these contracts work on a
small set of real editor tasks.
