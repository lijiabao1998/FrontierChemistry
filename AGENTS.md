# FrontierChemistry agent 入口

固定治理： https://github.com/lijiabao1998/FrontierLab-Governance/tree/07d2b13051b83215182e411e1612f92f1912d8fb
先讀其AGENTS、RESEARCH_PROTOCOL、EVIDENCE_POLICY、SAFETY，再讀本庫README、STATUS、VALIDATION與題卡。

所有agent在bootstrap後走 `<agent>/CHEM-xxx-<topic>`，不直接寫main、不自合。owner明確批准後才合併；文件規則不等於伺服器端branch protection。fetch後記base SHA，先查領題／PR／失敗紀錄，一目錄一寫入者。

每輪start → 本輪四路檢索與原文閱讀 → 凍結化學條件／基線／指標／預算 → admit → 重現 → 探索 → 獨立Verifier及Skeptic → 記失敗 → PR。沒有網路／授權／已核實來源則停，不用舊搜尋冒充新輪次。外部同範圍完成立即標COMPLETED_EXTERNAL，未確認聲稱先暫停核實。

明列電子能／自由能差別、units、標準態、原子／電荷／自旋、構象、基組、邊界、方法與資料版本。候選與驗證器不同責任，禁止刪難例、改閾值、把DFT標籤當實驗真值。基線重現与新發現分開。

只做低風險計算研究；不自動啟動高風險化學、濕實驗或付費計算，不提供危險合成操作。研究檔案放problems/<ID>/{experiments,proofs,results}/，輪次runs/<id>/round.json。未跑寫NOT_RUN，負結果不刪。預設30分鐘／0美元／100次；首輪CHEM-004小基線。
