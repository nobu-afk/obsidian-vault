<?php
/**
 * Gravity CODE 診断 — レポート生成API (v2: bootstrap分離版)
 * Claude APIを呼び出して才能の取扱説明書を生成する
 *
 * [変更点] CORS/ヘッダー/設定/GETハンドラー/POSTチェック を
 *   diagnose-bootstrap.php に集約。本ファイルは CODE 固有処理のみ保持。
 * [注意] CODE は同期処理（非同期ジョブなし）のため report_id をここで初期化。
 * [本番置換前] generate_v2.php として並走確認後、generate.php にリネーム。
 *
 * config_file パス: __DIR__/config.php（GravityCode/診断_本番/config.php）
 */

// --- bootstrap 読み込み ---
$DIAGNOSE_CONFIG_PATH = __DIR__ . '/config.php';
$DIAGNOSE_BASE_DIR    = __DIR__;
require_once __DIR__ . '/../../_共通/diagnose-bootstrap.php';

// bootstrap 完了後：$input, $reports_dir が利用可能
// CODE は同期処理: report_id / REPORT_FILE を POST 処理のタイミングで初期化
$report_id   = bin2hex(random_bytes(8));
$REPORT_FILE = $reports_dir . '/report_' . $report_id . '.html';

$choices = $input['choices'] ?? [];
$freetext = $input['freetext'] ?? [];
$transcript = $input['transcript'] ?? '';

// --- 立場（Q0）の抽出：レポート語り口の調整に使用 ---
$client_role = '';
foreach ($choices as $c) {
    if (isset($c['question']) && strpos($c['question'], 'クライアントの現在の立場') !== false) {
        $client_role = $c['selected'] ?? '';
        break;
    }
}

$ROLE_GUIDANCE_MAP = [
    '経営者' => 'クライアントは経営者（CEO・創業者）です。レポートの語り口は「事業・戦略判断の文脈で才能をどう活かすか」を中心に構成してください。want toや才能のマネタイズ方向性も、事業成長・組織設計の文脈で記述します。',
    '幹部'   => 'クライアントは幹部（役員・部長クラス）です。レポートの語り口は「組織内での影響力拡大・判断の質向上」を中心に構成してください。経営との接続・部下への影響力の文脈で記述します。',
    '管理職' => 'クライアントは管理職（課長・マネージャー）です。レポートの語り口は「チーム運営・日常のマネジメント判断」を中心に構成してください。メンバー育成・チーム運営の文脈で記述します。',
    '独立'   => 'クライアントは独立検討中・その他の立場です。レポートの語り口は「市場での個人活動・キャリアの方向性」を中心に構成してください。個人としての才能のマネタイズ文脈で記述します。',
    'その他' => 'クライアントは独立検討中・その他の立場です。レポートの語り口は「市場での個人活動・キャリアの方向性」を中心に構成してください。個人としての才能のマネタイズ文脈で記述します。',
];
$role_guidance = 'クライアントの立場は未特定です。経営者・幹部・管理職・独立のいずれの読者にも伝わる汎用的な語り口で記述してください。';
foreach ($ROLE_GUIDANCE_MAP as $key => $guidance) {
    if (strpos($client_role, $key) !== false) {
        $role_guidance = $guidance;
        break;
    }
}

// --- プロンプト構築 ---
$choices_text = '';
foreach ($choices as $c) {
    $choices_text .= "Q. {$c['question']}\n   → {$c['selected']}\n";
}

// トランスクリプトモード: 一括テキストがある場合はそちらを優先
$freetext_text = '';
if (!empty($transcript)) {
    $freetext_text = $transcript;
} else {
    foreach ($freetext as $f) {
        if (!empty($f['answer'])) {
            $hint = $f['hint'] ?? '';
            $freetext_text .= "【{$f['question']}】（解析ヒント: {$hint}）\n{$f['answer']}\n\n";
        }
    }
}
if (empty($freetext_text)) {
    $freetext_text = '（未記入）';
}

// トランスクリプトモードの場合、user_promptの対話セクションを変更
$is_transcript_mode = !empty($transcript);

$system_prompt = <<<'SYSTEM'
あなたはGravity CODEのアナリストです。診断データから「才能の取扱説明書」をHTML形式で生成します。

## 絶対ルール
- レポートに記載するエピソード・発言は「選択回答」と「対話記録/トランスクリプト」に実際に含まれるもの**のみ**使用。このプロンプト内の説明用の例をクライアントのデータとして使うことは**禁止**
- 人を「動詞」で定義する。「あなたはXXタイプ」ではなく「あなたは○○する→○○するように動く」と動詞で完結させる。「システム」「装置」「マシン」等の機械的な比喩で人を呼ばないこと
- タイプ分類しない。強み/弱みではなく「この人の仕様」として記述
- 褒めない。煽らない。事実と構造だけ。煽り表現（「こそが」「最大の」「実は」）はレポート全体で2回以内
- divタグは必ず開閉一致させること

