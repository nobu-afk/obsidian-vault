<?php
/**
 * 問い直し装置の共通CSS
 * CODE（final-question）と Scan（analyst-question-block）で共用
 *
 * 使い方（呼び出し側 generate.php）:
 *   require_once __DIR__ . '/../../shared/question_block_styles.php';
 *   echo get_question_block_css();
 *
 * または変数経由で HEREDOC 内に埋め込む:
 *   $QUESTION_BLOCK_CSS = get_question_block_css();
 *   // <style> ... {$QUESTION_BLOCK_CSS} ... </style>
 */

if (!function_exists('get_question_block_css')) {
    function get_question_block_css() {
        return <<<'CSS'
/* === 問い直し装置（CODE/Scan 共通） === */
.final-question, .analyst-question-block {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #fff;
  border-radius: 12px;
  page-break-inside: avoid;
  text-align: center;
}
.final-question {
  padding: 32px 36px;
  margin: 32px 0 24px;
}
.analyst-question-block {
  padding: 28px 32px;
  margin: 28px 0 32px;
}
.analyst-question-divider {
  width: 40px;
  height: 2px;
  background: #94a3b8;
  margin: 0 auto 16px;
}
.final-question-label, .analyst-question-label {
  display: inline-block;
  font-size: 9pt;
  font-weight: 800;
  letter-spacing: 0.12em;
  color: #94a3b8;
  border: 1px solid #475569;
  padding: 4px 14px;
  border-radius: 100px;
  margin-bottom: 18px;
}
.analyst-question-label {
  border: none;
  padding: 0;
  margin-bottom: 14px;
}
.final-question-text, .analyst-question-text {
  font-weight: 700;
  color: #fff;
  margin: 0 0 14px;
  letter-spacing: 0.02em;
}
.final-question-text {
  font-size: 13pt;
  line-height: 1.7;
}
.analyst-question-text {
  font-size: 12pt;
  line-height: 1.9;
}
.analyst-question-text strong {
  color: #fbbf24;
  font-weight: 800;
}
.final-question-caveat, .analyst-question-caveat {
  font-size: 10pt;
  color: #cbd5e1;
  line-height: 1.7;
  margin: 0;
  font-style: italic;
}
.final-question-caveat {
  margin-bottom: 22px;
  font-style: normal;
}
.final-question-cta {
  display: inline-block;
  background: #fff;
  color: #0f172a;
  font-size: 11pt;
  font-weight: 700;
  padding: 14px 32px;
  border-radius: 100px;
  text-decoration: none;
  letter-spacing: 0.03em;
  transition: transform 0.2s, opacity 0.2s;
}
.final-question-cta:hover {
  transform: translateY(-1px);
  opacity: 0.92;
}

@media screen and (max-width: 800px) {
  .final-question, .analyst-question-block {
    padding: 24px 20px;
    margin: 24px 0 20px;
  }
  .final-question-text, .analyst-question-text {
    font-size: 15px;
    line-height: 1.8;
  }
  .final-question-caveat, .analyst-question-caveat {
    font-size: 12px;
    margin-bottom: 18px;
  }
  .final-question-cta {
    padding: 12px 24px;
    font-size: 13px;
  }
}

@media print {
  .final-question, .analyst-question-block {
    break-inside: avoid;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .final-question-cta {
    background: #0f172a !important;
    color: #fff !important;
    border: 2px solid #fff;
  }
}
CSS;
    }
}
