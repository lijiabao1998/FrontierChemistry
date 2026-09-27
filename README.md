# FrontierChemistry
前沿化學

## 主線：計算／實驗參照分清 → 基線重現 → 誤差與外推 → 候選假說
先啟動 **CHEM-004：溶劑化自由能的資料、標準態與基線核對**，不直接跑昂貴量子計算或大模型訓練。第一輪先拿一個合法公開、良性的小資料子集，確認單位、條件及驗證方式，再展開新方法。

這10題是依原始文獻整理的研究缺口，題卡明列本庫自己的 scope，不冒稱來源已將相同廣泛問題完全形式化。`OPEN` 只代表初始有界篩查未確認同範圍完成；每輪重新檢索。

| ID | 問題 | 優先級 | 第一個任務 |
|---|---|---|---|
| [CHEM-001](problems/CHEM-001/problem.json) | 強關聯電子下可遷移的交換關聯近似 | B | 小分子解離曲線與參照誤差 |
| [CHEM-002](problems/CHEM-002/problem.json) | 過渡金屬自旋態能差 | B | 固定幾何／自旋／環境的基準 |
| [CHEM-003](problems/CHEM-003/problem.json) | 液相反應自由能障壁的条件外推 | A | 反應族／溶劑留出與誤差核對 |
| [CHEM-004](problems/CHEM-004/problem.json) | 溶劑化自由能的可遷移性 | A | 標準態、電荷與公開參照一致性 |
| [CHEM-005](problems/CHEM-005/problem.json) | 晶體多形體有限溫自由能排序 | B | 盲測結構、溫度與排序基線 |
| [CHEM-006](problems/CHEM-006/problem.json) | 固態電解質的化學—力學失效機制 | C | 公開資料下的耦合模型對照 |
| [CHEM-007](problems/CHEM-007/problem.json) | 催化活性位點的operando重構 | C | 結構／訊號／活性映射的可識別性 |
| [CHEM-008](problems/CHEM-008/problem.json) | CO2電還原選擇性的跨條件預測 | C | 微觀動力學與傳質／環境對照 |
| [CHEM-009](problems/CHEM-009/problem.json) | 圓錐交叉附近的非絕熱動力學 | B | 兩態toy model與相位／收斂檢查 |
| [CHEM-010](problems/CHEM-010/problem.json) | 晶體穩定性預測到前瞻發現 | A | 固定資料切分、hull參照及假陽性 |

A/B/C只表示起步資源與順序。每題都有精確研究描述、已知結果、剩餘缺口、最小任務、evaluator、限制、完成條件與原始來源。

## 每輪開始
讀 AGENTS、STATUS、VALIDATION 和固定治理pin，fetch後在獨立agent分支工作。

```bash
# 旁邊的治理repo checkout GOVERNANCE.lock.json指定commit
python3 ../FrontierLab-Governance/tools/frontier.py validate .
python3 ../FrontierLab-Governance/tools/frontier.py start . CHEM-004 --agent gpt
# 真正完成本輪 general / discipline / solution / criticism 搜尋與原文閱讀
python3 ../FrontierLab-Governance/tools/frontier.py admit . runs/<round-id>/round.json
```

確認外部同範圍解答：立即標 `COMPLETED_EXTERNAL`、附作者和核查、停止重做。新的計算近似或單一材料實驗若只涵蓋子範圍，更新部分成果，不把廣泛問題標完成。

## 化學特別界線
電子能、焓、自由能、反應速率不是同一量；溫度、壓力、標準態、電荷、自旋、構象、基組、溶劑與模型版本都要記。計算label不是實驗truth，simulation不是實際合成。新候選是否可合成、安全、穩定需要相應證據。

本庫預設低風險公開計算／資料研究；不自動執行濕實驗，不設計毒劑、爆炸物、武器或危險操作流程。任何實驗、付費算力、受限資料均另需授權與合資格審查。

## 本次狀態
題卡、流程與紀錄CI已建立；原創研究輪次0，各題evaluator尚未實作，無新合成或新材料實驗宣稱。尚未安裝量子化學套件、配置GPU或研究API金鑰。CI只驗紀錄，實際結果以Actions為準。
