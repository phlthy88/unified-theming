# Handoff Protocol: Multi-Agent Collaboration

**Version:** 1.0
**Date:** October 21, 2025
**Project:** Unified Theming v1.0.0
**Agents:** Claude Code, Qwen Coder, Opencode AI

---

## Executive Summary

This document defines the formal handoff protocol for agent collaboration during the Unified Theming project. It specifies deliverables, formats, triggers, validation criteria, and acknowledgment procedures for each week of the 11-13 week timeline.

**Core Principles:**
1. **Explicit Deliverables**: Every handoff requires a concrete artifact (file/report)
2. **Clear Triggers**: Git tags signal handoff completion
3. **Validation Gates**: Numerical thresholds prevent premature handoffs
4. **Acknowledgment Required**: Receiving agent confirms receipt and understanding
5. **Rollback Protocol**: Failed handoffs trigger remediation before proceeding

---

## Agent Specialization

### Claude Code (Architect/Designer)
**Responsibilities:**
- Test architecture design
- Integration test scenario design
- UX mockups and specifications
- Documentation authoring (user-facing)
- Code review (quality gate)

**Primary Outputs:** Markdown specs, mockup files, documentation

### Qwen Coder (Implementation)
**Responsibilities:**
- Test implementation (pytest)
- Feature implementation (GUI, handlers)
- Performance optimization
- Bug fixes from QA

**Primary Outputs:** Python code, test files, coverage reports

### Opencode AI (QA/DevOps)
**Responsibilities:**
- Coverage validation
- Gap analysis
- Performance benchmarking
- Packaging (Flatpak, AppImage, PPA, AUR)
- Release validation

**Primary Outputs:** QA reports, benchmark results, packages

---

## Week 1: Foundation Testing

### Handoff 1A: Claude → Qwen (Test Plan)

**Deliverable:** `docs/test_plan_week1.md`

**Content Requirements:**
- [ ] Test cases for color.py (normalization, translation, validation, contrast)
- [ ] Test cases for manager.py (orchestration, rollback, error aggregation)
- [ ] Test cases for config.py (backup, restore, pruning)
- [ ] Test cases for gtk_handler.py (GTK2/3/4/libadwaita CSS generation)
- [ ] Coverage targets per module
- [ ] Edge cases and error scenarios
- [ ] Fixture requirements

**Format:** Markdown tables with columns: Test ID, Module, Function, Scenario, Expected Result, Priority (P0/P1/P2)

**Trigger:** Git commit with message prefix `[HANDOFF]` + tag `handoff/week1-plan`

**Acknowledgment:** Qwen creates `docs/test_implementation_week1.md` with:
- Implementation approach per module
- Estimated LOC per test file
- Dependency identification (fixtures, mocks)
- Timeline confirmation (Day 1-2: color, Day 2-3: manager, etc.)

**Deadline:** Week 1, Day 1 (09:00)

---

### Handoff 1B: Qwen → Opencode (Test Implementation Complete)

**Deliverable:**
1. Test files: `tests/test_color_utils.py`, `tests/test_manager_integration.py`, `tests/test_config_backup.py`, `tests/test_gtk_handler.py`
2. Coverage report: `htmlcov/index.html` + `coverage.xml`
3. Implementation summary: `docs/test_implementation_week1.md` (updated with actuals)

**Validation Criteria:**
- [ ] `color.py`: ≥80% line coverage
- [ ] `manager.py`: ≥85% line coverage
- [ ] `config.py`: ≥70% line coverage
- [ ] `gtk_handler.py`: ≥70% line coverage
- [ ] All tests pass (`pytest` exit code 0)
- [ ] No blocking TODOs in test files
- [ ] Fixtures documented in `conftest.py`

**Trigger:** Git commit with message prefix `[QA-READY]` + tag `qa/week1-tests`

**Acknowledgment:** Opencode creates `docs/qa_report_week1.md` with:
- Coverage validation (pass/fail per module)
- Gap analysis (untested functions/branches)
- Test quality assessment (assertion count, edge case coverage)
- Recommendations for Week 2

**Deadline:** Week 1, Day 5 (17:00)

---

## Week 2: Handler Testing + v0.5 Release

### Handoff 2A: Qwen → Opencode (Handler Tests Complete)

**Deliverable:**
1. Test files: `tests/test_qt_handler.py`, `tests/test_flatpak_handler.py`, `tests/test_snap_handler.py`
2. Updated coverage report
3. Implementation notes: `docs/test_implementation_week2.md`

**Validation Criteria:**
- [ ] `qt_handler.py`: ≥85% line coverage
- [ ] `flatpak_handler.py`: ≥75% line coverage
- [ ] `snap_handler.py`: ≥60% line coverage
- [ ] All new tests pass
- [ ] No regressions in Week 1 tests

