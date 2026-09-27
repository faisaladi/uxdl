# 02. UXDL 0.1 Specification

> **Status:** Working draft for editor prototyping and user validation.
>
> UXDL 0.1 intentionally keeps content flexible while making product behavior addressable. The design principle is **loose content, strict addressability**.

## 1. Purpose

UXDL is a compact, human-readable description of a user experience flow. It gives product managers, designers, engineers, QA, researchers, and analysts stable identifiers for the same screens, states, actions, and relations.

UXDL is:

- a shared map of product behavior;
- readable YAML;
- visualizable as a graph;
- open to any domain-specific context through `metadata`;
- suitable for deterministic structural checks and human review.

UXDL is not:

- a replacement for every PRD, research report, design file, or technical RFC;
- an executable programming language;
- a component, layout, or styling specification;
- a guarantee that a product decision is correct or complete.

## 2. Design rules

1. **Stable identifiers:** structural elements use stable IDs so teams can reference the same behavior.
2. **Local ownership:** actions belong to screens; relations belong to actions.
3. **Open metadata:** contextual content can be a string, list, or nested object.
4. **Progressive detail:** actors, states, groups, conditions, analytics, security, and technical details are optional.
5. **Visual-first authoring:** people may use an editor instead of writing YAML directly.
6. **Advisory completeness:** templates and prompts may suggest missing paths without rejecting intentional product choices.
7. **Portable composition:** large projects may use the optional multi-file project profile while preserving one deterministic assembled UXDL 0.1 document.

## 3. Minimal document

```yaml
# UXDL 0.1 Specification
# Full Standard & AI Prompt Spec: https://uxdl.dev/docs
# Connect AI Agents via MCP Server: https://uxdl.dev/mcp

uxdl: "0.1"
app: Example App
title: Sign-in flow

screens:
  sign_in:
    name: Sign In
    actions:
      submit:
        relations:
          success:
            to: home

  home:
    name: Home
```

The root object MUST contain:

- `uxdl`: the supported format version. For this draft it MUST be `"0.1"`.
- `screens`: a dictionary keyed by screen ID.

The root MAY contain:

- `app`: product or service name.
- `title`: document or flow name.
- `metadata`: open document-level context.
- `actors`: addressable human or system participants.
- `groups`: visual or conceptual collections of screens.
- `layout`: editor-managed positions and preferences.
- `extensions`: namespaced tool-specific data.

Unknown root keys SHOULD produce a warning rather than data loss.

## 4. Identifiers and references

IDs SHOULD use lowercase `snake_case` and match:

```text
^[a-z0-9][a-z0-9_]*$
```

IDs are unique within their parent dictionary. Fully qualified references are formed from ownership:

```text
sign_in
sign_in.states.invalid_otp
sign_in.actions.submit
sign_in.actions.submit.relations.invalid
```

Renaming an ID is a semantic change. Editors SHOULD update references or warn before the rename is applied.

## 5. Metadata

Every addressable element MAY contain `metadata`. Its contents are intentionally open:

```yaml
metadata:
  description: Authenticate a partner with email OTP.
  security:
    - OTP expires after 10 minutes.
    - Lock the account after 5 failed attempts.
  analytics:
    event: otp_submitted
    properties: [organization_id, attempt_number]
  design:
    figma: https://example.com/design-reference
  qa:
    - Verify paste and autofill.
    - Verify expiration at exactly 10 minutes.
```

A core parser MUST preserve metadata without interpreting or deleting unknown keys. Templates and plugins MAY understand particular metadata shapes, but those shapes are not core UXDL requirements.

Structural keys are reserved outside `metadata`. Domain-specific keys SHOULD NOT be placed beside structural keys because they may collide with future versions.

## 6. Actors

Actors are optional and keyed by stable ID:

```yaml
actors:
  partner:
    name: Travel Partner
    type: human
    metadata:
      roles: [owner, admin, booking, finance]

  auth_service:
    name: Authentication Service
    type: system
```

Reserved actor keys:

- `name`: human-readable label.
- `type`: recommended values are `human`, `system`, or `external`.
- `metadata`: open context.

An action MAY reference an actor ID. Missing actor references are warnings in 0.1 because actors are optional.

## 7. Screens

Screens are the primary addressable surfaces:

```yaml
screens:
  sign_in:
    name: Partner Sign In
    type: page
    metadata:
      description: Public email OTP sign-in.
```

Reserved screen keys:

- `name`: human-readable label; REQUIRED.
- `type`: free-text surface classification such as `page`, `modal`, `sheet`, `drawer`, `panel`, `header`, `sidebar`, or `overlay`.
- `parent`: optional host screen ID for a sub-screen, modal, sheet, drawer, panel, or overlay.
- `states`: optional dictionary of addressable states.
- `actions`: optional dictionary of addressable actions.
- `metadata`: open context (including `requirements`).

Screen types are not a closed enum in 0.1.

For detailed architectural guidance on deciding when to model an element as a Sub-Screen vs. a Requirement, see:

the *Sub-Screen vs. Requirement Modeling Guide*

For step-by-step guidance on deriving Unit, Integration/E2E, and Regression test suites from UXDL specifications, see:

[`64_Generating_Test_Cases_from_UXDL_Guide.md`](../guides/test-generation.md)

## 8. States

States describe meaningful variations of a screen. They are optional and may use compact or expanded form.

Compact:

```yaml
states:
  default: Ready for input
  invalid_otp: The entered OTP is invalid
```

Expanded:

```yaml
states:
  invalid_otp:
    name: Invalid OTP
    metadata:
      message: The code is incorrect or expired.
      recovery: Let the user retry or request a new code.
```

An expanded state MAY contain:

- `name`: human-readable label.
- `metadata`: open context.

Parsers MUST preserve other state content as metadata-compatible content and SHOULD warn when it collides with a reserved structural key.

## 9. Actions

Actions describe something a human or system can do from a screen:

```yaml
actions:
  submit_otp:
    name: Submit OTP
    actor: partner
    metadata:
      trigger: Submit button
    relations: {}
```

Reserved action keys:

- `name`: optional human-readable label; defaults to a title-cased ID.
- `actor`: optional actor ID.
- `relations`: dictionary of addressable relations.
- `metadata`: open context.

An action without relations is valid while drafting and produces an advisory warning.

## 10. Relations

A relation describes what follows an action. Relations are dictionaries keyed by stable ID:

```yaml
actions:
  submit_otp:
    relations:
      valid:
        to: product_list
        when: OTP is valid
        path: happy

      invalid:
        to: sign_in
        state: invalid_otp
        when: OTP is invalid
        path: error
        metadata:
          behavior: Preserve the entered email.
```

Reserved relation keys:

- `to`: target screen ID.
- `state`: optional state ID on the target screen.
- `external`: external destination when the relation leaves the modeled experience.
- `end`: `true` when the journey intentionally terminates.
- `when`: optional human-readable condition.
- `path`: optional free-text classification such as `happy`, `error`, `edge`, or `fallback`.
- `metadata`: open context.

A relation MUST declare exactly one destination form:

1. `to`, optionally with `state`;
2. `external`; or
3. `end: true`.

Conditions remain natural language in 0.1. They are not executable expressions and do not require a formal condition registry.

## 11. Groups

Groups organize screens without changing behavior:

```yaml
groups:
  authentication:
    name: Authentication
    screens: [sign_in, verify_email]
    metadata:
      owner: Identity team
```

Reserved group keys:

- `name`: human-readable label.
- `screens`: list of screen IDs.
- `metadata`: open context.

Groups do not own screens and cannot change relation semantics.

## 12. Layout

`layout` stores editor-managed presentation data:

```yaml
layout:
  direction: left_to_right
  positions:
    sign_in: {x: 120, y: 240}
    home: {x: 520, y: 240}
```

Layout is optional and MUST NOT be interpreted as product behavior. Tools SHOULD preserve unknown layout keys.

## 13. Validation

### Errors

Errors are deterministic and prevent reliable parsing or rendering:

- invalid YAML;
- unsupported or missing `uxdl`;
- missing `screens`;
- invalid or duplicate IDs;
- screen without `name`;
- broken `parent`, `to`, target `state`, or group screen reference;
- relation with no destination or multiple destination forms;
- invalid structural value type.

### Warnings

Warnings identify potentially incomplete work but do not make the document invalid:

- unreachable screen;
- screen without actions;
- action without relations;
- actor reference not declared;
- screen with only self-relations;
- unknown structural key outside `metadata` or `extensions`.

Entry screens and intentional terminal screens may be declared in metadata or accepted explicitly by an editor.

### Template prompts

Templates provide contextual questions rather than universal rules:

- What happens when this request fails?
- Does a conditional relation need an alternative path?
- Can the actor cancel or retry?
- What happens when data is empty, loading, or offline?
- Who is allowed to perform this action?
- How will success be measured?
- What evidence or design reference supports this decision?

## 14. Canonical example

The complete uxdl.dev product project is maintained in `examples/team-workspace/uxdl.project.yaml` (with the frozen v0.1 single-file snapshot archived in `archive/12_UXFlow_SaaS.v0.1.snapshot.uxdl.yaml`).

The non-normative UX research example is:

[`auth.uxdl.yaml`](../examples/team-workspace/flows/auth.uxdl.yaml)

It demonstrates evidence, interaction notes, assessments, and opportunities
using only open metadata. Its research vocabulary is an example profile, not
required UXDL syntax.

The optional, non-normative slices experiment is documented in:

[`35_UXDL_0.1_Slices_Extension.md`](../profiles/slices.md)

Its example is:

[`subscription.uxdl.yaml`](../examples/team-workspace/slices/subscription.uxdl.yaml)

Slices are stored under `extensions` and do not change UXDL 0.1 conformance.
The current core validator preserves the extension while validating its
underlying actors, screens, states, actions, and relations.

Large UXDL projects may use the optional packaging profile documented in:

[`37_UXDL_0.1_Multi_File_Project_Profile.md`](../profiles/multi-file.md)

The profile adds a manifest and source modules at the tooling layer. It does
not change screen, state, action, relation, or fully qualified reference
semantics. Project-aware tools must assemble and validate the complete document;
ordinary UXDL 0.1 tools may consume the generated single-file export.

The standalone editor and visualizer is:

the prototype editor

## 15. Versioning

UXDL remains in `0.x` while the team tests authoring, visualization, review, and handoff with real users.

- Minor `0.x` releases may change structure.
- Documents MUST declare their version.
- The editor MUST reject unsupported versions instead of silently reinterpreting them.
- A `1.0` release requires validated adoption evidence, stable migration rules, and a documented compatibility policy.