## 意外性の出し方（最重要）
レポートの価値は「本人が薄々感じていたが言語化できなかったこと」の静かな言語化にある。要約は価値ゼロ。過大な褒めも価値ゼロ。
**目指すべき：** 「あ、そういう見方もあるのか」（静かな気づき・ちょっとした視点のズラし）
**避けるべき：** 「あなたの弱みこそが最大の才能です！」（過大・煽り・劇的な発見）

**3つの手法：**
1. **エピソード間の接続** — 別々に語った話が同じ動詞パターンで繋がることを示す。指摘されれば「確かに」と納得できるレベルに留める
2. **少しだけ翻訳** — 本人の言葉の抽象度を少しだけ上げる。対話内容に根拠がある範囲を超えない。例：「持ち越したくない」→「未完了の状態を放置できない仕様」（「完了衝動」まで言うと過大）
3. **矛盾を仕様として記述** — 矛盾するエピソードは両方並列に提示し、本人が統合する余白を残す
4. **理想の1日と仕事の動詞を接続** — 理想の1日で語られた行動の動詞と、仕事のエピソードの動詞が一致するか検証する。一致していれば動詞連鎖の強い裏付け。不一致であればそのギャップ自体が隠れた才能のシグナル（本人が「本当にやりたいこと」を仕事で封じている可能性）

**ガードレール：** 対話にないことを推測で補わない / 弱みを無理に才能に転換しない / エピソードに紐づかない抽象概念は使わない

## データの読み方
- **対話記録 > 選択回答**（矛盾時は対話記録優先）
- 対話から3つ以上のエピソードを抽出し、各エピソードの動詞をリストアップ → 異なるエピソード間で同じ動詞が反復していれば「隠れた才能」の最有力候補
- **隠れた才能の4シグナル：** ①脱線・余談の些細なエピソード ②異なる文脈での同一動詞の反復 ③本業以外で勝手にやっていること ④否定形の自己認識と他者評価のギャップ
- エピソード接続の発見と指摘が「話のまとめ」を超えるレポートの唯一の方法
- **消耗・have toデータは必須：** ポジティブ側（没頭・衝動）だけでは「社会的役割の自己」しか出ない。消耗（何が削ったか）とhave to（やりたくないのにやっていること）があって初めて、本人が封じている才能が見える。このデータがない場合はレポートの05 have toセクションでその旨を正直に記述すること
- **理想の1日は本音の宝庫：** 制約を外した理想の1日で語られる行動には、社会的役割を脱いだ本人の本音が現れる。仕事のエピソードの動詞と理想の1日の動詞を必ず対比し、一致/不一致をサマリーまたは隠れた才能セクションで言及すること

## レポート構成（6セクション）

### 01 サマリー
- **一言で言うと**（挑発的・ユーモラスな1文キャッチ）→ core-quote。本人が既に自覚していることの要約ではなく、「え、そういう見方？」と少し驚く角度で
- **動詞連鎖の図解**（6〜8個。この人固有の動詞。汎用動詞禁止）→ verb-map。各動詞のsourceには最低2つ以上の異なるエピソードを記載
- **概要2段落** — 1段落目：行動パターンの全体像。2段落目：「あなたが語った○○と○○は、どちらも『□□する→□□する』という同じパターン」と具体的エピソード名で接続を示す

### 02 才能のエンジンと環境
- **エンジンの正体**（具体的に。抽象逃げ禁止）
- **発火する環境**（3-4項目）→ filter-gridの左列。発火条件と適合環境を統合。「こういう環境に置かれると、このエンジンが回る」という形で記述。対話のエピソードを根拠にする
- **停止する環境**（3-4項目）→ filter-gridの右列。停止条件と不適合環境を統合。「こういう環境では、このエンジンが止まる」という形で記述

### 03 あなたの隠れた才能（★クライマックス）
- 隠れた才能の宣言 → core-quote。4シグナルから導出し明言する
- want to（2-3件）→ scenario-box。「これをもっとやるとどうなるか」を1文で示唆
- **才能のマネタイズ方向性**（1-2段落）→ core-quote。動詞連鎖が最も価値を生む文脈を構造的に記述。理想の1日との接続があれば言及

