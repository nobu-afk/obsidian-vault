<div class="l-footer">
        <div class="footer">
            <div class="footer_logo" style="display: flex; flex-direction: column; align-items: flex-start;">
                <a href="/" class="d-flex"><span class="footer-logo__text">GrowthFix</span></a>
            </div>
            <div class="menu d-flex flex-row flex-between">
                <ul class="menu_list">
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/profile" class="menu_btn">代表者プロフィール</a>
                    </li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/news" class="menu_btn">お知らせ</a>
                    </li>
                </ul>
                <ul class="menu_list head">
                    <li class="menu_link">個人軸（経営者自身）</li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/gravity-code/" class="menu_btn" target="_blank" rel="noopener noreferrer">Gravity CODE</a>
                    </li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/gravity-coaching/" class="menu_btn" target="_blank" rel="noopener noreferrer">Gravity Coaching</a>
                    </li>
                </ul>
                <ul class="menu_list head">
                    <li class="menu_link">組織軸（経営者×組織）</li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/gravity-blueprint/" class="menu_btn" target="_blank" rel="noopener noreferrer">Gravity Blueprint</a>
                    </li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/gravity-scan/" class="menu_btn" target="_blank" rel="noopener noreferrer">Gravity Scan</a>
                    </li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/gravity-shift/" class="menu_btn" target="_blank" rel="noopener noreferrer">Gravity Shift</a>
                    </li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/gravity-orbit/" class="menu_btn" target="_blank" rel="noopener noreferrer">Gravity Orbit</a>
                    </li>
                </ul>
                <ul class="menu_list">
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/achievement" class="menu_btn">事例・実績</a>
                    </li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/knowledge" class="menu_btn">ナレッジ</a>
                    </li>
                </ul>
                <ul class="menu_list">
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/contact" class="menu_btn">お問い合わせ</a>
                    </li>
                </ul>
                <ul class="menu_list">
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/privacy-policy/" class="menu_btn">プライバシーポリシー</a>
                    </li>
                    <li class="menu_link">
                        <a href="<?php echo home_url() ?>/terms/" class="menu_btn">利用規約</a>
                    </li>
                </ul>
            </div>
            <p class="copyright">Copyrights by GrowthFix. All rights reserved.</p>
        </div>
    </div>
    <?php wp_footer(); ?>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.8.1/slick.min.js"></script>
    <script src="<?php echo get_template_directory_uri()?>/assets/js/wow.min.js"></script>
    <script src="<?php echo get_template_directory_uri()?>/assets/js/bundle.js"></script>
    <script src="<?php echo get_template_directory_uri()?>/assets/js/common.js"></script>

    <script>
        new WOW().init();
    </script>

</body>

</html>