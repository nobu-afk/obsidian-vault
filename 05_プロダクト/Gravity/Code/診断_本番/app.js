/* ========================================
   Gravity CODE Diagnostic — App Logic
   v8: ストーリー形式 + 収束防止（トレードオフ・反射・本音フレーム）
   ======================================== */

const API_URL = 'generate.php';

// セクションIDの定数定義（QUESTIONSのsectionフィールドはこの定数を参照すること）
const SECTION = Object.freeze({
  SCENE0: 0,      // Part 1 — 事前情報（立場選択）
  SCENE1: 1,      // Scene 1 — 未知のプロジェクト
  SCENE2: 2,      // Scene 2 — 壁にぶつかる
  SCENE3: 3,      // Scene 3 — 終わりと次の始まり
  TRANSCRIPT: 4,  // Part 2 — ストーリー（コーチ記入）
});

const SECTIONS = [
  { id: 'scene0', label: 'Part 1 — 事前情報' },
  { id: 'scene1', label: 'Scene 1 — 未知のプロジェクト' },
  { id: 'scene2', label: 'Scene 2 — 壁にぶつかる' },
  { id: 'scene3', label: 'Scene 3 — 終わりと次の始まり' },
  { id: 'transcript', label: 'Part 2 — ストーリー（コーチ記入）' },
];

const SCENE_INTROS = {
  0: {
    title: 'Part 1 — 事前情報',
    body: 'より精度の高いレポートを生成するため、\n'
      + 'クライアントの立場を教えてください。',
  },
  1: {
    title: 'Scene 1 — 未知のプロジェクト',
    body: 'ある日、新しいプロジェクトに招かれた。\n'
      + 'メンバーは半分知らない人。テーマも専門外。\n'
      + 'でも、声をかけてくれた人の期待は感じている。',
  },
  2: {
    title: 'Scene 2 — 壁にぶつかる',
    body: '動き出して3週間。壁にぶつかった。\n'
      + 'スケジュールは遅れ、空気が重い。',
  },
  3: {
    title: 'Scene 3 — 終わりと次の始まり',
    body: 'プロジェクトは完了に近づいている。\n'
      + '作り上げたものを、次の人に渡す時が来た。',
  },
  4: {
    title: 'Part 2 — トランスクリプト',
    body: '',
    isNormal: true,
    extra: '<div style="text-align:left;max-width:720px;margin:24px auto 0;font-size:18px;line-height:2.6;color:#0f172a;background:#fff;padding:28px 32px;border-radius:12px;border:1px solid #e2e8f0;box-shadow:0 4px 6px -1px rgba(0,0,0,0.05);">'
      + '<strong>① 転機</strong>：キャリアの中で「自分が変わった」と感じる出来事は？<br>'
      + '<strong>② 没頭</strong>：人生で最も没頭した経験は？何にどうのめり込んだか<br>'
      + '<strong>③ 衝動</strong>：頼まれてないのに勝手にやってしまうことは？<br>'
      + '<strong>④ ギャップ</strong>：周りからどう見られている？自分の認識とのズレは？<br>'
      + '<strong>⑤ 消耗</strong>：仕事で最も消耗した時期は？何が削っていたか<br>'
      + '<strong>⑥ have to</strong>：本当はやりたくないのにやっていることは？なぜ続けている？<br>'
      + '<strong>⑦ 理想</strong>：5年後の理想の1日を肩書き抜きで。朝起きてから寝るまで</div>',
  },
};

