# トップページ ナレッジセクション 差し替え パッチ（260423）

> **目的：** https://growthfix.jp/ トップのナレッジセクションを旧3冊→新3テーマに差し替え
> **対象：** WPテーマの front-page.php（or home.php / page-home.php / index.php）内 `<section class="know">` ブロック
> **想定所要時間：** 15 分

---

## 🛠 実装手順

### 1. WP管理画面 → 外観 → テーマファイルエディター

左側メニューから対象テンプレートを開く（優先度順：front-page.php → home.php → page-home.php → index.php）。

該当ブロックは `<section class="know">` で検索。「ナレッジ」「事業中心人事の教科書」で検索しても見つかる。

### 2. バックアップ

編集前に、現在のコードを**全文コピーして別ファイルに保存**（ロールバック用）。

### 3. 旧コード（削除対象）

`<section class="know">` 〜 `</section>` の範囲で、以下の **3 つの box 要素** が対象：

- `事業中心人事の教科書` を含む div
- `ベンチャー向け 人事制度ハンドブック` を含む div
- `経営者向け　組織開発ハンドブック` を含む div

### 4. 新コード（貼り付け）

以下のコードで 3 つの box 要素を**完全置換**します。

```html
                            <div data-wow-delay=".4s" class="box wow fadeInUp">
                                <a href="https://note.com/growthfix_corp/m/mc2938aaf8171" target="_blank" rel="noopener">
                                <figure class="box_img">
                                    <img loading="lazy" src="https://growthfix.jp/wp-content/uploads/2025/12/Gemini_Generated_Image_ab1rfcab1rfcab1r-1024x572.png" alt="引力経営　〜経営者が自分の引力源泉を見つける〜">                                </figure>
                                <div class="area">
                                    <p class="category">
                                        ナレッジ 
                                    </p>
                                    <p class="time">2026.04.23</p>
                                    <p class="txt">引力経営　〜経営者が自分の引力源泉を見つける〜</p>
                                </div>
                                </a>
                            </div>
                             
                            <div data-wow-delay=".4s" class="box wow fadeInUp">
                                <a href="https://note.com/growthfix_corp/m/me320728064bb" target="_blank" rel="noopener">
                                <figure class="box_img">
                                    <img loading="lazy" src="https://growthfix.jp/wp-content/uploads/2025/12/Gemini_Generated_Image_oe4hieoe4hieoe4h-1024x572.png" alt="組織の引力設計　〜&#8221;仕組み&#8221;から&#8221;仕掛け&#8221;へ〜">                                </figure>
                                <div class="area">
                                    <p class="category">
                                        ナレッジ 
                                    </p>
                                    <p class="time">2026.04.23</p>
                                    <p class="txt">組織の引力設計　〜"仕組み"から"仕掛け"へ〜</p>
                                </div>
                                </a>
                            </div>
                             
                            <div data-wow-delay=".4s" class="box wow fadeInUp">
                                <a href="https://note.com/growthfix_corp/m/m4e2c342489e9" target="_blank" rel="noopener">
                                <figure class="box_img">
                                    <img loading="lazy" src="https://growthfix.jp/wp-content/uploads/2025/09/Gemini_Generated_Image_dsdibwdsdibwdsdi-1024x572.png" alt="事業中心人事　〜事業から逆算する人事戦略〜">                                </figure>
                                <div class="area">
                                    <p class="category">
                                        ナレッジ 
                                    </p>
                                    <p class="time">2026.04.23</p>
                                    <p class="txt">事業中心人事　〜事業から逆算する人事戦略〜</p>
                                </div>
                                </a>
                            </div>
```

### 5. 「ナレッジ一覧を見る」ボタンのリンク先確認

同じセクション内にある `<a href="https://growthfix.jp/knowledge" class="c-btn ...">ナレッジ一覧を見る</a>` は**そのまま維持**。

### 6. 保存＋キャッシュパージ

1. テーマエディターで「ファイルを更新」
2. 「設定」→「W3 Total Cache」→「Purge All Caches」
3. シークレットブラウザで https://growthfix.jp/ にアクセスして反映確認

---

## ⚠️ 注意：旧コードとの差分

本パッチでは、旧コードから以下を変更・追加しています：

1. **各 box に `<a href="...">` リンクを追加**（旧はリンクなしで視覚のみ。クリックで Note マガジンに遷移する改善）
2. **target="_blank" rel="noopener"** でマガジンは別タブ開き（SEO・UX観点）
3. **日付を 2026.04.23** に統一（公開日）
4. **alt テキスト** にサブコピー含める（SEO強化）

旧コードが box にリンクなしだった場合、リンクありになることで**クリック率が跳ね上がる**はず。

## 🔄 WPテーマが子テーマ運用でない場合の安全策

テーマのコア `front-page.php` を直接編集すると、**テーマアップデート時に上書きリセット**される可能性があります。

### 推奨：子テーマ作成 or バックアップ

- 可能なら「子テーマ」に `front-page.php` をコピーして編集
- 難しければ、編集前のコード全文を別途保存（ロールバック用）

### 代替：FTP 経由でテーマファイルを直接編集＋バージョン管理

FTP 情報：
- ホスト: sv16489.xserver.jp
- ユーザー: xs992119
- パス: `/growthfix.jp/public_html/wp-content/themes/{テーマ名}/front-page.php`

FTPアクセスで、編集前のファイルを `front-page.php.bak.260423` として保存→差し替え→WPキャッシュパージ の流れが安全。

---

## 📅 Phase 2（5月以降）：動的連携への移行

A案で即対応した後、5月以降にC案（カスタム投稿 get_posts）でリファクタすれば、以降は /knowledge/ 更新が自動反映。

実装の概略：

```php
// front-page.php のナレッジセクション内
<section class="know">
    <div class="c-inner">
        <h3 class="c-sub_ttl wow fadeInUp">ナレッジ</h3>
        <div class="item d-flex flex-wrap flex-between">
        <?php
        $knowledge_posts = get_posts([
            'post_type' => 'knowledge',  // カスタム投稿タイプ名（or 'post' でカテゴリーID指定）
            'posts_per_page' => 3,
            'orderby' => 'date',
            'order' => 'DESC'
        ]);
        foreach ($knowledge_posts as $post) : setup_postdata($post);
            $thumb = get_the_post_thumbnail_url($post->ID, 'large');
            $note_url = get_field('note_magazine_url', $post->ID); // ACFカスタムフィールド
        ?>
            <div class="box wow fadeInUp">
                <a href="<?php echo esc_url($note_url); ?>" target="_blank" rel="noopener">
                    <figure class="box_img">
                        <img loading="lazy" src="<?php echo esc_url($thumb); ?>" alt="<?php the_title_attribute(); ?>">
                    </figure>
                    <div class="area">
                        <p class="category">ナレッジ</p>
                        <p class="time"><?php echo get_the_date('Y.m.d'); ?></p>
                        <p class="txt"><?php the_title(); ?></p>
                    </div>
                </a>
            </div>
        <?php endforeach; wp_reset_postdata(); ?>
        </div>
        ...
    </div>
</section>
```

この動的化は GW 以降に実装予定。

---

## 🔗 関連

- `04_GrowthFix/02_マーケティング/260423_情報発信_HPバナー_Noteマガジン設計.md`
- `05_プロダクト/top_本番/index.html` ── ローカル本番スナップショット（今回同期更新）
