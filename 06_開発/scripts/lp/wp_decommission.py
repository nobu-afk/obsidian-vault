#!/usr/bin/env python3
"""
WordPress complete decommission
Usage:
  python3 wp_decommission.py clean-html    # Local HTML cleanup only
  python3 wp_decommission.py move-assets   # FTP: copy WP assets to /assets/
  python3 wp_decommission.py upload-html   # FTP: upload cleaned HTMLs
  python3 wp_decommission.py delete-wp     # FTP: delete WP core files (DESTRUCTIVE)
  python3 wp_decommission.py edit-htaccess # FTP: strip WP rewrite block
  python3 wp_decommission.py verify        # HTTP verification
"""
import ftplib
import re
import sys
import os
import tempfile
from pathlib import Path

FTP_HOST = "sv16489.xserver.jp"
FTP_USER = "xs992119"
FTP_PASS = "cgq1fv99"
REMOTE_ROOT = "/growthfix.jp/public_html"

VAULT = Path("/Users/ishiinobuyuki/Documents/Obsidian Vault")
TOP_HTML = VAULT / "05_プロダクト/top_本番/index.html"

ASSET_MOVES = [
    ("wp-content/themes/growth/assets/css/animate.min.css", "assets/css/animate.min.css"),
    ("wp-content/themes/growth/assets/js/wow.min.js", "assets/js/wow.min.js"),
    ("wp-content/themes/growth/assets/js/bundle.js", "assets/js/bundle.js"),
    ("wp-content/themes/growth/assets/js/common.js", "assets/js/common.js"),
    ("wp-content/themes/growth/assets/img/top/fv_bg1.png", "assets/img/top/fv_bg1.png"),
    ("wp-content/themes/growth/assets/img/top/fv_bg2.png", "assets/img/top/fv_bg2.png"),
    ("wp-content/themes/growth/assets/img/common/btn_white.svg", "assets/img/common/btn_white.svg"),
    ("wp-content/themes/growth/assets/img/common/new_btn_arrow.svg", "assets/img/common/new_btn_arrow.svg"),
    ("wp-content/uploads/2025/06/DSC00224-scaled.jpg", "assets/img/profile/DSC00224.jpg"),
    ("wp-content/uploads/2025/12/Gemini_Generated_Image_ab1rfcab1rfcab1r-1024x572.png", "assets/img/knowledge/gravity-management.png"),
    ("wp-content/uploads/2025/12/Gemini_Generated_Image_oe4hieoe4hieoe4h-1024x572.png", "assets/img/knowledge/org-design.png"),
    ("wp-content/uploads/2025/09/Gemini_Generated_Image_dsdibwdsdibwdsdi-1024x572.png", "assets/img/knowledge/business-hr.png"),
]

URL_REPLACEMENTS = [
    ("https://growthfix.jp/wp-content/themes/growth/assets/img/top/fv_bg1.png", "https://growthfix.jp/assets/img/top/fv_bg1.png"),
    ("https://growthfix.jp/wp-content/themes/growth/assets/img/top/fv_bg2.png", "https://growthfix.jp/assets/img/top/fv_bg2.png"),
    ("https://growthfix.jp/wp-content/themes/growth/assets/img/common/btn_white.svg", "https://growthfix.jp/assets/img/common/btn_white.svg"),
    ("https://growthfix.jp/wp-content/themes/growth/assets/img/common/new_btn_arrow.svg", "https://growthfix.jp/assets/img/common/new_btn_arrow.svg"),
    ("https://growthfix.jp/wp-content/uploads/2025/06/DSC00224-scaled.jpg", "https://growthfix.jp/assets/img/profile/DSC00224.jpg"),
    ("https://growthfix.jp/wp-content/uploads/2025/12/Gemini_Generated_Image_ab1rfcab1rfcab1r-1024x572.png", "https://growthfix.jp/assets/img/knowledge/gravity-management.png"),
    ("https://growthfix.jp/wp-content/uploads/2025/12/Gemini_Generated_Image_oe4hieoe4hieoe4h-1024x572.png", "https://growthfix.jp/assets/img/knowledge/org-design.png"),
    ("https://growthfix.jp/wp-content/uploads/2025/09/Gemini_Generated_Image_dsdibwdsdibwdsdi-1024x572.png", "https://growthfix.jp/assets/img/knowledge/business-hr.png"),
    ("https://growthfix.jp/wp-content/themes/growth/assets/js/wow.min.js", "https://growthfix.jp/assets/js/wow.min.js"),
    ("https://growthfix.jp/wp-content/themes/growth/assets/js/bundle.js", "https://growthfix.jp/assets/js/bundle.js"),
    ("https://growthfix.jp/wp-content/themes/growth/assets/js/common.js", "https://growthfix.jp/assets/js/common.js"),
]