const QUESTIONS = [
  // ============================
  // Part 1: 事前情報（Q0）— クライアントの立場
  // ============================

  // Q0: 立場（報告トーン調整用）
  {
    section: SECTION.SCENE0,
    text: 'クライアントの現在の立場に最も近いものを選んでください。\nこの情報をもとに、レポートの語り口を調整します。',
    type: 'choice',
    options: [
      { text: '経営者（CEO・創業者）', voice: '事業・戦略判断の文脈で才能を語る' },
      { text: '幹部（役員・部長クラス）', voice: '組織内での影響力拡大の文脈で語る' },
      { text: '管理職（課長・マネージャー）', voice: 'チーム運営の文脈で語る' },
      { text: '独立検討中・その他', voice: '市場での個人活動の文脈で語る' },
    ]
  },

  // ============================
  // Scene 1: 未知のプロジェクト（Q1-Q3）
  // ============================

  // Q1: インプット方法（反射フレーム）
  {
    section: SECTION.SCENE1,
    text: '参加初日。自己紹介が終わり、デスクに着いた。\n目の前には共有フォルダ、メンバーリスト、今期の計画書。\nまだ誰にも話しかけていない。最初に頭をよぎったのは？',
    type: 'choice',
    options: [
      { text: '「全体像が見えない」', voice: '構造を掴まないと動けない' },
      { text: '「この人たち、どんな人だろう」', voice: '空気を読みたい' },
      { text: '「何か手を動かしたい」', voice: 'じっとしているのが落ち着かない' },
      { text: '「ここまで何があったんだろう」', voice: '背景を知りたい' },
    ]
  },

  // Q2: 集団介入（反射フレーム）
  {
    section: SECTION.SCENE1,
    text: '2日目。キックオフ会議で、メンバー同士の意見がかみ合わない。\n同じ論点を行ったり来たりしている。\nあなたの中で最初にざわついたのは？',
    type: 'choice',
    options: [
      { text: '「論点がズレてる」', voice: '構造が気になる' },
      { text: '「あの人、何か言いたそう」', voice: '人が気になる' },
      { text: '「早く決めたい」', voice: '止まっている時間がもったいない' },
      { text: '「まだ判断できない」', voice: '情報が足りていない' },
    ]
  },

  // Q3: 権威対応（トレードオフ型）
  {
    section: SECTION.SCENE1,
    text: '会議後、リーダーが方針を決めた。\n自分の中では「それじゃないな」という感覚がある。\nただ、反論する根拠もまだ揃っていない。',
    type: 'choice',
    options: [
      { text: '根拠が揃うまで待つ', voice: '中途半端に言っても仕方ない' },
      { text: 'まずリーダーの意図を確認する', voice: '自分が見えていない何かがあるかもしれない' },
      { text: '根拠がなくても感覚を伝える', voice: '言わないまま進む方が怖い' },
      { text: '自分のパートで工夫する', voice: '全体は変えられなくても自分の範囲なら' },
    ]
  },

  // ============================
  // Scene 2: 壁にぶつかる（Q4-Q5）
  // ============================

  // Q4: 対人スタイル（トレードオフ型）
  {
    section: SECTION.SCENE2,
    text: 'メンバーが2人、同時に困っている。\n1人は黙り込んで明らかに元気がない。\nもう1人は「どうすればいいですか」と答えを求めてきている。\n最初に声をかけるのは？',
    type: 'choice',
    options: [
      { text: '黙り込んでいる方', voice: '放っておけない' },
      { text: '答えを求めている方', voice: '具体的に助けられるから' },
      { text: '2人を集めて一緒に話す', voice: '問題を共有した方がいい' },
      { text: '少し様子を見る', voice: '自分が入るタイミングじゃないかもしれない' },
    ]
  },

  // Q5: 動機の源泉（本音フレーム）
  {
    section: SECTION.SCENE2,
    text: 'チームは踏ん張って、壁を越えた。成果が出た。\n打ち上げで誰かが「今回、何が一番よかった？」と聞いた。\nあなたが思わず口にするのは？',
    type: 'choice',
    options: [
      { text: '「あの仕組みが回ったこと」', voice: '自分の設計が機能した実感' },
      { text: '「○○さんが化けたこと」', voice: 'あの人の成長が嬉しい' },
      { text: '「あの修羅場を一緒に越えたこと」', voice: 'この仲間と乗り越えた' },
      { text: '「誰もやったことないことをやったこと」', voice: '前例がなかった' },
    ]
  },

  // ============================
  // Scene 3: 終わりと次の始まり（Q6-Q7）
  // ============================

  // Q6: 手放し（反射フレーム）
  {
    section: SECTION.SCENE3,
    text: '引き継ぎの日。自分が設計し、調整し、育ててきたものを渡す。\n引き継ぎ相手は真面目そうだが、経験は浅い。\n資料を渡した瞬間、最初に感じたのは？',
    type: 'choice',
    options: [
      { text: '「次は何をやろう」', voice: 'もう頭が次に向いている' },
      { text: '「ここまで来たんだな」', voice: '少し感慨がある' },
      { text: '「大丈夫かな、この人」', voice: 'つい相手の力量が気になる' },
      { text: '「あそこの設計、ちゃんと伝わったかな」', voice: '品質が維持されるか心配' },
    ]
  },

  // Q7: have to（本音フレーム）
  {
    section: SECTION.SCENE3,
    text: 'すべてが終わった帰り道。ふと思う。\n「このプロジェクト、自分じゃなくてもよかったんじゃないか」\nその直後に浮かんだ感情は？',
    type: 'choice',
    options: [
      { text: '「…で、自分は本当は何がしたいんだろう」', voice: '自分の本音に向き合いたくなった' },
      { text: '「いや、やりきったからいい」', voice: '終わらせたこと自体に意味がある' },
      { text: '「もっと早く誰かに渡せばよかった」', voice: '抱え込みすぎた自覚がある' },
      { text: '「まあいいか、次いこう」', voice: '振り返るより前に進みたい' },
    ]
  },

  // ============================
  // Transcript（Q8）
  // ============================
  {
    section: SECTION.TRANSCRIPT,
    text: 'セッションの録音トランスクリプトを貼り付けてください。\nAIが7つの観点を自動抽出してレポートを生成します。',
    type: 'transcript',
    placeholder: 'Zoomの文字起こし、またはWhisperの出力テキストをここに貼り付けてください...',
    reportHint: '対話全体からの自動抽出',
  },
];

