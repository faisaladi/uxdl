# UXDL Implementation Readiness Profile

> **Status:** Active profile for the Phase 1 ready-to-develop handoff.
>
> This profile is backward-compatible with UXDL 0.1. It adds conventions in the
> open `metadata` namespace and does not change the Screen, State, Action, Relation,
> Slice, requirement, coverage, or stable-address core.

## 1. Purpose and boundary

`results/uxdl_dev_spec.html` is a generated handoff for an engineer who has not
read the source PRD or repository. The HTML is a projection, not a new source of
truth. Editable behavior remains in `examples/team-workspace/uxdl.project.yaml` and its declared
modules; approved presentation remains in `uxdl.dev/design.md`; technical and
security constraints remain in their active linked documents.

The profile makes the boundary explicit:

- UXDL carries observable behavior, requirements, acceptance, coverage,
  provenance, build evidence, guidance references, and gaps.
- A referenced source carries detailed design, content, technical, security, data,
  accessibility, or verification decisions that do not belong on every element.
- The renderer embeds each exact referenced source section once in the Source
  Library and links every citing packet to it.
- Missing information is a `specification_gaps` entry. It is never replaced with
  a template default, a guessed convention, or model-written filler.

## 2. Requirement values

An element-level requirement remains a dictionary under the nearest constrained
element's `metadata.requirements`.

### 2.1 Compact form remains legal

```yaml
metadata:
  requirements:
    editor_is_the_primary_call: The primary call to action opens the editor.
```

The compact string is the complete statement. Existing compact documents compose,
validate, edit, project, search, render, and generate exactly as before.

### 2.2 Expanded form

Use an object only when the obligation needs source-backed context or a verifiable
implementation handoff:

```yaml
metadata:
  requirements:
    editor_is_the_primary_call:
      statement: The primary call to action opens the editor.
      rationale: The Phase 1 loop begins in the local editor rather than an account flow.
      verification: At the published route, the primary CTA links to /editor and no signup CTA is presented as the primary action.
      guidance_refs:
        - ref: design_public_landing
          relationship: interaction and content guidance
      source_ref: product_public_landing
      priority: required
```

Fields:

| Field | Required | Meaning |
|---|---:|---|
| `statement` | yes for the new form | The obligation an implementation must satisfy. |
| `rationale` | no | Why the source or approved decision requires it. Preserve source wording. |
| `verification` | no | Observable evidence that proves the obligation. It is not a test implementation. |
| `guidance_refs` | no | Project-level authoritative reference IDs with an element relationship. |
| `source_ref` | no | A project-level reference ID for the source/provenance of the obligation. |
| `provenance` | no | An open source-backed provenance object when more detail is needed. |
| `priority` | no | Preserve only when the source states a priority; never assign a default. |
| legacy fields | preserved | `title`, `external_ref`, `task`, and other existing metadata remain lossless. `title` is a legacy statement alias when `statement` is absent. |

An expanded object with a legacy `title` is valid for existing documents. A new
implementation-guidance object uses `statement`. Consumers must preserve the raw
object, including unknown fields, while deriving a display statement from
`statement`, then legacy `title`, then a visible invalid-value finding. No
consumer may silently discard an object because it is not a string.

Requirement addresses use the existing stable grammar:

```text
<element_address>.requirements.<requirement_id>
```

The requirement remains on its nearest constrained screen, state, action, or
relation. Cross-element intent and acceptance remain on a Slice; coverage exposes
them without copying the criterion onto every element.

## 3. Authoritative reference registry

The project root may declare a registry at `metadata.authoritative_references`.
Registry IDs are stable within the project and are the only references that the
published renderer resolves.

```yaml
metadata:
  authoritative_references:
    design_public_landing:
      type: design
      label: Landing Page design direction
      path: uxdl.dev/design.md
      section: "## 18. Landing Page design direction"
      embed: true
    code_public_landing:
      type: code_evidence
      label: Shipped landing route
      path: uxdl.dev/src/app/(marketing)/page.tsx
      section: "export default function HomePage"
      embed: false
    proposed_generation_spec:
      type: technical
      label: Proposed importer and generation specification
      path: docs/65_UXDL_Importer_and_Generation_Specification.md
      section: "## 8. Generation architecture"
      embed: false
```

Each entry supports:

| Field | Rule |
|---|---|
| `type` | One of `design`, `content`, `technical`, `security`, `data`, `accessibility`, `code_evidence`, or `task_history`. |
| `label` | Human-readable authoritative source label shown with provenance. |
| `path` | A workspace-relative path declared by the project. It must not escape the workspace. |
| `url` | Optional external provenance link. The renderer never fetches it. |
| `section` | Exact Markdown heading line, section anchor, or code locator. Required when a local Markdown section is embedded. |
| `embed` | Required boolean. `true` means the referenced local Markdown section is required in the HTML; `false` means provenance/link only. |
| `status` | Optional source status such as `active`, `approved`, `proposed`, or `history`; preserve the source's stated status. |

At least one of `path` or `url` is required. A local path is resolved relative to
the workspace root, after normalizing separators. Paths containing `..`, absolute
paths, symlink escapes, or undeclared files fail resolution. A remote `url` is
displayed as provenance only; it never satisfies an embedded handoff requirement.

Elements cite registry entries through `metadata.guidance_refs`; expanded
requirements cite them through `guidance_refs`; slices may cite them through
`metadata.guidance_refs`. The canonical citation form is:

```yaml
guidance_refs:
  - ref: design_public_landing
    relationship: responsive and interaction guidance
```

The relationship is required, preserved verbatim, and rendered next to the source
label. A string reference may be accepted as a compatibility shorthand, but a new
source-backed handoff should use the object form so the relationship is explicit.

## 4. Deterministic section resolution and Source Library

The renderer resolves references in this order:

1. Read only the declared local `path` inside the workspace root.
2. For a local Markdown file with `embed: true`, match the exact `section` heading
   or section anchor.
3. Copy that heading and its body until the next heading of the same or higher
   level. Do not copy the entire document or execute arbitrary Markdown.
4. Emit that extracted section once in the Source Library. The library entry keeps
   the stable reference ID, type/status, label, path or URL, exact heading, and
   source-grounded body together.
5. Escape the extracted text into the HTML while preserving code fences, lists,
   tables, and links as inert source-grounded content.
6. For code evidence, render the path and exact locator as concise evidence; never
   embed the source file.
7. For an external URL, render a provenance link without network access.

The stable citation anchor is `source-<reference-id>`. A packet renders only the
source label, type/status, required relationship, and that anchor link. It never
repeats the full extracted body. If several registry entries resolve to the same
normalized local path and exact heading, the renderer emits one section body and
deterministic alias anchors for the other IDs; duplicate bodies are forbidden.

The renderer does not infer or summarize a packet excerpt. A short source-backed
statement needed beside a requirement must already be authored as its statement,
rationale, verification, or exact copy. This keeps interpretation at authoring
time and prevents different packets from presenting different summaries of one
authoritative section.

Required local sections that fail to resolve produce a visible finding at every
citation, an unresolved Source Library entry, and a `specification_gaps` entry in
the readiness result. They are never omitted.
An external reference with `embed: true` is invalid because it cannot be resolved
offline. A source whose stated status is `proposed` or `history` is not
authoritative shipped guidance; the packet must label that status and name the
remaining gap if implementation depends on it.

## 5. Implementation packet contract

Every delivery Slice of type `story` or `task` gets a stable packet anchor
`packet-<slice_id>`. Every canonical screen gets a screen packet anchor
`screen-<screen_id>`. A feature-map entry links directly to its delivery packet.

The primary page shows compact delivery and screen indexes. Opening or directly
linking to a packet reveals its implementation body; a fragment target must not
leave the relevant body closed and invisible. Print exposes packet bodies without
printing interactive navigation controls.

### 5.1 Delivery packet

A delivery packet renders:

1. intent and implementation outcome;
2. phase/build status, dependencies, and exact blocking gaps;
3. linked included screens;
4. ordered acceptance criteria;
5. relevant requirement statements grouped by owning element;
6. links from criteria and requirements to affected screen packets;
7. progressively disclosed coverage addresses, build evidence, source
   relationships/provenance, and editor targets.

It does not duplicate complete screen behavior or Source Library bodies.

### 5.2 Screen packet

A screen packet renders:

1. purpose, scope, route/type, build status, and concise code evidence;
2. computed readiness and every exact blocking gap;
3. states, actions, outcomes, conditions, branches, and targets;
4. requirement statements grouped under their nearest owning element;
5. content/copy obligations;
6. design and accessibility source relationships;
7. technical, security, and data source relationships;
8. verification evidence;
9. covered delivery criteria and links back to delivery packets;
10. progressively disclosed rationale, provenance, raw stable addresses, detailed
    code paths, and editor targets.

Requirements remain grouped by owning address. The packet may link to the global
requirement index, but it must not duplicate a Slice criterion onto every screen.
Exact gaps stay visible in the owning packet even though the global gap registry
lives in the appendix.

