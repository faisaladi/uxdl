# UXDL Versioning and Compatibility Guideline

> **Status:** Normative repository operating guideline  
> **Applies to:** UXDL standards, profiles, schemas, fixtures, product projects, uxdl.dev, generators, validators, migrations, and published artifacts  
> **Current supported format:** UXDL `0.1` only  
> **Authority:** This document governs how versions are introduced and supported. It does not define UXDL `0.2` syntax.

---

## 1. Purpose

UXDL has several independently changing artifacts: a serialized behavior format,
optional profiles, a multi-file packaging model, validators, a Canvas application,
the uxdl.dev product contract, and generated handoff artifacts. A single version
number cannot accurately represent all of them.

This guideline establishes:

1. which artifact each version number identifies;
2. what counts as backward compatible;
3. how one uxdl.dev application supports more than one UXDL format;
4. how existing projects remain readable and editable;
5. when explicit migration is required;
6. how standards, fixtures, code, product sources, and generated artifacts are
   organized and released; and
7. which evidence is required before an agent may claim compatibility.

The objective is durable user ownership of UXDL projects. Opening a project in a
newer app must not silently change its meaning, erase unsupported content, or force
an upgrade.

---

## 2. Normative Language

The terms **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and
**MAY** are normative.

- **MUST / MUST NOT**: mandatory for a conforming implementation or release.
- **SHOULD / SHOULD NOT**: expected unless a documented exception is approved.
- **MAY**: optional behavior that must remain within the other compatibility rules.

No agent may weaken a MUST-level rule merely to make a fixture, validator, build,
or migration pass.

---

## 3. Version Dimensions

UXDL uses separate versions for separate responsibilities.

### 3.1 Format version

The format version identifies the serialized core structure and semantics of a
UXDL document.

```yaml
uxdl: "0.1"
```

Examples: `0.1`, `0.2`, and eventually `1.0`.

The format version governs:

- core structural keys;
- Screen, State, Action, and Relation semantics;
- address grammar;
- reference resolution;
- core validation rules;
- required declarations; and
- serialization and round-trip behavior.

A document MUST declare its format version. Importers MUST NOT guess a missing
version for user-supplied content. A new-project template MAY insert the latest
stable version because it is creating, not interpreting, a document.

### 3.2 Project packaging version

The project packaging version identifies the manifest and module composition
contract.

```yaml
uxdl_project: "0.1"
uxdl: "0.1"
```

Each module declares its module profile:

```yaml
uxdl_module: "0.1"
```

Packaging and format compatibility MUST be declared explicitly. A composer MUST
reject a manifest/module combination it does not support instead of attempting a
best-effort merge.

### 3.3 Extension or profile version

An extension under the open `extensions` namespace MAY carry an independent
profile version.

```yaml
extensions:
  uxdl_slices:
    version: "0.1"
```

A profile version governs only that profile. Adding or revising an optional profile
does not automatically change the core UXDL format version.

Core tools that do not understand an extension MUST preserve its source content
when round-tripping. They MAY omit an unsupported extension from a derived view,
but MUST report the unsupported capability and MUST NOT silently discard it.

### 3.4 Standard release version

The standard release version identifies a published bundle of normative text,
schemas, fixtures, and conformance expectations.

Example: **UXDL Standard 0.1.1**.

A standard patch release MAY clarify format `0.1` without changing the serialized
identifier. Documents governed by Standard 0.1.1 still declare:

```yaml
uxdl: "0.1"
```

### 3.5 Application release version

The uxdl.dev application has an independent release version. An app release may
add Canvas, Flow, Document, validation, accessibility, or rendering improvements
without changing any UXDL format.

The app MUST publish a support matrix naming the format and profile versions it
can open, validate, edit, round-trip, export, and migrate.

### 3.6 Product-contract revision

`examples/team-workspace/uxdl.project.yaml` and its declared modules describe the current uxdl.dev
product. Their revision is recorded by Git history and product release metadata,
not by inventing another UXDL format version.

A product behavior change does not change the UXDL format version unless it
requires syntax or semantics that the current format cannot represent.

