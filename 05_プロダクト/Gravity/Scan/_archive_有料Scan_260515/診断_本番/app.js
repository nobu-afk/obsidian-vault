/* ========================================
   Gravity Scan — App Logic v7.0（260508 UI 構造ブラッシュアップ版・レポート v1.5 整合）
   GRAVITY SCAN: 組織の引力タイプ診断・Pre-Shift 適合診断
   v7.0 改修：レポート v1.5 が要求する素材から逆算して 5 問 → 7 問に再設計
   - Q4 集まる軸の現状自己診断（◎/○/△/× 4 段階）── Block A type-matrix-box 直結
   - Q5 躍動軸の現状自己診断（◎/○/△/× 4 段階）── Block A type-matrix-box 直結
   - Q6 過去 2 年エピソード拡張（採用費 vs 昇給原資 倍率ヒント追加）── Block C Recruit 推奨理由
   ======================================== */

const API_URL = 'generate.php';
const STORAGE_KEY = 'gravity-scan-v70-answers';

const QUESTIONS = [
  // ============================
  // Q1（index 0）: CODE結果（URL貼付 or 自由記入・v5.3 から維持）
  // ============================
  {
    text: 'Gravity CODE の結果（任意・受講済みの方のみ）',
    subtext: '【任意】Gravity CODE（経営者個人の引力タイプ診断・5 万円）を受講済みの場合のみ、結果を入力してください。CODE 結果がある場合は Block A の「個人引力 × 組織引力ギャップ図」を追加生成します。CODE 未受講の方は空欄のまま「次へ」ボタンを押してください（SCAN は単独でも組織の引力タイプ判定として完結します）。',
    type: 'code-result',
    category: 'code-result',
    placeholder: '【CODE 未受講の方は空欄のまま「次へ」ボタンを押してください】\n\n受講済みの場合：\nCODE結果URL（推奨）：https://growthfix.jp/gravity-code/executive/generate.php?report=...\n\nまたは、CODE結果の概要を自由記入：\n・キャラ名：[ あなたの引力キャラ名 ]\n・4型判定：[ 整合 / Why ズレ / 才能ズレ / 偏愛ズレ ]\n・Why：[ あなたの根源的動機 ]\n・才能：[ 自然にできてしまう動詞 ＋ 発火する環境 ]\n・偏愛：[ 譲れない好み ＋ 絶対に選ばない嫌い ]',
  },

  // ============================
  // Q2（index 1）: 組織規模＋幹部数（v7.0 順序前倒し・マトリクス前提情報）
  // ============================
  {
    text: 'あなたの組織の規模＋幹部数は？',
    subtext: 'Pre-Shift 適合診断（Recruit/Cultivate/Shift）の判定マトリクスに使用します。',
    type: 'choice',
    category: 'org-size',
    options: [
      { text: '5名以下（自分含む）／幹部なし', voice: '5以下・幹部0' },
      { text: '6〜10名／幹部 1-2 名', voice: '10以下・幹部少' },
      { text: '11〜30名／幹部 2-3 名', voice: '30以下・幹部中' },
      { text: '31名以上／幹部 3 名以上', voice: '31超・幹部多' },
    ]
  },

  // ============================
  // Q3（index 2）: 採用ペイン主訴（v7.2：複数選択可能化・最大 3 つ）
  // ============================
  {
    text: '採用と離脱の現場で、いま何が起きていますか？',
    subtext: '該当するものを選択してください（複数選択可・最大 3 つ）。当てはまるものがない場合は「上記のいずれにも該当しない」を選択し、セッション中に主訴を深掘りします。',
    type: 'multi-choice',
    category: 'recruitment-pain',
    maxSelect: 3,
    options: [
      { text: '採用エージェントに年 300 万以上払っているが、思うように決まらない', voice: 'A1 採用費用増' },
      { text: '最終面接まで進んだ候補者から辞退連絡が増えている', voice: 'A2 最終面接辞退' },
      { text: '優秀な幹部から、なぜか順番に辞めていく', voice: 'B1 優秀幹部離脱' },
      { text: '採用基準が社内（経営者・現場・HR）で 3 回以上揉めている', voice: 'A6 採用基準曖昧' },
      { text: 'ビジョンを語っても、幹部が翌日違うことを言い始める', voice: 'C5 言葉が届かない' },
      { text: '1on1・OKR・識学・人事制度・サーベイを入れたが採用力は変わらない', voice: 'D6 施策疲れ' },
      { text: '上記のいずれにも該当しない／別の主訴がある', voice: 'Z 該当なし', exclusive: true },
    ]
  },

  // ============================
  // Q4（index 3）: ★ NEW v7.0 ── 集まる軸の現状自己診断
  // 引力 7 項目のうち「採用パイプライン・最終面接辞退率・採用最大壁の自覚度」を統合
  // レポート Block A の type-matrix-box（集まる軸 ◎/△ 判定）の事前材料
  // ============================
  {
    text: '【集まる軸】採用パイプラインの現状を自己診断すると？',
    subtext: '採用パイプライン（応募数・通過率・最終辞退率）と「私が面接に出続ければ採用は機能する」自覚度を含めた 4 段階自己診断。レポートの集まる軸（◎/○/△/×）判定に直結します。',
    type: 'choice',
    category: 'attract-axis',
    options: [
      { text: '◎ 機能している ── 月次応募 10 件超・最終辞退ほぼゼロ・優秀層が継続的に集まる仕組みがある', voice: '集まる◎（整合的）' },
      { text: '○ 部分機能 ── 社長/HR 自身が面接に出続ければ採れる。但しスケールしない自覚あり', voice: '集まる○（社長依存）' },
      { text: '△ 詰まっている ── 応募数または最終辞退率が業界平均より悪い・エージェント費が高騰している', voice: '集まる△（採用詰まり）' },
      { text: '× 機能不全 ── 半年以上、採用したい役職で内定承諾ゼロ。応募が来ない or 来ても通らない', voice: '集まる×（崩壊）' },
    ]
  },

  // ============================
  // Q5（index 4）: ★ NEW v7.0 ── 躍動軸の現状自己診断
  // 引力 7 項目のうち「優秀人材定着率・幹部発話量・エンゲージメント・離脱予兆」を統合
  // レポート Block A の type-matrix-box（躍動軸 ◎/△ 判定）の事前材料
  // ============================
  {
    text: '【躍動軸】組織内部で優秀人材が躍動できているか自己診断すると？',
    subtext: '優秀人材定着率（過去 2 年）・幹部発話量（経営会議で幹部発議の有無）・エンゲージメント・離脱予兆の 4 項目を総合した 4 段階自己診断。レポートの躍動軸（◎/○/△/×）判定に直結します。',
    type: 'choice',
    category: 'thrive-axis',
    options: [
      { text: '◎ 躍動している ── 過去 2 年で優秀層の離脱ゼロ・経営会議で幹部が自律発議する・エンゲージメント上昇傾向', voice: '躍動◎（整合的）' },
      { text: '○ 部分的に躍動 ── 一部の幹部は自走しているが、社長が先回りすると幹部発話が止まる感覚あり', voice: '躍動○（部分機能）' },
      { text: '△ 躍動していない ── 過去 2 年で優秀層が 1-2 名離脱・経営会議は社長発議が大半・エンゲージメント横ばい', voice: '躍動△（停滞）' },
      { text: '× 躍動が立ち上がらない ── 1on1・OKR・識学・人事制度を全部入れたのに数値が動かない・離脱予兆が複数', voice: '躍動×（施策疲れ）' },
    ]
  },

  // ============================
  // Q6（index 5）: 過去 2 年エピソード ★ v7.0 拡張：採用費 vs 昇給原資ヒント追加
  // Block C の Recruit 推奨理由「採用費 / 昇給原資 倍率」材料 + 引力 7 項目スコアリング材料
  // ============================
  {
    text: '過去 2 年の採用・離脱エピソード 3 件と、年間採用費 vs 年間昇給原資の概算を教えてください',
    subtext: 'エピソードは具体名・金額・タイミング・頻度を含めて記入。採用費／昇給原資の倍率は Pre-Shift 適合診断（Recruit/Cultivate）の推奨理由として使用します（倍率 2 倍超で「悪循環」判定）。',
    type: 'free-text',
    category: 'recruitment-episodes',
    placeholder: '【エピソード 3 件】\n1. 2025年Q3、エージェントに 300 万払って採用したマネージャーが、3 ヶ月で辞めた。理由は「経営の方向性が見えなかった」。\n2. 2025年Q4、最終面接で 3 名連続辞退。経営者が口説いた言葉が候補者に響かなかった可能性。\n3. 2024年、創業期から支えてくれた CFO が突然退職。優秀な人ほど先に辞めていく構造への気づき。\n\n【採用コスト対効果（任意・推測値で OK）】\n- 年間採用費（エージェント費 + 求人広告 + 紹介報酬）：例）1,000 万円\n- 年間昇給原資（昇給率 × 平均年収 × 人数）：例）540 万円\n- 倍率：例）1.85 倍（悪循環閾値 2 倍に近接）',
  },

  // ============================
  // Q7（index 6）: トランスクリプト（v7.0：6 問の事前情報 + 60 分対話の文字起こし）
  // ============================
  {
    text: 'Scan 60 分対面セッションのトランスクリプトを貼り付けてください。',
    subtext: '事前情報 Q1-Q6（CODE 結果 + 組織規模 + 採用ペイン主訴 + 集まる軸自己診断 + 躍動軸自己診断 + エピソード 3 件 + 採用コスト対効果）と組み合わせて Block A/B/C を生成します。',
    type: 'transcript',
    category: 'transcript',
    placeholder: 'Zoomの文字起こし、またはWhisperの出力テキストをここに貼り付けてください...',
  },
];

