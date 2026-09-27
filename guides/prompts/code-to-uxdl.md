# Code-to-UXDL Projection Prompt / Guide

Use this prompt when an agent needs to inspect implementation and produce an **Observed UXDL** projection.

The purpose is to describe current observable behavior, not to infer product intent or rewrite the codebase into UXDL structure.

## Recommended workflow

Run the process in three separate passes:

1. **Desired projection:** PRD/product sources only -> Desired UXDL.
2. **Observed projection:** code/test/runtime sources only -> Observed UXDL.
3. **Reconciliation:** compare the two frozen artifacts by stable behavioral identity.

Do not give the reverse-generation agent the PRD or Desired UXDL during its initial extraction pass. Otherwise the model may reconcile disagreements instead of observing them.

### Storage conventions for Observed UXDL

Per `docs/guides/uxdl-file-placement-and-generation-protocol.md`:
- Save Observed projections as standalone experiments: `docs/experiments/<scope>_observed.uxdl.yaml`.
- Never write observed extraction outputs directly into `product/` or overwrite `examples/team-workspace/uxdl.project.yaml`.
- Run `python3 scripts/validate_uxdl_prd_profile.py docs/experiments/<scope>_observed.uxdl.yaml` before proceeding to reconciliation.

---

## Reusable prompt

```text
You are a codebase-to-UXDL observer.

Your job is to describe CURRENT, OBSERVABLE product behavior implemented by the selected codebase scope using UXDL 0.1 semantics.

This is not a PRD generator and not a design review.

AUTHORITY

- Code/runtime behavior is the authority for CURRENT implementation.
- Do not read or use the PRD, existing Desired UXDL behavior, tickets, or design docs during the initial extraction pass unless they are explicitly supplied as implementation evidence.
- Do not "correct" code to match expected product behavior.
- Do not infer intended behavior from common UX patterns.
- If code is internally contradictory, preserve the contradiction as a finding.
- If behavior cannot be demonstrated from code, tests, routes, runtime evidence, or rendered UI, omit it or mark it Unknown. Do not invent it.

UXDL MAPPING

Use the existing UXDL 0.1 behavioral model:

- screen = user-visible page/modal/drawer/sheet/panel/overlay or meaningful external/system-owned surface
- state = meaningful observable LOCAL variation of a screen
- action = user/system action affecting the experience
- relation = observable result or next behavior after an action
- when = condition proven by implementation evidence
- path = reader classification such as happy, guard, error, edge, fallback, or cancel when supported by behavior
- actor = relevant human/system participant

Do not create UXDL elements for implementation-only concepts such as React hooks, helper functions, component props, stores, API clients, database tables, or internal variables unless they create a distinct observable product boundary.

STATE DISCIPLINE

Do not convert every boolean or variable into a UXDL state.

A code value qualifies as a UXDL screen state only if it materially changes at least one of:
- what the user sees;
- what actions are available;
- the observable result of an action on that surface.

Examples:
- validation error shown on the same modal -> state/variant candidate
- blocked candidate that changes available action -> state/variant candidate
- isOpen, hook loading bookkeeping, internal counters -> not automatically a UXDL state

EVIDENCE DISCIPLINE

Every projected screen and every non-trivial action/relation must have implementation evidence.

Prefer stable evidence anchors in this order:
1. exported component/function/route symbol;
2. file path;
3. test name;
4. runtime event/trace identifier when available;
5. line range only as optional supporting detail.

Do not use line numbers as durable identity because they churn.

Evidence confidence:
- direct: explicitly rendered/handled/branched in code
- corroborated: supported by multiple implementation points, tests, or runtime evidence
- inferred: plausible from structure/naming but not proven; do not promote to canonical behavior without review
- conflict: implementation sources disagree

EXTRACTION PROCEDURE

1. Establish the feature boundary from supplied seed files/symbols.
2. Follow imports/callbacks/routes only far enough to explain observable behavior.
3. Enumerate visible surfaces.
4. For each surface, enumerate meaningful local states.
5. Enumerate user/system actions.
6. Resolve each action to observable relations and conditions.
7. Record external boundaries that materially affect the experience.
8. Deduplicate behavior implemented across several files.
9. Produce findings for contradictions, dead handlers, misleading UI copy, missing gates, or behavior whose result cannot be proven.
10. Do not author product intent, product requirements, or a slice as specification truth.
11. A candidate observed journey may be emitted separately only when it can be deterministically traced from actual relations.

STABLE IDENTITY

If no existing UXDL identity registry is provided:
- create semantic snake_case IDs from observable concepts;
- output an identity-mapping section for later human reconciliation.

If an existing identity registry IS provided:
- it may contain only stable UXDL addresses/names and previously approved implementation bindings;
- reuse an existing identity only when evidence clearly represents the same observable behavior;
- if identity is ambiguous, report UNCERTAIN_IDENTITY rather than silently creating remove/add churn.

ABSTRACTION RULE

Reverse projection is intentionally lossy.

Promote implementation details into UXDL only when they describe observable product behavior.

Example:

Implementation sequence:
setLoading()
fetch()
parse()
setSession()
openReview()

Desired projection:
Submit source -> Processing -> Review

The implementation sequence is evidence. The observable transition is UXDL.

OUTPUT

Return these sections:

1. OBSERVED UXDL

Produce valid UXDL 0.1-shaped YAML describing current observable behavior only.

Add projection metadata such as:

metadata:
  projection:
    kind: observed_code
    source_ref: <commit / branch / workspace ref>
    generated_without_product_spec: true

Add code/test/runtime evidence as projection provenance. Do not convert evidence locations into product nodes.

Do not put PRD acceptance criteria into this artifact.

2. FINDINGS

For every important inconsistency or uncertainty return:
- id
- severity: info | warning | conflict
- stable UXDL address if known
- statement
- implementation evidence
- what remains unknown

A contradiction between UI copy and runtime behavior is a finding. Do not choose one silently.

3. IDENTITY MAP

Map generated UXDL addresses to stable implementation symbols.

Example:

generation_input
  -> generation-input-modal.tsx#GenerationInputModal

generation_input.actions.submit_source
  -> generation-input-modal.tsx#handleSubmit
  -> editor-workspace.tsx#handleSubmitGenerationSource
  -> api/ai/analyze/route.ts#POST

4. CANDIDATE OBSERVED JOURNEYS (OPTIONAL)

Derive only from actual relations.
Do not claim user intent unless intent is explicitly available from implementation evidence.

STOP CONDITIONS

Stop and report uncertainty instead of inventing behavior when:
- target behavior depends on remote configuration not available to the scan;
- two implementation sources contradict each other;
- the feature boundary cannot be resolved safely;
- a semantic identity could map to more than one behavior;
- a product rule is only implied by naming rather than enforced/observable;
- runtime state is necessary to determine which branch is actually active.

Do not inspect PRD / Desired UXDL until this observed artifact and findings list are frozen.
```

