#!/usr/bin/env python3
"""
Validate a UXDL 0.1 document against the UXDL PRD Profile (docs/68_UXDL_PRD_Profile.md).

Two independent results, never merged:
  CORE      — UXDL 0.1 structural validity. Errors here mean the document is broken.
  PROFILE   — PRD Profile conformance. Findings here are advisory: they tell you what
              will render in the editor's Overview and what will be empty.

Usage:
  python3 validate_uxdl_prd_profile.py <file.uxdl.yaml> [--json] [--strict]

  --strict  exit 1 when any Tier 1 profile item is missing (default: only CORE errors fail)
"""
import sys, re, json, argparse
from collections import defaultdict

from pathlib import Path

def compose_project_if_needed(file_path):
    """Load UXDL document, auto-composing multi-file projects if manifest is passed."""
    path = Path(file_path).resolve()
    with open(path, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}

    if not isinstance(doc, dict):
        sys.exit(f"Error: {file_path} root must be a YAML mapping")

    if doc.get("uxdl_project") == "0.1":
        # Manifest detected: compose declared modules
        base_dir = path.parent
        composed = {
            "uxdl": doc.get("uxdl", "0.1"),
            "app": doc.get("app", "Unnamed Project"),
            "title": doc.get("title", ""),
            "metadata": doc.get("metadata", {}),
            "actors": {},
            "screens": {},
            "groups": {},
            "extensions": {}
        }
        for mod in doc.get("modules", []):
            mod_file = base_dir / mod.get("file", "")
            if not mod_file.exists():
                print(f"Warning: module file not found: {mod_file}", file=sys.stderr)
                continue
            with open(mod_file, "r", encoding="utf-8") as mf:
                mdata = yaml.safe_load(mf) or {}
            if "actors" in mdata:
                composed["actors"].update(mdata["actors"])
            if "screens" in mdata:
                composed["screens"].update(mdata["screens"])
            if "groups" in mdata:
                composed["groups"].update(mdata["groups"])
            if "extensions" in mdata:
                for ext_k, ext_v in mdata["extensions"].items():
                    if ext_k not in composed["extensions"]:
                        composed["extensions"][ext_k] = {}
                    if isinstance(ext_v, dict):
                        for sub_k, sub_v in ext_v.items():
                            if isinstance(sub_v, dict):
                                if sub_k not in composed["extensions"][ext_k]:
                                    composed["extensions"][ext_k][sub_k] = {}
                                composed["extensions"][ext_k][sub_k].update(sub_v)
                            else:
                                composed["extensions"][ext_k][sub_k] = sub_v
        return composed
    return doc

try:
    import yaml
except ImportError:
    sys.exit("pyyaml required: pip install pyyaml")

ID = re.compile(r"^[a-z][a-z0-9_]*$")
RECOMMENDED_PATHS = {"happy", "error", "guard", "cancel", "retry", "edge", "fallback"}
CHANGE_CLASSES = {"new", "changed", "inherited"}
BUILD_CLASSES = {"shipped", "partial", "planned"}
REFERENCE_TYPES = {"design", "content", "technical", "security", "data", "accessibility", "code_evidence", "task_history"}
REFERENCE_STATUSES = {"approved", "active", "shipped", "partial", "proposed", "history"}
TIER1_META = ["entry_screens", "open_questions", "specification_gaps"]
DEPRECATED_KEYS = {"unspecified_behavior": "specification_gaps", "owners": "owner"}


def addresses(screens):
    out = set(screens)
    for sid, s in screens.items():
        for k in (s.get("states") or {}):
            out.add(f"{sid}.states.{k}")
        for aid, a in (s.get("actions") or {}).items():
            out.add(f"{sid}.actions.{aid}")
            for rid in (a.get("relations") or {}):
                out.add(f"{sid}.actions.{aid}.relations.{rid}")
    return out