---

## 4. Canonical Authority and Derived Artifacts

### 4.1 Active product authority

The sole editable authority for uxdl.dev product behavior is:

- `examples/team-workspace/uxdl.project.yaml`; and
- every module explicitly declared by that manifest.

Only the owning manifest or module may be edited to change product behavior.

### 4.2 Generated projections

Composed YAML under `results/`, readiness ledgers, published HTML, diagrams, and
other projections are deterministic derived artifacts. They MUST NOT be edited as
product sources.

The active composed projection is regenerated from `product/` and may be used for:

- validation;
- rendering;
- download and handoff;
- compatibility testing; and
- tools that consume only a single-file document.

### 4.3 Archived snapshots

An archived composed UXDL file records a historical checkpoint. It MUST be labelled
with its format/release context and MUST NOT remain a freshness target after it is
archived.

An archived snapshot may be used as a regression fixture only when a test declares
that purpose explicitly. It never competes with `product/` as a living authority.

---

## 5. Compatibility Vocabulary

Compatibility claims must name the exact capability being claimed.

| Capability | Required meaning |
|---|---|
| Detect | Identify the declared format without guessing. |
| Parse | Read the syntax without crashing or dropping data. |
| Validate | Apply the correct version-specific rules and findings. |
| View | Render supported meaning and visibly report unsupported capabilities. |
| Edit | Allow changes without corrupting unsupported or untouched content. |
| Round-trip | Parse and serialize without unintended semantic or data loss. |
| Export | Produce a valid document in the project's declared format. |
| Compose | Deterministically assemble a supported manifest and modules. |
| Migrate | Explicitly convert a copy into another declared format with a report. |

“Supported” without a capability is insufficient. For example, read-only viewing
does not prove editable round-trip support.

---

## 6. Compatibility Levels

The support matrix uses four levels.

### 6.1 Full

The app can detect, parse, validate, view, edit, round-trip, compose when applicable,
and export the version. Required conformance suites pass.

### 6.2 Maintenance

The app can safely open, validate, view, and export the version. Some new authoring
features may be unavailable. Any editing limitation is visible before mutation.

### 6.3 Migration only

The app can validate the source sufficiently to run a documented migration, but
does not claim general editing support. The original remains unchanged.

### 6.4 Unsupported

The app refuses semantic editing. It reports the declared version, the supported
versions, and a safe next action. Raw source MAY remain downloadable or viewable,
but MUST NOT be reinterpreted as another version.

---

## 7. Change Classification

Every proposed standard or tooling change MUST be classified before implementation.

| Proposed change | Release effect |
|---|---|
| Clarify wording without changing accepted documents | Standard patch; same format identifier |
| Correct validator behavior to match an already normative rule | Standard/tool patch; same format identifier |
| Improve errors, Canvas layout, accessibility, or renderer output | Application release only |
| Add fixtures for rules already defined | Standard/tool patch; same format identifier |
| Add optional metadata content within an already open metadata area | Usually same format; verify round-trip preservation |
| Add or revise an optional extension | Profile release; core format may remain unchanged |
| Add a core structural key with new semantics | New format unless older tools can preserve and safely ignore it by existing rule |
| Change required keys or allowed value shapes | New format |
| Change Screen, State, Action, or Relation meaning | New format |
| Change address or reference grammar | New format |
| Make a previously valid published document invalid | New format, except correction of proven implementation nonconformance to an unchanged normative rule |
| Move behavior between core structures in a way requiring document conversion | New format |
| Change the product described by `product/` using existing syntax | Product-contract revision only |

When classification is ambiguous, the change MUST be treated as potentially
breaking and stopped for a format decision.

### 7.1 Standard 0.1.1 boundary

UXDL Standard 0.1.1 MAY contain:

- editorial clarification;
- canonical-authority cleanup;
- schema or validator corrections that enforce existing 0.1 meaning;
- additional valid and invalid fixtures;
- deterministic composition corrections;
- Canvas and handoff improvements; and
- better unsupported-content reporting.

It MUST NOT require an existing conforming 0.1 document to change its structure or
declared `uxdl` value.