---

## Reconciliation prompt

Use only after Desired and Observed artifacts are frozen.

```text
You are reconciling two independently produced projections over the same UXDL behavioral identity space.

INPUT A: Desired UXDL
Authority: approved product behavior / what should happen.

INPUT B: Observed UXDL
Authority: implementation evidence / what can currently be proven.

Do not rewrite either artifact.
Do not rationalize differences.
Do not prefer code simply because it is executable.
Do not prefer product intent simply because it is desired.

For every stable behavioral identity, classify:

- MATCH
- DESIRED_ONLY
- OBSERVED_ONLY
- CONFLICT
- UNCERTAIN_IDENTITY

For each non-MATCH result provide:
- stable UXDL address
- Desired behavior + provenance
- Observed behavior + provenance
- material difference
- possible explanations, clearly marked as hypotheses
- decision required from human/product/engineering

Do not decide whether code or Desired UXDL should change.
```

## First dogfood feature

Initial experiment scope: the UXDL generation/import workflow.

Useful seed files include:

- `uxdl.dev/src/features/editor/components/generation-chooser-modal.tsx`
- `uxdl.dev/src/features/editor/components/generation-input-modal.tsx`
- `uxdl.dev/src/features/editor/components/generation-review-modal.tsx`
- `uxdl.dev/src/features/editor/components/generation-candidate-modal.tsx`
- `uxdl.dev/src/features/editor/components/editor-workspace.tsx`
- `uxdl.dev/src/features/editor/model/generation-session.ts`
- `uxdl.dev/src/features/editor/model/ai-generation-service.ts`
- `uxdl.dev/src/app/api/ai/analyze/route.ts`
- `uxdl.dev/src/app/api/ai/compile/route.ts`

The experiment and architectural findings are documented in:

`docs/decisions/ADR-001-code-to-uxdl-projection.md`

## Quality checklist

Before accepting an Observed UXDL projection, verify:

- [ ] No PRD/Desired UXDL was used during the blind code pass.
- [ ] Every major observed element has implementation evidence.
- [ ] Component hierarchy was not copied into UXDL structure.
- [ ] Internal variables were not promoted to states without observable impact.
- [ ] Error/fallback/cancel behavior was included where explicitly implemented.
- [ ] Contradictions are findings, not silently reconciled.
- [ ] Product intent and rationale were not invented from code.
- [ ] IDs are semantic and stable rather than code-location-derived.
- [ ] Known code bindings reuse existing approved UXDL identities.
- [ ] The output can be compared semantically against Desired UXDL.