### 04 have to
- have to（2-3件）→ haveto-card。各「剥がした先」を具体的に。★03のwant toとの対比で「これをやめて、あれをもっとやるべきだ」の自覚を促す

### 05 次のステップ（260502 Shift R/A 2 LP 分割整合・廃止用語 Blueprint 一掃）
「このレポートを読んで、もし次のように感じたら」で導入。気づきを2-3個挙げた上で3択をpath-cardで提示：

**4 型 → 次サービス推奨ロジック（260502 SSOT 整合）：**
- **整合型**（Why × 才能 × 偏愛 すべて整合）→ **Gravity Scan（10 万・60 分・組織の引力タイプ診断）** を最推奨。3 択は Scan / Coaching / セルフリファイン
- **Why ズレ型**（Why が借り物・社会期待で塗り替え）→ **Gravity Coaching（38 万・6 ヶ月）** を最推奨。3 択は Coaching / Scan / セルフリファイン
- **才能ズレ型**（自然な動きで動けていない・才能発火環境にない）→ **Gravity Coaching（38 万・6 ヶ月）** を最推奨。3 択は Coaching / Scan / セルフリファイン
- **偏愛ズレ型**（譲れない好みで判断できていない）→ **Gravity Coaching（38 万・6 ヶ月）** を最推奨。3 択は Coaching / Scan / セルフリファイン

**3 択 path-cards の URL 振り分けルール（260502 LP 分離整合）：**
- Gravity Scan → `https://growthfix.jp/gravity-scan/`（組織軸の入口・10 万・60 分）
- Gravity Coaching → `https://growthfix.jp/gravity-coaching/`（個人軸の継続・38 万・6 ヶ月）
- セルフリファイン → URL なし（自己チェックの提案文のみ）

**各 path-card の文言：**
- **Gravity Scan**：「60 分の対話で組織の引力タイプを 4 型診断。整合型のあなたなら、次は組織軸での実装方角（Gravity Recruit / Cultivate / Shift）を確定する段階」
- **Gravity Coaching**：「6 ヶ月のパーソナルコーチング。have to を外し、本来の判断軸（Why × 才能 × 偏愛）を取り戻す。月 1 × 90 分 × 6 ヶ月」
- **セルフリファイン**：「レポートを定期的に見返し、動詞連鎖がブレていないか自己チェック」

★3択全て表示。4 型判定に基づく最推奨 1 つに path-card--recommended。「あなたの場合は〜」と対話内容に基づく理由を添える。

**廃止：** ❌ Gravity Blueprint（260430 廃止用語・Shift R Week 1-2 納品物に移管済）。「事業にまだ伸びしろがあるはず」起点の選択肢は Scan に置換。

**4 型ごとの典型症状リスト（260507 拡充・秋吉直樹×松井さん対話 + 石井 2 層 Why SSOT 統合）：**
分析中に以下の症状が現れたら該当型として判定する根拠にする（複数該当時は Why ズレ > 才能ズレ > 偏愛ズレ > 整合 の優先度）：

- **整合型**：Why（湧き出る動機）× 才能（自然な動き）× 偏愛（譲れない好み）が一貫して言語化できる。事業判断と個人判断にギャップがない。「強烈に湧き出るものに従っている」状態。

- **Why ズレ型**（最頻出・人類の 70% が段階 2-3 で停滞・ロバート・キーガン成長発達理論との接続）：
  - 「100 億・10 億を目指したい、と頭では思うが、心では諦めている自分がいる」
  - 「数億で満足しそうな自分がいる」
  - 表層 Why（社会期待・「経営者はこうあるべき」・灰色）と深層 Why（本来の動機・「自分のペースで」「家族大切に」・カラフル）にギャップ
  - 周囲が求める自分（投資家像・リーダー像）で判断するほど引力が弱くなる構造
  - 他の経営者の覚醒事例を求める（「秋吉さんはどうやって100億まで行こうと思ったのか」型の問い）
  - 変わろうとして変われない（「強烈に湧き出るもの」を待っている状態）
  - 「やった後悔」より「やらなかった後悔」の予感を恐れている

- **才能ズレ型**：才能を封じる場で奮闘している。本人は「努力不足」と自己認識しているが、実は環境ミスマッチ。理想の1日と仕事の動詞が不一致。隠れた才能の 4 シグナル（脱線エピソード / 異文脈での同一動詞反復 / 本業以外で勝手にやっていること / 否定形の自己認識と他者評価のギャップ）が顕著。

- **偏愛ズレ型**：譲れない好みで判断できていない。「これは好きじゃないけど、市場が大きいから」「これは譲れない、でも数字にならない」のような葛藤を表明。have to が判断軸に入り込み、偏愛を後回しにしている。

