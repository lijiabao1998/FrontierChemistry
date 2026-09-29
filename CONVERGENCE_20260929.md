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

The scientific result JSON and numerical model are unchanged. A subsequent review added an early binary-dependency guard to freesolv_validator.py; incompatible platforms return BLOCKED before import.
Full model rerun and independent chemical validation are NOT_RUN. The legacy runner
also writes a dynamic generated timestamp: frozen artifact identity must not be
misrepresented as a byte-identical new experiment. A future round needs its own
fresh search, preregistered scaffold policy, evaluator and independent verification.

Validation commands and actual results are appended after execution.

Maintenance results: 4 integrity tests PASS; working manifest 7/7 PASS. Before commit, --git-revision HEAD on bdca662 reproduces the original tests_regression.py mismatch (expected exit 1). Pinned governance validates all 10 problem cards. Model and scientific result JSON are unchanged. Post-commit validation follows.

Post-commit 312e963 verified 7/7 Git blobs. Independent review reran four tests, rejected bdca662, verified unchanged model/results, then requested completion/index corrections; these are now incorporated. Scientific acceptance remains unverified.

Automatic review on 312e963 identified the Windows-only binary import crash and incomplete dependency provenance. The repair now blocks incompatible CPython/platform tags before importing bundled code, catches loader failures, and binds all 2019 tracked dependency files plus version metadata. This does not retrofit proof of the historical execution environment. Git verification uses one cat-file batch process.

Dependency repair validation: five integrity/platform tests PASS; all 2027 manifest entries match both working bytes and commit 8929fe5. Source line endings then canonicalized to LF with the manifest regenerated. No numerical model replay performed.


Final runner maintenance scope (fixed before the following edit/tests): propagate
BLOCKED_DEPENDENCY/exit 2 through the legacy regression-runner entrypoint before
any chemical assertions execute, exercise that unsupported-platform path without
writing a scientific result, and correct stale stdlib/naive-key documentation.
Do not rerun or change the numerical model, historical output, split or thresholds.
Regenerate changed source hashes and verify the exact committed snapshot.

Runner follow-up validation: six maintenance tests PASS, including simulated
unsupported-platform entrypoints for both validator and legacy runner; both return
exit 2 without changing the historical result. The runner reports tests_run=0.
Scientific numerical functions and result JSON remain unchanged; no model replay.
The new regression catches the prior runner AssertionError/exit 1. Dependency
coverage remains all 2019 tracked files, with 2027 total manifest entries.