## 6. Computed readiness

Readiness is derived by the validator and renderer. Authors must not assert a
`ready` boolean.

For each screen and delivery packet, the machine-readable ledger records these
dimensions:

```yaml
readiness:
  behavior: complete | partial | missing | unresolved
  requirements: complete | partial | missing | unresolved
  design: direct | referenced | missing | unresolved
  content: direct | referenced | missing | unresolved
  technical: direct | referenced | missing | unresolved
  verification: direct | referenced | missing | unresolved
  authoritative_sources: [<registry_id>]
  gaps: [<exact_gap_id>]
  result: ready | ready_with_authoritative_references | blocked_by_specification_gaps
```

The result is computed as follows:

- `ready` means every required dimension is answered directly by UXDL/build
  evidence and there are no unresolved gaps or required references.
- `ready_with_authoritative_references` means every required dimension is
  answered, but one or more answers come from resolved, embedded authoritative
  sections. The packet remains self-contained.
- `blocked_by_specification_gaps` means any required dimension is missing or
  unresolved, build evidence contradicts the claim, a required source is
  proposed/history only, or a required reference cannot be resolved.

`not_applicable` is not a default or a new ledger enum. A source must explicitly
say that a dimension does not apply; the ledger then records direct evidence plus
that provenance. Otherwise absence is a gap. Phase 2 screens may remain blocked,
but their exact gaps remain visible. Every Phase 1 screen receives a computed
result, even when that result is blocked.

The global summary reports counts for `ready`,
`ready_with_authoritative_references`, and `blocked_by_specification_gaps`. It
never labels a packet ready when a required reference failed to resolve.

### 6.1 Evidence states

`direct` means the owning UXDL element, requirement, or Slice contains the required
decision or observable evidence. `referenced` means an `active` or `approved`
registry section resolves and its citation relationship explains exactly what it
supplies for the affected element. `partial` means some required obligations are
answered and others are not. `missing` means no qualifying evidence exists.
`unresolved` means evidence is cited but cannot resolve, is proposed/history only,
is contradicted by another active source, or has no element-specific relationship.

A generic cross-surface reference does not satisfy a screen-specific dimension
merely because its type matches. Its relationship must state how it constrains that
screen, and any remaining screen-specific decision is still a gap.

`specification_gaps_ref` propagates from the screen, its states, actions,
relations, requirements, and every owning or covering Slice. A nested gap keeps its
exact element address in the ledger and blocks the affected screen and delivery
packet. A declared gap is never cancelled by build evidence.

### 6.2 Dimension definitions and required evidence

#### Behavior

`complete` requires the purpose/scope and every state, action, outcome, condition,
branch, and target needed by the owning acceptance criteria to be explicit and
resolvable. A static surface without actions is complete only when UXDL or an exact
authoritative relationship establishes that no interactive behavior is required.
A description or shipped route alone is insufficient.

#### Requirements

`complete` requires every build-critical obligation to be attached to its nearest
constrained element and every owning Slice criterion to retain resolvable coverage.
For readiness, a compact requirement needs either expanded source-backed rationale,
verification, and guidance or a precise authoritative relationship that supplies
the missing implementation context. Compact syntax remains valid and lossless when
this evidence is absent; the packet is simply not ready to implement.

#### Design

`direct` or `referenced` evidence must resolve layout, hierarchy, interaction,
responsive behavior, visual states, accessibility presentation, and motion where
those decisions affect faithful implementation. Generic identity guidance alone
does not satisfy screen layout or interaction. Code appearance and build status are
evidence of what exists, not approval of intended design.

#### Content

Evidence must provide exact user-facing copy when wording is contractual, or an
explicit content structure and source relationship when wording may vary. A screen
name, route, placeholder, or current implementation string is not content guidance
unless an active source declares it authoritative.

#### Technical

Evidence must define the implementation boundaries material to the screen, such as
data ownership and persistence, interfaces, security/privacy constraints, failure
handling, and platform limitations. Only applicable boundaries need evidence, but
absence is not automatically `not_applicable`. A route, `build_ref`, dependency,
or existing code path proves implementation state; it does not by itself define
the intended technical contract.

#### Verification

Evidence must state observable proof for every build-critical requirement and
acceptance criterion, directly in expanded requirements/Slices or through an exact
active verification reference. Relations describe behavior and code tests describe
current implementation; neither automatically supplies the acceptance evidence for
the intended obligation.

### 6.3 Readiness result gate