**Trigger:** Tag `qa/week2-handlers`

**Acknowledgment:** Opencode validates and creates `docs/v0.5_readiness_report.md`

**Deadline:** Week 2, Day 4 (17:00)

---

### Handoff 2B: Qwen + Opencode → Claude (v0.5 Release Prep)

**Deliverable:**
1. **From Qwen:** Release notes draft (`docs/RELEASE_NOTES_v0.5.md`) with:
   - New features (CLI commands)
   - Test coverage summary
   - Known limitations (no GUI, container support partial)
2. **From Opencode:**
   - Final QA report (`docs/v0.5_readiness_report.md`)
   - Installation test results (pip install -e ., CLI smoke tests)

**Validation Criteria:**
- [ ] Overall coverage ≥80%
- [ ] All critical modules ≥70%
- [ ] CLI commands functional (`list`, `apply`, `backup`, `restore`)
- [ ] No P0 bugs in QA report
- [ ] Installation tested on clean Ubuntu 22.04/24.04

**Trigger:** Tag `release/v0.5-candidate`

**Acknowledgment:** Claude reviews release notes, polishes documentation, and creates:
- `docs/RELEASE_NOTES_v0.5.md` (final)
- `docs/INSTALL_v0.5.md` (installation guide)
- Approves with tag `release/v0.5-approved`

**Deadline:** Week 2, Day 5 (17:00)

---

## Week 3: Integration & Performance Testing

### Handoff 3A: Claude → Qwen (Integration Test Scenarios)

**Deliverable:** `docs/integration_test_scenarios.md`

**Content Requirements:**
- [ ] End-to-end workflow scenarios (happy path)
- [ ] Multi-handler coordination scenarios
- [ ] Error recovery scenarios (partial failure, rollback)
- [ ] Theme switching scenarios (A→B→A consistency)
- [ ] Expected behavior per scenario
- [ ] Validation checkpoints

**Format:** Gherkin-style scenarios (Given/When/Then) or narrative descriptions

**Trigger:** Tag `handoff/week3-integration`

**Acknowledgment:** Qwen creates `tests/test_integration.py` skeleton and confirms approach

**Deadline:** Week 3, Day 2 (12:00)

---

### Handoff 3B: Claude → Qwen (Performance Benchmark Specs)

**Deliverable:** `docs/performance_benchmarks.md`

**Content Requirements:**
- [ ] Benchmark definitions (theme discovery <5s for 100 themes, etc.)
- [ ] Test data requirements (500+ themes, corrupted themes, etc.)
- [ ] Success criteria per benchmark
- [ ] Stress test scenarios (concurrency, low memory, rapid switching)
- [ ] Memory leak detection approach

**Trigger:** Tag `handoff/week3-performance`

**Acknowledgment:** Qwen creates `tests/test_performance_stress.py` and confirms tooling (pytest-benchmark, memory_profiler)

**Deadline:** Week 3, Day 3 (12:00)

---

### Handoff 3C: Qwen → Opencode (Phase 2 Complete)

**Deliverable:**
1. All test files (integration, CLI, performance, stress)
2. Final coverage report
3. Performance benchmark results (`docs/benchmark_results_week3.md`)
4. Phase 2 completion summary (`docs/phase2_completion.md`)

**Validation Criteria (CHECKPOINT: Proceed to GUI?):**
- [ ] Overall coverage ≥80%
- [ ] All critical modules ≥70%
- [ ] Integration tests pass (100% scenarios)
- [ ] Performance benchmarks meet targets
- [ ] Stress tests complete without crashes
- [ ] No P0/P1 bugs open

**Trigger:** Tag `milestone/phase2-complete`

**Acknowledgment:** Opencode validates all criteria and creates:
- `docs/phase2_validation_report.md`
- GO/NO-GO recommendation for Phase 3 (GUI)

**Deadline:** Week 3, Day 5 (17:00)

---

## Weeks 4-6: Qt6 GUI Development

### Handoff 4A: Claude → Qwen (UX Mockups)

**Deliverable:** `docs/gui_mockups_and_specs.md`

**Content Requirements:**
- [ ] Wireframes/mockups (ASCII art, Excalidraw PNG, or Figma export)
- [ ] MainWindow layout specification
- [ ] ThemeBrowser component spec (search, grid/list view, preview)
- [ ] PreviewPanel spec (live preview requirements)
- [ ] SettingsDialog spec (toolkit toggles, backup settings)
- [ ] User workflows (discover → preview → apply → verify)
- [ ] Accessibility requirements (keyboard nav, screen reader)

**Format:** Markdown + embedded images (PNG/SVG) in `docs/mockups/`

**Trigger:** Tag `handoff/week4-gui-specs`

