# Fitbit開発者ポータル - アプリ登録手順

## 概要

Fitbit APIを使用するためには、まずFitbit開発者ポータルでアプリケーションを登録し、OAuth 2.0認証を通じてアクセストークンを取得する必要があります。

## 1. Fitbit開発者アカウントの作成

1. [Fitbit開発者ポータル](https://dev.fitbit.com/)にアクセス
2. 右上の「**Log In**」または「**Sign Up**」をクリック
3. Fitbitアカウントでログイン（Fitbitアカウントがない場合は新規作成）

## 2. アプリケーションの登録

### 2.1 アプリ登録画面へアクセス

1. ログイン後、右上の「**Manage**」をクリック
2. 「**Register An App**」を選択

### 2.2 必須情報の入力

以下の情報を入力します：

#### 基本情報
- **Application Name**: アプリケーション名（例：My Fitbit App）
- **Description**: アプリケーションの説明
- **Application Website**: アプリケーションのウェブサイトURL（任意）

#### OAuth 2.0設定（重要）

- **OAuth 2.0 Application Type**: 
  - `Personal` を選択（個人開発・テスト用）
  - `Server` を選択（本番環境用、より厳格な審査が必要）

- **Redirect URL**: 
  - 開発環境の場合：`http://localhost:8888` など
  - 本番環境の場合：実際のコールバックURL（例：`https://yourdomain.com/callback`）
  - **重要**: このURLは後で変更可能ですが、認証フローで使用するため正確に入力

- **Default Access Type**: 
  - `Read Only`: 読み取り専用（推奨）
  - `Read & Write`: 読み書き可能（より多くの権限が必要）

#### その他の設定

- **Organization**: 組織名（個人の場合は個人名）
- **Terms of Service URL**: 利用規約のURL（任意）
- **Privacy Policy URL**: プライバシーポリシーのURL（任意）

### 2.3 登録完了

1. 「**Register**」ボタンをクリック
2. 登録が完了すると、以下の情報が表示されます：
   - **Client ID**（OAuth Client ID）
   - **Client Secret**（OAuth Client Secret）

⚠️ **重要**: これらの情報は**一度しか表示されません**。必ず安全な場所に保存してください。

## 3. 必要な情報の確認

アプリ登録後、以下の情報を控えておきます：

- **Client ID**: OAuth認証で使用
- **Client Secret**: トークン取得時に使用
- **Redirect URL**: 認証後のコールバック先
- **Application Type**: Personal または Server

## 4. 次のステップ

アプリ登録が完了したら、次はOAuth 2.0認証フローを実装してアクセストークンを取得します。

詳細は「**Fitbit OAuth2.0認証フロー実装手順.md**」を参照してください。

## 参考リンク

- [Fitbit開発者ポータル](https://dev.fitbit.com/)
- [Fitbit Web API ドキュメント](https://dev.fitbit.com/build/reference/web-api/)