LOCAL_TO_REMOTE_HTMLS = [
    ("05_プロダクト/top_本番/index.html", "index.html"),
    ("05_プロダクト/contact_本番/index.html", "contact/index.html"),
    ("05_プロダクト/profile_本番/index.html", "profile/index.html"),
    ("05_プロダクト/news_本番/index.html", "news/index.html"),
    ("05_プロダクト/achievement_本番/index.html", "achievement/index.html"),
    ("05_プロダクト/knowledge_本番/index.html", "knowledge/index.html"),
    ("05_プロダクト/whitepaper_optin_本番/index.html", "whitepaper/index.html"),
    ("05_プロダクト/privacy-policy_本番/index.html", "privacy-policy/index.html"),
    ("05_プロダクト/service_本番/index.html", "service/index.html"),
    ("05_プロダクト/news_本番/site-renewal/index.html", "news/site-renewal/index.html"),
    ("05_プロダクト/news_本番/gravity-release/index.html", "news/gravity-release/index.html"),
]


def clean_top_html():
    """Remove all remaining WP dependencies from top_本番/index.html"""
    html = TOP_HTML.read_text(encoding="utf-8")
    original_size = len(html)

    # URL replacements (wp-content paths → /assets/)
    for old, new in URL_REPLACEMENTS:
        html = html.replace(old, new)

    # Delete large WP inline-css/script blocks
    patterns = [
        # AIOSEO JSON-LD leftover (the stale removed-marker we left earlier)
        (r"<script type=\"application/ld\+json\" data-removed=\"aioseo-was-here\">.*?</script>\s*", "", re.DOTALL),
        (r"<!-- All in One SEO -->\s*", "", 0),
        # All wp generated inline styles
        (r"<style id='global-styles-inline-css-removed'.*?</style>\s*", "", re.DOTALL),
        (r"<style id='wp-img-auto-sizes-contain-inline-css'.*?</style>\s*", "", re.DOTALL),
        (r"<style id='wp-emoji-styles-inline-css'.*?</style>\s*", "", re.DOTALL),
        (r"<style id='wp-block-library-inline-css'.*?</style>\s*", "", re.DOTALL),
        (r"<style id='classic-theme-styles-inline-css'.*?</style>\s*", "", re.DOTALL),
        # WP plugin / wp-includes stylesheets and scripts in head
        (r"<link rel='stylesheet' id='contact-form-7-css'[^>]*/>\s*", "", 0),
        (r"<link rel='stylesheet' id='wpcf7-redirect-script-frontend-css'[^>]*/>\s*", "", 0),
        (r"<script[^>]*id=\"jquery-core-js\"[^>]*></script>\s*", "", 0),
        (r"<script[^>]*id=\"jquery-migrate-js\"[^>]*></script>\s*", "", 0),
        # wp-json / xmlrpc / cdp / Site Kit generator / WP favicons
        (r"<link rel=\"https://api\.w\.org/\"[^>]*/>", "", 0),
        (r"<link rel=\"EditURI\"[^>]*xmlrpc[^>]*/>", "", 0),
        (r"<meta name=\"cdp-version\"[^>]*/?>", "", 0),
        (r"<meta name=\"generator\" content=\"Site Kit by Google[^\"]*\"\s*/?>", "", 0),
        (r"<link rel=\"icon\"[^>]*wp-content/uploads[^>]*/>\s*", "", 0),
        (r"<link rel=\"apple-touch-icon\"[^>]*wp-content/uploads[^>]*/>\s*", "", 0),
        (r"<meta name=\"msapplication-TileImage\"[^>]*wp-content/uploads[^>]*/?>\s*", "", 0),
        # speculationrules
        (r"<script type=\"speculationrules\">.*?</script>\s*", "", re.DOTALL),
        # Site Kit Sign in with Google block (between sentinel comments)
        (r"<!-- Sign in with Google button added by Site Kit -->.*?(?=<!-- Site Kit が追加した|<script src=\"https://cdnjs)", "", re.DOTALL),
        (r"<!-- Site Kit が追加した「Google でログイン」ボタンを閉じる -->\s*", "", 0),
        # WP scripts at body end
        (r"<script[^>]*src=\"[^\"]*wp-includes/js/dist/hooks[^\"]*\"[^>]*></script>\s*", "", 0),
        (r"<script[^>]*src=\"[^\"]*wp-includes/js/dist/i18n[^\"]*\"[^>]*></script>\s*", "", 0),
        (r"<script[^>]*id=\"wp-i18n-js-after\"[^>]*>.*?</script>\s*", "", re.DOTALL),
        (r"<script[^>]*src=\"[^\"]*wp-content/plugins/contact-form-7[^\"]*\"[^>]*></script>\s*", "", 0),
        (r"<script[^>]*id=\"contact-form-7-js-translations\"[^>]*>.*?</script>\s*", "", re.DOTALL),
        (r"<script[^>]*id=\"contact-form-7-js-before\"[^>]*>.*?</script>\s*", "", re.DOTALL),
        (r"<script[^>]*id=\"wpcf7-redirect-script-js-extra\"[^>]*>.*?</script>\s*", "", re.DOTALL),
        (r"<script[^>]*src=\"[^\"]*wpcf7-redirect[^\"]*\"[^>]*></script>\s*", "", 0),
        (r"<script[^>]*src=\"[^\"]*google-site-kit[^\"]*\"[^>]*></script>\s*", "", 0),
        (r"<script id=\"wp-emoji-settings\"[^>]*>.*?</script>\s*", "", re.DOTALL),
        (r"<script type=\"module\">\s*/\* <!\[CDATA\[ \*/\s*/\*! This file is auto-generated \*/.*?</script>\s*", "", re.DOTALL),
        # W3 Total Cache footer comment
        (r"<!--\s*\nPerformance optimized by W3 Total Cache.*?-->", "", re.DOTALL),
    ]

    for pat, repl, flags in patterns:
        if flags:
            html = re.sub(pat, repl, html, flags=flags)
        else:
            html = re.sub(pat, repl, html)

    # Collapse multiple blank lines
    html = re.sub(r"\n{4,}", "\n\n", html)

    TOP_HTML.write_text(html, encoding="utf-8")
    print(f"✓ Cleaned {TOP_HTML.name}: {original_size:,} → {len(html):,} bytes ({original_size - len(html):,} removed)")
    # Final WP-content sanity check
    remaining = len(re.findall(r"wp-content|wp-includes|wp-json|wp-admin|xmlrpc", html))
    print(f"  Remaining wp-* refs: {remaining}")


