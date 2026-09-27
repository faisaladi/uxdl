# Contributing to UXDL

Thank you for your interest in contributing to UXDL!

UXDL is an open behavioral standard designed to bring rigor and machine addressability to product specifications.

## Principles for Contributions
1. **Preserve Addressability**: Every screen, state, and action must remain strictly and stably addressable.
2. **Backward Compatibility**: UXDL 0.1 documents must remain valid unless an explicit version transition is approved under [spec/versioning.md](spec/versioning.md).
3. **Deterministic Output**: Tooling and validators must produce deterministic results with zero random heuristics.

## Pull Request Guidelines
- Ensure `python3 tools/validate.py examples/team-workspace/uxdl.project.yaml --strict` passes.
- Keep specifications language-agnostic.
- When proposing a syntax clarification or profile addition, provide matching fixture examples.
