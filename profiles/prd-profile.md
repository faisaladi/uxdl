# UXDL 0.1 — PRD Profile

> **Status:** Optional, non-normative profile. It adds **no syntax** to
> `docs/02_The_Specification.md`. Every key below lives in open `metadata` or in the
> `uxdl_slices` extension, so a document that ignores this profile entirely is still
> valid UXDL 0.1.
>
> **Reference implementation:** `docs/experiments/stpdf_decoupling.uxdl.yaml`
> **Validator:** `scripts/validate_uxdl_prd_profile.py`

## 1. Why this exists

UXDL 0.1 is deliberately open. That openness is correct for the format and a
problem for the tooling: the editor's Overview, Flow and Requirements views can only
show what a document happens to contain, so two equally valid documents produce
wildly different reading experiences.

Observed on two real projects:

| | `stpdf_decoupling.uxdl.yaml` | uxdl.dev's own UXDL |
|---|---|---|
| screens | 10 | 18 |
| element requirements | 39 | 67 |
| slices | 7 (3 journey, 3 story, 1 task) | 1 (task) |
| screens inside any declared scope | 9 / 10 | 2 / 18 |
| relations carrying `path:` | 26 / 26 | 0 / 35 |
| elements carrying `prd_ref` | 46 | 0 |
| Tier 1 profile items missing | **0** | **8** |

Both are structurally valid. The second renders as a near-empty Overview — not
because the tool failed, but because the document has no scope layer, no journeys,
and no traceability. Without a written profile, that outcome reads as a bug.

This profile names the conventions that make a PRD-derived UXDL legible, states what
each one unlocks, and stays advisory so the format's openness survives.

## 2. Conformance

- **Core UXDL validity** and **profile conformance** are separate results. Never merge them.
- A missing profile item is **never an error**. It is a finding that predicts an empty section in the editor.
- Tools MUST render unknown keys regardless of this profile (spec §5). No allowlist may decide whether content appears.
- `--strict` mode in the validator fails on missing **Tier 1** items only, for use in CI on documents that opt in.

## 3. Naming decisions

These settle inconsistencies observed across existing documents. Adopt the right-hand column.

| Deprecated | Use | Reason |
|---|---|---|
| `metadata.unspecified_behavior` | `metadata.specification_gaps` | Matches the editor's "Specification gaps" section; clearer to non-authors. |
| `metadata.owners` | `metadata.owner` | Singular key holding a role→person map. |
| `metadata.source_of_truth` as a string | `metadata.source_of_truth` as an **object** | String form cannot carry the PRD link, the epic and related docs separately. |

`source_of_truth` object shape:

```yaml
source_of_truth:
  prd: <url>                  # the authoritative prose document, if one exists
  jira_epic: <key>            # optional
  related:                    # optional list of "Label — url"
    - In-App Ticket Delivery PRD — https://…
  change_policy:              # optional list of authoring rules for this document
    - Put product behavior on the nearest screen, state, action, or relation.
```

### 3.1 Published implementation brief

UXDL remains a behavioral contract, not a prose-PRD replacement. A document intended
for people who have not read its source preserves a **thin, source-backed project
brief** before the detailed behavior:

```yaml
metadata:
  product_brief:
    nutshell: <what is being built, one short paragraph>
    background: <why this work exists>
    target_users:
      <id>:
        description: <who they are in this product context>
        problem: <the source-stated problem>
        desired_outcome: <what success means for them>
    solution: <the proposed product approach>
    design_direction:
      summary: <interaction and experience direction>
      principles: [<source-stated principles>]
      references: [<document paths or URLs>]
    implementation_approach:
      summary: <how the solution is intended to be built>
      references: [<technical documents or code contracts>]
```

Actors and target users are different. An actor is a role participating in behavior;
a target user describes a person, their problem, and desired outcome. Do not turn a
persona into a permission identity or copy research into the contract.

A published brief also needs a top-down delivery plan:

```yaml
metadata:
  delivery_plan:
    <phase_id>:
      name: <human label>
      objective: <observable outcome>
      rationale: <why these slices belong together now>
      slice_refs: [<story_or_task_slice_id>]
      exit_criteria: [<observable checks>]       # current phase
      entry_conditions: [<required evidence>]   # later phase
```

The feature map is derived from `delivery_plan.*.slice_refs` and the referenced
story/task slices. Do not repeat phase data on Screens or build another graph.

Every statement above must come from the source, an approved product decision, or a
linked design/technical contract. When the source does not state the user problem,
design direction, implementation approach, phase objective, rationale, or exit
criteria, add that absence to `metadata.specification_gaps`; never infer strategy to
make the page look complete.