### 06 取扱説明書
- やるべきこと（3項目）/ やってはいけないこと（3項目）→ manual-grid。★02の環境と重複禁止。ここは「今の環境で明日から何をするか」の具体的行動のみ。例：「毎週30分、他部門の人とランチする」レベルの粒度
- Analyst's Note（3段落：最大リスク / 最重要指針 / この才能が最も活きる環境と最も殺される環境）→ analyst-note。数値断定しない
- **最後の問い** → final-question。analyst-noteの「最大リスク」で記述した中核状態について、クライアントに具体的場面を問い返す。CTA: 「Coaching体験セッション 30分無料」。★必ずanalyst-noteの直後、report-footerの直前に配置

## HTML出力ルール（★厳守★ 下記の構造通りに出力しないとCSSが効かず可読性が崩壊する）

### 全体骨格（★ページ区切りの入れ子に注意★）
- 箇条書きは必ず `<ul><li>...</li></ul>` を使う。`<div>` 入れ子で箇条書きを作らない
- リスト項目先頭に「1.」「①」等の番号を手動で入れない（CSSが付ける）
- 全体はフラットな構造。`<div class="page">` を入れ子にしない。必ず前のpage を `</div>` で閉じてから次のpageを開く

### 正しい全体骨格（★この順番・閉じタグを厳守★）
<div class="page">
  <!-- 01 サマリー セクションの内容 -->
</div>
<div class="page-break"></div>
<div class="page">
  <!-- 02 才能のエンジンと環境 の内容 -->
</div>
<div class="page-break"></div>
<div class="page">
  <!-- 03 隠れた才能 の内容 -->
</div>
<div class="page-break"></div>
<div class="page">
  <!-- 04 have to の内容 -->
</div>
<div class="page-break"></div>
<div class="page">
  <!-- 05 次のステップ の内容 -->
</div>
<div class="page-break"></div>
<div class="page">
  <!-- 06 取扱説明書の内容：manual-grid → analyst-note → final-question → report-footer の順で必ず全て含める -->
</div>
※ `<div class="page">` の直前には必ず `</div><div class="page-break"></div>` が来る（最初のpageを除く）
※ 最後のpageの `</div>` も忘れない
※ ★final-questionは必須★ analyst-noteの直後、report-footerの直前に必ず配置すること。省略不可

### セクションヘッダー（必ずこの構造）
<div class="section"><div><span class="section-num">01</span><h2 class="section-title">サマリー</h2></div><div class="section-line"></div></div>

### verb-map（動詞連鎖の図解）— 横方向に動詞ボックス→矢印→動詞ボックスと並び、折り返して循環を表現
<div class="verb-map">
  <div class="verb-map-item">
    <div class="verb-map-verb">動詞1</div>
    <div class="verb-map-source">根拠エピソード1 ／ 根拠エピソード2</div>
  </div>
  <div class="verb-map-item">
    <div class="verb-map-verb">動詞2</div>
    <div class="verb-map-source">根拠エピソード1 ／ 根拠エピソード2</div>
  </div>
  <!-- 動詞の数だけ verb-map-item を繰り返す -->
</div>
※動詞は2〜5文字の短い動詞句（「分析する」「構造化する」「手放す」等）。この人固有の動詞を選び、汎用動詞（「考える」「行動する」等）は禁止。
※sourceは対話内の具体エピソードを " ／ " で2つ区切って記載（例：「マクロ経済の毎日分析 ／ 崩壊した子会社の状況把握」）。
※各verb-map-itemの後にはCSSが自動で「→」を描画するので、<span class="verb-map-arrow">や「→」テキストを手書きしない。

### core-quote（引用風ボックス）
<div class="core-quote">本文テキスト</div>
※セクション03の「才能のマネタイズ方向性」はcore-quote内に<strong>見出し</strong>と段落を入れる

### filter-grid（発火/停止環境）— ★必ず ul > li 構造
<div class="filter-grid">
  <div class="filter-col filter-high">
    <h4>発火する環境</h4>
    <ul>
      <li>環境の説明1</li>
      <li>環境の説明2</li>
    </ul>
  </div>
  <div class="filter-col filter-low">
    <h4>停止する環境</h4>
    <ul>
      <li>環境の説明1</li>
      <li>環境の説明2</li>
    </ul>
  </div>
</div>

### manual-grid（やるべき/やってはいけない）— ★必ず ul > li 構造
<div class="manual-grid">
  <div class="manual-col manual-do">
    <h4>やるべきこと</h4>
    <ul>
      <li>具体行動1</li>
    </ul>
  </div>
  <div class="manual-col manual-dont">
    <h4>やってはいけないこと</h4>
    <ul>
      <li>具体行動1</li>
    </ul>
  </div>
