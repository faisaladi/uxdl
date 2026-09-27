# 01. Overview and Principles: UXDL

> **Current direction:** UXDL 0.1 — loose content, strict addressability.

## 1. The Problem Space
In modern digital product development, there is a fundamental disconnect between Design, Development, and Analytics.
- **Design Tools (Figma):** Are inherently visual and static. "App Flows" are represented by vector arrows drawn between hundreds of duplicated screens to represent different states. When a flow changes, the manual wiring breaks.
- **Analytics (Mixpanel/Amplitude):** Assume flat, linear funnels. They struggle to visualize contextual variations (e.g., how the UI changes dynamically based on an earlier action) without complex, manual tracking plans.
- **Development & Legacy Apps:** Over time, as apps grow, PMs and Developers lose track of the holistic user journey. There is no single source of truth that defines *what* happens when a user clicks a button in a specific state. The "documentation" often becomes the source code itself, which is unreadable to non-engineers.

**The result:** PMs lose track of legacy app journeys, designers waste time drawing arrows, and developers build logic that doesn't match the original design intent.

## 2. Product hypothesis

PRDs may be detailed and still leave designers, engineers, QA, researchers, and analysts interpreting product behavior differently. UXDL reduces that ambiguity by giving each screen, action, and relation a stable address.

The first product hypothesis is deliberately narrow:

> When a team can point to the same addressable UX elements and see their relations, it finds missing or ambiguous behavior earlier and needs fewer clarification cycles during delivery.

UXDL can serve as the canonical behavioral PRD while complementing research repositories, design files, technical RFCs, test plans, and analytics tools. Open metadata lets teams attach the context they need without forcing every discipline into one closed schema.

## 3. Possible use cases

1. **Cross-functional behavior review:** A team reviews the same screens, actions, and relations before implementation.
2. **Compact product definition:** A PM captures the behavior-heavy part of a requirement with fewer repeated words than a traditional narrative document.
3. **Reverse documentation:** A person or tool maps an existing product into a reviewable flow.
4. **Template-guided discovery:** Checkout, authentication, onboarding, and other templates prompt authors about commonly missed paths.
5. **Downstream automation:** Analytics plans, QA cases, design references, tickets, or AI-assisted drafts may later use stable UXDL identifiers.
6. **Story and task slices:** A natural-language story or external task can be mapped onto the relevant UXDL behavior without copying screens or requiring the author to maintain a path list.

## 4. Design principles

1. **Loose content, strict addressability:** IDs and references are predictable; contextual metadata is open.
2. **Human-readable first:** The syntax remains understandable YAML even when an editor is the normal authoring surface.
3. **Progressive detail:** A useful draft does not require a complete formal product model.
4. **Visual-first authoring:** Drawing, forms, placeholders, and templates help people define behavior without editing YAML directly.
5. **Advisory completeness:** The system distinguishes objective errors from review warnings and template suggestions.
6. **Contextual state awareness:** A screen can optionally expose addressable loading, empty, success, error, or domain-specific states.
7. **Tool agnostic:** UXDL is not tied to a framework, design tool, analytics vendor, or implementation language.
8. **Token conscious, not context destructive:** Compactness is valuable only when the flow remains clear enough to prevent misunderstanding.
9. **One requirement, visible in context:** Local requirements belong on the nearest behavior element; cross-path criteria belong to a slice and appear on related screens through generated coverage rather than duplication.

## 5. Success criteria for 0.x

- **Shared interpretation:** Reviewers consistently identify the same intended behavior from the flow.
- **Earlier gap detection:** Teams find missing paths and unresolved decisions before implementation.
- **Lower clarification cost:** Design, engineering, and QA require fewer requirement clarification cycles.
- **Fast authoring:** A user can create and revise a useful flow without learning a formal language.
- **Open context:** Teams attach security, analytics, research, design, QA, or engineering context without breaking the parser.
- **Compactness:** UXDL reduces repeated prose while retaining information needed for delivery.
- **Real-user evidence:** A stable `1.0` is not declared until the format and editor have been tested across multiple teams and product domains.