### 7.2 Format 0.2 boundary

UXDL format 0.2 is required when a proposal changes serialized structure or meaning
in a way that cannot preserve 0.1 behavior through the existing contract.

Potential 0.2 topics include externalized requirement ownership, new reference
semantics, or behavior constructs that 0.1 cannot express. This guideline does not
approve or define any such structure.

---

## 8. One Application, Versioned Format Adapters

uxdl.dev SHOULD remain one application. It SHOULD NOT fork into separate “0.1
Canvas” and “0.2 Canvas” products.

The application architecture for multiple formats is:

```text
source files
  -> version detection
  -> version-specific parser
  -> version-specific validator
  -> normalized behavioral model + retained source data
  -> shared Canvas / Flow / Document projections
  -> version-specific serializer
```

### 8.1 Version registry

The app MUST have one explicit registry of supported versions. Each registered
format identifies:

- detector;
- parser;
- validator;
- normalizer;
- serializer;
- composer, if applicable;
- supported profiles;
- capability flags;
- conformance fixtures; and
- available migrations.

Scattered string comparisons are not a sufficient multi-version architecture.

### 8.2 Normalized behavioral model

Shared visual surfaces SHOULD consume a normalized model of behavioral concepts,
not raw version-specific YAML keys.

The normalized model MUST preserve stable identity and source provenance. It MUST
NOT pretend that a concept exists in an older format when it does not.

### 8.3 Lossless source retention

Normalization for display is not permission to rewrite source. Unknown open
metadata and extension namespaces MUST survive editing and export unless the user
explicitly removes them.

If a version-specific feature cannot be represented by a shared editor control,
the app MUST retain it, show a capability limitation, and prevent destructive edits.

### 8.4 Version-specific serialization

Saving a 0.1 project MUST use the 0.1 serializer. Saving a 0.2 project MUST use the
0.2 serializer. The app MUST NOT serialize all projects through the newest format.

---

## 9. Required Application Behavior

| Situation | Required behavior |
|---|---|
| Open a supported 0.1 project | Validate and open as 0.1. |
| Edit a supported 0.1 project in a newer app | Preserve format 0.1 and all untouched supported/open content. |
| Export a 0.1 project | Export valid 0.1 unless the user explicitly chose migration. |
| Open a supported 0.2 project | Route through the 0.2 adapter. |
| Open an unsupported version | Refuse semantic editing and show supported versions and safe next steps. |
| Open a document without a version | Report a missing-version error; do not assume 0.1. |
| Encounter a supported document with an unsupported profile | Preserve the profile, report limited capability, and prevent lossy edits. |
| New project creation | Use the latest stable format, never an experimental draft by default. |
| Draft-format experiment | Require an explicit experimental flag and visible warning. |

The app MUST NOT silently upgrade a project when it is opened, viewed, edited, or
saved.

---

## 10. Migration Contract

Migration is an explicit product operation, not a parser fallback.

### 10.1 Required properties

A migration MUST be:

- deterministic for identical input and decisions;
- version-specific, such as `0.1 -> 0.2`;
- non-destructive to the source project;
- explicit about unsupported or ambiguous mappings;
- validated before and after conversion;
- reviewable as a semantic and source diff; and
- cancellable before the new project is accepted.

### 10.2 Required sequence

1. Detect and validate the source version.
2. Record source validation failures separately from migration findings.
3. Evaluate whether every source concept has a target representation.
4. Report automatic conversions, unresolved decisions, conflicts, and losses.
5. Obtain required user decisions.
6. Generate a new project copy with the target version declaration.
7. Validate the target project with the target validator and profiles.
8. Present behavioral, address, requirement, and source diffs.
9. Require explicit confirmation before the migrated copy becomes active.
10. Preserve the original project and migration report.

### 10.3 Forbidden migration behavior

A migration MUST NOT:

- mutate the active project in place before confirmation;
- invent missing product decisions;
- silently drop unknown metadata or extensions;
- hide address changes;
- repair unrelated invalid source content without reporting it;
- convert an unresolved source concept into a guessed target concept; or
- claim success when target validation fails.

