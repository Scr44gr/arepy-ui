# Roadmap

This roadmap consolidates the highest-impact improvements discovered during a repository-wide review of arepy-ui.

## North Star

- Keep the published documentation aligned with the public API.
- Reduce per-frame CPU work in layout, text measurement, and input traversal.
- Make performance measurable with repeatable `uv`-based benchmarks.
- Replace silent failure paths with explicit contracts and safe diagnostics.

## Phase 1 — Documentation Alignment

**Goal:** eliminate examples that do not run against the current API.

- Make the published docs consistently show that `load_aui()` returns `ParseResult`.
- Standardize on `handlers=` instead of legacy `context=` examples.
- Standardize all frame loops on `ui_manager.update(dt)`.
- Audit public examples against the current exports from `arepy_ui/__init__.py`.
- Mark non-published legacy doc trees as deprecated or remove them to avoid drift.

**Success criteria**

- No published page contains `context=` examples for `load_aui()`.
- No published page calls `ui_manager.update()` without `dt`.
- The top-level docs match the runtime behavior in `arepy_ui/manager.py` and `arepy_ui/markup/loader.py`.

## Phase 2 — Quick Performance Wins

**Goal:** reduce avoidable CPU work without changing architecture.

- Add a text measurement cache keyed by `(text, font_name, font_size, spacing)` in `arepy_ui/core/fonts.py`.
- Avoid repeated `split("\n")` and repeated per-line measurements in `arepy_ui/components/text.py`.
- Cache viewport size for the active layout pass so `vw` and `vh` do not call runtime repeatedly in `arepy_ui/core/node.py`.
- Move hot-path imports out of frame/update traversal, especially in `arepy_ui/manager.py`.
- Avoid repeated full-tree cursor scans when hover target has not changed.

**Success criteria**

- Fewer runtime calls inside `calculate_layout()`, `render()`, and cursor lookup.
- Stable behavior under existing tests.
- Visible reduction in frame time on large UI trees.

## Phase 3 — Layout Engine Refactor

**Goal:** stop recalculating more of the tree than necessary.

- Introduce subtree-level dirty tracking instead of a single global dirty bit.
- Collapse duplicated work between `calculate_layout()` and `_propagate_position_to_children()`.
- Separate measurement and positioning clearly so auto-sizing does not force redundant recursion.
- Carry frame/layout context through the tree instead of querying runtime from each node.

**Success criteria**

- Changing one branch of the tree does not trigger full recomputation of unrelated branches.
- Layout complexity scales closer to the size of the dirty subtree, not the whole UI.

## Phase 4 — Instrumentation and Benchmarks

**Goal:** make performance regressions easy to detect.

- Add benchmark scenes for `50`, `500`, and `2000` nodes.
- Measure separate timings for layout, input, and render traversal.
- Add a `uv` command or script to run repeatable microbenchmarks locally.
- Store baseline numbers in the repository so regressions are visible in PRs.

**Candidate scenarios**

- Deep nested layout tree
- Large text-heavy screen
- Scroll-heavy inventory screen
- Multiple overlays/select dropdowns
- Video component with controls enabled

## Phase 5 — Reliability Cleanup

**Goal:** reduce hidden failure modes and make the codebase easier to evolve.

- Replace broad `except Exception: pass` blocks with targeted exceptions and actionable logging.
- Remove duplicated font filter application logic between `arepy_ui/config.py` and `arepy_ui/core/fonts.py`.
- Tighten public API docs around what is stable vs. experimental, especially the video component.
- Add doc checks and focused smoke tests to keep examples aligned over time.

## Suggested Execution Order

1. Finish Phase 1 to stop documenting broken usage.
2. Ship Phase 2 quick wins behind existing tests.
3. Add Phase 4 benchmarks before deep refactors.
4. Use benchmark data to drive Phase 3 layout work.
5. Close with Phase 5 hardening and documentation guardrails.

## First PR Batch

If you want the fastest path to visible improvement, start with this batch:

- Text measurement cache
- Viewport-size cache per layout pass
- Remove hot-path imports in manager traversal
- Fix remaining public docs that still show legacy API usage
- Add a small `uv` benchmark entry point