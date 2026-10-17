# SCAFFOLD PREREGISTRATION AUDIT｜CHEM-004 r1｜2026-09-28

誠實記錄（Codex 多輪審查 + owner 指示彙整）：

1. **凍結時的 key**：自製 naive regex（`ring:<digit-adjacent atoms>` / `acyclic:<bucket>`）——未凍結 RDKit 語意。
2. **事後變更史**：v1 naive（aromatic 漏 → 483/642 塌縮）→ v2 digit-adjacent+aromatic（仍 174 aromatics 塌縮）→ v3 RDKit Murcko（acyclic 全塌成 EMPTY_SCAFFOLD 單一 key，320 筆）→ v4 RDKit + per-molecule acyclic canonical SMILES。
3. **現況結論**：v4 下 C4 凍結檢查 **FAIL**（scaffold_ols2 2.647 < random_ols2 2.883——無劣化）。+0.635/+0.656 兩次「劣化」宣稱皆為塌縮產物，已全部撤回。
4. **preregistration 狀態**：現行 v4 key 相對原凍結而言是 post-hoc 修改；因此 **C4 的任何 PASS/FAIL 都不能宣稱為 preregistered 結果**。若 owner 要正式的 C4 結論：需新開 admitted round、事前凍結 RDKit Murcko key 與 split 規則後再執行。
5. **可移植性**：RDKit wheel 為 cp313-win_amd64；其他平台 `pip install --target problems/CHEM-004/experiments/chem004_r1/.deps rdkit`。無 RDKit 時 C4 分析標 BLOCKED（validator 已優雅降級，不再回退手刻 parser）。
