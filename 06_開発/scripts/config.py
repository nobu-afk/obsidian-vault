"""
設定ファイル
環境変数から設定を読み込みます
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """設定クラス"""
    
    # Note.com 認証情報
    NOTE_EMAIL = os.getenv('NOTE_EMAIL', '')
    NOTE_PASSWORD = os.getenv('NOTE_PASSWORD', '')
    
    # 記事編集設定
    NOTE_EDIT_URL = os.getenv('NOTE_EDIT_URL', '')
    NOTE_OLD_TEXT = os.getenv('NOTE_OLD_TEXT', '')
    NOTE_NEW_TEXT = os.getenv('NOTE_NEW_TEXT', '')
    NOTE_LINK_URL = os.getenv('NOTE_LINK_URL', '')
    
    # 実行設定
    NOTE_HEADLESS = os.getenv('NOTE_HEADLESS', 'false').lower() == 'true'
    
    # クッキーファイルのパス
    COOKIES_FILE = os.getenv('COOKIES_FILE', 'note_cookies.json')
    
    @classmethod
    def validate(cls):
        """必須設定の検証"""
        errors = []
        
        if not cls.NOTE_EMAIL:
            errors.append("NOTE_EMAIL が設定されていません")
        if not cls.NOTE_PASSWORD:
            errors.append("NOTE_PASSWORD が設定されていません")
        if not cls.NOTE_EDIT_URL:
            errors.append("NOTE_EDIT_URL が設定されていません")
        if not cls.NOTE_OLD_TEXT:
            errors.append("NOTE_OLD_TEXT が設定されていません")
        if not cls.NOTE_NEW_TEXT:
            errors.append("NOTE_NEW_TEXT が設定されていません")
            
        if errors:
            raise ValueError("\n".join(errors))
        
        return True
