# CursorとGitHub連携ガイド

## 現在の状況
✅ Gitリポジトリの初期化完了
✅ .gitignoreファイルの作成完了
✅ 初回コミット完了
✅ リモートリポジトリの設定完了: `https://github.com/nobu-afk/obsidian-vault.git`
⚠️ プッシュ時に認証が必要（次のステップ）

## 次のステップ

### 1. GitHubリポジトリを作成する

1. GitHubにログインして、https://github.com/new にアクセス
2. リポジトリ名を入力（例: `obsidian-vault`）
3. 説明を追加（任意）
4. **Public** または **Private** を選択
5. **「Initialize this repository with a README」のチェックを外す**（既にローカルにファイルがあるため）
6. 「Create repository」をクリック

### 2. リモートリポジトリを設定する（✅ 完了）

リモートリポジトリの設定は完了しています：
- リモートURL: `https://github.com/nobu-afk/obsidian-vault.git`
- ブランチ: `main`

### 3. 認証について（重要）

GitHubへのプッシュには認証が必要です。詳細は **`GitHub認証方法.md`** を参照してください。

**簡単な方法（推奨）: Personal Access Token**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 「Generate new token (classic)」をクリック
3. `repo` スコープにチェック
4. トークンを生成してコピー
5. プッシュ時に Username: `nobu-afk`、Password: **トークン**を入力

詳細な手順は `GitHub認証方法.md` を参照してください。

### 4. 今後の作業フロー

変更をコミットしてプッシュする場合：

```bash
git add .
git commit -m "変更内容の説明"
git push
```

### 5. CursorでのGit操作

Cursorでは、サイドバーのソース管理アイコンから以下が可能です：
- 変更の確認
- コミット
- プッシュ/プル
- ブランチの切り替え

## トラブルシューティング

### 認証エラーが発生する場合
- Personal Access Tokenを使用しているか確認
- GitHub CLI (`gh auth login`) を使用して認証

### プッシュが拒否される場合
- リモートリポジトリが正しく設定されているか確認: `git remote -v`
- ブランチ名が `main` になっているか確認: `git branch`