**Acknowledgment:** Qwen creates:
- `unified_theming/gui/main_window.py` skeleton
- `docs/gui_implementation_plan.md` with component breakdown

**Deadline:** Week 4, Day 2 (17:00)

---

### Handoff 4B-6B: Qwen → Opencode (GUI Components)

**Interleaved Testing Pattern:**
- Week 4: MainWindow + ThemeBrowser → QTest validation
- Week 5: PreviewPanel + SettingsDialog → Component tests
- Week 6: Backend integration → Workflow tests

**Per-Component Deliverable:**
1. Python implementation (`unified_theming/gui/*.py`)
2. QTest file (`tests/gui/test_*.py`)
3. Coverage report for GUI module

**Validation Criteria:**
- [ ] Component renders without crashes
- [ ] User interactions functional (clicks, keypresses)
- [ ] Backend integration correct (theme data flows to UI)
- [ ] No blocking UI bugs

**Trigger:** Tag pattern `qa/week{4,5,6}-gui-{component}`

**Acknowledgment:** Opencode validates and reports bugs in `docs/gui_qa_week{4,5,6}.md`

**Deadline:** End of each week (Friday 17:00)

---

### Handoff 6C: Qwen + Opencode → Claude (GUI Beta Review)

**Deliverable:**
1. **From Qwen:** Functional GUI (`unified_theming/gui/` complete)
2. **From Opencode:**
   - UX test report (`docs/gui_ux_testing.md`)
   - Performance test results (theme preview latency, memory usage)
   - Accessibility audit results

**Validation Criteria:**
- [ ] All workflows functional (discover, preview, apply, backup, restore)
- [ ] Performance acceptable (preview <500ms, apply <2s)
- [ ] Accessibility: keyboard nav, screen reader compatible
- [ ] No P0/P1 UI bugs

**Trigger:** Tag `milestone/gui-beta`

**Acknowledgment:** Claude conducts UX review and creates:
- `docs/gui_polish_recommendations.md` (UI/UX improvements)
- Draft user documentation (`docs/USER_GUIDE.md`)

**Deadline:** Week 6, Day 5 (17:00)

---

## Weeks 7-9: Packaging & Release

### Handoff 7A: Opencode → Claude (Packaging Complete)

**Deliverable:**
1. Flatpak manifest + .flatpak build
2. AppImage build script + .AppImage binary
3. Installation test results (`docs/install_test_results.md`)

**Validation Criteria:**
- [ ] Flatpak installs and runs on Fedora 40/Ubuntu 24.04
- [ ] AppImage runs on Ubuntu 22.04/24.04
- [ ] Theme application works in packaged version
- [ ] File permissions correct (no root required)

**Trigger:** Tag `milestone/packaging-flatpak-appimage`

**Acknowledgment:** Claude creates:
- `docs/INSTALL.md` (Flatpak + AppImage instructions)
- `README.md` update with installation badges

**Deadline:** Week 7, Day 5 (17:00)

---

### Handoff 8A: Opencode → Claude (PPA/AUR Complete)

**Deliverable:**
1. PPA repository setup (Launchpad)
2. AUR PKGBUILD + published package
3. CI/CD pipeline (GitHub Actions for releases)

**Validation Criteria:**
- [ ] PPA installs via apt on Ubuntu 22.04/24.04
- [ ] AUR package builds via yay/paru on Arch
- [ ] CI runs tests on push and generates release artifacts

**Trigger:** Tag `milestone/packaging-complete`

**Acknowledgment:** Claude updates `docs/INSTALL.md` with PPA/AUR instructions

**Deadline:** Week 8, Day 5 (17:00)

---

### Handoff 9A: Claude → Opencode (Final Documentation)

**Deliverable:**
1. `docs/USER_GUIDE.md` (complete user manual)
2. `docs/RELEASE_NOTES_v1.0.md` (final release notes)
3. `README.md` (polished with screenshots/demo GIF)
4. `docs/DEMO.md` (demo script for social media)

**Trigger:** Tag `docs/v1.0-final`

**Acknowledgment:** Opencode validates documentation and performs final release testing

**Deadline:** Week 9, Day 3 (17:00)

---

### Handoff 9B: Opencode → All (v1.0.0 Release)

**Deliverable:**
1. GitHub release created (tag `v1.0.0`)
2. Release artifacts uploaded (Flatpak, AppImage)
3. Final QA report (`docs/v1.0_release_validation.md`)

**Validation Criteria:**
- [ ] All tests pass (coverage ≥80%)
- [ ] All packages install and run
- [ ] Documentation complete and accurate
- [ ] No P0/P1 bugs open
- [ ] Performance benchmarks met

**Trigger:** Tag `release/v1.0.0`

