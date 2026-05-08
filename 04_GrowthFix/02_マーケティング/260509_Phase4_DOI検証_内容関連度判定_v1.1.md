# Phase 4：DOI 検証 + 内容関連度判定 v1.1（260509）

> **目的：** Phase 4 v1.0 で厳選した 50 論文に対し、(1) **Crossref API で DOI 実在確認**（Layer 3 三段検証）+ (2) **内容関連度判定**（abstract / title にコア主張キーワードが含まれるか）を実施。
> **重要発見：** OpenAlex の検索（被引用数降順）では、Gravity 主張と **無関係な高引用論文**が混入する傾向。内容関連度判定で 🟢高 / 🟡中 / 🔴低 にフラグ。
> **次工程：** 1 論文ずつ石井さんとスパーリング形式で目利き → 真に Gravity を裏付ける論文だけを Phase 5（媒体配置）へ進める
> **作成：** 2026-05-09（土）

---

## 0. 検証サマリ

| 項目 | 値 |
|---|---|
| 検証対象 | 50 論文（Phase 4 v1.0 厳選）|
| **Crossref DOI 実在確認** | ✅ 45 件 / ❌ 5 件（DOI なし or 404）|
| **内容関連度 🟢 高（キーワード ≥ 3 一致）** | **1 件**（即採用候補）|
| **内容関連度 🟡 中（キーワード 1-2 一致）** | **5 件**（要石井判断）|
| **内容関連度 🔴 低（キーワード 0 一致）** | **44 件**（除外候補・OpenAlex 検索ノイズ）|

→ **🟢 + 🟡 = 6 件**を石井さん目利きスパーリングの候補リストへ。🔴 は基本除外（再検索が必要なら別クエリで取り直し）。


---

## コア主張 #1 個人引力 3 要素整合（Why × 才能 × 偏愛）

### ✗ #01（賛成・🔴 低（無関係の可能性））Job demands–resources theory: Taking stock and looking forward.（2016・引用 5757）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Job demands–resources theory: Taking stock and looking forward.
- **Crossref 著者：** Arnold B. Bakker / Evangelia Demerouti
- **Crossref 媒体：** Journal of Occupational Health Psychology
- **DOI URL：** https://doi.org/10.1037/ocp0000056
- **OpenAlex 著者：** Arnold B. Bakker / Evangelia Demerouti
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://pure.eur.nl/ws/files/176689432/Job_Demands-Resources_theory.pdf
- **要旨：** The job demands-resources (JD-R) model was introduced in the international literature 15 years ago (Demerouti, Bakker, Nachreiner, & Schaufeli, 2001). The model has been applied in
- **出典クエリ：** 1.2

### ★ #02（賛成・🟢 高）Intrinsic and extrinsic motivation from a self-determination theory perspective: Definitions, theory, practices, and future directions（2020・引用 4878）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Intrinsic and extrinsic motivation from a self-determination theory perspective: Definitions, theory, practices, and future directions
- **Crossref 著者：** Richard M. Ryan / Edward L. Deci
- **Crossref 媒体：** Contemporary Educational Psychology
- **DOI URL：** https://doi.org/10.1016/j.cedpsych.2020.101860
- **OpenAlex 著者：** Richard M. Ryan / Edward L. Deci
- **キーワード一致：** motivation, self-determination, intrinsic（3 個）
- **出典クエリ：** 1.2

### ✗ #03（賛成・🔴 低（無関係の可能性））Beyond Adoption: A New Framework for Theorizing and Evaluating Nonadoption, Abandonment, and Challenges to the Scale-Up, Spread, and Sustainability of Health and Care Technologies（2017・引用 2574）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Beyond Adoption: A New Framework for Theorizing and Evaluating Nonadoption, Abandonment, and Challenges to the Scale-Up, Spread, and Sustainability of Health and Care Technologies
- **Crossref 著者：** Trisha Greenhalgh / Joseph Wherton / Chrysanthi Papoutsi 他
- **Crossref 媒体：** Journal of Medical Internet Research
- **DOI URL：** https://doi.org/10.2196/jmir.8775
- **OpenAlex 著者：** Trisha Greenhalgh / Joseph Wherton / Chrysanthi Papoutsi
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://www.jmir.org/2017/11/e367/PDF
- **要旨：** BACKGROUND: Many promising technological innovations in health and social care are characterized by nonadoption or abandonment by individuals or by failed attempts to scale up loca
- **出典クエリ：** 1.1

### ✗ #04（反論・🔴 低（無関係の可能性））Artificial Intelligence (AI): Multidisciplinary perspectives on emerging challenges, opportunities, and agenda for research, practice and policy（2019・引用 3917）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Artificial Intelligence (AI): Multidisciplinary perspectives on emerging challenges, opportunities, and agenda for research, practice and policy
- **Crossref 著者：** Yogesh K. Dwivedi / Laurie Hughes / Elvira Ismagilova 他
- **Crossref 媒体：** International Journal of Information Management
- **DOI URL：** https://doi.org/10.1016/j.ijinfomgt.2019.08.002
- **OpenAlex 著者：** Yogesh K. Dwivedi / Laurie Hughes / Elvira Ismagilova
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://www.sciencedirect.com/science/article/pii/S026840121930917X
- **要旨：** As far back as the industrial revolution, significant development in technical innovation has succeeded in transforming numerous manual tasks and processes that had been in existen
- **出典クエリ：** 1.4

