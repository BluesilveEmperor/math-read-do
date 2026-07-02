---
name: math-paper-reproduction
description: >-
  鏁板鏂囩尞瀹為獙澶嶇幇鏍囧噯鍖栧伐浣滄祦 / Standardized Math Paper Reproduction Pipeline
  8闃舵鍏ㄩ摼璺細瀹夸富妫€娴?鈫?鐗堟湰绠＄悊 鈫?MinerU PDF瑙ｆ瀽(鍚叕寮?琛ㄦ牸/鍥捐〃) 鈫?  涓夋柟瑙嗚瀹￠槄(鐮旂┒鐢熸繁搴︾悊瑙?瀵煎笀鍙鐜版€ц瘎浼?瀹＄浜烘壒鍒ゅ鏌? 鈫?  鐜閲嶅缓 鈫?鍩虹嚎楠岃瘉 鈫?澧為噺瀹炵幇 鈫?缁熻楠岃瘉(浜旀€佸垽鍐?95%CI) 鈫?鍙岃鎶ュ憡 鈫?鍒跺搧鎵撳寘銆?  鏀寔鏁板€艰绠?绗﹀彿浠ｆ暟/AI4Math/缁熻/浼樺寲/缁忔祹瀛︺€傛瘡浠芥姤鍛婂繀椤讳腑鑻卞弻璇€?  Triggers: 澶嶇幇, reproduction, 瀹為獙澶嶇幇, reproduce paper, 澶嶇幇璁烘枃, 閲嶇幇瀹為獙,
  reproduce experiment, 澶嶇幇鎶ュ憡, reproduction report, PDF瑙ｆ瀽, paper parsing, 瀹為獙閲嶇幇,
  閲嶇幇璁烘枃, 璁烘枃閲嶇幇, 鏁板€煎鐜? 璁烘枃澶嶇幇, paper reproduction, experiment reproduction,
  reproduce results, reproduce figures, 閲嶇幇缁撴灉, 閲嶇幇鍥捐〃, 澶嶇幇缁撴灉, 澶嶇幇鍥捐〃,
  reproducibility check, 鍙鐜版€ц瘎浼? 澶嶇幇楠岃瘉
compatibility:
  - python3 (mineru-open-sdk >= 0.2.5, openai)
  - 閰嶇疆鏂囦欢: ~/.mineru/config.yaml (MinerU token)
  - 鐜鍙橀噺: LLM_API_KEY, LLM_API_BASE, LLM_MODEL
---

# Mathematical Literature Experiment Reproduction Standardized Workflow
# 鏁板鏂囩尞瀹為獙澶嶇幇鏍囧噯鍖栨祦绋?
## 鏍稿績鍘熷垯 / Core Principles

1. **鍙岃杈撳嚭**: 鎵€鏈夋姤鍛婂繀椤绘湁涓嫳鍙岀増鏈?(`.md` + `.zh.md`)
2. **澧為噺楠岃瘉**: 姣忔坊鍔犱竴涓ā鍧楀嵆楠岃瘉涓€娆?3. **鍙璁?*: 姣忔浜х敓缁撴瀯鍖栦骇鐗╋紝婧簮閾惧畬鏁?4. **浜烘満鍗忓悓**: 椋庨櫓鍒嗙骇瀹℃壒
5. **閿佸畾鍗冲绾?*: 鐗堟湰/鐜/渚濊禆姣忔閿佸畾锛屼笉淇′换闅愬紡缁ф壙

## 鍙嶄緥涓庨粦鍚嶅崟 / Anti-Patterns & Blacklist

| # | 鍙嶆ā寮?| 鍚庢灉 | 姝ｇ‘鍋氭硶 |
|---|--------|------|---------|
| 1 | MinerU token 鏈厤缃氨鎵ц Phase 1.1 | 鑴氭湰鎶?401 | 鍏堟鏌?`~/.mineru/config.yaml`锛屾湭閰嶇疆鍒欏紩瀵肩敤鎴疯幏鍙?|
| 2 | Windows 涓婄洿璺?Linux 璺緞鑴氭湰 | 鎹㈣绗?璺緞鍒嗛殧绗︿笉鍏煎 | 浣跨敤 WSL2 鎴?Windows 鍘熺敓鑴氭湰 |
| 3 | 鍏堣鍖呭啀瑁呰瑷€杩愯鏃?| Conda/pip SAT 姝婚攣 | 涓ユ牸 杩愯鏃垛啋鐗堟湰绠＄悊鍣ㄢ啋閿佸畾鈫掑寘鐨勯『搴?|
| 4 | 鍙窇涓€涓瀛愬氨涓嬪垽鍐?| 闈炵‘瀹氭€ц蹇界暐 | 鑷冲皯 N=5 绉嶅瓙, 95% CI 缁熻鍒ゅ喅 |
| 5 | 鍙敓鎴愯嫳鏂囨姤鍛?| 涓枃鐢ㄦ埛鏃犳硶闃呰 | 姣忎唤鎶ュ憡鍚屾椂鐢熸垚 `.md` 鍜?`.zh.md` |
| 6 | 璺宠繃涓夋柟瀹￠槄鐩存帴杩?Phase 2 | 璁烘枃鐞嗚В涓嶅厖鍒?| 蹇呴』璺戝畬 Phase 1.4, 鑾峰緱 reproducibility_assessment.json |
| 7 | 瀵煎嚭鍥捐〃鏃朵笉瀵煎嚭鐢熸垚浠ｇ爜 | 鍥捐〃鏃犳硶鐙珛澶嶇幇 | 姣忓紶鍥鹃檮甯?`results/figures/code/plot_*.py` |
| 8 | 璺宠繃鍙鎬ч鍒ょ洿鎺ュ缓鐜 | 閬囧埌绉佹湁鏁版嵁/纭欢鏃跺ぇ閲忔氮璐?| Phase 0 鍏堝揩閫熷彲琛屾€ф爣璁?|
| 9 | 鍩虹嚎澶辫触鏃朵笉璁板綍鍋忕 | 涓㈠け璇婃柇淇℃伅 | 鍩虹嚎澶辫触蹇呴』鍐?`analysis/gray_areas.md` |
| 10 | conda + pip 涓€娆℃€ф贩鍚堝畨瑁?| SAT 姹傝В鍣ㄦ閿?| 涓ユ牸 conda鈫抪ip 椤哄簭锛屽崟姝ラ獙璇?|
| 11 | 鍗曠偣鍧囧€兼瘮杈冨拷鐣ユ柟宸?| CI 寰堝鏃跺垽鍐宠櫄鍋囩Н鏋?| 鐢?95% CI 鍖洪棿楠岃瘉, 鎶ュ憡 x虅 卤 CI |
| 12 | 鑷姩缈昏瘧涓嶆牎瀵逛笓涓氭湳璇?| 鏈娣锋穯 (identification鈮犺瘑鍒? | 鏈鍏堝湪 glossary.md 瀵归綈, 缈昏瘧鍚庝汉宸ユ牎瀵?|
| 13 | 澧為噺瀹炵幇鏃朵笉鏍囨敞璁烘枃鍑哄 | 浠ｇ爜婧簮鏂 | 姣忎釜鍑芥暟 docstring 鍐?`Ref: Section X.Y, Eq.(Z)` |

## 闃舵閫熸煡 / Phase Quick-Ref

| Stage | What | Key Artifact | 馃敶 CHECKPOINT |
|-------|------|-------------|---------------|
| 0 | 瀹夸富妫€娴嬧啋鐜鏋勫缓鈫扜PU閰嶇疆 | `infra_manifest.json` | G0: 鍩虹璁炬柦灏辩华 |
| 0.5 | 鐗堟湰妫€娴嬧啋瀹夎鈫掗攣瀹氣啋楠岃瘉 | `version_spec.json` | G1: 鐗堟湰涓€鑷?|
| 1 | PDF瑙ｆ瀽鈫掔粨鏋勫寲鎻愬彇鈫掗鍩熷垎绫烩啋涓夋柟瀹￠槄 | `reproducibility_assessment.json` | G01: 鍙鐜版€ч棬绂?|
| 2 | 渚濊禆鎵弿鈫掔幆澧冩瀯寤衡啋纭畾鎬ч厤缃啋楠岃瘉 | `conda-lock.yml` | G3: 鐜灏辩华 |
| 3 | 瀹樻柟浠ｇ爜杩愯鈫掓寚鏍囧榻愨啋澶辫触璇婃柇鈫掗攣瀹?| `baseline_metrics.json` | G4: 鍩虹嚎寤虹珛 |
| 4 | 妯″潡鎷嗚В鈫掑閲忓疄鐜扳啋浠ｇ爜绠＄悊 | `delta_report.json` | 鈥?|
| 5 | 澶氳疆杩愯鈫掔粺璁¤绠椻啋浜旀€佸垽鍐斥啋鍥捐〃瀵煎嚭 | `verdict.json` | 5.1 鍙傛暟纭 |
| 6 | 鏁版嵁灏辩华妫€娴嬧啋鍙岃鎶ュ憡鐢熸垚(鍚ā鏉? | `reproduction_report.md/zh.md` | 鏁版嵁灏辩华 |
| 7 | 璇佹嵁鍖呪啋婧簮閾锯啋绛惧悕瀛樿瘉 | `artifact_bundle.zip` | 瀹屾暣鎬х‘璁?|

---

## 闃舵璇﹁堪 / Phase Detail

### Phase 0: 鍩虹璁炬柦妫€娴嬩笌閰嶇疆 / Infrastructure Detection & Setup

**杈撳叆**: 瀹夸富鎿嶄綔绯荤粺淇℃伅  
**杈撳嚭**: `infra/infra_manifest.json` + 鐜閰嶇疆  

0.1 **瀹夸富妫€娴?*: OS/GPU/鍐呭瓨/纾佺洏/铏氭嫙鍖?鈫?`infra/host_detection.json`  
0.2 **闇€姹傚垎鏋?*: 鎵弿璁烘枃鍏抽敭璇?(CUDA/MPI/Fortran/MATLAB) + 鍙鎬ч鍒?鈫?`info/feasibility_precheck.json`  
    - 鍐崇瓥鐭╅樀: Windows鈫扺SL2/Vagrant/Docker; macOS鈫扗ocker/Lima; Linux鈫扤ative/Docker  
0.3 **鐜鏋勫缓**: 璺緞 A WSL2 鈫?B Vagrant 鈫?C Docker 鈫?D Native (鎸夊簭 fallback)  
    - 澶辫触澶勭悊: `wsl --install` 澶辫触鈫掓鏌?BIOS 铏氭嫙鍖栤啋鍒?Vagrant; `vagrant up` 瓒呮椂鈫抈destroy -f && --no-provision`; `docker pull` 瓒呮椂鈫掗厤缃浗鍐呴暅鍍? 
0.4 **楠岃瘉**: 鏋舵瀯/鍐呮牳/鍐呭瓨/GPU/纾佺洏 鈫?`infra/infra_manifest.json`  
0.9 **GPU 閰嶇疆**: NVIDIA鈫扖UDA, AMD鈫扲OCm, Intel鈫扻PU, 闆嗘樉鈫扖PU  
    - 绮惧害 vs 鎬ц兘閰嶇疆: deterministic=False (鎬ц兘) / deterministic=True (鍙鐜?  
    - WSL2: 瀹夸富瑁?CUDA on WSL driver, WSL2 鍐呮棤闇€棰濆瀹夎  
    - Docker: `--gpus all` + nvidia/cuda 鍩虹闀滃儚  
    - 浜у嚭: `infra/gpu_manifest.json`  

馃敶 **G0**: 鍩虹璁炬柦妫€娴嬪畬鎴? manifest 宸查獙璇? GPU 閰嶇疆灏辩华, 鐜閰嶇疆榻愬銆備换涓€涓嶆弧瓒斥啋杩斿洖淇銆?
---

### Phase 0.5: 鐗堟湰绠＄悊 / Version Management

**杈撳叆**: `infra/infra_manifest.json` + 鐗堟湰绾跨储  
**杈撳嚭**: `env/version_spec.json` + `env/reproduction_manifest.json`  

0.5.1 **闇€姹傛娴?*: 鎵弿 `.python-version` / `Manifest.toml` / `.Rprofile` / `.nvmrc` / `CMakeLists.txt` 绛? 
0.5.2 **鐗堟湰绠＄悊鍣?*: pyenv/juliaup/rig/nvm/sdkman/rustup (缂哄け鍒欒嚜鍔ㄥ畨瑁?  
0.5.3 **鐗堟湰瀹夎**: pyenv install / juliaup add / rig add / nvm install / conda cudatoolkit / apt gcc 绛? 
0.5.4 **鐗堟湰閿佸畾**: conda env export 鈫?`conda-lock.yml`; pip freeze 鈫?`requirements-locked.txt`; 澶嶅埗 `Manifest.toml`; dpkg 蹇収  
0.5.5 **涓€鑷存€ч獙璇?*: 瀵规瘮 `version_spec.json` 涓庤繍琛岀増鏈? 璁板綍宸紓  

馃敶 **G1**: 鎵€鏈夎繍琛屾椂鐗堟湰涓?`version_spec.json` 涓€鑷? 閿佸畾鏂囦欢宸插啓鍏?`env/`銆傜増鏈笉鍖归厤鈫掍慨澶嶅悗缁х画銆?
---

### Phase 1: 璁烘枃瑙ｆ瀽涓庝笁鏂瑰闃?/ Paper Parsing & 3-Perspective Review

**杈撳叆**: PDF 鏂囦欢璺緞 / arXiv 閾炬帴  
**杈撳嚭**: `analysis/paper_summary.json` + 涓夋柟瀹￠槄鎶ュ憡 + `reproducibility_assessment.json`  

1.1 **PDF 瑙ｆ瀽**: 馃敶 纭 MinerU token 宸查厤缃? 
    - 浼樺厛绾? MinerU SDK (棣栭€? 鍚叕寮?琛ㄦ牸/鍥捐〃) 鈫?LaTeXML 鈫?PyMuPDF 鈫?OCR  
    - 鍙傛暟: `--model vlm`, `--ocr`, `--pages`, `--language`  
    - 鎵ц: `python scripts/math_pdf_extract.py <pdf> --output-dir analysis/`  
    - 鏃ョ敤閲忚窡韪? 鑷姩璁板綍鍒?`daily_usage.json` (闄愰 2000 椤?  
    - 浜у嚭: `analysis/parsed_text.md` + `analysis/formulas.tex`  

1.2 **缁撴瀯鍖栨彁鍙?*: 鏍稿績鏂规硶/鏁板鍏紡/瓒呭弬鏁?鏁版嵁闆?璇勪及鎸囨爣/鐏拌壊鍦板甫  

1.3 **棰嗗煙鍒嗙被**: 鍏抽敭璇?渚濊禆 鈫?璺敱鍒版暟鍊?绗﹀彿/AI4Math/缁熻/浼樺寲/缁忔祹瀛愮瓥鐣? 

1.4 **涓夋柟瑙嗚瀹￠槄**: 浣跨敤 `scripts/three_perspective_review.py`  
    - **鐮旂┒鐢?*: 娣卞害鐞嗚В (妗嗘灦 1-7 绔? 鈫?娑堣垂鏂? Phase 2-4 澶嶇幇璁″垝  
    - **瀵煎笀**: 鍙鐜版€ц瘎绾?鈫?娑堣垂鏂? G01 闂ㄧ  
    - **瀹＄浜?*: 鎵瑰垽瀹℃煡 鈫?娑堣垂鏂? Phase 5 鍒ゅ喅寮曟搸  
    - 闇€瑕?`LLM_API_KEY` 鐜鍙橀噺; 鏈厤缃椂杈撳嚭鍗犱綅鍒嗘瀽  
    - 浜у嚭: `analysis/<paper>_{student,advisor,reviewer}_review.md` + `reproducibility_assessment.json` + `review_manifest.json`  

馃敶 **G01 闂ㄧ**: 瀹℃煡 `reproducibility_assessment.json`  
    - `proceed` 鈫?鐩存帴杩?Phase 2  
    - `proceed_with_caution` 鈫?杩?Phase 2, 璁板綍宸茬煡椋庨櫓  
    - `needs_human_approval` 鈫?馃洃 STOP: 灞曠ず椋庨櫓鏍囪, 鑾峰彇鐢ㄦ埛纭  
    - `discourage` 鈫?馃洃 STOP: 涓嶅缓璁鐜? 灞曠ず鐞嗙敱  

---

### Phase 2: 鐜閲嶅缓 / Environment Setup

**杈撳叆**: `analysis/paper_summary.json` + `env/version_spec.json`  
**杈撳嚭**: `env/environment.yml` + `env/requirements-locked.txt`  

2.1 **渚濊禆鎵弿**: 鎵弿 repo 閰嶇疆鏂囦欢 (`requirements.txt`, `environment.yml`, `Manifest.toml`, `renv.lock`) + 闈欐€佸垎鏋?import  
2.2 **鐜鏋勫缓**: Conda/Mamba 鈫?Python venv 鈫?Julia 鈫?绯荤粺绾у簱 (閫愮骇 fallback)  
    - Conda 鍐茬獊鈫抈mamba clean --all && --force`; 浠嶅け璐モ啋閫愪釜瀹夎鏍稿績鍖? 
    - pip 瓒呮椂鈫抈--default-timeout=120`; 浠嶅け璐モ啋鍒嗘壒娆″厛绉戝璁＄畻鍐嶉鍩熷寘  
2.3 **纭畾鎬ч厤缃?*: 鍥哄畾闅忔満绉嶅瓙 (torch/np/random/tf) + 娴偣纭畾鎬?+ `PYTHONHASHSEED`  
2.4 **楠岃瘉**: 鍩虹瀵煎叆娴嬭瘯 + 鐗堟湰涓€鑷?+ GPU 鍙敤鎬?+ 閿佸畾  

馃敶 **G3**: 瀵煎叆娴嬭瘯閫氳繃, 閿佸畾鏂囦欢宸插啓鍏? GPU 鍙敤/宸查檷绾с€備换涓€涓嶆弧瓒斥啋杩斿洖 2.4 淇銆?
---

### Phase 3: 鍩虹嚎楠岃瘉 / Baseline Verification

**杈撳叆**: `analysis/paper_summary.json` + 灏辩华鐜  
**杈撳嚭**: `results/baseline_metrics.json` + `results/tolerance_spec.json` + `analysis/gray_areas.md`  

3.1 **杩愯瀹樻柟浠ｇ爜**: 鎸?README 鎵ц, 璁板綍瀹屾暣鏃ュ織  
3.2 **鎸囨爣瀵归綈**: 鎻愬彇鎵€鏈夋寚鏍?鈫?瀵规瘮璁烘枃澹扮О鍊?鈫?璁剧疆瀹瑰繊搴?(鏁板€?卤5%, 缁熻 95% CI, 瓒嬪娍涓€鑷?  
3.3 **鍩虹嚎澶辫触澶勭悊**: 鐜璇婃柇鈫掍唬鐮佹渶灏忎慨澶嶁啋璁板綍鍋忕鍒?`gray_areas.md`  
    - 澶辫触鍒嗘敮: bug 鏃犳硶缁曡繃鈫掓爣璁?`not_testable`; 鐜涓嶅彲閲嶅缓鈫掑垏 OS/瀹瑰櫒閲嶈瘯; 鍩虹嚎涓嶅彲寤衡啋杈撳嚭瀹屾暣璇婃柇  
3.4 **鍩虹嚎閿佸畾**: commit SHA + 澶嶇幇閿佸畾 + `reproduction_manifest.json` 鏇存柊  

馃敶 **G4**: 鍩虹嚎鎸囨爣宸茶褰? tolerance_spec 宸茶瀹氥€傚熀绾挎湭寤虹珛鈫掔敤鎴峰喅瀹氭槸鍚︾户缁繘 Phase 4銆?
---

### Phase 4: 澧為噺瀹炵幇 / Incremental Implementation (鎸夐渶)

**杈撳叆**: `analysis/paper_summary.json` + `results/baseline_metrics.json`  
**杈撳嚭**: `implementation/implementation_log.md` + `implementation/delta_report.json`  

4.1 **妯″潡鎷嗚В**: DAG 渚濊禆鍥?+ 姣忎釜妯″潡鐨?I/O 鎺ュ彛 + 鎷撴墤鎺掑簭 鈫?`implementation/modules_dag.json`  
4.2 **澧為噺寰幆** (鎸夋嫇鎵戝簭):
    1. 瀹炵幇褰撳墠妯″潡 (鏍囨敞璁烘枃鍏紡/绠楁硶缂栧彿)
    2. 灏忚妯℃祴璇? `python -c "from module import *; test_small()"`
    3. 瀵规瘮鍩虹嚎: `python analysis/compare.py --module <name> --baseline results/baseline_metrics.json`
    4. 璁板綍鍋忓樊鍒?`implementation/delta_report.json`
    5. delta 瓒呭蹇嶅害鈫掓帓鏌モ啋淇鈫掑洖鍒扮 2 姝?    6. 纭鍚?`git commit` 鈫?璁板綍鍒?`implementation_log.md` 鈫?涓嬩竴妯″潡
4.3 **浠ｇ爜绠＄悊**: 姣忎釜妯″潡鐙珛 commit (鍚鏂囧叕寮忕紪鍙?; 姣忎釜鍑芥暟 docstring 鍐?`Ref: Section X.Y, Eq.(Z)`; 棰嗗煙鍛藉悕绾﹀畾

---

### Phase 5: 瀹為獙楠岃瘉涓庣粺璁″垽鍐?/ Experiment Execution & Verdict

**杈撳叆**: 鍙繍琛屼唬鐮?+ `results/tolerance_spec.json`  
**杈撳嚭**: `results/raw_metrics.csv` + `reports/verdict.json` + `results/figures/` (鍥?+ 鐢熸垚浠ｇ爜)  

5.1 **澶氳疆杩愯**: 馃敶 纭鍙傛暟 (鍩虹嚎鍙? N=5 绉嶅瓙? 杩愯鏃堕棿? GPU 鍚敤?) 鈫?姣忚疆鐙珛鎵ц 鈫?`raw_metrics.csv`  
5.2 **缁熻璁＄畻**: 鍧囧€?x虅 + 鏍囧噯宸?s + 95% t-CI: x虅 卤 t路s/鈭歂 鈫?`statistical_summary.json`  
5.3 **浜旀€佸垽鍐?*: `within_ci`鈫掆湏 / `close_outside_ci`鈫掆増 / `outside_tolerance`鈫掆湕 / `not_testable`鈫掆殸 / `static_check_failed`鈫掆湕  
5.4 **璇婃柇杈撳嚭**: 鈮? 鏉¤瘖鏂亣璇?+ Top-12 澶辫触妯″紡 + 寮曠敤瀹＄浜鸿瑙掑彂鐜?鈫?`reports/diagnosis.md/zh.md`  
5.5 **鍥捐〃+浠ｇ爜瀵煎嚭**: 鏀舵暃鏇茬嚎/鎸囨爣瀵规瘮/娑堣瀺鍥?鈫?PNG+PDF + 姣忓浘闄勭嫭绔嬪彲杩愯 `results/figures/code/plot_*.py`  

**Top-12 澶辫触妯″紡**: 浠ｇ爜/鏁版嵁缂哄け | 鐜婕傜Щ | CUDA 鍐茬獊 | ABI 涓嶅吋瀹?| 渚濊禆鍐茬獊 | 闈炵‘瀹氭€?| BLAS 鍙樹綋 | 璺ㄥ钩鍙拌矾寰?| 鏁版嵁娉勯湶 | 棰勮缁冩潈閲嶆紓绉?| 閫夋嫨鎬ф姤鍛?| 涓婃父渚濊禆浣嶈厫

---

### Phase 6: 鍙岃鎶ュ憡鐢熸垚 / Bilingual Report Generation

**杈撳叆**: 鎵€鏈夐樁娈典骇鍑? 
**杈撳嚭**: `reports/` 涓嫳鍙岃鏂囨。  

馃敶 **纭鎵€鏈夋暟鎹氨缁?* 鈫?鍒ゅ喅/鍥捐〃/涓夋柟瀹￠槄/璺緞涓€鑷?鈫?鐢熸垚鎶ュ憡

**鏂囨。娓呭崟** (姣忎釜 `.md` + `.zh.md`):
- `reproduction_report.md` 鈥?瀹屾暣鎶ュ憡 (鍚ā鏉? 鍏冧俊鎭?鍒ゅ喅/鐜/瀹為獙缁撴灉/璇婃柇/閿佸畾)
- `comparison_table.md` 鈥?瀵规瘮琛?(鍙屽垪琛ㄦ牸: EN/ZH 骞惰)
- `diagnosis.md` 鈥?璇婃柇鍒嗘瀽
- `RUN_SUMMARY.md` 鈥?杩愯鎽樿 (鐘舵€?鍏抽敭缁撴灉/鐜/鍒跺搧)
- `verdict.json` 鈥?鍒ゅ喅 JSON (涓嫳鍙岃瀛楁)

**鏍煎紡**: 鑻辨枃鏍囬+涓枃鏍囬; 琛ㄦ牸鍒楀ご `Metric / 鎸囨爣`; 鏁板€肩粺涓€绮惧害; 鍥捐〃鏍囬 EN/ZH 鏍囨敞

---

### Phase 7: 鍒跺搧鎵撳寘涓庢函婧?/ Artifact Packaging & Provenance

**杈撳叆**: 鎵€鏈夐樁娈典骇鐗? 
**杈撳嚭**: `dist/artifact_bundle.zip` + `dist/provenance_chain.json`  

7.1 **璇佹嵁鍖?*: 浠ｇ爜蹇収 + 鐜閿佸畾 + 妫€娴嬫姤鍛?+ 鐗堟湰閿佸畾 + 杩愯鏃ュ織 + 鍘熷缁撴灉 + 涓夋柟瀹￠槄 + 鍙岃鎶ュ憡 鈫?鎵撳寘  
    馃敶 CHECKPOINT: 瀹屾暣鎬х‘璁?(SHA/閿佹枃浠?瀹￠槄/鍙岃閰嶅/鍥捐〃浠ｇ爜)  
7.2 **婧簮閾?*: 姣忔潯杈撳叆鈫掑鐞嗏啋杈撳嚭鐨?SHA-256 璁板綍 鈫?`provenance_chain.json`  
7.3 **绛惧悕**: GPG 绛惧悕 + ACM Badge 鐩稿瀛樿瘉 (鍙€夋彁浜ゅ叕鍏卞鐜拌处鏈?

---

## 闂ㄧ鎬昏〃 / Gate Map

| Gate | 浣嶇疆 | 鏉′欢 | 杩濆弽鍔ㄤ綔 |
|------|------|------|---------|
| G0 | Phase 0 鈫?0.5 | infra_manifest.json + GPU 灏辩华 | 杩斿洖淇 |
| G00 | Phase 0.9 | GPU 妗嗘灦妫€娴嬮€氳繃鎴?CPU 闄嶇骇 | 妫€鏌ラ┍鍔?|
| G01 馃敶 | Phase 1.4 鈫?2 | reproducibility_assessment 鍐崇瓥 proceed | 馃洃 鐢ㄦ埛浠嬪叆 |
| G1 | Phase 0.5 鈫?1 | 鐗堟湰涓€鑷存€ч€氳繃 | 淇鐗堟湰鍐茬獊 |
| G3 馃敶 | Phase 2 鈫?3 | 瀵煎叆娴嬭瘯+閿佸畾+GPU | 杩斿洖 2.4 |
| G4 馃敶 | Phase 3 鈫?4 | 鍩虹嚎鎸囨爣璁板綍+tolerance | 鐢ㄦ埛鍐崇瓥 |
| G5 | Phase 4 | 姣忎釜妯″潡 delta 鍦ㄩ鏈熷唴 | 鎺掓煡淇 |
| G6 | Phase 5 | 浜旀€佸垽鍐充骇鍑?| 琛ヨ窇缁熻 |
| G66 | Phase 5.5 | 鏈夊浘琛ㄦ椂姣忓浘鏈夌嫭绔嬫簮鐮?| 琛ュ鍑?|
| G7 | Phase 6 | 鎵€鏈夋姤鍛婁腑鑻卞弻璇?| 琛ヨ瘧 |
| G8 | Phase 7 | 璇佹嵁鍖呭畬鏁存€ф牎楠岄€氳繃 | 琛ユ枃浠?|

---

## 鏂囦欢缁撴瀯 / Directory Structure

```
reproduction/
鈹溾攢鈹€ SKILL.md
鈹溾攢鈹€ skills/registry.yaml
鈹溾攢鈹€ infra/              # 鍩虹璁炬柦 (manifest/Vagrantfile/Dockerfile/apptainer)
鈹溾攢鈹€ provisioning/       # 閰嶇疆鑴氭湰 (ansible/鐗堟湰绠＄悊鍣?CUDA/HPC)
鈹溾攢鈹€ env/                # 鐜閿佸畾 (version_spec/conda-lock/requirements/Manifest)
鈹溾攢鈹€ analysis/           # 璁烘枃鍒嗘瀽 (summary/parsed/formulas/gray_areas/涓夎瑙掑闃?
鈹溾攢鈹€ code/               # 浠ｇ爜 (Git repo)
鈹溾攢鈹€ logs/               # 杩愯鏃ュ織
鈹溾攢鈹€ results/            # 瀹為獙 (baseline/tolerance/raw/stat/figures+code)
鈹溾攢鈹€ reports/            # 鍙岃鎶ュ憡 (repro/comparison/verdict/diagnosis/RUN_SUMMARY/html)
鈹溾攢鈹€ implementation/     # 澧為噺瀹炵幇 (log/delta)
鈹斺攢鈹€ dist/               # 鍙戝竷鍒跺搧 (bundle/provenance)
```

## 渚濊禆涓庨厤缃?/ Dependencies & Configuration

| 鍖?| 鐢ㄩ€?| 瀹夎 |
|---|------|------|
| mineru-open-sdk | PDF鈫扢arkdown (鍚叕寮?琛ㄦ牸) | `pip install mineru-open-sdk` |
| openai | 涓夋柟瀹￠槄 LLM 鍚庣 | `pip install openai` |
| pyyaml | MinerU 閰嶇疆瑙ｆ瀽 | `pip install pyyaml` |

**鐜鍙橀噺**: `LLM_API_KEY` (蹇呭～), `LLM_API_BASE` (榛樿 `https://api.openai.com/v1`), `LLM_MODEL` (榛樿 `gpt-4o`)

**棣栨閰嶇疆**:
```bash
# MinerU token
mkdir -p ~/.mineru && echo "token: '浣犵殑API瀵嗛挜'" > ~/.mineru/config.yaml
# 鏉ユ簮: https://mineru.net/apiManage/token
# 渚濊禆瀹夎
pip install mineru-open-sdk openai pyyaml
# LLM API
export LLM_API_KEY='your-key'
```

## 鍐崇瓥鍝嶅簲 / Decision Responses

| 鎿嶄綔 | EN | ZH |
|------|----|-----|
| 鎵瑰噯 | approve / ok / yes | 鍙互 / 濂界殑 / 缁х画 / 鍚屾剰 / 鎵瑰噯 |
| 淇 | revise | 淇敼 |
| 鎷掔粷 | reject | 鎷掔粷 |
| 璺宠繃 | skip | 璺宠繃 |

**椋庨櫓鍒嗙骇**: 浣?鍙鍒嗘瀽, 鏃犻渶瀹℃壒) / 涓?杩愯鍓嶈鍒掑鎵? / 楂?閫愭潯瀹℃壒)

## 鍙傝€冩枃鐚?/ References

- MaRDI Mathematical Research Data Initiative. https://www.mardi4nfdi.de/
- ICERM Workshop on Reproducibility in Computational and Experimental Mathematics (2012)
- ConanXu-math/Scientific-Computing-Reproduction---Auto-Tuning
- OpenResearch. https://github.com/armaanamatya/openresearch
- paper-replay. https://github.com/bettyguo/paper-replay
- repro-agent. https://github.com/hqygtr-prog/repro-agent
- MaRDIFlow: A Workflow Framework for Documentation and Integration of FAIR Computational Experiments
- repo2docker. https://repo2docker.readthedocs.io/
- Apptainer. https://apptainer.org/