---

## 11. Product Project Operating Model

`product/` represents one current living uxdl.dev product contract and MUST declare
one active format at a time.

The repository MUST NOT maintain parallel editable directories such as
`product-v0.1/` and `product-v0.2/` as competing product authorities.

When a new format is being designed:

1. v0.2 syntax and fixtures are developed outside the living product authority;
2. the app gains v0.2 support while retaining v0.1 support;
3. migration is implemented and verified;
4. a copy of `product/` is migrated and reviewed;
5. behavior and address changes are reconciled; and
6. only after approval is the living product switched to the new format.

Git history and released snapshots preserve earlier product states. Generated or
archived projections do not become parallel editable sources.

---

## 12. Repository Model

Before a second format exists, the current v0.1 files may remain at their approved
stable paths. Introducing v0.2 requires an explicit repository-structure task.

The target logical organization is:

```text
standard/
  compatibility.md
  0.1/
    specification
    schema
    profiles
    fixtures
  0.2/
    specification
    schema
    profiles
    fixtures
  migrations/

product/
  uxdl.project.yaml
  actors.uxdl.yaml
  flows/
  slices/

uxdl.dev/
  version registry
  version adapters
  normalized behavioral model
  shared views
  migrations

results/
  generated current product projections
```

This is a responsibility model, not authorization to move current files during an
unrelated cleanup. Stable paths may be preserved through indexes or redirects when
the physical organization changes.

---

## 13. Conformance Fixtures

Every supported format requires immutable, version-labelled fixture sets.

Each set MUST include:

- smallest valid document;
- representative full document;
- multi-file project, if supported;
- valid open metadata;
- valid supported profiles;
- unknown extension preservation;
- every blocking structural error class;
- broken address/reference cases;
- round-trip golden files;
- composition golden output; and
- migration input/output pairs when migration exists.

Fixtures MUST declare which standard release establishes their expected result.
Deliberately invalid fixtures MUST never be repaired to make tests pass.

---

## 14. CI and Release Evidence

The app's supported-version claim MUST be executable.

For every fully supported format, CI MUST prove:

1. version detection;
2. valid parsing;
3. deterministic validation;
4. invalid-fixture rejection;
5. lossless round-trip for governed content;
6. unknown open-content preservation;
7. deterministic composition where applicable;
8. Canvas/projection compatibility for representative behavior;
9. version-correct export; and
10. migration behavior when a migration is advertised.

The CI matrix SHOULD be organized by format and profile version rather than by the
latest format only.

A release MUST NOT claim backward compatibility solely because the TypeScript
build passes or an old file can be parsed.

---

## 15. Standard Release Procedure

### 15.1 Compatible standard patch

For a release such as Standard 0.1.1:

1. classify every change as non-structural;
2. confirm conforming 0.1 documents require no migration;
3. update normative documents, schemas, and fixtures where applicable;
4. run the full 0.1 conformance suite;
5. publish changed clarification and implementation notes;
6. retain `uxdl: "0.1"`; and
7. tag the approved standard release.

### 15.2 New format release

For a format such as 0.2:

1. approve the problem and breaking-change rationale;
2. define the new normative structure and semantics;
3. define compatibility and migration behavior;
4. create versioned schema, profiles, and fixtures;
5. implement version detection and a dedicated adapter;
6. retain and run the complete 0.1 suite;
7. implement target serialization and explicit migration;
8. publish the app support matrix;
9. validate real exemplars without migrating `product/` first;
10. release format support; and
11. migrate the living product only through a later approved product task.

Draft syntax MUST NOT become the default generator or new-project output.

---

## 16. Support and Deprecation Policy

The initial multi-version policy is:

- format 0.1 remains **Full** while it is the only released format;
- releasing format 0.2 MUST NOT automatically remove 0.1 support;
- the support matrix must state each capability separately;
- a format may move from Full to Maintenance only through an explicit product
  decision with conformance evidence;
- a format may move to Migration only only when a safe migration exists; and
- removal requires a published deprecation window and a durable way for users to
  recover or export their source.