### ✗ #05（反論・🔴 低（無関係の可能性））The Lancet Commission on global mental health and sustainable development（2018・引用 3333）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** The Lancet Commission on global mental health and sustainable development
- **Crossref 著者：** Vikram Patel / Shekhar Saxena / Crick Lund 他
- **Crossref 媒体：** The Lancet
- **DOI URL：** https://doi.org/10.1016/s0140-6736(18)31612-x
- **OpenAlex 著者：** Vikram Patel / Shekhar Saxena / Crick Lund
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://kclpure.kcl.ac.uk/ws/files/102654274/The_Lancet_Commission_on_PATEL_Firstonline16October2018_GREEN_AAM_CC_BY_NC_ND_.pdf
- **出典クエリ：** 1.4


---

## コア主張 #2 組織引力 4 型（集まる軸 × 躍動軸）

### ◇ #06（賛成・🟡 中）A theory of organizational readiness for change（2009・引用 2126）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** A theory of organizational readiness for change
- **Crossref 著者：** Bryan J Weiner
- **Crossref 媒体：** Implementation Science
- **DOI URL：** https://doi.org/10.1186/1748-5908-4-67
- **OpenAlex 著者：** Bryan J. Weiner
- **キーワード一致：** organization（1 個）
- **OA PDF：** https://implementationscience.biomedcentral.com/counter/pdf/10.1186/1748-5908-4-67
- **要旨：** BACKGROUND: Change management experts have emphasized the importance of establishing organizational readiness for change and recommended various strategies for creating it. Althoug
- **出典クエリ：** 2.2

### ✗ #07（賛成・🔴 低（無関係の可能性））Educating the Net Generation（2005・引用 2123）
- **DOI 検証：** ❌ DOI なし
- **OpenAlex 著者：** Diana G. Oblinger / J.L. Oblinger / Joan K. Lippincott
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** http://www.cdc.qc.ca/url_regard/023910b.html
- **要旨：** This is a book for educators.Those who have chosen to be educators are generally dedicated to students.But, sometimes we don't quite understand what we are seeing.We hope this book
- **出典クエリ：** 2.1

### ✗ #08（賛成・🔴 低（無関係の可能性））Field Experiments（2004・引用 2054）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Field Experiments
- **Crossref 著者：** Glenn W Harrison / John A List
- **Crossref 媒体：** Journal of Economic Literature
- **DOI URL：** https://doi.org/10.1257/0022051043004577
- **OpenAlex 著者：** Glenn W. Harrison / John A. List
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://stars.library.ucf.edu/cgi/viewcontent.cgi?article=5410&context=facultybib2000
- **要旨：** Experimental economists are leaving the reservation. They are recruiting subjects in the field rather than in the classroom, using field goods rather than induced valuations, and u
- **出典クエリ：** 2.1

### ✗ #09（反論・🔴 低（無関係の可能性））Induction of Decision Trees（1986・引用 14691）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Induction of Decision Trees
- **Crossref 著者：** J.R. Quinlan
- **Crossref 媒体：** Machine Learning
- **DOI URL：** https://doi.org/10.1023/a:1022643204877
- **OpenAlex 著者：** J. R. Quinlan
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://link.springer.com/content/pdf/10.1023%2FA%3A1022643204877.pdf
- **出典クエリ：** 2.5

### ✗ #10（反論・🔴 低（無関係の可能性））Induction of decision trees（1986・引用 12362）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Induction of decision trees
- **Crossref 著者：** J. R. Quinlan
- **Crossref 媒体：** Machine Learning
- **DOI URL：** https://doi.org/10.1007/bf00116251
- **OpenAlex 著者：** J. R. Quinlan
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://link.springer.com/content/pdf/10.1007/BF00116251.pdf
- **出典クエリ：** 2.5


---

## コア主張 #3 個人 → 組織翻訳機構

### ◇ #11（賛成・🟡 中）The Psychology of Entrepreneurship（2014・引用 900）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** The Psychology of Entrepreneurship
- **Crossref 著者：** Michael Frese / Michael M. Gielnik
- **Crossref 媒体：** Annual Review of Organizational Psychology and Organizational Behavior
- **DOI URL：** https://doi.org/10.1146/annurev-orgpsych-031413-091326
- **OpenAlex 著者：** Michael Fresé / Michael M. Gielnik
- **キーワード一致：** personality（1 個）
- **OA PDF：** https://www.annualreviews.org/doi/pdf/10.1146/annurev-orgpsych-031413-091326
- **要旨：** In this review of the psychology of entrepreneurship, we first present meta-analytic findings showing that personality dimensions, such as (general) self-efficacy and need for achi
- **出典クエリ：** 3.1

