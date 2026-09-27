# 64. Guide to Generating Test Cases from UXDL Specifications

> **Status:** Active standard guide for QA engineers, developers, and AI coding agents.  
> **Purpose:** Document deterministic methodology and patterns for deriving Unit, Integration/E2E, and Regression test suites directly from UXDL 0.1 YAML specifications.

---

## 1. Executive Summary & Core Principle

In traditional software development, test cases are derived from informal prose PRDs or Figma mocks. This leads to missing edge cases, untested error states, and unmaintained test suites.

UXDL eliminates this ambiguity by providing a **finite, deterministic state machine and behavioral graph** with stable addressable identifiers (`#screen.state`, `#screen.action`, `#screen.action.relation`).

```
UXDL YAML Specification (Source of Truth)
   │
   ├─► 1. Unit Tests (States & Actions)        ──► Vitest / Jest / React Testing Library
   ├─► 2. E2E / Integration Tests (Relations)  ──► Playwright / Cypress
   └─► 3. Regression & Traceability (Slices)   ──► CI Coverage Gate
```

---

## 2. Unit & Component Testing (`screens.<id>.states` & `actions`)

### Mapping Rules
- Every declared **Screen State** (`screens.<id>.states.<state_id>`) maps to an explicit component render assertion test.
- Every declared **Screen Action** (`screens.<id>.actions.<action_id>`) maps to a user event trigger test.

### UXDL Source Example (`product/flows/auth.uxdl.yaml`)

```yaml
screens:
  auth_login:
    name: Public Email OTP Login
    type: page
    states:
      default: Email input form ready
      loading: OTP submission in progress
      invalid_email: Invalid email format message shown
    actions:
      submit_login:
        name: Submit Email OTP
        relations:
          on_success:
            to: auth_verify_otp
```

### Generated Unit Test Suite (Vitest + React Testing Library)

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { LoginPage } from './login-page';

describe('UXDL Screen: #auth_login', () => {
  // Derived from UXDL Address: #auth_login.states.default
  it('renders default state with email input ready', () => {
    render(<LoginPage state="default" />);
    expect(screen.getByRole('textbox', { name: /email/i })).toBeInTheDocument();
  });

  // Derived from UXDL Address: #auth_login.states.loading
  it('renders loading state during submission', () => {
    render(<LoginPage state="loading" />);
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });

  // Derived from UXDL Address: #auth_login.states.invalid_email
  it('renders invalid_email state message', () => {
    render(<LoginPage state="invalid_email" />);
    expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
  });

  // Derived from UXDL Address: #auth_login.actions.submit_login
  it('triggers submit_login action handler on button click', () => {
    const onSubmit = vi.fn();
    render(<LoginPage state="default" onSubmit={onSubmit} />);
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));
    expect(onSubmit).toHaveBeenCalledTimes(1);
  });
});
```

---

## 3. Integration & E2E Flow Testing (`actions.<id>.relations.<rel_id>.to`)

### Mapping Rules
- Every directed **Relation Edge** (`to: <target_screen_id>`) maps to an E2E navigation path test.
- Transition assertions verify that triggering `actions.<action_id>` lands on the expected target screen.

### UXDL Relation Graph Path

$$\text{\#auth\_login.actions.submit\_login} \xrightarrow{\text{on\_success}} \text{\#auth\_verify\_otp}$$

### Generated E2E Test Suite (Playwright)

```typescript
import { test, expect } from '@playwright/test';

test.describe('UXDL Flow Relation: #auth_login -> #auth_verify_otp', () => {
  test('Path: submit_login triggers transition to auth_verify_otp', async ({ page }) => {
    // 1. Navigate to origin screen (#auth_login)
    await page.goto('/login');

    // 2. Interact with UXDL Action element (#auth_login.actions.submit_login)
    await page.fill('[data-uxdl="auth_login.email_input"]', 'user@example.com');
    await page.click('[data-uxdl="auth_login.actions.submit_login"]');

    // 3. Assert transition to target screen (#auth_verify_otp)
    await expect(page).toHaveURL('/verify-otp');
    await expect(page.locator('[data-uxdl="auth_verify_otp"]')).toBeVisible();
  });
});
```

---

## 4. Regression Testing & Traceability Gates (`uxdl_slices`)

### Mapping Rules
- Use `data-uxdl="<screen_id>.<action_id>"` DOM attributes in application markup.
- Annotate test code with `// @uxdl-coverage: #<screen_id>.<state_id>` comments.
- CI pipeline validates that **100% of declared UXDL states and relations have matching tests**.

