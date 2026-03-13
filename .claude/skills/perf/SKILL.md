---
name: perf
description: Performance profiling, bottleneck identification, optimization, and benchmarking workflow. Measures before/after to validate improvements.
argument-hint: [area to optimize, e.g. "API response time" or "bundle size"]
disable-model-invocation: true
context: fork
---

# Performance Optimization Workflow

Systematic approach to identifying and fixing performance bottlenecks with measurable results.

## Step 1: Understand Target

- Read `PROJECT.md` and `CLAUDE.md` for conventions
- Parse `$ARGUMENTS` to understand what needs optimizing
- Identify the relevant area: API latency, page load, bundle size, memory, CPU, DB queries, etc.

## Step 2: Baseline Measurement

Use the **debugger** agent to profile the target area:
- Record current metrics (latency, throughput, memory, CPU, bundle size -- whichever apply)
- Identify measurement methodology (how to reproduce the measurement)
- Document the baseline numbers

## Step 3: Bottleneck Analysis

Identify performance bottlenecks:
- N+1 database queries
- Unnecessary re-renders
- Blocking I/O on hot paths
- Large bundle sizes or unoptimized imports
- Missing database indexes
- Unoptimized algorithms (O(n^2) where O(n) is possible)
- Memory leaks or excessive allocations
- Missing caching opportunities

Present findings with file:line references and evidence.

## Step 4: Human Review

Present:
- Baseline metrics
- Identified bottlenecks with evidence
- Proposed optimization strategy (ordered by expected impact)
- Risk assessment for each optimization

Wait for approval.

## Step 5: Implement

Create branch: `perf/[description]`

Use the **implementer** agent to apply optimizations.
After each optimization:
- Run validation from `PROJECT.md`
- Commit separately: `perf: [specific optimization]`

## Step 6: Benchmark

Re-run the same measurements from Step 2.

Present a before/after comparison:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| [metric] | [value] | [value] | [% or absolute] |

## Step 7: Validate

Run the full test suite to confirm no regressions.

## Step 8: Review

Use the **code-reviewer** agent to review changes.
Focus: correctness, maintainability, and whether the optimization is worth the complexity.

## Step 9: Summary

Present:
- Before/after metrics table
- Optimizations applied
- Test results
- Review findings
- Ask about PR creation

---

Target: $ARGUMENTS
