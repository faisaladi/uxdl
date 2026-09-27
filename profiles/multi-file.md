# UXDL 0.1 Multi-File Project Profile

> **Status:** Public-editor alpha contract. This profile packages multiple UXDL
> source modules as one logical project without changing UXDL 0.1 behavior or
> reference syntax.

## 1. Why this exists

A useful product specification can become too large for one file even when the
UXDL structure remains correct. Splitting by feature or concern should improve
navigation, ownership, AI retrieval, and change review without creating several
independent sources of truth.

The profile therefore separates:

- the **project**, which owns product identity, root context, module membership,
  and presentation settings;
- **modules**, which own addressable actors, screens, groups, or one extension
  namespace;
- the **assembled UXDL document**, which is a deterministic portable export and
  remains valid UXDL 0.1.

The editor presents one project. Files are an authoring and integration
boundary, not separate user journeys.

## 2. Project manifest

The conventional manifest name is `uxdl.project.yaml`:

```yaml
uxdl_project: "0.1"
uxdl: "0.1"
app: uxdl.dev
title: Public Editor Alpha

metadata:
  owner: product
  entry_screens: [landing_page]

modules:
  - id: public_experience
    file: flows/public.uxdl.yaml
  - id: editor
    file: flows/editor.uxdl.yaml
  - id: product_slices
    file: slices/product.slices.uxdl.yaml

layout:
  direction: left_to_right
```

Reserved manifest fields are:

| Field | Requirement |
| --- | --- |
| `uxdl_project` | Required profile version; currently `"0.1"` |
| `uxdl` | Required assembled UXDL version; currently `"0.1"` |
| `app` | Optional product or service name |
| `title` | Optional project name |
| `metadata` | Optional open root context |
| `modules` | Required ordered list of explicit module declarations |
| `layout` | Optional project-level presentation data |

Module order makes assembled output deterministic. It MUST NOT imply navigation,
priority, or requirement precedence.

## 3. Modules

A module is a partial source artifact with an explicit identity:

```yaml
uxdl_module: "0.1"
id: editor

screens:
  local_editor:
    name: Free Local UXDL Editor
    type: page
    actions:
      open_property:
        relations:
          property_sidebar:
            to: property_sidebar

  property_sidebar:
    name: Element Property Sidebar
    type: overlay
    parent: local_editor
```

A module MAY contribute:

- `actors`;
- `screens`;
- `groups`;
- one complete namespace below `extensions`.

`id` MUST match the corresponding manifest declaration. Root product identity,
root metadata, and layout remain in the manifest so they have one owner.

The initial profile deliberately excludes overrides, inheritance, patches,
recursive imports, and YAML anchors across files.

## 4. Ownership and references

Every actor, screen, group, and slice ID has exactly one source owner in the
assembled project. Duplicate definitions are errors even when their content is
identical.

References remain the short UXDL 0.1 IDs and addresses:

```yaml
to: property_sidebar
```

```text
local_editor.actions.open_property.relations.property_sidebar
```

Authors do not prefix references with a filename or module ID. The project
resolver builds one global index and resolves cross-file references after all
declared modules load. Moving an element between modules therefore does not
change its UXDL address.

One module MUST own a complete extension namespace. For example, a dedicated
module may own `extensions.uxdl_slices`. Splitting one extension namespace
across several modules is deferred until that extension defines deterministic
merge semantics.

## 5. File rules

For the initial public editor:

- module paths are relative to the manifest and use `/` separators;
- absolute paths, URLs, globs, `..`, symlinks, and files outside the project
  package are rejected;
- every file is declared explicitly and appears once;
- paths are compared case-sensitively for portable behavior;
- missing, duplicate, cyclic, or undeclared modules are errors;
- YAML aliases and custom executable tags remain disabled;
- aggregate project limits apply across the manifest and all modules.

Remote modules, package registries, and Git dependencies require separate trust,
locking, availability, and supply-chain design and are not part of this profile.