### ✗ #12（賛成・🔴 低（無関係の可能性））Doing More with Less: Innovation Input and Output in Family Firms（2015・引用 893）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Doing More with Less: Innovation Input and Output in Family Firms
- **Crossref 著者：** Patricio Duran / Nadine Kammerlander / Marc van Essen 他
- **Crossref 媒体：** Academy of Management Journal
- **DOI URL：** https://doi.org/10.5465/amj.2014.0424
- **OpenAlex 著者：** Patricio Durán / Nadine Kammerlander / Marc van Essen
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://dspace.library.uu.nl/handle/1874/343202
- **要旨：** Family firms are often portrayed as an important yet conservative form of organization that is reluctant to invest in innovation; however, simultaneously, evidence has shown that f
- **出典クエリ：** 3.1

### ✗ #13（賛成・🔴 低（無関係の可能性））How Experience and Network Ties Affect the Influence of Demographic Minorities on Corporate Boards（2000・引用 775）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** How Experience and Network Ties Affect the Influence of Demographic Minorities on Corporate Boards
- **Crossref 著者：** James D. Westphal / Laurie P. Milton
- **Crossref 媒体：** Administrative Science Quarterly
- **DOI URL：** https://doi.org/10.2307/2667075
- **OpenAlex 著者：** James D. Westphal / Laurie P. Milton
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://repositories.lib.utexas.edu/bitstreams/4e81aaaf-2979-4bc5-a28a-12a418e313cd/download
- **要旨：** This study examines how the influence of directors who are demographic minorities on corporate boards is contingent on the prior experience of board members and the larger social s
- **出典クエリ：** 3.1

### ✗ #14（反論・🔴 低（無関係の可能性））Dynamic capabilities: what are they?（2000・引用 14330）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Dynamic capabilities: what are they?
- **Crossref 著者：** Kathleen M. Eisenhardt / Jeffrey A. Martin
- **Crossref 媒体：** Strategic Management Journal
- **DOI URL：** https://doi.org/10.1002/1097-0266(200010/11)21:10/11<1105::aid-smj133>3.0.co;2-e
- **OpenAlex 著者：** Kathleen M. Eisenhardt / Jeffrey A. Martin
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/1097-0266%28200010/11%2921%3A10/11%3C1105%3A%3AAID-SMJ133%3E3.0.CO%3B2-E
- **要旨：** This paper focuses on dynamic capabilities and, more generally, the resource-based view of the firm. We argue that dynamic capabilities are a set of specific and identifiable proce
- **出典クエリ：** 3.4

### ✗ #15（反論・🔴 低（無関係の可能性））Entrepreneurial Orientation and Business Performance: An Assessment of past Research and Suggestions for the Future（2009・引用 3423）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Entrepreneurial Orientation and Business Performance: An Assessment of past Research and Suggestions for the Future
- **Crossref 著者：** Andreas Rauch / Johan Wiklund / G.T. Lumpkin 他
- **Crossref 媒体：** Entrepreneurship Theory and Practice
- **DOI URL：** https://doi.org/10.1111/j.1540-6520.2009.00308.x
- **OpenAlex 著者：** Andreas Rauch / Johan Wiklund / G. T. Lumpkin
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** http://hdl.handle.net/10036/4249
- **要旨：** Entrepreneurial orientation (EO) has received substantial conceptual and empirical attention, representing one of the few areas in entrepreneurship research where a cumulative body
- **出典クエリ：** 3.4


---

## コア主張 #4 AI 速度非対称性

### ◇ #16（賛成・🟡 中）Automation, Algorithms, and Beyond: Why Work Design Matters More Than Ever in a Digital World（2019・引用 733）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Automation, Algorithms, and Beyond: Why Work Design Matters More Than Ever in a Digital World
- **Crossref 著者：** Sharon K. Parker / Gudela Grote
- **Crossref 媒体：** Applied Psychology
- **DOI URL：** https://doi.org/10.1111/apps.12241
- **OpenAlex 著者：** Sharon K. Parker / Gudela Grote
- **キーワード一致：** automation（1 個）
- **OA PDF：** https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/apps.12241
- **要旨：** Abstract We propose a central role for work design in understanding the effects of digital technologies. We give examples of how new technologies can—depending on various factors—p
- **出典クエリ：** 4.3

### ✗ #17（賛成・🔴 低（無関係の可能性））The role of internet-related technologies in shaping the work of accountants: New directions for accounting research（2019・引用 600）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** The role of internet-related technologies in shaping the work of accountants: New directions for accounting research
- **Crossref 著者：** Jodie Moll / Ogan Yigitbasioglu
- **Crossref 媒体：** The British Accounting Review
- **DOI URL：** https://doi.org/10.1016/j.bar.2019.04.002
- **OpenAlex 著者：** Jodie Moll / Ogan Yigitbasioglu
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://research.manchester.ac.uk/en/publications/b4555940-fbb0-4f8f-be9b-18cd5a6256e3
- **出典クエリ：** 4.2

### ◇ #18（賛成・🟡 中）Six Human-Centered Artificial Intelligence Grand Challenges（2023・引用 420）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Six Human-Centered Artificial Intelligence Grand Challenges
- **Crossref 著者：** Ozlem Ozmen Garibay / Brent Winslow / Salvatore Andolina 他
- **Crossref 媒体：** International Journal of Human–Computer Interaction
- **DOI URL：** https://doi.org/10.1080/10447318.2022.2153320
- **OpenAlex 著者：** Özlem Özmen Garibay / Brent Winslow / Salvatore Andolina
- **キーワード一致：** ai, artificial intelligence（2 個）
- **OA PDF：** https://www.tandfonline.com/doi/pdf/10.1080/10447318.2022.2153320?needAccess=true&role=button
- **要旨：** Widespread adoption of artificial intelligence (AI) technologies is substantially affecting the human condition in ways that are not yet well understood. Negative unintended conseq
- **出典クエリ：** 4.1

