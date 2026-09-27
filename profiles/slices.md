# UXDL 0.1 Slices Extension

> **Status:** Optional Phase 0 experiment. This extension does not change the
> UXDL 0.1 core syntax in `02_The_Specification.md`.

## 1. Purpose

A slice connects a familiar natural-language story, journey, task, analysis, or
technical scope to existing UXDL 0.1 behavior.

The initial job is:

> For this story or task, show which behavior matters, what remains ambiguous,
> and what context a human or coding agent needs.

Users should not need to maintain ordered lists of fully qualified relation
addresses. They provide concise intent, prerequisites, screen anchors, and
acceptance criteria. AI and editor tooling propose or maintain exact behavior
coverage for review.

## 2. Compact form

```yaml
extensions:
  uxdl_slices:
    version: "0.1"
    slices:
      cancel_subscription:
        type: story
        name: Cancel Subscription
        actor: workspace_owner
        intent: Stop future renewal while retaining paid access.
        prerequisites:
          signed_in: User is signed in.
          active_subscription: The subscription is active.
        screens: [billing]
        acceptance:
          open_review: Selecting Cancel Subscription opens cancellation_review.
          choose_reason: The user can select a cancellation reason.
          dismiss_review: Dismiss closes cancellation_review without changing the subscription.
          confirm_cancellation: Confirm immediately disables future renewal.
          retain_access: Paid access remains until the current period ends.
          send_email: Send the cancellation email within 10 seconds of confirmation.
```

The compact string is the default acceptance form. Authors do not need YAML
block-scalar syntax such as `>-`.

An individual criterion MAY use expanded form only when it needs additional
context:

```yaml
acceptance:
  send_email:
    statement: Send the cancellation email within 10 seconds of confirmation.
    priority: required
    technical_reference: docs/cancellation-email-rfc.md
```

## 3. Structural vocabulary

### 3.1 Flexible IDs

The following are project-defined IDs and SHOULD use lowercase `snake_case`:

- `cancel_subscription`: slice ID;
- `signed_in`: prerequisite ID;
- `open_review`: acceptance-criterion ID.

Their names and statements are free text.

### 3.2 Standard fields

| Field | Requirement |
| --- | --- |
| `type` | Required free-text classification with recommended values |
| `name` | Required human-readable slice name |
| `actor` | Required for `story` by default; references a declared UXDL actor |
| `intent` | Required for `story`; natural-language outcome |
| `prerequisites` | Optional dictionary of stable IDs to compact statements or expanded objects |
| `screens` | Required non-empty list of declared UXDL screen IDs |
| `acceptance` | Optional dictionary for `story` criteria (supported/round-trippable for v0.1 compatibility; optional narrative/verification context for new authoring) |
| `tags` | Optional list of free-text tags for filtering and organization |
| `external_refs` | Optional project-management or documentation references |
| `coverage` | Optional machine-generated exact UXDL references |
| `metadata` | Optional open context |

Recommended `type` values are:

- `story`;
- `journey`;
- `task`;
- `technical`;
- `analysis`.

Custom values are preserved and SHOULD warn rather than fail core parsing.
Templates MAY require different fields by type. For example, a technical slice
does not need a human actor or product intent.

## 4. Screen anchors, not entry paths

`screens` states where the requirement is initially located or exposed:

```yaml
screens: [billing]
```

It is not an exhaustive list of every screen affected by the story and not a
manually authored navigation path. UXDL 0.1 already describes how screens are
connected.

If the same requirement is available from several screens, list each anchor:

```yaml
screens: [billing, account_settings]
```

The editor may navigate backward and forward from these anchors, resolve
acceptance statements against existing actions and relations, and propose
missing behavior. All affected screens are calculated as coverage rather than
manually repeated in `screens`.

## 5. Requirement ownership and authority

Requirements do not move wholesale into slices. Slices are scopes, lenses, and
traceability mechanisms over behavior, not competing specification authorities.

