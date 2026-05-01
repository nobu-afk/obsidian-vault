#!/usr/bin/env python3
"""Generate SVG versions of Gravity Map and Loop chart for V9 web version."""

# ── GRAVITY MAP SVG ──────────────────────────────────────────────────────────
gravity_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 520" width="640" height="520" font-family="'Noto Sans JP', sans-serif">
  <!-- Background -->
  <rect width="640" height="520" fill="#f8fafc" rx="8"/>

  <!-- Title -->
  <text x="320" y="36" text-anchor="middle" font-size="15" font-weight="700" fill="#0f172a">Gravityマップ：事業の伸ばし方4パターン</text>

  <!-- Axis lines -->
  <!-- Vertical center -->
  <line x1="320" y1="60" x2="320" y2="460" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,3"/>
  <!-- Horizontal center -->
  <line x1="60" y1="260" x2="580" y2="260" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,3"/>

  <!-- Outer border axes -->
  <line x1="60" y1="60" x2="60" y2="460" stroke="#334155" stroke-width="2"/>
  <line x1="60" y1="460" x2="580" y2="460" stroke="#334155" stroke-width="2"/>

  <!-- Y-axis arrow -->
  <line x1="60" y1="60" x2="60" y2="30" stroke="#334155" stroke-width="2"/>
  <polygon points="60,22 55,36 65,36" fill="#334155"/>
  <!-- X-axis arrow -->
  <line x1="580" y1="460" x2="610" y2="460" stroke="#334155" stroke-width="2"/>
  <polygon points="618,460 604,455 604,465" fill="#334155"/>

  <!-- Y-axis labels -->
  <text x="52" y="64" text-anchor="end" font-size="9" fill="#64748b">仕組みで回す</text>
  <text x="52" y="458" text-anchor="end" font-size="9" fill="#64748b">人で回す</text>
  <text x="30" y="265" text-anchor="middle" font-size="10" fill="#334155" font-weight="700" transform="rotate(-90,30,265)">仕組み化レベル</text>

  <!-- X-axis labels -->
  <text x="65" y="478" text-anchor="start" font-size="9" fill="#64748b">今を回す</text>
  <text x="575" y="478" text-anchor="end" font-size="9" fill="#64748b">次を作る</text>
  <text x="320" y="498" text-anchor="middle" font-size="10" fill="#334155" font-weight="700">経営者の視点</text>

  <!-- ❶ 社長独走 (left-bottom) -->
  <rect x="68" y="268" width="244" height="184" fill="#e2e8f0" rx="6"/>
  <text x="190" y="300" text-anchor="middle" font-size="22" fill="#334155">❶</text>
  <text x="190" y="326" text-anchor="middle" font-size="14" font-weight="700" fill="#1e293b">社長独走</text>
  <text x="190" y="346" text-anchor="middle" font-size="9" fill="#475569">今を回す × 人で回す</text>
  <text x="190" y="372" text-anchor="middle" font-size="8.5" fill="#64748b">CEO関与度：80-100%</text>
  <text x="190" y="390" text-anchor="middle" font-size="8" fill="#94a3b8">社長が全決定を担い、</text>
  <text x="190" y="406" text-anchor="middle" font-size="8" fill="#94a3b8">組織が自走しない状態</text>

  <!-- ❷ 人力拡大 (right-bottom) -->
  <rect x="320" y="268" width="252" height="184" fill="#e2e8f0" rx="6"/>
  <text x="446" y="300" text-anchor="middle" font-size="22" fill="#334155">❷</text>
  <text x="446" y="326" text-anchor="middle" font-size="14" font-weight="700" fill="#1e293b">人力拡大</text>
  <text x="446" y="346" text-anchor="middle" font-size="9" fill="#475569">次を作る × 人で回す</text>
  <text x="446" y="372" text-anchor="middle" font-size="8.5" fill="#64748b">CEO関与度：60-80%</text>
  <text x="446" y="390" text-anchor="middle" font-size="8" fill="#94a3b8">採用で解決しようとするが、</text>
  <text x="446" y="406" text-anchor="middle" font-size="8" fill="#94a3b8">人が増えるほど複雑化する</text>

  <!-- ❸ 施策先行 (left-top) -->
  <rect x="68" y="68" width="244" height="184" fill="#cbd5e1" rx="6"/>
  <text x="190" y="100" text-anchor="middle" font-size="22" fill="#334155">❸</text>
  <text x="190" y="126" text-anchor="middle" font-size="14" font-weight="700" fill="#1e293b">施策先行</text>
  <text x="190" y="146" text-anchor="middle" font-size="9" fill="#475569">今を回す × 仕組みで回す</text>
  <text x="190" y="172" text-anchor="middle" font-size="8.5" fill="#64748b">CEO関与度：40-60%</text>
  <text x="190" y="190" text-anchor="middle" font-size="8" fill="#64748b">制度・ツールを導入するが、</text>
  <text x="190" y="206" text-anchor="middle" font-size="8" fill="#64748b">経営者の思想が乗っていない</text>

  <!-- ❹ グラビティ型成長 (right-top) - special treatment -->
  <rect x="320" y="68" width="252" height="184" fill="#0f172a" rx="6"/>
  <rect x="320" y="68" width="252" height="184" fill="none" stroke="#475569" stroke-width="3" rx="6"/>
  <text x="446" y="100" text-anchor="middle" font-size="22" fill="white">❹</text>
  <text x="446" y="126" text-anchor="middle" font-size="14" font-weight="700" fill="white">グラビティ型成長</text>
  <text x="446" y="146" text-anchor="middle" font-size="9" fill="#94a3b8">次を作る × 仕組みで回す</text>
  <text x="446" y="172" text-anchor="middle" font-size="8.5" fill="#94a3b8">CEO関与度：20-40%</text>
  <text x="446" y="190" text-anchor="middle" font-size="8" fill="#cbd5e1">経営者の思想が仕組みに宿り、</text>
  <text x="446" y="206" text-anchor="middle" font-size="8" fill="#cbd5e1">組織が自律的に引力を持つ</text>
  <text x="446" y="228" text-anchor="middle" font-size="9" fill="#64748b" font-style="italic">← 目指すべき状態</text>
