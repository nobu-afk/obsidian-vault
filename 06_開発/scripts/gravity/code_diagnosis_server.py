"""
Gravity CODE 診断 — ローカルAPIサーバー
診断結果を受け取り、Claude APIでレポートを生成する

使い方:
  cd ~/Documents/Obsidian\ Vault/07_開発/scripts/
  python3 code_diagnosis_server.py

サーバーが http://localhost:8000 で起動
診断ページから自動的にAPIが呼ばれる
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError

# --- 設定 ---
PORT = 8000
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

# APIキーがなければconfig_claude.jsonから読む
if not ANTHROPIC_API_KEY:
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config_claude.json')
    if os.path.exists(config_path):
        with open(config_path) as f:
            cfg = json.load(f)
            ANTHROPIC_API_KEY = cfg.get('api_key', '')

if not ANTHROPIC_API_KEY:
    print('エラー: ANTHROPIC_API_KEY が設定されていません')
    print('方法1: export ANTHROPIC_API_KEY="sk-ant-..."')
    print('方法2: config_claude.json に {"api_key": "sk-ant-..."} を作成')
    sys.exit(1)

# --- レポート生成プロンプト ---
SYSTEM_PROMPT = """あなたはGravity CODEのアナリストです。
診断回答データを基に「ソースコード解析レポート」をHTML形式で生成します。

## レポートの設計思想（最重要）
- 人を「肩書き」や「性格」ではなく「動詞」で定義する
- 「あなたはXXなタイプです」ではなく「あなたは○○する→○○する→○○するシステムである」と記述する
- 名詞（役職、肩書き）はドメインラベルに過ぎない。本質は動作原理（動詞の連鎖）
- 強み/弱みの二元論ではなく「このシステムの仕様」として記述する
- ストレングスファインダーのような「タイプ分類」は絶対にしない
- 褒めない。持ち上げない。事実を構造的に記述する

## データの優先度
1. **自由記述**が最も重要。ここに本人のエピソード・言葉が含まれている。レポートの骨格はここから構築する
2. **選択回答**は傾向の補助情報。自由記述と矛盾する場合は自由記述を優先
3. **タグプロファイル**は全体傾向の参考値

## 自由記述の読み方
各自由記述には「レポートのどこに効くか」のヒントが付いている。
- 「駆動源・エンジンの特定」→ 02 駆動源セクションの根拠にする
- 「コアの動詞連鎖の抽出」→ 01 サマリーの動詞連鎖を、この回答の中の動詞から抽出する
- 「発火条件の特定」→ 02 駆動源の発火条件に使う
- 「停止条件・have toの検出」→ 02 停止条件 + 03 have to検出に使う
- 「フィルター・自己認識のギャップ」→ 03 フィルターに使う
- 「have toの直接検出」→ 03 have to検出に使う
- 「動詞連鎖の未来方向の検証」→ 動詞連鎖が未来でも一貫しているか検証する材料

## レポート構成（5セクション＋取扱説明書）

### 01 サマリー
- コア定義文：「あなたとは、『○○し、○○し、○○する』[システム/エンジン/装置]である。」
- 動詞連鎖（6〜8個の動詞を→で接続）— 自由記述のエピソードから抽出した動詞を使う
- 2段落の概要説明

### 02 駆動源
- エンジンの正体（何が燃料か）— 自由記述の「没頭経験」「勝手にやっていたこと」から特定
- 発火条件（3つ）— 「転機」「没頭」のエピソードから条件を抽出
- 停止条件（3つ）— 「消耗した時期」のエピソードから条件を抽出

### 03 フィルター
- 適合度が高い環境（4項目）
- 適合度が低い環境（4項目）
- have toの検出（2〜3件）— 「やりたくないのにやっている」「周囲の評価とのズレ」から検出。それぞれ「剥がした先」を提示

### 04 実行パターン
- コアプロセス（動詞連鎖の各動詞を詳細に解説。自由記述のエピソードを具体例として引用する）
- 強みが最大化する場面（4項目）
- 精度が落ちる場面（4項目）

### 05 取扱説明書
- やるべきこと（5項目）
- やってはいけないこと（5項目）
- Analyst's Note（2段落。この人の最大のリスクと、最も重要な1つの指針を記述）

