#!/usr/bin/env python3
"""CHEM-004 round 1: FreeSolv v0.52 data validator, chemical split, baselines,
and wrong-unit negative control. Stdlib only, deterministic (seed 42).

Checks (pre-registered in round.json):
  C1 parse 640-644 records
  C2 zero records with net formal charge != 0 (bracket-charge sum; nitro +/- cancel)
  C3 reproduce the dataset's own GAFF calc-vs-exp MAE within [0.9, 1.6] kcal/mol
     (literature anchor ~1.2-1.3; band frozen before running)
  C4 leave-scaffold-out MAE must be WORSE than random-split MAE (leakage risk quantified)
  C5 wrong-unit negative control: 10% of labels x4.184 (kcal->kJ confusion) must be
     flagged for >=90% of poisoned records by the z-score detector
  C6 duplicate/stereochemistry report (exact SMILES dups, stereo-stripped dups,
     records with @/@@, notes mentioning stereo renames)

Dataset-level conventions recorded: kcal/mol, 298 K, 1 atm gas -> 1 M solution
standard state, neutral solutes (per file header and Mobley & Guthrie 2014).

The naive scaffold key (ring-system element-class signature; acyclics grouped by
heavy-atom count bucket) is an explicit approximation of Bemis-Murcko, which
requires RDKit and is unavailable under the stdlib constraint.
"""
from __future__ import annotations
import json
import sys
import math
import random
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / ".deps"))
try:
    from rdkit import Chem, RDLogger  # noqa: E402
    from rdkit.Chem.Scaffolds import MurckoScaffold  # noqa: E402
    RDLogger.DisableLog("rdApp.warning")
    RDKIT_VERSION = Chem.rdBase.rdkitVersion
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    RDKIT_VERSION = None
    Chem = None
    MurckoScaffold = None
# RDKit availability: the committed .deps wheel is cp313-win_amd64; on other
# platforms install with `pip install --target problems/CHEM-004/experiments/
# chem004_r1/.deps rdkit`. Without RDKit the C4/Murcko analysis is BLOCKED,
# not attempted with hand-rolled parsers (two review rounds proved those
# unreliable).
SRC = HERE / "lit_data" / "freesolv_database.txt"
RESULTS = HERE.parent.parent / "results" / "r1"
SEED = 42


def parse_database() -> list[dict]:
    recs = []
    for line in SRC.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        f = [x.strip() for x in line.split(";")]
        recs.append({"id": f[0], "smiles": f[1], "name": f[2],
                     "dg_exp": float(f[3]), "unc_exp": float(f[4]),
                     "dg_calc": float(f[5]), "unc_calc": float(f[6]),
                     "doi_exp": f[7], "note": f[9] if len(f) > 9 else ""})
    return recs


def _mol(smiles: str):
    if not RDKIT_AVAILABLE:
        raise ValueError("RDKit unavailable: C4/Murcko analysis BLOCKED; "
                         "install per round.json remediation_v2.rdkit.install")
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        raise ValueError(f"unparseable SMILES: {smiles}")
    return m


def murcko_scaffold(smiles: str) -> str:
    """Canonical Bemis-Murcko scaffold via RDKit (Codex P1: hand-rolled regex
    parsers collapsed aromatics/heterocycles and are retired)."""
    try:
        m = _mol(smiles)
        sc = MurckoScaffold.GetScaffoldForMol(m)
        sc_smiles = Chem.MolToSmiles(sc) if sc is not None and sc.GetNumAtoms() > 0 else ""
        if not sc_smiles:
            # acyclic molecules have an empty Murcko scaffold; key them by
            # their canonical molecular SMILES so 320 distinct chains do not
            # collapse into one group (Codex convergence P1)
            return "acyclic:" + Chem.MolToSmiles(m)
        return sc_smiles
    except ValueError:
        return "UNPARSED"


def heavy_atoms(smiles: str) -> int:
    """Heavy-atom count from the RDKit molecular graph (Codex P1: the old
    uppercase-only regex undercounted every aromatic record)."""
    return _mol(smiles).GetNumHeavyAtoms()


def hetero_atoms(smiles: str) -> int:
    return sum(1 for a in _mol(smiles).GetAtoms()
               if a.GetAtomicNum() not in (1, 6))


