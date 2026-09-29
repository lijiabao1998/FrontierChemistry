# CHEM-004 evidence maintenance — 2026-09-29

Base: `bdca66228bc05ac51a20404d3028c4cc05aa2079` (PR #1).
Owner delegated convergence and merge decisions to GPT; integration still requires
independent review of this repair and its committed bytes.

Scope frozen before validation: correct artifact identity and active summaries;
preserve scientific data, historical failures, frozen acceptance and source records.
No new chemistry experiment, threshold, split, literature search or admission.

The old manifest described CRLF working bytes for tests_regression.py although its
Git blob used LF. A fresh isolated checkout exposed the mismatch. The updated hash
gate has --git-revision to read BOTH the manifest and its artifacts from a resolved
immutable commit. It also rejects empty/malformed/duplicate/escaping records.

C1-C3 and the recorded GAFF MAE 1.114 remain historical results, not a new independent
replication. C4's v4 scaffold key was post-hoc: its 2.647 vs 2.883 comparison does not
establish degradation and is not confirmatory. C5 remains 8/12 (66.7%), below 90%.
Prior +0.635/+0.656 claims are withdrawn; copies of the original round/report/manifest
are kept in the round's history/bdca662 directory.

The scientific result JSON and freesolv_validator.py are unchanged in this repair.
Full model rerun and independent chemical validation are NOT_RUN. The legacy runner
also writes a dynamic generated timestamp: frozen artifact identity must not be
misrepresented as a byte-identical new experiment. A future round needs its own
fresh search, preregistered scaffold policy, evaluator and independent verification.

Validation commands and actual results are appended after execution.

Maintenance results: 4 integrity tests PASS; working manifest 7/7 PASS. Before commit, --git-revision HEAD on bdca662 reproduces the original tests_regression.py mismatch (expected exit 1). Pinned governance validates all 10 problem cards. Model and scientific result JSON are unchanged. Post-commit validation follows.