// ============================
// App State
// ============================
const App = {
  currentIndex: 0,
  answers: new Array(QUESTIONS.length).fill(null),
  coverageChecks: [false, false, false, false, false],  // v6.0: 5 観点
  isSubmitting: false,
  _autoAdvanceTimer: null,

  updateProgress() {
    const total = QUESTIONS.length;
    const fill = document.getElementById('progress-fill');
    const text = document.getElementById('progress-text');
    if (fill) fill.style.width = ((this.currentIndex + 1) / total * 100) + '%';
    if (text) text.textContent = `${this.currentIndex + 1} / ${total}`;
  },

  track(eventName, params = {}) {
    if (typeof gtag === 'function') {
      gtag('event', eventName, params);
    }
    if (typeof fbq === 'function') {
      if (eventName === 'diagnosis_complete') fbq('track', 'Lead');
      if (eventName === 'diagnosis_start') fbq('track', 'ViewContent');
    }
  },

  init() {
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY);
      if (saved) {
        const data = JSON.parse(saved);
        const answered = (data.answers || []).filter(a => a !== null && a !== '').length;
        if (answered > 0) {
          const notice = document.createElement('p');
          notice.style.cssText = 'font-size:13px;color:#64748b;margin-top:16px;';
          notice.textContent = '前回の途中データがあります（' + answered + '/' + QUESTIONS.length + '問回答済み）。開始すると続きから再開します。';
          const resetBtn = document.createElement('button');
          resetBtn.textContent = '最初からやり直す';
          resetBtn.style.cssText = 'font-size:12px;color:#94a3b8;background:none;border:none;text-decoration:underline;cursor:pointer;margin-top:4px;display:block;';
          resetBtn.onclick = (e) => {
            e.stopPropagation();
            sessionStorage.removeItem(STORAGE_KEY);
            notice.remove();
            resetBtn.remove();
          };
          const startBtn = document.querySelector('.intro-container .btn-primary');
          if (startBtn) {
            startBtn.parentNode.insertBefore(notice, startBtn.nextSibling);
            startBtn.parentNode.insertBefore(resetBtn, notice.nextSibling);
          }
        }
      }
    } catch(e) {}
  },

  start() {
    this.track('diagnosis_start');
    let resumed = false;
    try {
      const saved = sessionStorage.getItem(STORAGE_KEY);
      if (saved) {
        const data = JSON.parse(saved);
        if (data.answers && data.answers.length === QUESTIONS.length) {
          this.answers = data.answers;
          this.currentIndex = Math.min(data.currentIndex || 0, QUESTIONS.length - 1);
          this.coverageChecks = data.coverageChecks || [false, false, false, false, false];
          // 旧 v5.3 形式の coverageChecks (3 elements) を v6.0 (5 elements) に変換
          if (this.coverageChecks.length !== 5) {
            this.coverageChecks = [false, false, false, false, false];
          }
          resumed = true;
        } else {
          sessionStorage.removeItem(STORAGE_KEY);
        }
      }
    } catch(e) {}
    this.showScreen('screen-quiz');
    this.render();
  },

  saveProgress() {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify({
        answers: this.answers,
        currentIndex: this.currentIndex,
        coverageChecks: this.coverageChecks,
      }));
    } catch(e) {}
  },

  // textarea入力用：500msデバウンスでJSON serialization回数を削減
  saveProgressDebounced() {
    if (this._saveTimer) clearTimeout(this._saveTimer);
    this._saveTimer = setTimeout(() => {
      this._saveTimer = null;
      this.saveProgress();
    }, 500);
  },

  cancelDebouncedSave() {
    if (this._saveTimer) {
      clearTimeout(this._saveTimer);
      this._saveTimer = null;
    }
  },

  render() {
    const q = QUESTIONS[this.currentIndex];

    this.updateProgress();

    const sectionLabel = document.getElementById('section-label');
    if (sectionLabel) {
      // v7.0 STEP 番号は質問順（1=CODE任意 / 2=組織規模 / 3=採用ペイン主訴 / 4=集まる軸 / 5=躍動軸 / 6=過去エピソード / 7=トランスクリプト）
      const stepNum = this.currentIndex + 1;
      const total = QUESTIONS.length;
      let label = '';
      if (q.type === 'code-result') {
        label = 'CODE 結果の入力（任意）';
      } else if (q.category === 'org-size') {
        label = '組織規模＋幹部数';
      } else if (q.category === 'recruitment-pain') {
        label = '採用ペイン主訴（複数選択可）';
      } else if (q.category === 'attract-axis') {
        label = '集まる軸 自己診断';
      } else if (q.category === 'thrive-axis') {
        label = '躍動軸 自己診断';
      } else if (q.category === 'recruitment-episodes') {
        label = '過去エピソード + 採用コスト対効果';
      } else if (q.type === 'transcript') {
        label = 'トランスクリプト（5 観点チェック）';
      } else {
        label = '';
      }
      sectionLabel.textContent = `STEP ${stepNum} / ${total} — ${label}`;
    }

    const qEl = document.getElementById('question-text');
    qEl.textContent = '';
    q.text.split('\n').forEach((line, i, arr) => {
      qEl.appendChild(document.createTextNode(line));
      if (i < arr.length - 1) qEl.appendChild(document.createElement('br'));
    });

    const container = document.getElementById('options-container');
    container.innerHTML = '';

    if (q.subtext) {
      const sub = document.createElement('p');
      sub.style.cssText = 'font-size:13px;color:#64748b;line-height:1.7;margin:0 0 16px;';
      sub.textContent = q.subtext;
      container.appendChild(sub);
    }

    if (q.type === 'choice') {
      q.options.forEach((opt, i) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn' + (this.answers[this.currentIndex] === i ? ' selected' : '');
        const mainText = document.createElement('span');
        mainText.className = 'option-main';
        mainText.textContent = opt.text;
        btn.appendChild(mainText);
        if (opt.voice) {
          const voiceText = document.createElement('span');
          voiceText.className = 'option-voice';
          voiceText.textContent = opt.voice;
          btn.appendChild(voiceText);
        }
        btn.onclick = () => this.selectOption(i);
        container.appendChild(btn);
      });
    } else if (q.type === 'multi-choice') {
      // v7.2（260508）：複数選択型（最大 maxSelect 個まで・チェックボックス風 UI）
      const currentSelected = Array.isArray(this.answers[this.currentIndex]) ? this.answers[this.currentIndex] : [];
      const maxSelect = q.maxSelect || 3;

      // 上部に選択数カウンター表示
      const counter = document.createElement('div');
      counter.style.cssText = 'font-size:13px;color:#0f172a;font-weight:700;margin-bottom:12px;padding:10px 14px;background:#f1f5f9;border-radius:6px;border:1px solid #e2e8f0;';
      counter.textContent = `${currentSelected.length} / ${maxSelect} 選択中（最低 1 つ・最大 ${maxSelect} つ）`;
      container.appendChild(counter);

      q.options.forEach((opt, i) => {
        const btn = document.createElement('button');
        const isSelected = currentSelected.includes(i);
        btn.className = 'option-btn' + (isSelected ? ' selected' : '');
        btn.style.cssText = 'display:flex;align-items:flex-start;gap:12px;text-align:left;';

        // チェックボックス風マーク
        const checkmark = document.createElement('span');
        checkmark.style.cssText = 'display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border:2px solid ' + (isSelected ? '#0f172a' : '#cbd5e1') + ';border-radius:4px;background:' + (isSelected ? '#0f172a' : '#fff') + ';color:#fff;font-weight:800;font-size:14px;flex-shrink:0;margin-top:2px;';
        if (isSelected) checkmark.textContent = '✓';
        btn.appendChild(checkmark);

        // テキスト部
        const textBox = document.createElement('span');
        textBox.style.cssText = 'flex:1;display:flex;flex-direction:column;gap:4px;';
        const mainText = document.createElement('span');
        mainText.className = 'option-main';
        mainText.textContent = opt.text;
        textBox.appendChild(mainText);
        if (opt.voice) {
          const voiceText = document.createElement('span');
          voiceText.className = 'option-voice';
          voiceText.textContent = opt.voice;
          textBox.appendChild(voiceText);
        }
        btn.appendChild(textBox);

        btn.onclick = () => this.toggleMultiOption(i, maxSelect);
        container.appendChild(btn);
      });
    } else if (q.type === 'code-result') {
      const textarea = document.createElement('textarea');
      textarea.className = 'free-text-area';
      textarea.id = 'code-result-textarea';
      textarea.style.cssText = 'min-height:160px;';
      textarea.placeholder = q.placeholder || '';
      textarea.value = this.answers[this.currentIndex] || '';
      const counter = document.createElement('div');
      counter.style.cssText = 'font-size:12px;color:#94a3b8;text-align:right;margin-top:6px;';
      const updateCounter = (val) => {
        const len = (val || '').length;
        counter.textContent = len + '文字';
        const isUrl = /https?:\/\/[^\s]*growthfix[^\s]*\/gravity-code\//i.test((val||'').trim());
        if (isUrl) {
          counter.textContent = '✓ CODE結果URL検出（自動パースされます）';
          counter.style.color = '#16a34a';
        } else {
          counter.style.color = len < 20 ? '#dc2626' : '#94a3b8';
        }
      };
      updateCounter(textarea.value);
      textarea.oninput = (e) => {
        this.answers[this.currentIndex] = e.target.value;
        updateCounter(e.target.value);
        this.updateNav();
        this.saveProgressDebounced();
      };
      container.appendChild(textarea);
      container.appendChild(counter);

      // CODE未受講者向けのセット申込み案内
      const setNote = document.createElement('div');
      setNote.style.cssText = 'background:#fef3c7;border:1px solid #f59e0b;border-radius:8px;padding:14px 18px;margin-top:18px;';
      setNote.innerHTML = '<p style="font-size:13px;color:#78350f;line-height:1.7;margin:0 0 8px;font-weight:700;">📌 CODE未受講の方へ</p>'
        + '<p style="font-size:12.5px;color:#78350f;line-height:1.7;margin:0;">'
        + 'Scanの効果は CODE 結果が前提です。<strong>CODE+Scan セット申込みで2万円OFF（13万円・税抜）</strong>。'
        + '<br>申込み後、CODE を先行実施 → Scan の流れになります。詳細は申込み確認時にご案内します。'
        + '</p>';
      container.appendChild(setNote);

      requestAnimationFrame(() => textarea.focus());
    } else if (q.type === 'free-text') {
      const textarea = document.createElement('textarea');
      textarea.className = 'free-text-area';
      textarea.id = 'episodes-textarea';
      textarea.style.cssText = 'min-height:240px;';
      textarea.placeholder = q.placeholder || '';
      textarea.value = this.answers[this.currentIndex] || '';
      const counter = document.createElement('div');
      counter.style.cssText = 'font-size:12px;color:#94a3b8;text-align:right;margin-top:6px;';
      const updateCounter = (val) => {
        const len = (val || '').length;
        counter.textContent = len + '文字';
        counter.style.color = len < 80 ? '#dc2626' : (len < 200 ? '#f59e0b' : '#16a34a');
      };
      updateCounter(textarea.value);
      textarea.oninput = (e) => {
        this.answers[this.currentIndex] = e.target.value;
        updateCounter(e.target.value);
        this.updateNav();
        this.saveProgressDebounced();
      };
      container.appendChild(textarea);
      container.appendChild(counter);

      const note = document.createElement('div');
      note.style.cssText = 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:14px 18px;margin-top:18px;';
      note.innerHTML = '<p style="font-size:12.5px;color:#475569;line-height:1.7;margin:0;">'
        + '<strong>v7.0 引力 7 項目スコアリングの素材：</strong>過去 2 年の採用・離脱・辞退の具体エピソードを 3 件以上記入することで、引力 7 項目（採用パイプライン／最終面接辞退率／優秀人材定着率／幹部発話量／エンゲージメント／離脱予兆／採用最大壁の自覚度）のスコアリング精度が大幅に上がります。具体名・金額・タイミング・頻度を可能な限り含めてください。'
        + '</p>';
      container.appendChild(note);

      requestAnimationFrame(() => textarea.focus());
    } else if (q.type === 'transcript') {
      // 5観点リスト（v7.0・引力 7 項目→ 5 トピック集約）
      const observations = document.createElement('div');
      observations.style.cssText = 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:18px 22px;margin-bottom:20px;';
      observations.innerHTML = '<p style="font-size:13px;color:#0f172a;line-height:1.8;margin:0 0 10px;font-weight:700;">AI が対話から抽出する 5 観点（v7.0・引力 7 項目を 5 トピックに集約）：</p>'
        + '<ol style="font-size:12.5px;color:#475569;line-height:1.9;padding-left:22px;margin:0;">'
        + '<li><strong>集まる軸の現状</strong> ── 採用パイプライン（応募数・面接通過率・最終辞退率・内定承諾率）＋採用最大壁の自覚度。具体数値とエピソードで深掘り</li>'
        + '<li><strong>躍動軸の現状</strong> ── 優秀人材定着率（過去 2 年）＋幹部発話量＋エンゲージメント＋離脱予兆。具体数値とエピソードで深掘り</li>'
        + '<li><strong>組織の引力タイプ確定（2 マトリクス判定）</strong> ── 集まる × 躍動 のスコアから 4 型（整合／拡散／渇望／不毛）のいずれかに確定</li>'
        + '<li><strong>引力欠損ポイントの特定</strong> ── 7 項目のうち最も低スコアの項目とその構造的原因</li>'
        + '<li><strong>Shift 適合診断＋経営者の覚悟確認</strong> ── 推奨 Shift パッケージ（R／A／Full／Orbit 直接／Coaching 先行）と 3 ヶ月着手の覚悟確信度</li>'
        + '</ol>';
      container.appendChild(observations);

      // トランスクリプト入力欄
      const textarea = document.createElement('textarea');
      textarea.className = 'free-text-area';
      textarea.id = 'transcript-textarea';
      textarea.style.cssText = 'min-height:260px;';
      textarea.placeholder = q.placeholder || '';
      textarea.value = this.answers[this.currentIndex] || '';
      const counter = document.createElement('div');
      counter.style.cssText = 'font-size:12px;color:#94a3b8;text-align:right;margin-top:6px;';
      const updateCounter = (val) => {
        const len = (val || '').length;
        counter.textContent = len + '文字';
        counter.style.color = len < 500 ? '#dc2626' : (len < 2000 ? '#f59e0b' : '#16a34a');
      };
      updateCounter(textarea.value);
      textarea.oninput = (e) => {
        this.answers[this.currentIndex] = e.target.value;
        updateCounter(e.target.value);
        this.updateNav();
        this.saveProgressDebounced();
      };
      container.appendChild(textarea);
      container.appendChild(counter);

      // 5観点カバレッジチェックボックス
      const checkHeader = document.createElement('div');
      checkHeader.style.cssText = 'margin-top:28px;padding-top:24px;border-top:1px solid #e2e8f0;';
      checkHeader.innerHTML = '<p style="font-size:14px;font-weight:700;color:#0f172a;margin:0 0 6px;">送信前チェック（コーチ承認）</p>'
        + '<p style="font-size:12.5px;color:#64748b;margin:0 0 14px;line-height:1.7;">上記のトランスクリプトが以下 5 観点（v7.0・引力 7 項目を 5 トピックに集約）を対話で含んでいるか、送信前に確認してください。全てチェック後に送信ボタンが有効化されます。</p>';
      container.appendChild(checkHeader);

      const checkLabels = [
        '集まる軸の現状 ── 採用パイプライン＋最終面接辞退率＋採用最大壁の自覚度を具体数値・エピソードで深掘りした',
        '躍動軸の現状 ── 優秀人材定着率＋幹部発話量＋エンゲージメント＋離脱予兆を具体数値・エピソードで深掘りした',
        '組織の引力タイプ確定 ── 集まる × 躍動 の 2 マトリクスにプロットし、4 型（整合／拡散／渇望／不毛）のいずれかに確定した',
        '引力欠損ポイントの特定 ── 7 項目のうち最低スコア項目とその構造的原因を 1 行で言語化した',
        'Shift 適合診断＋覚悟確認 ── 推奨 Shift パッケージ（R／A／Full／Orbit 直接／Coaching 先行）と経営者の覚悟確信度を確認した',
      ];
      checkLabels.forEach((label, i) => {
        const row = document.createElement('label');
        row.style.cssText = 'display:flex;align-items:flex-start;gap:10px;padding:12px 14px;margin-bottom:8px;background:#fff;border:1px solid #e2e8f0;border-radius:8px;cursor:pointer;transition:all 0.15s;';
        row.onmouseenter = () => row.style.background = '#f8fafc';
        row.onmouseleave = () => row.style.background = '#fff';
        const cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.checked = this.coverageChecks[i];
        cb.style.cssText = 'margin-top:4px;width:18px;height:18px;cursor:pointer;flex-shrink:0;accent-color:#0f172a;';
        cb.onchange = (e) => {
          this.coverageChecks[i] = e.target.checked;
          this.updateNav();
          this.saveProgress();
        };
        const text = document.createElement('span');
        text.style.cssText = 'font-size:13px;line-height:1.7;color:#334155;';
        text.textContent = label;
        row.appendChild(cb);
        row.appendChild(text);
        container.appendChild(row);
      });

      requestAnimationFrame(() => textarea.focus());
    }

    this.updateNav();
  },

  selectOption(index) {
    const wasAnswered = this.answers[this.currentIndex] !== null;
    this.answers[this.currentIndex] = index;
    this.saveProgress();
    const buttons = document.querySelectorAll('.option-btn');
    buttons.forEach((btn, i) => {
      btn.className = 'option-btn' + (i === index ? ' selected' : '');
    });
    this.updateNav();

    if (!wasAnswered) {
      if (this._autoAdvanceTimer) clearTimeout(this._autoAdvanceTimer);
      this._autoAdvanceTimer = setTimeout(() => {
        this._autoAdvanceTimer = null;
        // v7.0：next() 内で currentIndex === 5 の場合のみ showSessionPreview() を呼ぶよう統一済
        if (this.currentIndex < QUESTIONS.length - 1) {
          this.next();
        }
      }, 800);
    }
  },

  toggleMultiOption(index, maxSelect) {
    // v7.3（260508）：複数選択型のトグル。autoAdvance なし（手動「次へ」操作）+ exclusive 排他制御
    const q = QUESTIONS[this.currentIndex];
    const opts = q.options || [];
    const targetOpt = opts[index];
    const current = Array.isArray(this.answers[this.currentIndex]) ? [...this.answers[this.currentIndex]] : [];
    const idx = current.indexOf(index);

    if (idx >= 0) {
      // 選択中 → 解除
      current.splice(idx, 1);
    } else {
      // 未選択 → 追加
      if (targetOpt && targetOpt.exclusive) {
        // exclusive 選択肢（「該当なし」など）→ 他選択肢を全クリアしてこれだけ選択
        this.answers[this.currentIndex] = [index];
        this.saveProgress();
        this.render();
        return;
      }
      // 通常選択肢を選ぶ → exclusive 選択肢が含まれていたら強制解除
      const filtered = current.filter(i => !(opts[i] && opts[i].exclusive));
      if (filtered.length >= maxSelect) {
        this.showToast(`最大 ${maxSelect} つまでです`);
        return;
      }
      filtered.push(index);
      this.answers[this.currentIndex] = filtered;
      this.saveProgress();
      this.render();
      return;
    }
    this.answers[this.currentIndex] = current;
    this.saveProgress();
    this.render();
  },

  updateNav() {
    const btnBack = document.getElementById('btn-back');
    const btnNext = document.getElementById('btn-next');
    if (!btnBack || !btnNext) return;

    btnBack.disabled = this.currentIndex === 0;

    const q = QUESTIONS[this.currentIndex];
    let answered = false;

    if (q.type === 'choice') {
      answered = this.answers[this.currentIndex] !== null;
    } else if (q.type === 'multi-choice') {
      // v7.2（260508）：複数選択型・最低 1 つ選択で次へ進める
      const arr = this.answers[this.currentIndex];
      answered = Array.isArray(arr) && arr.length > 0;
    } else if (q.type === 'code-result') {
      // v7.1（260508）：CODE 受講は任意。未受講者は空欄のまま次へ進めます。入力時のみ URL or 20 文字以上で検証
      const v = (this.answers[this.currentIndex] || '').trim();
      const isUrl = /https?:\/\/[^\s]*growthfix[^\s]*\/gravity-code\//i.test(v);
      answered = v.length === 0 || isUrl || v.length >= 20;
    } else if (q.type === 'free-text') {
      const v = (this.answers[this.currentIndex] || '').trim();
      answered = v.length >= 80;
    } else if (q.type === 'transcript') {
      const transcriptFilled = (this.answers[this.currentIndex] || '').trim().length >= 500;
      const allChecked = this.coverageChecks.every(c => c === true);
      answered = transcriptFilled && allChecked;
    }

    const isLast = this.currentIndex === QUESTIONS.length - 1;

    btnNext.disabled = !answered;
    if (isLast) {
      btnNext.textContent = 'レポートを生成する';
      btnNext.style.cssText = answered ? 'background:#0f172a;padding:16px 40px;font-weight:800;' : '';
    } else if (this.currentIndex === 5) {
      btnNext.textContent = 'セッション誘導画面へ';
      btnNext.style.cssText = '';
    } else {
      btnNext.textContent = '次へ';
      btnNext.style.cssText = '';
    }
  },

  next() {
    if (this.currentIndex === 5) {
      this.showSessionPreview();
      return;
    }
    if (this.currentIndex < QUESTIONS.length - 1) {
      this.currentIndex++;
      this.render();
      window.scrollTo(0, 0);
    } else {
      this.submit();
    }
  },

  back() {
    if (this.currentIndex > 0) {
      this.currentIndex--;
      this.render();
      window.scrollTo(0, 0);
    }
  },

  showSessionPreview() {
    // v7.1：CODE 受講は任意。空欄なら未受講メッセージを表示
    const codeInput = (this.answers[0] || '').trim();
    const urlMatch = codeInput.match(/https?:\/\/[^\s]*growthfix[^\s]*\/gravity-code\/[^\s]*/i);
    let codeRefHtml;
    if (codeInput.length === 0) {
      codeRefHtml = '<p style="font-size:13px;color:#64748b;margin:0;line-height:1.7;">CODE 未受講の方として SCAN 単独で進行します。Block A は「個人引力 × 組織引力ギャップ図」を省略し、組織の引力タイプ判定（4 型）+ 引力 7 項目スコアリング + Pre-Shift 適合診断で完結します。</p>';
    } else if (urlMatch) {
      codeRefHtml = '<a href="' + urlMatch[0] + '" target="_blank" rel="noopener" style="display:inline-block;background:#0f172a;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:700;font-size:13px;">CODE結果を別タブで開く ↗</a>';
    } else {
      codeRefHtml = '<p style="font-size:13px;color:#64748b;margin:0;">（CODE結果は申込時に記入したテキストを参照してください）</p>';
    }

    // v7.2 採用ペイン情報の要約（multi-choice 配列対応）
    const orgSize = QUESTIONS[1].options[this.answers[1]] ? QUESTIONS[1].options[this.answers[1]].text : '';
    const painArr = Array.isArray(this.answers[2]) ? this.answers[2] : [];
    const recruitmentPain = painArr.length > 0
      ? painArr.map(idx => QUESTIONS[2].options[idx].text).join('<br>・ ')
      : '';
    const recruitmentPainHtml = recruitmentPain ? '・ ' + recruitmentPain : '';
    const attractAxis = QUESTIONS[3].options[this.answers[3]] ? QUESTIONS[3].options[this.answers[3]].text : '';
    const thriveAxis = QUESTIONS[4].options[this.answers[4]] ? QUESTIONS[4].options[this.answers[4]].text : '';
    const episodes = (this.answers[5] || '').trim();
    const episodeShort = episodes.length > 200 ? episodes.substring(0, 200) + '...' : episodes;

    const summaryList = document.getElementById('preview-summary-list');
    if (summaryList) {
      summaryList.innerHTML = '';
      const items = [
        { label: '組織規模＋幹部数', value: orgSize },
        { label: '採用ペイン主訴', value: recruitmentPainHtml || '（未選択）' },
        { label: '集まる軸 自己診断', value: attractAxis },
        { label: '躍動軸 自己診断', value: thriveAxis },
        { label: '過去エピソード', value: '<span style="white-space:pre-wrap;word-break:break-word;overflow-wrap:anywhere;">' + (episodeShort || '（未記入）') + '</span>' },
      ];
      items.forEach((item, idx) => {
        const li = document.createElement('li');
        const isLast = idx === items.length - 1;
        // v7.4（260508）：長文連続英数字でもボックス内で折り返すよう word-break/overflow-wrap を強制
        li.style.cssText = 'padding:8px 0;' + (isLast ? '' : 'border-bottom:1px solid #e2e8f0;') + 'font-size:14px;line-height:1.7;color:#334155;word-break:break-word;overflow-wrap:anywhere;';
        li.innerHTML = '<strong style="color:#0f172a;display:inline-block;min-width:150px;">' + item.label + '：</strong>' + item.value;
        summaryList.appendChild(li);
      });
    }

    const codeRefBox = document.getElementById('preview-code-ref');
    if (codeRefBox) codeRefBox.innerHTML = codeRefHtml;

    this.showScreen('screen-preview');
    window.scrollTo(0, 0);
  },

  showTranscriptInput() {
    this.currentIndex = QUESTIONS.length - 1;
    this.showScreen('screen-quiz');
    this.render();
    window.scrollTo(0, 0);
  },

  getStructuredAnswers() {
    // v7.0 インデックスマッピング：0=code, 1=org_size, 2=recruitment_pain（multi-choice配列）, 3=attract_axis, 4=thrive_axis, 5=recruitment_episodes, 6=transcript
    const painArr = Array.isArray(this.answers[2]) ? this.answers[2] : [];
    const recruitmentPainText = painArr.length > 0
      ? painArr.map(idx => '・' + QUESTIONS[2].options[idx].text).join('\n')
      : '';
    return {
      code_result: this.answers[0] || '',
      org_size: this.answers[1] !== null ? QUESTIONS[1].options[this.answers[1]].text : '',
      recruitment_pain: recruitmentPainText,
      recruitment_pain_count: painArr.length,
      attract_axis: this.answers[3] !== null ? QUESTIONS[3].options[this.answers[3]].text : '',
      thrive_axis: this.answers[4] !== null ? QUESTIONS[4].options[this.answers[4]].text : '',
      recruitment_episodes: this.answers[5] || '',
      transcript: this.answers[6] || '',
    };
  },

  async submit() {
    const data = this.getStructuredAnswers();

    if (this.isSubmitting) return;

    if ((data.transcript || '').trim().length < 500) {
      this.showToast('トランスクリプトを貼り付けてください（最低500文字）');
      return;
    }
    if (!this.coverageChecks.every(c => c === true)) {
      this.showToast('5 観点（引力 7 項目→ 5 トピック集約）チェックをすべて完了してください');
      return;
    }

    this.track('diagnosis_submit', {
      recruitment_pain: data.recruitment_pain,
      org_size: data.org_size,
      attract_axis: data.attract_axis,
      thrive_axis: data.thrive_axis,
      coverage_all_checked: true,
      version: 'v7.0',
    });

    this.isSubmitting = true;
    this.showScreen('screen-loading');
    this.animateLoading();

    const payload = {
      preInfo: '【CODE結果】\n' + data.code_result + '\n\n【組織規模＋幹部数】' + data.org_size + '\n\n【採用ペイン主訴】\n' + data.recruitment_pain + '\n\n【集まる軸 自己診断】\n' + data.attract_axis + '\n\n【躍動軸 自己診断】\n' + data.thrive_axis + '\n\n【過去 2 年の採用・離脱エピソード + 採用コスト対効果】\n' + data.recruitment_episodes,
      choices: [
        { question: '組織規模＋幹部数', selected: data.org_size },
        { question: '採用ペイン主訴', selected: data.recruitment_pain },
        { question: '集まる軸 自己診断（採用パイプライン・最終辞退率・自覚度の総合）', selected: data.attract_axis },
        { question: '躍動軸 自己診断（定着率・幹部発話・エンゲージメント・離脱予兆の総合）', selected: data.thrive_axis },
      ],
      freetext: [
        { question: '過去 2 年の採用・離脱エピソード + 採用コスト対効果', answer: data.recruitment_episodes, hint: 'v7.0 引力 7 項目スコアリング素材 + 採用費／昇給原資倍率（Block C Recruit/Cultivate 推奨理由）' },
      ],
      transcript: data.transcript,
    };

    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 600000);
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });
      clearTimeout(timeout);

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const job = await response.json();
      // ジョブベース：完了までポーリング
      this.pollJob(job.job_id, job.report_url);
    } catch (err) {
      this.isSubmitting = false;
      console.error('Generation failed:', err);
      this.track('diagnosis_error', { error: err.message });
      if (this._loadingInterval) clearInterval(this._loadingInterval);
      const errEl = document.getElementById('error-message');
      if (errEl) errEl.textContent = `レポート生成に失敗しました: ${err.message}`;
      this.showScreen('screen-error');
    }
  },

  async pollJob(jobId, reportUrl) {
    const start = Date.now();
    const maxWait = 600000; // 10min
    while (Date.now() - start < maxWait) {
      try {
        const r = await fetch(API_URL + '?job=' + encodeURIComponent(jobId));
        const s = await r.json();
        if (s.status === 'done') {
          this.track('diagnosis_complete');
          this._reportUrl = reportUrl;
          this.isSubmitting = false;
          this.cancelDebouncedSave();
          try { sessionStorage.removeItem(STORAGE_KEY); } catch(e) {}
          window.open(reportUrl, '_blank');
          this.showComplete();
          return;
        }
        if (s.status === 'error') {
          throw new Error(s.error || 'unknown error');
        }
      } catch (e) {
        // 一時的エラーはリトライ
      }
      await new Promise(res => setTimeout(res, 5000));
    }
    throw new Error('タイムアウトしました（10分超過）');
  },

  showComplete() {
    if (this._loadingInterval) clearInterval(this._loadingInterval);
    const url = this._reportUrl || 'generate.php?report=1';
    document.getElementById('report-container').innerHTML =
      '<div style="text-align:center;padding:80px 40px;">' +
      '<span class="badge" style="display:inline-block;font-size:11px;font-weight:700;letter-spacing:0.2em;color:#fff;background:#0f172a;padding:5px 20px;border-radius:100px;">GRAVITY SCAN v7.0</span>' +
      '<h2 style="font-size:24px;font-weight:800;color:#0f172a;margin:24px 0 12px;">Gravity Scan レポートが生成されました</h2>' +
      '<p style="font-size:15px;color:#64748b;margin-bottom:32px;">新しいタブでレポートが開いています。<br>表示されない場合は下のボタンをクリックしてください。</p>' +
      '<a href="' + url + '" target="_blank" style="display:inline-block;background:#0f172a;color:#fff;font-size:15px;font-weight:700;padding:16px 48px;border-radius:8px;text-decoration:none;letter-spacing:0.04em;">レポートを開く</a>' +
      '</div>';
    this.showScreen('screen-report');
  },

  clearAll() {
    if (!confirm('入力データをすべてクリアしますか？')) return;
    this.cancelDebouncedSave();
    this.currentIndex = 0;
    this.answers = new Array(QUESTIONS.length).fill(null);
    this.coverageChecks = [false, false, false, false, false];
    try { sessionStorage.removeItem(STORAGE_KEY); } catch(e) {}
    this.showScreen('screen-intro');
  },

  retry() {
    this.currentIndex = 0;
    this.answers = new Array(QUESTIONS.length).fill(null);
    this.coverageChecks = [false, false, false, false, false];
    this.showScreen('screen-quiz');
    this.render();
  },

  animateLoading() {
    const steps = document.querySelectorAll('.loading-step');
    steps.forEach(s => { s.className = 'loading-step'; });
    const sub = document.querySelector('.loading-sub');

    let i = 0;
    this._loadingInterval = setInterval(() => {
      if (i > 0 && i <= steps.length) steps[i - 1].classList.replace('active', 'done');
      if (i < steps.length) {
        steps[i].classList.add('active');
        i++;
      } else if (i === steps.length) {
        if (sub) sub.textContent = 'もう少しお待ちください...Gravity Scan レポートを仕上げています';
        i++;
      } else {
        clearInterval(this._loadingInterval);
      }
    }, 2500);
  },

  showToast(message) {
    let toast = document.getElementById('toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'toast';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.className = 'toast show';
    setTimeout(() => { toast.className = 'toast'; }, 4000);
  },

  showScreen(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const target = document.getElementById(id);
    if (target) target.classList.add('active');
  },
};

// ============================
// DOMContentLoaded
// ============================
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
