# CHEM-004 independent bounded audit

Protocol commit: `62d890b9e4917b1373896605324045e314dfe44c`. Execution: `BOUNDED_REPLICATION_COMPLETE_FROZEN_C5_FAIL`, exit1; one attempt, single CPU mask1, USD0, no timeout. Started 2026-10-11T19:13:35.386781+00:00, completed 2026-10-11T19:13:35.675071+00:00; child wall 0.131368s. Whole preparation began18:47:09UTC; scientific execution ended before19:17:09UTC.

Independent Decimal replay of642 pinned rows reproduced GAFF MAE1.114kcal/mol, seed42 train513/test129 mean-predictor MAE3.120/RMSE4.382. Labels-only x4.184 poison12, hits8, misses4; C5=8/12<.90 FAIL and whole scientific FAIL retained. All9 fixed integrity mutations rejected. Original C2_net_charge_clean and C4_scaffold_split_degrades NOT_RUN; inherited C4 posthoc FAIL retained. No RDKit import, molecular simulation, reference repair or universal/ionic result. Full ordered IDs, exact flag comparisons, metrics and mutants are in attempt-1/result.json.

Reproduction uses a fresh isolated clone/round on the same pinned source, fresh four-route search and public scope/budget registration, the same frozen PROTOCOL/source/code bytes, official pinned-governance admit, and a prelaunch Git blob audit. Never restart attempt-1 or edit a FINISHED round. After the fresh round is ADMITTED:

```powershell
python problems/CHEM-004/experiments/independent_20261011/run_bounded.py --repo . --round <NEW_ADMITTED_ROUND_ID>
```

The actual absolute command, Python3.13.5 environment, affinity, deadline, output paths and exact exit status are in attempt-1/launch.json and execution.json. Stderr preserves the nonfatal Python installation-location warning. The Git long-path preflight failure and review-driven bounded-launcher correction are preserved; neither triggered a scientific rerun. Direct NBER web Internal Error is preserved in WEB_TRACE and was not turned into a missing-paper claim. New findings concern only evaluator behavior; inherited repairs and broad problem states remain separate. No merge/deploy or original artifact edits.