**Acknowledgment:** Claude announces release, Qwen closes milestone, Opencode monitors for hotfix needs

**Deadline:** Week 9-11 (buffer for final polish)

---

## Code Review Process (Optional Enhancement #1)

### Qwen → Claude Review Workflow

**When:** After each significant implementation (daily or per-component)

**Process:**
1. Qwen creates feature branch (e.g., `test/color-utils`)
2. Qwen commits with descriptive message and pushes
3. Qwen tags commit with `review/{component}` (e.g., `review/color-utils`)
4. Claude reviews code for:
   - Type safety (mypy compliance)
   - Test quality (edge cases, assertions)
   - Code style (Black, isort)
   - Architecture adherence (4-layer separation)
5. Claude comments in `docs/code_review_{component}.md` or inline (if using GitHub)
6. If approved: Claude tags `approved/{component}`
7. If changes needed: Qwen addresses feedback and re-tags

**Benefit:** Catches architectural drift early, ensures type safety

---

## Rollback Protocol

### Failed Handoff Scenarios

**Scenario 1: Coverage Below Threshold**
- Example: Week 1 handoff has `color.py` at 65% (target: 80%)
- **Action:** Opencode creates `docs/coverage_gap_week1.md` with missing test cases
- **Resolution:** Qwen adds tests, re-triggers handoff
- **Timeline Impact:** +1 day (use contingency buffer)

**Scenario 2: Tests Failing**
- Example: Week 2 has 5 failing tests in `test_qt_handler.py`
- **Action:** Opencode reports failures in `docs/test_failures_week2.md`
- **Resolution:** Qwen debugs and fixes, re-runs QA
- **Timeline Impact:** +0.5-1 day

**Scenario 3: Performance Benchmark Missed**
- Example: Theme discovery takes 8s for 100 themes (target: <5s)
- **Action:** Opencode documents in `docs/performance_issues_week3.md`
- **Resolution:** Qwen optimizes (caching, parallelization), re-benchmarks
- **Timeline Impact:** +1-2 days (may require Week 10 buffer)

**Escalation:** If rollback exceeds +2 days, all agents convene to reassess timeline and scope.

---

## Communication Channels

### Git Tags (Primary)
- `handoff/{week}-{component}`: Claude → Qwen
- `qa/{week}-{component}`: Qwen → Opencode
- `approved/{component}`: Claude code review approval
- `milestone/{phase}`: Major checkpoints
- `release/{version}`: Release candidates and finals

### Documentation (Asynchronous)
- All specs/reports in `docs/` directory
- Naming convention: `{type}_{component}_week{N}.md`
- Types: `test_plan`, `qa_report`, `implementation`, `review`, `benchmark`

### Issue Tracker (Bug Reports)
- Opencode creates GitHub issues for bugs found during QA
- Labels: `P0-critical`, `P1-high`, `P2-medium`, `P3-low`, `week-{N}`
- Qwen assigns to self and fixes before next handoff

---

## Success Metrics

### Handoff Quality KPIs
- **On-time handoffs:** ≥90% (≤1 day delay acceptable)
- **Coverage compliance:** 100% (all modules meet targets)
- **Test pass rate:** 100% (no failing tests at handoff)
- **Rework rate:** ≤10% (bugs found in QA requiring code changes)
- **Code review approval:** ≥95% (minimal revisions needed)

### Weekly Tracking
Each Friday, Opencode creates `docs/weekly_status_week{N}.md` with:
- Handoffs completed vs. planned
- Coverage actuals vs. targets
- Bugs opened/closed
- Timeline adherence (on-track / +N days delayed)
- Risks identified

---

## Handoff Checklist Template

```markdown
## Handoff: {From Agent} → {To Agent}

**Week:** {N}
**Component:** {component_name}
**Date:** {YYYY-MM-DD}
**Tag:** {git_tag}

### Deliverables
- [ ] {File 1}
- [ ] {File 2}
- [ ] {Report/Coverage}

### Validation Criteria Met
- [ ] {Criterion 1}
- [ ] {Criterion 2}
- [ ] {Coverage/Tests/Performance}

### Known Issues
- {Issue 1 - P{N}}
- {Issue 2 - P{N}}

### Next Steps for Receiving Agent
1. {Action 1}
2. {Action 2}
3. {Acknowledgment deadline}

### Acknowledgment
- [ ] Received and reviewed by {Receiving Agent}
- [ ] Acknowledgment document created: {filename}
- [ ] Concerns raised: {Yes/No - details below}

---
**Signed:**
{From Agent} - {Timestamp}
{To Agent} - {Timestamp}
```

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-10-21 | Initial protocol | Claude Code |

---

**This protocol is binding for all agents. Adherence ensures project success.** ✅