No agent may delete an old adapter, fixture suite, serializer, or migration merely
because `product/` has moved to a newer format.

---

## 17. Current Implementation Baseline

As of this guideline's approval:

- UXDL format `0.1` is the only supported format;
- the manifest and module composer requires `uxdl_project: "0.1"`,
  `uxdl: "0.1"`, and `uxdl_module: "0.1"`;
- generators emit UXDL 0.1;
- application code and tests contain direct 0.1 assumptions;
- no multi-version registry or normalized version-adapter layer has been proven;
- no 0.1-to-0.2 migration exists; and
- UXDL 0.2 is unsupported and undefined.

Therefore, changing a file declaration to `0.2` is not a valid way to begin 0.2.
The architecture and release sequence in this guideline must be completed first.

---

## 18. Agent Decision Procedure

Before changing UXDL syntax, validation, composition, generation, or app support,
an agent MUST answer:

1. Which version dimension is changing?
2. Does a currently conforming project need to change?
3. Could an older supported app preserve the new content without semantic loss?
4. Does the change alter addresses, references, ownership, or behavior meaning?
5. Is the change core, profile-specific, product-specific, or presentation-only?
6. Which fixtures prove compatibility or breakage?
7. Does a migration become necessary?
8. Which existing format adapters and suites must continue to pass?
9. Is `product/` being changed too early?
10. Has a human approved any breaking-format decision?

If any answer is unknown, the agent MUST stop and write a decision task instead of
inventing compatibility behavior.

---

## 19. Agent Change Checklist

### Compatible patch checklist

- [ ] Existing valid projects remain valid without source changes.
- [ ] Existing addresses and behavior semantics are unchanged.
- [ ] The format identifier remains unchanged.
- [ ] Validator changes implement an already normative rule.
- [ ] Round-trip fixtures remain lossless.
- [ ] The support matrix remains accurate.
- [ ] No migration is required.

### New format checklist

- [ ] Breaking rationale is approved.
- [ ] Versioned normative specification exists.
- [ ] Schema and fixture suite exist.
- [ ] Version detection does not guess.
- [ ] Dedicated parser, validator, normalizer, and serializer exist.
- [ ] Shared views declare capability limitations.
- [ ] Previous format suites continue to pass.
- [ ] Migration is explicit, non-destructive, and validated.
- [ ] Support matrix is published.
- [ ] New projects use the new format only after it is stable.
- [ ] `product/` migration is a separate approved task.

---

## 20. Examples

### 20.1 Canonical-authority cleanup

Making the multi-file `product/` project the sole editable authority and archiving
a duplicate composed document changes repository governance, not the UXDL format.
It may be released as part of a Standard 0.1.1/tooling update.

### 20.2 Canvas layout improvement

Changing node layout, labels, navigation, or accessibility while preserving source
and behavior is an application release only.

### 20.3 Additional optional profile

Adding an optional profile under `extensions` may introduce a new profile version
without changing core UXDL, provided unsupported tools preserve it and no core
semantics are changed.

### 20.4 Externalizing requirement detail

Moving requirement ownership out of current element metadata, changing how it is
addressed, or requiring external references for its meaning changes document
structure or semantics. It requires a format decision and is a candidate for 0.2.

### 20.5 Stricter validation

Rejecting content already forbidden by the published 0.1 specification is a
validator correction. Rejecting documents previously valid under the published
rules is a breaking format change, regardless of whether the new rule appears
desirable.

---

## 21. Non-Goals

This guideline does not:

- define UXDL 0.2 syntax;
- approve a requirement-reference architecture;
- guarantee that all future concepts fit one normalized model;
- authorize current file moves;
- replace the UXDL specification, profiles, schemas, or design contract;
- require migration of `product/`; or
- make generated projections canonical.

---

## 22. Governing Principle

Versioning exists to protect meaning and user ownership, not to label the latest
implementation.

The application may improve continuously. A project changes format only through an
explicit, validated, reviewable decision. Unsupported meaning remains visible, and
unresolved migration decisions remain unresolved rather than being guessed.
