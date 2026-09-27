"""Deterministic implementation-readiness projection for UXDL projects.

This module intentionally resolves only declared local references. It is shared by
the machine-readable ledger and the published handoff renderer so the two outputs
cannot silently disagree about readiness or missing guidance.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import yaml


ROOT = Path.cwd()
REFERENCE_TYPES = {
    "design",
    "content",
    "technical",
    "security",
    "data",
    "accessibility",
    "code_evidence",
    "task_history",
}
AUTHORITY_STATUSES = {"approved", "active", "shipped", "partial"}
READINESS_RESULTS = {
    "ready",
    "ready_with_authoritative_references",
    "blocked_by_specification_gaps",
}


def load_project(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle) or {}
    if not isinstance(value, dict):
        raise ValueError("UXDL project root must be a mapping")
    return value


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _ref_id(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("ref"), str):
        return value["ref"]
    return None


def _collect_refs(value: Any, output: list[str]) -> None:
    for item in _as_list(value):
        ref = _ref_id(item)
        if ref and ref not in output:
            output.append(ref)


def _section_heading_level(line: str) -> int | None:
    match = re.match(r"^\s*(#{1,6})\s+", line)
    return len(match.group(1)) if match else None


def extract_markdown_section(text: str, heading: str) -> str | None:
    """Return one exact Markdown heading and its body, without its siblings."""

    wanted = heading.strip()
    lines = text.splitlines()
    start = None
    level = None
    for index, line in enumerate(lines):
        if line.strip() == wanted:
            start = index
            level = _section_heading_level(line)
            break
    if start is None or level is None:
        return None

    end = len(lines)
    for index in range(start + 1, len(lines)):
        next_level = _section_heading_level(lines[index])
        if next_level is not None and next_level <= level:
            end = index
            break
    section = "\n".join(lines[start:end]).strip()
    return section or None


def _safe_local_path(workspace_root: Path, declared: Any) -> tuple[Path | None, str | None]:
    if not isinstance(declared, str) or not declared:
        return None, "missing local path"
    candidate_path = Path(declared)
    if candidate_path.is_absolute():
        return None, "absolute paths are not allowed"
    if any(part == ".." for part in candidate_path.parts):
        return None, "parent traversal is not allowed"
    root = workspace_root.resolve()
    candidate = (root / candidate_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None, "path escapes the workspace"
    if not candidate.is_file():
        return None, "declared file does not exist"
    return candidate, None


def resolve_reference(
    registry: dict[str, Any],
    ref_id: str,
    workspace_root: Path = ROOT,
) -> dict[str, Any]:
    """Resolve one registry entry and return safe provenance plus embedded text."""

    entry = registry.get(ref_id)
    base: dict[str, Any] = {
        "id": ref_id,
        "resolved": False,
        "authoritative": False,
        "embedded": False,
        "label": ref_id,
        "type": None,
        "path": None,
        "section": None,
        "status": None,
        "error": None,
        "embedded_text": None,
    }
    if not isinstance(entry, dict):
        base["error"] = "reference id is not declared in metadata.authoritative_references"
        return base

    base.update(
        {
            "label": entry.get("label", ref_id),
            "type": entry.get("type"),
            "path": entry.get("path"),
            "section": entry.get("section"),
            "status": entry.get("status"),
        }
    )
    if entry.get("type") not in REFERENCE_TYPES:
        base["error"] = "reference type is invalid"
        return base

    declared_url = entry.get("url")
    if not entry.get("path") and isinstance(declared_url, str) and re.match(r"^https?://", declared_url):
        base["resolved"] = True
        base["authoritative"] = entry.get("status") in AUTHORITY_STATUSES
        if entry.get("embed"):
            base["resolved"] = False
            base["authoritative"] = False
            base["error"] = "remote URLs are never fetched or embedded during offline rendering"
        return base

    path, path_error = _safe_local_path(workspace_root, entry.get("path"))
    if path_error:
        base["error"] = path_error
        return base

    try:
        source_text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        base["error"] = "declared file is not UTF-8 text"
        return base

    locator = entry.get("section")
    if not isinstance(locator, str) or not locator.strip():
        base["error"] = "reference requires an exact section or code locator"
        return base

    if path.suffix.lower() in {".md", ".markdown"}:
        excerpt = extract_markdown_section(source_text, locator)
        if excerpt is None:
            base["error"] = "exact Markdown heading was not found"
            return base
    elif locator not in source_text:
        base["error"] = "code or structured-data locator was not found"
        return base
    else:
        excerpt = None

    status = entry.get("status")
    base["resolved"] = True
    base["authoritative"] = status in AUTHORITY_STATUSES
    base["embedded"] = bool(entry.get("embed"))
    if base["embedded"] and excerpt is not None:
        base["embedded_text"] = excerpt
    elif base["embedded"]:
        base["error"] = "only Markdown sections can be embedded deterministically"
        base["resolved"] = False
        base["authoritative"] = False
    return base


def _requirements(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    raw = metadata.get("requirements")
    if not isinstance(raw, dict):
        return []
    output: list[dict[str, Any]] = []
    for requirement_id in sorted(raw):
        value = raw[requirement_id]
        if isinstance(value, str):
            output.append(
                {
                    "id": requirement_id,
                    "statement": value,
                    "expanded": False,
                    "raw": value,
                    "rationale": None,
                    "verification": None,
                    "guidance_refs": [],
                    "source_ref": None,
                    "provenance": None,
                    "priority": None,
                }
            )
            continue
        if isinstance(value, dict):
            statement = value.get("statement") or value.get("title")
            output.append(
                {
                    "id": requirement_id,
                    "statement": statement if isinstance(statement, str) else None,
                    "expanded": True,
                    "raw": value,
                    "rationale": value.get("rationale"),
                    "verification": value.get("verification"),
                    "guidance_refs": [
                        item
                        for item in (
                            _ref_id(ref)
                            for ref in _as_list(value.get("guidance_refs"))
                        )
                        if item
                    ],
                    "source_ref": value.get("source_ref"),
                    "provenance": value.get("provenance"),
                    "priority": value.get("priority"),
                }
            )
            continue
        output.append(
            {
                "id": requirement_id,
                "statement": None,
                "expanded": False,
                "raw": value,
                "rationale": None,
                "verification": None,
                "guidance_refs": [],
                "source_ref": None,
                "provenance": None,
                "priority": None,
            }
        )
    return output


def _walk_nested_metadata(screen: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            metadata = value.get("metadata")
            if isinstance(metadata, dict):
                found.append(metadata)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(screen)
    return found


def _build_evidence(metadata: dict[str, Any]) -> dict[str, Any]:
    build = metadata.get("build")
    return {
        "status": build if build in {"shipped", "partial", "planned"} else "unspecified",
        "build_ref": metadata.get("build_ref"),
        "description": metadata.get("description"),
    }


def _dimension_status(
    refs: list[dict[str, Any]],
    types: set[str],
    *,
    direct: bool = False,
) -> str:
    relevant = [ref for ref in refs if ref.get("type") in types]
    if any(not ref.get("resolved") for ref in relevant):
        return "unresolved"
    if direct:
        return "direct"
    if relevant:
        return "referenced"
    return "missing"


def build_screen_readiness(
    project: dict[str, Any],
    screen_id: str,
    screen: dict[str, Any],
    workspace_root: Path = ROOT,
) -> dict[str, Any]:
    metadata = screen.get("metadata") if isinstance(screen.get("metadata"), dict) else {}
    registry = project.get("metadata", {}).get("authoritative_references", {})
    registry = registry if isinstance(registry, dict) else {}
    metadata_refs: list[str] = []
    relationships: dict[str, list[str]] = {}

    def collect_guidance(value: Any) -> None:
        for item in _as_list(value):
            ref_id = _ref_id(item)
            if not ref_id:
                continue
            if ref_id not in metadata_refs:
                metadata_refs.append(ref_id)
            if isinstance(item, dict) and isinstance(item.get("relationship"), str):
                relationships.setdefault(ref_id, [])
                if item["relationship"] not in relationships[ref_id]:
                    relationships[ref_id].append(item["relationship"])

    _collect_refs(metadata.get("guidance_refs"), metadata_refs)
    collect_guidance(metadata.get("guidance_refs"))
    nested_metadata = _walk_nested_metadata(screen)
    for nested in nested_metadata:
        collect_guidance(nested.get("guidance_refs"))
        for requirement in _requirements(nested):
            collect_guidance(requirement.get("guidance_refs"))
            _collect_refs(requirement.get("source_ref"), metadata_refs)
    _collect_refs(metadata.get("specification_gaps_ref"), [])

    resolved_refs = [resolve_reference(registry, ref_id, workspace_root) for ref_id in metadata_refs]
    for reference in resolved_refs:
        if relationships.get(reference["id"]):
            reference["relationship"] = "; ".join(relationships[reference["id"]])
    authoritative_sources = [
        {
                key: reference.get(key)
                for key in ("id", "label", "type", "path", "section", "status", "embedded", "relationship")
        }
        for reference in resolved_refs
        if reference.get("resolved") and reference.get("authoritative")
    ]

    requirements = _requirements(metadata)
    all_requirements = requirements[:]
    for nested in nested_metadata:
        if nested is metadata:
            continue
        all_requirements.extend(_requirements(nested))

    states = screen.get("states") if isinstance(screen.get("states"), dict) else {}
    actions = screen.get("actions") if isinstance(screen.get("actions"), dict) else {}
    has_relations = False
    for action in actions.values():
        if isinstance(action, dict) and isinstance(action.get("relations"), dict) and action["relations"]:
            has_relations = True
            break

    build_status = metadata.get("build")
    behavior_status = "complete" if (states or actions or metadata.get("description")) else "missing"
    if build_status == "partial" and behavior_status == "complete":
        behavior_status = "partial"
    requirement_status = "complete" if all_requirements else "missing"
    if all_requirements and any(item.get("statement") is None for item in all_requirements):
        requirement_status = "partial"

    has_exact_copy = isinstance(metadata.get("copy"), dict)
    is_public_page = metadata.get("route", "").startswith("/") and screen_id not in {
        "editor",
    }
    content_status = _dimension_status(
        resolved_refs,
        {"content"},
        direct=has_exact_copy or (not is_public_page and bool(screen.get("name"))),
    )
    if content_status == "missing" and screen_id not in {
        "landing_page",
        "docs",
        "pricing",
        "enterprise",
        "mcp_page",
        "templates",
        "auth_login",
        "onboarding_profile",
        "dashboard",
        "cloud_project_editor",
        "shared_project",
        "billing_checkout",
    }:
        content_status = "direct"

    design_status = _dimension_status(
        resolved_refs,
        {"design", "accessibility"},
    )
    technical_status = _dimension_status(
        resolved_refs,
        {"technical", "security", "data"},
        direct=bool(metadata.get("data_operations")) or bool(metadata.get("route")) and bool(metadata.get("build_ref")),
    )
    verification_status = _dimension_status(
        resolved_refs,
        {"task_history"},
        direct=has_relations or any(item.get("verification") for item in all_requirements),
    )

    gaps: list[dict[str, Any]] = []
    root_gaps = project.get("metadata", {}).get("specification_gaps", {})
    root_gaps = root_gaps if isinstance(root_gaps, dict) else {}
    for gap_id in _as_list(metadata.get("specification_gaps_ref")):
        if isinstance(gap_id, str):
            gaps.append(
                {
                    "id": gap_id,
                    "statement": root_gaps.get(gap_id, "Declared specification gap has no root explanation."),
                    "address": screen_id,
                }
            )

    for reference in resolved_refs:
        if not reference.get("resolved") or not reference.get("authoritative"):
            reason = reference.get("error") or "reference is not authoritative"
            gaps.append(
                {
                    "id": f"reference:{reference['id']}",
                    "statement": f"Authoritative reference {reference['id']} cannot be used: {reason}.",
                    "address": screen_id,
                    "reference_id": reference["id"],
                }
            )

    dimensions = {
        "behavior": behavior_status,
        "requirements": requirement_status,
        "design": design_status,
        "content": content_status,
        "technical": technical_status,
        "verification": verification_status,
    }
    dimension_labels = {
        "behavior": "behavior definition",
        "requirements": "requirements",
        "design": "design guidance",
        "content": "content/copy guidance",
        "technical": "technical guidance",
        "verification": "verification guidance",
    }
    for dimension, status in dimensions.items():
        if status in {"missing", "unresolved"}:
            gaps.append(
                {
                    "id": f"{screen_id}.{dimension}",
                    "statement": f"This screen has {status} {dimension_labels[dimension]}; an engineer would otherwise need to invent it.",
                    "address": screen_id,
                }
            )

    phase_1 = project.get("metadata", {}).get("implementation_readiness", {}).get("phase_1_screen_refs", [])
    phase_2 = project.get("metadata", {}).get("implementation_readiness", {}).get("phase_2_screen_refs", [])
    phase = "phase_1" if screen_id in phase_1 else "phase_2" if screen_id in phase_2 else "unclassified"

    has_references = any(reference.get("resolved") and reference.get("authoritative") for reference in resolved_refs)
    result = "blocked_by_specification_gaps" if gaps else (
        "ready_with_authoritative_references" if has_references else "ready"
    )

    return {
        "id": screen_id,
        "name": screen.get("name", screen_id),
        "type": screen.get("type"),
        "parent": screen.get("parent"),
        "phase": phase,
        "build": _build_evidence(metadata),
        "dimensions": dimensions,
        "requirements": all_requirements,
        "behavior": {
            "states": sorted(states),
            "actions": sorted(actions),
            "has_relations": has_relations,
        },
        "guidance_refs": [
            {
                key: reference.get(key)
                for key in ("id", "label", "type", "path", "section", "status", "relationship", "resolved", "authoritative", "embedded", "error", "embedded_text")
            }
            for reference in resolved_refs
        ],
        "authoritative_sources": authoritative_sources,
        "gaps": gaps,
        "readiness": result,
    }


def build_readiness(project: dict[str, Any], workspace_root: Path = ROOT) -> dict[str, Any]:
    screens = project.get("screens")
    if not isinstance(screens, dict):
        raise ValueError("UXDL project must contain a screens mapping")
    records = {
        screen_id: build_screen_readiness(project, screen_id, screen, workspace_root)
        for screen_id, screen in sorted(screens.items())
        if isinstance(screen, dict)
    }
    counts = {result: sum(record["readiness"] == result for record in records.values()) for result in READINESS_RESULTS}
    phase_counts: dict[str, dict[str, int]] = {}
    for phase in ("phase_1", "phase_2", "unclassified"):
        phase_counts[phase] = {
            result: sum(record["phase"] == phase and record["readiness"] == result for record in records.values())
            for result in READINESS_RESULTS
        }
    return {
        "profile": "docs/73_Implementation_Readiness_Profile.md",
        "source": "results/uxdl_dev.composed.uxdl.yaml",
        "screen_count": len(records),
        "summary": counts,
        "phase_summary": phase_counts,
        "screens": records,
    }


def write_readiness(path: str | Path, readiness: dict[str, Any]) -> None:
    output = Path(path)
    output.write_text(
        __import__("json").dumps(readiness, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