// ============================
// App State
// ============================
const App = {
  currentIndex: 0,
  answers: new Array(QUESTIONS.length).fill(null),
  isSubmitting: false,
  _showingSceneIntro: false,
  _autoAdvanceTimer: null,

  updateProgress() {
    const total = QUESTIONS.length;
    document.getElementById('progress-fill').style.width =
      ((this.currentIndex + 1) / total * 100) + '%';
    document.getElementById('progress-text').textContent =
      `${this.currentIndex + 1} / ${total}`;
  },

  // GA4 + Meta Pixel イベント送信ヘルパー
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
      const saved = sessionStorage.getItem('gravity-code-answers');
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
            sessionStorage.removeItem('gravity-code-answers');
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
      const saved = sessionStorage.getItem('gravity-code-answers');
      if (saved) {
        const data = JSON.parse(saved);
        if (data.answers && data.answers.length === QUESTIONS.length) {
          this.answers = data.answers;
          this.currentIndex = Math.min(data.currentIndex || 0, QUESTIONS.length - 1);
          resumed = true;
        } else {
          sessionStorage.removeItem('gravity-code-answers');
        }
      }
    } catch(e) {}
    this.showScreen('screen-quiz');
    if (!resumed) {
      this.showSceneIntro(0);
    } else {
      this.render();
    }
  },

  saveProgress() {
    try {
      sessionStorage.setItem('gravity-code-answers', JSON.stringify({
        answers: this.answers,
        currentIndex: this.currentIndex,
      }));
    } catch(e) {}
  },

  showSceneIntro(sectionIndex) {
    this._showingSceneIntro = true;
    const intro = SCENE_INTROS[sectionIndex];
    if (!intro) { this._showingSceneIntro = false; this.render(); return; }

    document.getElementById('section-label').textContent = intro.title;

    const qEl = document.getElementById('question-text');
    qEl.textContent = '';

    const container = document.getElementById('options-container');
    const bodyClass = intro.isNormal ? 'scene-intro-body normal' : 'scene-intro-body';
    container.innerHTML = '<div class="scene-intro">'
      + '<div class="' + bodyClass + '">'
      + intro.body.split('\n').map(line => line || '<br>').join('<br>')
      + '</div>'
      + (intro.extra || '')
      + '</div>';

    this.updateProgress();

    const btnNext = document.getElementById('btn-next');
    btnNext.disabled = false;
    btnNext.textContent = '続ける';
    btnNext.style.cssText = '';

    const btnBack = document.getElementById('btn-back');
    btnBack.disabled = (sectionIndex === 0 && this.currentIndex === 0);

    this.track('diagnosis_section', {
      section: intro.title,
      question_number: this.currentIndex + 1,
    });
  },

  render() {
    this._showingSceneIntro = false;
    const q = QUESTIONS[this.currentIndex];

    this.updateProgress();

    document.getElementById('section-label').textContent =
      SECTIONS[q.section].label;

    const qEl = document.getElementById('question-text');
    qEl.textContent = '';
    q.text.split('\n').forEach((line, i, arr) => {
      qEl.appendChild(document.createTextNode(line));
      if (i < arr.length - 1) qEl.appendChild(document.createElement('br'));
    });

    const container = document.getElementById('options-container');
    container.innerHTML = '';

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
      const intro = document.createElement('div');
      intro.style.cssText = 'background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:16px 20px;margin-bottom:16px;';
      intro.innerHTML = '<p style="font-size:13px;color:#475569;line-height:1.8;margin:0;">'
        + '<strong>AIが自動抽出する7つの観点：</strong><br>'
        + '① 自分が変わった転機　② 没頭した経験　③ 勝手にやっていたこと<br>'
        + '④ 周りからの評価とのズレ　⑤ 消耗した時期　⑥ やりたくないのにやっていること　⑦ 理想の1日'
        + '</p>';
      container.appendChild(intro);
      const textarea = document.createElement('textarea');
      textarea.className = 'free-text-area';
      textarea.style.cssText = 'min-height:300px;';
      textarea.placeholder = q.placeholder || '';
      textarea.value = this.answers[this.currentIndex] || '';
      const counter = document.createElement('div');
      counter.style.cssText = 'font-size:12px;color:#94a3b8;text-align:right;margin-top:8px;';
      const updateCounter = (val) => {
        const len = (val || '').length;
        counter.textContent = len + '文字';
        counter.style.color = len < 100 ? '#dc2626' : '#94a3b8';
      };
      updateCounter(textarea.value);
      textarea.oninput = (e) => {
        this.answers[this.currentIndex] = e.target.value;
        updateCounter(e.target.value);
        this.updateNav();
        this.saveProgress();
      };
      container.appendChild(textarea);
      container.appendChild(counter);
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
        if (this.currentIndex < QUESTIONS.length - 1) {
          this.next();
        }
      }, 800);
    }
  },

  updateNav() {
    const btnBack = document.getElementById('btn-back');
    const btnNext = document.getElementById('btn-next');

    btnBack.disabled = this.currentIndex === 0 && !this._showingSceneIntro;

    const answered = this.answers[this.currentIndex] !== null &&
                     this.answers[this.currentIndex] !== '';
    const isLast = this.currentIndex === QUESTIONS.length - 1;

    btnNext.disabled = !answered;
    if (isLast) {
      btnNext.textContent = 'レポートを生成する';
      btnNext.style.cssText = answered ? 'background:#1e40af;padding:16px 40px;' : '';
    } else {
      btnNext.textContent = '次へ';
      btnNext.style.cssText = '';
    }
  },

  next() {
    if (this._showingSceneIntro) {
      this._showingSceneIntro = false;
      this.render();
      window.scrollTo(0, 0);
      return;
    }
    if (this.currentIndex < QUESTIONS.length - 1) {
      const prevSection = QUESTIONS[this.currentIndex].section;
      this.currentIndex++;
      const newSection = QUESTIONS[this.currentIndex].section;
      if (newSection !== prevSection) {
        this.showSceneIntro(newSection);
        window.scrollTo(0, 0);
        return;
      }
      this.render();
      window.scrollTo(0, 0);
    } else {
      this.submit();
    }
  },

  back() {
    if (this._showingSceneIntro) {
      this._showingSceneIntro = false;
      if (this.currentIndex > 0) {
        this.currentIndex--;
        this.render();
      } else {
        this.showScreen('screen-intro');
      }
      window.scrollTo(0, 0);
      return;
    }
    if (this.currentIndex > 0) {
      this.currentIndex--;
      this.render();
      window.scrollTo(0, 0);
    }
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
    const hasTranscript = transcriptText.trim().length > 100;

    if (!hasTranscript) {
      this.showScreen('screen-quiz');
      this.currentIndex = transcriptQ >= 0 ? transcriptQ : QUESTIONS.length - 1;
      this.render();
      this.showToast('トランスクリプトを貼り付けてください（100文字以上）');
      return;
    }

    this.track('diagnosis_submit', {
      choices_count: choices.length,
      has_transcript: hasTranscript,
    });

    this.isSubmitting = true;
    this.showScreen('screen-loading');
    this.animateLoading();

    const payload = { choices, freetext: [], transcript: transcriptText };

    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 150000);
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
      try { sessionStorage.removeItem('gravity-code-answers'); } catch(e) {}
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
    this.currentIndex = 0;
    this.answers = new Array(QUESTIONS.length).fill(null);
    try { sessionStorage.removeItem('gravity-code-answers'); } catch(e) {}
    this.showScreen('screen-intro');
  },

  retry() {
    this.currentIndex = 0;
    this.answers = new Array(QUESTIONS.length).fill(null);
    this.showScreen('screen-quiz');
    this.showSceneIntro(0);
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
