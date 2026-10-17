# REMEDIATION｜CHEM-004 r1｜Codex review 回應（2026-09-28）

| Finding | 級別 | 修復 | 回歸測試 |
|---|---|---|---|
| scaffold key 漏芳香原子（483/642 塌縮） | P1 | ATOM_TOK 含 bracket+lowercase aromatic；ring 簽名+aromaticity | tests_regression.py T1 |
| unseen scaffold fallback 用「均值之均值」 | P1 | 改為 record-weighted 全域均值；**+0.656 劣化宣稱撤回**（修正後 scaffold_scaffoldmean=2.85=scaffold_global 內部一致；group-aware 劣化實為 +0.523：2.327→2.85） | T2 |
| licenses_checked 提前勾 true | P1 | LICENSE 實檔審查：**CC BY 4.0 International**（附 attribution 合規結論）記入 round.json remediation 與 lit_data/FREESOLV_LICENSE | T3 |
| hashes 與 committed 結果不符 | P2 | 以最終檔案重算，`sha256sum -c` 通過 | T4 |

重跑：C1/C2/C3 維持 PASS（錨點 1.114 不變）；C4/C5 維持 FAIL（凍結門檻不動，修正後分析見上）。