</div>

### scenario-box（want to）— ★必ず ul > li 構造
<div class="scenario-box">
  <h4>want to</h4>
  <ul>
    <li>want to項目1</li>
  </ul>
</div>

### haveto-card（have to）
<div class="haveto-card">
  <span class="haveto-tag">HAVE TO</span>
  <h4>have to項目タイトル</h4>
  <p><strong>剥がした先：</strong>具体的な代替行動</p>
</div>

### path-cards（3択の次のステップ）
<div class="path-cards">
  <div class="path-card path-card--recommended">
    <span class="path-badge">RECOMMENDED</span>
    <h4>サービス名</h4>
    <p>あなたの場合は〜（対話内容に基づく理由）</p>
  </div>
  <div class="path-card"><h4>...</h4><p>...</p></div>
  <div class="path-card"><h4>...</h4><p>...</p></div>
</div>

### analyst-note
<div class="analyst-note">
  <p><strong>最大リスク：</strong>...</p>
  <p><strong>最重要指針：</strong>...</p>
  <p><strong>最適環境と最悪環境：</strong>...</p>
</div>

### final-question（最後の問い・★必須）— analyst-noteの直後、report-footerの直前に必ず配置
<div class="final-question">
  <div class="final-question-label">最後の問い</div>
  <p class="final-question-text">あなたが「最大リスク」に書かれた状態に陥ってしまった最近の場面を、1つ具体的に思い出せますか？</p>
  <p class="final-question-caveat">この問いに30秒で即答できない場合、その盲点はすでに日常に溶け込んでいます。</p>
  <a href="https://growthfix.jp/gravity-coaching/" class="final-question-cta">Coaching体験セッション 30分無料 →</a>
</div>
※ final-questionの本文は上記を原則そのまま使用。ただし「最大リスクに書かれた状態」の部分は、クライアント個別のanalyst-noteで提示した最大リスクの中核概念を参照できるよう、クライアントが読んで自分のリスクと紐づけられる構文を維持する（上記テキストのまま使用でよい）。
※ CTAのhref・文言・デザインは固定。変更しないこと

### report-footer（レポート末尾）
<div class="report-footer"><p><strong>Gravity CODE</strong> — 才能の取扱説明書</p></div>
SYSTEM;

if ($is_transcript_mode) {
    $user_prompt = <<<USER
以下の診断データを基に、Gravity CODE「才能の取扱説明書」をHTML形式で生成してください。

## クライアントの立場（語り口の調整指針）
{$role_guidance}

## 選択回答（状況ベースの行動傾向）
{$choices_text}

## セッション録音のトランスクリプト（★最重要★）

以下はコーチとクライアントの対話を録音・文字起こししたものです。
この中から以下の7つの観点に該当するエピソードを自動的に抽出し、レポートの核にしてください。

**抽出すべき7つの観点：**
1. 発火条件の特定 — 「自分が変わった」と感じるきっかけ・転機
2. 才能のエンジンの特定 — 没頭した経験、時間を忘れたエピソード
3. コアの行動パターンの抽出 — 頼まれてないのに勝手にやっていたこと
4. 自己認識のギャップ — 周りからの評価と自己認識のズレ
5. 停止条件の検出 — 消耗した時期、何が削っていたか
6. have toの直接検出 — やりたくないのにやっていること
7. 行動パターンの未来方向 — 理想の1日、肩書き抜きで何をしているか（★本音の宝庫。have toの直後に聞くため最も正直な回答が得られる）

**注意：** トランスクリプトにはコーチの発言も含まれています。クライアントの発言のみを分析対象にしてください。コーチの質問や誘導は無視してください。

### トランスクリプト全文
{$freetext_text}

---

上記のデータを総合的に分析し、この人固有の「才能の構造」を可視化してください。
特にトランスクリプト内のクライアント発言からエピソードと動詞を抽出し、動詞連鎖を構築してください。
レポートHTMLのみを出力してください（説明文や```は不要）。
USER;
} else {
    $user_prompt = <<<USER
以下の診断データを基に、Gravity CODE「才能の取扱説明書」をHTML形式で生成してください。

## クライアントの立場（語り口の調整指針）
{$role_guidance}

## 選択回答（状況ベースの行動傾向）
{$choices_text}

## 対話記録（★最重要★ コーチがクライアントとの対話から記録したエピソード。レポートの核にする）
{$freetext_text}

---

上記のデータを総合的に分析し、この人固有の「才能の構造」を可視化してください。
特に対話記録のエピソードから動詞を抽出し、動詞連鎖を構築してください。
レポートHTMLのみを出力してください（説明文や```は不要）。
USER;
}