### ✗ #19（反論・🔴 低（無関係の可能性））Global burden of 369 diseases and injuries in 204 countries and territories, 1990–2019: a systematic analysis for the Global Burden of Disease Study 2019（2020・引用 18808）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Global burden of 369 diseases and injuries in 204 countries and territories, 1990–2019: a systematic analysis for the Global Burden of Disease Study 2019
- **Crossref 著者：** Theo Vos / Stephen S Lim / Cristiana Abbafati 他
- **Crossref 媒体：** The Lancet
- **DOI URL：** https://doi.org/10.1016/s0140-6736(20)30925-9
- **OpenAlex 著者：** Theo Vos / Stephen S Lim / Cristiana Abbafati
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** http://www.thelancet.com/article/S0140673620309259/pdf
- **要旨：** BACKGROUND: In an era of shifting global agendas and expanded emphasis on non-communicable diseases and injuries along with communicable diseases, sound evidence on trends by cause
- **出典クエリ：** 4.4

### ✗ #20（反論・🔴 低（無関係の可能性））Data clustering（1999・引用 13137）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Data clustering
- **Crossref 著者：** A. K. Jain / M. N. Murty / P. J. Flynn
- **Crossref 媒体：** ACM Computing Surveys
- **DOI URL：** https://doi.org/10.1145/331499.331504
- **OpenAlex 著者：** Anil K. Jain / M. Narasimha Murty / Patrick J. Flynn
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://dl.acm.org/doi/pdf/10.1145/331499.331504
- **要旨：** Clustering is the unsupervised classification of patterns (observations, data items, or feature vectors) into groups (clusters). The clustering problem has been addressed in many c
- **出典クエリ：** 4.4


---

## コア主張 #5 能力の輪

### ✗ #21（賛成・🔴 低（無関係の可能性））Deciphering the Liquidity and Credit Crunch 2007–2008（2009・引用 3384）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Deciphering the Liquidity and Credit Crunch 2007–2008
- **Crossref 著者：** Markus K Brunnermeier
- **Crossref 媒体：** Journal of Economic Perspectives
- **DOI URL：** https://doi.org/10.1257/jep.23.1.77
- **OpenAlex 著者：** Markus K. Brunnermeier
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://www.aeaweb.org/articles/pdf/doi/10.1257/jep.23.1.77
- **要旨：** The financial market turmoil in 2007 and 2008 has led to the most severe financial crisis since the Great Depression and threatens to have large repercussions on the real economy. 
- **出典クエリ：** 5.3

### ✗ #22（賛成・🔴 低（無関係の可能性））The Future of the Internet--And How to Stop It（2008・引用 1387）
- **DOI 検証：** ❌ DOI なし
- **OpenAlex 著者：** Jonathan Zittrain
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** http://nrs.harvard.edu/urn-3:HUL.InstRepos:4455262
- **要旨：** This extraordinary book explains the engine that has catapulted the Internet from backwater to ubiquity—and reveals that it is sputtering precisely because of its runaway success. 
- **出典クエリ：** 5.1

### ✗ #23（賛成・🔴 低（無関係の可能性））Theory and research in strategic management: Swings of a pendulum（1999・引用 1287）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Theory and research in strategic management: Swings of a pendulum
- **Crossref 著者：** Robert E. Hoskisson / Michael A. Hitt / William P. Wan 他
- **Crossref 媒体：** Journal of Management
- **DOI URL：** https://doi.org/10.1177/014920639902500307
- **OpenAlex 著者：** Robert E. Hoskisson / Michael A. Hitt / William P. Wan
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://ink.library.smu.edu.sg/lkcsb_research/7339
- **要旨：** The development of the field of strategic management within the last two decades has been dramatic. While its roots have been in a more applied area, often referred to as business 
- **出典クエリ：** 5.1

### ✗ #24（反論・🔴 低（無関係の可能性））Designing qualitative research（1989・引用 9931）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Designing qualitative research
- **Crossref 著者：** 
- **Crossref 媒体：** Choice Reviews Online
- **DOI URL：** https://doi.org/10.5860/choice.27-1232
- **OpenAlex 著者：** Shaliha, Farnaz / Mozaffari, Maryam / Ramezani, Faeze
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://www.drugsandalcohol.ie/11280/1/Drugnet_19.pdf
- **要旨：** Objectives: This study investigated the relationship between sleep quality during pregnancy and preterm birth.&#13;\nMethods: This longitudinal study was conducted between August 2
- **出典クエリ：** 5.4

