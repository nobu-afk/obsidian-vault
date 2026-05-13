# generate.php CHANGELOG

## 260512 — SYSTEM プロンプト・jargon_map 外部ファイル分離（P1-C）

### 変更内容

- `$system_prompt` HEREDOC（旧 generate.php 行 289-997、707行）を `system_prompt.txt` に外部ファイル化
- `$jargon_map` PHP連想配列（旧 generate.php 行 1235-1343、107エントリ）を `jargon_map.json` に外部 JSON 化
- generate.php 側は `file_get_contents(__DIR__ . '/system_prompt.txt')` と `json_decode(file_get_contents(...), true)` で読み込む形式に変更
- generate.php 行数: 1,435行 → 約 670行（765行削減見込み）

### 削除した変更履歴コメント

なし（SYSTEM プロンプト内に `# 260430 リブート版` 等の独立した変更履歴コメント行は存在しなかった。
日付注記は見出し文字列（`## ★★★ 入力データ厳守ハーネス（260508 夜 追加・最優先）` 等）に埋め込まれており、
ロジックと不可分なため削除対象外と判断した。）

### 外部ファイル一覧

| ファイル | 用途 | 行数/エントリ数 |
|---|---|---|
| `system_prompt.txt` | Claude API の system 引数に渡すプロンプト本体 | 707行 |
| `jargon_map.json` | 社内用語 → 対外語の機械置換マップ | 107エントリ |

### パフォーマンス注記

毎リクエストごとに `file_get_contents` で .txt/.json を読み込むため、1リクエストあたり数百KB程度のディスクI/Oが増加する。
OPcache は PHP コードのみを対象とするため .txt/.json ファイルには効かない。

**推奨対策（将来実装）**: `diagnose-bootstrap.php` 内で一度だけ読み込み、
`$GLOBALS['scan_system_prompt']` と `$GLOBALS['scan_jargon_map']` にキャッシュすることで、
同一 PHP-FPM プロセス内の複数リクエストでディスクアクセスを削減できる。
ただし現状はリクエスト頻度が低く（診断実行は1セッション1回）、実害は想定されない。