### The Slice Authority Invariant

> **A Slice scopes, references, and may summarize specification. It must not carry product behavior that has no authoritative home elsewhere.**

- **Atomic/cross-screen observable product behavior** must be authoritative on the nearest applicable Screen / State / Action / Relation `metadata.requirements`, or in an explicitly referenced external authoritative source.
- **Slice acceptance remains supported and round-trippable** for UXDL 0.1 compatibility.
- **Optional narrative / story verification context**: In new authoring workflows, Slice acceptance is treated as optional story-level verification context, not mandatory product specification.
- **Authoring guardrail**: New editor UI must not encourage moving canonical requirements into Slice acceptance.
- **Deterministic compilation**: internal-task Flow compilation derives behavior exclusively from canonical UXDL elements and relations; it must not depend on interpreting Slice acceptance prose.

### Element-level requirements (canonical behavioral truth)

Put an atomic requirement on the nearest screen, state, action, or relation it
constrains:

```yaml
screens:
  billing:
    name: Billing
    metadata:
      requirements:
        show_renewal_date: Show the active plan and renewal date.
    actions:
      start_cancellation:
        metadata:
          requirements:
            owner_only: Only workspace owners may start cancellation.
```

### Slice-level criteria (story scope and verification pointers)

Keep actor intent and criteria that describe the complete story or cross several
elements on the slice:

```yaml
intent: Stop future renewal while retaining paid access.
acceptance:
  retain_access: Paid access remains until the current period ends.
```

Slice acceptance criteria serve as human-readable story summaries and verification
checklists. They do NOT replace element-level requirements or become a second
canonical specification source of truth.

### No duplication rule

Do not copy a slice criterion into every affected element. Generated coverage
and backlinks make it visible from those elements. If one statement can be
owned precisely by one element, prefer element metadata and let the slice refer
to it. Legacy acceptance criteria remain round-trippable for backwards
compatibility, but are never presented as a competing canonical product truth.

## 6. Generated coverage

Coverage is tool-maintained exact traceability. It may be hidden or collapsed
in normal authoring:

```yaml
coverage:
  generated_from_revision: 7
  acceptance:
    open_review:
      - billing.actions.start_cancellation
      - billing.actions.start_cancellation.relations.review_opened
      - cancellation_review
    confirm_cancellation:
      - cancellation_review.actions.confirm_cancellation
      - cancellation_review.actions.confirm_cancellation.relations.success
    retain_access:
      - cancellation_review.actions.confirm_cancellation.relations.success
    send_email:
      - cancellation_review.actions.confirm_cancellation.relations.success
```

Coverage references use the fully qualified addresses already defined by UXDL
0.1. These dot-separated addresses are UXDL conventions, not generic YAML
syntax.

Coverage MAY be omitted from a clean authoring projection, but an approved
portable artifact SHOULD retain enough information to reproduce the mapping or
declare that it requires regeneration.

## 7. Screen inspector aggregation

Selecting a screen should assemble four clearly labeled sources:

1. **Direct requirements:** metadata on the screen.
2. **Owned behavior:** requirements on its states, actions, and outgoing
   relations.
3. **Connected behavior:** relevant incoming relations and their conditions.
4. **Related slices:** prerequisites and acceptance criteria whose anchors or
   generated coverage include the screen or its descendants.

Example:

```text
Billing

Direct requirements
• Show the plan and renewal date.

Action requirements
• Only workspace owners may start cancellation.

Related slice: Cancel Subscription
• Opens cancellation review.
• Confirm disables future renewal.
• Paid access remains until period end.

Linked delivery
• BILL-142 — Cancellation implementation
• MSG-38 — Cancellation email
```

Every item displays its source. Slice-level context must not appear to be direct
screen metadata.

## 8. AI generation and approval

Given a natural-language story, an AI-assisted editor should:

1. create or update one concise slice;
2. split compound acceptance paragraphs into stable atomic criteria;
3. resolve the actor, prerequisites, and screen anchors against existing UXDL;
4. match each criterion to existing screens, states, actions, and relations;
5. propose missing 0.1 elements rather than silently inventing approved
   behavior;
6. show a readable flow and exact coverage diff;
7. ask only material product questions;
8. apply the behavior and coverage changes after approval;
9. regenerate task, test, document, and coding-agent projections from the
   approved slice.

AI should specifically challenge ambiguous language. In the cancellation
example:

- “immediately cancel” may mean disable renewal immediately or remove access;
- “Cancel” inside a confirmation modal may mean Dismiss;
- cancellation reason may be optional or required;
- provider failure and timeout behavior may be missing;
- an email “within 10 seconds” needs a controllable enqueue, provider-acceptance,
  or inbox-delivery definition.

## 9. External tasks and technical work

Slices may carry lightweight external references:

```yaml
external_refs:
  - provider: github
    id: BILL-142
    relationship: implements
  - provider: github
    id: MSG-38
    relationship: enables
```

Project-management tools remain authoritative for assignee, estimate, sprint,
and live status.

Use these boundaries:

- user-visible behavior belongs in UXDL screens, actions, states, relations, and
  slice acceptance;
- backend or third-party effects caused by an interaction belong in the nearest
  action/relation metadata and link to a technical RFC;
- a technical slice may collect multiple affected UXDL elements without
  pretending to be a user story;
- pure infrastructure work with no behavior impact does not require a UXDL
  slice;
- email, push, and in-app notifications may be user-visible surfaces, while
  queue, retry, provider, and delivery mechanics stay in technical documents.

## 10. Validation

Core UXDL 0.1 validation runs first and is unchanged.

Optional slice validation can deterministically check:

- extension version and structural types;
- slice, prerequisite, and acceptance IDs;
- required fields for recognized slice types;
- actor and screen references;
- compact or expanded acceptance values;
- external-reference structure;
- generated coverage references;
- whether coverage revision is stale.

Deterministic warnings may report:

- criterion without approved coverage;
- anchor screen absent from all generated coverage;
- coverage that references a deleted element;
- external task linked to an older approved revision.

Template or AI review remains advisory:

- missing permission-denied, abandonment, failure, timeout, or recovery behavior;
- ambiguous prerequisites;
- compound or untestable acceptance criteria;
- contradictions between local requirements and slice criteria;
- technical SLAs that the product cannot directly guarantee.

`Valid` means the slice and its references are structurally reliable. It does
not mean the story is complete, correct, or ready to build.

## 11. Slice, flow, story, and view

The terms remain distinct:

```text
Slice = the bounded context/scope relevant to a question or work item
Story = a slice type describing actor, intent, and acceptance
Flow  = a deterministic behavioral journey projection derived from UXDL
View  = primary editor projections (Document, Canvas, Flow)
```

In the UXDL Editor architecture:
- `Document`, `Canvas`, and `Flow` are the three primary synchronized top-level views.
- `Slice` is a shared scope filter (a dropdown selector) applied across all three views, NOT a fourth top-level view. Selecting a slice filters/highlights relevant behavior in Document, Canvas, and Flow without creating disconnected data or mutating canonical UXDL truth.

One slice may contain several behavioral paths. Several slices may reference the
same screen without owning or duplicating it.

## 12. Adoption boundary

The slices extension should remain optional until testing shows that it:

- maps natural-language stories onto 0.1 behavior with acceptable correction
  effort;
- makes task scope clearer than a conventional ticket;
- improves coding-agent context retrieval;
- keeps screen-level requirements discoverable;
- handles overlapping stories without confusing users;
- creates enough value to justify maintaining coverage links.

If users do not use slice views or prefer sending the original story directly
to a coding agent, keep UXDL 0.1 as a flow format and do not expand the core.