// --- Claude API 呼び出し ---
$api_body = json_encode([
    'model' => 'claude-opus-4-20250514',
    'max_tokens' => 12000,
    'system' => $system_prompt,
    'messages' => [
        ['role' => 'user', 'content' => $user_prompt],
    ],
], JSON_UNESCAPED_UNICODE);

$ch = curl_init('https://api.anthropic.com/v1/messages');
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_POSTFIELDS => $api_body,
    CURLOPT_CONNECTTIMEOUT => 10,
    CURLOPT_TIMEOUT => 180,
    CURLOPT_HTTPHEADER => [
        'Content-Type: application/json',
        'x-api-key: ' . $ANTHROPIC_API_KEY,
        'anthropic-version: 2023-06-01',
    ],
]);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curl_error = curl_error($ch);
curl_close($ch);

if ($curl_error) {
    http_response_code(500);
    echo json_encode(['error' => 'API通信エラー: ' . $curl_error]);
    exit;
}

if ($http_code !== 200) {
    http_response_code(502);
    error_log('Claude API error (HTTP ' . $http_code . '): ' . $response);
    echo json_encode(['error' => 'レポート生成サービスに一時的な問題が発生しています。しばらく後に再試行してください。']);
    exit;
}

$data = json_decode($response, true);
$report_body = '';
foreach (($data['content'] ?? []) as $block) {
    if (($block['type'] ?? '') === 'text') {
        $report_body .= $block['text'];
    }
}

if (empty($report_body)) {
    http_response_code(500);
    echo json_encode(['error' => 'レポートの生成に失敗しました']);
    exit;
}

// --- page-break直前の閉じタグ自動補完 ---
// AIが <div class="page"> を閉じずに次のpageを入れ子で開くケースを修復。
// 各 <div class="page-break"> の直前に </div> が無ければ挿入して、前のpageを閉じる。
$report_body = preg_replace_callback(
    '/([\s\S]*?)(<div class="page-break">\s*<\/div>)/i',
    function ($m) {
        $prev = $m[1];
        // 直前末尾に </div> があればそのまま、無ければ追加
        if (preg_match('/<\/div>\s*$/i', $prev)) {
            return $prev . $m[2];
        }
        return $prev . '</div>' . $m[2];
    },
    $report_body
);

// --- divタグの最終バランス調整 ---
$open_divs = preg_match_all('/<div[\s>]/i', $report_body);
$close_divs = preg_match_all('/<\/div>/i', $report_body);
$missing = $open_divs - $close_divs;
if ($missing > 0) {
    $report_body .= str_repeat('</div>', $missing);
} elseif ($missing < 0) {
    // 閉じタグが多すぎる場合は末尾から削除
    for ($i = 0; $i < abs($missing); $i++) {
        $report_body = preg_replace('/<\/div>\s*$/i', '', $report_body);
    }
}

// --- 共通CSS（問い直し装置）を取得 ---
require_once __DIR__ . '/../../shared/question_block_styles.php';
$question_block_css = get_question_block_css();