def ftp_connect():
    ftp = ftplib.FTP(FTP_HOST, timeout=60)
    ftp.login(FTP_USER, FTP_PASS)
    return ftp


def ensure_dir(ftp, remote_path):
    parts = [p for p in remote_path.strip("/").split("/") if p]
    cur = ""
    for p in parts:
        cur = cur + "/" + p
        try:
            ftp.mkd(cur)
        except ftplib.error_perm:
            pass


def move_assets():
    ftp = ftp_connect()
    for old, new in ASSET_MOVES:
        old_remote = f"{REMOTE_ROOT}/{old}"
        new_remote = f"{REMOTE_ROOT}/{new}"
        new_dir = "/".join(new_remote.split("/")[:-1])
        ensure_dir(ftp, new_dir)
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        try:
            with open(tmp_path, "wb") as f:
                ftp.retrbinary(f"RETR {old_remote}", f.write)
            with open(tmp_path, "rb") as f:
                ftp.storbinary(f"STOR {new_remote}", f)
            size = os.path.getsize(tmp_path)
            print(f"✓ {old} → {new} ({size:,}B)")
        except ftplib.error_perm as e:
            print(f"✗ {old}: {e}")
        finally:
            os.unlink(tmp_path)
    ftp.quit()


def upload_html():
    ftp = ftp_connect()
    for local, remote in LOCAL_TO_REMOTE_HTMLS:
        local_path = VAULT / local
        remote_path = f"{REMOTE_ROOT}/{remote}"
        remote_dir = "/".join(remote_path.split("/")[:-1])
        ensure_dir(ftp, remote_dir)
        with open(local_path, "rb") as f:
            ftp.storbinary(f"STOR {remote_path}", f)
        size = os.path.getsize(local_path)
        print(f"✓ uploaded {local} → {remote} ({size:,}B)")
    ftp.quit()


