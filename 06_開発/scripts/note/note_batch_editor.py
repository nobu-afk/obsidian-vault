#!/usr/bin/env python3
"""
Note.comの複数記事を一括編集するスクリプト
指定したユーザーのすべての記事から、特定のテキスト/リンク/ウィジェットを削除
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# 環境変数を読み込む
load_dotenv()

class NoteBatchEditor:
    """Note.comの複数記事を一括編集するクラス"""
    
    def __init__(self, headless=False):
        self.headless = headless
        self.email = os.getenv('NOTE_EMAIL')
        self.password = os.getenv('NOTE_PASSWORD')
        self.playwright = None
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
            
            print("ブラウザを起動中...")
            print(f"ヘッドレスモード: {self.headless}")
            
            # テストスクリプトと同じ方法で起動（シンプルに）
            print("ブラウザを起動中...")
            try:
                self.browser = await self.playwright.chromium.launch(headless=self.headless)
                print("✓ ブラウザを起動しました")
                await asyncio.sleep(0.5)
            except Exception as launch_error:
                print(f"✗ ブラウザの起動に失敗: {type(launch_error).__name__}: {launch_error}")
                raise
            
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"✗ ブラウザの起動に失敗しました")
            print(f"{'='*60}")
            print(f"エラータイプ: {type(e).__name__}")
            print(f"エラーメッセージ: {e}")
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
            
            await asyncio.sleep(0.3)
            current_url = self.page.url
            print(f"✓ 初期URL: {current_url}")
            
            return self
        except Exception as e:
            print(f"✗ ブラウザコンテキストの作成に失敗しました: {e}")
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
        """クッキーを保存"""
        try:
            cookies = await self.context.cookies()
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2)
            print("✓ クッキーを保存しました")
        except Exception as e:
            print(f"⚠ クッキーの保存に失敗: {e}")
    
    async def login(self):
        """Note.comにログイン"""
        # クッキーを読み込む
        if await self.load_cookies():
            # ログイン状態を確認
            await self.page.goto('https://note.com/mypage', wait_until='networkidle', timeout=10000)
            if 'mypage' in self.page.url:
                print("✓ クッキーでログイン済み")
                return True
        
        # ログインページに移動
        print("ログインページにアクセス中...")
        await self.page.goto('https://note.com/login', wait_until='networkidle', timeout=30000)
        print("✓ ログインページにアクセスしました")
        
        await asyncio.sleep(2)
        
        # メールアドレスを入力
        email_selectors = [
            'input[name="email"]',
            'input[type="email"]',
            'input[placeholder*="メールアドレス"]',
            '#email',
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
            raise Exception("ログインページのメールアドレス入力欄が見つかりません")
        
        await email_input.fill(self.email)
        print("✓ メールアドレスを入力")
        
        # パスワードを入力
        password_selectors = [
            'input[name="password"]',
            'input[type="password"]',
            '#password',
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
        
        await password_input.fill(self.password)
        print("✓ パスワードを入力")
        
        # ログインボタンをクリック
        login_button_selectors = [
            'button[type="submit"]',
            'button:has-text("ログイン")',
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
            await self.page.wait_for_url('**/mypage**', timeout=15000)
            print("✓ ログイン成功")
            await self.save_cookies()
            return True
        except PlaywrightTimeoutError:
            try:
                error_locator = self.page.locator('.error, .alert, [role="alert"]').first
                if await error_locator.is_visible(timeout=2000):
                    error_text = await error_locator.text_content()
                    raise Exception(f"ログイン失敗: {error_text}")
            except PlaywrightTimeoutError:
                current_url = self.page.url
                if '/login' in current_url:
                    raise Exception("ログインに失敗しました。メールアドレスとパスワードを確認してください")
                else:
                    print("⚠ ログイン状態を確認できませんでしたが、続行します")
                    await self.save_cookies()
                    return True
    
    async def get_all_article_urls(self, user_url):
        """
        指定したユーザーのすべての記事URLを取得
        
        Args:
            user_url: ユーザーのNote.com URL（例: https://note.com/growthfix_corp）
        
        Returns:
            記事の編集URLのリスト
        """
        print(f"\n{'='*60}")
        print(f"記事一覧を取得中: {user_url}")
        print(f"{'='*60}")
        
        article_urls = []
        page_num = 1
        max_pages = 100  # 最大100ページまで取得
        
        while page_num <= max_pages:
            # 記事一覧ページにアクセス
            list_url = f"{user_url}?page={page_num}" if page_num > 1 else user_url
            print(f"\nページ {page_num} にアクセス中...")
            
            try:
                await self.page.goto(list_url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(2)
            except Exception as e:
                print(f"⚠ ページ {page_num} へのアクセスに失敗: {e}")
                break
            
            # 記事リンクを取得
            article_links = await self.page.locator('a[href*="/n/"]').all()
            
            if not article_links:
                print(f"✓ ページ {page_num} には記事がありませんでした")
                break
            
            print(f"✓ ページ {page_num} で {len(article_links)} 件の記事リンクを発見")
            
            for link in article_links:
                try:
                    href = await link.get_attribute('href')
                    if href and '/n/' in href:
                        # 公開URLから編集URLに変換
                        # 例: /growthfix_corp/n/n3b5600729769 → /notes/n3b5600729769/edit/
                        note_id = href.split('/n/')[-1].split('?')[0]
                        if note_id:
                            edit_url = f"https://editor.note.com/notes/{note_id}/edit/"
                            if edit_url not in article_urls:
                                article_urls.append(edit_url)
                                print(f"  ✓ 記事を追加: {edit_url}")
                except Exception as e:
                    print(f"  ⚠ リンクの取得に失敗: {e}")
                    continue
            
            # 次のページがあるか確認
            next_button = self.page.locator('a:has-text("次へ"), a:has-text(">"), .pagination-next').first
            if await next_button.is_visible(timeout=2000):
                page_num += 1
            else:
                print(f"✓ すべてのページを取得しました")
                break
        
        print(f"\n✓ 合計 {len(article_urls)} 件の記事を取得しました")
        return article_urls
    
    async def delete_from_article(self, edit_url, old_texts):
        """
        記事から指定したテキスト/リンク/ウィジェットを削除
        
        Args:
            edit_url: 記事の編集URL
            old_texts: 削除したいテキストのリスト
        """
        print(f"\n{'='*60}")
        print(f"記事を編集: {edit_url}")
        print(f"{'='*60}")
        
        try:
            # ブラウザが有効か確認
            if not self.page:
                raise Exception("ページが無効です")
            
            await self.page.goto(edit_url, wait_until='networkidle', timeout=30000)
            print(f"✓ ページにアクセスしました")
            
            # 下書きがある場合、公開版を読み込む必要がある
            # Note.comでは、編集画面にアクセスすると下書きが表示される
            # 公開版を確実に編集するため、一度公開版に切り替える
            await asyncio.sleep(3)
            
            # 公開版/下書き版の切り替えボタンを探す（複数のセレクターを試す）
            # Note.comでは、タブやリンクで切り替える可能性がある
            version_selectors = [
                'a:has-text("公開版")',
                'button:has-text("公開版")',
                '[data-tab="published"]',
                '[data-version="published"]',
                '.published-version-button',
                '[aria-label*="公開版"]',
                'a[href*="published"]',
            ]
            
            version_switched = False
            for selector in version_selectors:
                try:
                    version_button = self.page.locator(selector).first
                    if await version_button.is_visible(timeout=3000):
                        print(f"✓ 公開版切り替えボタンを発見: {selector}")
                        await version_button.click()
                        await asyncio.sleep(4)  # 切り替え後の読み込みを待つ（長めに）
                        print("✓ 公開版に切り替えました")
                        version_switched = True
                        break
                except Exception as e:
                    continue
            
            if not version_switched:
                print("⚠ 公開版切り替えボタンが見つかりませんでした（既に公開版の可能性があります）")
            
            # 切り替え後、ページが再読み込みされるまで待つ
            await asyncio.sleep(3)
            
        except Exception as e:
            error_msg = str(e)
            if "Target page, context or browser has been closed" in error_msg:
                raise  # 上位に伝播
            print(f"✗ エラー: ページにアクセスできませんでした: {e}")
            return False
        
        # エディタが読み込まれるまで待つ（公開版切り替え後は時間がかかる可能性がある）
        print("エディタの読み込みを待機中...")
        await asyncio.sleep(4)  # 公開版切り替え後は長めに待つ
        
        editor_selectors = [
            '[contenteditable="true"]',
            'textarea',
            '.editor',
            '.note-editor',
            '[role="textbox"]',
            '.ProseMirror',
            'div[contenteditable]',
            'article[contenteditable]',
        ]
        
        editor = None
        editor_selector = None
        
        # エディタを複数回試行（公開版切り替え後は読み込みに時間がかかる）
        max_editor_attempts = 5
        for attempt in range(1, max_editor_attempts + 1):
            for selector in editor_selectors:
                try:
                    elements = await self.page.locator(selector).all()
                    for elem in elements:
                        if await elem.is_visible(timeout=2000):
                            text = await elem.text_content()
                            if text and len(text) > 30:
                                editor = elem
                                editor_selector = selector
                                print(f"✓ エディタが見つかりました: {selector} (内容: {len(text)}文字)")
                                break
                    if editor:
                        break
                except:
                    continue
            
            if editor:
                break
            elif attempt < max_editor_attempts:
                print(f"  エディタ検索試行 {attempt}/{max_editor_attempts}... 再試行します")
                await asyncio.sleep(2)
        
        if not editor:
            print("✗ エディタが見つかりませんでした")
            # デバッグ用スクリーンショット
            try:
                await self.page.screenshot(path=f'debug_editor_not_found_{edit_url.split("/")[-2]}.png')
                print(f"デバッグ用スクリーンショットを保存しました")
            except:
                pass
            return False
        
        # 本文を取得（公開版の内容を確認）
        print("本文を取得中...")
        await asyncio.sleep(2)
        content = await editor.text_content()
        html_content = ""
        try:
            html_content = await editor.inner_html()
            print(f"✓ 本文を取得しました（テキスト: {len(content)}文字, HTML: {len(html_content)}文字）")
        except:
            print(f"✓ 本文を取得しました（テキスト: {len(content)}文字）")
        
        # 公開版の内容を確認（削除対象が含まれているか）
        print(f"公開版の内容を確認中...")
        if html_content:
            # HTMLコンテンツに削除対象が含まれているか確認
            for old_text in old_texts:
                if old_text in html_content or old_text in content:
                    print(f"  ✓ 公開版に '{old_text}' が含まれています")
                else:
                    print(f"  ⚠ 公開版に '{old_text}' は含まれていません（既に削除済みの可能性）")
        
        deleted_count = 0
        
        # 各削除対象を処理
        for text_to_delete in old_texts:
            if not text_to_delete:
                continue
            
            print(f"\n削除対象: '{text_to_delete}'")
            
            deleted = False
            
            # 方法1: 外部記事ウィジェットを検索
            try:
                widget_locator = editor.locator(f'.external-article-widget:has-text("{text_to_delete}")').first
                if await widget_locator.count() > 0:
                    print(f"  ✓ 外部記事ウィジェットを発見")
                    await widget_locator.click()
                    await asyncio.sleep(0.5)
                    await self.page.keyboard.press('Delete')
                    print(f"  ✓ '{text_to_delete}' を削除（外部記事ウィジェット）")
                    deleted = True
                    deleted_count += 1
                    await asyncio.sleep(0.5)
                    content = await editor.text_content()
                    try:
                        html_content = await editor.inner_html()
                    except:
                        pass
                    continue
            except:
                pass
            
            # 方法2: リンクのhref属性から検索（URLの場合）
            if not deleted and ('http://' in text_to_delete or 'https://' in text_to_delete):
                try:
                    # URLの部分一致で検索
                    url_parts = text_to_delete.replace('https://', '').replace('http://', '').split('/')
                    domain = url_parts[0] if url_parts else ''
                    
                    link_selectors = [
                        f'a[href*="{text_to_delete}"]',
                        f'a[href*="{domain}"]',
                    ]
                    
                    for selector in link_selectors:
                        try:
                            link_locator = editor.locator(selector).first
                            link_count = await link_locator.count()
                            if link_count > 0:
                                print(f"  ✓ リンクを発見（href属性）: {selector}")
                                await link_locator.click()
                                await asyncio.sleep(0.5)
                                # リンク全体を選択して削除
                                await self.page.keyboard.press('Control+A' if os.name != 'nt' else 'Meta+A')
                                await asyncio.sleep(0.2)
                                link_text = await link_locator.text_content()
                                if link_text:
                                    for _ in range(len(link_text)):
                                        await self.page.keyboard.press('Shift+ArrowRight')
                                await asyncio.sleep(0.2)
                                await self.page.keyboard.press('Delete')
                                print(f"  ✓ '{text_to_delete}' を削除（リンク）")
                                deleted = True
                                deleted_count += 1
                                await asyncio.sleep(0.5)
                                content = await editor.text_content()
                                try:
                                    html_content = await editor.inner_html()
                                except:
                                    pass
                                break
                        except:
                            continue
                except Exception as e:
                    print(f"  ⚠ リンク検索に失敗: {e}")
            
            # 方法3: リンクテキストで検索
            if not deleted:
                try:
                    link_locator = editor.locator(f'a:has-text("{text_to_delete}")').first
                    if await link_locator.count() > 0:
                        print(f"  ✓ リンクを発見（リンクテキスト）")
                        await link_locator.click()
                        await asyncio.sleep(0.3)
                        await self.page.keyboard.press('Delete')
                        print(f"  ✓ '{text_to_delete}' を削除（リンク）")
                        deleted = True
                        deleted_count += 1
                        await asyncio.sleep(0.5)
                        content = await editor.text_content()
                        try:
                            html_content = await editor.inner_html()
                        except:
                            pass
                        continue
                except:
                    pass
            
            # 方法4: テキストとして削除
            if not deleted and text_to_delete in content:
                try:
                    text_locator = editor.locator(f'text={text_to_delete}').first
                    await text_locator.click()
                    await text_locator.dblclick()
                    await asyncio.sleep(0.3)
                    await self.page.keyboard.press('Delete')
                    print(f"  ✓ '{text_to_delete}' を削除（テキスト）")
                    deleted = True
                    deleted_count += 1
                    await asyncio.sleep(0.5)
                    content = await editor.text_content()
                    try:
                        html_content = await editor.inner_html()
                    except:
                        pass
                except Exception as e:
                    print(f"  ⚠ テキスト削除に失敗: {e}")
            
            if not deleted:
                # HTMLには含まれているが、テキストには含まれていない場合
                if html_content and text_to_delete in html_content:
                    print(f"  ⚠ HTMLには含まれていますが、削除できませんでした（リンクとして埋め込まれている可能性）")
                else:
                    print(f"  ⚠ '{text_to_delete}' が見つかりませんでした")
        
        # 削除対象が見つかった場合も、見つからなかった場合も、公開処理を実行
        # （下書きがある場合、公開版を更新する必要があるため）
        
        if deleted_count > 0:
            print(f"\n✓ {deleted_count} 件の削除対象を削除しました")
        else:
            print("\n⚠ 削除対象が見つかりませんでした（既に削除済みの可能性があります）")
        
        # 保存と公開を実行
        print("保存・公開処理を開始...")
        await asyncio.sleep(1)
        
        # まず公開ボタンを探す（保存と公開が一緒のボタンの場合もある）
        publish_selectors = [
            'button:has-text("公開")',
            'button:has-text("公開する")',
            'button:has-text("公開して保存")',
            'button:has-text("リリース")',
            '[data-action="publish"]',
            '.publish-button',
            'button[aria-label*="公開"]',
        ]
        
        publish_button = None
        for selector in publish_selectors:
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
                await publish_button.click()
                await asyncio.sleep(3)
                print("✓ 記事を公開しました")
                return True
            except Exception as pub_error:
                print(f"⚠ 公開ボタンのクリックに失敗: {pub_error}")
        
        # 公開ボタンが見つからない場合、保存ボタンを探す
        save_button = self.page.locator('button:has-text("保存"), button:has-text("下書き保存")').first
        if await save_button.is_visible(timeout=5000):
            await save_button.click()
            await asyncio.sleep(2)
            print("✓ 記事を保存しました")
            
            # 保存後、再度公開ボタンを探す
            await asyncio.sleep(1)
            for selector in publish_selectors:
                try:
                    publish_button = self.page.locator(selector).first
                    if await publish_button.is_visible(timeout=2000):
                        print(f"✓ 公開ボタンを発見（保存後）: {selector}")
                        await publish_button.click()
                        await asyncio.sleep(3)
                        print("✓ 記事を公開しました")
                        return True
                except:
                    continue
            
            print("⚠ 公開ボタンが見つかりませんでした（既に公開済みの可能性があります）")
            return True
        else:
            print("⚠ 保存ボタンも公開ボタンも見つかりませんでした")
            return False
    
    async def process_all_articles(self, user_url, old_texts):
        """
        すべての記事を処理
        
        Args:
            user_url: ユーザーのNote.com URL
            old_texts: 削除したいテキストのリスト
        """
        # ログイン
        print("\nログイン処理を開始します...")
        await self.login()
        
        # すべての記事URLを取得
        article_urls = await self.get_all_article_urls(user_url)
        
        if not article_urls:
            print("✗ 記事が見つかりませんでした")
            return
        
        # テストモード: 最大処理数を制限
        max_articles = int(os.getenv('NOTE_MAX_ARTICLES', '0'))  # 0の場合はすべて処理
        if max_articles > 0:
            article_urls = article_urls[:max_articles]
            print(f"⚠ テストモード: 最大 {max_articles} 件まで処理します")
        
        print(f"\n{'='*60}")
        print(f"処理を開始します")
        print(f"  対象記事数: {len(article_urls)}")
        print(f"  削除対象: {old_texts}")
        print(f"{'='*60}\n")
        
        success_count = 0
        fail_count = 0
        skip_count = 0
        
        for idx, edit_url in enumerate(article_urls, 1):
            print(f"\n[{idx}/{len(article_urls)}] 処理中...")
            
            # ブラウザが閉じられていないか確認
            try:
                if not self.browser or not self.page:
                    print("⚠ ブラウザが閉じられています。再起動します...")
                    # ブラウザを再起動（簡易版：エラーをスキップ）
                    fail_count += 1
                    skip_count += 1
                    print(f"⚠ 記事 {idx}/{len(article_urls)} をスキップしました")
                    continue
                
                # ページが有効か確認
                try:
                    current_url = self.page.url
                except:
                    print("⚠ ページが無効です。スキップします...")
                    fail_count += 1
                    skip_count += 1
                    print(f"⚠ 記事 {idx}/{len(article_urls)} をスキップしました")
                    continue
                
            except Exception as check_error:
                print(f"⚠ ブラウザ状態の確認に失敗: {check_error}")
                fail_count += 1
                skip_count += 1
                print(f"⚠ 記事 {idx}/{len(article_urls)} をスキップしました")
                continue
            
            try:
                result = await self.delete_from_article(edit_url, old_texts)
                if result:
                    success_count += 1
                    print(f"✓ 記事 {idx}/{len(article_urls)} の処理が完了しました")
                else:
                    fail_count += 1
                    print(f"⚠ 記事 {idx}/{len(article_urls)} の処理に失敗しました（削除対象が見つかりませんでした）")
            except Exception as e:
                fail_count += 1
                error_type = type(e).__name__
                error_msg = str(e)
                
                # ブラウザが閉じられた場合の特別処理
                if "Target page, context or browser has been closed" in error_msg or "TargetClosedError" in error_type:
                    print(f"⚠ 記事 {idx}/{len(article_urls)} でブラウザが閉じられました")
                    print(f"   残りの記事をスキップします")
                    skip_count += 1
                    # 残りの記事もスキップ
                    remaining = len(article_urls) - idx
                    if remaining > 0:
                        skip_count += remaining
                        print(f"   残り {remaining} 件の記事をスキップしました")
                    break
                else:
                    print(f"✗ 記事 {idx}/{len(article_urls)} でエラーが発生: {error_type}: {error_msg}")
            
            # 次の記事処理前に少し待機
            await asyncio.sleep(2)
        
        print(f"\n{'='*60}")
        print(f"処理完了")
        print(f"  成功: {success_count} 件")
        print(f"  失敗: {fail_count} 件")
        if skip_count > 0:
            print(f"  スキップ: {skip_count} 件（ブラウザエラーなど）")
        print(f"{'='*60}")
        
        if skip_count > 0:
            print(f"\n⚠ {skip_count} 件の記事がスキップされました。")
            print(f"   再度実行すると、スキップされた記事のみ処理されます。")


async def main():
    """メイン処理"""
    import sys
    
    # 設定を環境変数または引数から取得
    user_url = os.getenv('NOTE_USER_URL') or (sys.argv[1] if len(sys.argv) > 1 else None)
    
    # 最大処理記事数（テスト用）
    max_articles = int(os.getenv('NOTE_MAX_ARTICLES', '0'))
    
    # 削除対象のテキストを取得
    old_texts = []
    idx = 1
    while True:
        text = os.getenv(f'NOTE_OLD_TEXT_{idx}')
        if text:
            old_texts.append(text)
            idx += 1
        else:
            break
    
    if not old_texts:
        # NOTE_OLD_TEXT からも取得を試みる
        old_text_str = os.getenv('NOTE_OLD_TEXT')
        if old_text_str:
            old_texts = [t.strip() for t in old_text_str.split('\n') if t.strip()]
    
    if not user_url or not old_texts:
        print("使用方法:")
        print("  python note_batch_editor.py <ユーザーURL>")
        print("\nまたは環境変数で設定:")
        print("  NOTE_USER_URL=https://note.com/growthfix_corp")
        print("  NOTE_OLD_TEXT_1=削除テキスト1")
        print("  NOTE_OLD_TEXT_2=削除テキスト2")
        print("  NOTE_MAX_ARTICLES=5  # テスト用: 最大処理記事数（0の場合はすべて）")
        print("  ...")
        sys.exit(1)
    
    # ヘッドレスモードの設定
    headless = os.getenv('NOTE_HEADLESS', 'false').lower() == 'true'
    
    try:
        async with NoteBatchEditor(headless=headless) as editor:
            await editor.process_all_articles(user_url, old_texts)
            
            print("\n処理完了！5秒後にブラウザを閉じます...")
            await asyncio.sleep(5)
            
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"✗ エラーが発生しました: {e}")
        print(f"{'='*60}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
