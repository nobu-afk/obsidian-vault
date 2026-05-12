"""
Note.com 記事編集自動化スクリプト
Playwrightを使用してNote.comの記事を自動編集します。
"""

import asyncio
import os
import json
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()


class NoteEditor:
    """Note.comの記事編集を自動化するクラス"""
    
    def __init__(self, headless=False):
        """
        初期化
        
        Args:
            headless: ブラウザを非表示で実行するかどうか
        """
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.cookies_file = Path("note_cookies.json")
        
    async def __aenter__(self):
        """非同期コンテキストマネージャーのエントリ"""
        try:
            print("Playwrightを起動中...")
            self.playwright = await async_playwright().start()
            print("✓ Playwrightを起動しました")
            
            # ブラウザ起動オプション（最小限に）
            print("ブラウザを起動中...")
            print(f"ヘッドレスモード: {self.headless}")
            
            # 複数の起動方法を試行
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    print(f"起動試行 {attempt}/{max_retries}...")
                    self.browser = await self.playwright.chromium.launch(
                        headless=self.headless,
                        timeout=60000  # タイムアウトを60秒に延長
                    )
                    print("✓ ブラウザを起動しました")
                    
                    # ブラウザが正常に起動したか確認
                    await asyncio.sleep(1)
                    
                    # ブラウザのバージョンを取得して確認
                    try:
                        version = await self.browser.version()
                        print(f"✓ ブラウザバージョン: {version}")
                    except:
                        print("⚠ ブラウザバージョンの取得に失敗しましたが、続行します")
                    
                    break  # 成功したらループを抜ける
                    
                except Exception as launch_error:
                    print(f"✗ 起動試行 {attempt} が失敗: {type(launch_error).__name__}: {launch_error}")
                    if attempt < max_retries:
                        print(f"   {max_retries - attempt}回再試行します...")
                        await asyncio.sleep(2)  # 2秒待ってから再試行
                    else:
                        raise Exception(f"ブラウザの起動に{max_retries}回失敗しました。最後のエラー: {launch_error}")
            
            # 少し待機
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"✗ ブラウザの起動に失敗しました")
            print(f"{'='*60}")
            print(f"エラータイプ: {type(e).__name__}")
            print(f"エラーメッセージ: {e}")
            print(f"\nトラブルシューティング:")
            print("1. Playwrightのブラウザを再インストール:")
            print("   python3 -m playwright install chromium")
            print("2. ヘッドレスモードを試す（.envファイルで）:")
            print("   NOTE_HEADLESS=true")
            print("3. macOSのセキュリティ設定を確認:")
            print("   システム環境設定 > セキュリティとプライバシー")
            print("="*60)
            import traceback
            traceback.print_exc()
            raise
        try:
            print("ブラウザコンテキストを作成中...")
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            print("✓ ブラウザコンテキストを作成しました")
            
            print("ページを作成中...")
            self.page = await self.context.new_page()
            print("✓ ページを作成しました")
            
            # ページが正常に作成されたか確認
            await asyncio.sleep(0.3)
            current_url = self.page.url
            print(f"✓ 初期URL: {current_url}")
            
            return self
        except Exception as e:
            print(f"✗ ブラウザコンテキストの作成に失敗しました: {e}")
            import traceback
            traceback.print_exc()
            if self.browser:
                try:
                    await self.browser.close()
                except:
                    pass
            raise
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャーのエグジット"""
        if self.browser:
            await self.browser.close()
        await self.playwright.stop()
        
    async def load_cookies(self):
        """保存されたクッキーを読み込む"""
        if self.cookies_file.exists():
            try:
                with open(self.cookies_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                    await self.context.add_cookies(cookies)
                    print("✓ クッキーを読み込みました")
                    return True
            except Exception as e:
                print(f"⚠ クッキーの読み込みに失敗: {e}")
                return False
        return False
        
    async def save_cookies(self):
        """現在のクッキーを保存"""
        try:
            cookies = await self.context.cookies()
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            print("✓ クッキーを保存しました")
        except Exception as e:
            print(f"⚠ クッキーの保存に失敗: {e}")
            
    async def login(self, email=None, password=None):
        """
        ログイン処理
        
        Args:
            email: メールアドレス（環境変数から取得可能）
            password: パスワード（環境変数から取得可能）
        """
        email = email or os.getenv('NOTE_EMAIL')
        password = password or os.getenv('NOTE_PASSWORD')
        
        if not email or not password:
            raise ValueError("メールアドレスとパスワードが必要です（環境変数または引数で指定）")
        
        # クッキーを試す
        if await self.load_cookies():
            await self.page.goto('https://note.com/', wait_until='networkidle')
            # ログイン済みかチェック
            try:
                await self.page.wait_for_selector('a[href*="/mypage"]', timeout=3000)
                print("✓ クッキーでログイン済みと確認")
                return True
            except PlaywrightTimeoutError:
                print("⚠ クッキーが無効。再ログインします")
        
        # ログインページに移動
        print("ログインページにアクセス中...")
        await self.page.goto('https://note.com/login', wait_until='networkidle', timeout=30000)
        print("✓ ログインページにアクセスしました")
        
        # ページの読み込みを待つ
        await asyncio.sleep(2)
        
        # メールアドレスを入力（複数のセレクターを試行）
        email_selectors = [
            'input[name="email"]',
            'input[type="email"]',
            'input[placeholder*="メールアドレス"]',
            'input[placeholder*="email"]',
            '#email',
            '.email-input',
            'input[autocomplete="email"]'
        ]
        
        email_input = None
        for selector in email_selectors:
            try:
                email_input = self.page.locator(selector).first
                if await email_input.is_visible(timeout=3000):
                    print(f"✓ メールアドレス入力欄を発見: {selector}")
                    break
            except:
                continue
        
        if not email_input or not await email_input.is_visible():
            # デバッグ用スクリーンショット
            await self.page.screenshot(path='debug_login_page.png')
            print("✗ メールアドレス入力欄が見つかりませんでした")
            print("デバッグ用スクリーンショットを保存しました: debug_login_page.png")
            raise Exception("ログインページのメールアドレス入力欄が見つかりません")
        
        await email_input.fill(email)
        print("✓ メールアドレスを入力")
        
        # パスワードを入力（複数のセレクターを試行）
        password_selectors = [
            'input[name="password"]',
            'input[type="password"]',
            'input[placeholder*="パスワード"]',
            'input[placeholder*="password"]',
            '#password',
            '.password-input',
            'input[autocomplete="current-password"]'
        ]
        
        password_input = None
        for selector in password_selectors:
            try:
                password_input = self.page.locator(selector).first
                if await password_input.is_visible(timeout=3000):
                    print(f"✓ パスワード入力欄を発見: {selector}")
                    break
            except:
                continue
        
        if not password_input or not await password_input.is_visible():
            raise Exception("ログインページのパスワード入力欄が見つかりません")
        
        await password_input.fill(password)
        print("✓ パスワードを入力")
        
        # ログインボタンをクリック（複数のセレクターを試行）
        login_button_selectors = [
            'button[type="submit"]',
            'button:has-text("ログイン")',
            'button:has-text("Login")',
            'input[type="submit"]',
            '.login-button',
            '[data-testid="login-button"]'
        ]
        
        login_button = None
        for selector in login_button_selectors:
            try:
                login_button = self.page.locator(selector).first
                if await login_button.is_visible(timeout=3000):
                    print(f"✓ ログインボタンを発見: {selector}")
                    break
            except:
                continue
        
        if not login_button or not await login_button.is_visible():
            raise Exception("ログインボタンが見つかりません")
        
        await login_button.click()
        print("✓ ログインボタンをクリック")
        
        # ログイン完了を待つ
        try:
            # ログイン成功の確認（URLが変わるか、特定の要素が表示される）
            await self.page.wait_for_url('**/mypage**', timeout=15000)
            print("✓ ログイン成功")
            await self.save_cookies()
            return True
        except PlaywrightTimeoutError:
            # タイムアウトした場合、エラーメッセージがあるか確認
            try:
                error_locator = self.page.locator('.error, .alert, [role="alert"]').first
                if await error_locator.is_visible(timeout=2000):
                    error_text = await error_locator.text_content()
                    raise Exception(f"ログイン失敗: {error_text}")
            except PlaywrightTimeoutError:
                # エラーメッセージが見つからない場合、現在のURLを確認
                current_url = self.page.url
                print(f"現在のURL: {current_url}")
                
                # mypageに遷移していないが、エラーもない場合、手動確認を促す
                if '/login' in current_url:
                    raise Exception("ログインに失敗しました。メールアドレスとパスワードを確認してください")
                else:
                    # 別のページに遷移している可能性がある
                    print("⚠ ログイン状態を確認できませんでしたが、続行します")
                    await self.save_cookies()
                    return True
            
    async def edit_article(self, edit_url, old_text, new_text, link_url=None):
        """
        記事を編集する
        
        Args:
            edit_url: 記事の編集URL（例: https://note.com/username/n/nnnnnnnnnnnn/edit）
            old_text: 削除したい文字列（文字列またはリスト、改行区切りの文字列も可）
            new_text: 新しいテキスト
            link_url: 新しいテキストに設定するリンクURL（オプション）
        """
        print(f"\n{'='*60}")
        print(f"記事編集を開始します")
        print(f"{'='*60}")
        print(f"編集URL: {edit_url}")
        print(f"削除対象: {old_text}")
        print(f"新規テキスト: {new_text if new_text else '(削除のみ)'}")
        print(f"{'='*60}\n")
        
        try:
            print(f"記事編集ページにアクセス中...")
            await self.page.goto(edit_url, wait_until='networkidle', timeout=30000)
            print(f"✓ ページにアクセスしました")
            
            # 下書きがある場合、公開版を読み込む必要がある
            await asyncio.sleep(2)
            
            # 公開版/下書き版の切り替えボタンを探す
            version_buttons = [
                'button:has-text("公開版"), button:has-text("公開済み")',
                '[data-version="published"]',
                '.published-version-button',
            ]
            
            for selector in version_buttons:
                try:
                    version_button = self.page.locator(selector).first
                    if await version_button.is_visible(timeout=2000):
                        print("✓ 公開版に切り替えます")
                        await version_button.click()
                        await asyncio.sleep(2)
                        break
                except:
                    continue
                    
        except Exception as e:
            print(f"✗ エラー: ページにアクセスできませんでした: {e}")
            raise
        
        # エディタが読み込まれるまで待つ
        print("エディタの読み込みを待機中...")
        await asyncio.sleep(3)  # エディタの読み込みを待つ
        
        # Note.comのエディタセレクター（複数のパターンを試す）
        editor_selectors = [
            '[contenteditable="true"]',
            'textarea',
            '.editor',
            '.note-editor',
            '[role="textbox"]',
            '.ProseMirror',  # Note.comが使用している可能性のあるエディタ
            'div[contenteditable]',
            'article[contenteditable]',
            '[data-testid="editor"]',
        ]
        
        editor = None
        editor_selector = None
        
        for selector in editor_selectors:
            try:
                elements = await self.page.locator(selector).all()
                for elem in elements:
                    if await elem.is_visible(timeout=2000):
                        # 内容を確認
                        text = await elem.text_content()
                        if text and len(text) > 30:  # 30文字以上の内容がある要素を選択
                            editor = elem
                            editor_selector = selector
                            print(f"✓ エディタが見つかりました: {selector} (内容: {len(text)}文字)")
                            break
                if editor:
                    break
            except:
                continue
        
        if not editor or not editor_selector:
            # ページのスクリーンショットを保存してデバッグ
            await self.page.screenshot(path='debug_editor_not_found.png')
            print("✗ エディタが見つかりませんでした")
            print("デバッグ用スクリーンショットを保存しました: debug_editor_not_found.png")
            raise Exception("エディタが見つかりません。URLが正しいか確認してください")
        
        # 本文を取得（テキストとHTMLの両方）
        print("本文を取得中...")
        await asyncio.sleep(2)  # エディタの内容が読み込まれるまで待つ
        
        content = await editor.text_content()
        
        # HTMLコンテンツも取得（リンク検索用）
        html_content = ""
        try:
            html_content = await editor.inner_html()
            print(f"✓ 本文を取得しました（テキスト: {len(content)}文字, HTML: {len(html_content)}文字）")
        except Exception as html_error:
            print(f"⚠ HTMLコンテンツの取得に失敗（テキストのみ）: {html_error}")
            print(f"✓ 本文を取得しました（テキスト: {len(content)}文字）")
        
        # old_textをリストに変換（複数の削除対象に対応）
        if isinstance(old_text, str):
            # 改行区切りで分割（空行は除外）
            old_texts = [t.strip() for t in old_text.split('\n') if t.strip()]
        elif isinstance(old_text, list):
            old_texts = old_text
        else:
            old_texts = [str(old_text)]
        
        # 複数のテキストを順番に削除
        for idx, text_to_delete in enumerate(old_texts, 1):
            if not text_to_delete:
                continue
                
            print(f"\n[{idx}/{len(old_texts)}] 削除対象: '{text_to_delete}'")
            
            deleted = False
            
            # 方法1: テキストとして直接検索
            if text_to_delete in content:
                print(f"✓ '{text_to_delete}' をテキストとして発見")
                
                try:
                    # テキストを含む要素を探す
                    text_locator = editor.locator(f'text={text_to_delete}').first
                    
                    # 親要素を確認（外部記事ウィジェットの場合）
                    try:
                        parent_widget = text_locator.locator('xpath=ancestor::div[contains(@class, "external-article-widget")]').first
                        if await parent_widget.count() > 0:
                            print(f"✓ 外部記事ウィジェットを発見。ウィジェット全体を削除します")
                            await parent_widget.click()
                            await asyncio.sleep(0.5)
                            await self.page.keyboard.press('Delete')
                            print(f"✓ '{text_to_delete}' を削除（外部記事ウィジェット）")
                            deleted = True
                            await asyncio.sleep(0.5)
                            content = await editor.text_content()
                            try:
                                html_content = await editor.inner_html()
                            except:
                                pass
                    except:
                        pass
                    
                    # ウィジェットでない場合、通常のテキスト削除
                    if not deleted:
                        await editor.click()
                        await asyncio.sleep(0.5)
                        await text_locator.click()
                        await text_locator.dblclick()
                        await asyncio.sleep(0.3)
                        await self.page.keyboard.press('Delete')
                        print(f"✓ '{text_to_delete}' を削除（テキスト）")
                        deleted = True
                        await asyncio.sleep(0.5)
                        content = await editor.text_content()
                except Exception as e:
                    print(f"⚠ テキスト選択に失敗: {e}")
                    # 外部記事ウィジェットを直接検索
                    try:
                        widget_locator = editor.locator(f'.external-article-widget:has-text("{text_to_delete}")').first
                        if await widget_locator.count() > 0:
                            print(f"✓ 外部記事ウィジェットを直接発見")
                            await widget_locator.click()
                            await asyncio.sleep(0.5)
                            await self.page.keyboard.press('Delete')
                            print(f"✓ '{text_to_delete}' を削除（外部記事ウィジェット）")
                            deleted = True
                            await asyncio.sleep(0.5)
                            content = await editor.text_content()
                    except:
                        pass
            
            # 方法2: リンクとして検索（href属性にURLが含まれている場合）
            if not deleted:
                try:
                    print(f"リンクとして検索中: '{text_to_delete}'")
                    
                    # リンク要素を検索（href属性にURLが含まれている）
                    # 複数のセレクターを試す
                    url_without_protocol = text_to_delete.replace('https://', '').replace('http://', '')
                    domain = url_without_protocol.split('/')[0] if '/' in url_without_protocol else url_without_protocol
                    path_parts = url_without_protocol.split('/')[1:] if '/' in url_without_protocol else []
                    path = '/' + '/'.join(path_parts) if path_parts else ''
                    
                    link_selectors = [
                        f'a[href="{text_to_delete}"]',  # 完全一致
                        f'a[href*="{text_to_delete}"]',  # 部分一致
                        f'a[href*="{url_without_protocol}"]',  # プロトコルなし
                        f'a[href*="{domain}"]',  # ドメインで検索
                    ]
                    
                    # パスがある場合のみ追加
                    if path and len(path) > 1:
                        link_selectors.append(f'a[href*="{path}"]')
                    
                    # パスの一部でも検索
                    if path_parts:
                        for part in path_parts:
                            if len(part) > 5:  # 5文字以上の部分のみ
                                link_selectors.append(f'a[href*="{part}"]')
                    
                    print(f"試行するセレクター数: {len(link_selectors)}")
                    
                    for selector in link_selectors:
                        try:
                            # ページ全体からも検索を試行
                            link_locator = editor.locator(selector).first
                            link_count = await link_locator.count()
                            if link_count > 0:
                                if await link_locator.is_visible(timeout=2000):
                                    print(f"✓ '{text_to_delete}' をリンクとして発見: {selector}")
                                    
                                    # リンクを削除（より安全な方法）
                                    try:
                                        # 方法A: リンクの親要素を取得して削除
                                        parent = link_locator.locator('xpath=..').first
                                        if await parent.count() > 0:
                                            await parent.click()
                                            await asyncio.sleep(0.3)
                                            await self.page.keyboard.press('Delete')
                                        else:
                                            # 方法B: リンクをクリックして選択
                                            await link_locator.click()
                                            await asyncio.sleep(0.3)
                                            # リンクテキスト全体を選択
                                            link_text = await link_locator.text_content()
                                            if link_text:
                                                # 全選択してから削除
                                                await self.page.keyboard.press('Control+A' if os.name != 'nt' else 'Meta+A')
                                                await asyncio.sleep(0.2)
                                                # リンクテキストだけを選択するため、範囲選択
                                                for _ in range(len(link_text)):
                                                    await self.page.keyboard.press('Shift+ArrowRight')
                                            await asyncio.sleep(0.2)
                                            await self.page.keyboard.press('Delete')
                                        
                                        print(f"✓ '{text_to_delete}' を削除（リンク）")
                                        deleted = True
                                        await asyncio.sleep(1)  # 削除後の待機時間を延長
                                        content = await editor.text_content()
                                        # HTMLコンテンツも再取得
                                        try:
                                            html_content = await editor.inner_html()
                                        except:
                                            pass
                                        break
                                    except Exception as del_error:
                                        print(f"⚠ リンク削除に失敗: {del_error}")
                                        continue
                        except Exception as sel_error:
                            continue
                except Exception as e:
                    print(f"⚠ リンク検索に失敗: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 方法3: 画像として検索（画像にリンクが設定されている場合）
            if not deleted:
                try:
                    # 画像要素を検索（href属性または親要素のaタグにURLが含まれている）
                    img_selectors = [
                        f'img[src*="{text_to_delete}"]',  # 画像のsrcにURLが含まれている
                        f'a[href*="{text_to_delete}"] img',  # リンク内の画像
                        f'img[alt*="{text_to_delete}"]',  # alt属性にURLが含まれている
                    ]
                    
                    for selector in img_selectors:
                        try:
                            img_locator = editor.locator(selector).first
                            if await img_locator.is_visible(timeout=2000):
                                print(f"✓ '{text_to_delete}' を画像として発見: {selector}")
                                await img_locator.click()
                                await asyncio.sleep(0.5)
                                # 画像を削除
                                await self.page.keyboard.press('Delete')
                                print(f"✓ '{text_to_delete}' を削除（画像）")
                                deleted = True
                                await asyncio.sleep(0.5)
                                content = await editor.text_content()
                                break
                        except:
                            continue
                except Exception as e:
                    print(f"⚠ 画像検索に失敗: {e}")
            
            # 方法4: 部分一致で検索（URLの一部が含まれている場合）
            if not deleted:
                # URLのドメイン部分やパス部分で検索
                url_parts = text_to_delete.replace('https://', '').replace('http://', '').split('/')
                for part in url_parts:
                    if len(part) > 5 and part in content:  # 5文字以上の部分のみ
                        print(f"⚠ URLの一部 '{part}' が見つかりました。手動で確認してください")
                        break
            
            # 方法5: HTMLコンテンツ全体から置換
            if not deleted:
                try:
                    print("HTMLコンテンツ全体から置換を試行...")
                    await editor.click()
                    await self.page.keyboard.press('Control+A' if os.name != 'nt' else 'Meta+A')
                    await asyncio.sleep(0.3)
                    full_content = await editor.text_content()
                    if text_to_delete in full_content:
                        new_content = full_content.replace(text_to_delete, '')
                        await editor.fill('')
                        await editor.type(new_content, delay=50)
                        print(f"✓ '{text_to_delete}' を削除（全置換）")
                        deleted = True
                        await asyncio.sleep(0.5)
                        content = await editor.text_content()
                except Exception as e:
                    print(f"⚠ 全置換に失敗: {e}")
            
            if not deleted:
                print(f"⚠ 警告: '{text_to_delete}' が見つかりませんでした")
                print(f"   現在の本文の一部: {content[:300]}...")
                print(f"   ヒント: URLがリンクとして埋め込まれている場合、リンクテキストを指定してください")
        
        # 新しいテキストを入力（new_textが指定されている場合のみ）
        if new_text:
            print(f"新しいテキストを入力: '{new_text}'")
            await editor.click()
            
            # カーソル位置を調整（最後に移動）
            await self.page.keyboard.press('End')
            await asyncio.sleep(0.3)
            
            # テキストを入力
            await editor.type(new_text, delay=50)
            await asyncio.sleep(0.5)
        else:
            print("新しいテキストは指定されていません（削除のみ）")
        
        # リンクを設定
        if link_url:
            print(f"リンクを設定: {link_url}")
            # 入力したテキストを選択
            # 方法1: 入力したテキストを選択
            await self.page.keyboard.press('Shift+ArrowLeft', press_options={'times': len(new_text)})
            await asyncio.sleep(0.3)
            
            # リンクボタンを探してクリック
            # Note.comのリンクボタンは通常、ツールバーにある
            link_button_selectors = [
                'button[aria-label*="リンク"], button[title*="リンク"]',
                'button:has-text("リンク")',
                '.link-button, .toolbar-link',
                '[data-action="link"]'
            ]
            
            link_button = None
            for selector in link_button_selectors:
                try:
                    link_button = self.page.locator(selector).first
                    if await link_button.is_visible(timeout=2000):
                        break
                except:
                    continue
            
            if link_button:
                await link_button.click()
                await asyncio.sleep(0.5)
                
                # リンクURL入力欄にURLを入力
                url_input_selectors = [
                    'input[type="url"], input[name="url"], input[placeholder*="URL"]',
                    '.link-url-input, .url-input'
                ]
                
                for selector in url_input_selectors:
                    try:
                        url_input = self.page.locator(selector).first
                        if await url_input.is_visible(timeout=2000):
                            await url_input.fill(link_url)
                            await asyncio.sleep(0.3)
                            # 確定ボタン
                            confirm_button = self.page.locator('button:has-text("確定"), button:has-text("OK"), button[type="submit"]').first
                            if await confirm_button.is_visible(timeout=2000):
                                await confirm_button.click()
                            print(f"✓ リンクを設定: {link_url}")
                            break
                    except:
                        continue
            else:
                # キーボードショートカットを試す（Ctrl+K または Cmd+K）
                print("リンクボタンが見つからないため、キーボードショートカットを試行")
                await self.page.keyboard.press('Control+K' if os.name != 'nt' else 'Meta+K')
                await asyncio.sleep(1)
                
                # URL入力欄を探す
                url_input = self.page.locator('input[type="url"], input[name="url"]').first
                if await url_input.is_visible(timeout=3000):
                    await url_input.fill(link_url)
                    await self.page.keyboard.press('Enter')
                    print(f"✓ リンクを設定（キーボードショートカット）: {link_url}")
        
        await asyncio.sleep(1)  # 変更が反映されるまで待機
        
        # 公開設定を確認（必要に応じて）
        print("公開設定を確認中...")
        # Note.comの公開設定は通常、サイドバーまたは上部にある
        publish_selectors = [
            'button:has-text("公開"), button:has-text("保存")',
            '[data-action="publish"], .publish-button',
            'button[aria-label*="公開"]'
        ]
        
        # 保存ボタンを探す
        save_button = None
        for selector in publish_selectors:
            try:
                save_button = self.page.locator(selector).first
                if await save_button.is_visible(timeout=2000):
                    break
            except:
                continue
        
        # まず公開ボタンを探す（保存と公開が一緒のボタンの場合もある）
        publish_button_selectors = [
            'button:has-text("公開")',
            'button:has-text("公開する")',
            'button:has-text("公開して保存")',
            'button:has-text("リリース")',
            '[data-action="publish"]',
            '.publish-button',
            'button[aria-label*="公開"]',
        ]
        
        publish_button = None
        for selector in publish_button_selectors:
            try:
                publish_button = self.page.locator(selector).first
                if await publish_button.is_visible(timeout=2000):
                    print(f"✓ 公開ボタンを発見: {selector}")
                    break
            except:
                continue
        
        if publish_button:
            # 公開ボタンが見つかった場合、それをクリック（保存も同時に行われる）
            try:
                print("公開ボタンをクリック...")
                await publish_button.click()
                await asyncio.sleep(3)
                print("✓ 記事を公開しました")
            except Exception as pub_error:
                print(f"⚠ 公開ボタンのクリックに失敗: {pub_error}")
        elif save_button:
            # 公開ボタンが見つからない場合、保存ボタンをクリック
            print("保存ボタンをクリック...")
            await save_button.click()
            await asyncio.sleep(2)
            
            # 保存完了を確認
            try:
                await self.page.wait_for_selector('.success, .saved, [data-saved="true"]', timeout=5000)
                print("✓ 記事を保存しました")
            except PlaywrightTimeoutError:
                print("⚠ 保存完了の確認ができませんでしたが、保存は実行されました")
            
            # 保存後、再度公開ボタンを探す
            print("公開処理を確認中...")
            await asyncio.sleep(1)
            
            for selector in publish_button_selectors:
                try:
                    publish_button = self.page.locator(selector).first
                    if await publish_button.is_visible(timeout=2000):
                        print(f"✓ 公開ボタンを発見（保存後）: {selector}")
                        await publish_button.click()
                        await asyncio.sleep(3)
                        print("✓ 記事を公開しました")
                        break
                except:
                    continue
            else:
                print("⚠ 公開ボタンが見つかりませんでした（既に公開済みの可能性があります）")
        else:
            print("⚠ 保存ボタンも公開ボタンも見つかりませんでした")
            print("手動で保存・公開してください")
            
        print("\n✓ 編集処理が完了しました")


async def main():
    """メイン処理"""
    import sys
    
    # 設定を環境変数または引数から取得
    edit_url = os.getenv('NOTE_EDIT_URL') or (sys.argv[1] if len(sys.argv) > 1 else None)
    
    # NOTE_OLD_TEXTは複数指定可能（改行区切り）
    # NOTE_OLD_TEXT_1, NOTE_OLD_TEXT_2 なども対応
    old_text = os.getenv('NOTE_OLD_TEXT') or (sys.argv[2] if len(sys.argv) > 2 else None)
    
    # 複数のNOTE_OLD_TEXT_* がある場合は結合
    old_texts = []
    if old_text:
        old_texts.append(old_text)
    
    # NOTE_OLD_TEXT_1, NOTE_OLD_TEXT_2 などをチェック
    idx = 1
    while True:
        additional_text = os.getenv(f'NOTE_OLD_TEXT_{idx}')
        if additional_text:
            old_texts.append(additional_text)
            idx += 1
        else:
            break
    
    # 複数のold_textを改行区切りで結合
    if old_texts:
        old_text = '\n'.join(old_texts)
    else:
        old_text = None
    
    new_text = os.getenv('NOTE_NEW_TEXT') or (sys.argv[3] if len(sys.argv) > 3 else None)
    # NOTE_NEW_TEXTが空文字列の場合はNoneに変換（削除のみの場合）
    if new_text == '':
        new_text = None
    
    link_url = os.getenv('NOTE_LINK_URL') or (sys.argv[4] if len(sys.argv) > 4 else None)
    # NOTE_LINK_URLが空文字列の場合はNoneに変換
    if link_url == '':
        link_url = None
    
    # 必須チェック: edit_urlとold_textは必須、new_textはオプション（削除のみの場合）
    if not edit_url or not old_text:
        print("使用方法:")
        print("  python note_editor.py <編集URL> <削除テキスト> <新規テキスト> [リンクURL]")
        print("\nまたは環境変数で設定:")
        print("  NOTE_EDIT_URL（必須）, NOTE_OLD_TEXT（必須）, NOTE_NEW_TEXT（オプション）, NOTE_LINK_URL（オプション）")
        print("\n複数の削除対象を指定する場合:")
        print("  NOTE_OLD_TEXT（改行区切り）または NOTE_OLD_TEXT_1, NOTE_OLD_TEXT_2 など")
        print("\n注意: NOTE_NEW_TEXTが空の場合は、削除のみが実行されます")
        sys.exit(1)
    
    # ヘッドレスモードの設定（環境変数から）
    headless = os.getenv('NOTE_HEADLESS', 'false').lower() == 'true'
    
    try:
        async with NoteEditor(headless=headless) as editor:
            # ログイン
            print("\nログイン処理を開始します...")
            await editor.login()
            
            # 記事編集
            await editor.edit_article(
                edit_url=edit_url,
                old_text=old_text,
                new_text=new_text,
                link_url=link_url
            )
            
            print("\n" + "="*60)
            print("処理完了！5秒後にブラウザを閉じます...")
            print("="*60)
            await asyncio.sleep(5)
            
    except Exception as e:
        print("\n" + "="*60)
        print(f"✗ エラーが発生しました: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