## HTML出力形式
以下のCSSクラスを使用してHTMLを生成してください。レポートHTMLのみを出力（<html>や<head>は不要、<div class="page">から開始）：

- セクションヘッダー: <div class="section"><div><span class="section-num">1</span><h2 class="section-title">タイトル</h2></div><div class="section-line"></div>
- 引用ボックス: <div class="core-quote"><strong>テキスト</strong></div>
- 動詞連鎖: <div class="verb-chain">動詞 → 動詞 → ...</div>
- 番号付きリスト: <ol class="numbered-list"><li><strong>見出し</strong> 説明</li></ol>
- フィルターグリッド: <div class="filter-grid"><div class="filter-col filter-high">...</div><div class="filter-col filter-low">...</div></div>
- have toカード: <div class="haveto-card"><div class="haveto-tag">検出 1</div><p>内容。<br><strong>剥がした先：</strong>○○</p></div>
- プロセスグリッド: <div class="process-grid"><div class="process-item"><div class="process-verb">動詞</div><p>説明</p></div></div>
- シナリオボックス: <div class="scenario-box"><h4>タイトル</h4><ul><li>内容</li></ul></div>
- マニュアルグリッド: <div class="manual-grid"><div class="manual-col manual-do"><h4>やるべきこと</h4><ol class="numbered-list">...</ol></div><div class="manual-col manual-dont"><h4>やってはいけないこと</h4><ol class="numbered-list">...</ol></div></div>
- アナリストノート: <div class="analyst-note"><strong>Analyst's Note：</strong>テキスト</div>
- フッター: <div class="report-footer"><p><strong>Gravity CODE｜GrowthFix</strong></p><p>あなたのソースコードを読み解く</p></div>
- ページ区切り: <div class="page-break"></div><div class="page">

## 重要な注意
- 自由記述の具体的なエピソードをレポート内で引用・参照すること（「あなたが語った○○の経験は〜」のように）
- 「弱み」ではなく「このシステムの仕様として出力が下がる条件」と記述する
- 動詞連鎖は本人のエピソードから抽出する。汎用的な動詞（「考える」「行動する」）ではなく、この人固有の動詞を使う
- have toの検出は断定ではなく「検出された可能性がある」というトーンで記述する"""

USER_PROMPT_TEMPLATE = """以下の診断データを基に、Gravity CODE ソースコード解析レポートをHTML形式で生成してください。

## 選択回答（状況ベースの行動傾向）
{choices_text}

## 対話記録（★最重要★ コーチがクライアントとの対話から記録したエピソード。レポートの核にする）
{freetext_text}

---

