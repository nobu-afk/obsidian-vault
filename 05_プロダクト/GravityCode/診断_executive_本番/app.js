/* ========================================
   Gravity CODE — App Logic v5.2
   YOUR GRAVITY CODE: あなたの引力の暗号
   選択式5問 + セッション誘導画面 + トランスクリプト(5観点チェック)
   ======================================== */

const API_URL = 'generate.php';

const QUESTIONS = [
  // ============================
  // Q1: 立場（直接・4択・voice無）
  // ============================
  {
    text: 'あなたの現在の立場に最も近いものは？',
    subtext: 'レポートの語り口を、あなたの立場に合わせて調整します。',
    type: 'choice',
    category: 'position',
    options: [
      { text: '経営者（CEO・創業者・代表取締役）', voice: '' },
      { text: '幹部（役員・執行役員・部長クラス）', voice: '' },
      { text: '独立検討中・フリーランス', voice: '' },
      { text: 'その他', voice: '' },
    ]
  },

  // ============================
  // Q2: 才能の動き（260507 v5.3.4 改修・無意識性強化・verb-map 整合・4択・voice有）
  // ============================
  {
    text: '頼まれてもいないのに、\n気づけば自然にやり続けているのはどれ？',
    subtext: '才能とは、無意識でも体が動いてしまう動きのこと',
    type: 'choice',
    category: 'verb',
    options: [
      { text: '何もないところから構造を組み立てる', voice: 'カオスを秩序に変えるのが快感' },
      { text: '相手の本音を引き出して言語化する', voice: '未言語の中にある真実を翻訳したい' },
      { text: '誰も気づいていない違和感を察知する', voice: '気づかないでいることが気持ち悪い' },
      { text: '型を作って、誰でも回せる状態にする', voice: '自分がいなくても機能する仕組みが好き' },
    ]
  },

  // ============================
  // Q3: Why の許せなさ（v5.3.4 整合・260507 改修・4択・voice有）
  // ============================
  {
    text: 'あなたの事業の根っこにある "許せなさ" は何ですか？',
    subtext: '一番近いものを選んでください',
    type: 'choice',
    category: 'why-anger',
    options: [
      { text: '能力があるのに、組織で発揮できていない人を見ること', voice: '才能を解き放ちたい' },
      { text: '本音と建前を使い分けて、自分を偽っている人を見ること', voice: '本音を取り戻したい' },
      { text: '構造が間違っているのに、誰も指摘せずに進む組織を見ること', voice: '構造を立て直したい' },
      { text: '小さな成功で満足して、本当の可能性に蓋をしている人を見ること', voice: '可能性に火を点けたい' },
    ]
  },

  // ============================
  // Q4: 偏愛（譲れない好み + 絶対に選ばない嫌い・v5.3.4 整合・260507 改修・4択・voice有）
  // ============================
  {
    text: 'あなたの「譲れない好み」と「絶対に選ばない嫌い」、\n最も近いセットはどれ？',
    subtext: '好みと嫌いの組み合わせで選んでください',
    type: 'choice',
    category: 'passion',
    options: [
      { text: '【好】ゼロから構造を作る ／ 【嫌】決まった運用を回す', voice: '創造と保守のコントラスト' },
      { text: '【好】人の本音を引き出す ／ 【嫌】形式的な会話・型通りのやり取り', voice: '本音と建前のコントラスト' },
      { text: '【好】未知の領域に挑む ／ 【嫌】同じことの繰り返し', voice: '挑戦と反復のコントラスト' },
      { text: '【好】数字で構造を読み解く ／ 【嫌】感覚的・曖昧な判断', voice: '論理と感覚のコントラスト' },
    ]
  },

  // ============================
  // Q5: 言行ギャップ（対比・4段階・voice無）
  // ============================
  {
    text: '普段やっていることと、本当はやりたいことに、\nどれくらいギャップがありますか？',
    subtext: '',
    type: 'choice',
    category: 'gap',
    options: [
      { text: '完全一致：やっていることとやりたいことは、ほぼ同じ', voice: '' },
      { text: '微ズレ：一部ズレがあるが、方向はおおむね合っている', voice: '' },
      { text: '大ズレ：やっていることの半分以上が「本当はやりたくないこと」', voice: '' },
      { text: '別世界：やっていることと、やりたいことは、まったく別の世界にある', voice: '' },
    ]
  },

  // ============================
  // Transcript（Q6）— 5観点チェック + 貼付
  // ============================
  {
    text: '経営者セッション（60分）のトランスクリプトを貼り付けてください。',
    subtext: '以下5観点をカバーしたトランスクリプトであることを確認してから送信します。',
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
  coverageChecks: [false, false, false, false, false],
  isSubmitting: false,
  _autoAdvanceTimer: null,

  // 260507 v5.3.4 改修：STEP 1 痛み選択廃止に伴い setupPainScreen / proceedToBridge / painSelection を撤去。
  // ブリッジ画面（screen-bridge）が初期 active になり、ユーザーは「60 分の解剖を始める」ボタンで proceedToIntro へ進む

  proceedToIntro() {
    this.showScreen('screen-intro');
    window.scrollTo(0, 0);
  },

  updateProgress() {
    const total = QUESTIONS.length;
    document.getElementById('progress-fill').style.width =
      ((this.currentIndex + 1) / total * 100) + '%';
    document.getElementById('progress-text').textContent =
      `${this.currentIndex + 1} / ${total}`;
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
      const saved = sessionStorage.getItem('gravity-code-v52-answers');
      if (saved) {
        const data = JSON.parse(saved);
        const answered = data.answers.filter(a => a !== null).length;
        if (answered > 0) {
          const notice = document.createElement('p');
          notice.style.cssText = 'font-size:13px;color:#64748b;margin-top:16px;';
          notice.textContent = '前回の途中データがあります（' + answered + '/' + QUESTIONS.length + '問回答済み）。開始すると続きから再開します。';
          const resetBtn = document.createElement('button');
          resetBtn.textContent = '最初からやり直す';
          resetBtn.style.cssText = 'font-size:12px;color:#94a3b8;background:none;border:none;text-decoration:underline;cursor:pointer;margin-top:4px;display:block;';
          resetBtn.onclick = (e) => {
            e.stopPropagation();
            sessionStorage.removeItem('gravity-code-v52-answers');
            notice.remove();
            resetBtn.remove();
          };
          const startBtn = document.querySelector('.intro-container .btn-primary');
          startBtn.parentNode.insertBefore(notice, startBtn.nextSibling);
          startBtn.parentNode.insertBefore(resetBtn, notice.nextSibling);
        }
      }
    } catch(e) {}
  },

  start() {
    this.track('diagnosis_start');
    let resumed = false;
    try {
      const saved = sessionStorage.getItem('gravity-code-v52-answers');
      if (saved) {
        const data = JSON.parse(saved);
        if (data.answers && data.answers.length === QUESTIONS.length) {
          this.answers = data.answers;
          this.currentIndex = Math.min(data.currentIndex || 0, QUESTIONS.length - 1);
          this.coverageChecks = data.coverageChecks || [false, false, false, false, false];
          resumed = true;
        } else {
          sessionStorage.removeItem('gravity-code-v52-answers');
        }
      }
    } catch(e) {}
    this.showScreen('screen-quiz');
    this.render();
  },

  saveProgress() {
    try {
      sessionStorage.setItem('gravity-code-v52-answers', JSON.stringify({
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
        sectionLabel.textContent = 'STEP 4 — トランスクリプト';
      } else {
        sectionLabel.textContent = `STEP 1 — 選択式 ${this.currentIndex + 1} / 5`;
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
    } else if (q.type === 'transcript') {
      // 5観点リスト
      const observations = document.createElement('div');
      observations.style.cssText = 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:18px 22px;margin-bottom:20px;';
      observations.innerHTML = '<p style="font-size:13px;color:#0f172a;line-height:1.8;margin:0 0 10px;font-weight:700;">AI が対話から抽出する 5 つの観点：</p>'
        + '<ol style="font-size:12.5px;color:#475569;line-height:1.9;padding-left:22px;margin:0;">'
        + '<li><strong>Why</strong> ── 経営の根源にある衝動／許せないこと</li>'
        + '<li><strong>才能</strong> ── 自然にできてしまう動きと、それが発揮される場</li>'
        + '<li><strong>偏愛</strong> ── 譲れない好みと、絶対に選ばない嫌い</li>'
        + '<li><strong>矛盾と have to</strong> ── 本当はやりたくないのにやっていること／本音と行動のズレ</li>'
        + '<li><strong>時間軸と象徴エピソード</strong> ── いつから変わらないか／あなたを最も表すエピソード</li>'
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
        + '<p style="font-size:12.5px;color:#64748b;margin:0 0 14px;line-height:1.7;">上記のトランスクリプトが以下5観点を対話で含んでいるか、送信前に確認してください。全てチェック後に送信ボタンが有効化されます。</p>';
      container.appendChild(checkHeader);

      const checkLabels = [
        'Why ── 経営の根源にある衝動が対話に含まれている',
        '才能 ── 自然にできてしまう動きと発揮される場が対話に含まれている',
        '偏愛 ── 譲れない好みと絶対に選ばない嫌いが対話に含まれている',
        '矛盾と have to ── 本音と行動のズレが対話に含まれている',
        '時間軸と象徴エピソード ── 過去からの不変パターンが対話に含まれている',
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
        // 選択式5問目(index=4)の後はセッション誘導画面へ
        if (this.currentIndex === 4) {
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

    btnBack.disabled = this.currentIndex === 0;

    const q = QUESTIONS[this.currentIndex];
    let answered = false;

    if (q.type === 'choice') {
      answered = this.answers[this.currentIndex] !== null;
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
    } else if (this.currentIndex === 4) {
      btnNext.textContent = 'セッション誘導画面へ';
      btnNext.style.cssText = '';
    } else {
      btnNext.textContent = '次へ';
      btnNext.style.cssText = '';
    }
  },

  next() {
    // 選択式5問目の後はセッション誘導画面へ
    if (this.currentIndex === 4) {
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
    // 選択式5問の要約を生成
    const summaryList = document.getElementById('preview-summary-list');
    if (summaryList) {
      summaryList.innerHTML = '';
      const labels = ['立場', '才能の仮説', 'Why の許せなさ', '偏愛（好み × 嫌い）', '言行ギャップ'];
      for (let i = 0; i < 5; i++) {
        const q = QUESTIONS[i];
        const ansIdx = this.answers[i];
        if (ansIdx === null || ansIdx === undefined) continue;
        const opt = q.options[ansIdx];
        const li = document.createElement('li');
        li.style.cssText = 'padding:8px 0;border-bottom:1px solid #e2e8f0;font-size:14px;line-height:1.7;color:#334155;';
        li.innerHTML = '<strong style="color:#0f172a;display:inline-block;min-width:130px;">' + labels[i] + '：</strong>' + opt.text + (opt.voice ? ' <span style="color:#64748b;font-size:12.5px;">（' + opt.voice + '）</span>' : '');
        summaryList.appendChild(li);
      }
    }
    this.showScreen('screen-preview');
    window.scrollTo(0, 0);
  },

  showTranscriptInput() {
    // トランスクリプト入力画面へ
    this.currentIndex = QUESTIONS.length - 1;
    this.showScreen('screen-quiz');
    this.render();
    window.scrollTo(0, 0);
  },

  getChoiceAnswers() {
    const choices = [];
    QUESTIONS.forEach((q, i) => {
      if (q.type === 'choice' && this.answers[i] !== null) {
        const opt = q.options[this.answers[i]];
        choices.push({
          question: q.text,
          selected: opt.text + (opt.voice ? '（' + opt.voice + '）' : ''),
        });
      }
    });
    return choices;
  },

  async submit() {
    const choices = this.getChoiceAnswers();

    if (this.isSubmitting) return;

    const transcriptQ = QUESTIONS.findIndex(q => q.type === 'transcript');
    const transcriptText = transcriptQ >= 0 ? (this.answers[transcriptQ] || '') : '';
    const hasTranscript = transcriptText.trim().length >= 500;
    const allChecked = this.coverageChecks.every(c => c === true);

    if (!hasTranscript) {
      this.showToast('トランスクリプトを貼り付けてください（最低500文字）');
      return;
    }
    if (!allChecked) {
      this.showToast('5つの観点チェックをすべて完了してください');
      return;
    }

    this.track('diagnosis_submit', {
      choices_count: choices.length,
      has_transcript: hasTranscript,
      coverage_all_checked: allChecked,
    });

    this.isSubmitting = true;
    this.showScreen('screen-loading');
    this.animateLoading();

    const payload = { choices, freetext: [], transcript: transcriptText, pain_selection: this.painSelection };  // v6.0 260430: 外的痛み選択を含める

    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 300000);
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

      const data = await response.json();
      this.track('diagnosis_complete');
      this._reportUrl = data.report_url;
      this.isSubmitting = false;
      this.cancelDebouncedSave();
      try { sessionStorage.removeItem('gravity-code-v52-answers'); } catch(e) {}
      window.open(data.report_url, '_blank');
      this.showComplete();
    } catch (err) {
      this.isSubmitting = false;
      console.error('Generation failed:', err);
      this.track('diagnosis_error', { error: err.message });
      if (this._loadingInterval) clearInterval(this._loadingInterval);
      document.getElementById('error-message').textContent =
        `レポート生成に失敗しました: ${err.message}`;
      this.showScreen('screen-error');
    }
  },

  showComplete() {
    if (this._loadingInterval) clearInterval(this._loadingInterval);
    const url = this._reportUrl || 'generate.php?report=1';
    document.getElementById('report-container').innerHTML =
      '<div style="text-align:center;padding:80px 40px;">' +
      '<span class="badge" style="display:inline-block;font-size:11px;font-weight:700;letter-spacing:0.2em;color:#fff;background:#0f172a;padding:5px 20px;border-radius:100px;">GRAVITY CODE</span>' +
      '<h2 style="font-size:24px;font-weight:800;color:#0f172a;margin:24px 0 12px;">レポートが生成されました</h2>' +
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
    try { sessionStorage.removeItem('gravity-code-v52-answers'); } catch(e) {}
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
        if (sub) sub.textContent = 'もう少しお待ちください...レポートを仕上げています';
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
    document.getElementById(id).classList.add('active');
  },
};