### ✗ #25（反論・🔴 低（無関係の可能性））Using social and behavioural science to support COVID-19 pandemic response（2020・引用 5030）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Using social and behavioural science to support COVID-19 pandemic response
- **Crossref 著者：** Jay J. Van Bavel / Katherine Baicker / Paulo S. Boggio 他
- **Crossref 媒体：** Nature Human Behaviour
- **DOI URL：** https://doi.org/10.1038/s41562-020-0884-z
- **OpenAlex 著者：** Jay Joseph Van Bavel / Katherine Baicker / Paulo S. Boggio
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://www.nature.com/articles/s41562-020-0884-z.pdf
- **出典クエリ：** 5.4


---

## コア主張 #6 ネガティブ・ケイパビリティ

### ✗ #26（賛成・🔴 低（無関係の可能性））Fostering implementation of health services research findings into practice: a consolidated framework for advancing implementation science（2009・引用 14613）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Fostering implementation of health services research findings into practice: a consolidated framework for advancing implementation science
- **Crossref 著者：** Laura J Damschroder / David C Aron / Rosalind E Keith 他
- **Crossref 媒体：** Implementation Science
- **DOI URL：** https://doi.org/10.1186/1748-5908-4-50
- **OpenAlex 著者：** Laura J. Damschroder / David C. Aron / Rosalind E. Keith
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://implementationscience.biomedcentral.com/counter/pdf/10.1186/1748-5908-4-50
- **要旨：** BACKGROUND: Many interventions found to be effective in health services research studies fail to translate into meaningful patient care outcomes across multiple contexts. Health se
- **出典クエリ：** 6.1

### ✗ #27（賛成・🔴 低（無関係の可能性））Molecular mechanisms of cell death: recommendations of the Nomenclature Committee on Cell Death 2018（2018・引用 6387）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Molecular mechanisms of cell death: recommendations of the Nomenclature Committee on Cell Death 2018
- **Crossref 著者：** Lorenzo Galluzzi / Ilio Vitale / Stuart A. Aaronson 他
- **Crossref 媒体：** Cell Death &amp; Differentiation
- **DOI URL：** https://doi.org/10.1038/s41418-017-0012-4
- **OpenAlex 著者：** Lorenzo Galluzzi / Ilio Vitale / Stuart A. Aaronson
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://www.nature.com/articles/s41418-017-0012-4.pdf
- **出典クエリ：** 6.2

### ✗ #28（賛成・🔴 低（無関係の可能性））The China Syndrome: Local Labor Market Effects of Import Competition in the United States（2013・引用 4264）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** The China Syndrome: Local Labor Market Effects of Import Competition in the United States
- **Crossref 著者：** David H Autor / David Dorn / Gordon H Hanson
- **Crossref 媒体：** American Economic Review
- **DOI URL：** https://doi.org/10.1257/aer.103.6.2121
- **OpenAlex 著者：** David Autor / David Dorn / Gordon Hanson
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://www.aeaweb.org/articles/pdf/doi/10.1257/aer.103.6.2121
- **要旨：** We analyze the effect of rising Chinese import competition between 1990 and 2007 on US local labor markets, exploiting cross-market variation in import exposure stemming from initi
- **出典クエリ：** 6.2

### ✗ #29（反論・🔴 低（無関係の可能性））Development and Distortion of Malaysian Public- Private Partnerships: Patronage, Privatised Profits and Pitfalls DOI: 10.1111/j.1467- 8500.2009.00655.x（2010・引用 16138）
- **DOI 検証：** ❌ Crossref HTTP 404
- **OpenAlex 著者：** Loo‐See Beh
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** http://civis.se/Cifras-de-la-situacion-de-los-y
- **要旨：** Americanae nace como un proyecto conjunto que surge dentro de la Red Europea de Información y Documentación sobre América Latina (REDIAL), y que ha afrontado la Biblioteca de la Ag
- **出典クエリ：** 6.4

### ✗ #30（反論・🔴 低（無関係の可能性））Diagnosis and Management of the Metabolic Syndrome（2005・引用 11734）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Diagnosis and Management of the Metabolic Syndrome
- **Crossref 著者：** Scott M. Grundy / James I. Cleeman / Stephen R. Daniels 他
- **Crossref 媒体：** Circulation
- **DOI URL：** https://doi.org/10.1161/circulationaha.105.169404
- **OpenAlex 著者：** Scott M. Grundy / James I. Cleeman / Stephen R. Daniels
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://www.ahajournals.org/doi/pdf/10.1161/CIRCULATIONAHA.105.169404
- **要旨：** The metabolic syndrome has received increased attention in the past few years. This statement from the American Heart Association (AHA) and the National Heart, Lung, and Blood Inst
- **出典クエリ：** 6.4


---

## コア主張 #7 have to 検出

### ✗ #31（賛成・🔴 低（無関係の可能性））American Institute of Certified Public Accountants (AICPA)（2018・引用 1510）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** American Institute of Certified Public Accountants (AICPA)
- **Crossref 著者：** 
- **Crossref 媒体：** The Grants Register 2018
- **DOI URL：** https://doi.org/10.1007/978-1-349-94186-5_84
- **OpenAlex 著者：** A-T Children' / SIRIUS Project / Cynthia Rothblum‐Oviatt
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://link.springer.com/content/pdf/10.1007%2F978-1-349-94186-5_84.pdf
- **要旨：** The A-T Children's Project is a non-profit organization that raises funds to support and co-ordinate biomedical research projects, scientific conferences and a clinical centre aime
- **出典クエリ：** 7.3