上記のデータを総合的に分析し、この人固有の「ソースコード」を解析してください。
特に対話記録のエピソードから動詞を抽出し、動詞連鎖を構築してください。
レポートHTMLのみを出力してください（説明文や```は不要）。"""


def build_prompt(payload):
    choices = payload.get('choices', [])
    freetext = payload.get('freetext', [])

    choices_text = '\n'.join(
        f'Q. {c["question"]}\n   → {c["selected"]}'
        for c in choices
    )

    freetext_text = '\n\n'.join(
        f'【{f["question"]}】（解析ヒント: {f.get("hint", "")}）\n{f["answer"]}'
        for f in freetext
        if f.get('answer')
    ) or '（未記入）'

    return USER_PROMPT_TEMPLATE.format(
        choices_text=choices_text,
        freetext_text=freetext_text,
    )


def call_claude(user_prompt):
    """Claude API を呼び出してレポートHTMLを生成"""
    url = 'https://api.anthropic.com/v1/messages'

    body = json.dumps({
        'model': 'claude-sonnet-4-20250514',
        'max_tokens': 8000,
        'system': SYSTEM_PROMPT,
        'messages': [
            {'role': 'user', 'content': user_prompt}
        ],
    }).encode('utf-8')

    req = Request(url, data=body, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('x-api-key', ANTHROPIC_API_KEY)
    req.add_header('anthropic-version', '2023-06-01')

    try:
        resp = urlopen(req, timeout=120)
    except Exception as e:
        try:
            error_body = e.read().decode('utf-8')
            print(f'API エラー詳細: {error_body}')
        except:
            print(f'APIエラー（詳細取得失敗）: {type(e).__name__}: {e}')
        raise

    data = json.loads(resp.read().decode('utf-8'))

    # テキストブロックを結合
    html = ''
    for block in data.get('content', []):
        if block.get('type') == 'text':
            html += block['text']

    return html


# --- レポートHTMLテンプレート（サンプルレポートと同じCSS） ---
REPORT_HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ソースコード解析レポート｜Gravity CODE</title>
<style>
  @page { size: A4; margin: 20mm 18mm 24mm 18mm; }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { background: #e8e8e8; }
  body {
    font-family: "Hiragino Kaku Gothic ProN", "Noto Sans JP", "Yu Gothic", sans-serif;
    font-size: 10.5pt; line-height: 1.8; color: #1a1a2e; background: #fff;
    -webkit-print-color-adjust: exact; print-color-adjust: exact;
    max-width: 210mm; margin: 0 auto; box-shadow: 0 0 40px rgba(0,0,0,0.1);
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
    body { max-width: none; box-shadow: none; margin: 0; }
    .page { padding: 0; }
    .pdf-btn { display: none; }
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
  .numbered-list { counter-reset: nlist; list-style: none; padding: 0; margin: 12px 0 24px; }
  .numbered-list li { counter-increment: nlist; position: relative; padding-left: 32px; margin-bottom: 14px; font-size: 10pt; line-height: 1.8; }
  .numbered-list li::before { content: counter(nlist); position: absolute; left: 0; top: 2px; width: 22px; height: 22px; background: #0f172a; color: #fff; border-radius: 50%; font-size: 9pt; font-weight: 700; display: flex; align-items: center; justify-content: center; }
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
  .report-footer { margin-top: 48px; padding-top: 20px; border-top: 2px solid #0f172a; text-align: center; font-size: 9pt; color: #64748b; page-break-inside: avoid; }
  .report-footer strong { color: #0f172a; font-size: 10pt; }
  .page-break { page-break-before: always; }
  @media print {
    body { font-size: 10pt; visibility: visible !important; }
    .filter-grid, .process-grid, .manual-grid { break-inside: avoid; }
    .haveto-card, .path-card, .scenario-box { break-inside: avoid; }
  }
</style>
</head>
<body style="visibility:hidden">
{{REPORT_BODY}}

<script>
window.addEventListener('load', function(){
  setTimeout(function(){
    document.body.style.visibility = 'visible';
    setTimeout(function(){
      window.print();
      window.close();
    }, 100);
  }, 300);
});
</script>
</body>
</html>'''

# 最後に生成されたレポートを保持
_last_report_html = None


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        global _last_report_html
        if self.path == '/report' and _last_report_html:
            response = _last_report_html.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(response)
        else:
            self.send_error(404)

    def do_POST(self):
        global _last_report_html

        if self.path != '/generate':
            self.send_error(404)
            return

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        payload = json.loads(body.decode('utf-8'))

        print(f'\n=== リクエスト受信 ===')
        scores = payload.get('scores', {})
        top3 = sorted(scores.items(), key=lambda x: -x[1])[:3]
        print(f'上位スコア: {", ".join(f"{k}={v}" for k,v in top3)}')

        try:
            user_prompt = build_prompt(payload)
            print('Claude API 呼び出し中...')
            report_body = call_claude(user_prompt)
            print(f'レポート生成完了（{len(report_body)}文字）')

            # フルHTMLを生成して保持
            _last_report_html = REPORT_HTML_TEMPLATE.replace('{{REPORT_BODY}}', report_body)

            # レポートURLを返す
            response = json.dumps({
                'report_url': f'http://localhost:{PORT}/report'
            }).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response)

        except Exception as e:
            print(f'エラー: {e}')
            error_resp = json.dumps({'error': str(e)}).encode('utf-8')
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(error_resp)

    def log_message(self, format, *args):
        # デフォルトのアクセスログを抑制
        pass


def main():
    print(f'Gravity CODE 診断サーバー起動')
    print(f'http://localhost:{PORT}')
    print(f'API endpoint: http://localhost:{PORT}/generate')
    print(f'Ctrl+C で停止\n')

    server = HTTPServer(('localhost', PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nサーバー停止')
        server.server_close()


if __name__ == '__main__':
    main()
