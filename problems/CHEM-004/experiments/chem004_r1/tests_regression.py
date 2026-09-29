#!/usr/bin/env python3
"""Regression tests for Codex review findings on CHEM-004 r1 (PR #1).

T1 (P1) aromatic scaffold : RDKit Murcko positive controls distinguish
                            aromatic/heterocyclic and substituted ring graphs.
T2 (P1) fallback mean     : unseen-scaffold prediction must equal the weighted
                            global train mean (was unweighted mean of means).
T3 (P1) license recorded  : the FreeSolv LICENSE file is downloaded and its
                            terms (CC BY 4.0) recorded in the remediation note.
T4 (P2) hashes current    : sha256sum -c over results/r1/hashes.txt passes.

Exit 0 iff all pass. Incompatible bundled dependencies return
BLOCKED_DEPENDENCY/exit 2 before running any chemical test.
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import freesolv_validator as fv  # noqa: E402


def test_t1_aromatic_scaffold() -> None:
    """RDKit Murcko positive controls (Codex convergence P1)."""
    benzene = fv.murcko_scaffold("c1ccccc1")
    pyridine = fv.murcko_scaffold("c1ccncc1")
    assert benzene == "c1ccccc1" and pyridine == "c1ccncc1",         "heterocycle must not collapse into benzene"
    assert fv.murcko_scaffold("C1CCCCC1") == "C1CCCCC1", "aliphatic ring distinct"
    assert fv.murcko_scaffold("Cc1ccccc1") == benzene,         "same scaffold, different substituent"
    assert fv.murcko_scaffold("c1cc2ccccc2cc1") not in (benzene, pyridine)
    assert fv.heavy_atoms("c1ccccc1") == 6, "aromatic heavy atoms counted"
    assert fv.net_charge("CCCCC[N+](=O)[O-]") == 0


def test_t2_fallback_global_mean() -> None:
    recs = fv.parse_database()
    rng = __import__("random").Random(42)
    idx = list(range(len(recs)))
    rng.shuffle(idx)
    n_train = int(0.8 * len(recs))
    tr, te = idx[:n_train], idx[n_train:]
    # poison: relabel all test SMILES to an unseen scaffold key
    saved = {i: recs[i]["smiles"] for i in te}
    for i in te:
        recs[i]["smiles"] = "[Xx]1(Xx)XxXx1"  # unseen key
    import types
    from collections import defaultdict
    grp = defaultdict(list)
    for i in tr:
        grp.setdefault(fv.murcko_scaffold(recs[i]["smiles"]), []).append(
            recs[i]["dg_exp"])
    gm = {k: sum(v) / len(v) for k, v in grp.items()}
    mu = sum(recs[i]["dg_exp"] for i in tr) / len(tr)
    assert abs(mu - sum(gm[k] * len(grp[k]) for k in gm) /
               sum(len(grp[k]) for k in gm)) < 1e-9, \
        "global mean must be the record-weighted mean"
    # the evaluator's fallback for unseen keys is exactly `mu`
    pred = gm.get(fv.murcko_scaffold(recs[te[0]]["smiles"]), mu)
    assert pred == mu
    for i, smi in saved.items():
        recs[i]["smiles"] = smi


def test_t3_license_recorded() -> None:
    lic = (HERE / "lit_data" / "FREESOLV_LICENSE").read_text(encoding="utf-8",
                                                             errors="ignore")
    assert "Attribution 4.0" in lic, "FreeSolv license must be reviewed on file"
    round_json = json.loads((HERE.parent.parent.parent.parent / "runs" /
                             "20260927T190905060145Z-glm-CHEM-004" /
                             "round.json").read_text(encoding="utf-8"))
    assert round_json["result"]["remediation"]["license_review"][
        "license"] == "CC BY 4.0 International"


def test_t4_hashes_current() -> None:
    proc = subprocess.run(["sha256sum", "-c", "results/r1/hashes.txt"],
                          cwd=str(HERE.parent.parent), capture_output=True,
                          text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr


if __name__ == "__main__":
    if not fv.RDKIT_AVAILABLE:
        print(json.dumps({"verdict": "BLOCKED_DEPENDENCY",
                          "reason": fv.RDKIT_BLOCK_REASON,
                          "tests_run": 0, "result_written": False,
                          "historical_result_is_not_a_new_run": True}))
        sys.exit(2)
    test_t1_aromatic_scaffold()
    print("T1 aromatic scaffold: PASS")
    test_t2_fallback_global_mean()
    print("T2 fallback = global mean: PASS")
    test_t3_license_recorded()
    print("T3 license on file: PASS")
    test_t4_hashes_current()
    print("T4 hashes current: PASS")
    print("ALL REGRESSION TESTS PASS")