### Coverage Matrix Table

| UXDL Address | Element Type | Coverage Target | Test File Location | Status |
| :--- | :--- | :--- | :--- | :--- |
| `#local_editor.states.default` | State | Component Render | `editor-workspace.test.tsx` | `PASSED` |
| `#local_editor.actions.folder_import` | Action | Modal Trigger | `import-file-picker-modal.test.tsx` | `PASSED` |
| `#local_editor.actions.yaml_export` | Action | File Download | `editor-workspace.test.tsx` | `PASSED` |

---

## 5. How Tests Are Generated: AI-Native Generation + Deterministic CI Gate

In modern AI-assisted development (Cursor, Claude Code, Antigravity), the recommended model is **AI-Native Generation + Deterministic CI Audit**:

```
                       ┌─────────────────────────────────────────────────────────────┐
                       │                   UXDL Specification                        │
                       └──────────────────────────────┬──────────────────────────────┘
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       │                                                             │
                       ▼                                                             ▼
       ┌──────────────────────────────┐                              ┌──────────────────────────────┐
       │ 1. AI Agent (Generator)      │                              │ 2. CI Gate (Auditor)         │
       │    (Cursor / Claude / AGY)   │                              │    (Deterministic CLI Script)│
       ├──────────────────────────────┤                              ├──────────────────────────────┤
       │ • Reads UXDL & Component     │                              │ • 0 Tokens, 100% Deterministic│
       │ • Writes DOM assertions      │                              │ • Scans test coverage tags   │
       │ • Executes & verifies tests  │                              │ • Blocks un-tested PRs       │
       └──────────────┬───────────────┘                              └──────────────┬───────────────┘
                      │                                                             │
                      └──────────────────────────────┬──────────────────────────────┘
                                                     │
                                                     ▼
                                     ┌──────────────────────────────┐
                                     │ Verified PR & Test Coverage  │
                                     └──────────────────────────────┘
```

---

## 6. Why the AI Agent is the Primary Test Generator

While deterministic scripts can output structural stubs (`it('handles state: loading')`), **AI agents (LLMs with tool execution) are the primary test generators** for two key reasons:

### 1. Semantic Understanding of `metadata.requirements`
Rich contextual requirements (business rules, error conditions, task IDs like `internal-task`, validation rules, and human descriptions) require semantic reasoning. 

An AI agent reads requirement descriptions like `"Selective multi-file folder import with file inclusion/exclusion checklist modal"` and translates them directly into meaningful DOM assertions (e.g. testing checkbox toggles, filter chips, and selective payload building).

### 2. Dual Capability: Reasoning + Tool Execution
Modern AI agents operate with tool use (`run_command`, AST tools, shell access). An AI agent can:
- **Parse the UXDL YAML** to identify exact address targets (`#screen.state`, `#screen.action`).
- **Inspect actual component source code** (`.tsx` / `.vue`) to match exact prop names and DOM selectors.
- **Generate and execute the test suite** (`npm run test`), fixing any initial syntax or setup mismatches autonomously before committing.

---

## 7. Recommended Workflow Summary

1. **Generation (AI Agent)**: The developer prompts the AI Agent: *"Generate unit & E2E tests for #auth_login based on its UXDL spec."* The AI Agent inspects the component, writes complete test assertions, and runs `npm run test` to verify.
2. **Verification (Deterministic Script in CI)**: A deterministic CLI tool (`uxdl audit-tests`) runs in GitHub Actions, scanning code for `// @uxdl-coverage #screen.state` tags. It ensures 100% of UXDL addresses are covered before PR merge.
