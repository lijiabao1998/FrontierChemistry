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

## C4 ✗（先驗設計失誤）＋機制補充分析
凍結比較用 OLS2（全局組成特徵）：scaffold 2.361 vs random 2.49 —— 未劣化（FAIL）。機制：全局組成特徵跨骨架本就泛化。補充分析（非凍結項）：group-aware 基線 random 3.103 vs scaffold-holdout 3.759 = **劣化 +0.656 MAE**——洩漏風險確實存在於依賴骨架同胞資訊的模型。教訓：凍結比較前必須先鎖定 baseline 類別；下一輪執行前重新登記（以 group-aware 為對象）。

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