### ✗ #32（賛成・🔴 低（無関係の可能性））2014 AHA/ACC Guideline for the Management of Patients With Non–ST-Elevation Acute Coronary Syndromes: Executive Summary（2014・引用 1252）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** 2014 AHA/ACC Guideline for the Management of Patients With Non–ST-Elevation Acute Coronary Syndromes: Executive Summary
- **Crossref 著者：** Ezra A. Amsterdam / Nanette K. Wenger / Ralph G. Brindis 他
- **Crossref 媒体：** Circulation
- **DOI URL：** https://doi.org/10.1161/cir.0000000000000133
- **OpenAlex 著者：** Ezra A. Amsterdam / Nanette K. Wenger / Ralph G. Brindis
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://www.ahajournals.org/doi/pdf/10.1161/CIR.0000000000000133
- **要旨：** The writing
- **出典クエリ：** 7.3

### ◇ #33（賛成・🟡 中）Teacher Wellbeing: The Importance of Teacher–Student Relationships（2011・引用 1041）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Teacher Wellbeing: The Importance of Teacher–Student Relationships
- **Crossref 著者：** Jantine L. Spilt / Helma M. Y. Koomen / Jochem T. Thijs
- **Crossref 媒体：** Educational Psychology Review
- **DOI URL：** https://doi.org/10.1007/s10648-011-9170-y
- **OpenAlex 著者：** Jantine L. Spilt / Helma M. Y. Koomen / Jochem Thijs
- **キーワード一致：** act（1 個）
- **OA PDF：** https://link.springer.com/content/pdf/10.1007/s10648-011-9170-y.pdf
- **要旨：** Many studies have examined the importance of teacher–student relationships for the development of children. Much less is known, however, about how these relationships impact the pr
- **出典クエリ：** 7.1

### ✗ #34（反論・🔴 低（無関係の可能性））AI Art: Machine Visions and Warped Dreams（2020・引用 160）
- **DOI 検証：** ❌ DOI なし
- **OpenAlex 著者：** Joanna Żylińska
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://research.gold.ac.uk/29131/1/Zylinska_2020_AI-and-Art.pdf
- **要旨：** Can computers be creative? Is algorithmic art just a form of Candy Crush? Cutting through the smoke and mirrors surrounding computation, robotics and artificial intelligence, Joann
- **出典クエリ：** 7.4

### ✗ #35（反論・🔴 低（無関係の可能性））Righting past wrongs: A superintendent’s social justice leadership for dual language education along the U.S.-Mexico border（2017・引用 144）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Righting past wrongs: A superintendent’s social justice leadership for dual language education along the U.S.-Mexico border
- **Crossref 著者：** David DeMatthews / Elena Izquierdo / David S. Knight
- **Crossref 媒体：** Education Policy Analysis Archives
- **DOI URL：** https://doi.org/10.14507/epaa.25.2436
- **OpenAlex 著者：** David E. DeMatthews / Elena Izquierdo / David S. Knight
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://epaa.asu.edu/ojs/article/download/2436/1859
- **要旨：** The role of superintendents in adopting and developing dual language education and other equity-oriented reforms that support the unique needs of Latina/o emergent bilinguals is a 
- **出典クエリ：** 7.4


---

## コア主張 #8 コーチング × コンサル × ソマティクス

### ✗ #36（賛成・🔴 低（無関係の可能性））The Theory and Practice of Online Learning（2008・引用 1823）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** The Theory and Practice of Online Learning
- **Crossref 著者：** 
- **Crossref 媒体：** (不明)
- **DOI URL：** https://doi.org/10.15215/aupress/9781897425084.01
- **OpenAlex 著者：** Terry Anderson / Mohamed Ally / M Ally
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://www.aupress.ca/app/uploads/120146_99Z_Anderson_2008-Theory_and_Practice_of_Online_Learning.pdf
- **要旨：** The revised version of the Theory and Practice of Online Learning, edited by Terry Anderson, brings together recent developments in both the practice and our understanding of onlin
- **出典クエリ：** 8.1

### ✗ #37（賛成・🔴 低（無関係の可能性））Strategic talent management: A review and research agenda（2009・引用 1758）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Strategic talent management: A review and research agenda
- **Crossref 著者：** David G. Collings / Kamel Mellahi
- **Crossref 媒体：** Human Resource Management Review
- **DOI URL：** https://doi.org/10.1016/j.hrmr.2009.04.001
- **OpenAlex 著者：** David G. Collings / Kamel Mellahi
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** http://hdl.handle.net/10379/683
- **出典クエリ：** 8.1

### ✗ #38（賛成・🔴 低（無関係の可能性））A vision for the future of genomics research（2003・引用 1741）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** A vision for the future of genomics research
- **Crossref 著者：** Francis S. Collins / Eric D. Green / Alan E. Guttmacher 他
- **Crossref 媒体：** Nature
- **DOI URL：** https://doi.org/10.1038/nature01626
- **OpenAlex 著者：** Francis S. Collins / Eric D. Green / Alan E. Guttmacher
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://www.nature.com/articles/nature01626.pdf
- **出典クエリ：** 8.2