def _delete_recursive(ftp, remote_path):
    try:
        items = []
        ftp.retrlines(f"LIST {remote_path}", items.append)
    except ftplib.error_perm:
        try:
            ftp.delete(remote_path)
            print(f"  - {remote_path}")
        except ftplib.error_perm:
            pass
        return

    for item in items:
        parts = item.split()
        if len(parts) < 9:
            continue
        name = " ".join(parts[8:])
        if name in (".", ".."):
            continue
        full = f"{remote_path}/{name}"
        if item.startswith("d"):
            _delete_recursive(ftp, full)
        else:
            try:
                ftp.delete(full)
            except ftplib.error_perm as e:
                print(f"  ! {full}: {e}")
    try:
        ftp.rmd(remote_path)
        print(f"  ✓ rmdir {remote_path}")
    except ftplib.error_perm as e:
        print(f"  ! rmdir failed {remote_path}: {e}")


def delete_wp():
    ftp = ftp_connect()
    wp_dirs = ["wp-admin", "wp-includes", "wp-content"]
    for d in wp_dirs:
        path = f"{REMOTE_ROOT}/{d}"
        print(f"Deleting {path} ...")
        _delete_recursive(ftp, path)

    wp_files = [
        "wp-config.php", "wp-config-sample.php",
        "wp-login.php", "wp-cron.php", "wp-load.php",
        "wp-settings.php", "wp-mail.php", "wp-comments-post.php",
        "wp-signup.php", "wp-trackback.php", "wp-activate.php",
        "wp-blog-header.php", "wp-links-opml.php",
        "xmlrpc.php", ".maintenance",
        "license.txt", "readme.html",
    ]
    for f in wp_files:
        try:
            ftp.delete(f"{REMOTE_ROOT}/{f}")
            print(f"  ✓ {f}")
        except ftplib.error_perm:
            pass
    ftp.quit()


def edit_htaccess():
    ftp = ftp_connect()
    remote = f"{REMOTE_ROOT}/.htaccess"
    with tempfile.NamedTemporaryFile(delete=False, mode="wb") as tmp:
        tmp_path = tmp.name
    with open(tmp_path, "wb") as f:
        ftp.retrbinary(f"RETR {remote}", f.write)
    content = Path(tmp_path).read_text(encoding="utf-8")
    backup = VAULT / "07_アーカイブ" / "htaccess_backup_260511.txt"
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(content, encoding="utf-8")
    print(f"✓ backup → {backup}")

    # Strip WP rewrite block
    new = re.sub(r"# BEGIN WordPress.*?# END WordPress\s*\n?", "", content, flags=re.DOTALL)
    Path(tmp_path).write_text(new, encoding="utf-8")
    with open(tmp_path, "rb") as f:
        ftp.storbinary(f"STOR {remote}", f)
    os.unlink(tmp_path)
    ftp.quit()
    print(f"✓ .htaccess updated ({len(content):,} → {len(new):,} bytes)")


def verify():
    import urllib.request
    checks = [
        ("https://growthfix.jp/", 200),
        ("https://growthfix.jp/contact/", 200),
        ("https://growthfix.jp/profile/", 200),
        ("https://growthfix.jp/news/", 200),
        ("https://growthfix.jp/achievement/", 200),
        ("https://growthfix.jp/knowledge/", 200),
        ("https://growthfix.jp/whitepaper/", 200),
        ("https://growthfix.jp/service/", 200),
        ("https://growthfix.jp/privacy-policy/", 200),
        ("https://growthfix.jp/news/site-renewal/", 200),
        ("https://growthfix.jp/news/gravity-release/", 200),
        ("https://growthfix.jp/gravity/", 200),
        ("https://growthfix.jp/gravity-code/", 200),
        ("https://growthfix.jp/gravity-scan/", 200),
        ("https://growthfix.jp/wp-login.php", 404),
        ("https://growthfix.jp/wp-admin/", 404),
        ("https://growthfix.jp/xmlrpc.php", 404),
        ("https://growthfix.jp/wp-config.php", 404),
        ("https://growthfix.jp/terms/", 404),
    ]
    for url, expected in checks:
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=10) as r:
                actual = r.status
        except urllib.error.HTTPError as e:
            actual = e.code
        except Exception as e:
            actual = f"ERR {e}"
        mark = "✓" if actual == expected else "✗"
        print(f"  {mark} {url}: expected {expected}, got {actual}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    actions = {
        "clean-html": clean_top_html,
        "move-assets": move_assets,
        "upload-html": upload_html,
        "delete-wp": delete_wp,
        "edit-htaccess": edit_htaccess,
        "verify": verify,
    }
    if cmd in actions:
        actions[cmd]()
    else:
        print(__doc__)
        sys.exit(1)
