# 301 リダイレクト配信物

旧 URL → 新 URL の 301 リダイレクト用 .htaccess の格納場所。FTP 配置時に参照する。

## 現在の配信物

| ファイル | 配置先（FTP）| 用途 |
|---|---|---|
| `gravity-activate/.htaccess` | `growthfix.jp/public_html/gravity-activate/.htaccess` | 260505 Gravity Activate → Gravity Cultivate 命名変更に伴う 301（旧 URL の SEO 資産・既存リンク資産を保持）|

## 運用ルール

- 廃止 URL のフォルダ（例：`/gravity-activate/`）はサーバーから削除せず、`.htaccess` のみアップロードしてリダイレクトをかける
- ローカル `05_プロダクト/GravityActivate/` 等は git mv で消滅しているが、サーバー上の旧パスは半永久的に保持（リダイレクト維持のため）
- 新規廃止 URL が発生したら本ディレクトリ配下にサブフォルダを切り、`.htaccess` を配置して FTP デプロイする
