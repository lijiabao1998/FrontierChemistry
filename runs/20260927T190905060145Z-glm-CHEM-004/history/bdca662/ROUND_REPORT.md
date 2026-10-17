# ROUND REPORT｜CHEM-004｜20260927T190905060145Z-glm-CHEM-004

- branch：`glm/CHEM-004-baseline-r1`（base `6edd379003c880e5c3e5b1ade556dff21e9a7591`）；pin `07d2b130`
- verdict：**NO_RESOLUTION_FOUND**（Moore 2026 中性分子進展 ≠ 離子/多溶劑可遷移性已解；題卡 known_result 準確）
- 本輪判定：**CHECKS_FAILED（3/5 凍結 checks 通過；2 個 FAIL 如實記錄＋分析）**

## 核對結果（單位/溫度/標準態/電荷/身份/重複/立體/參照不確定度）
- 資料集層級聲明（檔頭第一手）：kcal/mol、水合、298K、1atm 氣相→1M 溶液、中性分子；v0.52（2017-06-11）。
- C1 ✓ 642 筆；C2 ✓ 0 筆淨電荷≠0（nitro +/− 抵消由括號電荷求和驗證）。
- C6 報告：exact SMILES dups／去立體 dups／含 @/@@ 記錄數／stereo rename notes／預設不確定度 0.60 之筆數／unpublished 來源筆數——全在 results JSON。

## C3：基線重現錨點 ✓
**資料集內建 GAFF calc-vs-exp MAE = 1.114 kcal/mol**（文獻 ~1.2-1.3；凍結帶 [0.9,1.6] 內）。此即「重現基線表」之錨。

## C4（Convergence Wave 改判：真 Murcko 分割下合法 PASS）
初版自製 regex scaffold 經兩次 Codex 審查證明不可靠（aromatic 塌縮→digit-adjacent 仍塌縮），已廢除。改用 RDKit MurckoScaffold（in-repo .deps）＋RDKit graph heavy-atom 計數：scaffold_ols2 **3.518** vs random_ols2 **2.883**（劣化 **+0.635 MAE**）——原凍結 C4 檢查以正確實作合法通過。group-aware 基線 2.871→3.545。舊值 2.361/3.103/3.759/+0.656 僅存 remediation 歷史。

## C5 ✗（偵測器 bug 修正後仍達不到凍結門檻）
初版偵測器把不確定度也 ×4.184（放水），flag 率僅 25%——修正為用記錄原始 unc 後 **66.7%**。物理天花板：真值 dg_exp ≈ −0.6 kcal/mol 附近之記錄，其 kJ 混淆值（≈ −2.5）落在全域均值附近，全域均值偵測器本質上抓不到。90% 門檻先驗校準失誤——記 FAIL；下一輪預登記特徵化偵測器（per-molecule 預測後 z-score）。

## 交付
`freesolv_validator.py`（stdlib、seed 42）、`results/r1/chem004_r1_results.json`（全部分裂 MAE/RMSE、wrong-unit 明細、C6 報告）、hashes、environment、dataset 檔（lit_data/freesolv_database.txt）。

## 沒做成／限制
JACS primary 僅摘要層級（付費牆）；FreeSolv LICENSE 檔未逐字審（下輪）；naive scaffold 非 Bemis-Murcko（RDKit 不可用之明示近似）；未做多溶劑/離子（本輪 scope 外）。

## 下一輪最小下一步
1. 執行前重新登記 C4（以 group-aware baseline 為對象）與 C5（特徵化偵測器、標定其可達 flag 率）。
2. 讀 JACS 全文＋blog caveats，列其測試集與 FreeSolv 重疊度。
3. 引入 RDKit（in-repo）後以真 Murcko scaffold 重跑 split 對照。

## Remediation v2（Convergence Wave，Codex 二審回應）
- P1 scaffold：RDKit MurckoScaffold（in-repo .deps；安裝：`pip install --target problems/CHEM-004/experiments/chem004_r1/.deps rdkit`）；hand-rolled parser 廢除。正控：benzene/pyridine/cyclohexane/fused ring/同骨架異取代基全過。
- P1 heavy_atoms：RDKit graph 計數，aromatic 267 筆不再低估。
- P2 tests_regression：T2 crash 修復；T1–T4 全部實際執行，runner exit code 為準。
- P2 hashes：verify_manifest.py 全綠（最後生成）。
- P1 報告：主結論統一修正後數字，舊值僅存 history。
- License：CC BY 4.0 International——URL github.com/MobleyLab/FreeSolv/blob/master/LICENSE、text version Attribution 4.0 International、attribution Mobley & Guthrie 2014 + per-record DOIs。

## Remediation v3（Convergence Wave 三審）
- C4 **撤回**：真 Murcko（acyclic 以 canonical SMILES 各自成 key）下 scaffold_ols2 2.647 < random_ols2 2.883——無劣化。+0.635 亦是 320-acyclic 塌縮之產物。誠實結論：**本資料集上 scaffold-holdout 劣化未被證示**；C4 凍結檢查 FAIL。T1-T4 exit 0。