### ✗ #39（反論・🔴 低（無関係の可能性））The Pascal Visual Object Classes (VOC) Challenge（2009・引用 19357）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** The Pascal Visual Object Classes (VOC) Challenge
- **Crossref 著者：** Mark Everingham / Luc Van Gool / Christopher K. I. Williams 他
- **Crossref 媒体：** International Journal of Computer Vision
- **DOI URL：** https://doi.org/10.1007/s11263-009-0275-4
- **OpenAlex 著者：** Mark Everingham / Luc Van Gool / Christopher K. I. Williams
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://www.pure.ed.ac.uk/ws/files/7879113/ijcv_voc09.pdf
- **出典クエリ：** 8.4

### ✗ #40（反論・🔴 低（無関係の可能性））MUSCLE: a multiple sequence alignment method with reduced time and space complexity（2004・引用 9313）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** MUSCLE: a multiple sequence alignment method with reduced time and space complexity
- **Crossref 著者：** Robert C Edgar
- **Crossref 媒体：** BMC Bioinformatics
- **DOI URL：** https://doi.org/10.1186/1471-2105-5-113
- **OpenAlex 著者：** R. C. Edgar
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://bmcbioinformatics.biomedcentral.com/counter/pdf/10.1186/1471-2105-5-113
- **要旨：** BACKGROUND: In a previous paper, we introduced MUSCLE, a new program for creating multiple alignments of protein sequences, giving a brief summary of the algorithm and showing MUSC
- **出典クエリ：** 8.4


---

## コア主張 #9 キャラ命名手法

### ✗ #41（賛成・🔴 低（無関係の可能性））Fostering implementation of health services research findings into practice: a consolidated framework for advancing implementation science（2009・引用 14613）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Fostering implementation of health services research findings into practice: a consolidated framework for advancing implementation science
- **Crossref 著者：** Laura J Damschroder / David C Aron / Rosalind E Keith 他
- **Crossref 媒体：** Implementation Science
- **DOI URL：** https://doi.org/10.1186/1748-5908-4-50
- **OpenAlex 著者：** Laura J. Damschroder / David C. Aron / Rosalind E. Keith
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://implementationscience.biomedcentral.com/counter/pdf/10.1186/1748-5908-4-50
- **要旨：** BACKGROUND: Many interventions found to be effective in health services research studies fail to translate into meaningful patient care outcomes across multiple contexts. Health se
- **出典クエリ：** 9.2

### ✗ #42（賛成・🔴 低（無関係の可能性））International regimes, transactions, and change: embedded liberalism in the postwar economic order（1982・引用 4403）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** International regimes, transactions, and change: embedded liberalism in the postwar economic order
- **Crossref 著者：** John Gerard Ruggie
- **Crossref 媒体：** International Organization
- **DOI URL：** https://doi.org/10.1017/s0020818300018993
- **OpenAlex 著者：** John Gerard Ruggie
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://www.cambridge.org/core/services/aop-cambridge-core/content/view/238A600FEFE7EDBC2DDAB30E6A28B4D9/S0020818300018993a.pdf/div-class-title-international-regimes-transactions-and-change-embedded-liberalism-in-the-postwar-economic-order-div.pdf
- **要旨：** The prevailing model of international economic regimes is strictly positivistic in its epistemological orientation and stresses the distribution of material power capabilities in i
- **出典クエリ：** 9.2

### ✗ #43（賛成・🔴 低（無関係の可能性））Where Is the Semantic System? A Critical Review and Meta-Analysis of 120 Functional Neuroimaging Studies（2009・引用 4138）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Where Is the Semantic System? A Critical Review and Meta-Analysis of 120 Functional Neuroimaging Studies
- **Crossref 著者：** Jeffrey R. Binder / Rutvik H. Desai / William W. Graves 他
- **Crossref 媒体：** Cerebral Cortex
- **DOI URL：** https://doi.org/10.1093/cercor/bhp055
- **OpenAlex 著者：** Jeffrey R. Binder / Rutvik H. Desai / William W. Graves
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://academic.oup.com/cercor/article-pdf/19/12/2767/17300551/bhp055.pdf
- **要旨：** Semantic memory refers to knowledge about people, objects, actions, relations, self, and culture acquired through experience. The neural systems that store and retrieve this inform
- **出典クエリ：** 9.3

### ✗ #44（反論・🔴 低（無関係の可能性））International regimes, transactions, and change: embedded liberalism in the postwar economic order（1982・引用 4403）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** International regimes, transactions, and change: embedded liberalism in the postwar economic order
- **Crossref 著者：** John Gerard Ruggie
- **Crossref 媒体：** International Organization
- **DOI URL：** https://doi.org/10.1017/s0020818300018993
- **OpenAlex 著者：** John Gerard Ruggie
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://www.cambridge.org/core/services/aop-cambridge-core/content/view/238A600FEFE7EDBC2DDAB30E6A28B4D9/S0020818300018993a.pdf/div-class-title-international-regimes-transactions-and-change-embedded-liberalism-in-the-postwar-economic-order-div.pdf
- **要旨：** The prevailing model of international economic regimes is strictly positivistic in its epistemological orientation and stresses the distribution of material power capabilities in i
- **出典クエリ：** 9.4

