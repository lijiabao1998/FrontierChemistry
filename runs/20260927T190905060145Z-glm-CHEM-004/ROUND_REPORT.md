# CHEM-004 r1 — corrected evidence summary (2026-09-29)

The original report is preserved in `history/bdca662/ROUND_REPORT.md`.
The frozen acceptance and original search records remain in round.json; this
maintenance is not a new scientific round or a fresh literature search.

- Historical snapshot: 642 FreeSolv records, recorded GAFF calc-vs-exp MAE
  **1.114 kcal/mol**. This maintenance did not independently rerun chemistry.
- **C4 is post-hoc and not confirmatory.** v4 uses RDKit Murcko keys and
  per-molecule canonical keys for acyclic molecules, unlike the frozen naive key.
  Recorded scaffold OLS2 MAE **2.647** is below random **2.883**; no degradation
  is demonstrated. Both +0.635 and +0.656 claims are withdrawn. Only two of
  382 keys were held out (174 records), so acyclic generalisation is untested.
- **C5 remains FAIL:** 8/12 corrupted labels detected (66.7%), below 90%.
- FreeSolv license was later reviewed as CC BY 4.0 International; the license
  and attribution are committed. The original preflight limitation is historical.
- RDKit is required by the current model code; the original stdlib-only/naive-key
  description is obsolete. This repair does not change the model implementation.
- New experiment, independent chemical replication, external completion and
  general scaffold/solvent/charge transferability: **NOT_ESTABLISHED**.

Artifact integrity is checked with:

```
python problems/CHEM-004/experiments/chem004_r1/verify_manifest.py --git-revision HEAD
python -m unittest discover -s problems/CHEM-004/experiments/chem004_r1 -p test_manifest_integrity.py -v
```

A future confirmatory round must freeze its scaffold/split and detector policy
before execution, perform fresh source checks and obtain independent verification.
The original admitted_at/checked_at chronology is not certified by this repair.