</svg>
'''

with open('/home/ubuntu/v9_web/gravity_map.svg', 'w', encoding='utf-8') as f:
    f.write(gravity_svg)
print("gravity_map.svg written.")

# ── LOOP CHART SVG ────────────────────────────────────────────────────────────
loop_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" width="600" height="480" font-family="'Noto Sans JP', sans-serif">
  <!-- Background -->
  <rect width="600" height="480" fill="#f8fafc" rx="8"/>

  <!-- Title -->
  <text x="300" y="34" text-anchor="middle" font-size="15" font-weight="700" fill="#0f172a">勝ち筋ループ ── 引力の構造</text>

  <!-- Central label -->
  <ellipse cx="300" cy="240" rx="62" ry="38" fill="#0f172a"/>
  <text x="300" y="235" text-anchor="middle" font-size="10" font-weight="700" fill="white">引力のある</text>
  <text x="300" y="252" text-anchor="middle" font-size="10" font-weight="700" fill="white">組織</text>

  <!-- Node 1: 獲得 (top) -->
  <rect x="220" y="55" width="160" height="64" rx="8" fill="#1e293b"/>
  <text x="300" y="80" text-anchor="middle" font-size="14" font-weight="700" fill="white">顧客・案件の獲得</text>
  <text x="300" y="100" text-anchor="middle" font-size="9" fill="#94a3b8">引力が人・顧客を引き寄せる</text>

  <!-- Node 2: 提供 (right) -->
  <rect x="430" y="170" width="150" height="64" rx="8" fill="#334155"/>
  <text x="505" y="195" text-anchor="middle" font-size="14" font-weight="700" fill="white">価値の提供</text>
  <text x="505" y="215" text-anchor="middle" font-size="9" fill="#94a3b8">本来の強みで届ける</text>

  <!-- Node 3: 成果 (bottom) -->
  <rect x="220" y="355" width="160" height="64" rx="8" fill="#334155"/>
  <text x="300" y="380" text-anchor="middle" font-size="14" font-weight="700" fill="white">顧客の成果</text>
  <text x="300" y="400" text-anchor="middle" font-size="9" fill="#94a3b8">成果が信頼と実績を生む</text>

  <!-- Node 4: 拡大 (left) -->
  <rect x="20" y="170" width="150" height="64" rx="8" fill="#334155"/>
  <text x="95" y="195" text-anchor="middle" font-size="14" font-weight="700" fill="white">紹介・再購入</text>
  <text x="95" y="215" text-anchor="middle" font-size="9" fill="#94a3b8">による拡大</text>

  <!-- Arrows (clockwise) -->
  <!-- Top → Right -->
  <path d="M 380 87 Q 460 87 460 170" fill="none" stroke="#475569" stroke-width="2.5" marker-end="url(#arrow)"/>
  <!-- Right → Bottom -->
  <path d="M 505 234 Q 505 320 380 372" fill="none" stroke="#475569" stroke-width="2.5" marker-end="url(#arrow)"/>
  <!-- Bottom → Left -->
  <path d="M 220 387 Q 140 387 140 234" fill="none" stroke="#475569" stroke-width="2.5" marker-end="url(#arrow)"/>
  <!-- Left → Top -->
  <path d="M 95 170 Q 95 87 220 87" fill="none" stroke="#475569" stroke-width="2.5" marker-end="url(#arrow)"/>

  <!-- Arrow marker -->
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#475569"/>
    </marker>
  </defs>

  <!-- Loop label -->
  <text x="300" y="460" text-anchor="middle" font-size="9" fill="#94a3b8">獲得 → 提供 → 成果 → 拡大 → 再獲得（自己強化サイクル）</text>
</svg>
'''

with open('/home/ubuntu/v9_web/loop_chart.svg', 'w', encoding='utf-8') as f:
    f.write(loop_svg)
print("loop_chart.svg written.")