def validate(doc):
    core, profile = [], []
    E = lambda m, **k: core.append({"severity": "error", "message": m, **k})
    W = lambda m, **k: core.append({"severity": "warning", "message": m, **k})
    P = lambda tier, m, **k: profile.append({"tier": tier, "message": m, **k})

    if doc.get("uxdl") != "0.1":
        E(f'root `uxdl` must be "0.1", found {doc.get("uxdl")!r}')
    screens = doc.get("screens") or {}
    if not screens:
        E("root `screens` is missing or empty")
        return core, profile, {"screens": 0, "states": 0, "actions": 0, "relations": 0, "requirements": 0, "slices": 0, "acceptance_criteria": 0, "coverage_links": 0, "slices_by_type": {}, "relations_with_when": 0, "relations_with_path": 0, "terminals": 0, "externals": 0, "prd_ref_annotations": 0, "prd_ref_inferred": 0}

    actors = set(doc.get("actors") or {})
    M = doc.get("metadata") or {}
    slices = ((doc.get("extensions") or {}).get("uxdl_slices") or {}).get("slices") or {}

    # ---------- CORE ----------
    for sid, s in screens.items():
        if not ID.match(sid):
            E(f"screen id is not lowercase snake_case", address=sid)
        if not s.get("name"):
            E("screen has no `name`", address=sid)
        if s.get("parent") and s["parent"] not in screens:
            E(f'`parent` targets unknown screen "{s["parent"]}"', address=sid)

    stats = defaultdict(int)
    paths = defaultdict(int)
    reqs = []
    for sid, s in screens.items():
        stats["screens"] += 1
        stats["states"] += len(s.get("states") or {})
        for k in ((s.get("metadata") or {}).get("requirements") or {}):
            reqs.append((sid, "screen"))
        for aid, a in (s.get("actions") or {}).items():
            stats["actions"] += 1
            if a.get("actor") and a["actor"] not in actors:
                W(f'action references undeclared actor "{a["actor"]}"', address=f"{sid}.actions.{aid}")
            for k in ((a.get("metadata") or {}).get("requirements") or {}):
                reqs.append((f"{sid}.actions.{aid}", "action"))
            rels = a.get("relations") or {}
            if not rels:
                W("action has no relations", address=f"{sid}.actions.{aid}")
            for rid, r in rels.items():
                stats["relations"] += 1
                addr = f"{sid}.actions.{aid}.relations.{rid}"
                dest = [k for k in ("to", "external", "end") if r.get(k)]
                if len(dest) != 1:
                    E(f"relation must declare exactly one destination, found {len(dest)}", address=addr)
                if r.get("to"):
                    if r["to"] not in screens:
                        E(f'`to` targets unknown screen "{r["to"]}"', address=addr)
                    elif r.get("state") and r["state"] not in (screens[r["to"]].get("states") or {}):
                        E(f'`state` targets unknown state "{r["to"]}.{r["state"]}"', address=addr)
                if r.get("end"): stats["terminals"] += 1
                if r.get("external"): stats["externals"] += 1
                if r.get("when"): stats["with_when"] += 1
                if r.get("path"):
                    stats["with_path"] += 1
                    paths[r["path"]] += 1

    for gid, g in (doc.get("groups") or {}).items():
        for sc in g.get("screens", []):
            if sc not in screens:
                E(f'group references unknown screen "{sc}"', address=f"groups.{gid}")

    ADDR = addresses(screens)
    for slid, sl in slices.items():
        if sl.get("actor") and sl["actor"] not in actors:
            W(f'slice references undeclared actor "{sl["actor"]}"', address=f"slices.{slid}")
        for sc in sl.get("screens") or []:
            if sc not in screens:
                E(f'slice anchor "{sc}" is not a declared screen', address=f"slices.{slid}")
        cov = (sl.get("coverage") or {}).get("acceptance") or {}
        for crit, refs in cov.items():
            if crit not in (sl.get("acceptance") or {}):
                E(f'coverage references unknown criterion "{crit}"', address=f"slices.{slid}")
            for ref in refs if isinstance(refs, list) else []:
                stats["coverage_links"] += 1
                if ref not in ADDR:
                    E(f'coverage address does not resolve: "{ref}"', address=f"slices.{slid}.{crit}")

    stats["requirements"] = len(reqs)
    stats["slices"] = len(slices)
    stats["acceptance_criteria"] = sum(len(sl.get("acceptance") or {}) for sl in slices.values())
    by_type = defaultdict(int)
    for sl in slices.values():
        by_type[sl.get("type", "unknown")] += 1

    # ---------- PROFILE ----------
    # Detected once, because several checks below behave differently for a living
    # product document (declares `build`) than for a proposal (does not).
    ELS = [(sid, sc.get("metadata") or {}) for sid, sc in screens.items()]
    ELS += [(f"{sid}.actions.{aid}", a.get("metadata") or {})
            for sid, sc in screens.items() for aid, a in (sc.get("actions") or {}).items()]
    declares_build = [(addr, em) for addr, em in ELS if em.get("build")]
    uses_build = bool(declares_build)

    # Expanded requirements and declared authoritative references. Compact string
    # requirements remain valid; an object is only interpreted through the profile's
    # stable fields and is otherwise preserved as source data by consumers.
    registry = M.get("authoritative_references")
    if registry is not None and not isinstance(registry, dict):
        P(1, "`metadata.authoritative_references` must be a mapping", key="authoritative_references")
        registry = {}
    registry = registry or {}

    def reference_id(value):
        if isinstance(value, str):
            return value
        if isinstance(value, dict) and isinstance(value.get("ref"), str):
            return value["ref"]
        return None

    def check_reference_entry(ref_id, entry):
        address = f"metadata.authoritative_references.{ref_id}"
        if not ID.match(ref_id):
            P(1, "reference id must be lowercase snake_case", key="authoritative_references", address=address)
        if not isinstance(entry, dict):
            P(1, "reference entry must be an object", key="authoritative_references", address=address)
            return
        if entry.get("type") not in REFERENCE_TYPES:
            P(1, f"reference type must be one of {sorted(REFERENCE_TYPES)}", key="authoritative_references", address=f"{address}.type")
        if not isinstance(entry.get("label"), str) or not entry.get("label"):
            P(2, "reference has no authoritative label", key="authoritative_references", address=f"{address}.label")
        path = entry.get("path")
        url = entry.get("url")
        if not isinstance(path, str) or not path:
            if not isinstance(url, str) or not re.match(r"^https?://", url):
                P(1, "reference requires a declared workspace-relative path or http(s) URL", key="authoritative_references", address=f"{address}.path")
            elif entry.get("embed") is True:
                P(1, "remote URLs are never fetched or embedded during offline rendering", key="authoritative_references", address=f"{address}.embed")
        else:
            if path.startswith("/") or "\\" in path or any(part == ".." for part in path.split("/")):
                P(1, "reference path must stay within the workspace and cannot traverse parents", key="authoritative_references", address=f"{address}.path")
        if not isinstance(entry.get("section"), str) or not entry.get("section"):
            P(1, "reference requires an exact section or code locator", key="authoritative_references", address=f"{address}.section")
        if not isinstance(entry.get("embed"), bool):
            P(2, "reference must declare boolean `embed` behavior", key="authoritative_references", address=f"{address}.embed")
        if entry.get("status") is not None and entry.get("status") not in REFERENCE_STATUSES:
            P(2, "reference status is not recognized", key="authoritative_references", address=f"{address}.status")

    for ref_id, entry in sorted(registry.items()):
        if isinstance(ref_id, str):
            check_reference_entry(ref_id, entry)

    referenced_ids = []
    def check_requirement_map(requirements, address):
        if requirements is None:
            return
        if not isinstance(requirements, dict):
            P(1, "requirements must be a mapping", key="expanded_requirement", address=address)
            return
        for req_id, value in sorted(requirements.items()):
            req_address = f"{address}.{req_id}"
            if isinstance(value, str):
                continue
            if not isinstance(value, dict):
                P(1, "requirement must be a compact string or expanded object", key="expanded_requirement", address=req_address)
                continue
            statement = value.get("statement") or value.get("title")
            if not isinstance(statement, str) or not statement.strip():
                P(1, "expanded requirement requires `statement` (legacy `title` is accepted)", key="expanded_requirement", address=req_address)
            guidance = value.get("guidance_refs", [])
            for index, ref in enumerate(guidance if isinstance(guidance, list) else [guidance]):
                ref_id = reference_id(ref)
                if not ref_id:
                    P(1, "guidance reference must be an id or `{ref: ...}` object", key="expanded_requirement", address=f"{req_address}.guidance_refs.{index}")
                else:
                    referenced_ids.append((ref_id, f"{req_address}.guidance_refs.{index}"))
            source_ref = value.get("source_ref")
            if source_ref is not None:
                ref_id = reference_id(source_ref)
                if not ref_id:
                    P(1, "source_ref must be an id or `{ref: ...}` object", key="expanded_requirement", address=f"{req_address}.source_ref")
                else:
                    referenced_ids.append((ref_id, f"{req_address}.source_ref"))

    def walk_reference_fields(value, address):
        if isinstance(value, dict):
            if "guidance_refs" in value:
                guidance = value.get("guidance_refs")
                for index, ref in enumerate(guidance if isinstance(guidance, list) else [guidance]):
                    ref_id = reference_id(ref)
                    if not ref_id:
                        P(1, "guidance reference must be an id or `{ref: ...}` object", key="authoritative_references", address=f"{address}.guidance_refs.{index}")
                    else:
                        referenced_ids.append((ref_id, f"{address}.guidance_refs.{index}"))
            for key, child in value.items():
                if key != "guidance_refs":
                    walk_reference_fields(child, f"{address}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk_reference_fields(child, f"{address}.{index}")

    def walk_requirements(value, address):
        if isinstance(value, dict):
            if "requirements" in value:
                check_requirement_map(value.get("requirements"), f"{address}.requirements")
            for key, child in value.items():
                if key != "requirements":
                    walk_requirements(child, f"{address}.{key}")
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk_requirements(child, f"{address}.{index}")

    walk_requirements(screens, "screens")
    walk_requirements(slices, "slices")
    walk_reference_fields(screens, "screens")
    walk_reference_fields(slices, "slices")
    if referenced_ids and not registry:
        P(1, "structured references are used but `metadata.authoritative_references` is missing", key="authoritative_references")
    for ref_id, address in sorted(set(referenced_ids)):
        if ref_id not in registry:
            P(1, f'unknown authoritative reference "{ref_id}"', key="authoritative_references", address=address)
        elif isinstance(registry[ref_id], dict) and registry[ref_id].get("status") in {"proposed", "history"}:
            P(1, f'authoritative reference "{ref_id}" is marked {registry[ref_id].get("status")}', key="authoritative_references", address=address)

    if not doc.get("title"):
        P(1, "root `title` missing — the editor will title the page with the filename", key="title")
    if not doc.get("app"):
        P(2, "root `app` missing — no product badge", key="app")

    for old, new in DEPRECATED_KEYS.items():
        if old in M:
            P(1, f"`metadata.{old}` is the pre-profile name; rename to `metadata.{new}`", key=old)

    for k in TIER1_META:
        if k not in M and DEPRECATED_KEYS.get(k) not in M:
            legacy = [o for o, n in DEPRECATED_KEYS.items() if n == k and o in M]
            if not legacy:
                P(1, f"`metadata.{k}` missing — the matching Overview section will be empty", key=k)

    brief = M.get("product_brief")
    if not isinstance(brief, dict) or not brief:
        if not (M.get("background") and M.get("solution")):
            P(2, "`metadata.product_brief` missing — add source-backed context or legacy `background` and `solution`", key="product_brief")
    else:
        for k in ["nutshell", "background", "solution", "design_direction", "implementation_approach"]:
            if not brief.get(k):
                P(2, f"`metadata.product_brief.{k}` missing", key="product_brief",
                  address=f"metadata.product_brief.{k}")
        target_users = brief.get("target_users")
        if not isinstance(target_users, dict) or not target_users:
            P(2, "`metadata.product_brief.target_users` missing or empty", key="product_brief",
              address="metadata.product_brief.target_users")
        else:
            for uid, user in target_users.items():
                for k in ["description", "problem", "desired_outcome"]:
                    if not isinstance(user, dict) or not user.get(k):
                        P(2, f"target user `{uid}` has no `{k}`", key="product_brief",
                          address=f"metadata.product_brief.target_users.{uid}.{k}")

    for k in ["goals", "success_metrics", "scope", "access_and_permissions"]:
        if k not in M:
            P(2, f"`metadata.{k}` missing", key=k)

    delivery_plan = M.get("delivery_plan")
    if not isinstance(delivery_plan, dict) or not delivery_plan:
        P(2, "`metadata.delivery_plan` missing or empty — no phase objectives or feature map", key="delivery_plan")
    else:
        for phase_id, phase in delivery_plan.items():
            phase_address = f"metadata.delivery_plan.{phase_id}"
            if not isinstance(phase, dict):
                P(2, "delivery phase must be an object", key="delivery_plan", address=phase_address)
                continue
            for k in ["name", "objective", "rationale"]:
                if not phase.get(k):
                    P(2, f"delivery phase has no `{k}`", key="delivery_plan",
                      address=f"{phase_address}.{k}")
            refs = phase.get("slice_refs")
            if not isinstance(refs, list) or not refs:
                P(2, "delivery phase has no `slice_refs`", key="delivery_plan",
                  address=f"{phase_address}.slice_refs")
            else:
                for index, ref in enumerate(refs):
                    target = slices.get(ref)
                    if not isinstance(target, dict) or target.get("type") not in ("story", "task"):
                        P(2, f'delivery phase references unknown or non-delivery slice "{ref}"',
                          key="delivery_plan", address=f"{phase_address}.slice_refs.{index}")
            if not (phase.get("exit_criteria") or phase.get("entry_conditions")):
                P(2, "delivery phase has neither `exit_criteria` nor `entry_conditions`",
                  key="delivery_plan", address=phase_address)

    journeys = {i: s for i, s in slices.items() if s.get("type") == "journey"}
    if not journeys:
        P(1, "no slice with `type: journey` — the Overview has no named entry points and no 'Start here' section")
    for jid, j in journeys.items():
        fh = (j.get("metadata") or {}).get("flow_hint") or {}
        if not fh:
            P(1, f"journey has no `metadata.flow_hint` — 'Trace this journey' will guess", address=f"slices.{jid}")
        else:
            if fh.get("start") not in screens:
                P(1, f'flow_hint.start "{fh.get("start")}" is not a screen', address=f"slices.{jid}")
            for g in fh.get("goal") or []:
                if g not in screens:
                    P(1, f'flow_hint.goal "{g}" is not a screen', address=f"slices.{jid}")
        if not j.get("acceptance"):
            P(1, "journey has no `acceptance` steps", address=f"slices.{jid}")

    delivery = {i: s for i, s in slices.items() if s.get("type") in ("story", "task")}
    if not delivery:
        P(1, "no slice with `type: story` or `type: task` — the Overview has no delivery split")
    for did, dl in delivery.items():
        m = dl.get("metadata") or {}
        if not m.get("covers_requirements"):
            P(1, "delivery slice has no `metadata.covers_requirements`", address=f"slices.{did}")
        if "depends_on" not in m:
            P(2, "delivery slice has no `metadata.depends_on` — sequencing will not render", address=f"slices.{did}")
        if not (dl.get("coverage") or {}).get("acceptance"):
            P(1, "delivery slice has no `coverage` — no traceability to behavior", address=f"slices.{did}")

    if stats["relations"]:
        pct = 100 * stats["with_path"] // stats["relations"]
        if pct < 100:
            P(1, f'only {stats["with_path"]}/{stats["relations"]} relations carry `path:` ({pct}%) — '
                 "branch colouring, route ranking and route naming all degrade", key="relation.path")
    unknown_paths = set(paths) - RECOMMENDED_PATHS
    if unknown_paths:
        P(3, f"non-recommended `path` values in use: {sorted(unknown_paths)}", key="relation.path")

    if not stats["terminals"] and not stats["externals"]:
        P(2, "no relation uses `end: true` or `external:` — no route in Flow view terminates naturally",
          key="end/external")

    prd_refs = inferred = 0
    def walk(o):
        nonlocal prd_refs, inferred
        if isinstance(o, dict):
            if "prd_ref" in o:
                prd_refs += 1
                if o["prd_ref"] == "inferred":
                    inferred += 1
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(screens)
    if prd_refs == 0 and not uses_build:
        P(1, "no element carries `metadata.prd_ref` — nothing traces back to the source document",
          key="prd_ref")

    covered_addr = set()
    for sl in slices.values():
        for refs in ((sl.get("coverage") or {}).get("acceptance") or {}).values():
            covered_addr |= set(refs if isinstance(refs, list) else [])
    anchored = set()
    for sl in slices.values(): anchored |= set(sl.get("screens") or [])
    orphan_screens = sorted(set(screens) - anchored - {a.split(".")[0] for a in covered_addr})
    if orphan_screens:
        P(2, f"{len(orphan_screens)} screen(s) are in no slice anchor and no coverage: "
             f"{', '.join(orphan_screens[:6])}{' …' if len(orphan_screens) > 6 else ''}", key="scope_coverage")

    jcov = set()
    for j in journeys.values():
        for refs in ((j.get("coverage") or {}).get("acceptance") or {}).values():
            jcov |= set(refs if isinstance(refs, list) else [])
    unwalked = [a for a in sorted(ADDR) if ".relations." in a and a not in jcov]
    if journeys and unwalked:
        P(3, f"{len(unwalked)} relation(s) are walked by no journey — branches no narrative describes",
          key="journey_coverage")


    # ---------- READABILITY & DELTA (profile) ----------
    # A journey is only readable if its covered behaviour forms a connected story.
    def journey_subgraph(j):
        """Screens and edges the journey's coverage actually names."""
        raw = [a for refs in ((j.get("coverage") or {}).get("acceptance") or {}).values()
               for a in (refs if isinstance(refs, list) else [])]
        rels, nodes = [], set()
        for a in raw:
            if ".relations." in a:
                rels.append(a)
            elif ".actions." in a:
                rels += [k for k in ADDR if k.startswith(a + ".relations.")]
            else:
                nodes.add(a.split(".")[0])
        edges = []
        for a in rels:
            sid, _, aid, _, rid = a.split(".")
            r = ((screens[sid].get("actions") or {}).get(aid, {}).get("relations") or {}).get(rid) or {}
            nodes.add(sid)
            if isinstance(r, dict) and r.get("to"):
                nodes.add(r["to"]); edges.append((sid, r["to"]))
        return nodes, edges

    for jid, j in journeys.items():
        nodes, edges = journey_subgraph(j)
        start = ((j.get("metadata") or {}).get("flow_hint") or {}).get("start")
        if start and nodes:
            adj = defaultdict(list)
            for u, v in edges: adj[u].append(v)
            seen_n, stack = {start}, [start]
            while stack:
                for v in adj[stack.pop()]:
                    if v not in seen_n: seen_n.add(v); stack.append(v)
            stranded = sorted(nodes - seen_n)
            if stranded:
                P(1, f"journey coverage names {len(stranded)} screen(s) not reachable from "
                     f'flow_hint.start "{start}": {", ".join(stranded[:5])}'
                     f'{" …" if len(stranded) > 5 else ""} — the diagram will draw disconnected fragments',
                  address=f"slices.{jid}", key="journey_connectivity")
        steps = len(j.get("acceptance") or {})
        if steps and not 3 <= steps <= 9:
            P(2, f"journey has {steps} acceptance step(s); 3–9 reads as one story "
                 f'({"too thin to be a journey" if steps < 3 else "split it"})',
              address=f"slices.{jid}", key="journey_length")
        if len(nodes) > 14:
            P(2, f"journey spans {len(nodes)} screens — the diagram will not fit one page; "
                 "consider splitting the narrative", address=f"slices.{jid}", key="journey_size")
        fan = defaultdict(int)
        for u, _ in edges: fan[u] += 1
        wide = [k for k, v in fan.items() if v > 6]
        if wide:
            P(3, f"screen(s) with more than 6 outgoing edges inside this journey: {', '.join(sorted(wide))} — "
                 "the diagram will render wide", address=f"slices.{jid}", key="journey_fanout")

    # Delta modelling: a PRD that changes an existing product references screens it does
    # not specify. Those stubs are legitimate — but only when declared.
    declared = [sid for sid, s in screens.items() if (s.get("metadata") or {}).get("change")]
    for sid, s in screens.items():
        m = s.get("metadata") or {}
        empty = not (s.get("actions") or {}) and not (s.get("states") or {})
        if empty:
            if m.get("change") != "inherited" and not m.get("owned_by"):
                P(1, "screen has no states and no actions — mark it `metadata.change: inherited` "
                     "with `owned_by` or a `prd_ref` to where its behaviour is specified, or model it. "
                     "As written it is indistinguishable from an under-specified screen",
                  address=sid, key="undeclared_stub")
            elif not (m.get("owned_by") or m.get("prd_ref")):
                P(2, "inherited screen names no source for its behaviour — add `owned_by` or `prd_ref`",
                  address=sid, key="inherited_source")
        if m.get("change") and m["change"] not in CHANGE_CLASSES:
            P(3, f'`metadata.change: {m["change"]}` is not one of {sorted(CHANGE_CLASSES)}',
              address=sid, key="change_vocabulary")
    if not declared and not uses_build and any((s.get("metadata") or {}).get("owned_by") or
                            not ((s.get("actions") or {}) or (s.get("states") or {}))
                            for s in screens.values()):
        P(3, "this document references screens it does not specify, but no screen declares "
             "`metadata.change` — classifying screens as new / changed / inherited tells the reader "
             "which behaviour this PRD introduces and which it merely assumes", key="change_absent")
    if declared and len(declared) != len(screens):
        P(2, f"{len(declared)}/{len(screens)} screens declare `metadata.change` — classify all of them "
             "so the reader can see what this document changes versus what it assumes",
          key="change_partial")


    # ---------- BUILD STATUS (living product documents) ----------
    # `change` describes this document's scope. `build` describes reality: what of
    # this specification exists in the product today. A living product document
    # declares build; a proposal does not.
    if uses_build:
        scr_with = sum(1 for sid, s in screens.items() if (s.get("metadata") or {}).get("build"))
        if scr_with != len(screens):
            P(1, f"{scr_with}/{len(screens)} screens declare `metadata.build` — in a living product "
                 "document every screen must say whether it is shipped, partial or planned, or the "
                 "reader cannot tell the product from the plan", key="build_partial")
        for addr, bm in declares_build:
            if bm["build"] not in BUILD_CLASSES:
                P(3, f'`metadata.build: {bm["build"]}` is not one of {sorted(BUILD_CLASSES)}',
                  address=addr, key="build_vocabulary")
                continue
            # An action inherits its screen's evidence. Evidence is only required where
            # the claim is new: on the screen itself, or on an action that disagrees
            # with its screen (a planned action on a shipped screen, and the reverse).
            own = addr.split(".")[0]
            screen_build = (screens[own].get("metadata") or {}).get("build") if own in screens else None
            is_new_claim = ("." not in addr) or bm["build"] != screen_build
            if is_new_claim and bm["build"] in ("shipped", "partial") and not bm.get("build_ref"):
                P(2, f'`build: {bm["build"]}` with no `build_ref` — the claim that this exists in the '
                     "product cannot be checked against the code", address=addr, key="build_evidence")
        for jid, j in journeys.items():
            jb = (j.get("metadata") or {}).get("build")
            covered = {a.split(".")[0] for refs in ((j.get("coverage") or {}).get("acceptance") or {}).values()
                       for a in (refs if isinstance(refs, list) else [])}
            builds = {(screens[c].get("metadata") or {}).get("build") for c in covered if c in screens}
            builds.discard(None)
            if builds and builds <= {"planned"} and jb != "planned":
                P(2, "every screen this journey touches is `planned`, but the journey does not declare "
                     "`metadata.build: planned` — a reader will take the diagram for the product",
                  address=f"slices.{jid}", key="journey_build")
            elif jb == "shipped" and "planned" in builds:
                P(2, "journey declares `build: shipped` but touches planned screens — say which steps "
                     "are not built", address=f"slices.{jid}", key="journey_build_mixed")

    summary = {
        **{k: stats[k] for k in ("screens", "states", "actions", "relations", "requirements",
                                 "slices", "acceptance_criteria", "coverage_links")},
        "slices_by_type": dict(by_type),
        "relations_with_when": stats["with_when"],
        "relations_with_path": stats["with_path"],
        "terminals": stats["terminals"],
        "externals": stats["externals"],
        "prd_ref_annotations": prd_refs,
        "prd_ref_inferred": inferred,
        "path_vocabulary": dict(paths),
    }
    return core, profile, summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    try:
        doc = compose_project_if_needed(args.file)
    except yaml.YAMLError as e:
        print(f"CORE  ✗ invalid YAML: {e}")
        sys.exit(1)

    core, profile, summary = validate(doc)
    errors = [f for f in core if f["severity"] == "error"]
    warnings = [f for f in core if f["severity"] == "warning"]
    t1 = [f for f in profile if f["tier"] == 1]

    if args.json:
        print(json.dumps({"summary": summary, "core": core, "profile": profile}, indent=2))
    else:
        print(f"\n=== {args.file} ===\n")
        print("SUMMARY")
        for k in ("screens", "states", "actions", "relations", "requirements", "slices",
                  "acceptance_criteria", "coverage_links"):
            print(f"  {k:22s} {summary[k]}")
        print(f"  {'slices_by_type':22s} {summary['slices_by_type']}")
        print(f"  {'relations with when':22s} {summary['relations_with_when']}/{summary['relations']}")
        print(f"  {'relations with path':22s} {summary['relations_with_path']}/{summary['relations']}")
        print(f"  {'end / external':22s} {summary['terminals']} / {summary['externals']}")
        print(f"  {'prd_ref (inferred)':22s} {summary['prd_ref_annotations']} ({summary['prd_ref_inferred']})")

        print(f"\nCORE — {len(errors)} error(s), {len(warnings)} warning(s)")
        for f in errors:   print(f"  ✗ {f.get('address','')}  {f['message']}")
        for f in warnings: print(f"  ⚠ {f.get('address','')}  {f['message']}")
        if not core: print("  clean")

        print(f"\nPROFILE — {len(t1)} Tier 1, "
              f"{len([f for f in profile if f['tier']==2])} Tier 2, "
              f"{len([f for f in profile if f['tier']==3])} Tier 3")
        for tier, mark in ((1, "▲"), (2, "▸"), (3, "·")):
            for f in [x for x in profile if x["tier"] == tier]:
                loc = f.get("address") or f.get("key") or ""
                print(f"  {mark} [T{tier}] {loc}  {f['message']}")
        if not profile: print("  full profile conformance")
        print()

    sys.exit(1 if errors or (args.strict and t1) else 0)


if __name__ == "__main__":
    main()