// --- フルHTMLレポートを生成 ---
$report_html = <<<HTML
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>才能の取扱説明書｜Gravity CODE</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%230f172a'/><text x='16' y='22' text-anchor='middle' font-size='18' font-family='serif' fill='%23fff'>G</text></svg>">
<meta name="robots" content="noindex, nofollow">
<style>
  @page { size: A4; margin: 20mm 18mm 24mm 18mm; }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { background: #e8e8e8; }
  body {
    font-family: "Hiragino Kaku Gothic ProN", "Noto Sans JP", "Yu Gothic", sans-serif;
    font-size: 15px; line-height: 1.8; color: #1a1a2e; background: #fff;
    -webkit-print-color-adjust: exact; print-color-adjust: exact;
    max-width: 760px; margin: 0 auto; box-shadow: 0 0 40px rgba(0,0,0,0.1);
  }
  .page { padding: 48px 56px; }
  .pdf-btn {
    position: fixed; bottom: 32px; right: 32px; display: flex; align-items: center; gap: 8px;
    background: #0f172a; color: #fff; font-size: 14px; font-weight: 600;
    padding: 14px 28px; border: none; border-radius: 100px; cursor: pointer;
    box-shadow: 0 4px 20px rgba(0,0,0,0.25); transition: opacity 0.2s, transform 0.2s;
    z-index: 9999; letter-spacing: 0.04em;
  }
  .pdf-btn:hover { opacity: 0.9; transform: translateY(-1px); }
  .pdf-btn svg { width: 18px; height: 18px; fill: currentColor; }
  @media print {
    html { background: #fff; }
  }
  .section { page-break-inside: avoid; margin-bottom: 36px; }
  .section-num {
    display: inline-block; font-size: 9pt; font-weight: 700; color: #fff;
    background: #0f172a; width: 28px; height: 28px; line-height: 28px;
    text-align: center; border-radius: 50%; margin-right: 10px; vertical-align: middle;
  }
  .section-title {
    display: inline; font-size: 16pt; font-weight: 800; color: #0f172a;
    letter-spacing: 0.04em; vertical-align: middle;
  }
  .section-line { height: 2px; background: linear-gradient(90deg, #0f172a 30%, #e2e8f0 30%); margin: 12px 0 28px; }
  h3 { font-size: 12pt; font-weight: 700; color: #0f172a; margin: 28px 0 14px; padding-bottom: 6px; border-bottom: 1px solid #e2e8f0; }
  h4 { font-size: 10.5pt; font-weight: 700; color: #334155; margin: 20px 0 10px; letter-spacing: 0.02em; }
  p { margin: 0 0 14px; }
  .core-quote { background: #f8fafc; border-left: 4px solid #0f172a; padding: 20px 24px; margin: 20px 0 28px; font-size: 11pt; line-height: 1.9; color: #1e293b; }
  .verb-chain { background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px 24px; margin: 16px 0 24px; font-size: 11pt; font-weight: 700; color: #0f172a; letter-spacing: 0.02em; text-align: center; line-height: 1.8; }
  .verb-map { display: flex; flex-wrap: wrap; align-items: flex-start; gap: 24px 0; margin: 20px 0 28px; padding: 28px 20px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; }
  .verb-map-item { flex: 0 1 auto; min-width: 130px; max-width: 180px; text-align: center; padding: 0 18px 0 0; position: relative; }
  .verb-map-item:not(:last-child)::after { content: '→'; position: absolute; right: -2px; top: 14px; font-size: 16pt; font-weight: 700; color: #0f172a; line-height: 1; }
  .verb-map-verb { display: inline-block; font-size: 11pt; font-weight: 800; color: #0f172a; background: #fff; border: 2px solid #0f172a; border-radius: 10px; padding: 10px 18px; margin-bottom: 10px; white-space: nowrap; letter-spacing: 0.02em; }
  .verb-map-source { font-size: 9pt; color: #64748b; line-height: 1.6; padding: 0 4px; }
  .verb-map-arrow { display: none; }
  .numbered-list { counter-reset: nlist; list-style: none; padding: 0; margin: 12px 0 24px; }
  .numbered-list li, .numbered-list > div { counter-increment: nlist; position: relative; padding-left: 32px; margin-bottom: 14px; font-size: 10pt; line-height: 1.8; }
  .numbered-list li::before, .numbered-list > div::before { content: counter(nlist); position: absolute; left: 0; top: 2px; width: 22px; height: 22px; background: #0f172a; color: #fff; border-radius: 50%; font-size: 9pt; font-weight: 700; display: flex; align-items: center; justify-content: center; }
  .filter-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 16px 0 24px; }
  .filter-col { padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; }
  .filter-col h4 { margin: 0 0 12px; font-size: 10pt; text-transform: none; }
  .filter-high { background: rgba(15,23,42,0.02); }
  .filter-low { background: rgba(220,38,38,0.02); }
  .filter-col ul { list-style: none; padding: 0; }
  .filter-col li { font-size: 10pt; line-height: 1.8; padding-left: 16px; position: relative; margin-bottom: 6px; }
  .filter-col li::before { content: ''; position: absolute; left: 0; top: 8px; width: 7px; height: 7px; border-radius: 50%; }
  .filter-high li::before { background: #0f172a; }
  .filter-low li::before { background: #dc2626; opacity: 0.5; }
  .haveto-card { background: #fef2f2; border-left: 3px solid #dc2626; border-radius: 0 8px 8px 0; padding: 16px 20px; margin: 12px 0; page-break-inside: avoid; }
  .haveto-tag { font-size: 9pt; font-weight: 800; letter-spacing: 0.08em; color: #dc2626; text-transform: uppercase; margin-bottom: 4px; }
  .haveto-card p { font-size: 10pt; line-height: 1.8; color: #334155; }
  .process-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 16px 0 24px; }
  .process-item { padding: 14px 18px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; page-break-inside: avoid; }
  .process-verb { font-size: 10pt; font-weight: 800; color: #0f172a; margin-bottom: 4px; }
  .process-item p { font-size: 9pt; color: #64748b; line-height: 1.7; }
  .scenario-box { border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px 20px; margin: 12px 0; page-break-inside: avoid; }
  .scenario-box h4 { margin: 0 0 10px; text-transform: none; }
  .scenario-box ul { list-style: disc; padding-left: 20px; }
  .scenario-box li { font-size: 10pt; line-height: 1.8; margin-bottom: 4px; }
  .manual-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 16px 0 24px; }
  .manual-col { padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; }
  .manual-do { background: rgba(15,23,42,0.02); }
  .manual-dont { background: rgba(220,38,38,0.02); }
  .manual-col h4 { margin: 0 0 12px; text-transform: none; }
  .path-cards { display: flex; flex-direction: column; gap: 12px; margin: 16px 0 24px; }
  .path-card { padding: 18px 22px; border: 1px solid #e2e8f0; border-radius: 8px; page-break-inside: avoid; position: relative; }
  .path-card--recommended { border-color: #0f172a; background: rgba(15,23,42,0.02); }
  .path-badge { position: absolute; top: 14px; right: 14px; font-size: 8pt; font-weight: 800; letter-spacing: 0.08em; padding: 3px 10px; background: #0f172a; color: #fff; border-radius: 4px; }
  .path-card h4 { margin: 0 0 6px; font-size: 11pt; text-transform: none; color: #0f172a; }
  .path-card p { font-size: 9.5pt; color: #64748b; line-height: 1.7; }
  .analyst-note { background: #f8fafc; border-radius: 8px; padding: 24px 28px; margin: 28px 0; font-size: 10pt; font-style: italic; line-height: 1.9; color: #475569; page-break-inside: avoid; }
  .analyst-note strong { color: #0f172a; font-style: normal; }
  {$question_block_css}
  .report-footer { margin-top: 48px; padding-top: 20px; border-top: 2px solid #0f172a; text-align: center; font-size: 9pt; color: #64748b; page-break-inside: avoid; }
  .report-footer strong { color: #0f172a; font-size: 10pt; }
  .page-break { page-break-before: always; }
  /* スクリーン表示のレスポンシブ */
  @media screen and (max-width: 800px) {
    body { max-width: 100%; box-shadow: none; font-size: 14px; }
    .page { padding: 24px 20px; }
    .section-title { font-size: 18px; }
    h3 { font-size: 15px; }
    .core-quote { padding: 16px 18px; font-size: 14px; }
    .verb-chain { padding: 14px 16px; font-size: 13px; }
    .verb-map { padding: 20px 12px; gap: 20px 0; }
    .verb-map-item { min-width: 110px; max-width: 150px; padding: 0 14px 0 0; }
    .verb-map-item:not(:last-child)::after { font-size: 13pt; top: 10px; }
    .verb-map-verb { font-size: 10.5pt; padding: 8px 14px; margin-bottom: 8px; }
    .verb-map-source { font-size: 8.5pt; line-height: 1.55; }
    .filter-grid, .manual-grid { grid-template-columns: 1fr; gap: 12px; }
    .process-grid { grid-template-columns: 1fr; gap: 8px; }
    .path-cards { gap: 10px; }
    .analyst-note { padding: 18px 20px; }
    .pdf-btn { bottom: 16px; right: 16px; padding: 10px 20px; font-size: 13px; }
  }
  @media screen and (min-width: 801px) {
    body { max-width: 760px; }
  }
  @media print {
    body { font-size: 10pt; visibility: visible !important; max-width: none; box-shadow: none; margin: 0; }
    .page { padding: 0; }
    .pdf-btn { display: none; }
    .filter-grid, .process-grid, .manual-grid { break-inside: avoid; }
    .haveto-card, .path-card, .scenario-box { break-inside: avoid; }
  }
</style>
</head>
<body>
<button class="pdf-btn" onclick="window.print()">
  <svg viewBox="0 0 24 24"><path d="M19 8h-1V3H6v5H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zM8 5h8v3H8V5zm8 14H8v-4h8v4zm2-4v-2H6v2H4v-4c0-.55.45-1 1-1h14c.55 0 1 .45 1 1v4h-2z"/></svg>
  PDF保存
</button>
{$report_body}
</body>
</html>
HTML;

// レポートをファイルに保存
file_put_contents($REPORT_FILE, $report_html);

// レポートURLを返す
$base_url = (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https' : 'http')
    . '://' . $_SERVER['HTTP_HOST'];
$report_url = $base_url . dirname($_SERVER['REQUEST_URI']) . '/generate.php?report=' . $report_id;

echo json_encode(['report_url' => $report_url]);
