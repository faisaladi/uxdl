# UXDL: User Experience Description Language

[![CI](https://github.com/faisaladi/uxdl/actions/workflows/ci.yml/badge.svg)](https://github.com/faisaladi/uxdl/actions)
[![Format: UXDL 0.1](https://img.shields.io/badge/UXDL-0.1-blue.svg)](spec/specification.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**UXDL is a human- and machine-readable specification language for modeling observable product behavior.**

It replaces ambiguous prose PRDs with a deterministic behavioral contract: **screens, states, actions, and relations**. UXDL provides an authoritative bridge connecting Product Managers, Designers, Software Engineers, and Autonomous AI Coding Agents.

---

## Why UXDL?

Natural language requirements leave product behavior implicit. Edge cases, recovery flows, and state branches are often reconstructed on the fly during development or missed until production.

UXDL makes behavior explicit, inspectable, and addressable:
- **Strict Addressability**: Every screen, state, and action has a stable coordinate (e.g. `login.actions.submit_credentials.relations.failure`).
- **AI Agent Native**: Autonomous coding agents (Cursor, Claude Code, Antigravity) consume UXDL to plan, build, and verify features without hallucinating flow boundaries.
- **Deterministic Validation**: Validate structural correctness, coverage, and implementation readiness with pure Python scripts.
- **Modular & Portable**: Split large systems into maintainable YAML modules or assemble them into single-file portable contracts.

---

## 30-Second Syntax Preview

```yaml
uxdl: "0.1"
app: TeamWorkspace
title: User Authentication

actors:
  visitor:
    name: Visitor
    type: human

screens:
  login:
    name: Log In Screen
    type: page
    states:
      default:
        name: Default
      invalid_credentials:
        name: Invalid Credentials Error
    actions:
      submit_credentials:
        name: Submit Credentials
        actor: visitor
        relations:
          success:
            to: dashboard
            path: happy
            when: credentials are valid
          failure:
            to: login.states.invalid_credentials
            path: error
            when: credentials invalid
```

---

## Repository Structure

```text
uxdl/
├── spec/                          # Normative Specification (The Core)
│   ├── overview.md                # Principles, problem statement, hypothesis
│   ├── specification.md           # Canonical UXDL 0.1 grammar & semantics
│   └── versioning.md              # Version governance and compatibility guidelines
├── profiles/                      # Standard Profiles & Extensions
│   ├── slices.md                  # Slices extension (story/task journeys)
│   ├── multi-file.md              # Multi-file packaging profile
│   ├── agent-harness.md           # AI Agent task decomposition harness
│   ├── prd-profile.md             # PRD profile rules
│   └── readiness.md               # Implementation readiness ledger profile
├── schema/                        # Machine-readable schemas
│   └── uxdl-0.1.schema.json       # JSON Schema definition
├── tools/                         # Reference Tools & Validators
│   ├── validate.py                # Standalone profile & structure validator
│   ├── readiness.py               # Readiness ledger generator
│   └── requirements.txt
├── examples/                      # Canonical Reference Project
│   └── team-workspace/            # Multi-file SaaS showcase
└── guides/                        # Community Guides
    ├── user-guide.md              # Guide to reading & writing UXDL
    ├── test-generation.md         # Deriving test cases from UXDL
    └── prompts/                   # Prompts for LLM-based generation
```

---

## Quickstart

### 1. Validate a UXDL Document or Multi-File Project

```bash
# Clone the repository
git clone https://github.com/faisaladi/uxdl.git
cd uxdl

# Install dependencies (only pyyaml is required)
pip install -r tools/requirements.txt

# Validate the reference SaaS project
python3 tools/validate.py examples/team-workspace/uxdl.project.yaml --strict
```

### 2. Use with AI Coding Assistants

UXDL publishes [`llms.txt`](llms.txt) and [`llms-full.txt`](llms-full.txt) directly in this repository.
You can reference `llms.txt` in Cursor, Claude Code, Windsurf, or Antigravity to teach your agent how to generate and adhere to UXDL contracts.

---

## Contributing

We welcome community feedback, RFCs, and tooling adapters. Please see [CONTRIBUTING.md](CONTRIBUTING.md) and our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