For the stronger engineering-handoff contract, use the backward-compatible
implementation-readiness profile in `docs/73_Implementation_Readiness_Profile.md`.
It preserves compact string requirements while allowing source-backed expanded
requirements and exact, section-level authoritative references. Readiness is
validated and computed by tools; it is not a manually asserted status.

## 4. Tier 1 — required for a legible PRD document

Each item names what it unlocks. Omit one and the corresponding surface is empty.

| Item | Unlocks |
|---|---|
| root `title` | The page title. Without it, every view titles the document with its filename. |
| `metadata.entry_screens` | Entry chips in Overview; root detection in Flow view. |
| At least one slice with **`type: journey`** | The "Start here / User journeys" section — the primary requirement-separation surface. One per named journey in the source. |
| `journey.metadata.flow_hint: {start, goal[]}` | "Trace this journey" seeds Flow view instead of guessing. |
| `journey.acceptance` | The journey's numbered steps, and its coverage anchor. |
| At least one slice with **`type: story` or `type: task`** | The "Delivery slices" table. |
| `delivery.metadata.covers_requirements: ["1.1"]` | The Requirements column; requirement→story traceability. |
| `delivery.coverage.acceptance` | Behavior traceability; definition of done; regression surface. |
| `relation.path` on **every** relation | Branch colouring, route ranking, route naming in Flow view. |
| `metadata.prd_ref` on every screen, action and relation | Traceability back to the source document. Use `prd_ref: inferred` where the source is silent — see §7. |
| `metadata.open_questions` | The "Open questions" panel — what the source flagged. |
| `metadata.specification_gaps` | The "Specification gaps" panel — what modeling found that the source never addressed. **This is the highest-value output of conversion.** |

## 5. Tier 2 — include when the source has them

| Item | Unlocks |
|---|---|
| root `app` | Product badge. |
| `metadata.document_status`, `target_release`, `owner` | Identity strip. |
| `metadata.source_of_truth` | Source links in the identity strip. |
| `metadata.product_brief` | Product context before behavioral detail in a published implementation brief. Legacy flat `background` and `solution` remain renderable source context. |
| `metadata.goals`, `success_metrics` | Collapsed context sections. |
| `metadata.scope` with `phase_1_*` / `phase_2_future` / `out_of_scope` | Broad scope boundaries; keeps deferred work visible. |
| `metadata.delivery_plan` with phase objective, rationale, slice references and gates | Top-down feature map and the reason each delivery phase exists. |
| `metadata.access_and_permissions` with a `matrix` | Renders as a permission table. |
| `delivery.metadata.depends_on: [slice_id]` | Sequencing in the Delivery slices table. |
| `relation.end: true` / `relation.external:` | Explicit terminals and off-product destinations; routes that end naturally. |
| Any object-of-objects with matching key sets | Renders as a matrix table. Use this shape for decision matrices deliberately. |

## 6. Tier 3 — optional

`metadata.branch_class_vocabulary`, `metadata.definitions`,
`metadata.measurement_note`, `slice.tags`, `slice.external_refs`.

## 7. Provenance rules

When converting an existing prose document, every element carries
`metadata.prd_ref` pointing at the section or requirement it came from:

```yaml
metadata:
  prd_ref: "req 1.3"            # or "§7 Design", or "§6 Journey — Ops"
```

Where a surface cannot exist without an element the source never mentions — a
confirmation dialog implies a dismiss path, a panel implies a close — mark it:

```yaml
metadata:
  prd_ref: inferred
  note: A confirmation dialog implies a dismissal path. Not described in the source.
```

**Every `inferred` element must also appear in `metadata.specification_gaps`.**
Invention becomes visible rather than hidden. Two inferred elements in a
10-screen document is healthy; twenty means the source is far less complete than
it appears, which is itself the finding.

## 8. Recommended `relation.path` vocabulary

`02_The_Specification.md` §10 lists `happy | error | edge | fallback`. Observed
fixtures also use `guard`, `cancel` and `retry`. The recommended set is:

| Value | Meaning |
|---|---|
| `happy` | Intended forward progress. |
| `guard` | A precondition, permission check or confirmation intercepts the action. |
| `error` | A validation or execution failure. |
| `retry` | An automatic or manual retry of a failed step. |
| `cancel` | The actor dismisses without applying a change. |
| `edge` | A valid but non-primary case. |
| `fallback` | An alternative route to the same outcome. |

The field remains free text. Unrecognised values must render, not fail. Declare
project-specific values in `metadata.branch_class_vocabulary`.

## 9. Slice conventions

