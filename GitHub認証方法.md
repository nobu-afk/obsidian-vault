# GitHub認証方法

## 現在の状況
✅ リモートリポジトリの設定完了: `https://github.com/nobu-afk/obsidian-vault.git`
⚠️ プッシュ時に認証が必要

## 認証方法（2つの選択肢）

### 方法1: Personal Access Tokenを使用（推奨・簡単）

1. **Personal Access Tokenを作成**
   - GitHubにログイン
   - 右上のプロフィールアイコン → Settings
   - 左メニューの「Developer settings」
   - 「Personal access tokens」→「Tokens (classic)」
   - 「Generate new token」→「Generate new token (classic)」
   - Note（メモ）: `obsidian-vault` など任意の名前
   - Expiration（有効期限）: 適切な期間を選択
   - Scopes（権限）: `repo` にチェック（すべてのリポジトリへのアクセス）
   - 「Generate token」をクリック
   - **表示されたトークンをコピー**（後で見れないので注意！）

2. **プッシュ時にトークンを使用**
   ```bash
   cd "/Users/ishiinobuyuki/Documents/Obsidian Vault"
   git push -u origin main
   ```
   - Username: `nobu-afk` を入力
   - Password: **Personal Access Token**を貼り付け（パスワードではない！）

3. **トークンを保存（オプション）**
   - macOS Keychainに保存する場合:
   ```bash
   git config --global credential.helper osxkeychain
   ```

### 方法2: SSH鍵を使用

1. **SSH鍵を確認**
   ```bash
   ls -la ~/.ssh
   ```
   - `id_rsa.pub` または `id_ed25519.pub` があれば既に鍵が存在

2. **SSH鍵がない場合、作成**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
   - Enterキーを3回押してデフォルト設定で作成

3. **公開鍵をGitHubに登録**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   - 表示された内容をコピー
   - GitHub → Settings → SSH and GPG keys → New SSH key
   - Title: 任意の名前（例: `MacBook`）
   - Key: コピーした公開鍵を貼り付け
   - Add SSH key

4. **リモートURLをSSHに変更**
   ```bash
   cd "/Users/ishiinobuyuki/Documents/Obsidian Vault"
   git remote set-url origin git@github.com:nobu-afk/obsidian-vault.git
   ```

5. **プッシュ**
   ```bash
   git push -u origin main
   ```

## 推奨

**Personal Access Token（方法1）**が最も簡単です。一度設定すれば、macOS Keychainに保存されるため、次回以降は自動的に認証されます。

## 次のステップ

認証方法を選択して設定後、以下のコマンドでプッシュしてください：

```bash
cd "/Users/ishiinobuyuki/Documents/Obsidian Vault"
git push -u origin main
```

