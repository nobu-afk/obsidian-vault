/* ========================================
   Gravity Scan — App Logic v6.1（260501 Scan リブート版・組織の引力タイプ診断）
   GRAVITY SCAN: 組織の引力タイプ診断・Pre-Shift 適合診断
   CODE結果＋採用ペイン主訴＋過去エピソード＋組織規模 → セッション誘導 → トランスクリプト 5 観点（引力 7 項目→ 5 トピック集約）チェック
   ======================================== */

const API_URL = 'generate.php';
const STORAGE_KEY = 'gravity-scan-v60-answers';

const QUESTIONS = [
  // ============================
  // Q1（index 0）: CODE結果（URL貼付 or 自由記入・v5.3 から維持）
  // ============================
  {
    text: 'Gravity CODE の結果をご入力ください',
    subtext: 'CODE結果URLを貼付すると6点（キャラ名・4型判定・Why・動詞・環境・引力の核）を自動取得します。CODE未受講の場合は概要を自由記入してください（Scan＋CODEセット申込推奨）。',
    type: 'code-result',
    category: 'code-result',
    placeholder: 'CODE結果URL（推奨）：https://growthfix.jp/gravity-code/executive/generate.php?report=...\n\nまたは、CODE結果の概要を自由記入：\n例）キャラ名「完成恐怖症の翻訳者」／4型判定：環境ズレ型／Why：才能解放／動詞:見抜く・翻訳する・手放す',
  },

  // ============================
  // Q2（index 1）: 採用と離脱の現場で起きていること（v6.0 新規）
  // ============================
  {
    text: '採用と離脱の現場で、いま何が起きていますか？',
    subtext: '主訴ペインに最も近いものを選んでください。経営者の言語マップ A-E カテゴリにマッピングし、組織の引力タイプ判定の素材として使用します。',
    type: 'choice',
    category: 'recruitment-pain',
    options: [
      { text: '採用エージェントに年 300 万以上払っているが、思うように決まらない', voice: 'A1 採用費用増' },
      { text: '最終面接まで進んだ候補者から辞退連絡が増えている', voice: 'A2 最終面接辞退' },
      { text: '優秀な幹部から、なぜか順番に辞めていく', voice: 'B1 優秀幹部離脱' },
      { text: '採用基準が社内（経営者・現場・HR）で 3 回以上揉めている', voice: 'A6 採用基準曖昧' },
      { text: 'ビジョンを語っても、幹部が翌日違うことを言い始める', voice: 'C5 言葉が届かない' },
      { text: '1on1・OKR・識学・人事制度・サーベイを入れたが採用力は変わらない', voice: 'D6 施策疲れ' },
    ]
  },

  // ============================
  // Q3（index 2）: 過去 2 年の採用・離脱の具体エピソード（v6.0 新規・自由記入）
  // ============================
  {
    text: '過去 2 年で「これは痛かった」採用・離脱・辞退のエピソードを 3 件、具体的に教えてください',
    subtext: 'エージェント費用・最終面接辞退・優秀な幹部の離脱・面接で口説けなかった事例など。具体名・金額・タイミング・頻度をできる限り記入してください（v6.1 引力 7 項目スコアリングの素材）。',
    type: 'free-text',
    category: 'recruitment-episodes',
    placeholder: '例：\n1. 2025年Q3、エージェントに 300 万払って採用したマネージャーが、3 ヶ月で辞めた。理由は「経営の方向性が見えなかった」。\n2. 2025年Q4、最終面接で 3 名連続辞退。経営者が口説いた言葉が候補者に響かなかった可能性。\n3. 2024年、創業期から支えてくれた CFO が突然退職。優秀な人ほど先に辞めていく構造への気づき。',
  },

  // ============================
  // Q4（index 3）: 組織規模＋幹部数（推奨マトリクス用）
  // ============================
  {
    text: 'あなたの組織の規模＋幹部数は？',
    subtext: '推奨サービス（Shift 80万 / Coaching+Shift 並行 / Coaching 単独）の判定マトリクスに使用します。',
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
  // Transcript（Q5・index 4）— 5観点チェック + 貼付（v6.1 引力 7 項目→ 5 トピック集約）
  // ============================
  {
    text: 'Scan 60分対面セッションのトランスクリプトを貼り付けてください。',
    subtext: '以下 5 観点（v6.1・引力 7 項目を 5 トピックに集約）をカバーしたトランスクリプトであることを確認してから送信します。',
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
      if (q.type === 'transcript') {
        sectionLabel.textContent = 'STEP 4 — トランスクリプト（5観点チェック）';
      } else if (q.type === 'code-result') {
        sectionLabel.textContent = 'STEP 1 — CODE結果の入力';
      } else if (q.category === 'recruitment-pain') {
        sectionLabel.textContent = 'STEP 2 — 採用ペイン主訴';
      } else if (q.category === 'recruitment-episodes') {
        sectionLabel.textContent = 'STEP 2 — 過去エピソード（v6.1 引力 7 項目スコアリングの素材）';
      } else if (q.category === 'org-size') {
        sectionLabel.textContent = 'STEP 3 — 組織規模＋幹部数';
      } else {
        sectionLabel.textContent = `STEP ${this.currentIndex + 1} / ${QUESTIONS.length}`;
      }
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
        + '<strong>v6.1 引力 7 項目スコアリングの素材：</strong>過去 2 年の採用・離脱・辞退の具体エピソードを 3 件以上記入することで、引力 7 項目（採用パイプライン／最終面接辞退率／優秀人材定着率／幹部発話量／エンゲージメント／離脱予兆／採用最大壁の自覚度）のスコアリング精度が大幅に上がります。具体名・金額・タイミング・頻度を可能な限り含めてください。'
        + '</p>';
      container.appendChild(note);

      requestAnimationFrame(() => textarea.focus());
    } else if (q.type === 'transcript') {
      // 5観点リスト（v6.1・引力 7 項目→ 5 トピック集約）
      const observations = document.createElement('div');
      observations.style.cssText = 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:18px 22px;margin-bottom:20px;';
      observations.innerHTML = '<p style="font-size:13px;color:#0f172a;line-height:1.8;margin:0 0 10px;font-weight:700;">AI が対話から抽出する 5 観点（v6.1・引力 7 項目を 5 トピックに集約）：</p>'
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
        + '<p style="font-size:12.5px;color:#64748b;margin:0 0 14px;line-height:1.7;">上記のトランスクリプトが以下 5 観点（v6.1・引力 7 項目を 5 トピックに集約）を対話で含んでいるか、送信前に確認してください。全てチェック後に送信ボタンが有効化されます。</p>';
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
        // Q4（org-size）の後はセッション誘導画面へ
        if (this.currentIndex === 3) {
          this.showSessionPreview();
        } else if (this.currentIndex < QUESTIONS.length - 1) {
          this.next();
        }
      }, 800);
    }
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
    } else if (q.type === 'code-result') {
      const v = (this.answers[this.currentIndex] || '').trim();
      const isUrl = /https?:\/\/[^\s]*growthfix[^\s]*\/gravity-code\//i.test(v);
      answered = isUrl || v.length >= 20;
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
    } else if (this.currentIndex === 3) {
      btnNext.textContent = 'セッション誘導画面へ';
      btnNext.style.cssText = '';
    } else {
      btnNext.textContent = '次へ';
      btnNext.style.cssText = '';
    }
  },

  next() {
    if (this.currentIndex === 3) {
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
    // CODE結果の表示
    const codeInput = (this.answers[0] || '').trim();
    const urlMatch = codeInput.match(/https?:\/\/[^\s]*growthfix[^\s]*\/gravity-code\/[^\s]*/i);
    const codeRefHtml = urlMatch
      ? '<a href="' + urlMatch[0] + '" target="_blank" rel="noopener" style="display:inline-block;background:#0f172a;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:700;font-size:13px;">CODE結果を別タブで開く ↗</a>'
      : '<p style="font-size:13px;color:#64748b;margin:0;">（CODE結果は申込時に記入したテキストを参照してください）</p>';

    // v6.0 採用ペイン情報の要約
    const recruitmentPain = QUESTIONS[1].options[this.answers[1]] ? QUESTIONS[1].options[this.answers[1]].text : '';
    const orgSize = QUESTIONS[3].options[this.answers[3]] ? QUESTIONS[3].options[this.answers[3]].text : '';
    const episodes = (this.answers[2] || '').trim();
    const episodeShort = episodes.length > 200 ? episodes.substring(0, 200) + '...' : episodes;

    const summaryList = document.getElementById('preview-summary-list');
    if (summaryList) {
      summaryList.innerHTML = '';
      const li1 = document.createElement('li');
      li1.style.cssText = 'padding:8px 0;border-bottom:1px solid #e2e8f0;font-size:14px;line-height:1.7;color:#334155;';
      li1.innerHTML = '<strong style="color:#0f172a;display:inline-block;min-width:150px;">採用ペイン主訴：</strong>' + recruitmentPain;
      summaryList.appendChild(li1);
      const li2 = document.createElement('li');
      li2.style.cssText = 'padding:8px 0;border-bottom:1px solid #e2e8f0;font-size:14px;line-height:1.7;color:#334155;';
      li2.innerHTML = '<strong style="color:#0f172a;display:inline-block;min-width:150px;">過去エピソード：</strong><span style="white-space:pre-wrap;">' + (episodeShort || '（未記入）') + '</span>';
      summaryList.appendChild(li2);
      const li3 = document.createElement('li');
      li3.style.cssText = 'padding:8px 0;font-size:14px;line-height:1.7;color:#334155;';
      li3.innerHTML = '<strong style="color:#0f172a;display:inline-block;min-width:150px;">組織規模＋幹部数：</strong>' + orgSize;
      summaryList.appendChild(li3);
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
    return {
      code_result: this.answers[0] || '',
      recruitment_pain: this.answers[1] !== null ? QUESTIONS[1].options[this.answers[1]].text : '',
      recruitment_episodes: this.answers[2] || '',
      org_size: this.answers[3] !== null ? QUESTIONS[3].options[this.answers[3]].text : '',
      transcript: this.answers[4] || '',
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
      coverage_all_checked: true,
      version: 'v6.1',
    });

    this.isSubmitting = true;
    this.showScreen('screen-loading');
    this.animateLoading();

    const payload = {
      preInfo: '【CODE結果】\n' + data.code_result + '\n\n【採用ペイン主訴】\n' + data.recruitment_pain + '\n\n【過去 2 年の採用・離脱エピソード】\n' + data.recruitment_episodes + '\n\n【組織規模＋幹部数】' + data.org_size,
      choices: [
        { question: '採用ペイン主訴', selected: data.recruitment_pain },
        { question: '組織規模＋幹部数', selected: data.org_size },
      ],
      freetext: [
        { question: '過去 2 年の採用・離脱エピソード', answer: data.recruitment_episodes, hint: 'v6.1 引力 7 項目スコアリングの素材 — 引力欠損ポイント特定に使用' },
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
      '<span class="badge" style="display:inline-block;font-size:11px;font-weight:700;letter-spacing:0.2em;color:#fff;background:#0f172a;padding:5px 20px;border-radius:100px;">GRAVITY SCAN v6.1</span>' +
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