**Journeys describe traversal. Stories and tasks describe delivery scope.** Never
merge them; a document needs both.

```yaml
journey_<actor>_<goal>:          # journey_ops_configure_delivery
  type: journey
  name: "Journey — <actor> <does what>"
  actor: <actor_id>
  intent: >-
    <the outcome, one sentence>
  screens: [<anchor screens>]
  acceptance:                    # the numbered steps from the source narrative
    <step_id>: <statement>
  coverage:
    generated_from_revision: <n>
    acceptance:
      <step_id>: [<uxdl addresses>]
  metadata:
    prd_ref: "<source section>"
    flow_hint:
      start: <screen_id>
      goal: [<screen_id>]
```

```yaml
<st_n>_<slug>:                   # st_1_backend_decoupling
  type: story                    # or task
  name: "ST-1 — <scope summary>"
  actor: <actor_id>
  intent: >-
    <what this story delivers>
  prerequisites: {<id>: <statement>}
  screens: [<anchor screens>]
  acceptance: {<criterion_id>: <statement>}
  coverage:
    generated_from_revision: <n>
    acceptance: {<criterion_id>: [<uxdl addresses>]}
  external_refs:
    - {provider: jira, id: <KEY>, relationship: implements}
  metadata:
    prd_ref: "<source requirement>, <source story-split section>"
    covers_requirements: ["1.1"]
    depends_on: [<slice_id>]
```

**Numbering.** Do not number screens, actions or relations — the dotted address is
the identifier and it survives reordering. Numbers live only where the source
already has them: story IDs in the slice name, source requirement numbers in
`covers_requirements`. Acceptance criterion IDs are stable `snake_case` words, never
decimals.

## 10. Requirement placement

- An atomic requirement goes on the **nearest** element it constrains — screen, state, action, or relation.
- Cross-cutting actor intent and multi-element criteria go on the **slice**.
- Never copy a slice criterion into every affected element. Coverage makes it visible from there.
- Permission rules go in the owning action's `metadata.requirements`, not into an invented `access_denied` state.

### 10.1 Implementation-ready requirements

Compact strings remain valid. When an obligation needs implementation context, the
nearest constrained element may carry an expanded requirement object. Its
`statement` is the obligation; optional `rationale`, `verification`,
`guidance_refs`, `source_ref`, `provenance`, and source-backed `priority` preserve
the evidence without moving design or technical detail into every requirement.

`guidance_refs` resolve through the project-level `metadata.authoritative_references`
registry. A reference names its stable ID, type, label, workspace-relative path or
external URL, exact heading/section, and whether that section is embedded in the
published artifact. Local Markdown sections are transcluded deterministically;
remote URLs are never fetched during rendering. Missing or unsafe references are
visible findings, never silently dropped content. The full compatibility and
consumer-parity rules live in `docs/73_Implementation_Readiness_Profile.md`.

## 11. What not to model

| Do not | Instead |
|---|---|
| Invent a state to fill a template slot | Leave it out and record the absence in `specification_gaps`. |
| Create an `access_denied` state because a permission matrix exists | Put the permission in the action's `metadata.requirements`. A matrix is not a UI spec. |
| Model Phase 2 / future screens that do not exist | Record them in `metadata.scope.phase_2_future`. |
| Create a fake screen for a third-party or infrastructure step | Use `relation.external:` for off-product hops, `screen.type: system` for a backend job or provider-owned surface. |
| Restate behavior owned by another document | Model the screen, set `metadata.owned_by`, and leave its internals out. |
| Number elements to mirror the source's requirement numbering | Use `covers_requirements` and `prd_ref`. |

## 12. Advisory checks

The validator reports, and none of these are errors:

- Tier 1 items missing, each with the surface it would have populated.
- Deprecated key names in use (§3).
- Relations without `path:`, as a percentage.
- No `end:` or `external:` anywhere — no route terminates naturally.
- Screens in no slice anchor and no coverage — outside all declared scope.
- Relations walked by no journey — branches no narrative in the source describes.
- Coverage addresses that do not resolve.
- Count of `prd_ref: inferred` elements versus entries in `specification_gaps`.

## 13. Adoption boundary

This profile earns its place only if it:

- makes a converted PRD readable without the source document open;
- lets a reader identify the user, problem, product approach, delivery objective and
  feature scope before reading detailed behavior;
- produces `specification_gaps` findings that change a refinement conversation;
- gives engineers a definition of done they trust more than an AC paragraph;
- costs less to maintain than the prose document it supplements.

If authors ignore journeys and coverage, or prefer sending the prose PRD straight
to engineering, keep UXDL as a behavior format and do not expand the profile.