## 6. Composition and validation

Composition is deterministic:

1. parse and validate the manifest;
2. resolve and parse every declared module within resource limits;
3. verify module identities and single ownership;
4. assemble `actors`, `screens`, `groups`, and owned extension namespaces;
5. validate every parent, actor, group, state, relation, slice, and coverage
   reference against the global index;
6. produce an assembled UXDL 0.1 document or fail without partial success.

Validation reports both the stable UXDL address and its source file. A
cross-file error should read like:

```text
flows/editor.uxdl.yaml · local_editor.actions.open_property.relations.sidebar
Target screen "property_sidebar" is not declared by this project.
```

Core UXDL validity and project-package validity are separate results. A valid
module set can still carry advisory product questions.

## 7. Import, persistence, and export

The public editor uses one internal project model from the beginning, even when
the user opens one file.

Supported paths are:

- open one `.uxdl.yaml` file as a one-module project;
- open `uxdl.project.yaml` plus its declared files;
- open an entire workspace directory via folder import (`webkitdirectory`);
- import or export a `.uxdl.zip` package containing manifest, modules, and binary image assets (`assets/previews/*`);
- selective file inclusion: when importing a folder, ZIP archive, or batch of files, the editor presents an interactive file picker modal allowing users to preview discovered paths, toggle presets (`All`, `YAML Only`, `Deselect All`), uncheck unwanted files (e.g. `README.md`, logs), and choose between replacing or merging into the active project;
- export one assembled `.uxdl.yaml` for tools that only understand UXDL 0.1;
- export readable Markdown or a scoped slice without changing module ownership.

Folder access through browser `webkitdirectory` directory selection or drag-and-drop provides native directory import. Multi-select file pickers and `.uxdl.zip` archive import/export remain the portable fallbacks.

IndexedDB stores project metadata and each exact source file separately. Canvas,
document, slice, and inspector views operate on the assembled in-memory index.
Saving a visual edit writes only the module that owns the changed element.

## 8. AI and MCP behavior

An AI or MCP client should request a project index before reading full modules.
It can then retrieve or patch only:

- the owner module of an address;
- modules needed for dependency closure;
- a named slice and its generated coverage;
- validation findings and affected references.

Every patch names the expected project revision and source module. The system
rejects stale writes, duplicate ownership, broken references, and silent moves
between modules. Exact diffs remain reviewable by humans.

## 9. Public-editor alpha boundary

The first implementation includes:

- the internal multi-file project model;
- one-file compatibility;
- manifest/module loading and deterministic assembly;
- project-aware validation with source locations;
- IndexedDB persistence;
- assembled single-file export;
- ZIP import/export fallback.

Git synchronization, remote modules, concurrent editing, cloud file-level
history, and AI generation remain outside the public-editor alpha.

## 10. Dogfooding migration

The editable uxdl.dev product requirement is
`examples/team-workspace/uxdl.project.yaml` plus the explicitly declared source modules. Its
assembled `examples/team-workspace/uxdl.project.yaml` is a generated single-file
read/export artifact, never a second manually maintained PRD. Regenerate it
from `uxdl.dev/` with the canonical TypeScript CLI:

```bash
npm run compose -- ../product --out ../examples/team-workspace/uxdl.project.yaml
```

The same CLI is the byte-for-byte freshness oracle and never
repairs a stale target while checking it:

```bash
npm run compose -- ../product --check ../examples/team-workspace/uxdl.project.yaml
```

Suggested initial modules are:

```text
examples/team-workspace/uxdl.project.yaml
product/flows/public.uxdl.yaml
product/flows/auth.uxdl.yaml
product/flows/editor.uxdl.yaml
product/flows/pro_workspace.uxdl.yaml
product/slices/product.slices.uxdl.yaml
```

This sequencing prevents a manual split from weakening validation before the
tooling intended to protect it exists.