### ✗ #45（反論・🔴 低（無関係の可能性））Heuristic Decision Making（2010・引用 3821）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Heuristic Decision Making
- **Crossref 著者：** Gerd Gigerenzer / Wolfgang Gaissmaier
- **Crossref 媒体：** Annual Review of Psychology
- **DOI URL：** https://doi.org/10.1146/annurev-psych-120709-145346
- **OpenAlex 著者：** Gerd Gigerenzer / Wolfgang Gaissmaier
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://pure.mpg.de/pubman/item/item_2099042_6/component/file_2099041/GG_Heuristic_2011.pdf
- **要旨：** As reflected in the amount of controversy, few areas in psychology have undergone such dramatic conceptual changes in the past decade as the emerging science of heuristics. Heurist
- **出典クエリ：** 9.4


---

## コア主張 #10 事業中心人事

### ✗ #46（賛成・🔴 低（無関係の可能性））Global Strategy for the Diagnosis, Management, and Prevention of Chronic Obstructive Pulmonary Disease（2012・引用 16081）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Global Strategy for the Diagnosis, Management, and Prevention of Chronic Obstructive Pulmonary Disease
- **Crossref 著者：** Jørgen Vestbo / Suzanne S. Hurd / Alvar G. Agustí 他
- **Crossref 媒体：** American Journal of Respiratory and Critical Care Medicine
- **DOI URL：** https://doi.org/10.1164/rccm.201204-0596pp
- **OpenAlex 著者：** Jørgen Vestbo / Suzanne S. Hurd / Àlvar Agustí
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** http://ajrccm.atsjournals.org/content/187/4/347.full.pdf+html
- **要旨：** Chronic obstructive pulmonary disease (COPD) is a global health problem, and since 2001, the Global Initiative for Chronic Obstructive Lung Disease (GOLD) has published its strateg
- **出典クエリ：** 10.3

### ✗ #47（賛成・🔴 低（無関係の可能性））Preferred reporting items for systematic review and meta-analysis protocols (PRISMA-P) 2015: elaboration and explanation（2015・引用 13046）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** Preferred reporting items for systematic review and meta-analysis protocols (PRISMA-P) 2015: elaboration and explanation
- **Crossref 著者：** L. Shamseer / D. Moher / M. Clarke 他
- **Crossref 媒体：** BMJ
- **DOI URL：** https://doi.org/10.1136/bmj.g7647
- **OpenAlex 著者：** Larissa Shamseer / David Moher / Mike Clarke
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://www.bmj.com/content/bmj/349/bmj.g7647.full.pdf
- **要旨：** Protocols of systematic reviews and meta-analyses allow for planning and documentation of review methods, act as a guard against arbitrary decision making during review conduct, en
- **出典クエリ：** 10.3

### ✗ #48（賛成・🔴 低（無関係の可能性））2016 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure（2016・引用 11450）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** 2016 ESC Guidelines for the diagnosis and treatment of acute and chronic heart failure
- **Crossref 著者：** Piotr Ponikowski / Adriaan A. Voors / Stefan D. Anker 他
- **Crossref 媒体：** European Heart Journal
- **DOI URL：** https://doi.org/10.1093/eurheartj/ehw128
- **OpenAlex 著者：** Piotr Ponikowski / Adriaan A. Voors / Stefan D. Anker
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://academic.oup.com/eurheartj/article-pdf/37/27/2129/23748755/ehw128.pdf
- **要旨：** No abstract available.
- **出典クエリ：** 10.3

### ✗ #49（反論・🔴 低（無関係の可能性））The clinician’s guide to prevention and treatment of osteoporosis（2022・引用 1286）
- **DOI 検証：** ✅ Crossref 一致
- **Crossref タイトル：** The clinician’s guide to prevention and treatment of osteoporosis
- **Crossref 著者：** M. S. LeBoff / S. L. Greenspan / K. L. Insogna 他
- **Crossref 媒体：** Osteoporosis International
- **DOI URL：** https://doi.org/10.1007/s00198-021-05900-y
- **OpenAlex 著者：** Meryl S. LeBoff / S. L. Greenspan / Karl Insogna
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://link.springer.com/content/pdf/10.1007/s00198-021-05900-y.pdf
- **要旨：** Osteoporosis is the most common metabolic bone disease in the USA and the world. It is a subclinical condition until complicated by fracture(s). These fractures place an enormous m
- **出典クエリ：** 10.4

### ✗ #50（反論・🔴 低（無関係の可能性））The Metric Tide: Report of the Independent Review of the Role of Metrics in Research Assessment and Management（2015・引用 730）
- **DOI 検証：** ❌ Crossref HTTP 404
- **OpenAlex 著者：** James Wilsdon / Liz Allen / Eleonora Belfiore
- **キーワード一致：** ゼロ（コア主張と無関係の可能性）
- **OA PDF：** https://kar.kent.ac.uk/81123/1/Metric_Tide_main_report.pdf
- **要旨：** This report presents the findings and recommendations of the Independent Review of the Role of Metrics in Research Assessment and Management. The review was chaired by Professor Ja
- **出典クエリ：** 10.4


---