Any `partial`, `missing`, or `unresolved` required dimension, any propagated gap,
or any contradiction produces `blocked_by_specification_gaps`. `ready` requires all
evidence to be direct. `ready_with_authoritative_references` requires every cited
answer to resolve and remain embedded in the Source Library. Build status is shown
separately and never changes this computation.

## 7. Local editor deep-link contract

The published artifact may provide progressive authoring links. The artifact must
remain sufficient without them.

The stable route is `/editor` with an explicit project and item target:

| Target | Query contract |
|---|---|
| Document focused on an address | `project=<local-id>&view=document&address=<stable-address>` |
| Canvas focused on a screen | `project=<local-id>&view=canvas&screen=<screen-id>` |
| Flow seeded from a journey | `project=<local-id>&view=flow&journey=<slice-id>` |
| Requirements focused on a requirement | `project=<local-id>&view=requirements&requirement=<requirement-address>` |
| Source document/reference | `project=<local-id>&view=files&source=<reference-id>` |
| Specification gap context | `project=<local-id>&view=document&gap=<gap-id>` |

The editor first looks for the requested project in its local repository. A link
with a missing project must not silently open the generic sample at an unrelated
selection.

The composed handoff payload appears exactly once in the HTML as inert bundled
data. One explicit **Open/import this project in the editor** control reads that
payload only when activated and constructs the single bootstrap navigation with
`handoff=<encoded-project>`. No ordinary Canvas, Document, Flow, Requirements,
source, or gap link contains the payload.

After the project exists locally, every target link uses only the short query
contract in the table above. If another local project is active, importing remains
confirmation-gated and cancellation leaves the active project and onboarding
persistence unchanged. If the requested project is missing, the editor shows the
import choice or missing-project fallback rather than an unrelated sample.

When the artifact is opened from `file:` or another context that cannot resolve
the local `/editor` route, the bootstrap control does not follow a known-broken
relative link. It shows the always-available manual fallback: download the composed
UXDL, open/import it in the local editor, and use the displayed stable address,
journey ID, requirement address, source ID, or gap ID. The HTML remains sufficient
without completing this handoff.

The payload is source data, not executable content. It is URL-safe encoded, size
bounded to 5 MB before decoding, parsed as the declared composed-project JSON
format, and decoded only by the local editor. No network fetch or account is
required. Links that contain only `/editor` are invalid handoff links. Validation
reports HTML bytes, maximum link length, ordinary target-link maximum length, total
link bytes, and payload-link count; the full payload may occur in at most the one
bootstrap interaction.

## 8. Validation and consumer parity

`composeUxdlProject` in TypeScript is the only composition implementation. The
TypeScript CLI is the canonical generator and freshness oracle for composed
projections; validators in other languages consume its assembled output and do not
independently compose project modules.

The Python and TypeScript profile validators emit the same ordered normalized
findings. The following consumers preserve compact and expanded requirements and
structured references without silent loss:

- core/profile validation;
- composition and source ownership;
- requirement projections, indexes, search, and filters;
- Document view and editor/Notion-style editing;
- generation conformance and the packaged generator skill;
- composed compatibility output;
- published HTML and readiness ledger.

Tests must prove round trips for both compact and expanded values through
composition, editing, projection, rendering, and generation. Reference resolution
tests must cover a valid local section, a missing heading, an unsafe path, an
external URL, and a required proposed/history source.

## 9. Readiness ledger

The generated machine-readable inventory is
`results/uxdl_dev_readiness.json`. It is a deterministic projection of the
composed project, the registry, active design/technical sources, and verified build
evidence. It contains:

- source revision/content hash;
- one entry for each of the 32 canonical screens;
- Phase 1/Phase 2 classification;
- all six readiness dimensions;
- authoritative source IDs, paths, headings, and resolution status;
- exact requirement and acceptance addresses;
- exact unresolved gap IDs and affected elements;
- global computed readiness counts and validator evidence.

The ledger is generated, not hand-edited. A fixed composed input and fixed source
files produce byte-stable JSON and HTML.

## 10. Safety and non-goals

- The renderer is offline, deterministic, printable, and has no runtime LLM or
  network dependency.
- The renderer never fetches a URL, executes Markdown, or embeds an entire source
  document for convenience.
- Detailed framework choices, database schemas, and measurements stay in their
  owning technical/design source; they are not repeated in every requirement.
- Tasks remain execution/history evidence. A task is not an authoritative source
  for a packet until a lasting decision is promoted to an active design or
  technical document.
- Phase 1 proves the ready-to-develop local handoff. Accounts, hosted persistence,
  sharing, and billing remain Phase 2 unless the active build and product contract
  say otherwise.