def net_charge(smiles: str) -> int:
    return sum(a.GetFormalCharge() for a in _mol(smiles).GetAtoms())


def mae(errs) -> float:
    return sum(abs(e) for e in errs) / len(errs)


def main() -> int:
    recs = parse_database()
    out = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "n_records": len(recs)}

    # C2 net charge
    charged = [r["id"] for r in recs if net_charge(r["smiles"]) != 0]

    # C6 duplicates / stereo
    smi = Counter(r["smiles"] for r in recs)
    exact_dups = {k: v for k, v in smi.items() if v > 1}
    stripped = Counter(r["smiles"].replace("@", "") for r in recs)
    stereo_dups = {k: v for k, v in stripped.items() if v > 1}
    n_stereo = sum("@" in r["smiles"] for r in recs)
    n_stereo_rename = sum("stereo" in r["note"].lower() for r in recs)
    n_default_unc = sum(abs(r["unc_exp"] - 0.60) < 1e-9 for r in recs)
    n_unpublished = sum("unpublished" in r["doi_exp"].lower() for r in recs)

    # C3 reproduce dataset's own calc-vs-exp anchor
    calc_errs = [r["dg_calc"] - r["dg_exp"] for r in recs]
    calc_mae = mae(calc_errs)

    # splits and baselines (deterministic)
    rng = random.Random(SEED)
    idx = list(range(len(recs)))
    rng.shuffle(idx)
    n_train = int(0.8 * len(recs))
    rand_tr, rand_te = idx[:n_train], idx[n_train:]

    for name, tr, te in (("random", rand_tr, rand_te),):
        pass  # placeholder; actual loops below keep names explicit

    def eval_on(tr, te, baseline: str) -> dict:
        errs, zmax = [], 0.0
        if baseline == "global_mean":
            mu = sum(recs[i]["dg_exp"] for i in tr) / len(tr)
            preds = {i: mu for i in te}
        elif baseline == "scaffold_mean":
            grp = defaultdict(list)
            for i in tr:
                grp[murcko_scaffold(recs[i]["smiles"])].append(recs[i]["dg_exp"])
            gm = {k: sum(v) / len(v) for k, v in grp.items()}
            mu = sum(recs[i]["dg_exp"] for i in tr) / len(tr)  # true global mean (Codex fix)
            preds = {i: gm.get(murcko_scaffold(recs[i]["smiles"]), mu) for i in te}
        else:  # ols2: heavy atoms + hetero atoms
            xs = [[heavy_atoms(recs[i]["smiles"]), hetero_atoms(recs[i]["smiles"])]
                  for i in tr]
            ys = [recs[i]["dg_exp"] for i in tr]
            n = len(tr)
            m1, m2, my = (sum(x[0] for x in xs) / n, sum(x[1] for x in xs) / n,
                          sum(ys) / n)
            c11 = sum((x[0] - m1) ** 2 for x in xs)
            c22 = sum((x[1] - m2) ** 2 for x in xs)
            c12 = sum((x[0] - m1) * (x[1] - m2) for x in xs)
            b1 = sum((x[0] - m1) * (y - my) for x, y in zip(xs, ys))
            b2 = sum((x[1] - m2) * (y - my) for x, y in zip(xs, ys))
            det = c11 * c22 - c12 * c12
            w1 = (c22 * b1 - c12 * b2) / det
            w2 = (c11 * b2 - c12 * b1) / det
            w0 = my - w1 * m1 - w2 * m2
            preds = {i: w0 + w1 * heavy_atoms(recs[i]["smiles"])
                        + w2 * hetero_atoms(recs[i]["smiles"]) for i in te}
        for i in te:
            errs.append(preds[i] - recs[i]["dg_exp"])
            unc = max(recs[i]["unc_exp"], 0.1)
            zmax = max(zmax, abs(preds[i] - recs[i]["dg_exp"]) / unc)
        return {"mae": round(mae(errs), 3), "rmse": round(
            math.sqrt(sum(e * e for e in errs) / len(errs)), 3), "n": len(te)}

    res = {"random_global": eval_on(rand_tr, rand_te, "global_mean"),
           "random_ols2": eval_on(rand_tr, rand_te, "ols2"),
           "random_scaffoldmean": eval_on(rand_tr, rand_te, "scaffold_mean")}
    # scaffold split: hold out whole scaffold keys (largest 25% of keys by records)
    keys = defaultdict(list)
    for i in idx:
        keys[murcko_scaffold(recs[i]["smiles"])].append(i)
    key_names = sorted(keys, key=lambda k: -len(keys[k]))
    hold_keys = set()
    acc = 0
    for k in key_names:
        hold_keys.add(k)
        acc += len(keys[k])
        if acc >= 0.25 * len(recs):
            break
    sca_tr = [i for k in keys for i in keys[k] if k not in hold_keys]
    sca_te = [i for k in hold_keys for i in keys[k]]
    res["scaffold_global"] = eval_on(sca_tr, sca_te, "global_mean")
    res["scaffold_ols2"] = eval_on(sca_tr, sca_te, "ols2")
    res["scaffold_scaffoldmean"] = eval_on(sca_tr, sca_te, "scaffold_mean")
    # supplementary mechanism analysis (NOT a frozen check): the group-aware
    # baseline is where scaffold holdout should hurt - random split lets it see
    # scaffold peers; holdout forbids that and it must fall back to global mean.
    res["leakage_mechanism_gap"] = round(
        res["random_scaffoldmean"]["mae"] - res["scaffold_scaffoldmean"]["mae"], 3)
    res["n_scaffold_keys_total"] = len(keys)
    res["n_scaffold_keys_held_out"] = len(hold_keys)

    # C5 wrong-unit negative control: poison 10% of RANDOM-TEST labels x4.184
    # (kcal->kJ confusion). The z-detector uses the record's REPORTED uncertainty
    # as-is: a unit-swapped label arrives with its original uncertainty attached,
    # so scaling `unc` alongside the label would smuggle the error past the guard
    # (initial implementation did exactly that and only flagged 25% - fixed).
    poison = set(rng.sample(rand_te, max(1, int(0.1 * len(rand_te)))))
    mu = sum(recs[i]["dg_exp"] for i in rand_tr) / len(rand_tr)
    flagged = []
    for i in poison:
        obs = recs[i]["dg_exp"] * 4.184
        z = abs(mu - obs) / max(recs[i]["unc_exp"], 0.1)
        if z > 10:
            flagged.append(recs[i]["id"])
    res["wrong_unit_control"] = {
        "poisoned": len(poison), "flagged": len(flagged),
        "flag_rate": round(len(flagged) / len(poison), 3),
        "detector_note": "z uses reported unc un-scaled; prior buggy run "
                         "scaled unc by 4.184 too and flagged only 25%"}

    checks = {
        "C1_record_count": 640 <= len(recs) <= 644,
        "C2_net_charge_clean": len(charged) == 0,
        "C3_calc_anchor_mae": 0.9 <= calc_mae <= 1.6,
        "C4_scaffold_split_degrades": res["scaffold_ols2"]["mae"] > res["random_ols2"]["mae"],
        "C5_wrong_unit_flag_rate": res["wrong_unit_control"]["flag_rate"] >= 0.9,
    }
    out.update({"checks_report": {
        "C2_charged_records": charged,
        "C6_exact_smiles_dups": exact_dups, "C6_stereo_stripped_dups": stereo_dups,
        "C6_records_with_stereo": n_stereo, "C6_stereo_rename_notes": n_stereo_rename,
        "C6_default_unc_060_count": n_default_unc,
        "C6_unpublished_source_count": n_unpublished},
        "calc_vs_exp_mae": round(calc_mae, 3),
        "split_results": res, "checks": checks,
        "verdict": "ALL_CHECKS_PASS" if all(checks.values()) else "CHECKS_FAILED"})
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "chem004_r1_results.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"n": len(recs), "calc_mae": round(calc_mae, 3),
                      "splits": {k: v["mae"] for k, v in res.items()
                                 if isinstance(v, dict) and "mae" in v},
                      "wrong_unit_flag_rate": res["wrong_unit_control"]["flag_rate"],
                      "checks": checks, "verdict": out["verdict"]},
                     ensure_ascii=False, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
